"""
FEDPOFFA CBT Backend - Main Application Entry Point

This module contains the main FastAPI application with FEDPOFFA-specific configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.api import api_router

# Create FastAPI application with FEDPOFFA branding
app = FastAPI(
    title="FEDPOFFA CBT System API",
    description="""
    Computer-Based Testing System API for Federal Polytechnic Offa.
    
    This API provides comprehensive testing capabilities including:
    - User authentication and management
    - Question bank management
    - Assessment creation and scheduling
    - Test-taking sessions
    - Automatic and manual grading
    - Analytics and reporting
    
    **FEDPOFFA Branding**: Purple (#6B46C1), Orange (#F59E0B), Green (#10B981)
    """,
    version="0.1.0",
    contact={
        "name": "FEDPOFFA IT Team",
        "url": "https://portal.fedpoffaonline.edu.ng/",
    },
    license_info={
        "name": "FEDPOFFA Internal",
        "url": "https://portal.fedpoffaonline.edu.ng/",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS for FEDPOFFA frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Root endpoint with FEDPOFFA branding information.
    """
    return JSONResponse(
        content={
            "message": "Welcome to FEDPOFFA CBT System API",
            "institution": "Federal Polytechnic Offa",
            "version": "0.1.0",
            "status": "active",
            "branding": {
                "primary_color": "#6B46C1",
                "accent_color": "#F59E0B",
                "success_color": "#10B981",
            },
            "docs": "/docs",
            "redoc": "/redoc",
        }
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "service": "FEDPOFFA CBT Backend"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
