# Router for books
from __future__ import annotations
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, status, Header, Query, Path, Response
from app.models import *
from app.database import db

router = APIRouter(prefix="", tags=["Books"])

@router.post("/books", status_code=201)
def createBook(payload: BookCreate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
    created = db.create("books", data)
    return created

@router.get("/books", status_code=200)
def listBooks(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    items = db.list_all("books", limit=limit, offset=offset)
    total = len(db.get_table("books"))
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.get("/books/{book_id}", status_code=200)
def getBookById(book_id: str = Path(...), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    item = db.get_by_id("books", book_id)
    if not item:
        raise HTTPException(status_code=404, detail="books not found")
    return item

@router.put("/books/{book_id}", status_code=200)
def updateBook(book_id: str = Path(...), payload: BookUpdate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else dict(payload)
    updated = db.update("books", book_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="books not found")
    return updated

@router.patch("/books/{book_id}", status_code=200)
def partiallyUpdateBook(book_id: str = Path(...), payload: BookPartialUpdate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else dict(payload)
    updated = db.update("books", book_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="books not found")
    return updated

@router.delete("/books/{book_id}", status_code=204)
def deleteBook(book_id: str = Path(...), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    deleted = db.delete("books", book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="books not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
