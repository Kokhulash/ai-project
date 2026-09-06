# Router for tasks
from __future__ import annotations
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, status, Header, Query, Path, Response
from app.models import *
from app.database import db

router = APIRouter(prefix="", tags=["Tasks"])

@router.post("/tasks", status_code=201)
async def post_tasks(payload: TaskCreate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
    created = db.create("tasks", data)
    return created

@router.get("/tasks", status_code=200)
async def get_tasks(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    items = db.list_all("tasks", limit=limit, offset=offset)
    total = len(db.get_table("tasks"))
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.get("/tasks/{task_id}", status_code=200)
async def get_tasks_task_id(task_id: str, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    item = db.get_by_id("tasks", task_id)
    if not item:
        raise HTTPException(status_code=404, detail="tasks not found")
    return item

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_tasks_task_id(task_id: str, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    deleted = db.delete("tasks", task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="tasks not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/tasks/{task_id}", status_code=200)
async def put_tasks_task_id(task_id: str, payload: TaskUpdate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else dict(payload)
    updated = db.update("tasks", task_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="tasks not found")
    return updated
