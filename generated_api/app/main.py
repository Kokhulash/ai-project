# Main entrypoint for Book Management API
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import books

app = FastAPI(
    title="Book Management API",
    version="1.0.0",
    description="API for managing a collection of books, allowing for creation, retrieval, updating, and deletion of book records. It supports tracking book details like title, author, ISBN, publication year, genre, and copy availability.",
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

app.include_router(books.router)
