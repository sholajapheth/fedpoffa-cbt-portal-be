"""
Pydantic schemas for FEDPOFFA CBT Backend.

This module contains all Pydantic models for request/response validation.
"""

from app.schemas.auth import *
from app.schemas.user import *
from app.schemas.department import *
from app.schemas.course import *
from app.schemas.semester import *
from app.schemas.common import *

__all__ = [
    # Auth schemas
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "TokenRefresh",
    "TokenData",
    "PasswordChange",
    "EmailVerification",
    "PasswordReset",
    "PasswordResetConfirm",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "UserListResponse",
    "UserStats",
    "ContactInfo",
    # Department schemas
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentResponse",
    "DepartmentDetail",
    "DepartmentListResponse",
    "DepartmentStats",
    # Course schemas
    "CourseBase",
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "CourseDetail",
    "CourseListResponse",
    "CourseEnrollmentRequest",
    "CourseEnrollmentResponse",
    "CourseStats",
    # Semester schemas
    "SemesterBase",
    "SemesterCreate",
    "SemesterUpdate",
    "SemesterResponse",
    "SemesterDetail",
    "SemesterListResponse",
    "CurrentSemesterResponse",
    "SemesterStats",
    # Common schemas
    "SuccessResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginationResponse",
]
