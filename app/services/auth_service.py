"""
Authentication service for FEDPOFFA CBT Backend.

This module contains business logic for user authentication and authorization.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_token_pair,
    validate_password_strength,
    generate_verification_token,
)
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.core.config import FedpoffaConstants


class AuthService:
    """Authentication service for FEDPOFFA CBT system."""

    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserRegister) -> Tuple[User, dict]:
        """
        Register a new FEDPOFFA user.

        Args:
            user_data: User registration data

        Returns:
            Tuple[User, dict]: Created user and response data

        Raises:
            HTTPException: If registration fails
        """
        # Validate matric number format
        if not self._validate_matric_number(user_data.matric_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid matric number format",
            )

        # Validate email domain
        if not self._validate_fedpoffa_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email must be from FEDPOFFA domain (@fedpoffa.edu.ng)",
            )

        # Validate password strength
        if not validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character",
            )

        # Check if user already exists
        if self._user_exists_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        if self._user_exists_by_matric_number(user_data.matric_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this matric number already exists",
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        verification_token = generate_verification_token()

        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            middle_name=user_data.middle_name,
            email=user_data.email,
            matric_number=user_data.matric_number,
            password_hash=hashed_password,
            role=user_data.role,
            department_id=user_data.department_id,
            phone_number=user_data.phone_number,
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # TODO: Send verification email
        # self._send_verification_email(user, verification_token)

        response_data = {
            "message": "Registration successful. Please check your email for verification.",
            "user_id": str(user.id),
            "requires_verification": True,
        }

        return user, response_data

    def authenticate_user(self, login_data: UserLogin) -> TokenResponse:
        """
        Authenticate a FEDPOFFA user.

        Args:
            login_data: User login data

        Returns:
            TokenResponse: JWT tokens and user data

        Raises:
            HTTPException: If authentication fails
        """
        # Find user by email or FEDPOFFA ID
        user = self._get_user_by_identifier(login_data.identifier)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive"
            )

        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()

        # Create token data
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "matric_number": user.matric_number,
            "role": user.role,
            "department_id": str(user.department_id) if user.department_id else None,
        }

        # Generate tokens
        tokens = create_token_pair(token_data)

        # Prepare user data for response
        user_data = {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "matric_number": user.matric_number,
            "role": user.role,
            "department_id": str(user.department_id) if user.department_id else None,
            "is_verified": user.is_verified,
        }

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=user_data,
        )

    def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            dict: New access token data

        Raises:
            HTTPException: If refresh fails
        """
        from app.core.security import verify_refresh_token, create_access_token

        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Get user from database
        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new access token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "matric_number": user.matric_number,
            "role": user.role,
            "department_id": str(user.department_id) if user.department_id else None,
        }

        new_access_token = create_access_token(token_data)

        return {"access_token": new_access_token, "expires_in": 1800}  # 30 minutes

    def verify_email(self, token: str) -> dict:
        """
        Verify user email with verification token.

        Args:
            token: Email verification token

        Returns:
            dict: Verification result

        Raises:
            HTTPException: If verification fails
        """
        # TODO: Implement email verification logic
        # For now, just return success
        return {"message": "Email verified successfully", "verified": True}

    def _validate_matric_number(self, matric_number: str) -> bool:
        """Validate matric number format."""
        return len(matric_number) >= 5

    def _validate_fedpoffa_email(self, email: str) -> bool:
        """Validate FEDPOFFA email domain."""
        return email.endswith("@fedpoffa.edu.ng")

    def _user_exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return self.db.query(User).filter(User.email == email).first() is not None

    def _user_exists_by_matric_number(self, matric_number: str) -> bool:
        """Check if user exists by matric number."""
        return (
            self.db.query(User).filter(User.matric_number == matric_number).first()
            is not None
        )

    def _get_user_by_identifier(self, identifier: str) -> Optional[User]:
        """Get user by email or matric number."""
        if "@" in identifier:
            # Search by email
            return self.db.query(User).filter(User.email == identifier).first()
        else:
            # Search by matric number
            return self.db.query(User).filter(User.matric_number == identifier).first()

    def _send_verification_email(self, user: User, token: str):
        """Send verification email to user."""
        # TODO: Implement email sending logic
        pass
