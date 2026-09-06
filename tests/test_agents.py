"""Unit tests for individual agents in APIForge AI."""

import pytest
from apiforge.core.llm import MockLLMClient
from apiforge.core.state import APIForgeState
from apiforge.agents.requirement_agent import RequirementAnalysisAgent
from apiforge.agents.generator_agent import APISpecificationGeneratorAgent
from apiforge.agents.review_agent import APIReviewAgent
from apiforge.agents.documentation_agent import DocumentationAgent
from apiforge.agents.codegen_agent import CodeGenerationAgent


def test_agent_pipeline_phases():
    llm = MockLLMClient()
    state = APIForgeState(raw_requirements="Design a Task Tracking REST API with projects and tasks.")

    # 1. Requirement Agent
    req_agent = RequirementAnalysisAgent(llm)
    state = req_agent.run(state)
    assert state.structured_requirements is not None
    assert len(state.structured_requirements.entities) > 0

    # 2. Generator Agent
    gen_agent = APISpecificationGeneratorAgent(llm)
    state = gen_agent.run(state)
    assert state.openapi_spec is not None
    assert "openapi" in state.openapi_spec
    assert "/projects" in state.openapi_spec["paths"]

    # 3. Review Agent
    rev_agent = APIReviewAgent(llm, max_iterations=2)
    state = rev_agent.run(state)
    assert len(state.quality_scores) > 0
    assert state.quality_scores[-1].overall_score >= 80.0

    # 4. Documentation Agent
    doc_agent = DocumentationAgent(llm)
    state = doc_agent.run(state)
    assert "README.md" in state.documentation_files
    assert "swagger.html" in state.documentation_files
    assert "redoc.html" in state.documentation_files

    # 5. Code Generation Agent
    code_agent = CodeGenerationAgent(llm)
    state = code_agent.run(state)
    assert "app/main.py" in state.generated_code_files
    assert "app/models.py" in state.generated_code_files
    assert "app/database.py" in state.generated_code_files
