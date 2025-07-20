"""
Common Pydantic schemas for FEDPOFFA CBT Backend.

This module contains shared response models and error handling schemas.
"""

from datetime import datetime
from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel):
    """Base response model for FEDPOFFA CBT API."""

    success: bool = Field(default=True, description="Request success status")
    message: str = Field(description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


class ErrorResponse(BaseModel):
    """Error response model for FEDPOFFA CBT API."""

    success: bool = Field(default=False, description="Request success status")
    error: str = Field(description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Any] = Field(default=None, description="Error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    search: Optional[str] = Field(default=None, description="Search term")


class PaginatedResponse(BaseModel):
    """Paginated response model."""

    success: bool = Field(default=True, description="Request success status")
    message: str = Field(description="Response message")
    data: list[dict] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


class FEDPOFFAConstants(BaseModel):
    """FEDPOFFA-specific constants and validation."""

    # FEDPOFFA ID pattern: POF/YYYY/NNN (e.g., POF/2023/001)
    MATRIC_NUMBER_PATTERN: str = r"^\d{4}/\d{3}$"

    # Email domain validation
    FEDPOFFA_EMAIL_DOMAIN: str = "fedpoffa.edu.ng"

    # Password requirements
    MIN_PASSWORD_LENGTH: int = 8
    PASSWORD_PATTERN: str = (
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )

    # Rate limiting
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_DURATION: int = 15  # minutes

    # Token settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
