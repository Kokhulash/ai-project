"""Requirement Analysis Agent for APIForge AI.

Extracts structured domain entities, fields, relationships, endpoints, 
authentication requirements, and business rules from natural language specifications.
"""

from __future__ import annotations
import json
import logging
from typing import Optional
from apiforge.core.llm import BaseLLMClient
from apiforge.core.state import (
    APIForgeState,
    StructuredRequirements,
    RequirementEntity,
    RequirementEndpoint,
)

logger = logging.getLogger(__name__)

REQUIREMENT_SYSTEM_PROMPT = """You are a Principal API Architect and Requirements Engineer.
Analyze the user's software requirements and extract a rigorous, structured API specification definition.

Your output MUST be a valid JSON object matching this schema:
{
  "title": "Clear concise API Name",
  "version": "1.0.0",
  "description": "Comprehensive description of API scope and purpose",
  "auth_type": "bearer | api_key | oauth2 | none",
  "entities": [
    {
      "name": "EntityName (Singular PascalCase)",
      "description": "Entity purpose",
      "fields": {"fieldName": "string|integer|boolean|number|datetime|uuid"},
      "relationships": ["OtherEntityName"]
    }
  ],
  "endpoints": [
    {
      "path": "/plural-resource or /plural-resource/{id}/sub-resource",
      "method": "GET | POST | PUT | PATCH | DELETE",
      "summary": "Short action summary",
      "description": "Detailed explanation of operation",
      "auth_required": true | false,
      "request_schema": "EntityCreate | EntityUpdate | null",
      "response_schema": "EntityResponse | EntityListResponse | MessageResponse",
      "expected_status_codes": [200, 201, 400, 401, 404]
    }
  ],
  "business_rules": [
    "Rule 1: constraint or validation rule",
    "Rule 2: access control rule"
  ]
}

Strict REST Rules to remember:
1. Resource names in paths MUST be plural nouns (e.g. /users, /orders, not /user or /order).
2. NEVER include verbs in endpoint paths (e.g. use POST /orders instead of /createOrder).
3. Always include standard error status codes: 400 for bad request, 401 for unauthorized, 404 for not found.
"""


class RequirementAnalysisAgent:
    """Agent responsible for analyzing natural language requirements into structured models."""

    def __init__(self, llm: BaseLLMClient):
        self.llm = llm

    def run(self, state: APIForgeState) -> APIForgeState:
        """Processes raw requirements and populates structured_requirements in state."""
        state.log_trace("RequirementAnalysisAgent", "Starting requirement analysis", raw_length=len(state.raw_requirements))
        prompt = f"""Software Requirements to analyze:
----------------------------------------
{state.raw_requirements}
----------------------------------------

Generate the structured JSON representation according to the schema."""

        try:
            structured_data = self.llm.generate_json(prompt, system_prompt=REQUIREMENT_SYSTEM_PROMPT)
            structured = StructuredRequirements.model_validate(structured_data)
        except Exception as e:
            logger.warning(f"Failed to generate/validate requirements via LLM ({e}). Falling back to heuristic extractor.")
            structured = self._heuristic_fallback(state.raw_requirements)

        state.structured_requirements = structured
        state.status = "analyzed"
        state.log_trace(
            "RequirementAnalysisAgent",
            "Requirements parsed successfully",
            entities_count=len(structured.entities),
            endpoints_count=len(structured.endpoints),
        )
        return state

    def _heuristic_fallback(self, text: str) -> StructuredRequirements:
        """Deterministic heuristic fallback parser when LLM response is unavailable or invalid."""
        title = "API Application Service"
        entities = []
        endpoints = []

        # Guess entities from common keywords
        keywords = ["user", "order", "product", "task", "project", "device", "patient", "item", "customer"]
        found = [k for k in keywords if k in text.lower()]
        if not found:
            found = ["item"]

        for kw in found:
            name = kw.capitalize()
            entities.append(RequirementEntity(
                name=name,
                description=f"Represents a {kw} record",
                fields={
                    "id": "uuid",
                    "title": "string",
                    "status": "string",
                    "created_at": "datetime"
                },
                relationships=[]
            ))
            plural = f"{kw}s" if not kw.endswith("s") else f"{kw}es"
            endpoints.extend([
                RequirementEndpoint(
                    path=f"/{plural}",
                    method="GET",
                    summary=f"List all {plural}",
                    auth_required=True,
                    response_schema=f"{name}ListResponse",
                    expected_status_codes=[200, 401]
                ),
                RequirementEndpoint(
                    path=f"/{plural}",
                    method="POST",
                    summary=f"Create a new {kw}",
                    auth_required=True,
                    request_schema=f"{name}Create",
                    response_schema=f"{name}Response",
                    expected_status_codes=[201, 400, 401]
                ),
                RequirementEndpoint(
                    path=f"/{plural}/{{{kw}_id}}",
                    method="GET",
                    summary=f"Get {kw} by ID",
                    auth_required=True,
                    response_schema=f"{name}Response",
                    expected_status_codes=[200, 401, 404]
                ),
                RequirementEndpoint(
                    path=f"/{plural}/{{{kw}_id}}",
                    method="DELETE",
                    summary=f"Delete a {kw}",
                    auth_required=True,
                    expected_status_codes=[204, 401, 404]
                )
            ])

        return StructuredRequirements(
            title=f"{found[0].capitalize()} Management API",
            version="1.0.0",
            description=f"Generated API based on requirements: {text[:100]}...",
            auth_type="bearer",
            entities=entities,
            endpoints=endpoints,
            business_rules=["All mutations require valid authentication", "IDs must be valid UUIDs"]
        )
