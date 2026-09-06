"""API Review Agent coordinating linting, semantic review, scoring, and refinement."""

from __future__ import annotations
import copy
import logging
from typing import Optional
from apiforge.core.llm import BaseLLMClient
from apiforge.core.state import APIForgeState
from apiforge.agents.review_agent.linter import OASLinter
from apiforge.agents.review_agent.semantic import SemanticReviewer
from apiforge.agents.review_agent.scoring import calculate_quality_score
from apiforge.agents.review_agent.refiner import OASRefiner

logger = logging.getLogger(__name__)


class APIReviewAgent:
    """The central review module evaluating and iteratively refining OpenAPI specs."""

    def __init__(self, llm: BaseLLMClient, max_iterations: int = 3, pass_threshold: float = 80.0):
        self.llm = llm
        self.max_iterations = max_iterations
        self.pass_threshold = pass_threshold
        self.linter = OASLinter()
        self.semantic = SemanticReviewer(llm)
        self.refiner = OASRefiner()

    def run(self, state: APIForgeState) -> APIForgeState:
        if not state.openapi_spec:
            raise ValueError("State does not contain openapi_spec to review.")

        state.log_trace("APIReviewAgent", "Starting API Review & Audit", iteration=state.review_iterations)

        while state.review_iterations < self.max_iterations:
            # 1. Run Linter
            linter_findings = self.linter.lint(state.openapi_spec)
            
            # 2. Run Semantic Review
            semantic_findings = self.semantic.review(state.openapi_spec)
            
            all_findings = linter_findings + semantic_findings
            state.review_findings = all_findings

            # 3. Calculate Score
            score = calculate_quality_score(all_findings, state.openapi_spec, self.pass_threshold)
            state.quality_scores.append(score)

            state.log_trace(
                "APIReviewAgent",
                f"Review iteration {state.review_iterations + 1} completed",
                score=score.overall_score,
                passed=score.passed_threshold,
                critical_issues=score.findings_count.get("critical", 0),
                warnings=score.findings_count.get("warning", 0),
            )

            # Check if spec meets quality criteria
            if score.passed_threshold:
                state.status = "approved"
                state.log_trace("APIReviewAgent", "OpenAPI specification approved with high quality score")
                break

            # 4. Refine Specification
            state.review_iterations += 1
            if state.review_iterations < self.max_iterations:
                state.log_trace("APIReviewAgent", "Refining specification based on review findings")
                # Save draft
                state.spec_draft_history.append(copy.deepcopy(state.openapi_spec))
                # Apply automated refinement
                state.openapi_spec = self.refiner.refine(state.openapi_spec, all_findings)
            else:
                state.status = "reviewed"
                state.log_trace("APIReviewAgent", "Max review iterations reached")

        return state
