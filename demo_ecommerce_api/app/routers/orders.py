# Router for orders
from __future__ import annotations
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, status, Header, Query, Path, Response
from app.models import *
from app.database import db

router = APIRouter(prefix="", tags=["Orders"])

@router.post("/orders", status_code=201)
async def post_orders(payload: OrderCreate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
    created = db.create("orders", data)
    return created

@router.get("/orders", status_code=200)
async def get_orders(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    items = db.list_all("orders", limit=limit, offset=offset)
    total = len(db.get_table("orders"))
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.get("/orders/{order_id}", status_code=200)
async def get_orders_order_id(order_id: str, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    item = db.get_by_id("orders", order_id)
    if not item:
        raise HTTPException(status_code=404, detail="orders not found")
    return item
