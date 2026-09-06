"""Documentation Agent for APIForge AI.

Enriches OpenAPI specifications with rich examples, descriptions, and generates
standalone Markdown reference guides, Swagger UI, and Redoc single-page HTML documentation.
"""

from __future__ import annotations
import copy
import json
import logging
from typing import Any, Dict
from apiforge.core.llm import BaseLLMClient
from apiforge.core.state import APIForgeState

logger = logging.getLogger(__name__)

SWAGGER_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} - Swagger Documentation</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    body {{ margin: 0; padding: 0; background: #fafafa; }}
    .topbar {{ display: none; }}
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin></script>
  <script>
    window.onload = () => {{
      window.ui = SwaggerUIBundle({{
        spec: {spec_json},
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout"
      }});
    }};
  </script>
</body>
</html>
"""

REDOC_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <title>{title} - API Reference</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
  <style>
    body {{ margin: 0; padding: 0; }}
  </style>
</head>
<body>
  <redoc spec-url="" id="redoc-container"></redoc>
  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
  <script>
    const spec = {spec_json};
    Redoc.init(spec, {{}}, document.getElementById('redoc-container'));
  </script>
</body>
</html>
"""


class DocumentationAgent:
    """Enriches OpenAPI specifications and generates multi-format developer documentation."""

    def __init__(self, llm: BaseLLMClient):
        self.llm = llm

    def run(self, state: APIForgeState) -> APIForgeState:
        if not state.openapi_spec:
            raise ValueError("State does not contain openapi_spec for documentation.")

        state.log_trace("DocumentationAgent", "Enriching OpenAPI specification and generating documentation")
        spec = copy.deepcopy(state.openapi_spec)

        # 1. Enrich Schemas with Examples if missing
        schemas = spec.get("components", {}).get("schemas", {})
        for sname, sdef in schemas.items():
            if isinstance(sdef, dict) and "properties" in sdef:
                props = sdef["properties"]
                example_obj = {}
                for pname, pdef in props.items():
                    if isinstance(pdef, dict):
                        if "example" in pdef:
                            example_obj[pname] = pdef["example"]
                        else:
                            ptype = pdef.get("type", "string")
                            if ptype == "integer":
                                pdef["example"] = 101
                                example_obj[pname] = 101
                            elif ptype == "boolean":
                                pdef["example"] = True
                                example_obj[pname] = True
                            elif ptype == "array":
                                pdef["example"] = []
                                example_obj[pname] = []
                            elif pdef.get("format") == "uuid":
                                pdef["example"] = "00000000-0000-0000-0000-000000000000"
                                example_obj[pname] = "00000000-0000-0000-0000-000000000000"
                            elif pdef.get("format") == "date-time":
                                pdef["example"] = "2026-01-01T00:00:00Z"
                                example_obj[pname] = "2026-01-01T00:00:00Z"
                            else:
                                pdef["example"] = f"sample_{pname}"
                                example_obj[pname] = f"sample_{pname}"
                if "example" not in sdef and example_obj:
                    sdef["example"] = example_obj

        # Update spec with enriched content
        state.openapi_spec = spec
        spec_json_str = json.dumps(spec, indent=2)
        title = spec.get("info", {}).get("title", "API Service")

        # 2. Generate Markdown Developer Documentation
        md_doc = self._generate_markdown_reference(spec)
        readme = self._generate_readme(spec)

        # 3. Generate HTML Bundles
        swagger_html = SWAGGER_HTML_TEMPLATE.format(title=title, spec_json=spec_json_str)
        redoc_html = REDOC_HTML_TEMPLATE.format(title=title, spec_json=spec_json_str)

        state.documentation_files["README.md"] = readme
        state.documentation_files["API_REFERENCE.md"] = md_doc
        state.documentation_files["swagger.html"] = swagger_html
        state.documentation_files["redoc.html"] = redoc_html

        state.log_trace(
            "DocumentationAgent",
            "Documentation generated successfully",
            files=list(state.documentation_files.keys()),
        )
        return state

    def _generate_markdown_reference(self, spec: Dict[str, Any]) -> str:
        info = spec.get("info", {})
        title = info.get("title", "API Service")
        version = info.get("version", "1.0.0")
        desc = info.get("description", "")
        paths = spec.get("paths", {})

        lines = [
            f"# {title} - API Reference Manual",
            f"**Version:** `{version}`  \n**Base URL:** `{spec.get('servers', [{}])[0].get('url', 'http://localhost:8000')}`",
            "",
            desc,
            "",
            "## Table of Contents",
        ]

        # TOC
        for p, methods in paths.items():
            for m in methods:
                if m.lower() in ("get", "post", "put", "patch", "delete"):
                    anchor = f"{m.lower()}-{p.replace('/', '').replace('{', '').replace('}', '')}"
                    lines.append(f"- [{m.upper()} `{p}`](#{anchor})")

        lines.append("\n---\n")

        # Endpoints
        for p, methods in paths.items():
            for m, op in methods.items():
                if m.lower() not in ("get", "post", "put", "patch", "delete"):
                    continue
                m_upper = m.upper()
                anchor = f"{m.lower()}-{p.replace('/', '').replace('{', '').replace('}', '')}"
                lines.append(f"### <a id=\"{anchor}\"></a>{m_upper} `{p}`")
                lines.append(f"**Summary:** {op.get('summary', 'N/A')}  ")
                if op.get("description"):
                    lines.append(f"**Description:** {op.get('description')}  ")
                
                # Auth
                sec = op.get("security", spec.get("security", []))
                if sec:
                    lines.append(f"🔒 **Authentication Required:** Bearer Token")

                # Parameters
                params = op.get("parameters", [])
                if params:
                    lines.append("\n#### Parameters:")
                    lines.append("| Name | In | Required | Type | Description |")
                    lines.append("| :--- | :--- | :--- | :--- | :--- |")
                    for param in params:
                        p_schema = param.get("schema", {})
                        lines.append(f"| `{param.get('name')}` | `{param.get('in')}` | `{param.get('required', False)}` | `{p_schema.get('type', 'string')}` | {param.get('description', '')} |")

                # Request Body
                if "requestBody" in op:
                    rb = op["requestBody"]
                    content = rb.get("content", {}).get("application/json", {})
                    schema_ref = content.get("schema", {}).get("$ref", "")
                    lines.append(f"\n#### Request Body (`application/json`):")
                    if schema_ref:
                        lines.append(f"Ref: `{schema_ref}`")

                # Responses
                responses = op.get("responses", {})
                if responses:
                    lines.append("\n#### Responses:")
                    lines.append("| Status Code | Description | Schema |")
                    lines.append("| :--- | :--- | :--- |")
                    for code, resp in responses.items():
                        r_content = resp.get("content", {}).get("application/json", {})
                        r_ref = r_content.get("schema", {}).get("$ref", "None")
                        lines.append(f"| `{code}` | {resp.get('description', '')} | `{r_ref}` |")

                # Curl Example
                url = f"http://localhost:8000{p}"
                lines.append(f"\n#### Example cURL:")
                curl = f"curl -X {m_upper} \"{url}\""
                if sec:
                    curl += ' -H "Authorization: Bearer <TOKEN>"'
                if m_upper in ("POST", "PUT", "PATCH"):
                    curl += ' -H "Content-Type: application/json" -d \'{}\''
                lines.append(f"```bash\n{curl}\n```\n")

        return "\n".join(lines)

    def _generate_readme(self, spec: Dict[str, Any]) -> str:
        info = spec.get("info", {})
        title = info.get("title", "API Service")
        desc = info.get("description", "")
        return f"""# {title}

{desc}

Designed and generated using **APIForge AI** multi-agent framework.

## Getting Started

### 1. Run the Backend Service
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 2. View Interactive Documentation
- **Swagger UI**: Open `swagger.html` in your browser or visit `http://localhost:8000/docs`
- **Redoc**: Open `redoc.html` in your browser or visit `http://localhost:8000/redoc`
- **API Reference**: Read `API_REFERENCE.md`

### 3. Run Automated Tests
```bash
pytest tests/ -v
```
"""
