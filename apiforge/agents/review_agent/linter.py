"""Deterministic OAS & REST Smell Linter for APIForge AI.

Evaluates OpenAPI 3.1 specifications against 20+ architectural, security,
and syntactic rules to detect anti-patterns and quality smells.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List
from apiforge.core.state import ReviewFinding

VERB_PATTERN = re.compile(
    r"\b(get|fetch|retrieve|find|post|create|add|new|put|update|modify|delete|remove|destroy|edit|list|search)\b",
    re.IGNORECASE
)

IRREGULAR_PLURALS = {
    "person": "people", "man": "men", "child": "children",
    "status": "statuses", "datum": "data", "corpus": "corpora"
}

def is_plural(word: str) -> bool:
    word = word.lower()
    if word in IRREGULAR_PLURALS.values():
        return True
    if word in IRREGULAR_PLURALS:
        return False
    if word.endswith("s") or word.endswith("es") or word.endswith("ies"):
        return True
    return False


class OASLinter:
    """Deterministic rule-based linter evaluating REST standards and OpenAPI specs."""

    def lint(self, oas: Dict[str, Any]) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []
        paths = oas.get("paths", {})
        components = oas.get("components", {})
        schemas = components.get("schemas", {})
        security_schemes = components.get("securitySchemes", {})
        has_security_schemes = bool(security_schemes)
        global_security = oas.get("security", [])

        # Check OAS-000: Info block
        info = oas.get("info", {})
        if not info.get("title"):
            findings.append(ReviewFinding(
                rule_id="OAS-000",
                category="documentation",
                severity="warning",
                path="info.title",
                message="API info block is missing a descriptive title.",
                recommendation="Provide a title for the API in info.title."
            ))
        if not info.get("description"):
            findings.append(ReviewFinding(
                rule_id="OAS-002",
                category="documentation",
                severity="info",
                path="info.description",
                message="API info block is missing a general description.",
                recommendation="Provide an overview of API functionality in info.description."
            ))

        # Check SEC-002: Security Schemes presence
        if not has_security_schemes and not global_security:
            findings.append(ReviewFinding(
                rule_id="SEC-002",
                category="security",
                severity="warning",
                path="components.securitySchemes",
                message="No security schemes defined in components.securitySchemes.",
                recommendation="Define at least one security scheme (e.g., Bearer JWT or APIKey) in components.securitySchemes."
            ))

        # Inspect Paths
        for path_key, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            # REST-010: Trailing slash in path
            if len(path_key) > 1 and path_key.endswith("/"):
                findings.append(ReviewFinding(
                    rule_id="REST-010",
                    category="rest_compliance",
                    severity="warning",
                    path=f"paths.{path_key}",
                    message=f"Path '{path_key}' contains a trailing slash.",
                    recommendation=f"Remove trailing slash: use '{path_key.rstrip('/')}'."
                ))

            segments = [s for s in path_key.split("/") if s]
            
            # REST-001: Verbs in URI path
            for seg in segments:
                if not seg.startswith("{") and not seg.endswith("}"):
                    # Split camelCase (e.g. getUsers -> ['get', 'Users']) and delimiters
                    words = re.findall(r'[A-Za-z][a-z]*', seg) or [seg]
                    for w in words:
                        if VERB_PATTERN.match(w):
                            findings.append(ReviewFinding(
                                rule_id="REST-001",
                                category="rest_compliance",
                                severity="critical",
                                path=f"paths.{path_key}",
                                message=f"Path segment '{seg}' contains an action verb ('{w}'). REST URIs must be nouns.",
                                recommendation=f"Replace '{seg}' with a resource noun and use appropriate HTTP methods (e.g., POST instead of /create)."
                            ))
                            break

            # REST-002: Plural noun on collection endpoints
            if segments:
                first_seg = segments[0]
                if not first_seg.startswith("{") and not is_plural(first_seg):
                    findings.append(ReviewFinding(
                        rule_id="REST-002",
                        category="rest_compliance",
                        severity="warning",
                        path=f"paths.{path_key}",
                        message=f"Root collection resource segment '{first_seg}' appears to be singular instead of plural.",
                        recommendation=f"Use plural noun for resource collections (e.g. '/{first_seg}s' instead of '/{first_seg}')."
                    ))

            # Extract path parameters defined in template {param}
            template_params = re.findall(r"\{([a-zA-Z0-9_]+)\}", path_key)

            # Inspect Operations
            for method, op in path_item.items():
                if method.lower() not in ("get", "post", "put", "patch", "delete", "options", "head"):
                    continue
                if not isinstance(op, dict):
                    continue

                m = method.upper()
                op_path = f"paths.{path_key}.{method}"

                # OAS-001: operationId
                if not op.get("operationId"):
                    findings.append(ReviewFinding(
                        rule_id="OAS-001",
                        category="documentation",
                        severity="warning",
                        path=op_path,
                        message=f"Operation {m} {path_key} lacks an operationId.",
                        recommendation="Assign a unique operationId for client SDK generation."
                    ))

                # OAS-002: summary or description
                if not op.get("summary") and not op.get("description"):
                    findings.append(ReviewFinding(
                        rule_id="OAS-002",
                        category="documentation",
                        severity="info",
                        path=op_path,
                        message=f"Operation {m} {path_key} is missing both summary and description.",
                        recommendation="Provide an operation summary explaining its intent."
                    ))

                # OAS-003: tags
                if not op.get("tags"):
                    findings.append(ReviewFinding(
                        rule_id="OAS-003",
                        category="documentation",
                        severity="info",
                        path=op_path,
                        message=f"Operation {m} {path_key} lacks categorization tags.",
                        recommendation="Add at least one tag to group operations in developer documentation."
                    ))

                # Parameters analysis
                declared_params = op.get("parameters", [])
                path_param_names = [p.get("name") for p in declared_params if isinstance(p, dict) and p.get("in") == "path"]

                # OAS-007: Path parameters match template
                for tp in template_params:
                    if tp not in path_param_names:
                        findings.append(ReviewFinding(
                            rule_id="OAS-007",
                            category="schema_completeness",
                            severity="critical",
                            path=op_path,
                            message=f"Template parameter '{{{tp}}}' is missing from operation parameters definition.",
                            recommendation=f"Add parameter '{tp}' with 'in: path' and 'required: true'."
                        ))

                # SEC-003: Sensitive tokens in query params
                for p in declared_params:
                    if isinstance(p, dict) and p.get("in") == "query":
                        p_name = p.get("name", "").lower()
                        if any(s in p_name for s in ("password", "token", "secret", "apikey", "api_key")):
                            findings.append(ReviewFinding(
                                rule_id="SEC-003",
                                category="security",
                                severity="critical",
                                path=f"{op_path}.parameters.{p.get('name')}",
                                message=f"Sensitive credential '{p.get('name')}' is passed as a query parameter.",
                                recommendation="Pass sensitive credentials in HTTP Authorization header, never in query parameters."
                            ))

                # REST-004: GET with requestBody
                if m == "GET" and "requestBody" in op:
                    findings.append(ReviewFinding(
                        rule_id="REST-004",
                        category="rest_compliance",
                        severity="critical",
                        path=op_path,
                        message="HTTP GET request contains a requestBody. GET methods must not have a request body.",
                        recommendation="Remove requestBody from GET operation or switch to POST/PUT if a body is required."
                    ))

                # OAS-006: Collection GET missing pagination
                if m == "GET" and not template_params:
                    query_param_names = [p.get("name") for p in declared_params if isinstance(p, dict) and p.get("in") == "query"]
                    has_pagination = any(p in query_param_names for p in ("limit", "offset", "page", "pageSize", "size"))
                    if not has_pagination:
                        findings.append(ReviewFinding(
                            rule_id="OAS-006",
                            category="schema_completeness",
                            severity="warning",
                            path=op_path,
                            message=f"Collection endpoint {m} {path_key} does not support pagination parameters (e.g. limit/offset or page/size).",
                            recommendation="Add pagination query parameters ('limit' and 'offset') to prevent unbounded collection responses."
                        ))

                # Responses
                responses = op.get("responses", {})
                if not responses:
                    findings.append(ReviewFinding(
                        rule_id="OAS-004",
                        category="schema_completeness",
                        severity="critical",
                        path=op_path,
                        message="No HTTP responses defined for operation.",
                        recommendation="Define at least one success response and standard error responses."
                    ))

                # REST-005: POST creating resource should return 201
                if m == "POST" and not path_key.endswith("/search") and not path_key.endswith("/login"):
                    if "201" not in responses and "200" in responses:
                        findings.append(ReviewFinding(
                            rule_id="REST-005",
                            category="rest_compliance",
                            severity="warning",
                            path=op_path,
                            message=f"POST {path_key} returns 200 OK instead of 201 Created.",
                            recommendation="Resource creation operations should return HTTP 201 Created with representation or Location header."
                        ))

                # REST-006: DELETE should return 204 No Content
                if m == "DELETE":
                    if "204" not in responses and "200" in responses:
                        findings.append(ReviewFinding(
                            rule_id="REST-006",
                            category="rest_compliance",
                            severity="info",
                            path=op_path,
                            message=f"DELETE {path_key} returns 200 OK instead of standard 204 No Content.",
                            recommendation="Use 204 No Content for successful deletions where no body is returned."
                        ))

                # REST-007: Missing 400 Bad Request
                if m in ("POST", "PUT", "PATCH") and "400" not in responses and "422" not in responses:
                    findings.append(ReviewFinding(
                        rule_id="REST-007",
                        category="rest_compliance",
                        severity="warning",
                        path=op_path,
                        message=f"Mutation operation {m} {path_key} does not declare a 400 or 422 validation error response.",
                        recommendation="Add 400 (Bad Request) or 422 (Unprocessable Entity) response schema."
                    ))

                # REST-008: Missing 404 on parameterized path
                if template_params and "404" not in responses:
                    findings.append(ReviewFinding(
                        rule_id="REST-008",
                        category="rest_compliance",
                        severity="warning",
                        path=op_path,
                        message=f"Operation {m} {path_key} references resource by ID but does not declare a 404 Not Found response.",
                        recommendation="Define 404 Not Found response when individual resource is not located."
                    ))

                # SEC-001: Sensitive operation missing security
                op_security = op.get("security", global_security)
                if not op_security and m in ("POST", "PUT", "PATCH", "DELETE") and not any(auth_kw in path_key for auth_kw in ("login", "token", "register")):
                    findings.append(ReviewFinding(
                        rule_id="SEC-001",
                        category="security",
                        severity="warning",
                        path=op_path,
                        message=f"Mutating operation {m} {path_key} has no authentication security requirements defined.",
                        recommendation="Attach security scheme (e.g. 'bearerAuth: []') to protect modifying operations."
                    ))

                # REST-009: Missing 401 on secured endpoints
                if op_security and "401" not in responses:
                    findings.append(ReviewFinding(
                        rule_id="REST-009",
                        category="security",
                        severity="warning",
                        path=op_path,
                        message=f"Secured operation {m} {path_key} requires authentication but does not define 401 Unauthorized response.",
                        recommendation="Add 401 response with standard ErrorResponse schema."
                    ))

        return findings
