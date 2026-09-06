"""Unit tests for the OAS Refiner."""

import pytest
from apiforge.agents.review_agent.linter import OASLinter
from apiforge.agents.review_agent.refiner import OASRefiner


def test_refiner_repairs_bad_spec():
    linter = OASLinter()
    refiner = OASRefiner()

    bad_oas = {
        "openapi": "3.1.0",
        "info": {"title": "Legacy Service", "version": "1.0.0"},
        "paths": {
            "/createUser": {
                "post": {
                    "operationId": "createUser",
                    "responses": {"200": {"description": "Success"}}
                }
            },
            "/user/{user_id}/": {
                "get": {
                    "operationId": "getUser",
                    "responses": {"200": {"description": "Success"}}
                }
            }
        }
    }

    initial_findings = linter.lint(bad_oas)
    assert len(initial_findings) > 0, "Initial bad OAS should have multiple violations"

    # Apply Refiner
    refined_oas = refiner.refine(bad_oas, initial_findings)

    # Verifications
    paths = refined_oas["paths"]
    assert "/users" in paths, "Verb should be removed and resource pluralized to /users"
    assert "/createUser" not in paths
    assert "/users/{user_id}" in paths, "Trailing slash should be removed and pluralized"

    # Verify status code 201 on POST
    assert "201" in paths["/users"]["post"]["responses"]
    assert "400" in paths["/users"]["post"]["responses"]

    # Verify 404 on parameterized GET
    assert "404" in paths["/users/{user_id}"]["get"]["responses"]

    # Verify security schemes and ErrorResponse
    assert "securitySchemes" in refined_oas["components"]
    assert "ErrorResponse" in refined_oas["components"]["schemas"]
