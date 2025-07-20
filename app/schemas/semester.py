"""
Semester schemas for FEDPOFFA CBT Backend.

This module contains Pydantic models for semester-related requests and responses.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class SemesterBase(BaseModel):
    """Base semester schema with common fields."""

    name: str = Field(..., min_length=2, max_length=100, description="Semester name")
    academic_year: str = Field(
        ..., min_length=4, max_length=20, description="Academic year"
    )
    semester_type: str = Field(..., description="Semester type (first, second, summer)")
    start_date: date = Field(..., description="Semester start date")
    end_date: date = Field(..., description="Semester end date")
    registration_start: Optional[date] = Field(
        None, description="Registration start date"
    )
    registration_end: Optional[date] = Field(None, description="Registration end date")
    exam_start: Optional[date] = Field(None, description="Exam period start date")
    exam_end: Optional[date] = Field(None, description="Exam period end date")
    description: Optional[str] = Field(None, description="Semester description")


class SemesterCreate(SemesterBase):
    """Semester creation schema."""

    pass


class SemesterUpdate(BaseModel):
    """Semester update schema."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    academic_year: Optional[str] = Field(None, min_length=4, max_length=20)
    semester_type: Optional[str] = Field(None)
    start_date: Optional[date] = Field(None)
    end_date: Optional[date] = Field(None)
    registration_start: Optional[date] = Field(None)
    registration_end: Optional[date] = Field(None)
    exam_start: Optional[date] = Field(None)
    exam_end: Optional[date] = Field(None)
    description: Optional[str] = Field(None)
    is_current: Optional[bool] = Field(None)
    is_active: Optional[bool] = Field(None)


class SemesterResponse(SemesterBase):
    """Semester response schema."""

    id: str = Field(..., description="Semester ID")
    is_current: bool = Field(..., description="Current semester status")
    is_active: bool = Field(..., description="Semester active status")
    created_at: datetime = Field(..., description="Semester creation date")
    updated_at: datetime = Field(..., description="Last update date")

    # Computed fields
    is_registration_open: bool = Field(False, description="Registration open status")
    is_exam_period: bool = Field(False, description="Exam period status")
    is_active_period: bool = Field(False, description="Active period status")
    total_assessments: int = Field(0, description="Number of assessments")
    total_enrollments: int = Field(0, description="Number of enrollments")

    class Config:
        from_attributes = True


class SemesterDetail(SemesterResponse):
    """Semester detail schema with additional information."""

    # Additional fields for detailed view
    assessments: List[dict] = Field(
        default_factory=list, description="List of assessments"
    )
    enrollments: List[dict] = Field(
        default_factory=list, description="List of enrollments"
    )


class SemesterListResponse(BaseModel):
    """Semester list response schema."""

    semesters: List[SemesterResponse] = Field(..., description="List of semesters")
    total: int = Field(..., description="Total number of semesters")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class CurrentSemesterResponse(BaseModel):
    """Current semester response schema."""

    semester: Optional[SemesterResponse] = Field(None, description="Current semester")
    registration_status: str = Field(..., description="Registration status")
    exam_status: str = Field(..., description="Exam period status")
    academic_calendar: dict = Field(
        default_factory=dict, description="Academic calendar"
    )


class SemesterStats(BaseModel):
    """Semester statistics schema."""

    total_semesters: int = Field(..., description="Total number of semesters")
    active_semesters: int = Field(..., description="Number of active semesters")
    current_semester: Optional[str] = Field(None, description="Current semester name")
    total_assessments: int = Field(
        ..., description="Total number of assessments across all semesters"
    )
    total_enrollments: int = Field(
        ..., description="Total number of enrollments across all semesters"
    )
