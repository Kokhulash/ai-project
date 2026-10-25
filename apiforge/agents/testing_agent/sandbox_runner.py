"""Sandbox Runtime Runner for APIForge AI.

Executes generated backend code against synthesized Pytest test suites
using high-speed in-process ASGI execution or managed subprocesses.
"""

from __future__ import annotations
import importlib.util
import logging
import os
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional
import httpx
from apiforge.core.state import TestExecutionReport, TestResultItem

logger = logging.getLogger(__name__)


class SandboxRunner:
    """Runs test suites against generated FastAPI applications and captures execution metrics."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def run_tests(self, code_files: Dict[str, str], test_files: Dict[str, str]) -> TestExecutionReport:
        """Executes test suite against generated code files in an isolated temporary directory."""
        start_time = time.time()
        report = TestExecutionReport()
        items: List[TestResultItem] = []
        logs: List[str] = []
        
        initial_modules = set(sys.modules.keys())

        with tempfile.TemporaryDirectory(prefix="apiforge_sandbox_") as temp_dir:
            # 1. Materialize all files
            for rel_path, content in code_files.items():
                full_path = os.path.join(temp_dir, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

            for rel_path, content in test_files.items():
                full_path = os.path.join(temp_dir, rel_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # 2. Add temp_dir to sys.path
            sys.path.insert(0, temp_dir)
            try:
                # Load app.main:app
                main_path = os.path.join(temp_dir, "app", "main.py")
                spec = importlib.util.spec_from_file_location("sandbox_app", main_path)
                if spec is None or spec.loader is None:
                    raise RuntimeError("Failed to load spec for generated app.main")
                module = importlib.util.module_from_spec(spec)
                sys.modules["sandbox_app"] = module
                spec.loader.exec_module(module)
                app = getattr(module, "app", None)
                if not app:
                    raise RuntimeError("No 'app' attribute found in app.main")

                # Load test file
                test_path = os.path.join(temp_dir, "tests", "test_api_functional.py")
                test_spec = importlib.util.spec_from_file_location("sandbox_tests", test_path)
                if test_spec is None or test_spec.loader is None:
                    raise RuntimeError("Failed to load spec for generated tests")
                test_mod = importlib.util.module_from_spec(test_spec)
                sys.modules["sandbox_tests"] = test_mod
                test_spec.loader.exec_module(test_mod)

                # 3. Discover and execute all test functions using FastAPI TestClient
                from fastapi.testclient import TestClient
                with TestClient(app, base_url="http://localhost:8000") as client:
                    test_funcs = [
                        (name, getattr(test_mod, name))
                        for name in dir(test_mod)
                        if name.startswith("test_") and callable(getattr(test_mod, name))
                    ]

                    for tname, tfunc in test_funcs:
                        t_start = time.time()
                        try:
                            # If function accepts 'client' arg, pass client
                            import inspect
                            sig = inspect.signature(tfunc)
                            if "client" in sig.parameters:
                                tfunc(client)
                            else:
                                tfunc()
                            duration = time.time() - t_start
                            items.append(TestResultItem(
                                test_name=tname,
                                status="PASSED",
                                duration_sec=round(duration, 4)
                            ))
                            logs.append(f"[PASS] {tname} ({round(duration, 3)}s)")
                        except AssertionError as ae:
                            duration = time.time() - t_start
                            err_msg = str(ae) if str(ae) else repr(ae)
                            items.append(TestResultItem(
                                test_name=tname,
                                status="FAILED",
                                duration_sec=round(duration, 4),
                                error_message=err_msg
                            ))
                            logs.append(f"[FAIL] {tname}: {err_msg}")
                        except Exception as ex:
                            duration = time.time() - t_start
                            err_msg = f"{type(ex).__name__}: {str(ex)}"
                            items.append(TestResultItem(
                                test_name=tname,
                                status="ERROR",
                                duration_sec=round(duration, 4),
                                error_message=err_msg
                            ))
                            logs.append(f"[ERROR] {tname}: {err_msg}")

            except Exception as e:
                logs.append(f"FATAL Execution Failure: {str(e)}")
                report.errors += 1
            finally:
                if temp_dir in sys.path:
                    sys.path.remove(temp_dir)
                for mod_key in list(sys.modules.keys()):
                    if mod_key not in initial_modules:
                        del sys.modules[mod_key]

        total = len(items)
        passed = sum(1 for it in items if it.status == "PASSED")
        failed = sum(1 for it in items if it.status == "FAILED")
        errors = sum(1 for it in items if it.status == "ERROR")

        report.total_tests = total
        report.passed = passed
        report.failed = failed
        report.errors = errors
        report.items = items
        report.logs = "\n".join(logs)
        report.duration_sec = round(time.time() - start_time, 3)
        report.success = bool(total > 0 and failed == 0 and errors == 0)

        return report
