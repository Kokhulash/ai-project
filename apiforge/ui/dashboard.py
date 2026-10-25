"""Streamlit Dashboard for APIForge AI Multi-Agent Framework."""

from __future__ import annotations
import json
import os
import streamlit as st
try:
    import pandas as pd
except ImportError:
    pd = None
from apiforge.core.llm import get_llm_client
from apiforge.core.orchestrator import APIForgeOrchestrator
from apiforge.core.state import APIForgeState, ReviewFinding, EvaluationMetricsModel, AgentTrace, TestExecutionReport
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
            
    test_reports = []
    tests_path = os.path.join(dir_path, "test_reports.json")
    if os.path.exists(tests_path):
        with open(tests_path, "r", encoding="utf-8") as f:
            test_reports = [TestExecutionReport.model_validate(x) for x in json.load(f)]
            
    traces = []
    traces_path = os.path.join(dir_path, "traces.json")
    if os.path.exists(traces_path):
        with open(traces_path, "r", encoding="utf-8") as f:
            traces = [AgentTrace.model_validate(x) for x in json.load(f)]

    code_files = {}
    app_dir = os.path.join(dir_path, "app")
    if os.path.exists(app_dir):
        for root, _, files in os.walk(app_dir):
            for file in files:
                if not file.endswith((".py", ".json", ".yaml", ".yml", ".md", ".txt", ".html")):
                    continue
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, dir_path).replace("\\", "/")
                with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                    code_files[rel_p] = f.read()

    test_files = {}
    tests_dir = os.path.join(dir_path, "tests")
    if os.path.exists(tests_dir):
        for root, _, files in os.walk(tests_dir):
            for file in files:
                if not file.endswith((".py", ".json", ".yaml", ".yml", ".md", ".txt", ".html")):
                    continue
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, dir_path).replace("\\", "/")
                with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                    test_files[rel_p] = f.read()

    doc_files = {}
    docs_dir = os.path.join(dir_path, "docs")
    if os.path.exists(docs_dir):
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if not file.endswith((".py", ".json", ".yaml", ".yml", ".md", ".txt", ".html")):
                    continue
                full_p = os.path.join(root, file)
                with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
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
        test_reports=test_reports,
        traces=traces,
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
st.sidebar.subheader("📂 Select Project Folder")

# Auto-detect directories containing openapi.json
detected_folders = []
for item in os.listdir("."):
    full_path = os.path.join(".", item)
    if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "openapi.json")):
        detected_folders.append(f"./{item}")

if not detected_folders:
    detected_folders = ["./demo_healthcare_api"]

selected_folder = st.sidebar.selectbox(
    "Available API Project Folders:",
    options=detected_folders,
    index=0,
)

if st.sidebar.button("📂 Load Selected Folder", width='stretch'):
    loaded_state = load_project_from_dir(selected_folder)
    if loaded_state:
        st.session_state.pipeline_state = loaded_state
        st.sidebar.success(f"✓ Loaded: {selected_folder}")
    else:
        st.sidebar.error("Could not load selected directory.")

# Native Windows File Explorer Folder Picker
try:
    import tkinter as tk
    from tkinter import filedialog
    HAS_TK = True
except Exception:
    HAS_TK = False

if HAS_TK:
    if st.sidebar.button("🖥️ Browse Folder in Windows...", width='stretch'):
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)
        folder_path = filedialog.askdirectory()
        root.destroy()
        if folder_path:
            loaded_state = load_project_from_dir(folder_path)
            if loaded_state:
                st.session_state.pipeline_state = loaded_state
                st.sidebar.success(f"✓ Loaded: {os.path.basename(folder_path)}")
            else:
                st.sidebar.error("Selected directory does not contain valid openapi.json")

# Auto-load demo healthcare API on initial launch if nothing in session state
if "pipeline_state" not in st.session_state or st.session_state.pipeline_state is None:
    if os.path.exists("./demo_healthcare_api/openapi.json"):
        st.session_state.pipeline_state = load_project_from_dir("./demo_healthcare_api")
    else:
        st.session_state.pipeline_state = None

if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = None

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🚀 Workflow & Spec",
    "🔍 API Review & Diff",
    "💻 Generated Backend",
    "🧪 Test Execution",
    "📊 Research Metrics",
    "📈 Benchmark Suite",
    "🤖 Agent Insights",
])

# ----------------- Tab 1: Workflow Runner & Spec -----------------
with tab1:
    st.subheader("1. Requirements & Generation")
    default_text = BENCHMARK_DATASETS.get(preset_choice, "Design a Healthcare Clinic Patient and Appointment Management API.")
    req_input = st.text_area("Enter natural language requirements:", value=default_text, height=140)

    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        run_button = st.button("▶ Run Multi-Agent Pipeline", type="primary", width='stretch')

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
        # Build Endpoints Catalog list first for accurate metrics & display
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

        st.divider()
        st.subheader("Validated OpenAPI 3.1 Specification")
        c1, c2, c3, c4 = st.columns(4)
        c1.text(f"API Title: {state.openapi_spec.get('info', {}).get('title', 'N/A')}")
        c2.metric("API Version", state.openapi_spec.get("info", {}).get("version", "1.0.0"))
        c3.metric("Total Endpoints", len(paths_list) if paths_list else len(state.openapi_spec.get("paths", {})))
        score_val = f"{state.quality_scores[-1].overall_score}/100" if state.quality_scores else "N/A"
        c4.metric("Review Quality Score", score_val)

        # Endpoints Table
        if paths_list:
            st.write("#### Endpoint Catalog")
            if pd:
                df = pd.DataFrame(paths_list)
                df.index = range(1, len(df) + 1)
                st.dataframe(df, width='stretch')
            else:
                st.json(paths_list)

        # Interactive Documentation Preview
        if "swagger.html" in state.documentation_files:
            st.write("#### Interactive Swagger UI Documentation")
            with st.expander("Expand Interactive Swagger UI Embed", expanded=False):
                st.iframe(state.documentation_files["swagger.html"], height=600)

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
            if pd:
                st.dataframe(pd.DataFrame(findings_data), width='stretch')
            else:
                st.table(findings_data)
                
            # Add Scores Table (User Requested)
            st.write("#### Detailed Quality Scores Breakdown")
            scores_table = [
                {"Category": "Overall Quality Score", "Score": f"{latest_score.overall_score}/100"},
                {"Category": "REST Compliance", "Score": f"{latest_score.rest_compliance_score}%"},
                {"Category": "Schema Completeness", "Score": f"{latest_score.schema_completeness_score}%"},
                {"Category": "Security Score", "Score": f"{latest_score.security_score}%"},
                {"Category": "Documentation Score", "Score": f"{latest_score.documentation_score}%"},
            ]
            if pd:
                st.dataframe(pd.DataFrame(scores_table), width='stretch', hide_index=True)
            else:
                st.table(scores_table)
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
            if pd:
                st.dataframe(pd.DataFrame(test_items_data), width='stretch')
            else:
                st.table(test_items_data)

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
        if pd:
            st.bar_chart(df_metrics.set_index("Metric"))
        else:
            st.json(df_metrics)
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
        if pd:
            st.dataframe(pd.DataFrame(table_rows), width='stretch')
        else:
            st.table(table_rows)

# ----- Agent Insights Tab -----
with tab7:
    st.subheader("🤖 Agent Execution Insights")
    st.write("Select an agent below to view what it accomplished during the pipeline execution.")
    
    if state:
        agent_tab1, agent_tab2, agent_tab3, agent_tab4, agent_tab5, agent_tab6 = st.tabs([
            "🗂️ Planning Agent",
            "📐 Generator Agent",
            "🔍 Review Agent",
            "📝 Documentation Agent",
            "🛠️ Coding Agent",
            "🔧 Debugging Agent",
        ])

        # Helper function to render traces for an agent
        def render_agent_traces(agent_name_keywords):
            if hasattr(state, 'traces') and state.traces:
                matching = [t for t in state.traces if any(k.lower() in t.agent_name.lower() for k in agent_name_keywords)]
                if matching:
                    st.write("**Action Log:**")
                    for t in matching:
                        st.markdown(f"- **{t.action}**")
                        if t.details:
                            for k, v in t.details.items():
                                label = k.replace("_", " ").title()
                                if isinstance(v, list):
                                    st.markdown(f"  - *{label}*: {', '.join(map(str, v)) if v else 'None'}")
                                elif isinstance(v, dict):
                                    st.markdown(f"  - *{label}*: {json.dumps(v)}")
                                else:
                                    st.markdown(f"  - *{label}*: `{v}`")

        # 1. Planning Agent
        with agent_tab1:
            st.markdown("### 🗂️ Planning & Requirement Analysis Agent")
            reqs = state.structured_requirements
            if reqs:
                st.markdown(f"**API Title:** `{reqs.title}` (v{reqs.version})")
                st.markdown(f"**Authentication Scheme:** `{reqs.auth_type}`")
                if reqs.description:
                    st.markdown(f"**Description:** {reqs.description}")

                if reqs.entities:
                    st.markdown("#### Planned Domain Entities")
                    entity_rows = []
                    for e in reqs.entities:
                        fields_str = ", ".join([f"{k}: {v}" for k, v in e.fields.items()]) if e.fields else "None"
                        entity_rows.append({"Entity": e.name, "Description": e.description, "Fields": fields_str})
                    if pd:
                        st.dataframe(pd.DataFrame(entity_rows), width='stretch', hide_index=True)
                    else:
                        st.table(entity_rows)

                if reqs.endpoints:
                    st.markdown("#### Planned API Endpoints")
                    ep_rows = []
                    for ep in reqs.endpoints:
                        ep_rows.append({
                            "Method": ep.method.upper(),
                            "Path": ep.path,
                            "Summary": ep.summary,
                            "Auth Required": "Yes" if ep.auth_required else "No"
                        })
                    if pd:
                        st.dataframe(pd.DataFrame(ep_rows), width='stretch', hide_index=True)
                    else:
                        st.table(ep_rows)

                if reqs.business_rules:
                    st.markdown("#### Business Rules")
                    for rule in reqs.business_rules:
                        st.markdown(f"- {rule}")
            else:
                st.info("Raw requirements analyzed. Structured requirements will appear here after execution.")
            
            st.divider()
            render_agent_traces(["requirement", "planning"])

        # 2. Generator Agent
        with agent_tab2:
            st.markdown("### 📐 API Specification Generator Agent")
            if state.openapi_spec:
                spec = state.openapi_spec
                info = spec.get("info", {})
                paths = spec.get("paths", {})
                schemas = spec.get("components", {}).get("schemas", {})
                st.markdown(f"**OpenAPI Version:** `{spec.get('openapi', '3.1.0')}`")
                st.markdown(f"**Title:** `{info.get('title', 'N/A')}`")
                st.markdown(f"**Endpoints Generated:** `{len(paths)}` paths")
                st.markdown(f"**Schemas Generated:** `{len(schemas)}` models ({', '.join(schemas.keys())})")
            else:
                st.info("No OpenAPI spec generated yet.")
            
            st.divider()
            render_agent_traces(["generator", "specification"])

        # 3. Review Agent
        with agent_tab3:
            st.markdown("### 🔍 API Quality & Security Review Agent")
            st.markdown(f"**Review Iterations Performed:** `{state.review_iterations}`")
            if state.quality_scores:
                latest = state.quality_scores[-1]
                st.markdown(f"**Overall Quality Score:** `{latest.overall_score}/100` (Passed: `{latest.passed_threshold}`)")
            if state.review_findings:
                st.markdown("#### Smells & Vulnerabilities Addressed")
                findings_summary = [
                    {"Severity": f.severity.upper(), "Path": f.path, "Issue": f.message, "Recommendation": f.recommendation}
                    for f in state.review_findings
                ]
                if pd:
                    st.dataframe(pd.DataFrame(findings_summary), width='stretch', hide_index=True)
                else:
                    st.table(findings_summary)
            else:
                st.success("✓ No design smells detected.")
            
            st.divider()
            render_agent_traces(["review", "audit"])

        # 4. Documentation Agent
        with agent_tab4:
            st.markdown("### 📝 Documentation Agent")
            if state.documentation_files:
                st.markdown("**Generated Documentation Files:**")
                for fname in state.documentation_files.keys():
                    st.markdown(f"- 📄 `{fname}`")
            else:
                st.info("No documentation generated yet.")
            
            st.divider()
            render_agent_traces(["documentation"])

        # 5. Coding Agent
        with agent_tab5:
            st.markdown("### 🛠️ Code Generation Agent")
            if state.generated_code_files:
                st.markdown("**Synthesized FastAPI Application Files:**")
                for fpath in state.generated_code_files.keys():
                    st.markdown(f"- 🐍 `{fpath}`")
            else:
                st.info("No code generated yet.")
            
            st.divider()
            render_agent_traces(["code", "codegen"])

        # 6. Debugging Agent
        with agent_tab6:
            st.markdown("### 🔧 Testing & Debugging Agent")
            st.markdown(f"**Debug Repair Iterations:** `{state.debug_iterations}`")
            if state.test_code_files:
                st.markdown("**Synthesized Pytest Files:**")
                for fpath in state.test_code_files.keys():
                    st.markdown(f"- 🧪 `{fpath}`")
            if state.test_reports:
                latest_report = state.test_reports[-1]
                st.markdown(f"**Test Results:** {latest_report.passed}/{latest_report.total_tests} passed (Success: `{latest_report.success}`)")
            else:
                st.info("No test reports available yet.")
            
            st.divider()
            render_agent_traces(["test", "debug", "sandbox"])
    else:
        st.info("No agent traces are available yet. Run the multi-agent pipeline in Tab 1 to see insights.")

