"""API Specification Generator Agent for APIForge AI.

Converts structured requirements into a complete, syntactically valid OpenAPI 3.1.0 specification.
"""

from __future__ import annotations
import copy
import json
import logging
from typing import Any, Dict, List, Optional
from apiforge.core.llm import BaseLLMClient
from apiforge.core.state import APIForgeState, StructuredRequirements

logger = logging.getLogger(__name__)

GENERATOR_SYSTEM_PROMPT = """You are an expert OpenAPI 3.1.0 Specification Architect.
Given structured requirements and domain entities, generate a complete, production-ready OpenAPI 3.1.0 specification in JSON.

Strict OpenAPI 3.1 & REST Guidelines:
1. "openapi": "3.1.0"
2. Every path must use plural nouns (e.g. /items, /items/{item_id}).
3. Use proper HTTP methods: GET (read), POST (create, 201), PUT (replace, 200), PATCH (partial update, 200), DELETE (204).
4. Define standard reusable schemas under components.schemas:
   - Entity schema (e.g. User, Task)
   - Create schema (e.g. UserCreate without system fields like id, created_at)
   - Update schema (e.g. UserUpdate with optional fields)
   - Paginated list schema (e.g. UserListResponse with items, total, limit, offset)
   - Standard ErrorResponse schema (title, status, detail, instance)
5. Include components.securitySchemes (e.g. bearerAuth with scheme: bearer, bearerFormat: JWT).
6. Every operation MUST have:
   - operationId (camelCase or snake_case, unique)
   - summary and description
   - tags
   - responses for success and error cases (e.g. 400, 401, 404, 422).
7. Return ONLY the valid JSON object representing the OpenAPI specification.
"""


class APISpecificationGeneratorAgent:
    """Agent that translates structured requirements into complete OpenAPI 3.1 specifications."""

    def __init__(self, llm: BaseLLMClient):
        self.llm = llm

    def run(self, state: APIForgeState) -> APIForgeState:
        """Generates or updates state.openapi_spec based on structured_requirements."""
        if not state.structured_requirements:
            raise ValueError("State must contain structured_requirements before running APISpecificationGeneratorAgent.")

        reqs = state.structured_requirements
        state.log_trace("APISpecificationGeneratorAgent", "Generating OpenAPI specification", iteration=state.review_iterations)

        # Build prompt
        prompt = f"""Generate an OpenAPI 3.1.0 specification for:
Title: {reqs.title}
Version: {reqs.version}
Description: {reqs.description}
Auth Type: {reqs.auth_type}

Entities:
{json.dumps([e.model_dump() for e in reqs.entities], indent=2)}

Endpoints:
{json.dumps([ep.model_dump() for ep in reqs.endpoints], indent=2)}

Business Rules:
{json.dumps(reqs.business_rules, indent=2)}
"""
        if state.review_findings:
            findings_summary = [
                f"[{f.rule_id}] {f.severity.upper()}: {f.path} - {f.message} (Recommendation: {f.recommendation})"
                for f in state.review_findings
            ]
            prompt += f"\n\nCRITICAL FIXES REQUIRED FROM PREVIOUS REVIEW:\n" + "\n".join(findings_summary)

        try:
            oas = self.llm.generate_json(prompt, system_prompt=GENERATOR_SYSTEM_PROMPT)
            if not isinstance(oas, dict) or "openapi" not in oas or "paths" not in oas:
                raise ValueError("LLM response did not contain valid OpenAPI structure.")
        except Exception as e:
            logger.warning(f"Spec generation via LLM encountered issue ({e}). Using deterministic OAS builder.")
            oas = self._build_deterministic_oas(reqs)

        # Save previous spec to history if any
        if state.openapi_spec:
            state.spec_draft_history.append(copy.deepcopy(state.openapi_spec))

        state.openapi_spec = oas
        state.status = "generated"
        state.log_trace(
            "APISpecificationGeneratorAgent",
            "OpenAPI specification generated",
            paths_count=len(oas.get("paths", {})),
            schemas_count=len(oas.get("components", {}).get("schemas", {})),
        )
        return state

    def _build_deterministic_oas(self, reqs: StructuredRequirements) -> Dict[str, Any]:
        """Constructs a compliant, production-grade OpenAPI 3.1.0 specification deterministically."""
        paths: Dict[str, Any] = {}
        schemas: Dict[str, Any] = {
            "ErrorResponse": {
                "type": "object",
                "required": ["detail", "status"],
                "properties": {
                    "detail": {"type": "string", "description": "Human-readable error description"},
                    "status": {"type": "integer", "description": "HTTP status code"},
                    "code": {"type": "string", "description": "Error classification code"}
                }
            }
        }

        # Build entity schemas
        for entity in reqs.entities:
            prop_defs = {}
            for fname, ftype in entity.fields.items():
                if ftype in ("int", "integer"):
                    prop_defs[fname] = {"type": "integer", "example": 1}
                elif ftype in ("bool", "boolean"):
                    prop_defs[fname] = {"type": "boolean", "example": True}
                elif ftype == "datetime":
                    prop_defs[fname] = {"type": "string", "format": "date-time", "example": "2026-01-01T12:00:00Z"}
                elif ftype == "uuid":
                    prop_defs[fname] = {"type": "string", "format": "uuid", "example": "123e4567-e89b-12d3-a456-426614174000"}
                else:
                    prop_defs[fname] = {"type": "string", "example": f"Sample {fname}"}

            schemas[entity.name] = {
                "type": "object",
                "description": entity.description or f"The {entity.name} schema",
                "required": [k for k in entity.fields.keys() if k in ("id", "name", "title")],
                "properties": prop_defs
            }

            # Create schema (without auto-generated fields like id, created_at)
            create_props = {k: v for k, v in prop_defs.items() if k not in ("id", "created_at", "updated_at")}
            schemas[f"{entity.name}Create"] = {
                "type": "object",
                "description": f"Payload for creating a new {entity.name}",
                "required": [k for k in create_props.keys() if k in ("name", "title")],
                "properties": create_props
            }

            # List response schema with pagination
            schemas[f"{entity.name}ListResponse"] = {
                "type": "object",
                "description": f"Paginated list of {entity.name} records",
                "required": ["items", "total", "limit", "offset"],
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"$ref": f"#/components/schemas/{entity.name}"}
                    },
                    "total": {"type": "integer", "example": 100},
                    "limit": {"type": "integer", "example": 20},
                    "offset": {"type": "integer", "example": 0}
                }
            }

        # Build paths from endpoints
        for ep in reqs.endpoints:
            path_key = ep.path
            if path_key not in paths:
                paths[path_key] = {}

            method = ep.method.lower()
            op_id = f"{method}_{path_key.replace('/', '_').replace('{', '').replace('}', '').strip('_')}"

            # Parameters
            parameters = []
            if "{" in path_key:
                for segment in path_key.split("/"):
                    if segment.startswith("{") and segment.endswith("}"):
                        param_name = segment[1:-1]
                        parameters.append({
                            "name": param_name,
                            "in": "path",
                            "required": True,
                            "description": f"Unique identifier for {param_name}",
                            "schema": {"type": "string"}
                        })

            if method == "get" and "{" not in path_key:
                # Add pagination params
                parameters.extend([
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "description": "Maximum number of records to return",
                        "schema": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100}
                    },
                    {
                        "name": "offset",
                        "in": "query",
                        "required": False,
                        "description": "Number of records to skip for pagination",
                        "schema": {"type": "integer", "default": 0, "minimum": 0}
                    }
                ])

            responses: Dict[str, Any] = {}
            if method == "post":
                success_code = "201"
                responses[success_code] = {
                    "description": "Resource created successfully",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{ep.response_schema or 'ErrorResponse'}"
                            }
                        }
                    }
                }
            elif method == "delete":
                success_code = "204"
                responses[success_code] = {"description": "Resource deleted successfully"}
            else:
                success_code = "200"
                responses[success_code] = {
                    "description": "Successful operation",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{ep.response_schema or 'ErrorResponse'}"
                            }
                        }
                    }
                }

            # Standard errors
            responses["400"] = {
                "description": "Bad Request / Validation Failure",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
            }
            if ep.auth_required:
                responses["401"] = {
                    "description": "Unauthorized / Missing Token",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
                }
            if "{" in path_key:
                responses["404"] = {
                    "description": "Resource Not Found",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
                }

            operation: Dict[str, Any] = {
                "operationId": op_id,
                "summary": ep.summary,
                "description": ep.description or ep.summary,
                "tags": [path_key.strip("/").split("/")[0].capitalize()],
                "parameters": parameters,
                "responses": responses
            }

            if ep.auth_required:
                operation["security"] = [{"bearerAuth": []}]

            if method in ("post", "put", "patch") and ep.request_schema:
                body_schema = (
                    {"$ref": f"#/components/schemas/{ep.request_schema}"}
                    if isinstance(ep.request_schema, str)
                    else ep.request_schema
                )
                operation["requestBody"] = {
                    "required": True,
                    "description": "Payload data",
                    "content": {
                        "application/json": {
                            "schema": body_schema
                        }
                    }
                }

            paths[path_key][method] = operation

        return {
            "openapi": "3.1.0",
            "info": {
                "title": reqs.title,
                "version": reqs.version,
                "description": reqs.description
            },
            "servers": [{"url": "http://localhost:8000", "description": "Local Development Server"}],
            "paths": paths,
            "components": {
                "schemas": schemas,
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "Enter JWT Bearer token"
                    }
                }
            }
        }
