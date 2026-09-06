"""End-to-end pipeline test for APIForge AI orchestrator."""

import os
import tempfile
import pytest
from apiforge.core.llm import MockLLMClient
from apiforge.core.orchestrator import APIForgeOrchestrator


def test_full_orchestrator_pipeline():
    with tempfile.TemporaryDirectory(prefix="apiforge_test_out_") as out_dir:
        llm = MockLLMClient()
        orchestrator = APIForgeOrchestrator(
            llm=llm,
            max_review_iterations=2,
            max_debug_iterations=2,
            pass_threshold=80.0,
        )

        requirements = "Design a Task Tracking API with projects, tasks, and user authentication."
        state = orchestrator.run(requirements, output_dir=out_dir)

        # 1. Verify Status and Spec
        assert state.status in ("completed", "approved")
        assert state.openapi_spec is not None
        assert "paths" in state.openapi_spec
        assert os.path.exists(os.path.join(out_dir, "openapi.json"))
        assert os.path.exists(os.path.join(out_dir, "openapi.yaml"))

        # 2. Verify Generated Backend & Tests
        assert os.path.exists(os.path.join(out_dir, "app", "main.py"))
        assert os.path.exists(os.path.join(out_dir, "app", "models.py"))
        assert os.path.exists(os.path.join(out_dir, "tests", "test_api_functional.py"))

        # 3. Verify Documentation
        assert os.path.exists(os.path.join(out_dir, "README.md"))
        assert os.path.exists(os.path.join(out_dir, "docs", "swagger.html"))
        assert os.path.exists(os.path.join(out_dir, "docs", "redoc.html"))

        # 4. Verify Sandbox Test Execution
        assert len(state.test_reports) > 0
        latest_report = state.test_reports[-1]
        assert latest_report.total_tests > 0
        assert latest_report.passed == latest_report.total_tests
        assert latest_report.success is True

        # 5. Verify Evaluation Metrics
        assert state.evaluation_metrics is not None
        m = state.evaluation_metrics
        assert m.openapi_validation_accuracy > 0
        assert m.rest_design_compliance > 80.0
        assert m.test_case_success_rate == 100.0
        assert m.execution_reliability == 100.0
        assert os.path.exists(os.path.join(out_dir, "evaluation_metrics.json"))
