"""
Course API endpoints for FEDPOFFA CBT Backend.

This module contains FastAPI routes for course management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    require_admin,
    get_current_user,
    require_lecturer,
)
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseDetail,
    CourseListResponse,
    CourseEnrollmentRequest,
    CourseEnrollmentResponse,
    CourseStats,
    StudentCourseListResponse,
    LecturerCourseListResponse,
)
from app.services.course_service import CourseService

router = APIRouter()


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Create a new course (Admin only).

    Args:
        course_data: Course creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        CourseResponse: Created course data
    """
    service = CourseService(db)
    return service.create_course(course_data)


@router.get("/", response_model=CourseListResponse)
async def get_courses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    active_only: bool = Query(False, description="Filter only active courses"),
    available_only: bool = Query(False, description="Filter only available courses"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get list of courses with pagination and filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        department_id: Filter by department ID
        active_only: Filter only active courses
        available_only: Filter only available courses
        db: Database session
        current_user: Current authenticated user

    Returns:
        CourseListResponse: List of courses with pagination info
    """
    service = CourseService(db)
    return service.get_courses(
        skip=skip,
        limit=limit,
        department_id=department_id,
        active_only=active_only,
        available_only=available_only,
    )


@router.get("/{course_id}", response_model=CourseDetail)
async def get_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get course by ID with detailed information.

    Args:
        course_id: Course ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        CourseDetail: Course details with related data
    """
    service = CourseService(db)
    return service.get_course(course_id)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Update course (Admin only).

    Args:
        course_id: Course ID
        course_data: Course update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        CourseResponse: Updated course data
    """
    service = CourseService(db)
    return service.update_course(course_id, course_data)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Delete course (Admin only).

    Args:
        course_id: Course ID
        db: Database session
        current_user: Current authenticated user
    """
    service = CourseService(db)
    service.delete_course(course_id)


@router.post("/{course_id}/enroll", response_model=CourseEnrollmentResponse)
async def enroll_in_course(
    course_id: str,
    enrollment_data: CourseEnrollmentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Enroll in a course.

    Args:
        course_id: Course ID
        enrollment_data: Enrollment data
        db: Database session
        current_user: Current authenticated user

    Returns:
        CourseEnrollmentResponse: Enrollment data
    """
    service = CourseService(db)
    return service.enroll_in_course(course_id, enrollment_data, current_user)


@router.get("/stats/overview", response_model=CourseStats)
async def get_course_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Get course statistics (Admin only).

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        CourseStats: Course statistics
    """
    service = CourseService(db)
    return service.get_course_stats()


@router.get("/my/enrolled", response_model=StudentCourseListResponse)
async def get_my_enrolled_courses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    status_filter: Optional[str] = Query(
        None,
        description="Filter by enrollment status (enrolled, completed, failed, dropped)",
    ),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get current user's enrolled courses (Students only).

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by enrollment status
        db: Database session
        current_user: Current authenticated user

    Returns:
        StudentCourseListResponse: List of enrolled courses
    """
    # Check if user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for students",
        )

    service = CourseService(db)
    return service.get_student_courses(
        user_id=str(current_user.id),
        skip=skip,
        limit=limit,
        status_filter=status_filter,
    )


@router.get("/my/coordinated", response_model=LecturerCourseListResponse)
async def get_my_coordinated_courses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    active_only: bool = Query(False, description="Filter only active courses"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get current user's coordinated courses (Lecturers only).

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        active_only: Filter only active courses
        db: Database session
        current_user: Current authenticated user

    Returns:
        LecturerCourseListResponse: List of coordinated courses
    """
    # Check if user is a lecturer
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for lecturers",
        )

    service = CourseService(db)
    return service.get_lecturer_courses(
        user_id=str(current_user.id),
        skip=skip,
        limit=limit,
        active_only=active_only,
    )
