# Cab Booking Backend - Folder Structure

## Current Structure Overview

```
cab_ap/
├── .env                          # Environment variables (local)
├── .env.example                  # Example environment variables
├── .env.production               # Production environment variables
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── deploy.sh                     # Deployment script
├── cab-api.service              # Systemd service file
├── Cab_Booking_API.postman_collection.json  # API testing collection
│
├── app/                         # Main application directory
│   ├── __init__.py              # App package initializer
│   ├── main.py                  # FastAPI application entry point
│   ├── database.py              # Database connection and session management
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic schemas for request/response validation
│   │
│   ├── api/                     # API versioning structure
│   │   └── v1/                  # API version 1
│   │       └── endpoints/       # API endpoints (currently empty - to be populated)
│   │
│   ├── core/                    # Core functionality (config, security, etc.)
│   │   └── (empty - to be populated)
│   │
│   ├── crud/                    # CRUD operations (currently empty - to be refactored)
│   │   └── (empty - to be populated)
│   │
│   ├── middleware/              # Custom middleware
│   │   └── (empty - to be populated)
│   │
│   ├── routers/                 # API route handlers
│   │   ├── __init__.py
│   │   ├── admins.py            # Admin management endpoints
│   │   ├── analytics.py         # Analytics and reporting endpoints
│   │   ├── drivers.py           # Driver management endpoints
│   │   ├── error_handling.py   # Error handling endpoints
│   │   ├── payments.py          # Payment processing endpoints
│   │   ├── raw_data.py          # Raw data endpoints
│   │   ├── tariff_config.py    # Tariff configuration endpoints
│   │   ├── trip_requests.py    # Trip request endpoints
│   │   ├── trips.py             # Trip management endpoints
│   │   ├── uploads.py           # File upload endpoints
│   │   ├── vehicles.py          # Vehicle management endpoints
│   │   └── wallet_transactions.py  # Wallet transaction endpoints
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   └── storage_service.py  # File storage service
│   │
│   └── utils/                   # Utility functions and helpers
│       └── (empty - to be populated)
│
├── docs/                        # Documentation files
│   └── (API documentation, guides, etc.)
│
└── uploads/                     # Uploaded files directory
    ├── drivers/                 # Driver-related uploads
    │   ├── photos/              # Driver profile photos
    │   ├── aadhar/              # Aadhar documents
    │   └── licenses/            # License documents
    └── vehicles/                # Vehicle-related uploads
        └── documents/           # Vehicle documents
```

## Recommended Folder Structure (Best Practices)

Here's the recommended structure following FastAPI and Python best practices:

```
cab_ap/
├── .env                          # Environment variables (local)
├── .env.example                  # Example environment variables
├── .env.production               # Production environment variables
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies (optional)
├── deploy.sh                     # Deployment script
├── cab-api.service              # Systemd service file
├── Cab_Booking_API.postman_collection.json
│
├── app/                         # Main application directory
│   ├── __init__.py              # App package initializer
│   ├── main.py                  # FastAPI application entry point
│   ├── database.py              # Database connection and session management
│   ├── models.py                # SQLAlchemy ORM models (or split into models/)
│   ├── schemas.py               # Pydantic schemas (or split into schemas/)
│   │
│   ├── api/                     # API layer
│   │   ├── __init__.py
│   │   ├── deps.py              # API dependencies (auth, db session, etc.)
│   │   └── v1/                  # API version 1
│   │       ├── __init__.py
│   │       ├── api.py           # API router aggregator
│   │       └── endpoints/       # Individual endpoint modules
│   │           ├── __init__.py
│   │           ├── admins.py
│   │           ├── analytics.py
│   │           ├── drivers.py
│   │           ├── payments.py
│   │           ├── trips.py
│   │           ├── vehicles.py
│   │           └── ...
│   │
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Application configuration (from .env)
│   │   ├── security.py          # Security utilities (password hashing, JWT, etc.)
│   │   ├── logging.py           # Logging configuration
│   │   └── constants.py         # Application constants
│   │
│   ├── crud/                    # CRUD operations (Database layer)
│   │   ├── __init__.py
│   │   ├── base.py              # Base CRUD class
│   │   ├── crud_driver.py       # Driver CRUD operations
│   │   ├── crud_vehicle.py      # Vehicle CRUD operations
│   │   ├── crud_trip.py         # Trip CRUD operations
│   │   ├── crud_payment.py      # Payment CRUD operations
│   │   └── ...
│   │
│   ├── middleware/              # Custom middleware
│   │   ├── __init__.py
│   │   ├── error_handler.py     # Global error handling middleware
│   │   ├── logging.py           # Request/response logging
│   │   └── rate_limit.py        # Rate limiting (optional)
│   │
│   ├── models/                  # SQLAlchemy models (if splitting models.py)
│   │   ├── __init__.py
│   │   ├── driver.py
│   │   ├── vehicle.py
│   │   ├── trip.py
│   │   ├── payment.py
│   │   └── ...
│   │
│   ├── schemas/                 # Pydantic schemas (if splitting schemas.py)
│   │   ├── __init__.py
│   │   ├── driver.py
│   │   ├── vehicle.py
│   │   ├── trip.py
│   │   ├── payment.py
│   │   └── ...
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── driver_service.py    # Driver business logic
│   │   ├── trip_service.py      # Trip business logic
│   │   ├── payment_service.py   # Payment business logic
│   │   ├── storage_service.py   # File storage service
│   │   ├── notification_service.py  # Notifications (SMS, email, push)
│   │   └── analytics_service.py # Analytics and reporting
│   │
│   └── utils/                   # Utility functions and helpers
│       ├── __init__.py
│       ├── validators.py        # Custom validators
│       ├── formatters.py        # Data formatters
│       ├── helpers.py           # General helper functions
│       └── enums.py             # Enumerations
│
├── tests/                       # Test directory
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── test_api/                # API endpoint tests
│   │   ├── __init__.py
│   │   ├── test_drivers.py
│   │   ├── test_trips.py
│   │   └── ...
│   ├── test_crud/               # CRUD operation tests
│   │   └── ...
│   └── test_services/           # Service layer tests
│       └── ...
│
├── alembic/                     # Database migrations (if using Alembic)
│   ├── versions/                # Migration versions
│   ├── env.py                   # Alembic environment
│   └── alembic.ini              # Alembic configuration
│
├── scripts/                     # Utility scripts
│   ├── init_db.py               # Database initialization
│   ├── seed_data.py             # Seed test data
│   └── backup_db.py             # Database backup
│
├── docs/                        # Documentation
│   ├── API.md                   # API documentation
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── DEVELOPMENT.md           # Development guide
│   └── ARCHITECTURE.md          # Architecture overview
│
└── uploads/                     # Uploaded files directory
    ├── drivers/
    │   ├── photos/
    │   ├── aadhar/
    │   └── licenses/
    └── vehicles/
        └── documents/
```

## Directory Purposes

### `/app` - Main Application
- **main.py**: FastAPI app initialization, middleware setup, router inclusion
- **database.py**: Database engine, session management, base class
- **models.py**: SQLAlchemy ORM models (can be split into `/models` directory)
- **schemas.py**: Pydantic models for validation (can be split into `/schemas` directory)

### `/app/api` - API Layer
- **deps.py**: Shared dependencies (authentication, database sessions)
- **v1/**: Version 1 of the API
  - **api.py**: Aggregates all endpoint routers
  - **endpoints/**: Individual endpoint modules

### `/app/core` - Core Functionality
- **config.py**: Configuration management (loads from .env)
- **security.py**: Authentication, authorization, password hashing
- **logging.py**: Logging configuration
- **constants.py**: Application-wide constants

### `/app/crud` - Database Operations
- CRUD (Create, Read, Update, Delete) operations
- Direct database interactions using SQLAlchemy
- One file per model (e.g., `crud_driver.py`, `crud_trip.py`)

### `/app/middleware` - Custom Middleware
- Error handling middleware
- Request/response logging
- Rate limiting
- CORS (if custom implementation needed)

### `/app/services` - Business Logic
- Complex business logic that doesn't fit in CRUD
- Orchestrates multiple CRUD operations
- External service integrations (payment gateways, SMS, etc.)
- File storage and management

### `/app/utils` - Utilities
- Helper functions
- Validators
- Formatters
- Enumerations

### `/tests` - Testing
- Unit tests
- Integration tests
- API endpoint tests
- Test fixtures and configurations

### `/alembic` - Database Migrations
- Version-controlled database schema changes
- Migration scripts

### `/scripts` - Utility Scripts
- Database initialization
- Data seeding
- Backup scripts
- Maintenance tasks

### `/docs` - Documentation
- API documentation
- Deployment guides
- Architecture diagrams
- Development setup

### `/uploads` - File Storage
- Organized by entity type (drivers, vehicles)
- Subdirectories by document type

## Key Principles

1. **Separation of Concerns**: Each layer has a specific responsibility
   - **Routers/Endpoints**: Handle HTTP requests/responses
   - **Services**: Business logic
   - **CRUD**: Database operations
   - **Models**: Data structure
   - **Schemas**: Validation

2. **Scalability**: Easy to add new features without affecting existing code

3. **Testability**: Each layer can be tested independently

4. **Maintainability**: Clear structure makes it easy to find and modify code

5. **Reusability**: Common functionality in utils and services

## Migration Path

To migrate from current to recommended structure:

1. **Phase 1**: Create core configuration
   - Move environment handling to `core/config.py`
   - Create `core/security.py` for auth

2. **Phase 2**: Refactor CRUD operations
   - Extract database operations from routers to `crud/` directory
   - Create base CRUD class

3. **Phase 3**: Create service layer
   - Move complex business logic from routers to `services/`
   - Keep routers thin (only HTTP handling)

4. **Phase 4**: Organize API structure
   - Move routers to `api/v1/endpoints/`
   - Create `api/v1/api.py` to aggregate routes
   - Create `api/deps.py` for shared dependencies

5. **Phase 5**: Add middleware
   - Implement error handling middleware
   - Add logging middleware

6. **Phase 6**: Split models and schemas (optional)
   - If files get too large, split into directories

7. **Phase 7**: Add tests
   - Create test structure
   - Add unit and integration tests

## Current vs Recommended

### Current Structure (Flat)
```
app/
├── routers/          # All endpoints
├── models.py         # All models
└── schemas.py        # All schemas
```

**Pros**: Simple, easy to start
**Cons**: Hard to scale, business logic mixed with HTTP handling

### Recommended Structure (Layered)
```
app/
├── api/              # HTTP layer
├── services/         # Business logic layer
├── crud/             # Database layer
├── core/             # Configuration
└── utils/            # Helpers
```

**Pros**: Scalable, testable, maintainable
**Cons**: More initial setup

## Next Steps

1. Review this structure
2. Decide which parts to implement first
3. Create a migration plan
4. Gradually refactor existing code
5. Add tests as you refactor

Would you like me to help implement any specific part of this structure?
