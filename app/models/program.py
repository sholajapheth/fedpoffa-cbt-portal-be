"""
Program model for FEDPOFFA CBT Backend.

This module contains the Program model with FEDPOFFA-specific fields and relationships.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Program(Base):
    """
    Program model for FEDPOFFA CBT system.

    This model represents FEDPOFFA programs within departments that students enroll into.
    """

    __tablename__ = "programs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Program information
    name = Column(String(255), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Academic information
    department_id = Column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False
    )
    duration_years = Column(Integer, default=2)  # ND = 2 years, HND = 2 years
    level = Column(String(20), nullable=False)  # ND, HND, etc.
    total_credits = Column(Integer, default=0)

    # FEDPOFFA-specific fields
    program_coordinator_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    admission_requirements = Column(Text, nullable=True)
    program_outline = Column(Text, nullable=True)
    career_prospects = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_accepting_enrollments = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="programs")
    program_coordinator = relationship("User", foreign_keys=[program_coordinator_id])
    courses = relationship("Course", back_populates="program")
    enrolled_students = relationship("UserProgram", back_populates="program")

    def __repr__(self):
        return f"<Program(id={self.id}, name='{self.name}', code='{self.code}')>"

    @property
    def total_enrolled_students(self):
        """Get total number of enrolled students."""
        return len(self.enrolled_students) if self.enrolled_students else 0

    @property
    def total_courses(self):
        """Get total number of courses in this program."""
        return len(self.courses) if self.courses else 0

    @property
    def department_name(self):
        """Get department name."""
        return self.department.name if self.department else None

    @property
    def coordinator_name(self):
        """Get program coordinator name."""
        return self.program_coordinator.full_name if self.program_coordinator else None
