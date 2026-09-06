# Router for projects
from __future__ import annotations
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, status, Header, Query, Path, Response
from app.models import *
from app.database import db

router = APIRouter(prefix="", tags=["Projects"])

@router.post("/projects", status_code=201)
async def post_projects(payload: ProjectCreate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
    created = db.create("projects", data)
    return created

@router.get("/projects", status_code=200)
async def get_projects(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    items = db.list_all("projects", limit=limit, offset=offset)
    total = len(db.get_table("projects"))
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.get("/projects/{project_id}", status_code=200)
async def get_projects_project_id(project_id: str = Path(...), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    item = db.get_by_id("projects", project_id)
    if not item:
        raise HTTPException(status_code=404, detail="projects not found")
    return item

@router.delete("/projects/{project_id}", status_code=204)
async def delete_projects_project_id(project_id: str = Path(...), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    deleted = db.delete("projects", project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="projects not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
