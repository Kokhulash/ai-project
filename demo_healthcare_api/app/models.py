# Auto-generated Pydantic models from OpenAPI 3.1 specification
from __future__ import annotations
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class ErrorResponse(BaseModel):
    """Model for ErrorResponse"""
    detail: str
    status: int
    code: Optional[str] = None

class Patient(BaseModel):
    """Patient record"""
    id: str
    full_name: Optional[str] = None
    birth_date: Optional[str] = None

class PatientCreate(BaseModel):
    """Payload for creating a new Patient"""
    full_name: Optional[str] = None
    birth_date: Optional[str] = None

class PatientListResponse(BaseModel):
    """Paginated list of Patient records"""
    items: List[Patient]
    total: int
    limit: int
    offset: int

class Appointment(BaseModel):
    """Clinical appointment"""
    id: str
    patient_id: Optional[str] = None
    appointment_time: Optional[str] = None
    status: Optional[str] = None

class AppointmentCreate(BaseModel):
    """Payload for creating a new Appointment"""
    patient_id: Optional[str] = None
    appointment_time: Optional[str] = None
    status: Optional[str] = None

class AppointmentListResponse(BaseModel):
    """Paginated list of Appointment records"""
    items: List[Appointment]
    total: int
    limit: int
    offset: int
