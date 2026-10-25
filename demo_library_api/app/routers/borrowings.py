# Router for borrowings
from __future__ import annotations
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, status, Header, Query, Path, Response
from app.models import *
from app.database import db

router = APIRouter(prefix="", tags=["Borrowings"])

@router.get("/borrowings", status_code=200)
async def listBorrowings(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    items = db.list_all("borrowings", limit=limit, offset=offset)
    total = len(db.get_table("borrowings"))
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.post("/borrowings", status_code=201)
async def borrowBook(payload: BorrowingCreate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
    created = db.create("borrowings", data)
    return created

@router.get("/borrowings/{borrowing_id}", status_code=200)
async def getBorrowingById(borrowing_id: str, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    item = db.get_by_id("borrowings", borrowing_id)
    if not item:
        raise HTTPException(status_code=404, detail="borrowings not found")
    return item

@router.patch("/borrowings/{borrowing_id}/return", status_code=200)
async def returnBook(borrowing_id: str, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else dict(payload)
    updated = db.update("borrowings", borrowing_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="borrowings not found")
    return updated
