"""
Question model for FEDPOFFA CBT Backend.

This module contains the Question model with FEDPOFFA-specific fields.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Question(Base):
    """
    Question model for FEDPOFFA CBT system.

    This model represents questions in the FEDPOFFA system.
    """

    __tablename__ = "questions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Question information
    type = Column(
        String(50), nullable=False
    )  # multiple_choice, true_false, short_answer, essay
    content = Column(Text, nullable=False)
    options = Column(Text, nullable=True)  # JSON string for multiple choice options
    correct_answer = Column(Text, nullable=True)
    points = Column(Integer, default=1)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard

    # Assessment relationship
    assessment_id = Column(
        UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False
    )

    # FEDPOFFA-specific fields
    explanation = Column(Text, nullable=True)  # Explanation for the correct answer
    tags = Column(Text, nullable=True)  # JSON string of tags for categorization

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    responses = relationship("StudentResponse", back_populates="question")

    def __repr__(self):
        return f"<Question(id={self.id}, type='{self.type}', content='{self.content[:50]}...')>"

    @property
    def question_type(self):
        """Get question type."""
        return self.type

    @property
    def is_multiple_choice(self):
        """Check if question is multiple choice."""
        return self.type == "multiple_choice"

    @property
    def is_true_false(self):
        """Check if question is true/false."""
        return self.type == "true_false"

    @property
    def is_short_answer(self):
        """Check if question is short answer."""
        return self.type == "short_answer"

    @property
    def is_essay(self):
        """Check if question is essay."""
        return self.type == "essay"
