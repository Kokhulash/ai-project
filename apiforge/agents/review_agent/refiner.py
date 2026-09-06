"""Automated OAS Refiner for APIForge AI.

Applies systematic architectural repairs and security enhancements to
OpenAPI specifications based on detected review findings.
"""

from __future__ import annotations
import copy
import re
from typing import Any, Dict, List
from apiforge.core.state import ReviewFinding
from apiforge.agents.review_agent.linter import is_plural, IRREGULAR_PLURALS


def to_plural(word: str) -> str:
    word_lower = word.lower()
    if word_lower in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[word_lower]
    if word_lower.endswith("y") and len(word_lower) > 1 and word_lower[-2] not in "aeiou":
        return word[:-1] + "ies"
    if word_lower.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    return word + "s"


def clean_verb_from_segment(segment: str) -> str:
    """Removes common action verbs from path segment."""
    cleaned = re.sub(r"^(get|fetch|retrieve|find|post|create|add|new|put|update|modify|delete|remove|destroy|list)[-_]?", "", segment, flags=re.IGNORECASE)
    cleaned = cleaned.lower().strip("-_")
    return cleaned if cleaned else segment.lower()


class OASRefiner:
    """Refines and repairs an OpenAPI specification to eliminate REST smells."""

    def refine(self, oas: Dict[str, Any], findings: List[ReviewFinding]) -> Dict[str, Any]:
        spec = copy.deepcopy(oas)

        # 1. Ensure Components & Security Schemes
        if "components" not in spec:
            spec["components"] = {}
        if "schemas" not in spec["components"]:
            spec["components"]["schemas"] = {}
        if "securitySchemes" not in spec["components"]:
            spec["components"]["securitySchemes"] = {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JSON Web Token for authorized API calls"
                }
            }

        # 2. Ensure Standard Error Schema
        if "ErrorResponse" not in spec["components"]["schemas"]:
            spec["components"]["schemas"]["ErrorResponse"] = {
                "type": "object",
                "required": ["detail", "status"],
                "properties": {
                    "detail": {"type": "string", "description": "Error details"},
                    "status": {"type": "integer", "description": "HTTP status code"},
                    "code": {"type": "string", "description": "Machine-readable error code"}
                }
            }

        # 3. Standardize and Fix Paths
        old_paths = spec.get("paths", {})
        new_paths: Dict[str, Any] = {}

        for raw_path, path_item in old_paths.items():
            if not isinstance(path_item, dict):
                new_paths[raw_path] = path_item
                continue

            # Remove trailing slash
            fixed_path = raw_path.rstrip("/") if len(raw_path) > 1 else raw_path

            # Clean verbs and normalize pluralization on segments
            segments = [s for s in fixed_path.split("/") if s]
            new_segments = []
            for idx, seg in enumerate(segments):
                if seg.startswith("{") and seg.endswith("}"):
                    new_segments.append(seg)
                else:
                    # Clean verb
                    cleaned = clean_verb_from_segment(seg)
                    # Pluralize root resource or collection
                    if idx == 0 and not is_plural(cleaned):
                        cleaned = to_plural(cleaned)
                    new_segments.append(cleaned)

            reconstructed_path = "/" + "/".join(new_segments)

            # Refine operations within path
            refined_path_item: Dict[str, Any] = {}
            template_params = re.findall(r"\{([a-zA-Z0-9_]+)\}", reconstructed_path)

            for method, op in path_item.items():
                if method.lower() not in ("get", "post", "put", "patch", "delete", "head", "options"):
                    refined_path_item[method] = op
                    continue
                if not isinstance(op, dict):
                    refined_path_item[method] = op
                    continue

                refined_op = copy.deepcopy(op)
                m = method.upper()

                # Ensure operationId
                if not refined_op.get("operationId"):
                    clean_id = reconstructed_path.replace("/", "_").replace("{", "").replace("}", "").strip("_")
                    refined_op["operationId"] = f"{method.lower()}_{clean_id}"

                # Ensure tags
                if not refined_op.get("tags") and segments:
                    tag_name = new_segments[0].capitalize()
                    refined_op["tags"] = [tag_name]

                # Ensure summary & description
                if not refined_op.get("summary"):
                    refined_op["summary"] = f"{m} {reconstructed_path}"
                if not refined_op.get("description"):
                    refined_op["description"] = f"Executes {m} operation on {reconstructed_path}."

                # Fix GET requestBody
                if m == "GET" and "requestBody" in refined_op:
                    del refined_op["requestBody"]

                # Fix parameters (path params & pagination)
                params = refined_op.get("parameters", [])
                existing_param_names = {p.get("name") for p in params if isinstance(p, dict)}

                # Add missing path parameters
                for tp in template_params:
                    if tp not in existing_param_names:
                        params.append({
                            "name": tp,
                            "in": "path",
                            "required": True,
                            "description": f"Unique identifier for {tp}",
                            "schema": {"type": "string"}
                        })
                        existing_param_names.add(tp)

                # Add pagination to collection GET
                if m == "GET" and not template_params:
                    if "limit" not in existing_param_names:
                        params.append({
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "description": "Page size limit",
                            "schema": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100}
                        })
                    if "offset" not in existing_param_names:
                        params.append({
                            "name": "offset",
                            "in": "query",
                            "required": False,
                            "description": "Pagination offset",
                            "schema": {"type": "integer", "default": 0, "minimum": 0}
                        })
                refined_op["parameters"] = params

                # Fix security
                if "security" not in refined_op and m in ("POST", "PUT", "PATCH", "DELETE"):
                    if not any(k in reconstructed_path for k in ("login", "token", "register")):
                        refined_op["security"] = [{"bearerAuth": []}]

                # Fix responses
                responses = refined_op.get("responses", {})

                # POST creation -> 201
                if m == "POST" and "200" in responses and "201" not in responses and not reconstructed_path.endswith("/search"):
                    responses["201"] = responses.pop("200")
                    responses["201"]["description"] = "Resource created successfully"

                # DELETE -> 204
                if m == "DELETE":
                    if "200" in responses:
                        del responses["200"]
                    responses["204"] = {"description": "Resource deleted successfully"}

                # Standard error responses
                error_ref = {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}
                if m in ("POST", "PUT", "PATCH"):
                    if "400" not in responses:
                        responses["400"] = {"description": "Bad Request / Validation Failure", "content": error_ref}
                    if "422" not in responses:
                        responses["422"] = {"description": "Unprocessable Entity", "content": error_ref}

                if template_params and "404" not in responses:
                    responses["404"] = {"description": "Resource Not Found", "content": error_ref}

                if refined_op.get("security") and "401" not in responses:
                    responses["401"] = {"description": "Unauthorized Access", "content": error_ref}

                refined_op["responses"] = responses
                refined_path_item[method] = refined_op

            new_paths[reconstructed_path] = refined_path_item

        spec["paths"] = new_paths
        return spec
