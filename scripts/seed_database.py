#!/usr/bin/env python3
"""
Database seeding script for FEDPOFFA CBT Backend.

This script populates the database with necessary initial data in the correct dependency order.
"""

import sys
import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import get_db
from app.models.user import User
from app.models.department import Department
from app.models.course import Course
from app.models.semester import Semester
from app.models.course_enrollment import CourseEnrollment
from app.core.security import get_password_hash
from app.core.config import FedpoffaConstants


def seed_departments(db: Session):
    """Seed departments."""
    print("🌱 Seeding departments...")

    departments_data = [
        {
            "name": "Computer Science",
            "code": "CSC",
            "description": "Department of Computer Science and Information Technology",
            "hod_name": "Dr. John Smith",
            "hod_email": "hod.cs@fedpoffa.edu.ng",
            "hod_phone": "+2348012345678",
        },
        {
            "name": "Electrical Engineering",
            "code": "EEE",
            "description": "Department of Electrical and Electronic Engineering",
            "hod_name": "Dr. Sarah Johnson",
            "hod_email": "hod.eee@fedpoffa.edu.ng",
            "hod_phone": "+2348012345679",
        },
        {
            "name": "Mechanical Engineering",
            "code": "MEE",
            "description": "Department of Mechanical Engineering",
            "hod_name": "Dr. Michael Brown",
            "hod_email": "hod.mee@fedpoffa.edu.ng",
            "hod_phone": "+2348012345680",
        },
        {
            "name": "Business Administration",
            "code": "BUA",
            "description": "Department of Business Administration and Management",
            "hod_name": "Dr. Emily Davis",
            "hod_email": "hod.bua@fedpoffa.edu.ng",
            "hod_phone": "+2348012345681",
        },
        {
            "name": "Accountancy",
            "code": "ACC",
            "description": "Department of Accountancy",
            "hod_name": "Dr. David Wilson",
            "hod_email": "hod.acc@fedpoffa.edu.ng",
            "hod_phone": "+2348012345682",
        },
    ]

    departments = []
    for dept_data in departments_data:
        # Check if department already exists
        existing = (
            db.query(Department).filter(Department.code == dept_data["code"]).first()
        )
        if existing:
            print(f"   ⚠️  Department {dept_data['code']} already exists, skipping...")
            departments.append(existing)
            continue

        department = Department(
            id=uuid.uuid4(),
            name=dept_data["name"],
            code=dept_data["code"],
            description=dept_data["description"],
            hod_name=dept_data["hod_name"],
            hod_email=dept_data["hod_email"],
            hod_phone=dept_data["hod_phone"],
        )
        db.add(department)
        departments.append(department)
        print(f"   ✅ Created department: {dept_data['name']} ({dept_data['code']})")

    db.commit()
    print(f"   📊 Total departments: {len(departments)}")
    return departments


def seed_semesters(db: Session):
    """Seed semesters."""
    print("🌱 Seeding semesters...")

    # Get current year
    current_year = datetime.now().year

    semesters_data = [
        {
            "name": f"{current_year}/{current_year + 1} First Semester",
            "academic_year": f"{current_year}/{current_year + 1}",
            "semester_type": "first",
            "start_date": datetime(current_year, 9, 1),
            "end_date": datetime(current_year, 12, 31),
            "registration_start": datetime(current_year, 8, 15),
            "registration_end": datetime(current_year, 9, 30),
            "exam_start": datetime(current_year, 12, 1),
            "exam_end": datetime(current_year, 12, 31),
            "description": f"First semester of academic year {current_year}/{current_year + 1}",
            "is_current": True,
        },
        {
            "name": f"{current_year}/{current_year + 1} Second Semester",
            "academic_year": f"{current_year}/{current_year + 1}",
            "semester_type": "second",
            "start_date": datetime(current_year + 1, 1, 1),
            "end_date": datetime(current_year + 1, 4, 30),
            "registration_start": datetime(current_year, 12, 15),
            "registration_end": datetime(current_year + 1, 1, 31),
            "exam_start": datetime(current_year + 1, 4, 1),
            "exam_end": datetime(current_year + 1, 4, 30),
            "description": f"Second semester of academic year {current_year}/{current_year + 1}",
            "is_current": False,
        },
    ]

    semesters = []
    for sem_data in semesters_data:
        # Check if semester already exists
        existing = db.query(Semester).filter(Semester.name == sem_data["name"]).first()
        if existing:
            print(f"   ⚠️  Semester {sem_data['name']} already exists, skipping...")
            semesters.append(existing)
            continue

        semester = Semester(
            id=uuid.uuid4(),
            name=sem_data["name"],
            academic_year=sem_data["academic_year"],
            semester_type=sem_data["semester_type"],
            start_date=sem_data["start_date"],
            end_date=sem_data["end_date"],
            registration_start=sem_data["registration_start"],
            registration_end=sem_data["registration_end"],
            exam_start=sem_data["exam_start"],
            exam_end=sem_data["exam_end"],
            description=sem_data["description"],
            is_current=sem_data["is_current"],
        )
        db.add(semester)
        semesters.append(semester)
        print(f"   ✅ Created semester: {sem_data['name']}")

    db.commit()
    print(f"   📊 Total semesters: {len(semesters)}")
    return semesters


def seed_users(db: Session, departments):
    """Seed users (admin, lecturers, students)."""
    print("🌱 Seeding users...")

    # Get first department for default assignment
    default_dept = departments[0] if departments else None

    users_data = [
        # Admin users
        {
            "first_name": "Admin",
            "last_name": "User",
            "middle_name": None,
            "email": "admin@fedpoffa.edu.ng",
            "matric_number": "ADMIN001",
            "password": "AdminPass123!",
            "role": FedpoffaConstants.ROLE_ADMIN,
            "department_id": default_dept.id if default_dept else None,
            "phone_number": "+2348012345683",
            "level": None,
        },
        {
            "first_name": "IT",
            "last_name": "Admin",
            "middle_name": None,
            "email": "it.admin@fedpoffa.edu.ng",
            "matric_number": "ITADMIN001",
            "password": "ITAdminPass123!",
            "role": FedpoffaConstants.ROLE_IT_ADMIN,
            "department_id": default_dept.id if default_dept else None,
            "phone_number": "+2348012345684",
            "level": None,
        },
        # Lecturer users
        {
            "first_name": "Dr. John",
            "last_name": "Smith",
            "middle_name": "A.",
            "email": "john.smith@fedpoffa.edu.ng",
            "matric_number": "LECT001",
            "password": "LecturerPass123!",
            "role": FedpoffaConstants.ROLE_LECTURER,
            "department_id": departments[0].id if len(departments) > 0 else None,
            "phone_number": "+2348012345685",
            "level": None,
        },
        {
            "first_name": "Dr. Sarah",
            "last_name": "Johnson",
            "middle_name": "B.",
            "email": "sarah.johnson@fedpoffa.edu.ng",
            "matric_number": "LECT002",
            "password": "LecturerPass123!",
            "role": FedpoffaConstants.ROLE_LECTURER,
            "department_id": departments[1].id if len(departments) > 1 else None,
            "phone_number": "+2348012345686",
            "level": None,
        },
        # Student users
        {
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "Smith",
            "email": "john.doe@fedpoffa.edu.ng",
            "matric_number": "2023/001",
            "password": "StudentPass123!",
            "role": FedpoffaConstants.ROLE_STUDENT,
            "department_id": departments[0].id if len(departments) > 0 else None,
            "phone_number": "+2348012345687",
            "level": "ND1",
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "middle_name": "A.",
            "email": "jane.smith@fedpoffa.edu.ng",
            "matric_number": "2023/002",
            "password": "StudentPass123!",
            "role": FedpoffaConstants.ROLE_STUDENT,
            "department_id": departments[0].id if len(departments) > 0 else None,
            "phone_number": "+2348012345688",
            "level": "ND1",
        },
        {
            "first_name": "Michael",
            "last_name": "Brown",
            "middle_name": "C.",
            "email": "michael.brown@fedpoffa.edu.ng",
            "matric_number": "2023/003",
            "password": "StudentPass123!",
            "role": FedpoffaConstants.ROLE_STUDENT,
            "department_id": departments[1].id if len(departments) > 1 else None,
            "phone_number": "+2348012345689",
            "level": "ND2",
        },
    ]

    users = []
    for user_data in users_data:
        # Check if user already exists
        existing = (
            db.query(User)
            .filter(
                (User.email == user_data["email"])
                | (User.matric_number == user_data["matric_number"])
            )
            .first()
        )
        if existing:
            print(f"   ⚠️  User {user_data['email']} already exists, skipping...")
            users.append(existing)
            continue

        user = User(
            id=uuid.uuid4(),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            middle_name=user_data["middle_name"],
            email=user_data["email"],
            matric_number=user_data["matric_number"],
            password_hash=get_password_hash(user_data["password"]),
            role=user_data["role"],
            department_id=user_data["department_id"],
            phone_number=user_data["phone_number"],
            level=user_data["level"],
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        users.append(user)
        print(f"   ✅ Created user: {user_data['email']} ({user_data['role']})")

    db.commit()
    print(f"   📊 Total users: {len(users)}")
    return users


def seed_courses(db: Session, departments, users):
    """Seed courses."""
    print("🌱 Seeding courses...")

    # Get lecturers
    lecturers = [u for u in users if u.role == FedpoffaConstants.ROLE_LECTURER]

    courses_data = [
        {
            "name": "Introduction to Computer Science",
            "code": "CSC101",
            "description": "Basic concepts of computer science and programming",
            "department_id": departments[0].id if len(departments) > 0 else None,
            "credits": 3,
            "level": "ND1",
            "semester": "first",
            "course_coordinator_id": lecturers[0].id if lecturers else None,
            "prerequisites": None,
            "course_outline": "Programming fundamentals, algorithms, data structures",
        },
        {
            "name": "Programming Fundamentals",
            "code": "CSC102",
            "description": "Introduction to programming with Python",
            "department_id": departments[0].id if len(departments) > 0 else None,
            "credits": 4,
            "level": "ND1",
            "semester": "first",
            "course_coordinator_id": lecturers[0].id if lecturers else None,
            "prerequisites": "CSC101",
            "course_outline": "Python programming, control structures, functions",
        },
        {
            "name": "Electrical Circuits",
            "code": "EEE101",
            "description": "Basic electrical circuit analysis",
            "department_id": departments[1].id if len(departments) > 1 else None,
            "credits": 4,
            "level": "ND1",
            "semester": "first",
            "course_coordinator_id": lecturers[1].id if len(lecturers) > 1 else None,
            "prerequisites": None,
            "course_outline": "Circuit analysis, Ohm's law, Kirchhoff's laws",
        },
        {
            "name": "Business Management",
            "code": "BUA101",
            "description": "Principles of business management",
            "department_id": departments[3].id if len(departments) > 3 else None,
            "credits": 3,
            "level": "ND1",
            "semester": "first",
            "course_coordinator_id": lecturers[0].id if lecturers else None,
            "prerequisites": None,
            "course_outline": "Management principles, organizational behavior",
        },
    ]

    courses = []
    for course_data in courses_data:
        # Check if course already exists
        existing = db.query(Course).filter(Course.code == course_data["code"]).first()
        if existing:
            print(f"   ⚠️  Course {course_data['code']} already exists, skipping...")
            courses.append(existing)
            continue

        course = Course(
            id=uuid.uuid4(),
            name=course_data["name"],
            code=course_data["code"],
            description=course_data["description"],
            department_id=course_data["department_id"],
            credits=course_data["credits"],
            level=course_data["level"],
            semester=course_data["semester"],
            course_coordinator_id=course_data["course_coordinator_id"],
            prerequisites=course_data["prerequisites"],
            course_outline=course_data["course_outline"],
        )
        db.add(course)
        courses.append(course)
        print(f"   ✅ Created course: {course_data['name']} ({course_data['code']})")

    db.commit()
    print(f"   📊 Total courses: {len(courses)}")
    return courses


def seed_enrollments(db: Session, users, courses, semesters):
    """Seed course enrollments."""
    print("🌱 Seeding course enrollments...")

    # Get students
    students = [u for u in users if u.role == FedpoffaConstants.ROLE_STUDENT]
    current_semester = next(
        (s for s in semesters if s.is_current), semesters[0] if semesters else None
    )

    if not students or not courses or not current_semester:
        print(
            "   ⚠️  No students, courses, or current semester found, skipping enrollments..."
        )
        return []

    enrollments = []
    for student in students:
        # Enroll student in courses from their department
        for course in courses:
            if course.department_id == student.department_id:
                # Check if enrollment already exists
                existing = (
                    db.query(CourseEnrollment)
                    .filter(
                        CourseEnrollment.student_id == student.id,
                        CourseEnrollment.course_id == course.id,
                        CourseEnrollment.semester_id == current_semester.id,
                    )
                    .first()
                )

                if existing:
                    print(
                        f"   ⚠️  Enrollment for {student.matric_number} in {course.code} already exists, skipping..."
                    )
                    enrollments.append(existing)
                    continue

                enrollment = CourseEnrollment(
                    id=uuid.uuid4(),
                    student_id=student.id,
                    course_id=course.id,
                    semester_id=current_semester.id,
                    status="enrolled",
                    is_active=True,
                )
                db.add(enrollment)
                enrollments.append(enrollment)
                print(f"   ✅ Enrolled {student.matric_number} in {course.code}")

    db.commit()
    print(f"   📊 Total enrollments: {len(enrollments)}")
    return enrollments


def main():
    """Main seeding function."""
    print("🚀 Starting FEDPOFFA CBT Database Seeding...")
    print("=" * 50)

    # Get database session
    db = next(get_db())

    try:
        # Seed in dependency order
        departments = seed_departments(db)
        semesters = seed_semesters(db)
        users = seed_users(db, departments)
        courses = seed_courses(db, departments, users)
        enrollments = seed_enrollments(db, users, courses, semesters)

        print("=" * 50)
        print("✅ Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Departments: {len(departments)}")
        print(f"   - Semesters: {len(semesters)}")
        print(f"   - Users: {len(users)}")
        print(f"   - Courses: {len(courses)}")
        print(f"   - Enrollments: {len(enrollments)}")
        print("\n🔑 Default Login Credentials:")
        print("   Admin: admin@fedpoffa.edu.ng / AdminPass123!")
        print("   IT Admin: it.admin@fedpoffa.edu.ng / ITAdminPass123!")
        print("   Lecturer: john.smith@fedpoffa.edu.ng / LecturerPass123!")
        print("   Student: john.doe@fedpoffa.edu.ng / StudentPass123!")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
