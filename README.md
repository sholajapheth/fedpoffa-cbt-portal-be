# FEDPOFFA CBT Backend

A comprehensive Computer-Based Testing system backend for **Federal Polytechnic Offa (FEDPOFFA)** built with FastAPI.

## 🎯 Overview

This backend provides a robust API for managing computer-based tests, assignments, and exams for FEDPOFFA students and lecturers. The system supports automatic and manual grading, comprehensive analytics, and seamless integration with FEDPOFFA's existing portal.

## 🏛️ FEDPOFFA Branding

- **Primary Color**: Purple (#6B46C1)
- **Accent Color**: Orange (#F59E0B) 
- **Success Color**: Green (#10B981)
- **Institution**: Federal Polytechnic Offa
- **Portal**: https://portal.fedpoffaonline.edu.ng/

## 🚀 Features

### Core Functionality
- **User Management**: Students, Lecturers, Administrators, IT Admins
- **Question Bank**: Multiple question types (MCQ, True/False, Essay, etc.)
- **Assessment Creation**: Tests, assignments, and exams with scheduling
- **Test Taking**: Responsive interface with auto-save functionality
- **Automatic Grading**: Objective question scoring
- **Manual Grading**: Theory question evaluation interface
- **Analytics & Reporting**: Comprehensive performance tracking
- **FEDPOFFA Integration**: Department and course management

### User Roles
- **FEDPOFFA Students**: Take tests, view results, track performance
- **FEDPOFFA Lecturers**: Create assessments, grade theory questions, manage results
- **FEDPOFFA Administrators**: System oversight, user management, analytics
- **FEDPOFFA IT Admin**: Technical management and maintenance

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT with OAuth2
- **Dependency Management**: Poetry
- **Testing**: pytest
- **Code Quality**: black, isort, mypy

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL
- Poetry (for dependency management)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd fedpoffa-cbt-portal
```

### 2. Environment Setup

```bash
# Create virtual environment
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
poetry install

# Copy environment file
cp env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb fedpoffa_cbt

# Run migrations
make migrate-upgrade
```

### 4. Run Development Server

```bash
# Start development server
make dev

# Or using poetry directly
poetry run uvicorn app.main:app --reload
```

### 5. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
fedpoffa-cbt-portal/
├── app/
│   ├── api/v1/           # API endpoints
│   │   ├── auth/         # Authentication
│   │   ├── users/        # User management
│   │   ├── departments/  # Department management
│   │   ├── courses/      # Course management
│   │   ├── questions/    # Question bank
│   │   ├── assessments/  # Assessment management
│   │   ├── sessions/     # Test-taking sessions
│   │   ├── grading/      # Manual grading
│   │   └── analytics/    # Reports and analytics
│   ├── core/             # Core configuration
│   ├── db/               # Database configuration
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── tests/                # Test files
├── env.example           # Environment template
├── Makefile              # Common commands
├── pyproject.toml        # Poetry configuration
└── README.md            # This file
```

## 🛠️ Available Commands

### Development
```bash
make dev              # Run development server
make run              # Run production server
make test             # Run tests
make test-coverage    # Run tests with coverage
```

### Code Quality
```bash
make format           # Format code with black and isort
make lint             # Run linting checks
make check            # Run all quality checks
```

### Database
```bash
make migrate          # Create new migration
make migrate-upgrade  # Apply migrations
make migrate-downgrade # Downgrade migration
make db-reset         # Reset database
```

### Utilities
```bash
make clean            # Clean generated files
make shell            # Open Poetry shell
make docs             # Start API documentation
```

## 🔧 Configuration

### Environment Variables

Key configuration variables in `.env`:

```bash
# Database
DATABASE_URL="postgresql://user:password@localhost/fedpoffa_cbt"

# Security
SECRET_KEY="your-super-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# FEDPOFFA Settings
INSTITUTION_NAME="Federal Polytechnic Offa"
INSTITUTION_URL="https://portal.fedpoffaonline.edu.ng/"

# Assessment Settings
DEFAULT_ASSESSMENT_DURATION=60
MAX_ASSESSMENT_ATTEMPTS=3
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
poetry run pytest tests/test_auth.py
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Departments
- `GET /api/v1/departments/` - List departments
- `POST /api/v1/departments/` - Create department

### Courses
- `GET /api/v1/courses/` - List courses
- `POST /api/v1/courses/` - Create course

### Questions
- `GET /api/v1/questions/` - List questions
- `POST /api/v1/questions/` - Create question

### Assessments
- `GET /api/v1/assessments/` - List assessments
- `POST /api/v1/assessments/` - Create assessment

### Sessions
- `GET /api/v1/sessions/` - List sessions
- `POST /api/v1/sessions/` - Create session

### Grading
- `GET /api/v1/grading/` - List grading sessions
- `POST /api/v1/grading/` - Create grading session

### Analytics
- `GET /api/v1/analytics/` - Get analytics data

## 🔒 Security

- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt
- CORS configuration for FEDPOFFA frontend
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   cp env.example .env
   # Update with production values
   ```

2. **Database Migration**
   ```bash
   make migrate-upgrade
   ```

3. **Run Production Server**
   ```bash
   make run
   ```

### Docker Deployment

```bash
# Build image
docker build -t fedpoffa-cbt-backend .

# Run container
docker run -p 8000:8000 fedpoffa-cbt-backend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Submit a pull request

## 📝 License

This project is proprietary software for Federal Polytechnic Offa.

## 📞 Support

For technical support or questions:
- **Email**: it@fedpoffaonline.edu.ng
- **Portal**: https://portal.fedpoffaonline.edu.ng/

## 🗺️ Roadmap

### Phase 1: Core Foundation ✅
- [x] Project setup with Poetry
- [x] FastAPI application structure
- [x] Database models and configuration
- [x] Basic authentication framework

### Phase 2: Question Management
- [ ] Question bank CRUD operations
- [ ] Multiple question types
- [ ] Question categorization

### Phase 3: Assessment Creation
- [ ] Assessment CRUD operations
- [ ] Assessment scheduling
- [ ] Question selection and randomization

### Phase 4: Test Taking Interface
- [ ] Assessment session management
- [ ] Response collection
- [ ] Auto-save functionality

### Phase 5: Automatic Marking
- [ ] Objective question grading
- [ ] Scoring algorithms
- [ ] Result calculation

### Phase 6: Manual Marking System
- [ ] Theory question grading
- [ ] Comment and feedback system
- [ ] Batch grading capabilities

### Phase 7: Analytics & Reporting
- [ ] Performance analytics
- [ ] Report generation
- [ ] Data export capabilities

### Phase 8: Advanced Features
- [ ] Question difficulty analysis
- [ ] Cheating detection
- [ ] Advanced question types

### Future: AI Integration
- [ ] AI question generation
- [ ] Difficulty prediction
- [ ] Intelligent proctoring

---

**Built with ❤️ for Federal Polytechnic Offa** 