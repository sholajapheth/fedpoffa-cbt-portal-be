"""
Student Response model for FEDPOFFA CBT Backend.

This module contains the StudentResponse model to track student answers.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class StudentResponse(Base):
    """
    Student Response model for FEDPOFFA CBT system.

    This model tracks student answers to questions in assessment sessions.
    """

    __tablename__ = "student_responses"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Response information
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("assessment_sessions.id"), nullable=False
    )
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    student_answer = Column(Text, nullable=True)  # Student's answer
    selected_options = Column(
        Text, nullable=True
    )  # JSON string for multiple choice selections

    # Grading information
    is_correct = Column(Boolean, nullable=True)  # NULL if not graded yet
    points_earned = Column(Integer, default=0)
    feedback = Column(Text, nullable=True)  # Feedback from lecturer

    # FEDPOFFA-specific fields
    time_spent = Column(Integer, nullable=True)  # seconds spent on this question
    attempts = Column(Integer, default=1)  # number of attempts for this question

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("AssessmentSession", back_populates="responses")
    question = relationship("Question", back_populates="responses")

    def __repr__(self):
        return f"<StudentResponse(id={self.id}, session_id={self.session_id}, question_id={self.question_id})>"

    @property
    def is_graded(self):
        """Check if response has been graded."""
        return self.is_correct is not None

    @property
    def is_answered(self):
        """Check if question was answered."""
        return self.student_answer is not None or self.selected_options is not None

    @property
    def time_spent_minutes(self):
        """Get time spent in minutes."""
        if self.time_spent:
            return self.time_spent / 60
        return 0
