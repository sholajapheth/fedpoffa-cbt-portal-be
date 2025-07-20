"""
Department API endpoints for FEDPOFFA CBT Backend.

This module contains FastAPI routes for department management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin, get_current_user
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentDetail,
    DepartmentListResponse,
    DepartmentStats,
)
from app.services.department_service import DepartmentService

router = APIRouter()


@router.post(
    "/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Create a new department (Admin only).

    Args:
        department_data: Department creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        DepartmentResponse: Created department data
    """
    service = DepartmentService(db)
    return service.create_department(department_data)


@router.get("/", response_model=DepartmentListResponse)
async def get_departments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    active_only: bool = Query(False, description="Filter only active departments"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get list of departments with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Filter only active departments
        db: Database session
        current_user: Current authenticated user

    Returns:
        DepartmentListResponse: List of departments with pagination info
    """
    service = DepartmentService(db)
    return service.get_departments(skip=skip, limit=limit, active_only=active_only)


@router.get("/{department_id}", response_model=DepartmentDetail)
async def get_department(
    department_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get department by ID with detailed information.

    Args:
        department_id: Department ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        DepartmentDetail: Department details with related data
    """
    service = DepartmentService(db)
    return service.get_department(department_id)


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Update department (Admin only).

    Args:
        department_id: Department ID
        department_data: Department update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        DepartmentResponse: Updated department data
    """
    service = DepartmentService(db)
    return service.update_department(department_id, department_data)


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Delete department (Admin only).

    Args:
        department_id: Department ID
        db: Database session
        current_user: Current authenticated user
    """
    service = DepartmentService(db)
    service.delete_department(department_id)


@router.get("/stats/overview", response_model=DepartmentStats)
async def get_department_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Get department statistics (Admin only).

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        DepartmentStats: Department statistics
    """
    service = DepartmentService(db)
    return service.get_department_stats()
