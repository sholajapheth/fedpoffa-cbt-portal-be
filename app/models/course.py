"""
Course model for FEDPOFFA CBT Backend.

This module contains the Course model with FEDPOFFA-specific fields and relationships.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Course(Base):
    """
    Course model for FEDPOFFA CBT system.

    This model represents FEDPOFFA courses with their associated departments, students, and lecturers.
    """

    __tablename__ = "courses"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Course information
    name = Column(String(255), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Academic information
    department_id = Column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False
    )
    credits = Column(Integer, default=0)
    level = Column(String(20), nullable=True)  # ND1, ND2, HND1, HND2, etc.
    semester = Column(String(20), nullable=True)  # First, Second, Summer

    # FEDPOFFA-specific fields
    course_coordinator_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    prerequisites = Column(Text, nullable=True)  # JSON string of prerequisite courses
    course_outline = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)  # For enrollment

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="courses")
    course_coordinator = relationship("User", foreign_keys=[course_coordinator_id])
    enrolled_students = relationship(
        "User", secondary="user_courses", back_populates="enrolled_courses"
    )
    assessments = relationship("Assessment", back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', code='{self.code}')>"

    @property
    def total_enrolled_students(self):
        """Get total number of enrolled students."""
        return len(self.enrolled_students) if self.enrolled_students else 0

    @property
    def total_assessments(self):
        """Get total number of assessments for this course."""
        return len(self.assessments) if self.assessments else 0

    @property
    def department_name(self):
        """Get department name."""
        return self.department.name if self.department else None

    @property
    def coordinator_name(self):
        """Get course coordinator name."""
        return self.course_coordinator.full_name if self.course_coordinator else None
