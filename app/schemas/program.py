"""
Program schemas for FEDPOFFA CBT Backend.

This module contains Pydantic models for program-related requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProgramBase(BaseModel):
    """Base program schema with common fields."""

    name: str = Field(..., min_length=2, max_length=255, description="Program name")
    code: str = Field(..., min_length=2, max_length=20, description="Program code")
    description: Optional[str] = Field(None, description="Program description")
    department_id: str = Field(..., description="Department ID")
    duration_years: int = Field(2, ge=1, le=4, description="Program duration in years")
    level: str = Field(..., description="Academic level (ND, HND, etc.)")
    total_credits: int = Field(0, ge=0, description="Total credits required")
    program_coordinator_id: Optional[str] = Field(
        None, description="Program coordinator ID"
    )
    admission_requirements: Optional[str] = Field(
        None, description="Admission requirements"
    )
    program_outline: Optional[str] = Field(None, description="Program outline")
    career_prospects: Optional[str] = Field(None, description="Career prospects")


class ProgramCreate(ProgramBase):
    """Program creation schema."""

    pass


class ProgramUpdate(BaseModel):
    """Program update schema."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    description: Optional[str] = Field(None)
    department_id: Optional[str] = Field(None)
    duration_years: Optional[int] = Field(None, ge=1, le=4)
    level: Optional[str] = Field(None)
    total_credits: Optional[int] = Field(None, ge=0)
    program_coordinator_id: Optional[str] = Field(None)
    admission_requirements: Optional[str] = Field(None)
    program_outline: Optional[str] = Field(None)
    career_prospects: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    is_accepting_enrollments: Optional[bool] = Field(None)


class ProgramResponse(ProgramBase):
    """Program response schema."""

    id: str = Field(..., description="Program ID")
    is_active: bool = Field(..., description="Program active status")
    is_accepting_enrollments: bool = Field(
        ..., description="Program enrollment availability"
    )
    created_at: datetime = Field(..., description="Program creation date")
    updated_at: datetime = Field(..., description="Last update date")

    # Computed fields
    department_name: Optional[str] = Field(None, description="Department name")
    coordinator_name: Optional[str] = Field(
        None, description="Program coordinator name"
    )
    total_enrolled_students: int = Field(0, description="Number of enrolled students")
    total_courses: int = Field(0, description="Number of courses")

    class Config:
        from_attributes = True


class ProgramDetail(ProgramResponse):
    """Program detail schema with additional information."""

    # Additional fields for detailed view
    enrolled_students: List[dict] = Field(
        default_factory=list, description="List of enrolled students"
    )
    courses: List[dict] = Field(default_factory=list, description="List of courses")


class ProgramListResponse(BaseModel):
    """Program list response schema."""

    programs: List[ProgramResponse] = Field(..., description="List of programs")
    total: int = Field(..., description="Total number of programs")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class ProgramEnrollmentRequest(BaseModel):
    """Program enrollment request schema."""

    user_id: str = Field(..., description="User ID to enroll")
    admission_number: Optional[str] = Field(None, description="Admission number")


class ProgramEnrollmentResponse(BaseModel):
    """Program enrollment response schema."""

    id: str = Field(..., description="Enrollment ID")
    user_id: str = Field(..., description="User ID")
    program_id: str = Field(..., description="Program ID")
    enrollment_date: datetime = Field(..., description="Enrollment date")
    status: str = Field(..., description="Enrollment status")
    is_active: bool = Field(..., description="Enrollment active status")
    current_level: Optional[str] = Field(None, description="Current academic level")
    current_semester: Optional[str] = Field(None, description="Current semester")
    gpa: Optional[int] = Field(None, description="Current GPA")
    total_credits_earned: int = Field(0, description="Total credits earned")

    # Computed fields
    student_name: Optional[str] = Field(None, description="Student name")
    program_name: Optional[str] = Field(None, description="Program name")

    class Config:
        from_attributes = True


class ProgramStats(BaseModel):
    """Program statistics schema."""

    total_programs: int = Field(..., description="Total number of programs")
    active_programs: int = Field(..., description="Number of active programs")
    accepting_enrollments: int = Field(
        ..., description="Number of programs accepting enrollments"
    )
    total_enrollments: int = Field(..., description="Total number of enrollments")
    total_courses: int = Field(..., description="Total number of courses")
