"""
Department service for FEDPOFFA CBT Backend.

This module contains business logic for department management.
"""

import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.user import User
from app.models.course import Course
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentDetail,
    DepartmentListResponse,
    DepartmentStats,
)


class DepartmentService:
    """Department service for FEDPOFFA CBT system."""

    def __init__(self, db: Session):
        self.db = db

    def create_department(
        self, department_data: DepartmentCreate
    ) -> DepartmentResponse:
        """
        Create a new department.

        Args:
            department_data: Department creation data

        Returns:
            DepartmentResponse: Created department data

        Raises:
            HTTPException: If department creation fails
        """
        # Check if department with same code already exists
        existing_dept = (
            self.db.query(Department)
            .filter(Department.code == department_data.code)
            .first()
        )

        if existing_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department with this code already exists",
            )

        # Create new department
        department = Department(
            id=uuid.uuid4(),
            name=department_data.name,
            code=department_data.code,
            description=department_data.description,
            hod_name=department_data.hod_name,
            hod_email=department_data.hod_email,
            hod_phone=department_data.hod_phone,
        )

        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)

        return DepartmentResponse(
            id=str(department.id),
            name=department.name,
            code=department.code,
            description=department.description,
            hod_name=department.hod_name,
            hod_email=department.hod_email,
            hod_phone=department.hod_phone,
            is_active=department.is_active,
            created_at=department.created_at,
            updated_at=department.updated_at,
            total_users=0,
            total_courses=0,
            students_count=0,
            lecturers_count=0,
        )

    def get_departments(
        self, skip: int = 0, limit: int = 100, active_only: bool = False
    ) -> DepartmentListResponse:
        """
        Get list of departments with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Filter only active departments

        Returns:
            DepartmentListResponse: List of departments with pagination info
        """
        query = self.db.query(Department)

        if active_only:
            query = query.filter(Department.is_active == True)

        total = query.count()
        departments = query.offset(skip).limit(limit).all()

        # Convert to response models
        department_responses = []
        for dept in departments:
            dept_response = DepartmentResponse(
                id=str(dept.id),
                name=dept.name,
                code=dept.code,
                description=dept.description,
                hod_name=dept.hod_name,
                hod_email=dept.hod_email,
                hod_phone=dept.hod_phone,
                is_active=dept.is_active,
                created_at=dept.created_at,
                updated_at=dept.updated_at,
                total_users=dept.total_users,
                total_courses=dept.total_courses,
                students_count=dept.students_count,
                lecturers_count=dept.lecturers_count,
            )
            department_responses.append(dept_response)

        pages = (total + limit - 1) // limit if limit > 0 else 1

        return DepartmentListResponse(
            departments=department_responses,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit,
            pages=pages,
        )

    def get_department(self, department_id: str) -> DepartmentDetail:
        """
        Get department by ID with detailed information.

        Args:
            department_id: Department ID

        Returns:
            DepartmentDetail: Department details with related data

        Raises:
            HTTPException: If department not found
        """
        department = (
            self.db.query(Department).filter(Department.id == department_id).first()
        )

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )

        # Get related courses
        courses = (
            self.db.query(Course).filter(Course.department_id == department_id).all()
        )
        courses_data = [
            {
                "id": str(course.id),
                "name": course.name,
                "code": course.code,
                "description": course.description,
            }
            for course in courses
        ]

        # Get related users
        users = self.db.query(User).filter(User.department_id == department_id).all()
        users_data = [
            {
                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
            }
            for user in users
        ]

        return DepartmentDetail(
            id=str(department.id),
            name=department.name,
            code=department.code,
            description=department.description,
            hod_name=department.hod_name,
            hod_email=department.hod_email,
            hod_phone=department.hod_phone,
            is_active=department.is_active,
            created_at=department.created_at,
            updated_at=department.updated_at,
            total_users=department.total_users,
            total_courses=department.total_courses,
            students_count=department.students_count,
            lecturers_count=department.lecturers_count,
            courses=courses_data,
            users=users_data,
        )

    def update_department(
        self, department_id: str, department_data: DepartmentUpdate
    ) -> DepartmentResponse:
        """
        Update department.

        Args:
            department_id: Department ID
            department_data: Department update data

        Returns:
            DepartmentResponse: Updated department data

        Raises:
            HTTPException: If department not found or update fails
        """
        department = (
            self.db.query(Department).filter(Department.id == department_id).first()
        )

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )

        # Update fields if provided
        if department_data.name is not None:
            department.name = department_data.name
        if department_data.code is not None:
            # Check if new code already exists
            existing_dept = (
                self.db.query(Department)
                .filter(
                    Department.code == department_data.code,
                    Department.id != department_id,
                )
                .first()
            )
            if existing_dept:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department with this code already exists",
                )
            department.code = department_data.code
        if department_data.description is not None:
            department.description = department_data.description
        if department_data.hod_name is not None:
            department.hod_name = department_data.hod_name
        if department_data.hod_email is not None:
            department.hod_email = department_data.hod_email
        if department_data.hod_phone is not None:
            department.hod_phone = department_data.hod_phone
        if department_data.is_active is not None:
            department.is_active = department_data.is_active

        department.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(department)

        return DepartmentResponse(
            id=str(department.id),
            name=department.name,
            code=department.code,
            description=department.description,
            hod_name=department.hod_name,
            hod_email=department.hod_email,
            hod_phone=department.hod_phone,
            is_active=department.is_active,
            created_at=department.created_at,
            updated_at=department.updated_at,
            total_users=department.total_users,
            total_courses=department.total_courses,
            students_count=department.students_count,
            lecturers_count=department.lecturers_count,
        )

    def delete_department(self, department_id: str):
        """
        Delete department.

        Args:
            department_id: Department ID

        Raises:
            HTTPException: If department not found or has related data
        """
        department = (
            self.db.query(Department).filter(Department.id == department_id).first()
        )

        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )

        # Check if department has related users
        users_count = (
            self.db.query(User).filter(User.department_id == department_id).count()
        )
        if users_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete department with existing users",
            )

        # Check if department has related courses
        courses_count = (
            self.db.query(Course).filter(Course.department_id == department_id).count()
        )
        if courses_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete department with existing courses",
            )

        self.db.delete(department)
        self.db.commit()

    def get_department_stats(self) -> DepartmentStats:
        """
        Get department statistics.

        Returns:
            DepartmentStats: Department statistics
        """
        total_departments = self.db.query(Department).count()
        active_departments = (
            self.db.query(Department).filter(Department.is_active == True).count()
        )

        total_courses = self.db.query(Course).count()
        total_students = self.db.query(User).filter(User.role == "student").count()
        total_lecturers = self.db.query(User).filter(User.role == "lecturer").count()

        return DepartmentStats(
            total_departments=total_departments,
            active_departments=active_departments,
            total_courses=total_courses,
            total_students=total_students,
            total_lecturers=total_lecturers,
        )
