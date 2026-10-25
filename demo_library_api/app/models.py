# Auto-generated Pydantic models from OpenAPI 3.1 specification
from __future__ import annotations
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class Book(BaseModel):
    """Represents a book available in the library, including its details and availability."""
    id: str
    title: str
    author: str
    isbn: str
    publicationYear: int
    genre: str
    totalCopies: int
    availableCopies: int

class BookCreate(BaseModel):
    """Data required to add a new book to the library catalog. 'availableCopies' will be initialized to 'totalCopies' by the system."""
    title: str
    author: str
    isbn: str
    publicationYear: int
    genre: str
    totalCopies: int

class BookUpdate(BaseModel):
    """Data required to fully update an existing book. All fields are required for a PUT operation, excluding system-managed fields like 'availableCopies'."""
    title: str
    author: str
    isbn: str
    publicationYear: int
    genre: str
    totalCopies: int

class BookListResponse(BaseModel):
    """Paginated list of books."""
    items: List[Book]
    total: int
    limit: int
    offset: int

class User(BaseModel):
    """Represents a library user who can authenticate and borrow books."""
    id: str
    username: str
    email: str
    firstName: str
    lastName: str
    registrationDate: str

class UserCreate(BaseModel):
    """Data required to register a new user. 'username' and 'email' must be unique."""
    username: str
    email: str
    firstName: str
    lastName: str

class UserListResponse(BaseModel):
    """Paginated list of users."""
    items: List[User]
    total: int
    limit: int
    offset: int

class Borrowing(BaseModel):
    """Records an instance of a user borrowing a specific book, including borrow/return dates and status."""
    id: str
    bookId: str
    userId: str
    borrowDate: str
    dueDate: str
    returnDate: Optional[str] = None
    status: str

class BorrowingCreate(BaseModel):
    """Data required to borrow a book. The 'userId' is derived from the authentication token."""
    bookId: str

class BorrowingListResponse(BaseModel):
    """Paginated list of borrowing records."""
    items: List[Borrowing]
    total: int
    limit: int
    offset: int

class ErrorResponse(BaseModel):
    """Standard error response format."""
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
