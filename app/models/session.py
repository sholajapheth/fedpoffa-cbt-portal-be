"""
Assessment Session model for FEDPOFFA CBT Backend.

This module contains the AssessmentSession model with FEDPOFFA-specific fields and relationships.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class AssessmentSession(Base):
    """
    Assessment Session model for FEDPOFFA CBT system.

    This model represents student assessment sessions with enrollment context.
    """

    __tablename__ = "assessment_sessions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Session information
    assessment_id = Column(
        UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False
    )
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    enrollment_id = Column(
        UUID(as_uuid=True), ForeignKey("course_enrollments.id"), nullable=True
    )

    # Session tracking
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(
        String(20), default="in_progress"
    )  # in_progress, completed, abandoned, timed_out

    # Performance tracking
    score = Column(Integer, nullable=True)  # Raw score
    percentage = Column(Integer, nullable=True)  # Percentage score
    grade = Column(String(5), nullable=True)  # A, B, C, D, F
    is_passed = Column(Boolean, nullable=True)

    # Session details
    attempt_number = Column(Integer, default=1)
    time_spent = Column(Integer, nullable=True)  # minutes
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # FEDPOFFA-specific fields
    is_proctored = Column(Boolean, default=False)
    proctor_notes = Column(Text, nullable=True)
    cheating_suspected = Column(Boolean, default=False)
    cheating_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessment = relationship("Assessment", back_populates="sessions")
    student = relationship("User", foreign_keys=[student_id])
    enrollment = relationship("CourseEnrollment", back_populates="assessments")
    responses = relationship("StudentResponse", back_populates="session")

    def __repr__(self):
        return f"<AssessmentSession(id={self.id}, assessment_id={self.assessment_id}, student_id={self.student_id})>"

    @property
    def student_name(self):
        """Get student name."""
        return self.student.full_name if self.student else None

    @property
    def assessment_title(self):
        """Get assessment title."""
        return self.assessment.title if self.assessment else None

    @property
    def course_name(self):
        """Get course name."""
        return self.assessment.course_name if self.assessment else None

    @property
    def is_completed(self):
        """Check if session is completed."""
        return self.status == "completed"

    @property
    def is_abandoned(self):
        """Check if session was abandoned."""
        return self.status == "abandoned"

    @property
    def is_timed_out(self):
        """Check if session timed out."""
        return self.status == "timed_out"

    @property
    def duration_minutes(self):
        """Calculate session duration in minutes."""
        if not self.start_time:
            return 0
        end_time = self.end_time or datetime.utcnow()
        duration = end_time - self.start_time
        return int(duration.total_seconds() / 60)

    @property
    def time_remaining(self):
        """Calculate time remaining for the session."""
        if not self.assessment or not self.start_time:
            return 0

        total_duration = self.assessment.duration
        elapsed = self.duration_minutes
        remaining = total_duration - elapsed

        return max(0, remaining)
