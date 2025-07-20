"""
User management endpoints for FEDPOFFA CBT Backend.

This module handles user operations including CRUD operations, profile management,
and user-specific data retrieval.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.dependencies import get_current_user, require_roles
from app.services.user_service import UserService
from app.schemas.user import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserProfile,
    UserListResponse,
    UserEnrollmentResponse,
    UserSimpleResponse,
)
from app.schemas.common import ResponseModel, PaginatedResponse
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    search: Optional[str] = Query(
        None, description="Search by name, email, or matric number"
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_roles(["admin", "it_admin"])),
):
    """
    Get paginated list of FEDPOFFA users with filtering options.

    This endpoint is restricted to admin and IT admin users only.
    """
    try:
        user_service = UserService(db)
        users_data = user_service.get_users_paginated(
            skip=skip,
            limit=limit,
            role=role,
            department_id=department_id,
            search=search,
            is_active=is_active,
        )

        return PaginatedResponse(
            success=True,
            message="Users retrieved successfully",
            data=[
                {
                    "id": str(user.id),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "middle_name": user.middle_name,
                    "full_name": f"{user.first_name} {user.middle_name or ''} {user.last_name}".strip(),
                    "email": user.email,
                    "matric_number": user.matric_number,
                    "phone_number": user.phone_number,
                    "role": user.role,
                    "department_id": (
                        str(user.department_id) if user.department_id else None
                    ),
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "last_login": user.last_login,
                }
                for user in users_data["users"]
            ],
            total=users_data["total"],
            page=skip // limit + 1,
            pages=users_data["pages"],
            has_next=users_data["has_next"],
            has_prev=users_data["has_prev"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}",
        )


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current FEDPOFFA user's profile information.
    """
    try:
        user_service = UserService(db)
        profile = user_service.get_user_profile(current_user.id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )

        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {str(e)}",
        )


@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    profile_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update current FEDPOFFA user's profile information.
    """
    try:
        user_service = UserService(db)
        updated_profile = user_service.update_user_profile(
            current_user.id, profile_data
        )

        return updated_profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}",
        )


@router.get("/{user_id}", response_model=UserSimpleResponse)
async def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_roles(["admin", "it_admin"])),
):
    """
    Get FEDPOFFA user by ID.

    This endpoint is restricted to admin and IT admin users only.
    """
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "middle_name": user.middle_name,
            "full_name": f"{user.first_name} {user.middle_name or ''} {user.last_name}".strip(),
            "email": user.email,
            "matric_number": user.matric_number,
            "phone_number": user.phone_number,
            "role": user.role,
            "department_id": str(user.department_id) if user.department_id else None,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}",
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_roles(["admin", "it_admin"])),
):
    """
    Update FEDPOFFA user information.

    This endpoint is restricted to admin and IT admin users only.
    """
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user(user_id, user_data)

        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        )


@router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_roles(["admin", "it_admin"])),
):
    """
    Delete FEDPOFFA user (soft delete).

    This endpoint is restricted to admin and IT admin users only.
    """
    try:
        # Prevent self-deletion
        if user_id == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account",
            )

        user_service = UserService(db)
        success = user_service.delete_user(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return ResponseModel(
            success=True,
            message="User deleted successfully",
            data={"user_id": user_id},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}",
        )


@router.get("/{user_id}/enrollments", response_model=List[UserEnrollmentResponse])
async def get_user_enrollments(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_roles(["admin", "it_admin", "lecturer"])),
):
    """
    Get FEDPOFFA user's course enrollments.

    This endpoint is restricted to admin, IT admin, and lecturer users only.
    """
    try:
        user_service = UserService(db)
        enrollments = user_service.get_user_enrollments(user_id)

        return enrollments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user enrollments: {str(e)}",
        )


@router.post("/{user_id}/activate", response_model=ResponseModel)
async def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_roles(["admin", "it_admin"])),
):
    """
    Activate a deactivated FEDPOFFA user.

    This endpoint is restricted to admin and IT admin users only.
    """
    try:
        user_service = UserService(db)
        success = user_service.activate_user(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or already active",
            )

        return ResponseModel(
            success=True,
            message="User activated successfully",
            data={"user_id": user_id},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating user: {str(e)}",
        )


@router.post("/{user_id}/deactivate", response_model=ResponseModel)
async def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_roles(["admin", "it_admin"])),
):
    """
    Deactivate a FEDPOFFA user.

    This endpoint is restricted to admin and IT admin users only.
    """
    try:
        # Prevent self-deactivation
        if user_id == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account",
            )

        user_service = UserService(db)
        success = user_service.deactivate_user(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or already deactivated",
            )

        return ResponseModel(
            success=True,
            message="User deactivated successfully",
            data={"user_id": user_id},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating user: {str(e)}",
        )


@router.get("/stats/overview", response_model=dict)
async def get_users_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_roles(["admin", "it_admin"])),
):
    """
    Get FEDPOFFA users statistics overview.

    This endpoint is restricted to admin and IT admin users only.
    """
    try:
        user_service = UserService(db)
        stats = user_service.get_users_stats()

        return {
            "success": True,
            "message": "Users statistics retrieved successfully",
            "data": stats,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users statistics: {str(e)}",
        )
