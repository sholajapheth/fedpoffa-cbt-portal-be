"""
Semester model for FEDPOFFA CBT Backend.

This module contains the Semester model to manage academic semesters.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Semester(Base):
    """
    Semester model for FEDPOFFA CBT system.

    This model represents academic semesters and manages the academic calendar.
    """

    __tablename__ = "semesters"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Semester information
    name = Column(String(100), nullable=False)  # e.g., "2025/2026 First Semester"
    academic_year = Column(String(20), nullable=False)  # e.g., "2025/2026"
    semester_type = Column(String(20), nullable=False)  # "first", "second", "summer"

    # Academic calendar
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    registration_start = Column(Date, nullable=True)
    registration_end = Column(Date, nullable=True)
    exam_start = Column(Date, nullable=True)
    exam_end = Column(Date, nullable=True)

    # FEDPOFFA-specific fields
    description = Column(Text, nullable=True)
    is_current = Column(Boolean, default=False)  # Only one semester can be current
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessments = relationship("Assessment", back_populates="semester")
    course_enrollments = relationship("CourseEnrollment", back_populates="semester")

    def __repr__(self):
        return f"<Semester(id={self.id}, name='{self.name}', academic_year='{self.academic_year}')>"

    @property
    def is_registration_open(self):
        """Check if registration is currently open."""
        today = date.today()
        return (
            self.registration_start
            and self.registration_end
            and self.registration_start <= today <= self.registration_end
        )

    @property
    def is_exam_period(self):
        """Check if we're in the exam period."""
        today = date.today()
        return (
            self.exam_start
            and self.exam_end
            and self.exam_start <= today <= self.exam_end
        )

    @property
    def is_active_period(self):
        """Check if we're in the active semester period."""
        today = date.today()
        return self.start_date <= today <= self.end_date

    @property
    def total_assessments(self):
        """Get total number of assessments in this semester."""
        return len(self.assessments) if self.assessments else 0

    @property
    def total_enrollments(self):
        """Get total number of course enrollments in this semester."""
        return len(self.course_enrollments) if self.course_enrollments else 0
