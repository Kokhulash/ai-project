"""Testing and Debugging Agent coordinating test generation, sandbox execution, and repair."""

from __future__ import annotations
import logging
from apiforge.core.llm import BaseLLMClient
from apiforge.core.state import APIForgeState
from apiforge.agents.testing_agent.test_generator import TestGeneratorAgent
from apiforge.agents.testing_agent.sandbox_runner import SandboxRunner
from apiforge.agents.testing_agent.debugger_agent import DebuggerAgent

logger = logging.getLogger(__name__)


class TestingAndDebuggingAgent:
    """Coordinates test synthesis, sandbox test execution, and iterative self-repair."""

    def __init__(self, llm: BaseLLMClient, max_debug_iterations: int = 3):
        self.llm = llm
        self.max_debug_iterations = max_debug_iterations
        self.generator = TestGeneratorAgent(llm)
        self.runner = SandboxRunner()
        self.debugger = DebuggerAgent(llm)

    def run(self, state: APIForgeState) -> APIForgeState:
        if not state.openapi_spec or not state.generated_code_files:
            raise ValueError("State must contain openapi_spec and generated_code_files for testing.")

        # 1. Synthesize tests
        state = self.generator.run(state)

        # 2. Execute test suite
        state.log_trace("TestingAndDebuggingAgent", "Running sandbox execution and automated tests")
        report = self.runner.run_tests(state.generated_code_files, state.test_code_files)
        state.test_reports.append(report)

        state.log_trace(
            "TestingAndDebuggingAgent",
            f"Test execution round completed",
            total=report.total_tests,
            passed=report.passed,
            failed=report.failed,
            errors=report.errors,
            success=report.success,
        )

        # 3. Debugging self-repair loop if needed
        while not report.success and state.debug_iterations < self.max_debug_iterations:
            state.debug_iterations += 1
            state.log_trace(
                "TestingAndDebuggingAgent",
                f"Initiating debug repair loop iteration {state.debug_iterations}",
            )
            state.generated_code_files = self.debugger.debug_and_repair(
                state.generated_code_files, report, iteration=state.debug_iterations
            )
            # Re-run tests
            report = self.runner.run_tests(state.generated_code_files, state.test_code_files)
            state.test_reports.append(report)
            state.log_trace(
                "TestingAndDebuggingAgent",
                f"Post-repair test execution: {report.passed}/{report.total_tests} passed",
            )
            if report.success:
                break

        state.status = "completed" if report.success else "tested"
        return state
