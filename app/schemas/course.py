"""
Course schemas for FEDPOFFA CBT Backend.

This module contains Pydantic models for course-related requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    """Base course schema with common fields."""

    name: str = Field(..., min_length=2, max_length=255, description="Course name")
    code: str = Field(..., min_length=2, max_length=20, description="Course code")
    description: Optional[str] = Field(None, description="Course description")
    department_id: str = Field(..., description="Department ID")
    credits: int = Field(0, description="Course credits")
    level: Optional[str] = Field(
        None, description="Academic level (ND1, ND2, HND1, HND2, etc.)"
    )
    semester: Optional[str] = Field(
        None, description="Semester (First, Second, Summer)"
    )
    course_coordinator_id: Optional[str] = Field(
        None, description="Course coordinator ID"
    )
    prerequisites: Optional[str] = Field(None, description="Prerequisite courses")
    course_outline: Optional[str] = Field(None, description="Course outline")


class CourseCreate(CourseBase):
    """Course creation schema."""

    pass


class CourseUpdate(BaseModel):
    """Course update schema."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    description: Optional[str] = Field(None)
    department_id: Optional[str] = Field(None)
    credits: Optional[int] = Field(None)
    level: Optional[str] = Field(None)
    semester: Optional[str] = Field(None)
    course_coordinator_id: Optional[str] = Field(None)
    prerequisites: Optional[str] = Field(None)
    course_outline: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    is_available: Optional[bool] = Field(None)


class CourseResponse(CourseBase):
    """Course response schema."""

    id: str = Field(..., description="Course ID")
    is_active: bool = Field(..., description="Course active status")
    is_available: bool = Field(..., description="Course availability for enrollment")
    created_at: datetime = Field(..., description="Course creation date")
    updated_at: datetime = Field(..., description="Last update date")

    # Computed fields
    department_name: Optional[str] = Field(None, description="Department name")
    coordinator_name: Optional[str] = Field(None, description="Course coordinator name")
    total_enrolled_students: int = Field(0, description="Number of enrolled students")
    total_assessments: int = Field(0, description="Number of assessments")

    class Config:
        from_attributes = True


class CourseDetail(CourseResponse):
    """Course detail schema with additional information."""

    # Additional fields for detailed view
    enrolled_students: List[dict] = Field(
        default_factory=list, description="List of enrolled students"
    )
    assessments: List[dict] = Field(
        default_factory=list, description="List of assessments"
    )


class CourseListResponse(BaseModel):
    """Course list response schema."""

    courses: List[CourseResponse] = Field(..., description="List of courses")
    total: int = Field(..., description="Total number of courses")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class CourseEnrollmentRequest(BaseModel):
    """Course enrollment request schema."""

    course_id: str = Field(..., description="Course ID to enroll in")
    semester_id: str = Field(..., description="Semester ID")


class CourseEnrollmentResponse(BaseModel):
    """Course enrollment response schema."""

    id: str = Field(..., description="Enrollment ID")
    student_id: str = Field(..., description="Student ID")
    course_id: str = Field(..., description="Course ID")
    semester_id: str = Field(..., description="Semester ID")
    enrollment_date: datetime = Field(..., description="Enrollment date")
    status: str = Field(..., description="Enrollment status")
    is_active: bool = Field(..., description="Enrollment active status")

    # Computed fields
    student_name: Optional[str] = Field(None, description="Student name")
    course_name: Optional[str] = Field(None, description="Course name")
    semester_name: Optional[str] = Field(None, description="Semester name")

    class Config:
        from_attributes = True


class CourseStats(BaseModel):
    """Course statistics schema."""

    total_courses: int = Field(..., description="Total number of courses")
    active_courses: int = Field(..., description="Number of active courses")
    available_courses: int = Field(..., description="Number of available courses")
    total_enrollments: int = Field(..., description="Total number of enrollments")
    total_assessments: int = Field(..., description="Total number of assessments")
