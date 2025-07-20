"""
Configuration settings for FEDPOFFA CBT Backend.

This module contains all configuration settings including database,
authentication, and FEDPOFFA-specific settings.
"""

import os
from typing import List, Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings with FEDPOFFA-specific configuration.
    """

    # Application
    APP_NAME: str = "FEDPOFFA CBT System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")

    # FEDPOFFA Institution
    INSTITUTION_NAME: str = "Federal Polytechnic Offa"
    INSTITUTION_URL: str = "https://portal.fedpoffaonline.edu.ng/"
    INSTITUTION_EMAIL: str = "it@fedpoffaonline.edu.ng"

    # FEDPOFFA Branding Colors
    PRIMARY_COLOR: str = "#6B46C1"  # Purple
    ACCENT_COLOR: str = "#F59E0B"  # Orange
    SUCCESS_COLOR: str = "#10B981"  # Green

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/fedpoffa_cbt", env="DATABASE_URL"
    )

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production", env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # CORS
    ALLOWED_HOSTS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"], env="ALLOWED_HOSTS"
    )

    # Email (for FEDPOFFA notifications)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")

    # File Upload (for FEDPOFFA documents)
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB

    # Assessment Settings
    DEFAULT_ASSESSMENT_DURATION: int = Field(
        default=60, env="DEFAULT_ASSESSMENT_DURATION"
    )  # minutes
    MAX_ASSESSMENT_ATTEMPTS: int = Field(default=3, env="MAX_ASSESSMENT_ATTEMPTS")
    AUTO_SAVE_INTERVAL: int = Field(default=30, env="AUTO_SAVE_INTERVAL")  # seconds

    # Redis (for session management)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# FEDPOFFA-specific constants
class FedpoffaConstants:
    """FEDPOFFA-specific constants and configurations."""

    # User Roles
    ROLE_STUDENT = "student"
    ROLE_LECTURER = "lecturer"
    ROLE_ADMIN = "admin"
    ROLE_IT_ADMIN = "it_admin"

    # Assessment Types
    ASSESSMENT_TYPE_TEST = "test"
    ASSESSMENT_TYPE_ASSIGNMENT = "assignment"
    ASSESSMENT_TYPE_EXAM = "exam"

    # Question Types
    QUESTION_TYPE_MCQ = "multiple_choice"
    QUESTION_TYPE_TRUE_FALSE = "true_false"
    QUESTION_TYPE_SHORT_ANSWER = "short_answer"
    QUESTION_TYPE_ESSAY = "essay"
    QUESTION_TYPE_MATCHING = "matching"

    # Grading Types
    GRADING_TYPE_AUTO = "automatic"
    GRADING_TYPE_MANUAL = "manual"
    GRADING_TYPE_MIXED = "mixed"

    # Academic Calendar (FEDPOFFA)
    SEMESTER_FIRST = "first"
    SEMESTER_SECOND = "second"
    SEMESTER_SUMMER = "summer"

    # Departments (FEDPOFFA)
    DEPARTMENTS = [
        "Computer Science",
        "Electrical Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Business Administration",
        "Accountancy",
        "Banking and Finance",
        "Marketing",
        "Mass Communication",
        "Architecture",
        "Building Technology",
        "Estate Management",
        "Quantity Surveying",
        "Science Laboratory Technology",
        "Food Technology",
        "Agricultural Technology",
        "Computer Engineering",
        "Telecommunications Engineering",
    ]
