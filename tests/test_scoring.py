"""Unit tests for the API Quality Scoring Engine."""

import pytest
from apiforge.core.state import ReviewFinding
from apiforge.agents.review_agent.scoring import calculate_quality_score


def test_calculate_quality_score_clean_spec():
    oas = {
        "openapi": "3.1.0",
        "paths": {
            "/users": {
                "get": {"operationId": "listUsers", "responses": {"200": {}}}
            }
        }
    }
    score = calculate_quality_score([], oas)
    assert score.overall_score == 100.0
    assert score.passed_threshold is True


def test_calculate_quality_score_deductions():
    oas = {
        "openapi": "3.1.0",
        "paths": {
            "/users": {
                "get": {"operationId": "listUsers", "responses": {"200": {}}}
            }
        }
    }
    findings = [
        ReviewFinding(
            rule_id="REST-001",
            category="rest_compliance",
            severity="critical",
            path="paths./getUsers",
            message="Verb in URI",
            recommendation="Fix URI"
        )
    ]
    score = calculate_quality_score(findings, oas)
    assert score.overall_score < 100.0
    assert score.passed_threshold is False
    assert score.findings_count["critical"] == 1
