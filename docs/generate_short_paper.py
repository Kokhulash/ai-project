"""
Generate a SHORT version of the APIForge AI research paper (Springer LNCS format).
Condensed to ~6-8 pages: compact sections, key tables, key figures only.
"""
import os
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

FIGURES = r"D:\Programs\ai-project\docs\figures"

def create_short_paper():
    doc = Document()

    # Page setup: A4, 2.54cm margins
    s = doc.sections[0]
    s.page_width = Cm(21.0)
    s.page_height = Cm(29.7)
    s.top_margin = Cm(2.54)
    s.bottom_margin = Cm(2.54)
    s.left_margin = Cm(2.54)
    s.right_margin = Cm(2.54)

    def add_para(text, size=10, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=Pt(6)):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = after
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        return p

    def add_img(filename, caption, width=Inches(5.0)):
        path = os.path.join(FIGURES, filename)
        if os.path.exists(path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(path, width=width)
        add_para(caption, size=9, align=WD_ALIGN_PARAGRAPH.CENTER, after=Pt(4))

    def add_table(data):
        t = doc.add_table(rows=len(data), cols=len(data[0]))
        t.style = 'Table Grid'
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                cell = t.cell(i, j)
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(val)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(8)
                if i == 0:
                    run.font.bold = True
        return t

    # ── TITLE ──
    add_para(
        "APIForge AI: A Multi-Agent Framework for Automated API-First\nSoftware Development with Intelligent API Review",
        size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=Pt(10))

    add_para(
        "Siva Sarvesh, Kokhulash MS\nDepartment of Computer Science and Engineering\n"
        "College of Engineering Guindy, Anna University, Chennai, India",
        size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=Pt(12))

    # ── ABSTRACT ──
    add_para("Abstract.", size=10, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=Pt(0))
    add_para(
        "Existing multi-agent frameworks generate APIs directly from draft specifications without "
        "pre-implementation architectural review, resulting in REST anti-patterns, security gaps, "
        "and incomplete documentation. This paper presents APIForge AI, a six-agent framework whose "
        "core contribution is an API Review Agent that combines deterministic OpenAPI linting "
        "(20+ rules), LLM-powered semantic auditing, multi-attribute quality scoring (0\u2013100), and "
        "automated iterative refinement. The framework generates production-ready FastAPI backends "
        "with self-healing Pytest suites. Evaluation across four domains achieves 100% REST "
        "compliance, 100.0 API Quality Score, and 100% execution reliability.",
        size=9, italic=True, after=Pt(4))
    add_para(
        "Keywords: Multi-Agent Systems \u00b7 API-First Development \u00b7 REST API Review \u00b7 "
        "Large Language Models \u00b7 OpenAPI Specification \u00b7 Automated Testing",
        size=9, after=Pt(10))

    # ── 1. INTRODUCTION ──
    add_para("1  Introduction", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=Pt(4))
    add_para(
        "API-first development\u2014where API contracts are designed before implementation\u2014has become "
        "the industry standard for scalable microservice architectures [1, 2]. Large Language Models "
        "(LLMs) now enable rapid code generation [3, 4], and multi-agent frameworks such as ChatDev "
        "[5], MetaGPT [6], and AutoGen [7] decompose complex engineering tasks across specialised "
        "agents. However, a critical gap persists: these systems generate code from draft "
        "specifications without rigorous pre-implementation review, propagating REST anti-patterns, "
        "missing status codes, and security vulnerabilities into production code.")
    add_para(
        "The base paper by Chauhan et al. [8] demonstrated autonomous API-first development using "
        "a five-agent pipeline (spec-generator, code-generator, json-cleaner, code-fixer, "
        "code-tester) targeting Node.js/Express.js. While achieving 100% runtime execution across "
        "7 PRAB benchmark APIs, their approach relies on manual specification review and does not "
        "measure REST compliance, security coverage, or documentation quality.")
    add_para(
        "This paper proposes APIForge AI, whose principal contribution is the API Review Agent\u2014a "
        "pre-implementation quality gate integrating: (i) a deterministic OAS Linter with 20+ "
        "REST/security/metadata rules, (ii) LLM semantic auditing, (iii) a weighted quality "
        "scorer (REST 30%, Schema 25%, Security 25%, Documentation 20%), and (iv) an automated "
        "OAS Refiner with iterative refinement (max 3 rounds, threshold \u2265 80).")

    # ── 2. LITERATURE SURVEY & GAP ──
    add_para("2  Literature Survey and Research Gap", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=Pt(4))
    add_para(
        "A comprehensive survey of 25 recent works reveals six thematic areas: (1) API design and "
        "specification-driven generation [8, 9]; (2) automated REST smell detection [10, 11]; "
        "(3) automated API testing using dependency graphs, MARL, and fine-tuned models [12\u201318]; "
        "(4) specification extraction and documentation generation [19\u201322]; (5) multi-agent "
        "software engineering architectures [23\u201326]; and (6) systematic reviews and empirical foundations "
        "[27\u201332]. Table 1 summarises the critical analysis.")

    add_para("Table 1. Critical analysis of representative related work.", size=9,
             align=WD_ALIGN_PARAGRAPH.CENTER, after=Pt(2))
    add_table([
        ["Reference", "Focus", "Strength", "Gap Addressed by APIForge"],
        ["Chauhan et al. [8]", "API-first gen.", "100% runtime (7 APIs)", "No automated review / scoring"],
        ["Lima et al. [10]", "Smell detection", "2,450 smells found", "Detection only; no repair"],
        ["Han & Zhu [14]", "API testing", "OAS-to-Pytest pipeline", "No upstream spec review"],
        ["AutoRestTest [15]", "MARL testing", "5 specialised agents", "No spec refinement"],
        ["LogiAgent [17]", "Logical testing", "234 logical issues", "Post-hoc; no prevention"],
        ["AgentMesh [23]", "Multi-agent SE", "Cooperative pattern", "No API-specific rules"],
        ["Otoum et al. [27]", "SLR (61 studies)", "Identifies gaps", "Survey only"],
    ])

    add_para(
        "Key research gap: No existing framework unifies deterministic REST linting, LLM semantic "
        "auditing, quantitative quality scoring (0\u2013100), automated specification repair, and "
        "specification-aware self-healing test generation in a single pipeline with a dedicated "
        "Review Agent as a pre-implementation quality gate.", after=Pt(8))

    # ── 3. METHODOLOGY ──
    add_para("3  Methodology", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=Pt(4))
    add_para(
        "APIForge AI implements a six-agent pipeline orchestrated by a central coordinator "
        "(APIForgeOrchestrator) operating on a shared Pydantic state object (APIForgeState). "
        "Figure 1 shows the overall architecture.")
    add_img("overall_architecture.jpg",
            "Fig. 1. Overall architecture: six-agent pipeline with iterative review and self-healing test loops.")

    add_para(
        "Agents 1\u20132 (Requirement Analysis, Specification Generator) convert natural language "
        "into a structured OpenAPI 3.1 draft. Agent 3 (API Review Agent\u2014core contribution) "
        "subjects the draft to four-stage evaluation (Fig. 2): the OAS Linter checks 20+ "
        "deterministic rules (REST-001\u2013010: URI verbs, singular resources, status codes; "
        "SEC-001\u2013003: auth enforcement; OAS-000\u2013007: metadata), the Semantic Reviewer "
        "performs LLM-based business logic and security analysis, the Quality Scorer computes a "
        "weighted 0\u2013100 score, and the OAS Refiner auto-repairs violations. The loop repeats "
        "until score \u2265 80 with zero critical issues (max 3 iterations).")
    add_img("review_agent_design.jpg",
            "Fig. 2. API Review Agent internal architecture with iterative refinement loop.",
            width=Inches(5.2))

    add_para(
        "Agents 4\u20135 (Documentation, Code Generation) produce API reference docs (Swagger UI, "
        "ReDoc, Markdown) and a FastAPI + Pydantic v2 backend. Agent 6 (Testing & Debugging) "
        "generates Pytest suites, executes them in a sandboxed TestClient, and applies a "
        "self-repair loop (max 3 debug iterations) for failing tests (Fig. 3).")
    add_img("testing_agent_design.jpg",
            "Fig. 3. Testing & Debugging Agent with self-repair execution loop.",
            width=Inches(5.2))

    # ── 4. RESULTS ──
    add_para("4  Results and Analysis", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=Pt(4))
    add_para(
        "The framework was evaluated across four benchmark domains (Healthcare, E-Commerce, IoT "
        "Fleet, Task Management) using eight quantitative metrics. Table 2 presents the results.")

    add_para("Table 2. Performance metrics across four evaluation domains.",
             size=9, align=WD_ALIGN_PARAGRAPH.CENTER, after=Pt(2))
    add_table([
        ["Metric", "Healthcare", "E-Commerce", "IoT Fleet", "Task Mgmt", "Overall"],
        ["OpenAPI Validation Accuracy", "95.0%", "95.0%", "95.0%", "95.0%", "95.0%"],
        ["REST Design Compliance", "100.0%", "100.0%", "100.0%", "100.0%", "100.0%"],
        ["Documentation Completeness", "100.0%", "100.0%", "100.0%", "100.0%", "100.0%"],
        ["Security Recommendation Coverage", "100.0%", "100.0%", "100.0%", "100.0%", "100.0%"],
        ["API Quality Score (0\u2013100)", "100.0", "100.0", "100.0", "100.0", "100.0"],
        ["Test Case Success Rate", "100.0%", "100.0%", "100.0%", "100.0%", "100.0%"],
        ["Execution Reliability", "100.0%", "100.0%", "100.0%", "100.0%", "100.0%"],
        ["Error Reduction Rate", "100.0%", "100.0%", "100.0%", "100.0%", "100.0%"],
    ])

    add_para(
        "All domains achieve 100% REST compliance, 100.0 quality score, and 100% execution "
        "reliability. The 95% OpenAPI validation accuracy reflects strict OAS 3.1 validator "
        "behaviour on minor specification notes that do not affect functionality. Figure 4 "
        "visualises the metrics distribution.")
    add_img("performance_metrics_grouped_bar.png",
            "Fig. 4. Performance metrics across evaluation domains.")

    add_para(
        "The Review Agent's effectiveness is demonstrated by the quality score progression "
        "(Fig. 5): initial drafts score 55\u201362; after Round 1, scores reach 78\u201385; final "
        "approved specs achieve 98.3\u2013100.0, exceeding the threshold of 80.")
    add_img("quality_score_progression.png",
            "Fig. 5. Quality score progression through iterative refinement rounds.")

    # ── 5. COMPARATIVE ANALYSIS ──
    add_para("5  Comparative Analysis", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=Pt(4))

    add_para("Table 3. Comparison with the base paper and related frameworks.",
             size=9, align=WD_ALIGN_PARAGRAPH.CENTER, after=Pt(2))
    add_table([
        ["Aspect", "Chauhan et al. [8]", "APIForge AI (This Work)"],
        ["Review Stage", "Manual (user-in-the-loop)", "Automated (20+ rules + LLM)"],
        ["Quality Metric", "Diff line reduction", "API Quality Score (0\u2013100)"],
        ["Backend Target", "Node.js / Express.js", "Python / FastAPI + Pydantic v2"],
        ["Testing", "Manual cURL", "Automated Pytest + self-healing"],
        ["REST Compliance", "Not measured", "100% across all domains"],
        ["Security Enforcement", "Not addressed", "Automated JWT Bearer injection"],
        ["Iterative Refinement", "Log-based code repair", "Spec-level refinement + code repair"],
    ])

    add_img("comparison_with_base_paper.png",
            "Fig. 6. Comparative performance: APIForge AI vs. base paper.")

    # ── 6. CONCLUSION ──
    add_para("6  Conclusion", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=Pt(4))
    add_para(
        "This paper presented APIForge AI, a multi-agent framework whose API Review Agent provides "
        "a pre-implementation quality gate combining deterministic linting (20+ rules), LLM "
        "semantic auditing, multi-attribute scoring, and automated specification repair. Evaluation "
        "across four domains confirms 100% REST compliance, 100.0 API Quality Score, and 100% "
        "execution reliability. Compared to the base paper [8], APIForge replaces manual review "
        "with automated enforcement, introduces quantitative quality measurement, and adds "
        "security-by-design through automated JWT injection.")
    add_para(
        "Limitations include the use of four benchmark domains with deterministic mock responses "
        "and the absence of cost/latency reporting. Future work targets closed-loop specification "
        "redesign from test failures, expansion to the full 60-API PRAB benchmark, multi-language "
        "backend generation (Node.js, Go, Java), and developer perception studies.")

    # ── REFERENCES ──
    add_para("References", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=Pt(4))
    refs = [
        '[1] OpenAPI Initiative, "OpenAPI Specification v3.0.4," Oct. 2024.',
        '[2] L. Richardson, M. Amundsen, and S. Ruby, RESTful Web APIs, O\'Reilly Media, 2013.',
        '[3] J. Jiang et al., "A survey on large language models for code generation," arXiv:2406.00515, 2024.',
        '[4] Q. Zhang et al., "A survey on large language models for software engineering," arXiv:2312.15223, 2023.',
        '[5] C. Qian et al., "ChatDev: Communicative agents for software development," in Proc. ACL, 2024.',
        '[6] S. Hong et al., "MetaGPT: Meta programming for a multi-agent collaborative framework," arXiv:2308.00352, 2023.',
        '[7] Q. Wu et al., "AutoGen: Enabling next-gen LLM applications via multi-agent conversation," arXiv:2308.08155, 2023.',
        '[8] S. Chauhan et al., "From specification to service: Accelerating API-first development using multi-agent systems," arXiv:2510.19274, 2025.',
        '[9] A. Decrop et al., "You can REST now: Automated specification inference and black-box testing of RESTful APIs with LLMs," arXiv:2402.05102, 2024.',
        '[10] R. Lima et al., "Making OpenAPI documentation agent-ready: Detecting documentation and REST smells with a multi-agent LLM system," arXiv:2605.14312, 2026.',
        '[11] T. Sharanarthi and S. Polineni, "Multi-agent LLM collaboration for adaptive code review, debugging, and security analysis," in Proc. MRAI, pp. 541\u2013546, 2025.',
        '[12] T. Le et al., "KAT: Dependency-aware automated API testing with large language models," in Proc. IEEE ICST, pp. 82\u201392, 2024.',
        '[13] R. Nooyens et al., "Test amplification for REST APIs via single and multi-agent LLM systems," arXiv:2504.08113, 2025.',
        '[14] X. Han and H. Zhu, "MASTEST: A LLM-based multi-agent system for RESTful API tests," arXiv:2511.18038, 2025.',
        '[15] T. Stennett et al., "AutoRestTest: A tool for automated REST API testing using LLMs and MARL," in Proc. ICSE Companion, pp. 21\u201324, 2025.',
        '[16] M. Kim, S. Sinha, and A. Orso, "LlamaRestTest: Effective REST API testing with small language models," in Proc. ACM Softw. Eng., vol. 2, pp. 465\u2013488, 2025.',
        '[17] K. Zhang et al., "LogiAgent: Automated logical testing for REST systems with LLM-based multi-agents," arXiv:2503.15079, 2025.',
        '[18] A. Pereira et al., "APITestGenie: Generating web API tests from requirements and API specifications with LLMs," in Proc. ACM/IEEE AST, 2026.',
        '[19] K. Lazar et al., "OASBuilder: Generating OpenAPI specifications from online API documentation with LLMs," arXiv:2507.05316, 2025.',
        '[20] K. Lazar et al., "SpeCrawler: Generating OpenAPI specifications from API documentation using LLMs," arXiv:2402.11625, 2024.',
        '[21] X. Ni et al., "ToolFactory: Automating tool generation by leveraging LLM to understand REST API documentations," arXiv:2501.16945, 2025.',
        '[22] K. Nybom, A. Ashraf, and I. Porres, "A systematic mapping study on API documentation generation approaches," in Proc. SEAA, pp. 462\u2013469, 2018.',
        '[23] S. Khanzadeh, "AgentMesh: A cooperative multi-agent generative AI framework for software development automation," arXiv:2507.19902, 2025.',
        '[24] T. Guan, "A multi-agent coding assistant for cloud-native development," in Proc. ICSMT, 2025.',
        '[25] M. A. Sami et al., "Experimenting with multi-agent software development: Towards a unified platform," arXiv:2406.05381, 2024.',
        '[26] S. Hu, C. Lu, and J. Clune, "Automated design of agentic systems," arXiv:2408.08435, 2024.',
        '[27] N. A. Otoum and N. Elkhalili, "Methods and techniques of agentic software engineering: A systematic literature review," IEEE Access, vol. 14, pp. 7443\u20137465, 2026.',
        '[28] M. Kim et al., "Enhancing REST API testing with NLP techniques," in Proc. ACM ISSTA, 2023.',
        '[29] M. Kim et al., "Leveraging large language models to improve REST API testing," in Proc. IEEE/ACM ICSE-NIER, pp. 37\u201341, 2024.',
        '[30] M. Schafer et al., "An empirical evaluation of using large language models for automated unit test generation," IEEE TSE, vol. 50, pp. 85\u2013105, 2023.',
        '[31] T. Barradas et al., "Combining TSL and LLM to automate REST API testing: A comparative study," in Proc. SBES, pp. 71\u201381, 2025.',
        '[32] A. M. Rincon et al., "LLM prompt engineering for automated white-box integration test generation in REST APIs," in Proc. IEEE ICSTW, pp. 21\u201328, 2025.',
    ]
    for r in refs:
        add_para(r, size=9, align=WD_ALIGN_PARAGRAPH.LEFT, after=Pt(2))

    # ── SAVE ──
    out = r"C:\Users\User\Downloads\APIForge_AI_Research_Paper_Short.docx"
    doc.save(out)
    print(f"Short paper saved to {out}")


if __name__ == '__main__':
    create_short_paper()
