# Router for appointments
from __future__ import annotations
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, status, Header, Query, Path, Response
from app.models import *
from app.database import db

router = APIRouter(prefix="", tags=["Appointments"])

@router.post("/appointments", status_code=201)
def post_appointments(payload: AppointmentCreate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    data = payload.model_dump() if hasattr(payload, "model_dump") else dict(payload)
    created = db.create("appointments", data)
    return created

@router.delete("/appointments/{appointment_id}", status_code=204)
def delete_appointments_appointment_id(appointment_id: str = Path(...), authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
    deleted = db.delete("appointments", appointment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="appointments not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
