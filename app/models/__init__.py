"""
Database models for FEDPOFFA CBT Backend.

This module contains all SQLAlchemy models for the FEDPOFFA CBT system.
"""

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User, user_course_association
from app.models.department import Department
from app.models.course import Course
from app.models.semester import Semester
from app.models.course_enrollment import CourseEnrollment
from app.models.question import Question
from app.models.student_response import StudentResponse
from app.models.assessment import Assessment
from app.models.session import AssessmentSession
from app.models.grading import GradingSession

__all__ = [
    "User",
    "user_course_association",
    "Department",
    "Course",
    "Semester",
    "CourseEnrollment",
    "Question",
    "StudentResponse",
    "Assessment",
    "AssessmentSession",
    "GradingSession",
]
