"""Semantic & Security Auditor using LLM reasoning for deep API review."""

from __future__ import annotations
import json
import logging
from typing import Any, Dict, List
from apiforge.core.llm import BaseLLMClient
from apiforge.core.state import ReviewFinding

logger = logging.getLogger(__name__)

SEMANTIC_AUDIT_PROMPT = """You are a Principal Security & REST Architecture Auditor.
Perform a semantic and security review of the following OpenAPI 3.1 specification.

Check for:
1. Business logic consistency across related endpoints (e.g. parent-child resource hierarchies).
2. Missing authorization scopes or role checks on sensitive operations.
3. Information disclosure risks in error responses or schema fields (e.g. exposed password hashes or internal IDs).
4. Idempotency guarantees for PUT and DELETE methods.

Return ONLY a JSON list of findings matching:
[
  {
    "rule_id": "SEM-001 | SEC-101 | BIZ-001",
    "category": "security | rest_compliance | schema_completeness",
    "severity": "critical | warning | info",
    "path": "paths./resource.method",
    "message": "Detailed description of the subtle issue",
    "recommendation": "Concrete remediation advice"
  }
]
If the specification is already well-designed with no major semantic flaws, return an empty array [].
"""


class SemanticReviewer:
    """Performs higher-order semantic and security analysis using LLM reasoning."""

    def __init__(self, llm: BaseLLMClient):
        self.llm = llm

    def review(self, oas: Dict[str, Any]) -> List[ReviewFinding]:
        prompt = f"""OpenAPI Specification to audit:
----------------------------------------
{json.dumps(oas, indent=2)[:6000]}
----------------------------------------
Perform semantic and security audit:"""

        try:
            items = self.llm.generate_json(prompt, system_prompt=SEMANTIC_AUDIT_PROMPT)
            if isinstance(items, list):
                findings = []
                for it in items:
                    if isinstance(it, dict) and "rule_id" in it and "message" in it:
                        findings.append(ReviewFinding(
                            rule_id=it.get("rule_id", "SEM-001"),
                            category=it.get("category", "security"),
                            severity=it.get("severity", "warning"),
                            path=it.get("path", "openapi"),
                            message=it.get("message", ""),
                            recommendation=it.get("recommendation", "")
                        ))
                return findings
        except Exception as e:
            logger.info(f"Semantic audit skipped or returned non-JSON ({e}). Relying on deterministic linter.")

        return []
