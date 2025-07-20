"""
Semester service for FEDPOFFA CBT Backend.

This module contains business logic for semester management.
"""

import uuid
from typing import List, Optional
from datetime import datetime, date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.semester import Semester
from app.models.assessment import Assessment
from app.models.course_enrollment import CourseEnrollment
from app.schemas.semester import (
    SemesterCreate,
    SemesterUpdate,
    SemesterResponse,
    SemesterDetail,
    SemesterListResponse,
    CurrentSemesterResponse,
    SemesterStats,
)


class SemesterService:
    """Semester service for FEDPOFFA CBT system."""

    def __init__(self, db: Session):
        self.db = db

    def create_semester(self, semester_data: SemesterCreate) -> SemesterResponse:
        """
        Create a new semester.

        Args:
            semester_data: Semester creation data

        Returns:
            SemesterResponse: Created semester data

        Raises:
            HTTPException: If semester creation fails
        """
        # Check if semester with same name already exists
        existing_semester = (
            self.db.query(Semester).filter(Semester.name == semester_data.name).first()
        )

        if existing_semester:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Semester with this name already exists",
            )

        # If this is set as current semester, unset other current semesters
        if semester_data.is_current:
            self.db.query(Semester).update({Semester.is_current: False})

        # Create new semester
        semester = Semester(
            id=uuid.uuid4(),
            name=semester_data.name,
            academic_year=semester_data.academic_year,
            semester_type=semester_data.semester_type,
            start_date=semester_data.start_date,
            end_date=semester_data.end_date,
            registration_start=semester_data.registration_start,
            registration_end=semester_data.registration_end,
            exam_start=semester_data.exam_start,
            exam_end=semester_data.exam_end,
            description=semester_data.description,
            is_current=semester_data.is_current,
        )

        self.db.add(semester)
        self.db.commit()
        self.db.refresh(semester)

        return SemesterResponse(
            id=str(semester.id),
            name=semester.name,
            academic_year=semester.academic_year,
            semester_type=semester.semester_type,
            start_date=semester.start_date,
            end_date=semester.end_date,
            registration_start=semester.registration_start,
            registration_end=semester.registration_end,
            exam_start=semester.exam_start,
            exam_end=semester.exam_end,
            description=semester.description,
            is_current=semester.is_current,
            is_active=semester.is_active,
            created_at=semester.created_at,
            updated_at=semester.updated_at,
            is_registration_open=semester.is_registration_open,
            is_exam_period=semester.is_exam_period,
            is_active_period=semester.is_active_period,
            total_assessments=semester.total_assessments,
            total_enrollments=semester.total_enrollments,
        )

    def get_semesters(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        academic_year: Optional[str] = None,
    ) -> SemesterListResponse:
        """
        Get list of semesters with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Filter only active semesters
            academic_year: Filter by academic year

        Returns:
            SemesterListResponse: List of semesters with pagination info
        """
        query = self.db.query(Semester)

        if active_only:
            query = query.filter(Semester.is_active == True)
        if academic_year:
            query = query.filter(Semester.academic_year == academic_year)

        total = query.count()
        semesters = query.offset(skip).limit(limit).all()

        # Convert to response models
        semester_responses = []
        for semester in semesters:
            semester_response = SemesterResponse(
                id=str(semester.id),
                name=semester.name,
                academic_year=semester.academic_year,
                semester_type=semester.semester_type,
                start_date=semester.start_date,
                end_date=semester.end_date,
                registration_start=semester.registration_start,
                registration_end=semester.registration_end,
                exam_start=semester.exam_start,
                exam_end=semester.exam_end,
                description=semester.description,
                is_current=semester.is_current,
                is_active=semester.is_active,
                created_at=semester.created_at,
                updated_at=semester.updated_at,
                is_registration_open=semester.is_registration_open,
                is_exam_period=semester.is_exam_period,
                is_active_period=semester.is_active_period,
                total_assessments=semester.total_assessments,
                total_enrollments=semester.total_enrollments,
            )
            semester_responses.append(semester_response)

        pages = (total + limit - 1) // limit if limit > 0 else 1

        return SemesterListResponse(
            semesters=semester_responses,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit,
            pages=pages,
        )

    def get_current_semester(self) -> CurrentSemesterResponse:
        """
        Get current semester information.

        Returns:
            CurrentSemesterResponse: Current semester information
        """
        current_semester = (
            self.db.query(Semester).filter(Semester.is_current == True).first()
        )

        if not current_semester:
            return CurrentSemesterResponse(
                semester=None,
                registration_status="no_current_semester",
                exam_status="no_current_semester",
                academic_calendar={},
            )

        # Determine registration and exam status
        registration_status = (
            "open" if current_semester.is_registration_open else "closed"
        )
        exam_status = "active" if current_semester.is_exam_period else "inactive"

        # Create academic calendar
        academic_calendar = {
            "semester_start": current_semester.start_date.isoformat(),
            "semester_end": current_semester.end_date.isoformat(),
            "registration_start": (
                current_semester.registration_start.isoformat()
                if current_semester.registration_start
                else None
            ),
            "registration_end": (
                current_semester.registration_end.isoformat()
                if current_semester.registration_end
                else None
            ),
            "exam_start": (
                current_semester.exam_start.isoformat()
                if current_semester.exam_start
                else None
            ),
            "exam_end": (
                current_semester.exam_end.isoformat()
                if current_semester.exam_end
                else None
            ),
        }

        return CurrentSemesterResponse(
            semester=SemesterResponse(
                id=str(current_semester.id),
                name=current_semester.name,
                academic_year=current_semester.academic_year,
                semester_type=current_semester.semester_type,
                start_date=current_semester.start_date,
                end_date=current_semester.end_date,
                registration_start=current_semester.registration_start,
                registration_end=current_semester.registration_end,
                exam_start=current_semester.exam_start,
                exam_end=current_semester.exam_end,
                description=current_semester.description,
                is_current=current_semester.is_current,
                is_active=current_semester.is_active,
                created_at=current_semester.created_at,
                updated_at=current_semester.updated_at,
                is_registration_open=current_semester.is_registration_open,
                is_exam_period=current_semester.is_exam_period,
                is_active_period=current_semester.is_active_period,
                total_assessments=current_semester.total_assessments,
                total_enrollments=current_semester.total_enrollments,
            ),
            registration_status=registration_status,
            exam_status=exam_status,
            academic_calendar=academic_calendar,
        )

    def get_semester(self, semester_id: str) -> SemesterDetail:
        """
        Get semester by ID with detailed information.

        Args:
            semester_id: Semester ID

        Returns:
            SemesterDetail: Semester details with related data

        Raises:
            HTTPException: If semester not found
        """
        semester = self.db.query(Semester).filter(Semester.id == semester_id).first()

        if not semester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found"
            )

        # Get assessments for this semester
        assessments = (
            self.db.query(Assessment)
            .filter(Assessment.semester_id == semester_id)
            .all()
        )
        assessments_data = [
            {
                "id": str(assessment.id),
                "title": assessment.title,
                "type": assessment.type,
                "status": "active" if assessment.is_active else "inactive",
            }
            for assessment in assessments
        ]

        # Get enrollments for this semester
        enrollments = (
            self.db.query(CourseEnrollment)
            .filter(CourseEnrollment.semester_id == semester_id)
            .all()
        )
        enrollments_data = [
            {
                "id": str(enrollment.id),
                "student_id": str(enrollment.student_id),
                "course_id": str(enrollment.course_id),
                "status": enrollment.status,
            }
            for enrollment in enrollments
        ]

        return SemesterDetail(
            id=str(semester.id),
            name=semester.name,
            academic_year=semester.academic_year,
            semester_type=semester.semester_type,
            start_date=semester.start_date,
            end_date=semester.end_date,
            registration_start=semester.registration_start,
            registration_end=semester.registration_end,
            exam_start=semester.exam_start,
            exam_end=semester.exam_end,
            description=semester.description,
            is_current=semester.is_current,
            is_active=semester.is_active,
            created_at=semester.created_at,
            updated_at=semester.updated_at,
            is_registration_open=semester.is_registration_open,
            is_exam_period=semester.is_exam_period,
            is_active_period=semester.is_active_period,
            total_assessments=semester.total_assessments,
            total_enrollments=semester.total_enrollments,
            assessments=assessments_data,
            enrollments=enrollments_data,
        )

    def update_semester(
        self, semester_id: str, semester_data: SemesterUpdate
    ) -> SemesterResponse:
        """
        Update semester.

        Args:
            semester_id: Semester ID
            semester_data: Semester update data

        Returns:
            SemesterResponse: Updated semester data

        Raises:
            HTTPException: If semester not found or update fails
        """
        semester = self.db.query(Semester).filter(Semester.id == semester_id).first()

        if not semester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found"
            )

        # Update fields if provided
        if semester_data.name is not None:
            semester.name = semester_data.name
        if semester_data.academic_year is not None:
            semester.academic_year = semester_data.academic_year
        if semester_data.semester_type is not None:
            semester.semester_type = semester_data.semester_type
        if semester_data.start_date is not None:
            semester.start_date = semester_data.start_date
        if semester_data.end_date is not None:
            semester.end_date = semester_data.end_date
        if semester_data.registration_start is not None:
            semester.registration_start = semester_data.registration_start
        if semester_data.registration_end is not None:
            semester.registration_end = semester_data.registration_end
        if semester_data.exam_start is not None:
            semester.exam_start = semester_data.exam_start
        if semester_data.exam_end is not None:
            semester.exam_end = semester_data.exam_end
        if semester_data.description is not None:
            semester.description = semester_data.description
        if semester_data.is_current is not None:
            # If setting as current, unset other current semesters
            if semester_data.is_current:
                self.db.query(Semester).update({Semester.is_current: False})
            semester.is_current = semester_data.is_current
        if semester_data.is_active is not None:
            semester.is_active = semester_data.is_active

        semester.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(semester)

        return SemesterResponse(
            id=str(semester.id),
            name=semester.name,
            academic_year=semester.academic_year,
            semester_type=semester.semester_type,
            start_date=semester.start_date,
            end_date=semester.end_date,
            registration_start=semester.registration_start,
            registration_end=semester.registration_end,
            exam_start=semester.exam_start,
            exam_end=semester.exam_end,
            description=semester.description,
            is_current=semester.is_current,
            is_active=semester.is_active,
            created_at=semester.created_at,
            updated_at=semester.updated_at,
            is_registration_open=semester.is_registration_open,
            is_exam_period=semester.is_exam_period,
            is_active_period=semester.is_active_period,
            total_assessments=semester.total_assessments,
            total_enrollments=semester.total_enrollments,
        )

    def delete_semester(self, semester_id: str):
        """
        Delete semester.

        Args:
            semester_id: Semester ID

        Raises:
            HTTPException: If semester not found or has related data
        """
        semester = self.db.query(Semester).filter(Semester.id == semester_id).first()

        if not semester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found"
            )

        # Check if semester has assessments
        assessments_count = (
            self.db.query(Assessment)
            .filter(Assessment.semester_id == semester_id)
            .count()
        )
        if assessments_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete semester with existing assessments",
            )

        # Check if semester has enrollments
        enrollments_count = (
            self.db.query(CourseEnrollment)
            .filter(CourseEnrollment.semester_id == semester_id)
            .count()
        )
        if enrollments_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete semester with existing enrollments",
            )

        self.db.delete(semester)
        self.db.commit()

    def get_semester_stats(self) -> SemesterStats:
        """
        Get semester statistics.

        Returns:
            SemesterStats: Semester statistics
        """
        total_semesters = self.db.query(Semester).count()
        active_semesters = (
            self.db.query(Semester).filter(Semester.is_active == True).count()
        )

        current_semester = (
            self.db.query(Semester).filter(Semester.is_current == True).first()
        )
        current_semester_name = current_semester.name if current_semester else None

        total_assessments = self.db.query(Assessment).count()
        total_enrollments = (
            self.db.query(CourseEnrollment)
            .filter(CourseEnrollment.is_active == True)
            .count()
        )

        return SemesterStats(
            total_semesters=total_semesters,
            active_semesters=active_semesters,
            current_semester=current_semester_name,
            total_assessments=total_assessments,
            total_enrollments=total_enrollments,
        )
