.PHONY: help install dev-install run dev test lint format check clean migrate migrate-upgrade migrate-downgrade db-reset

# Default target
help:
	@echo "FEDPOFFA CBT Backend - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install          Install production dependencies"
	@echo "  dev-install      Install all dependencies (including dev)"
	@echo ""
	@echo "Development:"
	@echo "  run              Run the FastAPI server in production mode"
	@echo "  dev              Run the FastAPI server in development mode with auto-reload"
	@echo "  test             Run all tests"
	@echo "  test-coverage    Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint             Run linting checks (black, isort, mypy)"
	@echo "  format           Format code with black and isort"
	@echo "  check            Run all code quality checks"
	@echo ""
	@echo "Database:"
	@echo "  migrate          Create a new migration"
	@echo "  migrate-upgrade  Apply all pending migrations"
	@echo "  migrate-downgrade Downgrade one migration"
	@echo "  db-reset         Reset database (drop and recreate)"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            Clean up generated files"
	@echo "  shell            Open Poetry shell"
	@echo "  docs             Generate API documentation"

# Setup
install:
	poetry install --only main

dev-install:
	poetry install

# Development
run:
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Testing
test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=app --cov-report=html --cov-report=term

# Code Quality
lint:
	poetry run black --check app tests
	poetry run isort --check-only app tests
	poetry run mypy app

format:
	poetry run black app tests
	poetry run isort app tests

check: lint test

# Database
migrate:
	poetry run alembic revision --autogenerate -m "$(message)"

migrate-upgrade:
	poetry run alembic upgrade head

migrate-downgrade:
	poetry run alembic downgrade -1

db-reset:
	poetry run alembic downgrade base
	poetry run alembic upgrade head

# Utilities
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov

shell:
	poetry shell

docs:
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
	@echo "API documentation available at: http://localhost:8000/docs"
	@echo "ReDoc available at: http://localhost:8000/redoc" 