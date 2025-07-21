"""
Custom exceptions for FEDPOFFA CBT Backend.

This module contains custom exception classes for the application.
"""


class FedpoffaException(Exception):
    """Base exception for FEDPOFFA CBT system."""

    pass


class NotFoundException(FedpoffaException):
    """Exception raised when a resource is not found."""

    pass


class ConflictException(FedpoffaException):
    """Exception raised when there's a conflict (e.g., duplicate resource)."""

    pass


class ValidationException(FedpoffaException):
    """Exception raised when validation fails."""

    pass


class AuthenticationException(FedpoffaException):
    """Exception raised when authentication fails."""

    pass


class AuthorizationException(FedpoffaException):
    """Exception raised when authorization fails."""

    pass


class DatabaseException(FedpoffaException):
    """Exception raised when database operations fail."""

    pass
