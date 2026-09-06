"""Command Line Interface for APIForge AI using Typer and Rich."""

from __future__ import annotations
import json
import os
import subprocess
import sys
from typing import Optional
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from apiforge.core.llm import get_llm_client
from apiforge.core.orchestrator import APIForgeOrchestrator
from apiforge.agents.review_agent import OASLinter, calculate_quality_score, OASRefiner
from apiforge.agents.codegen_agent import CodeGenerationAgent
from apiforge.agents.testing_agent.sandbox_runner import SandboxRunner
from apiforge.agents.testing_agent.test_generator import TestGeneratorAgent
from apiforge.evaluation.benchmark_runner import BenchmarkRunner
from apiforge.core.state import APIForgeState

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = typer.Typer(
    name="apiforge",
    help="APIForge AI: Multi-Agent Framework for API Design, Review, Documentation, and Testing",
    add_completion=False,
)
console = Console(safe_box=True)


@app.command()
def run(
    requirements: str = typer.Argument(..., help="Natural language software requirements or path to .txt/.md file"),
    output_dir: str = typer.Option("./generated_api", "--output-dir", "-o", help="Directory to save generated artifacts"),
    provider: str = typer.Option("auto", "--provider", "-p", help="LLM Provider: auto, gemini, openai, or mock"),
    max_review_iters: int = typer.Option(3, "--max-review", help="Max iterative review loops"),
):
    """Run the complete end-to-end multi-agent APIForge development lifecycle."""
    console.print(Panel.fit(
        "[bold cyan]APIForge AI Multi-Agent Framework[/bold cyan]\n"
        "[dim]Intelligent API Design, Automated Review, Documentation, and Testing[/dim]",
        border_style="cyan"
    ))

    # Check if requirements is a file path
    if os.path.exists(requirements) and os.path.isfile(requirements):
        with open(requirements, "r", encoding="utf-8") as f:
            requirements_text = f.read()
    else:
        requirements_text = requirements

    llm = get_llm_client(provider=provider)
    orchestrator = APIForgeOrchestrator(
        llm=llm,
        max_review_iterations=max_review_iters,
    )

    with console.status("[bold green]Executing multi-agent workflow...") as status:
        def on_step(msg: str, st: APIForgeState):
            status.update(f"[bold green]{msg}[/bold green]")
            console.log(f"[dim]* {msg}[/dim]")

        state = orchestrator.run(
            requirements=requirements_text,
            output_dir=output_dir,
            on_step_callback=on_step,
        )

    console.print(f"\n[bold green][SUCCESS] Generation and Validation Complete![/bold green]")
    console.print(f"Artifacts exported to: [bold underline]{os.path.abspath(output_dir)}[/bold underline]\n")

    # Display Metrics Table
    if state.evaluation_metrics:
        m = state.evaluation_metrics
        table = Table(title="APIForge AI - Performance Evaluation Metrics", border_style="cyan")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right", style="green")

        table.add_row("OpenAPI Validation Accuracy", f"{m.openapi_validation_accuracy}%")
        table.add_row("REST Design Compliance", f"{m.rest_design_compliance}%")
        table.add_row("Documentation Completeness", f"{m.documentation_completeness}%")
        table.add_row("Security Recommendation Coverage", f"{m.security_recommendation_coverage}%")
        table.add_row("API Quality Score", f"{m.api_quality_score} / 100")
        table.add_row("Test Case Success Rate", f"{m.test_case_success_rate}%")
        table.add_row("Execution Reliability", f"{m.execution_reliability}%")
        table.add_row("Error Reduction Rate", f"{m.error_reduction_rate}%")
        console.print(table)


@app.command()
def review(
    spec_path: str = typer.Argument(..., help="Path to OpenAPI JSON or YAML file to review"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Automatically apply automated refiner repairs"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Path to save refined specification"),
):
    """Audit an OpenAPI specification for REST design smells, schema flaws, and security gaps."""
    if not os.path.exists(spec_path):
        console.print(f"[bold red]File not found:[/bold red] {spec_path}")
        raise typer.Exit(1)

    with open(spec_path, "r", encoding="utf-8") as f:
        if spec_path.endswith(".yaml") or spec_path.endswith(".yml"):
            oas = yaml.safe_load(f)
        else:
            oas = json.load(f)

    linter = OASLinter()
    findings = linter.lint(oas)
    score = calculate_quality_score(findings, oas)

    console.print(Panel.fit(
        f"[bold]API Quality Score: {score.overall_score} / 100[/bold]\n"
        f"REST Compliance: {score.rest_compliance_score}% | "
        f"Schema: {score.schema_completeness_score}% | "
        f"Security: {score.security_score}% | "
        f"Docs: {score.documentation_score}%\n"
        f"Status: {'[green]PASSED[/green]' if score.passed_threshold else '[red]NEEDS REFINEMENT[/red]'}",
        title="Review Summary",
        border_style="cyan"
    ))

    if findings:
        table = Table(title="Detected Quality Smells & Violations")
        table.add_column("Rule ID", style="bold cyan")
        table.add_column("Severity")
        table.add_column("Path", style="dim")
        table.add_column("Message")
        table.add_column("Recommendation", style="green")

        for finding in findings:
            sev_color = "red" if finding.severity == "critical" else "yellow" if finding.severity == "warning" else "blue"
            table.add_row(
                finding.rule_id,
                f"[{sev_color}]{finding.severity.upper()}[/{sev_color}]",
                finding.path,
                finding.message,
                finding.recommendation
            )
        console.print(table)
    else:
        console.print("[green][PASS] No architectural or security smells detected![/green]")

    if fix:
        refiner = OASRefiner()
        fixed_oas = refiner.refine(oas, findings)
        new_findings = linter.lint(fixed_oas)
        new_score = calculate_quality_score(new_findings, fixed_oas)
        console.print(f"\n[bold green]Refinement complete! Quality Score improved: {score.overall_score} -> {new_score.overall_score}[/bold green]")
        out_path = output_file or spec_path.replace(".json", "_refined.json").replace(".yaml", "_refined.yaml")
        with open(out_path, "w", encoding="utf-8") as f:
            if out_path.endswith(".yaml") or out_path.endswith(".yml"):
                yaml.dump(fixed_oas, f, sort_keys=False)
            else:
                json.dump(fixed_oas, f, indent=2)
        console.print(f"Refined specification saved to: {out_path}")


@app.command()
def benchmark(
    suite: str = typer.Option("all", "--suite", "-s", help="Benchmark suite: all, ecommerce, healthcare, iot_fleet, task_management"),
    output_report: Optional[str] = typer.Option(None, "--output", "-o", help="Path to save benchmark markdown report"),
    provider: str = typer.Option("mock", "--provider", "-p", help="LLM Provider to evaluate"),
):
    """Run performance benchmarks across standard domain requirement datasets."""
    console.print("[bold cyan]Running APIForge AI Benchmark Evaluation Suite...[/bold cyan]")
    llm = get_llm_client(provider=provider)
    runner = BenchmarkRunner(llm=llm)

    suite_names = None if suite == "all" else [suite]
    results = runner.run_suite(suite_names)
    md_report = runner.generate_markdown_report(results)

    console.print("\n" + md_report)

    if output_report:
        with open(output_report, "w", encoding="utf-8") as f:
            f.write(md_report)
        console.print(f"\n[bold green]Benchmark report saved to:[/bold green] {output_report}")


@app.command()
def ui(
    port: int = typer.Option(8501, "--port", help="Port to bind Streamlit dashboard"),
):
    """Launch the interactive Streamlit Web UI Dashboard."""
    dashboard_path = os.path.join(os.path.dirname(__file__), "ui", "dashboard.py")
    console.print(f"[bold green]Starting APIForge AI Dashboard on port {port}...[/bold green]")
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.port", str(port)]
    subprocess.run(cmd)


if __name__ == "__main__":
    app()
