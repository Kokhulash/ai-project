# Main entrypoint for Healthcare Clinical API
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import patients
from app.routers import appointments

app = FastAPI(
    title="Healthcare Clinical API",
    version="1.0.0",
    description="API for patient health records and clinical appointments.",
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

app.include_router(patients.router)
app.include_router(appointments.router)
