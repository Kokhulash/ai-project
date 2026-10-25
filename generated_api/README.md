# E-Commerce Product and Order Management API

API for managing products available for sale and customer orders within an e-commerce system. It supports product catalog management, including creation, retrieval, update, and deletion of products, as well as the full lifecycle of customer orders, from creation to status updates and cancellation.

Designed and generated using **APIForge AI** multi-agent framework.

## Getting Started

### 1. Run the Backend Service
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 2. View Interactive Documentation
- **Swagger UI**: Open `swagger.html` in your browser or visit `http://localhost:8000/docs`
- **Redoc**: Open `redoc.html` in your browser or visit `http://localhost:8000/redoc`
- **API Reference**: Read `API_REFERENCE.md`

### 3. Run Automated Tests
```bash
pytest tests/ -v
```
