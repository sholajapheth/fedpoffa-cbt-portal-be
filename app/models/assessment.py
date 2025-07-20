"""
Assessment model for FEDPOFFA CBT Backend.

This module contains the Assessment model with FEDPOFFA-specific fields and relationships.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Assessment(Base):
    """
    Assessment model for FEDPOFFA CBT system.

    This model represents assessments (tests, assignments, exams) with semester context.
    """

    __tablename__ = "assessments"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Assessment information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # test, assignment, exam, quiz

    # Course and semester relationships
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    semester_id = Column(UUID(as_uuid=True), ForeignKey("semesters.id"), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Assessment configuration
    duration = Column(Integer, default=60)  # minutes
    max_attempts = Column(Integer, default=1)
    total_points = Column(Integer, default=100)
    passing_score = Column(Integer, default=50)  # percentage

    # Scheduling
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)

    # FEDPOFFA-specific fields
    is_proctored = Column(Boolean, default=False)
    allow_calculator = Column(Boolean, default=False)
    allow_notes = Column(Boolean, default=False)
    instructions = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="assessments")
    semester = relationship("Semester", back_populates="assessments")
    creator = relationship("User", foreign_keys=[creator_id])
    questions = relationship("Question", back_populates="assessment")
    sessions = relationship("AssessmentSession", back_populates="assessment")

    def __repr__(self):
        return f"<Assessment(id={self.id}, title='{self.title}', type='{self.type}')>"

    @property
    def course_name(self):
        """Get course name."""
        return self.course.name if self.course else None

    @property
    def semester_name(self):
        """Get semester name."""
        return self.semester.name if self.semester else None

    @property
    def creator_name(self):
        """Get creator name."""
        return self.creator.full_name if self.creator else None

    @property
    def total_questions(self):
        """Get total number of questions."""
        return len(self.questions) if self.questions else 0

    @property
    def total_sessions(self):
        """Get total number of assessment sessions."""
        return len(self.sessions) if self.sessions else 0

    @property
    def is_available(self):
        """Check if assessment is currently available."""
        now = datetime.utcnow()
        return (
            self.is_active
            and self.is_published
            and (not self.start_time or self.start_time <= now)
            and (not self.end_time or now <= self.end_time)
        )

    @property
    def is_overdue(self):
        """Check if assessment is overdue."""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date
