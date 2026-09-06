# Main entrypoint for Book Library API
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import books
from app.routers import users
from app.routers import borrowings

app = FastAPI(
    title="Book Library API",
    version="1.0.0",
    description="API for managing books and facilitating the borrowing and returning of books by users in a library system. It allows users to browse available books, borrow them, and return them, while also providing administrative functions for managing the book catalog.",
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
app.include_router(users.router)
app.include_router(borrowings.router)
