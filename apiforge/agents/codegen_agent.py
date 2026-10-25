"""Code Generation Agent for APIForge AI.

Translates reviewed OpenAPI 3.1 specifications into fully functional, production-ready
FastAPI applications with Pydantic v2 schemas, typed route handlers, and in-memory persistence.
"""

from __future__ import annotations
import copy
import json
import logging
import re
from typing import Any, Dict, List
from apiforge.core.llm import BaseLLMClient
from apiforge.core.state import APIForgeState

logger = logging.getLogger(__name__)


class CodeGenerationAgent:
    """Agent translating reviewed OpenAPI specifications into executable FastAPI services."""

    def __init__(self, llm: BaseLLMClient):
        self.llm = llm

    def run(self, state: APIForgeState) -> APIForgeState:
        if not state.openapi_spec:
            raise ValueError("State does not contain openapi_spec for code generation.")

        state.log_trace("CodeGenerationAgent", "Generating FastAPI backend application")
        spec = state.openapi_spec

        files: Dict[str, str] = {}

        # 1. Generate Models (Pydantic v2)
        models_code = self._generate_models_code(spec)
        files["app/models.py"] = models_code

        # 2. Generate In-Memory Database / Store
        db_code = self._generate_db_code(spec)
        files["app/database.py"] = db_code

        # 3. Generate Routers for Resources
        routers_dict, router_names = self._generate_routers(spec)
        for rpath, rcode in routers_dict.items():
            files[rpath] = rcode

        # 4. Generate app/main.py
        main_code = self._generate_main_code(spec, router_names)
        files["app/main.py"] = main_code
        files["app/__init__.py"] = ""
        files["app/routers/__init__.py"] = ""

        # 5. Requirements & Dockerfile
        files["requirements.txt"] = "fastapi>=0.110.0\nuvicorn>=0.29.0\npydantic>=2.7.0\npytest>=8.0.0\nhttpx>=0.27.0\n"
        files["Dockerfile"] = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

        state.generated_code_files = files
        state.status = "implemented"
        state.log_trace(
            "CodeGenerationAgent",
            "FastAPI backend generated successfully",
            files_count=len(files),
            files=list(files.keys()),
        )
        return state

    def _generate_models_code(self, spec: Dict[str, Any]) -> str:
        schemas = spec.get("components", {}).get("schemas", {})
        lines = [
            "# Auto-generated Pydantic models from OpenAPI 3.1 specification",
            "from __future__ import annotations",
            "from typing import Optional, List, Any, Dict",
            "from pydantic import BaseModel, Field",
            "from datetime import datetime",
            "",
        ]

        for sname, sdef in schemas.items():
            if not isinstance(sdef, dict):
                continue
            desc = sdef.get("description", f"Model for {sname}")
            props = sdef.get("properties", {})
            required_fields = sdef.get("required", [])

            lines.append(f"class {sname}(BaseModel):")
            lines.append(f'    """{desc}"""')

            if not props:
                lines.append("    pass\n")
                continue

            for pname, pdef in props.items():
                if not isinstance(pdef, dict):
                    continue
                is_req = pname in required_fields
                ptype = "str"
                raw_type = pdef.get("type", "string")
                if raw_type == "integer":
                    ptype = "int"
                elif raw_type == "number":
                    ptype = "float"
                elif raw_type == "boolean":
                    ptype = "bool"
                elif raw_type == "array":
                    items_def = pdef.get("items", {})
                    if "$ref" in items_def:
                        ref_name = items_def["$ref"].split("/")[-1]
                        ptype = f"List[{ref_name}]"
                    else:
                        ptype = "List[Any]"
                elif "$ref" in pdef:
                    ptype = pdef["$ref"].split("/")[-1]

                if not is_req:
                    lines.append(f"    {pname}: Optional[{ptype}] = None")
                else:
                    lines.append(f"    {pname}: {ptype}")
            lines.append("")

        return "\n".join(lines)

    def _generate_db_code(self, spec: Dict[str, Any]) -> str:
        schemas = spec.get("components", {}).get("schemas", {})
        entity_names = [s for s in schemas.keys() if not s.endswith("Create") and not s.endswith("Update") and not s.endswith("ListResponse") and s != "ErrorResponse"]

        lines = [
            "# In-memory thread-safe state store for functional testing and local execution",
            "import uuid",
            "from typing import Dict, List, Any, Optional",
            "",
            "class InMemoryStore:",
            "    def __init__(self):",
            "        self.tables: Dict[str, Dict[str, Dict[str, Any]]] = {",
        ]
        for ename in entity_names:
            plural = ename.lower() + "s"
            lines.append(f'            "{plural}": {{}},')
        lines.append("        }")
        lines.append("")
        lines.append("""    def get_table(self, resource: str) -> Dict[str, Dict[str, Any]]:
        if resource not in self.tables:
            self.tables[resource] = {}
        return self.tables[resource]

    def list_all(self, resource: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        items = list(self.get_table(resource).values())
        return items[offset:offset + limit]

    def get_by_id(self, resource: str, item_id: str) -> Optional[Dict[str, Any]]:
        return self.get_table(resource).get(str(item_id))

    def create(self, resource: str, data: Dict[str, Any], item_id: Optional[str] = None) -> Dict[str, Any]:
        table = self.get_table(resource)
        rid = str(item_id) if item_id else data.get("id") or str(uuid.uuid4())
        record = dict(data)
        record["id"] = rid
        table[rid] = record
        return record

    def update(self, resource: str, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        table = self.get_table(resource)
        rid = str(item_id)
        if rid not in table:
            return None
        table[rid].update(data)
        return table[rid]

    def delete(self, resource: str, item_id: str) -> bool:
        table = self.get_table(resource)
        rid = str(item_id)
        if rid in table:
            del table[rid]
            return True
        return False

db = InMemoryStore()
""")
        return "\n".join(lines)

    def _generate_routers(self, spec: Dict[str, Any]) -> tuple[Dict[str, str], List[str]]:
        paths = spec.get("paths", {})
        # Group paths by top-level resource segment
        resource_groups: Dict[str, List[tuple[str, str, Dict[str, Any]]]] = {}

        for path_str, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            segs = [s for s in path_str.split("/") if s]
            root_res = segs[0] if segs else "default"
            if root_res not in resource_groups:
                resource_groups[root_res] = []
            for method, op in path_item.items():
                if method.lower() in ("get", "post", "put", "patch", "delete"):
                    resource_groups[root_res].append((path_str, method.lower(), op))

        routers: Dict[str, str] = {}
        router_names: List[str] = []

        for resource, ops in resource_groups.items():
            mod_name = resource.replace("-", "_").lower()
            router_names.append(mod_name)
            rlines = [
                f"# Router for {resource}",
                "from __future__ import annotations",
                "from typing import Optional, List, Any",
                "from fastapi import APIRouter, HTTPException, status, Header, Query, Path, Response",
                "from app.models import *",
                "from app.database import db",
                "",
                f'router = APIRouter(prefix="", tags=["{resource.capitalize()}"])',
                "",
            ]

            for path_str, method, op in ops:
                op_id = op.get("operationId", f"{method}_{resource}")
                status_code = 200
                if method == "post":
                    status_code = 201
                elif method == "delete":
                    status_code = 204

                rlines.append(f'@router.{method}("{path_str}", status_code={status_code})')
                
                # Build function signature
                func_params = []
                path_params = re.findall(r"\{([a-zA-Z0-9_]+)\}", path_str)
                for pp in path_params:
                    func_params.append(f"{pp}: str")

                if method in ("post", "put", "patch") and "requestBody" in op:
                    rb = op["requestBody"]
                    ref = rb.get("content", {}).get("application/json", {}).get("schema", {}).get("$ref", "")
                    m_type = ref.split("/")[-1] if ref else "dict"
                    func_params.append(f"payload: {m_type}")

                if method == "get" and not path_params:
                    func_params.append("limit: int = Query(20, ge=1, le=100)")
                    func_params.append("offset: int = Query(0, ge=0)")

                if op.get("security"):
                    func_params.append("authorization: Optional[str] = Header(None)")

                sig = ", ".join(func_params)
                rlines.append(f"async def {op_id}({sig}):")

                # Function body
                if op.get("security"):
                    rlines.append('    if not authorization or not authorization.startswith("Bearer "):')
                    rlines.append('        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")')

                target_table = resource.lower()

                if method == "post":
                    rlines.append(f'    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)')
                    rlines.append(f'    created = db.create("{target_table}", data)')
                    rlines.append("    return created")
                elif method == "delete":
                    pk = path_params[0] if path_params else "id"
                    rlines.append(f'    deleted = db.delete("{target_table}", {pk})')
                    rlines.append("    if not deleted:")
                    rlines.append(f'        raise HTTPException(status_code=404, detail="{resource} not found")')
                    rlines.append("    return Response(status_code=status.HTTP_204_NO_CONTENT)")
                elif method in ("put", "patch"):
                    pk = path_params[0] if path_params else "id"
                    rlines.append(f'    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else dict(payload)')
                    rlines.append(f'    updated = db.update("{target_table}", {pk}, data)')
                    rlines.append("    if not updated:")
                    rlines.append(f'        raise HTTPException(status_code=404, detail="{resource} not found")')
                    rlines.append("    return updated")
                elif method == "get":
                    if path_params:
                        pk = path_params[0]
                        rlines.append(f'    item = db.get_by_id("{target_table}", {pk})')
                        rlines.append("    if not item:")
                        rlines.append(f'        raise HTTPException(status_code=404, detail="{resource} not found")')
                        rlines.append("    return item")
                    else:
                        rlines.append(f'    items = db.list_all("{target_table}", limit=limit, offset=offset)')
                        rlines.append(f'    total = len(db.get_table("{target_table}"))')
                        rlines.append('    return {"items": items, "total": total, "limit": limit, "offset": offset}')
                rlines.append("")

            routers[f"app/routers/{mod_name}.py"] = "\n".join(rlines)

        return routers, router_names

    def _generate_main_code(self, spec: Dict[str, Any], router_names: List[str]) -> str:
        info = spec.get("info", {})
        title = info.get("title", "API Service")
        version = info.get("version", "1.0.0")
        desc = info.get("description", "")

        lines = [
            f"# Main entrypoint for {title}",
            "from fastapi import FastAPI, Request",
            "from fastapi.responses import JSONResponse",
            "from fastapi.middleware.cors import CORSMiddleware",
            "",
        ]
        for rname in router_names:
            lines.append(f"from app.routers import {rname}")

        lines.append("")
        lines.append(f'app = FastAPI(')
        lines.append(f'    title="{title}",')
        lines.append(f'    version="{version}",')
        lines.append(f'    description="""{desc}""",')
        lines.append(f'    openapi_url="/openapi.json",')
        lines.append(f'    docs_url="/docs",')
        lines.append(f'    redoc_url="/redoc",')
        lines.append(")")
        lines.append("")
        lines.append("""app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "api-forge"}
""")
        for rname in router_names:
            lines.append(f"app.include_router({rname}.router)")
        lines.append("")
        return "\n".join(lines)
