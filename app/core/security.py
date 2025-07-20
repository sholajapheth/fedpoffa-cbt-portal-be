"""
Security utilities for FEDPOFFA CBT Backend.

This module contains JWT token management, password hashing, and authentication utilities.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        str: The JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),  # JWT ID for token tracking
            "type": "access",
        }
    )

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        str: The JWT refresh token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),  # JWT ID for token tracking
            "type": "refresh",
        }
    )

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token to verify

    Returns:
        dict: The decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[dict]:
    """
    Verify and decode an access token specifically.

    Args:
        token: The JWT access token to verify

    Returns:
        dict: The decoded token payload or None if invalid
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def verify_refresh_token(token: str) -> Optional[dict]:
    """
    Verify and decode a refresh token specifically.

    Args:
        token: The JWT refresh token to verify

    Returns:
        dict: The decoded token payload or None if invalid
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration time of a JWT token.

    Args:
        token: The JWT token

    Returns:
        datetime: The expiration time or None if invalid
    """
    payload = verify_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None


def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired.

    Args:
        token: The JWT token

    Returns:
        bool: True if expired, False otherwise
    """
    exp_time = get_token_expiration(token)
    if exp_time:
        return datetime.utcnow() > exp_time
    return True


def create_token_pair(user_data: dict) -> dict:
    """
    Create both access and refresh tokens for a user.

    Args:
        user_data: User data to include in tokens

    Returns:
        dict: Dictionary containing access_token and refresh_token
    """
    access_token = create_access_token(data=user_data)
    refresh_token = create_refresh_token(data=user_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
    }


def extract_token_from_header(authorization: str) -> str:
    """
    Extract token from Authorization header.

    Args:
        authorization: The Authorization header value

    Returns:
        str: The extracted token

    Raises:
        HTTPException: If token format is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return parts[1]


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength according to FEDPOFFA requirements.

    Args:
        password: The password to validate

    Returns:
        bool: True if password meets requirements
    """
    import re

    # Minimum length
    if len(password) < 8:
        return False

    # Must contain at least one lowercase letter
    if not re.search(r"[a-z]", password):
        return False

    # Must contain at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        return False

    # Must contain at least one digit
    if not re.search(r"\d", password):
        return False

    # Must contain at least one special character
    if not re.search(r"[@$!%*?&]", password):
        return False

    return True


def generate_verification_token() -> str:
    """
    Generate a secure verification token for email verification.

    Returns:
        str: A secure random token
    """
    return str(uuid.uuid4())


def generate_password_reset_token() -> str:
    """
    Generate a secure password reset token.

    Returns:
        str: A secure random token
    """
    return str(uuid.uuid4())
