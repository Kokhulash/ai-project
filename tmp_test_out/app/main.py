# Main entrypoint for Task & Project Management API
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import projects
from app.routers import tasks

app = FastAPI(
    title="Task & Project Management API",
    version="1.0.0",
    description="API for managing projects, tasks, team assignments, and statuses.",
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

app.include_router(projects.router)
app.include_router(tasks.router)
