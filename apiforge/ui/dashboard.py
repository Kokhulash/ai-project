"""Streamlit Dashboard for APIForge AI Multi-Agent Framework."""

from __future__ import annotations
import json
import os
import streamlit as st
import pandas as pd
from apiforge.core.llm import get_llm_client
from apiforge.core.orchestrator import APIForgeOrchestrator
from apiforge.core.state import APIForgeState, ReviewFinding, EvaluationMetricsModel
from apiforge.evaluation.benchmark_runner import BENCHMARK_DATASETS, BenchmarkRunner
from apiforge.agents.review_agent.scoring import calculate_quality_score
from apiforge.agents.testing_agent.sandbox_runner import SandboxRunner

st.set_page_config(
    page_title="APIForge AI Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ APIForge AI")
st.caption("A Multi-Agent Framework for Intelligent API Design, Automated Review, Documentation, and Testing")


def load_project_from_dir(dir_path: str) -> APIForgeState | None:
    """Reconstructs APIForgeState from an existing generated project directory."""
    if not os.path.exists(dir_path):
        return None
    oas_path = os.path.join(dir_path, "openapi.json")
    if not os.path.exists(oas_path):
        return None

    with open(oas_path, "r", encoding="utf-8") as f:
        oas = json.load(f)

    metrics = None
    metrics_path = os.path.join(dir_path, "evaluation_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = EvaluationMetricsModel.model_validate(json.load(f))

    findings = []
    findings_path = os.path.join(dir_path, "review_findings.json")
    if os.path.exists(findings_path):
        with open(findings_path, "r", encoding="utf-8") as f:
            findings = [ReviewFinding.model_validate(x) for x in json.load(f)]

    code_files = {}
    app_dir = os.path.join(dir_path, "app")
    if os.path.exists(app_dir):
        for root, _, files in os.walk(app_dir):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, dir_path).replace("\\", "/")
                with open(full_p, "r", encoding="utf-8") as f:
                    code_files[rel_p] = f.read()

    test_files = {}
    tests_dir = os.path.join(dir_path, "tests")
    if os.path.exists(tests_dir):
        for root, _, files in os.walk(tests_dir):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, dir_path).replace("\\", "/")
                with open(full_p, "r", encoding="utf-8") as f:
                    test_files[rel_p] = f.read()

    doc_files = {}
    docs_dir = os.path.join(dir_path, "docs")
    if os.path.exists(docs_dir):
        for root, _, files in os.walk(docs_dir):
            for file in files:
                full_p = os.path.join(root, file)
                with open(full_p, "r", encoding="utf-8") as f:
                    doc_files[file] = f.read()
    readme_path = os.path.join(dir_path, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            doc_files["README.md"] = f.read()

    q_score = calculate_quality_score(findings, oas)

    return APIForgeState(
        raw_requirements=oas.get("info", {}).get("description", "Loaded from existing project directory"),
        openapi_spec=oas,
        review_findings=findings,
        quality_scores=[q_score],
        generated_code_files=code_files,
        test_code_files=test_files,
        documentation_files=doc_files,
        evaluation_metrics=metrics,
        status="completed"
    )


# Sidebar Configuration
st.sidebar.header("Configuration")
provider = st.sidebar.selectbox("LLM Provider", ["auto", "gemini", "openai", "mock"], index=0)
max_review_iters = st.sidebar.slider("Max Review Iterations", 1, 5, 3)
max_debug_iters = st.sidebar.slider("Max Debug Iterations", 1, 5, 3)
pass_threshold = st.sidebar.slider("Review Pass Threshold", 60, 95, 80)

# Preset Templates
preset_choice = st.sidebar.selectbox(
    "Load Preset Requirement",
    ["Custom"] + list(BENCHMARK_DATASETS.keys()),
    index=0
)

# Load existing project section in sidebar
st.sidebar.divider()
st.sidebar.subheader("📂 Load Project Directory")
default_demo = "./demo_healthcare_api" if os.path.exists("./demo_healthcare_api") else ""
proj_dir_input = st.sidebar.text_input("Project Folder Path", value=default_demo)
if st.sidebar.button("Load Existing API", use_container_width=True):
    loaded_state = load_project_from_dir(proj_dir_input)
    if loaded_state:
        st.session_state.pipeline_state = loaded_state
        st.sidebar.success(f"✓ Loaded: {loaded_state.openapi_spec.get('info', {}).get('title', 'API')}")
    else:
        st.sidebar.error("Directory does not contain valid openapi.json")

# Auto-load demo healthcare API on initial launch if nothing in session state
if "pipeline_state" not in st.session_state or st.session_state.pipeline_state is None:
    if os.path.exists("./demo_healthcare_api/openapi.json"):
        st.session_state.pipeline_state = load_project_from_dir("./demo_healthcare_api")
    else:
        st.session_state.pipeline_state = None

if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = None

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🚀 Workflow & Spec",
    "🔍 API Review & Diff",
    "💻 Generated Backend",
    "🧪 Test Execution",
    "📊 Research Metrics",
    "📈 Benchmark Suite",
])

# ----------------- Tab 1: Workflow Runner & Spec -----------------
with tab1:
    st.subheader("1. Requirements & Generation")
    default_text = BENCHMARK_DATASETS.get(preset_choice, "Design a Healthcare Clinic Patient and Appointment Management API.")
    req_input = st.text_area("Enter natural language requirements:", value=default_text, height=140)

    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        run_button = st.button("▶ Run Multi-Agent Pipeline", type="primary", use_container_width=True)

    if run_button:
        st.info("Executing multi-agent workflow...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        llm = get_llm_client(provider=provider)
        orchestrator = APIForgeOrchestrator(
            llm=llm,
            max_review_iterations=max_review_iters,
            max_debug_iterations=max_debug_iters,
            pass_threshold=float(pass_threshold),
        )

        step_weights = {
            "Requirement": 15,
            "Specification": 35,
            "Review": 55,
            "Documentation": 70,
            "Backend": 85,
            "Testing": 95,
            "completed": 100
        }

        def on_step(msg: str, st_obj):
            for k, w in step_weights.items():
                if k in msg:
                    progress_bar.progress(w)
                    break
            status_text.text(f"Agent Action: {msg}")

        state = orchestrator.run(
            requirements=req_input,
            output_dir="./generated_api",
            on_step_callback=on_step,
        )

        progress_bar.progress(100)
        status_text.text("Workflow finished successfully!")
        st.session_state.pipeline_state = state
        st.success("Artifacts generated and verified successfully!")

    # Display Current Spec
    state = st.session_state.pipeline_state
    if state and state.openapi_spec:
        st.divider()
        st.subheader("Validated OpenAPI 3.1 Specification")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("API Title", state.openapi_spec.get("info", {}).get("title", "N/A"))
        c2.metric("API Version", state.openapi_spec.get("info", {}).get("version", "1.0.0"))
        c3.metric("Total Endpoints", len(state.openapi_spec.get("paths", {})))
        score_val = f"{state.quality_scores[-1].overall_score}/100" if state.quality_scores else "N/A"
        c4.metric("Review Quality Score", score_val)

        # Endpoints Table
        paths_list = []
        for path_str, p_item in state.openapi_spec.get("paths", {}).items():
            if isinstance(p_item, dict):
                for m, op in p_item.items():
                    if m.lower() in ("get", "post", "put", "patch", "delete"):
                        paths_list.append({
                            "Method": m.upper(),
                            "Endpoint Path": path_str,
                            "Summary": op.get("summary", ""),
                            "Secured": "🔒 Bearer" if op.get("security") else "Public",
                            "Responses": ", ".join(op.get("responses", {}).keys())
                        })
        if paths_list:
            st.write("#### Endpoint Catalog")
            st.dataframe(pd.DataFrame(paths_list), use_container_width=True)

        # Interactive Documentation Preview
        if "swagger.html" in state.documentation_files:
            st.write("#### Interactive Swagger UI Documentation")
            with st.expander("Expand Interactive Swagger UI Embed", expanded=False):
                st.components.v1.html(state.documentation_files["swagger.html"], height=600, scrolling=True)

        with st.expander("View Raw OpenAPI 3.1 JSON Specification", expanded=False):
            st.json(state.openapi_spec)

# ----------------- Tab 2: Review & Diff Inspector -----------------
with tab2:
    st.subheader("API Review Agent: Quality & Smell Audit")
    state = st.session_state.pipeline_state
    if state:
        if state.quality_scores:
            latest_score = state.quality_scores[-1]
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Overall Quality Score", f"{latest_score.overall_score}/100")
            m2.metric("REST Compliance", f"{latest_score.rest_compliance_score}%")
            m3.metric("Schema Completeness", f"{latest_score.schema_completeness_score}%")
            m4.metric("Security Score", f"{latest_score.security_score}%")
            m5.metric("Documentation Score", f"{latest_score.documentation_score}%")

        st.write("#### Detected Quality Smells & Applied Remediations")
        if state.review_findings:
            findings_data = [
                {
                    "Rule": f.rule_id,
                    "Severity": f.severity.upper(),
                    "Category": f.category,
                    "Target Path": f.path,
                    "Issue Description": f.message,
                    "Recommendation": f.recommendation,
                }
                for f in state.review_findings
            ]
            st.dataframe(pd.DataFrame(findings_data), use_container_width=True)
        else:
            st.success("✓ Excellent! No architectural, syntactic, or security smells detected. Full REST compliance.")

        if state.spec_draft_history:
            st.write("#### Specification Evolution Across Review Iterations")
            st.write(f"Refinement cycles performed: **{len(state.spec_draft_history)}**")
            col_draft, col_final = st.columns(2)
            with col_draft:
                st.write("**Initial Unreviewed Draft (Endpoints)**")
                st.json(list(state.spec_draft_history[0].get("paths", {}).keys()))
            with col_final:
                st.write("**Final Refined Specification (Endpoints)**")
                st.json(list(state.openapi_spec.get("paths", {}).keys()))
    else:
        st.info("Run the pipeline in Tab 1 or load an existing project from the sidebar.")

# ----------------- Tab 3: Generated Code -----------------
with tab3:
    st.subheader("Generated FastAPI Backend & Test Implementation")
    state = st.session_state.pipeline_state
    if state and (state.generated_code_files or state.test_code_files):
        all_files = {**state.generated_code_files, **state.test_code_files}
        selected_file = st.selectbox("Select File to View", list(all_files.keys()))
        code_content = all_files[selected_file]
        st.code(code_content, language="python" if selected_file.endswith(".py") else "text")
    else:
        st.info("No generated code files loaded. Run the pipeline in Tab 1 or load a project directory.")

# ----------------- Tab 4: Test Execution -----------------
with tab4:
    st.subheader("Sandboxed Pytest Execution & Self-Repair Logs")
    state = st.session_state.pipeline_state
    if state and state.generated_code_files and state.test_code_files:
        col_run_test, _ = st.columns([1, 4])
        with col_run_test:
            if st.button("▶ Run Sandboxed Tests Now", type="primary"):
                runner = SandboxRunner()
                with st.spinner("Executing test suite against FastAPI service in sandbox..."):
                    report = runner.run_tests(state.generated_code_files, state.test_code_files)
                    state.test_reports.append(report)
                    st.success("Test execution completed!")

        if state.test_reports:
            latest_report = state.test_reports[-1]
            t1, t2, t3, t4 = st.columns(4)
            t1.metric("Total Tests", latest_report.total_tests)
            t2.metric("Passed Tests", latest_report.passed)
            t3.metric("Failed Tests", latest_report.failed)
            t4.metric("Execution Duration", f"{latest_report.duration_sec}s")

            st.write("#### Individual Test Case Results")
            test_items_data = [
                {"Test Case": it.test_name, "Status": it.status, "Duration (s)": it.duration_sec, "Failure Details": it.error_message or "None"}
                for it in latest_report.items
            ]
            st.dataframe(pd.DataFrame(test_items_data), use_container_width=True)

            st.write("#### Sandbox Console Logs")
            st.text_area("Console Output", latest_report.logs, height=200)
    else:
        st.info("No test files available. Load a project or run the pipeline first.")

# ----------------- Tab 5: Research Metrics -----------------
with tab5:
    st.subheader("Project Research Performance Metrics")
    state = st.session_state.pipeline_state
    if state and state.evaluation_metrics:
        m = state.evaluation_metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("1. OAS Validation Accuracy", f"{m.openapi_validation_accuracy}%")
        c2.metric("2. REST Design Compliance", f"{m.rest_design_compliance}%")
        c3.metric("3. Docs Completeness", f"{m.documentation_completeness}%")
        c4.metric("4. Security Coverage", f"{m.security_recommendation_coverage}%")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("5. API Quality Score", f"{m.api_quality_score}/100")
        c6.metric("6. Test Success Rate", f"{m.test_case_success_rate}%")
        c7.metric("7. Execution Reliability", f"{m.execution_reliability}%")
        c8.metric("8. Error Reduction Rate", f"{m.error_reduction_rate}%")

        # Metric Chart
        df_metrics = pd.DataFrame({
            "Metric": [
                "OAS Validation Accuracy",
                "REST Compliance",
                "Docs Completeness",
                "Security Coverage",
                "Quality Score",
                "Test Success Rate",
                "Execution Reliability",
                "Error Reduction Rate"
            ],
            "Score (%)": [
                m.openapi_validation_accuracy,
                m.rest_design_compliance,
                m.documentation_completeness,
                m.security_recommendation_coverage,
                m.api_quality_score,
                m.test_case_success_rate,
                m.execution_reliability,
                m.error_reduction_rate
            ]
        })
        st.bar_chart(df_metrics.set_index("Metric"))
    else:
        st.info("No evaluation metrics computed yet. Run the pipeline in Tab 1.")

# ----------------- Tab 6: Benchmark Suite -----------------
with tab6:
    st.subheader("Run Academic Multi-Domain Benchmark Suite")
    st.write("Evaluate APIForge AI against 4 academic domains: E-Commerce, Healthcare, IoT Fleet, and Task Management.")

    if st.button("⚡ Execute Full Benchmark Suite", type="primary"):
        with st.spinner("Evaluating all 4 benchmark suites..."):
            runner = BenchmarkRunner(llm=get_llm_client(provider="mock"))
            results = runner.run_suite()
            st.session_state.benchmark_results = results

    if st.session_state.benchmark_results:
        b_res = st.session_state.benchmark_results
        suites = b_res.get("suites", {})
        avgs = b_res.get("aggregate_averages", {})

        st.success(f"Successfully evaluated {b_res.get('total_suites_evaluated')} benchmark domains!")

        table_rows = []
        metric_keys = [
            ("openapi_validation_accuracy", "OAS Validation Accuracy (%)"),
            ("rest_design_compliance", "REST Compliance (%)"),
            ("documentation_completeness", "Documentation Completeness (%)"),
            ("security_recommendation_coverage", "Security Coverage (%)"),
            ("api_quality_score", "API Quality Score (0-100)"),
            ("test_case_success_rate", "Test Success Rate (%)"),
            ("execution_reliability", "Execution Reliability (%)"),
            ("error_reduction_rate", "Error Reduction Rate (%)"),
        ]

        for mk, label in metric_keys:
            row = {"Metric": label}
            for sname, sdata in suites.items():
                row[sname.capitalize()] = sdata["metrics"].get(mk, 0)
            row["Average"] = avgs.get(mk, 0)
            table_rows.append(row)

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
