"""
User service for FEDPOFFA CBT Backend.

This module contains business logic for user profile management.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.department import Department
from app.core.security import (
    verify_password,
    get_password_hash,
    validate_password_strength,
)
from app.schemas.user import UserProfile, UserUpdate, PasswordChange


class UserService:
    """User service for FEDPOFFA CBT system."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_profile(self, user_id: str) -> UserProfile:
        """
        Get user profile by ID.

        Args:
            user_id: User ID

        Returns:
            UserProfile: User profile data

        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Get department name if department_id exists
        department_name = None
        if user.department_id:
            department = (
                self.db.query(Department)
                .filter(Department.id == user.department_id)
                .first()
            )
            department_name = department.name if department else None

        return UserProfile(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            full_name=user.full_name,
            email=user.email,
            matric_number=user.matric_number,
            phone_number=user.phone_number,
            role=user.role,
            department_id=str(user.department_id) if user.department_id else None,
            department_name=department_name,
            level=user.level,
            profile_picture=user.profile_picture,
            bio=user.bio,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            enrolled_courses_count=(
                len(user.enrolled_courses) if user.enrolled_courses else 0
            ),
            completed_assessments_count=0,  # TODO: Implement assessment counting
        )

    def update_user_profile(
        self, user_id: str, profile_data: UserUpdate
    ) -> UserProfile:
        """
        Update user profile.

        Args:
            user_id: User ID
            profile_data: Profile update data

        Returns:
            UserProfile: Updated user profile

        Raises:
            HTTPException: If update fails
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Update fields if provided
        if profile_data.first_name is not None:
            user.first_name = profile_data.first_name

        if profile_data.last_name is not None:
            user.last_name = profile_data.last_name

        if profile_data.middle_name is not None:
            user.middle_name = profile_data.middle_name

        if profile_data.phone_number is not None:
            user.phone_number = profile_data.phone_number

        if profile_data.department_id is not None:
            user.department_id = profile_data.department_id

        if profile_data.level is not None:
            user.level = profile_data.level

        if profile_data.matric_number is not None:
            user.matric_number = profile_data.matric_number

        if profile_data.profile_picture is not None:
            user.profile_picture = profile_data.profile_picture

        if profile_data.bio is not None:
            user.bio = profile_data.bio

        user.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(user)

        return self.get_user_profile(user_id)

    def change_password(self, user_id: str, password_data: PasswordChange) -> dict:
        """
        Change user password.

        Args:
            user_id: User ID
            password_data: Password change data

        Returns:
            dict: Success response

        Raises:
            HTTPException: If password change fails
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Validate new password strength
        if not validate_password_strength(password_data.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters with uppercase, lowercase, digit, and special character",
            )

        # Hash new password
        user.password_hash = get_password_hash(password_data.new_password)
        user.updated_at = datetime.utcnow()

        self.db.commit()

        return {"message": "Password changed successfully"}

    def get_users_paginated(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        department_id: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> dict:
        """
        Get paginated list of users with filtering options.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Optional role filter
            department_id: Optional department filter
            search: Optional search term
            is_active: Optional active status filter

        Returns:
            dict: Paginated users data
        """
        query = self.db.query(User)

        # Apply filters
        if role:
            query = query.filter(User.role == role)

        if department_id:
            query = query.filter(User.department_id == department_id)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.first_name.ilike(search_term))
                | (User.last_name.ilike(search_term))
                | (User.email.ilike(search_term))
                | (User.matric_number.ilike(search_term))
            )

        # Get total count
        total = query.count()

        # Apply pagination
        users = query.offset(skip).limit(limit).all()

        # Calculate pagination info
        pages = (total + limit - 1) // limit
        has_next = skip + limit < total
        has_prev = skip > 0

        return {
            "users": users,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_prev": has_prev,
        }

    def get_users(
        self, skip: int = 0, limit: int = 100, role: Optional[str] = None
    ) -> List[User]:
        """
        Get list of users with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Optional role filter

        Returns:
            List[User]: List of users
        """
        query = self.db.query(User)

        if role:
            query = query.filter(User.role == role)

        return query.offset(skip).limit(limit).all()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            Optional[User]: User object or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """
        Update user information.

        Args:
            user_id: User ID
            user_data: User update data

        Returns:
            User: Updated user

        Raises:
            HTTPException: If user not found or update fails
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Update fields if provided
        if user_data.first_name is not None:
            user.first_name = user_data.first_name
        if user_data.last_name is not None:
            user.last_name = user_data.last_name
        if user_data.middle_name is not None:
            user.middle_name = user_data.middle_name
        if user_data.phone_number is not None:
            user.phone_number = user_data.phone_number
        if user_data.department_id is not None:
            user.department_id = user_data.department_id
        if user_data.level is not None:
            user.level = user_data.level
        if user_data.matric_number is not None:
            user.matric_number = user_data.matric_number
        if user_data.profile_picture is not None:
            user.profile_picture = user_data.profile_picture
        if user_data.bio is not None:
            user.bio = user_data.bio

        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        return user

    def delete_user(self, user_id: str) -> bool:
        """
        Soft delete user.

        Args:
            user_id: User ID

        Returns:
            bool: True if successful, False if user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()

        return True

    def activate_user(self, user_id: str) -> bool:
        """
        Activate a deactivated user.

        Args:
            user_id: User ID

        Returns:
            bool: True if successful, False if user not found or already active
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user or user.is_active:
            return False

        user.is_active = True
        user.updated_at = datetime.utcnow()
        self.db.commit()

        return True

    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user.

        Args:
            user_id: User ID

        Returns:
            bool: True if successful, False if user not found or already deactivated
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()

        return True

    def get_user_enrollments(self, user_id: str) -> List[dict]:
        """
        Get user's course enrollments.

        Args:
            user_id: User ID

        Returns:
            List[dict]: List of enrollment data
        """
        from app.models.course_enrollment import CourseEnrollment
        from app.models.course import Course
        from app.models.semester import Semester

        enrollments = (
            self.db.query(CourseEnrollment)
            .join(Course, CourseEnrollment.course_id == Course.id)
            .join(Semester, CourseEnrollment.semester_id == Semester.id)
            .filter(CourseEnrollment.student_id == user_id)
            .all()
        )

        enrollment_data = []
        for enrollment in enrollments:
            enrollment_data.append(
                {
                    "id": str(enrollment.id),
                    "course_id": str(enrollment.course_id),
                    "course_name": enrollment.course.name,
                    "course_code": enrollment.course.code,
                    "semester_id": str(enrollment.semester_id),
                    "semester_name": enrollment.semester.name,
                    "enrollment_date": enrollment.enrollment_date,
                    "status": enrollment.status,
                    "is_active": enrollment.is_active,
                    "final_grade": enrollment.final_grade,
                    "final_score": enrollment.final_score,
                    "gpa_points": enrollment.gpa_points,
                    "attendance_percentage": enrollment.attendance_percentage,
                    "remarks": enrollment.remarks,
                }
            )

        return enrollment_data

    def get_users_stats(self) -> dict:
        """
        Get FEDPOFFA users statistics.

        Returns:
            dict: Users statistics
        """
        from datetime import datetime, timedelta

        # Get current date and 30 days ago
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)

        # Total users
        total_users = self.db.query(User).count()

        # Active users
        active_users = self.db.query(User).filter(User.is_active == True).count()

        # Verified users
        verified_users = self.db.query(User).filter(User.is_verified == True).count()

        # Users by role
        students_count = self.db.query(User).filter(User.role == "student").count()
        lecturers_count = self.db.query(User).filter(User.role == "lecturer").count()
        admins_count = (
            self.db.query(User).filter(User.role.in_(["admin", "it_admin"])).count()
        )

        # Recent registrations (last 30 days)
        recent_registrations = (
            self.db.query(User).filter(User.created_at >= thirty_days_ago).count()
        )

        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "students_count": students_count,
            "lecturers_count": lecturers_count,
            "admins_count": admins_count,
            "recent_registrations": recent_registrations,
        }

    def get_user_stats(self) -> dict:
        """
        Get user statistics.

        Returns:
            dict: User statistics
        """
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        verified_users = self.db.query(User).filter(User.is_verified == True).count()

        students_count = self.db.query(User).filter(User.role == "student").count()
        lecturers_count = self.db.query(User).filter(User.role == "lecturer").count()
        admins_count = (
            self.db.query(User).filter(User.role.in_(["admin", "it_admin"])).count()
        )

        # TODO: Implement date-based statistics
        new_users_today = 0
        new_users_this_week = 0
        new_users_this_month = 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "students_count": students_count,
            "lecturers_count": lecturers_count,
            "admins_count": admins_count,
            "new_users_today": new_users_today,
            "new_users_this_week": new_users_this_week,
            "new_users_this_month": new_users_this_month,
        }
