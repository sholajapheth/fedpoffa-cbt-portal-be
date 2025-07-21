"""
User model for FEDPOFFA CBT Backend.

This module contains the User model with FEDPOFFA-specific fields and relationships.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.config import FedpoffaConstants


class User(Base):
    """
    User model for FEDPOFFA CBT system.

    This model represents students, lecturers, administrators, and IT admins
    in the FEDPOFFA system.
    """

    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # FEDPOFFA-specific fields
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)

    # FEDPOFFA academic information
    matric_number = Column(
        String(50), unique=True, nullable=False
    )  # Required for all users

    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Role and permissions
    role = Column(String(20), nullable=False, default=FedpoffaConstants.ROLE_STUDENT)

    # Profile information
    profile_picture = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    # Program enrollments (primary enrollment method)
    program_enrollments = relationship("UserProgram", back_populates="user")

    # Course enrollments (for specific course enrollments within programs)
    course_enrollments = relationship("CourseEnrollment", back_populates="student")

    # Assessment relationships
    created_assessments = relationship("Assessment", back_populates="creator")
    assessment_sessions = relationship("AssessmentSession", back_populates="student")
    grading_sessions_as_lecturer = relationship(
        "GradingSession",
        foreign_keys="[GradingSession.lecturer_id]",
        back_populates="lecturer",
    )
    grading_sessions_as_student = relationship(
        "GradingSession",
        foreign_keys="[GradingSession.student_id]",
        back_populates="student",
    )

    def __repr__(self):
        return f"<User(id={self.id}, matric_number='{self.matric_number}', email='{self.email}', role='{self.role}')>"

    @property
    def full_name(self):
        """Get the full name of the user."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def is_student(self):
        """Check if user is a student."""
        return self.role == FedpoffaConstants.ROLE_STUDENT

    @property
    def is_lecturer(self):
        """Check if user is a lecturer."""
        return self.role == FedpoffaConstants.ROLE_LECTURER

    @property
    def is_admin(self):
        """Check if user is an administrator."""
        return self.role in [
            FedpoffaConstants.ROLE_ADMIN,
            FedpoffaConstants.ROLE_IT_ADMIN,
        ]

    @property
    def is_it_admin(self):
        """Check if user is an IT administrator."""
        return self.role == FedpoffaConstants.ROLE_IT_ADMIN

    @property
    def current_program_enrollment(self):
        """Get the user's current active program enrollment."""
        if not self.program_enrollments:
            return None
        # Return the first active program enrollment
        for enrollment in self.program_enrollments:
            if enrollment.is_active:
                return enrollment
        return None

    @property
    def department(self):
        """Get the user's department through their program enrollment."""
        enrollment = self.current_program_enrollment
        if enrollment and enrollment.program:
            return enrollment.program.department
        return None

    @property
    def current_level(self):
        """Get the user's current academic level from program enrollment."""
        enrollment = self.current_program_enrollment
        if enrollment and hasattr(enrollment, "current_level"):
            return enrollment.current_level
        return None
