"""
User-Program association model for FEDPOFFA CBT Backend.

This module contains the UserProgram model to track student program enrollments.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserProgram(Base):
    """
    User-Program association model for FEDPOFFA CBT system.

    This model tracks student enrollments in programs.
    """

    __tablename__ = "user_programs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Enrollment information
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)

    # Enrollment status
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    status = Column(
        String(20), default="enrolled"
    )  # enrolled, graduated, dropped, suspended

    # Academic progress
    current_level = Column(String(20), nullable=True)  # ND1, ND2, HND1, HND2
    current_semester = Column(String(20), nullable=True)  # First, Second
    gpa = Column(Integer, nullable=True)  # Current GPA
    total_credits_earned = Column(Integer, default=0)

    # FEDPOFFA-specific fields
    admission_number = Column(String(50), nullable=True)
    graduation_date = Column(DateTime, nullable=True)
    remarks = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship(
        "User", foreign_keys=[user_id], overlaps="enrolled_programs,enrolled_students"
    )
    program = relationship(
        "Program",
        foreign_keys=[program_id],
        overlaps="enrolled_programs,enrolled_students",
    )

    def __repr__(self):
        return f"<UserProgram(id={self.id}, user_id={self.user_id}, program_id={self.program_id})>"

    @property
    def student_name(self):
        """Get student name."""
        return self.user.full_name if self.user else None

    @property
    def program_name(self):
        """Get program name."""
        return self.program.name if self.program else None

    @property
    def is_graduated(self):
        """Check if student has graduated."""
        return self.status == "graduated"

    @property
    def is_dropped(self):
        """Check if enrollment was dropped."""
        return self.status == "dropped"

    @property
    def is_suspended(self):
        """Check if enrollment is suspended."""
        return self.status == "suspended"
