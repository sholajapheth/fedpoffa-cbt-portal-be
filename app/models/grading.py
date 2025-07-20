"""
Grading session model for FEDPOFFA CBT Backend.

This module contains the GradingSession model with FEDPOFFA-specific fields.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class GradingSession(Base):
    """
    GradingSession model for FEDPOFFA CBT system.

    This model represents grading sessions for assessments.
    """

    __tablename__ = "gradings"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Grading information
    assessment_id = Column(
        UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False
    )
    lecturer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Grading status and scores
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    total_score = Column(Integer, nullable=True)
    max_score = Column(Integer, nullable=True)
    percentage = Column(Integer, nullable=True)  # Percentage score
    grade = Column(String(5), nullable=True)  # A, B, C, D, F

    # FEDPOFFA-specific fields
    comments = Column(Text, nullable=True)  # Lecturer comments
    feedback = Column(Text, nullable=True)  # Detailed feedback
    is_passed = Column(Boolean, nullable=True)  # Pass/fail status

    # Timestamps
    graded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessment = relationship("Assessment", foreign_keys=[assessment_id])
    lecturer = relationship("User", foreign_keys=[lecturer_id])
    student = relationship("User", foreign_keys=[student_id])

    def __repr__(self):
        return f"<GradingSession(id={self.id}, assessment_id={self.assessment_id}, student_id={self.student_id})>"

    @property
    def is_completed(self):
        """Check if grading is completed."""
        return self.status == "completed"

    @property
    def is_pending(self):
        """Check if grading is pending."""
        return self.status == "pending"

    @property
    def is_in_progress(self):
        """Check if grading is in progress."""
        return self.status == "in_progress"

    @property
    def score_percentage(self):
        """Calculate score percentage."""
        if self.total_score is not None and self.max_score and self.max_score > 0:
            return (self.total_score / self.max_score) * 100
        return self.percentage
