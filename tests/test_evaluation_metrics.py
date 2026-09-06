"""Unit tests for the 8 research evaluation metrics and benchmark harness."""

import pytest
from apiforge.core.llm import MockLLMClient
from apiforge.core.state import APIForgeState, TestExecutionReport, QualityScoreModel
from apiforge.evaluation.metrics import evaluate_state_metrics
from apiforge.evaluation.benchmark_runner import BenchmarkRunner


def test_evaluate_state_metrics_calculation():
    state = APIForgeState(
        raw_requirements="Test requirements",
        openapi_spec={
            "openapi": "3.1.0",
            "info": {"title": "Sample API", "version": "1.0.0", "description": "API Docs"},
            "paths": {
                "/items": {
                    "get": {
                        "operationId": "listItems",
                        "summary": "List items",
                        "description": "Returns items",
                        "parameters": [
                            {"name": "limit", "in": "query", "description": "Page limit"}
                        ],
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            },
            "components": {
                "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}}
            }
        },
        quality_scores=[QualityScoreModel(overall_score=92.5, passed_threshold=True)],
        test_reports=[TestExecutionReport(total_tests=5, passed=5, failed=0, errors=0, success=True)]
    )

    metrics = evaluate_state_metrics(state)

    assert metrics.openapi_validation_accuracy > 0
    assert metrics.rest_design_compliance > 80.0
    assert metrics.documentation_completeness > 50.0
    assert metrics.security_recommendation_coverage > 50.0
    assert metrics.api_quality_score == 92.5
    assert metrics.test_case_success_rate == 100.0
    assert metrics.execution_reliability == 100.0
    assert metrics.error_reduction_rate >= 0.0


def test_benchmark_runner_smoke():
    runner = BenchmarkRunner(llm=MockLLMClient())
    # Run a single suite to verify end-to-end benchmark execution
    results = runner.run_suite(["task_management"])
    assert "task_management" in results["suites"]
    tm_res = results["suites"]["task_management"]
    assert tm_res["tests_passed"] > 0
    assert tm_res["tests_passed"] == tm_res["tests_total"]

    md_report = runner.generate_markdown_report(results)
    assert "# APIForge AI - Comprehensive Benchmark Evaluation Report" in md_report
    assert "Task_management" in md_report
