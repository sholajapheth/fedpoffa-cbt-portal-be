"""
Department model for FEDPOFFA CBT Backend.

This module contains the Department model with FEDPOFFA-specific fields and relationships.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Department(Base):
    """
    Department model for FEDPOFFA CBT system.

    This model represents FEDPOFFA departments with their associated courses and users.
    """

    __tablename__ = "departments"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Department information
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(10), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # FEDPOFFA-specific fields
    hod_name = Column(String(255), nullable=True)  # Head of Department
    hod_email = Column(String(255), nullable=True)
    hod_phone = Column(String(20), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="department")
    courses = relationship("Course", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', code='{self.code}')>"

    @property
    def total_users(self):
        """Get total number of users in this department."""
        return len(self.users) if self.users else 0

    @property
    def total_courses(self):
        """Get total number of courses in this department."""
        return len(self.courses) if self.courses else 0

    @property
    def students_count(self):
        """Get number of students in this department."""
        return (
            len([user for user in self.users if user.is_student]) if self.users else 0
        )

    @property
    def lecturers_count(self):
        """Get number of lecturers in this department."""
        return (
            len([user for user in self.users if user.is_lecturer]) if self.users else 0
        )
