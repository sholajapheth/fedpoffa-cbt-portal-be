"""
Authentication router for FEDPOFFA CBT Backend.

This module handles user authentication including login, logout, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.dependencies import auth_rate_limiter, get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
)
from app.schemas.common import ResponseModel
from app.models.user import User

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=ResponseModel)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
    rate_limit: None = Depends(auth_rate_limiter),
):
    """
    Register a new FEDPOFFA user.

    This endpoint handles registration for students, lecturers, and administrators.
    """
    try:
        auth_service = AuthService(db)
        user, response_data = auth_service.register_user(user_data)

        return ResponseModel(
            success=True,
            message=response_data["message"],
            data={
                "user_id": response_data["user_id"],
                "requires_verification": response_data["requires_verification"],
            },
        )
    except HTTPException as e:
        return ResponseModel(success=False, message=e.detail, data=None)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
    rate_limit: None = Depends(auth_rate_limiter),
):
    """
    Authenticate FEDPOFFA user and return access token.

    This endpoint handles login for students, lecturers, and administrators.
    """
    try:
        auth_service = AuthService(db)
        return auth_service.authenticate_user(login_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.post("/logout", response_model=ResponseModel)
async def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Logout FEDPOFFA user and invalidate token.
    """
    try:
        auth_service = AuthService(db)
        auth_service.logout_user(current_user.id)

        return ResponseModel(
            success=True,
            message="Successfully logged out",
            data={"user_id": str(current_user.id)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: Session = Depends(get_db),
):
    """
    Refresh access token for FEDPOFFA user.
    """
    try:
        auth_service = AuthService(db)
        return auth_service.refresh_token(refresh_data.refresh_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}",
        )


@router.post("/verify-email", response_model=ResponseModel)
async def verify_email(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Verify user email with verification token.
    """
    try:
        auth_service = AuthService(db)
        result = auth_service.verify_email(token)

        return ResponseModel(
            success=True,
            message=result["message"],
            data={"verified": result["verified"]},
        )
    except HTTPException as e:
        return ResponseModel(
            success=False,
            message=e.detail,
            data={"verified": False},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email verification failed: {str(e)}",
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current FEDPOFFA user information.
    """
    try:
        return {
            "success": True,
            "message": "Current user information retrieved successfully",
            "data": {
                "id": str(current_user.id),
                "email": current_user.email,
                "matric_number": current_user.matric_number,
                "full_name": f"{current_user.first_name} {current_user.middle_name or ''} {current_user.last_name}".strip(),
                "role": current_user.role,
                "department_id": (
                    str(current_user.department.id) if current_user.department else None
                ),
                "is_active": current_user.is_active,
                "is_verified": current_user.is_verified,
                "level": (
                    current_user.current_level
                    if hasattr(current_user, "current_level")
                    else None
                ),
                "phone_number": current_user.phone_number,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving current user information: {str(e)}",
        )


@router.post("/change-password", response_model=ResponseModel)
async def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change current FEDPOFFA user's password.
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.change_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        return ResponseModel(
            success=True,
            message="Password changed successfully",
            data={"user_id": str(current_user.id)},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}",
        )


@router.post("/forgot-password", response_model=ResponseModel)
async def forgot_password(
    email: str,
    db: Session = Depends(get_db),
):
    """
    Send password reset email to FEDPOFFA user.
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.send_password_reset_email(email)

        return ResponseModel(
            success=True,
            message="Password reset email sent successfully",
            data={"email": email},
        )
    except HTTPException as e:
        return ResponseModel(
            success=False,
            message=e.detail,
            data=None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset request failed: {str(e)}",
        )


@router.post("/reset-password", response_model=ResponseModel)
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    """
    Reset FEDPOFFA user password with reset token.
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.reset_password(token, new_password)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        return ResponseModel(
            success=True,
            message="Password reset successfully",
            data={"reset": True},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}",
        )


@router.post("/resend-verification", response_model=ResponseModel)
async def resend_verification_email(
    email: str,
    db: Session = Depends(get_db),
):
    """
    Resend email verification to FEDPOFFA user.
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.resend_verification_email(email)

        return ResponseModel(
            success=True,
            message="Verification email resent successfully",
            data={"email": email},
        )
    except HTTPException as e:
        return ResponseModel(
            success=False,
            message=e.detail,
            data=None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification email resend failed: {str(e)}",
        )
