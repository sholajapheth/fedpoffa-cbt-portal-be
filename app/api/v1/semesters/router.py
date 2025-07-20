"""
Semester API endpoints for FEDPOFFA CBT Backend.

This module contains FastAPI routes for semester management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin, get_current_user
from app.schemas.semester import (
    SemesterCreate,
    SemesterUpdate,
    SemesterResponse,
    SemesterDetail,
    SemesterListResponse,
    CurrentSemesterResponse,
    SemesterStats,
)
from app.services.semester_service import SemesterService

router = APIRouter()


@router.post("/", response_model=SemesterResponse, status_code=status.HTTP_201_CREATED)
async def create_semester(
    semester_data: SemesterCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Create a new semester (Admin only).

    Args:
        semester_data: Semester creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        SemesterResponse: Created semester data
    """
    service = SemesterService(db)
    return service.create_semester(semester_data)


@router.get("/", response_model=SemesterListResponse)
async def get_semesters(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    active_only: bool = Query(False, description="Filter only active semesters"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get list of semesters with pagination and filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Filter only active semesters
        academic_year: Filter by academic year
        db: Database session
        current_user: Current authenticated user

    Returns:
        SemesterListResponse: List of semesters with pagination info
    """
    service = SemesterService(db)
    return service.get_semesters(
        skip=skip, limit=limit, active_only=active_only, academic_year=academic_year
    )


@router.get("/current", response_model=CurrentSemesterResponse)
async def get_current_semester(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get current semester information.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        CurrentSemesterResponse: Current semester information
    """
    service = SemesterService(db)
    return service.get_current_semester()


@router.get("/{semester_id}", response_model=SemesterDetail)
async def get_semester(
    semester_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get semester by ID with detailed information.

    Args:
        semester_id: Semester ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        SemesterDetail: Semester details with related data
    """
    service = SemesterService(db)
    return service.get_semester(semester_id)


@router.put("/{semester_id}", response_model=SemesterResponse)
async def update_semester(
    semester_id: str,
    semester_data: SemesterUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Update semester (Admin only).

    Args:
        semester_id: Semester ID
        semester_data: Semester update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        SemesterResponse: Updated semester data
    """
    service = SemesterService(db)
    return service.update_semester(semester_id, semester_data)


@router.delete("/{semester_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_semester(
    semester_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Delete semester (Admin only).

    Args:
        semester_id: Semester ID
        db: Database session
        current_user: Current authenticated user
    """
    service = SemesterService(db)
    service.delete_semester(semester_id)


@router.get("/stats/overview", response_model=SemesterStats)
async def get_semester_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Get semester statistics (Admin only).

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        SemesterStats: Semester statistics
    """
    service = SemesterService(db)
    return service.get_semester_stats()
