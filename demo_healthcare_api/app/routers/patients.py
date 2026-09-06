# Router for patients
from __future__ import annotations
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, status, Header, Query, Path, Response
from app.models import *
from app.database import db

router = APIRouter(prefix="", tags=["Patients"])

@router.get("/patients", status_code=200)
def get_patients(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    items = db.list_all("patients", limit=limit, offset=offset)
    total = len(db.get_table("patients"))
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.post("/patients", status_code=201)
def post_patients(payload: PatientCreate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
    created = db.create("patients", data)
    return created

@router.get("/patients/{patient_id}", status_code=200)
def get_patients_patient_id(patient_id: str = Path(...), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    item = db.get_by_id("patients", patient_id)
    if not item:
        raise HTTPException(status_code=404, detail="patients not found")
    return item
