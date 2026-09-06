# Main entrypoint for E-Commerce Store API
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import products
from app.routers import orders

app = FastAPI(
    title="E-Commerce Store API",
    version="1.0.0",
    description="API for products, orders, and customer management.",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "api-forge"}

app.include_router(products.router)
app.include_router(orders.router)
