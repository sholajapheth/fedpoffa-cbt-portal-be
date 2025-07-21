"""
Migration script to create default programs for existing courses.

This script creates default programs for each department and assigns existing courses to them.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.base import Base
from app.core.dependencies import get_db
from app.models.department import Department
from app.models.program import Program
from app.models.course import Course
from app.core.config import settings


def create_default_programs():
    """Create default programs for each department."""
    db = next(get_db())

    try:
        # Get all departments
        departments = db.query(Department).all()

        for department in departments:
            print(f"Processing department: {department.name}")

            # Create a default program for each department
            default_program = Program(
                name=f"General {department.name}",
                code=f"GEN_{department.code}",
                description=f"Default program for {department.name}",
                department_id=department.id,
                duration_years=2,
                level="ND",
                total_credits=0,
                is_active=True,
                is_accepting_enrollments=True,
            )

            db.add(default_program)
            db.commit()
            db.refresh(default_program)

            print(f"  Created program: {default_program.name}")

            # Assign all courses in this department to the default program
            courses = (
                db.query(Course)
                .filter(
                    Course.department_id == department.id, Course.program_id.is_(None)
                )
                .all()
            )

            for course in courses:
                course.program_id = default_program.id
                print(
                    f"    Assigned course '{course.name}' to program '{default_program.name}'"
                )

            db.commit()

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def make_program_id_not_null():
    """Create a migration to make program_id NOT NULL."""
    print("Creating migration to make program_id NOT NULL...")

    # This would be done through Alembic
    # For now, we'll just print the SQL that would be executed
    sql = """
    -- This SQL should be executed after all courses have program_id assigned
    ALTER TABLE courses ALTER COLUMN program_id SET NOT NULL;
    """
    print(sql)


if __name__ == "__main__":
    print("Starting course to program migration...")
    create_default_programs()
    print("Migration completed!")
