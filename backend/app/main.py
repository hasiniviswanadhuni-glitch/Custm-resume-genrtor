import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import (
    profile_router,
    job_router,
    match_router,
    suggestions_router,
    resume_router,
    export_router
)

from contextlib import asynccontextmanager

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("customize_resume")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema and storage directories...")
    init_db()
    logger.info("Database initialized successfully.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Explainable Resume Customization Platform Using User Profile and Job Description Analysis",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler to prevent leaking internal stack traces to clients
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again or check input parameters."}
    )

# Include API routers
app.include_router(profile_router, prefix=settings.API_PREFIX)
app.include_router(job_router, prefix=settings.API_PREFIX)
app.include_router(match_router, prefix=settings.API_PREFIX)
app.include_router(suggestions_router, prefix=settings.API_PREFIX)
app.include_router(resume_router, prefix=settings.API_PREFIX)
app.include_router(export_router, prefix=settings.API_PREFIX)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected"
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to Customize Resume Generation API",
        "docs": "/docs",
        "health": "/api/health"
    }
