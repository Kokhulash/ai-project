"""Scoring engine for OpenAPI Review Agent.

Computes REST Design Compliance, Schema Completeness, Security Coverage,
Documentation Readiness, and the composite API Quality Score (0-100).
"""

from __future__ import annotations
from typing import Any, Dict, List
from apiforge.core.state import QualityScoreModel, ReviewFinding


def calculate_quality_score(findings: List[ReviewFinding], oas: Dict[str, Any], pass_threshold: float = 80.0) -> QualityScoreModel:
    """Calculates granular and overall API Quality Scores."""
    paths = oas.get("paths", {})
    total_operations = 0
    for p_item in paths.values():
        if isinstance(p_item, dict):
            for m in p_item.keys():
                if m.lower() in ("get", "post", "put", "patch", "delete"):
                    total_operations += 1

    total_operations = max(total_operations, 1)

    # Count findings by category and severity
    cat_counts = {
        "rest_compliance": {"critical": 0, "warning": 0, "info": 0},
        "schema_completeness": {"critical": 0, "warning": 0, "info": 0},
        "security": {"critical": 0, "warning": 0, "info": 0},
        "documentation": {"critical": 0, "warning": 0, "info": 0},
    }
    severity_totals = {"critical": 0, "warning": 0, "info": 0}

    for f in findings:
        cat = f.category if f.category in cat_counts else "rest_compliance"
        sev = f.severity if f.severity in severity_totals else "warning"
        cat_counts[cat][sev] += 1
        severity_totals[sev] += 1

    def compute_category_score(cat: str) -> float:
        c = cat_counts[cat]
        # Weighted deductions normalized by total operations
        deduction = (c["critical"] * 20.0 + c["warning"] * 8.0 + c["info"] * 2.0) / total_operations
        return max(0.0, min(100.0, 100.0 - deduction))

    rest_score = compute_category_score("rest_compliance")
    schema_score = compute_category_score("schema_completeness")
    sec_score = compute_category_score("security")
    doc_score = compute_category_score("documentation")

    # Composite weighted score (REST: 30%, Schema: 25%, Security: 25%, Docs: 20%)
    overall = (
        rest_score * 0.30 +
        schema_score * 0.25 +
        sec_score * 0.25 +
        doc_score * 0.20
    )
    overall = round(overall, 1)

    summary_parts = []
    if severity_totals["critical"] > 0:
        summary_parts.append(f"{severity_totals['critical']} critical issues detected")
    if severity_totals["warning"] > 0:
        summary_parts.append(f"{severity_totals['warning']} warnings")
    if not summary_parts:
        summary_parts.append("Specification meets high REST standards")

    return QualityScoreModel(
        overall_score=overall,
        rest_compliance_score=round(rest_score, 1),
        schema_completeness_score=round(schema_score, 1),
        security_score=round(sec_score, 1),
        documentation_score=round(doc_score, 1),
        summary="; ".join(summary_parts),
        passed_threshold=bool(overall >= pass_threshold and severity_totals["critical"] == 0),
        findings_count=severity_totals,
    )
