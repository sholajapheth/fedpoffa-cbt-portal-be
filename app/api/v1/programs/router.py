"""
Program router for FEDPOFFA CBT Backend.

This module contains API endpoints for program management.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.program_service import ProgramService
from app.schemas.program import (
    ProgramCreate,
    ProgramUpdate,
    ProgramResponse,
    ProgramDetail,
    ProgramListResponse,
    ProgramEnrollmentRequest,
    ProgramEnrollmentResponse,
    ProgramStats,
)
from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    ValidationException,
)

router = APIRouter()


@router.post("/", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    program_data: ProgramCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new program."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create programs",
        )

    program_service = ProgramService(db)
    try:
        program = program_service.create_program(program_data)
        return program
    except (ConflictException, NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=ProgramListResponse)
def get_programs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    level: Optional[str] = Query(None, description="Filter by academic level"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all programs with optional filtering."""
    # Convert department_id string to UUID if provided and not empty
    department_uuid = None
    if department_id and department_id.strip():
        try:
            department_uuid = UUID(department_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid department_id format. Must be a valid UUID.",
            )

    program_service = ProgramService(db)
    programs = program_service.get_programs(
        skip=skip,
        limit=limit,
        department_id=department_uuid,
        is_active=is_active,
        level=level,
    )

    # Convert to response models
    program_responses = []
    for program in programs:
        program_response = ProgramResponse(
            id=str(program.id),
            name=program.name,
            code=program.code,
            description=program.description,
            department_id=str(program.department_id),
            duration_years=program.duration_years,
            level=program.level,
            total_credits=program.total_credits,
            program_coordinator_id=(
                str(program.program_coordinator_id)
                if program.program_coordinator_id
                else None
            ),
            admission_requirements=program.admission_requirements,
            program_outline=program.program_outline,
            career_prospects=program.career_prospects,
            is_active=program.is_active,
            is_accepting_enrollments=program.is_accepting_enrollments,
            created_at=program.created_at,
            updated_at=program.updated_at,
            department_name=program.department.name if program.department else None,
            coordinator_name=(
                program.program_coordinator.full_name
                if program.program_coordinator
                else None
            ),
            total_enrolled_students=program.total_enrolled_students,
            total_courses=program.total_courses,
        )
        program_responses.append(program_response)

    return ProgramListResponse(
        programs=program_responses,
        total=len(program_responses),
        page=skip // limit + 1,
        size=limit,
        pages=(len(program_responses) + limit - 1) // limit,
    )


@router.get("/stats", response_model=ProgramStats)
def get_program_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get program statistics."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view program statistics",
        )

    program_service = ProgramService(db)
    stats = program_service.get_program_stats()
    return ProgramStats(**stats)


@router.get("/{program_id}", response_model=ProgramDetail)
def get_program(
    program_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific program by ID."""
    program_service = ProgramService(db)
    try:
        program = program_service.get_program(program_id)
        return ProgramDetail(
            id=str(program.id),
            name=program.name,
            code=program.code,
            description=program.description,
            department_id=str(program.department_id),
            duration_years=program.duration_years,
            level=program.level,
            total_credits=program.total_credits,
            program_coordinator_id=(
                str(program.program_coordinator_id)
                if program.program_coordinator_id
                else None
            ),
            admission_requirements=program.admission_requirements,
            program_outline=program.program_outline,
            career_prospects=program.career_prospects,
            is_active=program.is_active,
            is_accepting_enrollments=program.is_accepting_enrollments,
            created_at=program.created_at,
            updated_at=program.updated_at,
            department_name=program.department.name if program.department else None,
            coordinator_name=(
                program.program_coordinator.full_name
                if program.program_coordinator
                else None
            ),
            total_enrolled_students=program.total_enrolled_students,
            total_courses=program.total_courses,
            enrolled_students=[],
            courses=[],
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{program_id}", response_model=ProgramResponse)
def update_program(
    program_id: UUID,
    program_data: ProgramUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a program."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update programs",
        )

    program_service = ProgramService(db)
    try:
        program = program_service.update_program(program_id, program_data)
        return ProgramResponse(
            id=str(program.id),
            name=program.name,
            code=program.code,
            description=program.description,
            department_id=str(program.department_id),
            duration_years=program.duration_years,
            level=program.level,
            total_credits=program.total_credits,
            program_coordinator_id=(
                str(program.program_coordinator_id)
                if program.program_coordinator_id
                else None
            ),
            admission_requirements=program.admission_requirements,
            program_outline=program.program_outline,
            career_prospects=program.career_prospects,
            is_active=program.is_active,
            is_accepting_enrollments=program.is_accepting_enrollments,
            created_at=program.created_at,
            updated_at=program.updated_at,
            department_name=program.department.name if program.department else None,
            coordinator_name=(
                program.program_coordinator.full_name
                if program.program_coordinator
                else None
            ),
            total_enrolled_students=program.total_enrolled_students,
            total_courses=program.total_courses,
        )
    except (NotFoundException, ConflictException, ValidationException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a program."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete programs",
        )

    program_service = ProgramService(db)
    try:
        program_service.delete_program(program_id)
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{program_id}/enroll", response_model=ProgramEnrollmentResponse)
def enroll_student_in_program(
    program_id: UUID,
    enrollment_data: ProgramEnrollmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enroll a student in a program."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can enroll students in programs",
        )

    program_service = ProgramService(db)
    try:
        enrollment = program_service.enroll_student_in_program(
            user_id=enrollment_data.user_id,
            program_id=program_id,
            admission_number=enrollment_data.admission_number,
        )
        return ProgramEnrollmentResponse(
            id=str(enrollment.id),
            user_id=str(enrollment.user_id),
            program_id=str(enrollment.program_id),
            enrollment_date=enrollment.enrollment_date,
            status=enrollment.status,
            is_active=enrollment.is_active,
            current_level=enrollment.current_level,
            current_semester=enrollment.current_semester,
            gpa=enrollment.gpa,
            total_credits_earned=enrollment.total_credits_earned,
            student_name=enrollment.student_name,
            program_name=enrollment.program_name,
        )
    except (NotFoundException, ConflictException, ValidationException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{program_id}/enrollments", response_model=List[ProgramEnrollmentResponse])
def get_program_enrollments(
    program_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by enrollment status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get enrollments for a specific program."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view program enrollments",
        )

    program_service = ProgramService(db)
    try:
        enrollments = program_service.get_program_enrollments(
            program_id=program_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        return [
            ProgramEnrollmentResponse(
                id=str(enrollment.id),
                user_id=str(enrollment.user_id),
                program_id=str(enrollment.program_id),
                enrollment_date=enrollment.enrollment_date,
                status=enrollment.status,
                is_active=enrollment.is_active,
                current_level=enrollment.current_level,
                current_semester=enrollment.current_semester,
                gpa=enrollment.gpa,
                total_credits_earned=enrollment.total_credits_earned,
                student_name=enrollment.student_name,
                program_name=enrollment.program_name,
            )
            for enrollment in enrollments
        ]
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/department/{department_id}", response_model=List[ProgramResponse])
def get_department_programs(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all programs for a specific department."""
    program_service = ProgramService(db)
    try:
        programs = program_service.get_department_programs(department_id)
        return [
            ProgramResponse(
                id=str(program.id),
                name=program.name,
                code=program.code,
                description=program.description,
                department_id=str(program.department_id),
                duration_years=program.duration_years,
                level=program.level,
                total_credits=program.total_credits,
                program_coordinator_id=(
                    str(program.program_coordinator_id)
                    if program.program_coordinator_id
                    else None
                ),
                admission_requirements=program.admission_requirements,
                program_outline=program.program_outline,
                career_prospects=program.career_prospects,
                is_active=program.is_active,
                is_accepting_enrollments=program.is_accepting_enrollments,
                created_at=program.created_at,
                updated_at=program.updated_at,
                department_name=program.department.name if program.department else None,
                coordinator_name=(
                    program.program_coordinator.full_name
                    if program.program_coordinator
                    else None
                ),
                total_enrolled_students=program.total_enrolled_students,
                total_courses=program.total_courses,
            )
            for program in programs
        ]
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
