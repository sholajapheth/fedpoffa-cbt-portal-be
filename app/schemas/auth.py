"""
Authentication schemas for FEDPOFFA CBT Backend.

This module contains Pydantic models for authentication-related requests and responses.
"""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator

from app.core.config import FedpoffaConstants


class UserRegister(BaseModel):
    """User registration schema for FEDPOFFA CBT system."""

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
    matric_number: str = Field(..., description="Student matric number")
    password: str = Field(..., min_length=8, description="User password")
    role: str = Field(..., description="User role")
    department_id: str = Field(..., description="User's department ID")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")

    @validator("matric_number")
    def validate_matric_number(cls, v):
        """Validate matric number format."""
        # Basic validation for matric number format
        if not v or len(v) < 5:
            raise ValueError("Matric number must be at least 5 characters long")
        return v

    @validator("email")
    def validate_fedpoffa_email(cls, v):
        """Validate FEDPOFFA email domain."""
        if not v.endswith("@fedpoffa.edu.ng"):
            raise ValueError("Email must be from FEDPOFFA domain (@fedpoffa.edu.ng)")
        return v

    @validator("password")
    def validate_password_strength(cls, v):
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError(
                "Password must contain at least one special character (@$!%*?&)"
            )
        return v

    @validator("role")
    def validate_role(cls, v):
        """Validate user role."""
        valid_roles = [
            FedpoffaConstants.ROLE_STUDENT,
            FedpoffaConstants.ROLE_LECTURER,
            FedpoffaConstants.ROLE_ADMIN,
            FedpoffaConstants.ROLE_IT_ADMIN,
        ]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v


class UserLogin(BaseModel):
    """User login schema for FEDPOFFA CBT system."""

    identifier: str = Field(..., description="Email or FEDPOFFA ID")
    password: str = Field(..., description="User password")

    @validator("identifier")
    def validate_identifier(cls, v):
        """Validate identifier format."""
        if "@" in v:
            # Email format
            if not v.endswith("@fedpoffa.edu.ng"):
                raise ValueError("Email must be from FEDPOFFA domain")
        else:
            # Matric number format
            if not v or len(v) < 5:
                raise ValueError("Matric number must be at least 5 characters long")
        return v


class TokenResponse(BaseModel):
    """JWT token response schema."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    user: dict = Field(..., description="User profile data")


class TokenRefresh(BaseModel):
    """Token refresh request schema."""

    refresh_token: str = Field(..., description="JWT refresh token")


class TokenData(BaseModel):
    """JWT token payload data."""

    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    matric_number: str = Field(..., description="Matric number")
    role: str = Field(..., description="User role")
    department: str = Field(..., description="User department")
    exp: datetime = Field(..., description="Token expiration")


class PasswordChange(BaseModel):
    """Password change request schema."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")

    @validator("new_password")
    def validate_new_password_strength(cls, v):
        """Validate new password strength requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError(
                "Password must contain at least one special character (@$!%*?&)"
            )
        return v


class EmailVerification(BaseModel):
    """Email verification request schema."""

    token: str = Field(..., description="Email verification token")


class PasswordReset(BaseModel):
    """Password reset request schema."""

    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., description="New password")

    @validator("new_password")
    def validate_new_password_strength(cls, v):
        """Validate new password strength requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError(
                "Password must contain at least one special character (@$!%*?&)"
            )
        return v
