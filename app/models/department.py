"""
Department model for FEDPOFFA CBT Backend.

This module contains the Department model with FEDPOFFA-specific fields and relationships.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Department(Base):
    """
    Department model for FEDPOFFA CBT system.

    This model represents FEDPOFFA departments with their associated programs and courses.
    """

    __tablename__ = "departments"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Department information
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(10), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # FEDPOFFA-specific fields
    hod_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )  # Head of Department

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    programs = relationship("Program", back_populates="department")
    courses = relationship("Course", back_populates="department")
    hod = relationship("User", foreign_keys=[hod_id])

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', code='{self.code}')>"

    @property
    def total_programs(self):
        """Get total number of programs in this department."""
        return len(self.programs) if self.programs else 0

    @property
    def total_courses(self):
        """Get total number of courses in this department."""
        return len(self.courses) if self.courses else 0

    @property
    def students_count(self):
        """Get number of students in this department through program enrollments."""
        total_students = 0
        for program in self.programs:
            total_students += len([e for e in program.enrolled_students if e.is_active])
        return total_students

    @property
    def total_users(self):
        """Get total number of users in this department through program enrollments."""
        total_users = 0
        for program in self.programs:
            total_users += len([e for e in program.enrolled_students if e.is_active])
        return total_users

    @property
    def lecturers_count(self):
        """Get number of lecturers in this department."""
        # This would need to be implemented based on how lecturers are assigned
        # For now, return 0 as we need to define lecturer assignment logic
        return 0

    @property
    def hod_name(self):
        """Get HOD name."""
        return self.hod.full_name if self.hod else None

    @property
    def hod_email(self):
        """Get HOD email."""
        return self.hod.email if self.hod else None

    @property
    def hod_phone(self):
        """Get HOD phone number."""
        return self.hod.phone_number if self.hod else None
