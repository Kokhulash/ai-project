"""Unit tests for the OpenAPI & REST smell linter."""

import pytest
from apiforge.agents.review_agent.linter import OASLinter


def test_linter_detects_verb_in_path():
    linter = OASLinter()
    bad_oas = {
        "openapi": "3.1.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/getUsers": {
                "get": {
                    "operationId": "getUsers",
                    "responses": {"200": {"description": "OK"}}
                }
            }
        }
    }
    findings = linter.lint(bad_oas)
    rule_ids = [f.rule_id for f in findings]
    assert "REST-001" in rule_ids, "Expected REST-001 verb-in-path violation"


def test_linter_detects_singular_resource():
    linter = OASLinter()
    bad_oas = {
        "openapi": "3.1.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/user": {
                "get": {
                    "operationId": "getUser",
                    "responses": {"200": {"description": "OK"}}
                }
            }
        }
    }
    findings = linter.lint(bad_oas)
    rule_ids = [f.rule_id for f in findings]
    assert "REST-002" in rule_ids, "Expected REST-002 singular resource violation"


def test_linter_detects_get_with_request_body():
    linter = OASLinter()
    bad_oas = {
        "openapi": "3.1.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "requestBody": {"content": {"application/json": {}}},
                    "responses": {"200": {"description": "OK"}}
                }
            }
        }
    }
    findings = linter.lint(bad_oas)
    rule_ids = [f.rule_id for f in findings]
    assert "REST-004" in rule_ids, "Expected REST-004 GET with body violation"


def test_linter_detects_missing_404_on_parameter():
    linter = OASLinter()
    bad_oas = {
        "openapi": "3.1.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users/{user_id}": {
                "get": {
                    "operationId": "getUserById",
                    "parameters": [{"name": "user_id", "in": "path", "required": True}],
                    "responses": {"200": {"description": "OK"}}
                }
            }
        }
    }
    findings = linter.lint(bad_oas)
    rule_ids = [f.rule_id for f in findings]
    assert "REST-008" in rule_ids, "Expected REST-008 missing 404 response violation"


def test_linter_detects_sensitive_query_param():
    linter = OASLinter()
    bad_oas = {
        "openapi": "3.1.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "listUsers",
                    "parameters": [{"name": "api_key", "in": "query"}],
                    "responses": {"200": {"description": "OK"}}
                }
            }
        }
    }
    findings = linter.lint(bad_oas)
    rule_ids = [f.rule_id for f in findings]
    assert "SEC-003" in rule_ids, "Expected SEC-003 sensitive credential in query param"
