"""
User schemas for FEDPOFFA CBT Backend.

This module contains Pydantic models for user-related requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from app.core.config import FedpoffaConstants


class UserBase(BaseModel):
    """Base user schema with common fields."""

    first_name: str = Field(
        ..., min_length=2, max_length=100, description="User's first name"
    )
    last_name: str = Field(
        ..., min_length=2, max_length=100, description="User's last name"
    )
    middle_name: Optional[str] = Field(
        None, max_length=100, description="User's middle name"
    )
    email: EmailStr = Field(..., description="User's email address")
    matric_number: str = Field(..., description="Student matriculation number")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    role: str = Field(..., description="User role")
    department_id: Optional[str] = Field(None, description="User's department ID")
    level: Optional[str] = Field(
        None, description="Academic level (ND1, ND2, HND1, HND2, etc.)"
    )
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    bio: Optional[str] = Field(None, description="User biography")


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """User update schema."""

    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    department_id: Optional[str] = Field(None)
    level: Optional[str] = Field(None)
    matric_number: Optional[str] = Field(None)
    profile_picture: Optional[str] = Field(None)
    bio: Optional[str] = Field(None)


class UserResponse(UserBase):
    """User response schema."""

    id: str = Field(..., description="User ID")
    is_active: bool = Field(..., description="User active status")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: datetime = Field(..., description="Last update date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    # Computed fields
    full_name: str = Field(..., description="User's full name")
    department_name: Optional[str] = Field(None, description="Department name")

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile schema for detailed view."""

    id: str = Field(..., description="User ID")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    middle_name: Optional[str] = Field(None, description="User's middle name")
    full_name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    matric_number: str = Field(..., description="Student matriculation number")
    phone_number: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="User role")
    department_id: Optional[str] = Field(None, description="Department ID")
    department_name: Optional[str] = Field(None, description="Department name")
    level: Optional[str] = Field(None, description="Academic level")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    bio: Optional[str] = Field(None, description="User biography")
    is_active: bool = Field(..., description="User active status")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: datetime = Field(..., description="Last update date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    # Academic information
    enrolled_courses_count: int = Field(0, description="Number of enrolled courses")
    completed_assessments_count: int = Field(
        0, description="Number of completed assessments"
    )

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change request schema."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class UserListResponse(BaseModel):
    """User list response schema."""

    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class UserStats(BaseModel):
    """User statistics schema."""

    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    verified_users: int = Field(..., description="Number of verified users")
    students_count: int = Field(..., description="Number of students")
    lecturers_count: int = Field(..., description="Number of lecturers")
    admins_count: int = Field(..., description="Number of administrators")
    recent_registrations: int = Field(
        ..., description="Recent registrations (last 30 days)"
    )


class ContactInfo(BaseModel):
    """Contact information schema."""

    email: EmailStr = Field(..., description="Primary email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    alternative_email: Optional[EmailStr] = Field(
        None, description="Alternative email address"
    )
    emergency_contact: Optional[str] = Field(
        None, max_length=20, description="Emergency contact number"
    )
    address: Optional[str] = Field(None, description="Residential address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")


class UserEnrollmentResponse(BaseModel):
    """User enrollment response schema."""

    id: str = Field(..., description="Enrollment ID")
    course_id: str = Field(..., description="Course ID")
    course_name: str = Field(..., description="Course name")
    course_code: str = Field(..., description="Course code")
    semester_id: str = Field(..., description="Semester ID")
    semester_name: str = Field(..., description="Semester name")
    enrollment_date: datetime = Field(..., description="Enrollment date")
    status: str = Field(..., description="Enrollment status")
    is_active: bool = Field(..., description="Enrollment active status")
    final_grade: Optional[str] = Field(None, description="Final grade")
    final_score: Optional[float] = Field(None, description="Final score")
    gpa_points: Optional[float] = Field(None, description="GPA points")
    attendance_percentage: Optional[float] = Field(
        None, description="Attendance percentage"
    )
    remarks: Optional[str] = Field(None, description="Remarks")

    class Config:
        from_attributes = True


class UserSimpleResponse(BaseModel):
    """Simple user response schema for list endpoints."""

    id: str = Field(..., description="User ID")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    middle_name: Optional[str] = Field(None, description="User's middle name")
    full_name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    matric_number: str = Field(..., description="Student matriculation number")
    phone_number: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="User role")
    department_id: Optional[str] = Field(None, description="User's department ID")
    is_active: bool = Field(..., description="User active status")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: datetime = Field(..., description="Last update date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
