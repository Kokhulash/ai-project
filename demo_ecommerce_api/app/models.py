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

class Product(BaseModel):
    """Store merchandise"""
    id: str
    title: str
    price: Optional[str] = None
    stock: Optional[int] = None

class ProductCreate(BaseModel):
    """Payload for creating a new Product"""
    title: str
    price: Optional[str] = None
    stock: Optional[int] = None

class ProductUpdate(BaseModel):
    """Payload for updating an existing Product"""
    title: Optional[str] = None
    price: Optional[str] = None
    stock: Optional[int] = None

class ProductListResponse(BaseModel):
    """Paginated list of Product records"""
    items: List[Product]
    total: int
    limit: int
    offset: int

class Order(BaseModel):
    """Customer purchase order"""
    id: str
    customer_id: Optional[str] = None
    total_amount: Optional[str] = None
    status: Optional[str] = None

class OrderCreate(BaseModel):
    """Payload for creating a new Order"""
    customer_id: Optional[str] = None
    total_amount: Optional[str] = None
    status: Optional[str] = None

class OrderUpdate(BaseModel):
    """Payload for updating an existing Order"""
    customer_id: Optional[str] = None
    total_amount: Optional[str] = None
    status: Optional[str] = None

class OrderListResponse(BaseModel):
    """Paginated list of Order records"""
    items: List[Order]
    total: int
    limit: int
    offset: int
