"""
User model for FEDPOFFA CBT Backend.

This module contains the User model with FEDPOFFA-specific fields and relationships.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.config import FedpoffaConstants

# Association table for many-to-many relationship between users and courses
user_course_association = Table(
    "user_courses",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("course_id", UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True),
    Column("enrolled_at", DateTime, default=datetime.utcnow),
    Column("is_active", Boolean, default=True),
)


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
    department_id = Column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )
    level = Column(String(20), nullable=True)  # ND1, ND2, HND1, HND2, etc.
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
    department = relationship("Department", back_populates="users")
    enrolled_courses = relationship(
        "Course", secondary=user_course_association, back_populates="enrolled_students"
    )

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
