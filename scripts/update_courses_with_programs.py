#!/usr/bin/env python3
"""
Script to update existing courses with program IDs.

This script assigns existing courses to default programs in their respective departments.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.course import Course
from app.models.program import Program
from app.models.department import Department


def update_courses_with_programs():
    """Update existing courses with program IDs."""
    print("🔄 Updating courses with program IDs...")

    # Get database session
    db = next(get_db())

    try:
        # Get all courses that don't have program_id
        courses_without_program = (
            db.query(Course).filter(Course.program_id.is_(None)).all()
        )

        if not courses_without_program:
            print("✅ All courses already have program IDs assigned.")
            return

        print(f"📝 Found {len(courses_without_program)} courses without program IDs")

        # Get all departments
        departments = db.query(Department).all()
        department_programs = {}

        # For each department, get or create a default program
        for department in departments:
            # Look for existing default program
            default_program = (
                db.query(Program)
                .filter(
                    Program.department_id == department.id,
                    Program.name.like("%Default%"),
                )
                .first()
            )

            if not default_program:
                # Create a default program for this department
                default_program = Program(
                    name=f"Default {department.name} Program",
                    code=f"DEFAULT_{department.code}",
                    description=f"Default program for {department.name}",
                    department_id=department.id,
                    level="ND",
                    is_active=True,
                    is_accepting_enrollments=True,
                )
                db.add(default_program)
                db.flush()  # Get the ID
                print(f"   ✅ Created default program for {department.name}")

            department_programs[department.id] = default_program

        # Update courses with program IDs
        updated_count = 0
        for course in courses_without_program:
            if course.department_id in department_programs:
                course.program_id = department_programs[course.department_id].id
                updated_count += 1
                print(f"   ✅ Updated course {course.code} with program ID")

        db.commit()
        print(f"✅ Successfully updated {updated_count} courses with program IDs")

    except Exception as e:
        print(f"❌ Error updating courses: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_courses_with_programs()
