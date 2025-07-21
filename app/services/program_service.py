"""
Program service for FEDPOFFA CBT Backend.

This module contains business logic for program management.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.program import Program
from app.models.user_program import UserProgram
from app.models.user import User
from app.models.department import Department
from app.schemas.program import ProgramCreate, ProgramUpdate
from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    ValidationException,
)


class ProgramService:
    """Service for program management operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_program(self, program_data: ProgramCreate) -> Program:
        """Create a new program."""
        # Check if program code already exists
        existing_program = (
            self.db.query(Program).filter(Program.code == program_data.code).first()
        )
        if existing_program:
            raise ConflictException(
                f"Program with code '{program_data.code}' already exists"
            )

        # Verify department exists
        department = (
            self.db.query(Department)
            .filter(Department.id == program_data.department_id)
            .first()
        )
        if not department:
            raise NotFoundException(
                f"Department with ID '{program_data.department_id}' not found"
            )

        # Create program
        program = Program(**program_data.model_dump())
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        return program

    def get_program(self, program_id: UUID) -> Program:
        """Get a program by ID."""
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            raise NotFoundException(f"Program with ID '{program_id}' not found")
        return program

    def get_programs(
        self,
        skip: int = 0,
        limit: int = 100,
        department_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        level: Optional[str] = None,
    ) -> List[Program]:
        """Get programs with optional filtering."""
        query = self.db.query(Program)

        if department_id:
            query = query.filter(Program.department_id == department_id)
        if is_active is not None:
            query = query.filter(Program.is_active == is_active)
        if level:
            query = query.filter(Program.level == level)

        return query.offset(skip).limit(limit).all()

    def update_program(self, program_id: UUID, program_data: ProgramUpdate) -> Program:
        """Update a program."""
        program = self.get_program(program_id)

        # Check if new code conflicts with existing programs
        if program_data.code and program_data.code != program.code:
            existing_program = (
                self.db.query(Program)
                .filter(
                    and_(Program.code == program_data.code, Program.id != program_id)
                )
                .first()
            )
            if existing_program:
                raise ConflictException(
                    f"Program with code '{program_data.code}' already exists"
                )

        # Update program
        update_data = program_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(program, field, value)

        self.db.commit()
        self.db.refresh(program)
        return program

    def delete_program(self, program_id: UUID) -> bool:
        """Delete a program."""
        program = self.get_program(program_id)

        # Check if program has enrolled students
        enrolled_students = (
            self.db.query(UserProgram)
            .filter(
                and_(
                    UserProgram.program_id == program_id, UserProgram.is_active == True
                )
            )
            .count()
        )
        if enrolled_students > 0:
            raise ValidationException(
                f"Cannot delete program '{program.name}' - it has {enrolled_students} enrolled students"
            )

        # Check if program has courses
        if program.courses:
            raise ValidationException(
                f"Cannot delete program '{program.name}' - it has {len(program.courses)} courses"
            )

        self.db.delete(program)
        self.db.commit()
        return True

    def enroll_student_in_program(
        self, user_id: UUID, program_id: UUID, admission_number: Optional[str] = None
    ) -> UserProgram:
        """Enroll a student in a program."""
        # Verify user exists and is a student
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(f"User with ID '{user_id}' not found")
        if not user.is_student:
            raise ValidationException("Only students can be enrolled in programs")

        # Verify program exists and is accepting enrollments
        program = self.get_program(program_id)
        if not program.is_active:
            raise ValidationException(f"Program '{program.name}' is not active")
        if not program.is_accepting_enrollments:
            raise ValidationException(
                f"Program '{program.name}' is not accepting enrollments"
            )

        # Check if student is already enrolled in this program
        existing_enrollment = (
            self.db.query(UserProgram)
            .filter(
                and_(
                    UserProgram.user_id == user_id, UserProgram.program_id == program_id
                )
            )
            .first()
        )
        if existing_enrollment:
            if existing_enrollment.is_active:
                raise ConflictException("Student is already enrolled in this program")
            else:
                # Reactivate enrollment
                existing_enrollment.is_active = True
                existing_enrollment.status = "enrolled"
                self.db.commit()
                self.db.refresh(existing_enrollment)
                return existing_enrollment

        # Create new enrollment
        enrollment = UserProgram(
            user_id=user_id,
            program_id=program_id,
            admission_number=admission_number,
            current_level="ND1",  # Default starting level
            current_semester="First",  # Default starting semester
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def get_student_program_enrollment(self, user_id: UUID) -> Optional[UserProgram]:
        """Get a student's active program enrollment."""
        return (
            self.db.query(UserProgram)
            .filter(and_(UserProgram.user_id == user_id, UserProgram.is_active == True))
            .first()
        )

    def get_program_enrollments(
        self,
        program_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[UserProgram]:
        """Get enrollments for a specific program."""
        query = self.db.query(UserProgram).filter(UserProgram.program_id == program_id)

        if status:
            query = query.filter(UserProgram.status == status)

        return query.offset(skip).limit(limit).all()

    def update_enrollment_status(
        self, enrollment_id: UUID, status: str, **kwargs
    ) -> UserProgram:
        """Update enrollment status."""
        enrollment = (
            self.db.query(UserProgram).filter(UserProgram.id == enrollment_id).first()
        )
        if not enrollment:
            raise NotFoundException(f"Enrollment with ID '{enrollment_id}' not found")

        valid_statuses = ["enrolled", "graduated", "dropped", "suspended"]
        if status not in valid_statuses:
            raise ValidationException(
                f"Invalid status. Must be one of: {valid_statuses}"
            )

        enrollment.status = status
        for key, value in kwargs.items():
            if hasattr(enrollment, key):
                setattr(enrollment, key, value)

        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def get_program_stats(self) -> Dict[str, Any]:
        """Get program statistics."""
        total_programs = self.db.query(Program).count()
        active_programs = (
            self.db.query(Program).filter(Program.is_active == True).count()
        )
        accepting_enrollments = (
            self.db.query(Program)
            .filter(
                and_(
                    Program.is_active == True, Program.is_accepting_enrollments == True
                )
            )
            .count()
        )
        total_enrollments = (
            self.db.query(UserProgram).filter(UserProgram.is_active == True).count()
        )

        # Get total courses across all programs
        from app.models.course import Course

        total_courses = self.db.query(Course).count()

        return {
            "total_programs": total_programs,
            "active_programs": active_programs,
            "accepting_enrollments": accepting_enrollments,
            "total_enrollments": total_enrollments,
            "total_courses": total_courses,
        }

    def get_department_programs(self, department_id: UUID) -> List[Program]:
        """Get all programs for a specific department."""
        return (
            self.db.query(Program)
            .filter(
                and_(Program.department_id == department_id, Program.is_active == True)
            )
            .all()
        )
