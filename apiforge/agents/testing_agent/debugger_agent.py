"""Runtime Debugger Agent for APIForge AI.

Analyzes runtime errors, test failure tracebacks, and execution logs
to generate targeted patches and repair backend implementations.
"""

from __future__ import annotations
import copy
import logging
import re
from typing import Any, Dict
from apiforge.core.llm import BaseLLMClient
from apiforge.core.state import TestExecutionReport

logger = logging.getLogger(__name__)

DEBUGGER_PROMPT = """You are a Senior Systems Debugger.
Given the failing test output and current backend code, diagnose the bug and output the corrected file content.

Failure report:
{failure_report}

Analyze the failure traceback and repair the affected router or model.
"""


class DebuggerAgent:
    """Isolates runtime bugs and applies repair patches to generated code."""

    def __init__(self, llm: BaseLLMClient):
        self.llm = llm

    def debug_and_repair(
        self,
        code_files: Dict[str, str],
        report: TestExecutionReport,
        iteration: int = 0
    ) -> Dict[str, str]:
        repaired = copy.deepcopy(code_files)
        logger.info(f"Running debugger repair iteration {iteration + 1} for {report.failed + report.errors} failed tests.")

        # Inspect failure messages for common deterministic fixes
        for item in report.items:
            if item.status in ("FAILED", "ERROR") and item.error_message:
                err = item.error_message

                # Fix status code discrepancies if any (e.g. 200 vs 201)
                if "Expected 201" in err:
                    for fname, code in list(repaired.items()):
                        if fname.startswith("app/routers/"):
                            repaired[fname] = code.replace("status_code=200", "status_code=201")

                # Fix 401 Bearer Token logic if missing
                if "Expected 401" in err:
                    for fname, code in list(repaired.items()):
                        if fname.startswith("app/routers/"):
                            if "authorization" in code and "HTTPException(status_code=401" not in code:
                                repaired[fname] = re.sub(
                                    r'(""".*?""")',
                                    r'\1\n    if not authorization or not authorization.startswith("Bearer "):\n        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")',
                                    code,
                                    flags=re.DOTALL
                                )
                
                # Fix import errors
                if "ModuleNotFoundError" in err or "ImportError" in err:
                    if "app/routers/__init__.py" not in repaired:
                        repaired["app/routers/__init__.py"] = ""

        return repaired
