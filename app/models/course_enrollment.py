"""
Course Enrollment model for FEDPOFFA CBT Backend.

This module contains the CourseEnrollment model to track student course enrollments.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class CourseEnrollment(Base):
    """
    Course Enrollment model for FEDPOFFA CBT system.

    This model tracks student enrollments in courses with semester context.
    """

    __tablename__ = "course_enrollments"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Enrollment information
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    semester_id = Column(UUID(as_uuid=True), ForeignKey("semesters.id"), nullable=False)

    # Enrollment status
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    status = Column(
        String(20), default="enrolled"
    )  # enrolled, dropped, completed, failed

    # Academic performance
    final_grade = Column(String(5), nullable=True)  # A, B, C, D, F
    final_score = Column(Integer, nullable=True)  # Percentage score
    gpa_points = Column(Integer, nullable=True)  # GPA points earned

    # FEDPOFFA-specific fields
    attendance_percentage = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", foreign_keys=[course_id])
    semester = relationship("Semester", back_populates="course_enrollments")
    assessments = relationship("AssessmentSession", back_populates="enrollment")

    def __repr__(self):
        return f"<CourseEnrollment(id={self.id}, student_id={self.student_id}, course_id={self.course_id})>"

    @property
    def student_name(self):
        """Get student name."""
        return self.student.full_name if self.student else None

    @property
    def course_name(self):
        """Get course name."""
        return self.course.name if self.course else None

    @property
    def semester_name(self):
        """Get semester name."""
        return self.semester.name if self.semester else None

    @property
    def is_completed(self):
        """Check if enrollment is completed."""
        return self.status == "completed"

    @property
    def is_failed(self):
        """Check if enrollment failed."""
        return self.status == "failed"

    @property
    def is_dropped(self):
        """Check if enrollment was dropped."""
        return self.status == "dropped"
