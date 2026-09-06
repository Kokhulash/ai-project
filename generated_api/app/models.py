# Auto-generated Pydantic models from OpenAPI 3.1 specification
from __future__ import annotations
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class Book(BaseModel):
    """Represents a single book in the management system, including its descriptive metadata and availability."""
    id: str
    title: str
    author: str
    isbn: str
    publicationYear: int
    genre: str
    availableCopies: int
    totalCopies: int

class BookCreate(BaseModel):
    """Data required to create a new book record."""
    title: str
    author: str
    isbn: str
    publicationYear: int
    genre: str
    totalCopies: int

class BookUpdate(BaseModel):
    """Full data to update an existing book record. All fields are required for a PUT operation."""
    title: str
    author: str
    isbn: str
    publicationYear: int
    genre: str
    availableCopies: int
    totalCopies: int

class BookPartialUpdate(BaseModel):
    """Partial data to update an existing book record. Fields not provided will remain unchanged. All fields are optional."""
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publicationYear: Optional[int] = None
    genre: Optional[str] = None
    availableCopies: Optional[int] = None
    totalCopies: Optional[int] = None

class BookListResponse(BaseModel):
    """A paginated list of books."""
    items: List[Book]
    total: int
    limit: int
    offset: int

class MessageResponse(BaseModel):
    """A generic response for operations that do not return specific data."""
    message: str

class ErrorResponse(BaseModel):
    """Standard error response format."""
    status: int
    title: str
    detail: str
    instance: Optional[str] = None
