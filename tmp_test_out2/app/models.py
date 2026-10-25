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

class Project(BaseModel):
    """A workspace containing tasks"""
    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None

class ProjectCreate(BaseModel):
    """Payload for creating a new Project"""
    name: str
    description: Optional[str] = None

class ProjectListResponse(BaseModel):
    """Paginated list of Project records"""
    items: List[Project]
    total: int
    limit: int
    offset: int

class Task(BaseModel):
    """An actionable work item within a project"""
    id: str
    project_id: Optional[str] = None
    title: str
    status: Optional[str] = None
    assigned_to: Optional[str] = None

class TaskCreate(BaseModel):
    """Payload for creating a new Task"""
    project_id: Optional[str] = None
    title: str
    status: Optional[str] = None
    assigned_to: Optional[str] = None

class TaskListResponse(BaseModel):
    """Paginated list of Task records"""
    items: List[Task]
    total: int
    limit: int
    offset: int
