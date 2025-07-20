"""
Dependencies for FEDPOFFA CBT Backend.

This module contains FastAPI dependencies for authentication, database sessions,
and role-based access control.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import verify_access_token, extract_token_from_header
from app.models.user import User
from app.core.config import FedpoffaConstants

# HTTP Bearer scheme for token authentication
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current authenticated user.

    Args:
        credentials: JWT token from Authorization header
        db: Database session

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The active user

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current verified user.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The verified user

    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email verification required"
        )
    return current_user


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.

    Args:
        required_role: The required role for the endpoint

    Returns:
        function: Dependency function that checks user role
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """
        Check if user has the required role.

        Args:
            current_user: The current authenticated user

        Returns:
            User: The user if role check passes

        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role != required_role and current_user.role not in [
            FedpoffaConstants.ROLE_ADMIN,
            FedpoffaConstants.ROLE_IT_ADMIN,
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}",
            )
        return current_user

    return role_checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require admin role for endpoint access.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The admin user

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role not in [
        FedpoffaConstants.ROLE_ADMIN,
        FedpoffaConstants.ROLE_IT_ADMIN,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


def require_lecturer(current_user: User = Depends(get_current_user)) -> User:
    """
    Require lecturer role for endpoint access.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The lecturer user

    Raises:
        HTTPException: If user is not lecturer
    """
    if current_user.role not in [
        FedpoffaConstants.ROLE_LECTURER,
        FedpoffaConstants.ROLE_ADMIN,
        FedpoffaConstants.ROLE_IT_ADMIN,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Lecturer access required"
        )
    return current_user


def require_student(current_user: User = Depends(get_current_user)) -> User:
    """
    Require student role for endpoint access.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The student user

    Raises:
        HTTPException: If user is not student
    """
    if current_user.role not in [
        FedpoffaConstants.ROLE_STUDENT,
        FedpoffaConstants.ROLE_ADMIN,
        FedpoffaConstants.ROLE_IT_ADMIN,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Student access required"
        )
    return current_user


def require_roles(required_roles: list):
    """
    Dependency factory for multiple role-based access control.

    Args:
        required_roles: List of required roles for the endpoint

    Returns:
        function: Dependency function that checks user role
    """

    def roles_checker(current_user: User = Depends(get_current_user)) -> User:
        """
        Check if user has any of the required roles.

        Args:
            current_user: The current authenticated user

        Returns:
            User: The user if role check passes

        Raises:
            HTTPException: If user doesn't have any required role
        """
        if current_user.role not in required_roles and current_user.role not in [
            FedpoffaConstants.ROLE_ADMIN,
            FedpoffaConstants.ROLE_IT_ADMIN,
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}",
            )
        return current_user

    return roles_checker


def get_optional_user(
    request: Request, db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Optional[User]: The authenticated user or None
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None

    try:
        token = extract_token_from_header(authorization)
        payload = verify_access_token(token)

        if payload is None:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if user and user.is_active:
            return user

        return None
    except HTTPException:
        return None


def rate_limit_dependency(max_requests: int = 100, window_seconds: int = 60):
    """
    Rate limiting dependency factory.

    Args:
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds

    Returns:
        function: Rate limiting dependency function
    """
    # Simple in-memory rate limiting (in production, use Redis)
    request_counts = {}

    def rate_limiter(request: Request):
        """
        Rate limiting dependency.

        Args:
            request: FastAPI request object

        Raises:
            HTTPException: If rate limit exceeded
        """
        client_ip = request.client.host
        current_time = int(request.scope.get("time", 0))
        window_start = current_time - window_seconds

        # Clean old entries
        request_counts[client_ip] = [
            req_time
            for req_time in request_counts.get(client_ip, [])
            if req_time > window_start
        ]

        # Check rate limit
        if len(request_counts[client_ip]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        # Add current request
        request_counts[client_ip].append(current_time)

    return rate_limiter


# Predefined rate limiters
auth_rate_limiter = rate_limit_dependency(
    max_requests=50, window_seconds=300
)  # 5 requests per 5 minutes
general_rate_limiter = rate_limit_dependency(
    max_requests=100, window_seconds=60
)  # 100 requests per minute
