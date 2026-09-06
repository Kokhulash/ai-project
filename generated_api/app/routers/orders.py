# Router for orders
from __future__ import annotations
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, status, Header, Query, Path, Response
from app.models import *
from app.database import db

router = APIRouter(prefix="", tags=["Orders"])

@router.get("/orders", status_code=200)
async def get_orders(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    items = db.list_all("orders", limit=limit, offset=offset)
    total = len(db.get_table("orders"))
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.post("/orders", status_code=201)
async def post_orders(payload: OrderCreate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
    created = db.create("orders", data)
    return created

@router.get("/orders/{id}", status_code=200)
async def get_orders_id(id: str, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    item = db.get_by_id("orders", id)
    if not item:
        raise HTTPException(status_code=404, detail="orders not found")
    return item

@router.patch("/orders/{id}", status_code=200)
async def patch_orders_id(id: str, payload: OrderStatusUpdate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else dict(payload)
    updated = db.update("orders", id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="orders not found")
    return updated

@router.delete("/orders/{id}", status_code=204)
async def delete_orders_id(id: str, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    deleted = db.delete("orders", id)
    if not deleted:
        raise HTTPException(status_code=404, detail="orders not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
