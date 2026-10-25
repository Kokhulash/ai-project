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
    """Represents an item available for sale in the e-commerce catalog."""
    id: str
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    stockQuantity: Optional[int] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class ProductCreate(BaseModel):
    """Payload for creating a new Product"""
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    stockQuantity: Optional[int] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class ProductUpdate(BaseModel):
    """Payload for updating an existing Product"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    stockQuantity: Optional[int] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class ProductListResponse(BaseModel):
    """Paginated list of Product records"""
    items: List[Product]
    total: int
    limit: int
    offset: int

class Order(BaseModel):
    """Represents a customer's purchase, containing one or more order items."""
    id: str
    customerId: Optional[str] = None
    orderDate: Optional[str] = None
    status: Optional[str] = None
    totalAmount: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class OrderCreate(BaseModel):
    """Payload for creating a new Order"""
    customerId: Optional[str] = None
    orderDate: Optional[str] = None
    status: Optional[str] = None
    totalAmount: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class OrderUpdate(BaseModel):
    """Payload for updating an existing Order"""
    customerId: Optional[str] = None
    orderDate: Optional[str] = None
    status: Optional[str] = None
    totalAmount: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class OrderListResponse(BaseModel):
    """Paginated list of Order records"""
    items: List[Order]
    total: int
    limit: int
    offset: int

class OrderItem(BaseModel):
    """Represents a single line item within an order, linking to a product and specifying quantity and price at the time of order."""
    id: str
    orderId: Optional[str] = None
    productId: Optional[str] = None
    quantity: Optional[int] = None
    priceAtOrder: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class OrderItemCreate(BaseModel):
    """Payload for creating a new OrderItem"""
    orderId: Optional[str] = None
    productId: Optional[str] = None
    quantity: Optional[int] = None
    priceAtOrder: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class OrderItemUpdate(BaseModel):
    """Payload for updating an existing OrderItem"""
    orderId: Optional[str] = None
    productId: Optional[str] = None
    quantity: Optional[int] = None
    priceAtOrder: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class OrderItemListResponse(BaseModel):
    """Paginated list of OrderItem records"""
    items: List[OrderItem]
    total: int
    limit: int
    offset: int
