"""Automated Test Generation Agent for APIForge AI.

Derives comprehensive functional pytest suites from OpenAPI 3.1 specifications,
testing CRUD lifecycles, auth security boundaries, pagination, and error statuses.
"""

from __future__ import annotations
import json
import logging
import re
from typing import Any, Dict, List
from apiforge.core.llm import BaseLLMClient
from apiforge.core.state import APIForgeState

logger = logging.getLogger(__name__)


class TestGeneratorAgent:
    """Generates executable pytest test suites adhering strictly to the OpenAPI specification."""

    def __init__(self, llm: BaseLLMClient):
        self.llm = llm

    def run(self, state: APIForgeState) -> APIForgeState:
        if not state.openapi_spec:
            raise ValueError("State does not contain openapi_spec for test generation.")

        state.log_trace("TestGeneratorAgent", "Synthesizing automated test suite from OpenAPI spec")
        spec = state.openapi_spec
        test_files: Dict[str, str] = {}

        # Generate main functional test file
        test_code = self._generate_pytest_code(spec)
        test_files["tests/test_api_functional.py"] = test_code
        test_files["tests/__init__.py"] = ""
        test_files["tests/conftest.py"] = """import pytest
import httpx

BASE_URL = "http://localhost:8000"
AUTH_HEADER = {"Authorization": "Bearer test-api-token-123"}

@pytest.fixture
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c
"""

        state.test_code_files = test_files
        state.log_trace(
            "TestGeneratorAgent",
            "Test suite generated",
            files=list(test_files.keys()),
        )
        return state

    def _generate_pytest_code(self, spec: Dict[str, Any]) -> str:
        paths = spec.get("paths", {})
        schemas = spec.get("components", {}).get("schemas", {})

        lines = [
            "# Auto-generated Pytest functional test suite by APIForge AI",
            "import pytest",
            "import httpx",
            "",
            "BASE_URL = 'http://localhost:8000'",
            "AUTH_HEADERS = {'Authorization': 'Bearer test-jwt-token'}",
            "",
            "def test_health_check(client):",
            "    response = client.get('/health')",
            "    assert response.status_code == 200",
            "    data = response.json()",
            "    assert data.get('status') == 'healthy'",
            "",
        ]

        # Group operations by resource
        resource_groups: Dict[str, Dict[str, Any]] = {}
        for p_str, p_item in paths.items():
            if not isinstance(p_item, dict):
                continue
            segs = [s for s in p_str.split("/") if s]
            root = segs[0] if segs else "default"
            if root not in resource_groups:
                resource_groups[root] = {"collection_path": None, "item_path": None, "ops": {}}
            if "{" in p_str:
                resource_groups[root]["item_path"] = p_str
            else:
                resource_groups[root]["collection_path"] = p_str
            for m, op in p_item.items():
                if m.lower() in ("get", "post", "put", "patch", "delete"):
                    resource_groups[root]["ops"][f"{m.lower()}:{p_str}"] = op

        for res, grp in resource_groups.items():
            col_path = grp["collection_path"]
            item_path = grp["item_path"]

            # CRUD Lifecycle Test
            lines.append(f"def test_{res.replace('-', '_')}_crud_lifecycle(client):")
            lines.append(f'    # 1. Create a new {res} resource via POST')
            
            # Find sample payload
            create_schema_name = f"{res.rstrip('s').capitalize()}Create"
            schema_def = schemas.get(create_schema_name, schemas.get(res.rstrip('s').capitalize(), {}))
            props = schema_def.get("properties", {}) if isinstance(schema_def, dict) else {}
            sample_payload = {}
            for pk, pv in props.items():
                if isinstance(pv, dict) and pk not in ("id", "created_at", "updated_at"):
                    pt = pv.get("type", "string")
                    if pt == "integer":
                        sample_payload[pk] = 10
                    elif pt == "boolean":
                        sample_payload[pk] = True
                    else:
                        sample_payload[pk] = f"Test {pk}"
            if not sample_payload:
                sample_payload = {"name": f"Test {res}", "title": f"Test {res}"}

            payload_json = json.dumps(sample_payload)

            has_post = any(k.startswith("post:") for k in grp["ops"])
            has_get_col = any(k.startswith("get:") and "{" not in k for k in grp["ops"])
            has_get_item = any(k.startswith("get:") and "{" in k for k in grp["ops"])
            has_put = any(k.startswith("put:") for k in grp["ops"])
            has_patch = any(k.startswith("patch:") for k in grp["ops"])
            has_delete = any(k.startswith("delete:") for k in grp["ops"])

            post_op = grp["ops"].get(f"post:{col_path}") if col_path else None
            is_secured = bool(post_op and post_op.get("security"))

            if col_path and has_post:
                lines.append(f"    create_payload = {payload_json}")
                lines.append(f"    res_create = client.post('{col_path}', json=create_payload, headers=AUTH_HEADERS)")
                lines.append("    assert res_create.status_code == 201, f'Expected 201 Created: {res_create.text}'")
                lines.append("    created_data = res_create.json()")
                lines.append("    assert 'id' in created_data, 'Created item must have an id'")
                lines.append("    item_id = created_data['id']")
                lines.append("")

            if col_path and has_get_col:
                # List with pagination
                lines.append(f"    # 2. List {res} collection with pagination")
                lines.append(f"    res_list = client.get('{col_path}?limit=10&offset=0', headers=AUTH_HEADERS)")
                lines.append("    assert res_list.status_code == 200")
                lines.append("    list_data = res_list.json()")
                lines.append("    assert 'items' in list_data")
                lines.append("    assert len(list_data['items']) >= 1")
                lines.append("")

            if item_path:
                template_var = re.findall(r"\{([a-zA-Z0-9_]+)\}", item_path)
                var_name = template_var[0] if template_var else "id"
                formatted_item_path = item_path.replace(f"{{{var_name}}}", "{item_id}")

                if has_get_item:
                    lines.append(f"    # 3. Retrieve {res} by ID")
                    lines.append(f"    res_get = client.get(f'{formatted_item_path}', headers=AUTH_HEADERS)")
                    lines.append("    assert res_get.status_code == 200")
                    lines.append(f"    assert res_get.json()['id'] == item_id")
                    lines.append("")

                if has_put or has_patch:
                    method_to_test = "put" if has_put else "patch"
                    lines.append(f"    # 4. Update {res}")
                    lines.append(f"    res_update = client.{method_to_test}(f'{formatted_item_path}', json=create_payload, headers=AUTH_HEADERS)")
                    lines.append("    assert res_update.status_code in (200, 204)")
                    lines.append("")

                if has_delete:
                    lines.append(f"    # 5. Delete {res}")
                    lines.append(f"    res_del = client.delete(f'{formatted_item_path}', headers=AUTH_HEADERS)")
                    lines.append("    assert res_del.status_code == 204")
                    lines.append("")

                    if has_get_item:
                        lines.append(f"    # 6. Verify 404 Not Found after deletion")
                        lines.append(f"    res_not_found = client.get(f'{formatted_item_path}', headers=AUTH_HEADERS)")
                        lines.append("    assert res_not_found.status_code == 404")
                        lines.append("")

            # Security test: Unauthorized access without token
            if col_path and has_post and is_secured:
                lines.append(f"def test_{res.replace('-', '_')}_auth_required(client):")
                lines.append(f"    # Accessing secured endpoint without token should return 401")
                lines.append(f"    create_payload = {payload_json}")
                lines.append(f"    res = client.post('{col_path}', json=create_payload)")
                lines.append("    assert res.status_code == 401, f'Expected 401 Unauthorized, got {res.status_code}'")
                lines.append("")

        return "\n".join(lines)
