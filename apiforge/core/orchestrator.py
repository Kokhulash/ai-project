"""End-to-end multi-agent orchestrator for APIForge AI."""

from __future__ import annotations
import json
import logging
import os
from typing import Any, Callable, Dict, Optional
import yaml
from apiforge.core.llm import BaseLLMClient, get_llm_client
from apiforge.core.state import APIForgeState
from apiforge.agents.requirement_agent import RequirementAnalysisAgent
from apiforge.agents.generator_agent import APISpecificationGeneratorAgent
from apiforge.agents.review_agent import APIReviewAgent
from apiforge.agents.documentation_agent import DocumentationAgent
from apiforge.agents.codegen_agent import CodeGenerationAgent
from apiforge.agents.testing_agent import TestingAndDebuggingAgent
from apiforge.evaluation.metrics import evaluate_state_metrics

logger = logging.getLogger(__name__)


class APIForgeOrchestrator:
    """Master workflow orchestrator coordinating all specialized agents in APIForge AI."""

    def __init__(
        self,
        llm: Optional[BaseLLMClient] = None,
        max_review_iterations: int = 3,
        max_debug_iterations: int = 3,
        pass_threshold: float = 80.0,
    ):
        self.llm = llm or get_llm_client(provider="auto")
        self.requirement_agent = RequirementAnalysisAgent(self.llm)
        self.generator_agent = APISpecificationGeneratorAgent(self.llm)
        self.review_agent = APIReviewAgent(
            self.llm,
            max_iterations=max_review_iterations,
            pass_threshold=pass_threshold,
        )
        self.documentation_agent = DocumentationAgent(self.llm)
        self.codegen_agent = CodeGenerationAgent(self.llm)
        self.testing_agent = TestingAndDebuggingAgent(
            self.llm,
            max_debug_iterations=max_debug_iterations,
        )

    def run(
        self,
        requirements: str,
        output_dir: Optional[str] = None,
        on_step_callback: Optional[Callable[[str, APIForgeState], None]] = None,
    ) -> APIForgeState:
        """Executes the full multi-agent APIForge lifecycle from requirements to tested service."""
        state = APIForgeState(raw_requirements=requirements)

        def step(msg: str):
            logger.info(f"[APIForge Workflow] {msg}")
            if on_step_callback:
                on_step_callback(msg, state)

        # Step 1: Requirement Analysis
        step("Analyzing requirements into structured domain models...")
        state = self.requirement_agent.run(state)

        # Step 2: API Specification Generation
        step("Generating initial OpenAPI 3.1 specification draft...")
        state = self.generator_agent.run(state)

        # Step 3: API Review & Iterative Refinement Loop (Core Contribution)
        step("Executing API Review Agent (smell detection, security audit, scoring & refinement)...")
        state = self.review_agent.run(state)

        # Step 4: Documentation Enrichment & Bundling
        step("Enriching specification with examples & generating developer documentation...")
        state = self.documentation_agent.run(state)

        # Step 5: Backend Code Generation
        step("Synthesizing executable FastAPI backend application...")
        state = self.codegen_agent.run(state)

        # Step 6: Testing & Sandbox Self-Repair Loop
        step("Synthesizing Pytest suite and running sandboxed execution...")
        state = self.testing_agent.run(state)

        # Step 7: Research Performance Evaluation
        step("Calculating 8 research evaluation metrics...")
        state.evaluation_metrics = evaluate_state_metrics(state)

        step("APIForge workflow completed successfully!")

        # Export if output_dir specified
        if output_dir:
            self.export_artifacts(state, output_dir)

        return state

    def export_artifacts(self, state: APIForgeState, output_dir: str) -> None:
        """Persists all generated artifacts (OpenAPI spec, code, tests, docs, metrics) to disk."""
        os.makedirs(output_dir, exist_ok=True)

        # 1. OpenAPI Specs (JSON & YAML)
        if state.openapi_spec:
            with open(os.path.join(output_dir, "openapi.json"), "w", encoding="utf-8") as f:
                json.dump(state.openapi_spec, f, indent=2)
            with open(os.path.join(output_dir, "openapi.yaml"), "w", encoding="utf-8") as f:
                yaml.dump(state.openapi_spec, f, sort_keys=False)

        # 2. Generated Code
        for rel_path, content in state.generated_code_files.items():
            full_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        # 3. Test Code
        for rel_path, content in state.test_code_files.items():
            full_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        # 4. Documentation
        docs_dir = os.path.join(output_dir, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        for fname, content in state.documentation_files.items():
            # README at root, other docs in docs/
            target_path = os.path.join(output_dir, fname) if fname == "README.md" else os.path.join(docs_dir, fname)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

        # 5. Metrics & Findings
        if state.evaluation_metrics:
            with open(os.path.join(output_dir, "evaluation_metrics.json"), "w", encoding="utf-8") as f:
                json.dump(state.evaluation_metrics.model_dump(), f, indent=2)

        if state.review_findings:
            with open(os.path.join(output_dir, "review_findings.json"), "w", encoding="utf-8") as f:
                json.dump([f.model_dump() for f in state.review_findings], f, indent=2)
                
        if state.test_reports:
            with open(os.path.join(output_dir, "test_reports.json"), "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in state.test_reports], f, indent=2)
                
        if state.traces:
            with open(os.path.join(output_dir, "traces.json"), "w", encoding="utf-8") as f:
                json.dump([t.model_dump() for t in state.traces], f, indent=2)
