"""
Course service for FEDPOFFA CBT Backend.

This module contains business logic for course management.
"""

import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.department import Department
from app.models.user import User
from app.models.course_enrollment import CourseEnrollment
from app.models.semester import Semester
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseDetail,
    CourseListResponse,
    CourseEnrollmentRequest,
    CourseEnrollmentResponse,
    CourseStats,
)


class CourseService:
    """Course service for FEDPOFFA CBT system."""

    def __init__(self, db: Session):
        self.db = db

    def create_course(self, course_data: CourseCreate) -> CourseResponse:
        """
        Create a new course.

        Args:
            course_data: Course creation data

        Returns:
            CourseResponse: Created course data

        Raises:
            HTTPException: If course creation fails
        """
        # Check if department exists
        department = (
            self.db.query(Department)
            .filter(Department.id == course_data.department_id)
            .first()
        )
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Department not found"
            )

        # Check if course with same code already exists
        existing_course = (
            self.db.query(Course).filter(Course.code == course_data.code).first()
        )

        if existing_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course with this code already exists",
            )

        # Create new course
        course = Course(
            id=uuid.uuid4(),
            name=course_data.name,
            code=course_data.code,
            description=course_data.description,
            department_id=course_data.department_id,
            credits=course_data.credits,
            level=course_data.level,
            semester=course_data.semester,
            course_coordinator_id=course_data.course_coordinator_id,
            prerequisites=course_data.prerequisites,
            course_outline=course_data.course_outline,
        )

        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)

        return CourseResponse(
            id=str(course.id),
            name=course.name,
            code=course.code,
            description=course.description,
            department_id=str(course.department_id),
            credits=course.credits,
            level=course.level,
            semester=course.semester,
            course_coordinator_id=(
                str(course.course_coordinator_id)
                if course.course_coordinator_id
                else None
            ),
            prerequisites=course.prerequisites,
            course_outline=course.course_outline,
            is_active=course.is_active,
            is_available=course.is_available,
            created_at=course.created_at,
            updated_at=course.updated_at,
            department_name=department.name,
            coordinator_name=None,  # TODO: Get coordinator name
            total_enrolled_students=0,
            total_assessments=0,
        )

    def get_courses(
        self,
        skip: int = 0,
        limit: int = 100,
        department_id: Optional[str] = None,
        active_only: bool = False,
        available_only: bool = False,
    ) -> CourseListResponse:
        """
        Get list of courses with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            department_id: Filter by department ID
            active_only: Filter only active courses
            available_only: Filter only available courses

        Returns:
            CourseListResponse: List of courses with pagination info
        """
        query = self.db.query(Course)

        if department_id:
            query = query.filter(Course.department_id == department_id)
        if active_only:
            query = query.filter(Course.is_active == True)
        if available_only:
            query = query.filter(Course.is_available == True)

        total = query.count()
        courses = query.offset(skip).limit(limit).all()

        # Convert to response models
        course_responses = []
        for course in courses:
            # Get department name
            department = (
                self.db.query(Department)
                .filter(Department.id == course.department_id)
                .first()
            )
            department_name = department.name if department else None

            # Get coordinator name
            coordinator_name = None
            if course.course_coordinator_id:
                coordinator = (
                    self.db.query(User)
                    .filter(User.id == course.course_coordinator_id)
                    .first()
                )
                coordinator_name = coordinator.full_name if coordinator else None

            course_response = CourseResponse(
                id=str(course.id),
                name=course.name,
                code=course.code,
                description=course.description,
                department_id=str(course.department_id),
                credits=course.credits,
                level=course.level,
                semester=course.semester,
                course_coordinator_id=(
                    str(course.course_coordinator_id)
                    if course.course_coordinator_id
                    else None
                ),
                prerequisites=course.prerequisites,
                course_outline=course.course_outline,
                is_active=course.is_active,
                is_available=course.is_available,
                created_at=course.created_at,
                updated_at=course.updated_at,
                department_name=department_name,
                coordinator_name=coordinator_name,
                total_enrolled_students=course.total_enrolled_students,
                total_assessments=course.total_assessments,
            )
            course_responses.append(course_response)

        pages = (total + limit - 1) // limit if limit > 0 else 1

        return CourseListResponse(
            courses=course_responses,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit,
            pages=pages,
        )

    def get_course(self, course_id: str) -> CourseDetail:
        """
        Get course by ID with detailed information.

        Args:
            course_id: Course ID

        Returns:
            CourseDetail: Course details with related data

        Raises:
            HTTPException: If course not found
        """
        course = self.db.query(Course).filter(Course.id == course_id).first()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )

        # Get department name
        department = (
            self.db.query(Department)
            .filter(Department.id == course.department_id)
            .first()
        )
        department_name = department.name if department else None

        # Get coordinator name
        coordinator_name = None
        if course.course_coordinator_id:
            coordinator = (
                self.db.query(User)
                .filter(User.id == course.course_coordinator_id)
                .first()
            )
            coordinator_name = coordinator.full_name if coordinator else None

        # Get enrolled students
        enrolled_students = (
            self.db.query(User)
            .join(Course.enrolled_students)
            .filter(Course.id == course_id)
            .all()
        )

        students_data = [
            {
                "id": str(student.id),
                "full_name": student.full_name,
                "email": student.email,
                "matric_number": student.matric_number,
            }
            for student in enrolled_students
        ]

        # Get assessments
        assessments = (
            self.db.query(Course).filter(Course.id == course_id).first().assessments
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

        return CourseDetail(
            id=str(course.id),
            name=course.name,
            code=course.code,
            description=course.description,
            department_id=str(course.department_id),
            credits=course.credits,
            level=course.level,
            semester=course.semester,
            course_coordinator_id=(
                str(course.course_coordinator_id)
                if course.course_coordinator_id
                else None
            ),
            prerequisites=course.prerequisites,
            course_outline=course.course_outline,
            is_active=course.is_active,
            is_available=course.is_available,
            created_at=course.created_at,
            updated_at=course.updated_at,
            department_name=department_name,
            coordinator_name=coordinator_name,
            total_enrolled_students=course.total_enrolled_students,
            total_assessments=course.total_assessments,
            enrolled_students=students_data,
            assessments=assessments_data,
        )

    def update_course(
        self, course_id: str, course_data: CourseUpdate
    ) -> CourseResponse:
        """
        Update course.

        Args:
            course_id: Course ID
            course_data: Course update data

        Returns:
            CourseResponse: Updated course data

        Raises:
            HTTPException: If course not found or update fails
        """
        course = self.db.query(Course).filter(Course.id == course_id).first()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )

        # Update fields if provided
        if course_data.name is not None:
            course.name = course_data.name
        if course_data.code is not None:
            # Check if new code already exists
            existing_course = (
                self.db.query(Course)
                .filter(Course.code == course_data.code, Course.id != course_id)
                .first()
            )
            if existing_course:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course with this code already exists",
                )
            course.code = course_data.code
        if course_data.description is not None:
            course.description = course_data.description
        if course_data.department_id is not None:
            # Check if department exists
            department = (
                self.db.query(Department)
                .filter(Department.id == course_data.department_id)
                .first()
            )
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department not found",
                )
            course.department_id = course_data.department_id
        if course_data.credits is not None:
            course.credits = course_data.credits
        if course_data.level is not None:
            course.level = course_data.level
        if course_data.semester is not None:
            course.semester = course_data.semester
        if course_data.course_coordinator_id is not None:
            course.course_coordinator_id = course_data.course_coordinator_id
        if course_data.prerequisites is not None:
            course.prerequisites = course_data.prerequisites
        if course_data.course_outline is not None:
            course.course_outline = course_data.course_outline
        if course_data.is_active is not None:
            course.is_active = course_data.is_active
        if course_data.is_available is not None:
            course.is_available = course_data.is_available

        course.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(course)

        # Get department name for response
        department = (
            self.db.query(Department)
            .filter(Department.id == course.department_id)
            .first()
        )
        department_name = department.name if department else None

        return CourseResponse(
            id=str(course.id),
            name=course.name,
            code=course.code,
            description=course.description,
            department_id=str(course.department_id),
            credits=course.credits,
            level=course.level,
            semester=course.semester,
            course_coordinator_id=(
                str(course.course_coordinator_id)
                if course.course_coordinator_id
                else None
            ),
            prerequisites=course.prerequisites,
            course_outline=course.course_outline,
            is_active=course.is_active,
            is_available=course.is_available,
            created_at=course.created_at,
            updated_at=course.updated_at,
            department_name=department_name,
            coordinator_name=None,  # TODO: Get coordinator name
            total_enrolled_students=course.total_enrolled_students,
            total_assessments=course.total_assessments,
        )

    def delete_course(self, course_id: str):
        """
        Delete course.

        Args:
            course_id: Course ID

        Raises:
            HTTPException: If course not found or has related data
        """
        course = self.db.query(Course).filter(Course.id == course_id).first()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )

        # Check if course has enrolled students
        enrolled_count = (
            self.db.query(CourseEnrollment)
            .filter(CourseEnrollment.course_id == course_id)
            .count()
        )
        if enrolled_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete course with enrolled students",
            )

        # Check if course has assessments
        assessments_count = len(course.assessments) if course.assessments else 0
        if assessments_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete course with existing assessments",
            )

        self.db.delete(course)
        self.db.commit()

    def enroll_in_course(
        self,
        course_id: str,
        enrollment_data: CourseEnrollmentRequest,
        current_user: dict,
    ) -> CourseEnrollmentResponse:
        """
        Enroll in a course.

        Args:
            course_id: Course ID
            enrollment_data: Enrollment data
            current_user: Current authenticated user

        Returns:
            CourseEnrollmentResponse: Enrollment data

        Raises:
            HTTPException: If enrollment fails
        """
        # Check if course exists and is available
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )

        if not course.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is not available for enrollment",
            )

        # Check if semester exists
        semester = (
            self.db.query(Semester)
            .filter(Semester.id == enrollment_data.semester_id)
            .first()
        )
        if not semester:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Semester not found"
            )

        # Check if user is already enrolled
        existing_enrollment = (
            self.db.query(CourseEnrollment)
            .filter(
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.student_id == current_user.id,
                CourseEnrollment.semester_id == enrollment_data.semester_id,
                CourseEnrollment.is_active == True,
            )
            .first()
        )

        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already enrolled in this course",
            )

        # Create enrollment
        enrollment = CourseEnrollment(
            id=uuid.uuid4(),
            student_id=current_user.id,
            course_id=course_id,
            semester_id=enrollment_data.semester_id,
            status="enrolled",
            is_active=True,
        )

        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)

        return CourseEnrollmentResponse(
            id=str(enrollment.id),
            student_id=str(enrollment.student_id),
            course_id=str(enrollment.course_id),
            semester_id=str(enrollment.semester_id),
            enrollment_date=enrollment.enrollment_date,
            status=enrollment.status,
            is_active=enrollment.is_active,
            student_name=current_user.full_name,
            course_name=course.name,
            semester_name=semester.name,
        )

    def get_course_stats(self) -> CourseStats:
        """
        Get course statistics.

        Returns:
            CourseStats: Course statistics
        """
        total_courses = self.db.query(Course).count()
        active_courses = self.db.query(Course).filter(Course.is_active == True).count()
        available_courses = (
            self.db.query(Course).filter(Course.is_available == True).count()
        )

        total_enrollments = (
            self.db.query(CourseEnrollment)
            .filter(CourseEnrollment.is_active == True)
            .count()
        )
        total_assessments = self.db.query(Course).join(Course.assessments).count()

        return CourseStats(
            total_courses=total_courses,
            active_courses=active_courses,
            available_courses=available_courses,
            total_enrollments=total_enrollments,
            total_assessments=total_assessments,
        )
