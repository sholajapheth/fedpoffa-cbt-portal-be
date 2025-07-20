"""
Main API router for FEDPOFFA CBT Backend v1.

This module aggregates all API endpoints for the FEDPOFFA CBT system.
"""

from fastapi import APIRouter

# Import routers from each module
from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router
from app.api.v1.departments.router import router as departments_router
from app.api.v1.courses.router import router as courses_router
from app.api.v1.semesters.router import router as semesters_router
from app.api.v1.questions.router import router as questions_router
from app.api.v1.assessments.router import router as assessments_router
from app.api.v1.sessions.router import router as sessions_router
from app.api.v1.grading.router import router as grading_router
from app.api.v1.analytics.router import router as analytics_router

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(
    departments_router, prefix="/departments", tags=["Departments"]
)
api_router.include_router(courses_router, prefix="/courses", tags=["Courses"])
api_router.include_router(semesters_router, prefix="/semesters", tags=["Semesters"])
api_router.include_router(questions_router, prefix="/questions", tags=["Questions"])
api_router.include_router(
    assessments_router, prefix="/assessments", tags=["Assessments"]
)
api_router.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(grading_router, prefix="/grading", tags=["Grading"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
