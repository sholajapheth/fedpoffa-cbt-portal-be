"""
Database models for FEDPOFFA CBT Backend.

This module contains all SQLAlchemy models for the FEDPOFFA CBT system.
"""

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.department import Department
from app.models.program import Program
from app.models.user_program import UserProgram
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
    "Department",
    "Program",
    "UserProgram",
    "Course",
    "Semester",
    "CourseEnrollment",
    "Question",
    "StudentResponse",
    "Assessment",
    "AssessmentSession",
    "GradingSession",
]
