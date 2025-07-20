"""
Database base configuration for FEDPOFFA CBT Backend.

This module contains the SQLAlchemy database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,  # Enable SQL logging in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database with all tables.

    This function creates all tables defined in the models.
    """
    from app.db.base import Base
    from app.models import (
        user,
        department,
        course,
        question,
        assessment,
        session,
        grading,
    )

    # Import all models to ensure they are registered
    Base.metadata.create_all(bind=engine)
