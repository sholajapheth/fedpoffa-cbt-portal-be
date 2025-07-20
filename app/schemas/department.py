"""
Department schemas for FEDPOFFA CBT Backend.

This module contains Pydantic models for department-related requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DepartmentBase(BaseModel):
    """Base department schema with common fields."""

    name: str = Field(..., min_length=2, max_length=255, description="Department name")
    code: str = Field(..., min_length=2, max_length=10, description="Department code")
    description: Optional[str] = Field(None, description="Department description")
    hod_name: Optional[str] = Field(
        None, max_length=255, description="Head of Department name"
    )
    hod_email: Optional[str] = Field(None, description="Head of Department email")
    hod_phone: Optional[str] = Field(
        None, max_length=20, description="Head of Department phone"
    )


class DepartmentCreate(DepartmentBase):
    """Department creation schema."""

    pass


class DepartmentUpdate(BaseModel):
    """Department update schema."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = Field(None, min_length=2, max_length=10)
    description: Optional[str] = Field(None)
    hod_name: Optional[str] = Field(None, max_length=255)
    hod_email: Optional[str] = Field(None)
    hod_phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = Field(None)


class DepartmentResponse(DepartmentBase):
    """Department response schema."""

    id: str = Field(..., description="Department ID")
    is_active: bool = Field(..., description="Department active status")
    created_at: datetime = Field(..., description="Department creation date")
    updated_at: datetime = Field(..., description="Last update date")

    # Computed fields
    total_users: int = Field(0, description="Total number of users")
    total_courses: int = Field(0, description="Total number of courses")
    students_count: int = Field(0, description="Number of students")
    lecturers_count: int = Field(0, description="Number of lecturers")

    class Config:
        from_attributes = True


class DepartmentDetail(DepartmentResponse):
    """Department detail schema with additional information."""

    # Additional fields for detailed view
    courses: List[dict] = Field(default_factory=list, description="List of courses")
    users: List[dict] = Field(default_factory=list, description="List of users")


class DepartmentListResponse(BaseModel):
    """Department list response schema."""

    departments: List[DepartmentResponse] = Field(
        ..., description="List of departments"
    )
    total: int = Field(..., description="Total number of departments")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class DepartmentStats(BaseModel):
    """Department statistics schema."""

    total_departments: int = Field(..., description="Total number of departments")
    active_departments: int = Field(..., description="Number of active departments")
    total_courses: int = Field(
        ..., description="Total number of courses across all departments"
    )
    total_students: int = Field(
        ..., description="Total number of students across all departments"
    )
    total_lecturers: int = Field(
        ..., description="Total number of lecturers across all departments"
    )
