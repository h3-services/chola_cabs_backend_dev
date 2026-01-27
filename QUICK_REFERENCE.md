# Quick Reference Guide - Cab Booking Backend

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Application
```bash
# Development
python -m uvicorn app.main:app --reload

# Production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📚 New Core Modules (Phase 1)

### 1. Configuration (`app/core/config.py`)

```python
from app.core.config import settings

# Database
settings.database_url          # MySQL connection URL
settings.DB_HOST              # Database host
settings.DB_NAME              # Database name

# Application
settings.APP_NAME             # Application name
settings.DEBUG                # Debug mode
settings.BASE_URL             # Base URL for API

# File Storage
settings.UPLOAD_DIR           # Upload directory path
settings.upload_url_base      # Base URL for uploads

# Security
settings.SECRET_KEY           # JWT secret key
settings.ACCESS_TOKEN_EXPIRE_MINUTES  # Token expiration

# S3 Storage (Optional)
settings.USE_S3_STORAGE       # Enable S3 storage
settings.S3_BUCKET_NAME       # S3 bucket name
```

### 2. Constants (`app/core/constants.py`)

```python
from app.core.constants import (
    TripStatus, KYCStatus, AdminRole,
    VehicleType, PaymentStatus, ErrorCode
)

# Trip Status
TripStatus.OPEN
TripStatus.ASSIGNED
TripStatus.STARTED
TripStatus.COMPLETED
TripStatus.CANCELLED

# KYC Status
KYCStatus.PENDING
KYCStatus.APPROVED
KYCStatus.REJECTED

# Admin Roles
AdminRole.SUPER_ADMIN
AdminRole.ADMIN
AdminRole.OPERATOR

# Error Codes
ErrorCode.DRIVER_NOT_FOUND        # 1001
ErrorCode.VEHICLE_NOT_FOUND       # 2001
ErrorCode.TRIP_NOT_FOUND          # 3001
ErrorCode.PAYMENT_FAILED          # 4002
```

### 3. Security (`app/core/security.py`)

```python
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
    get_current_admin,
    get_current_super_admin
)

# Password Hashing
hashed = get_password_hash("password123")
is_valid = verify_password("password123", hashed)

# JWT Tokens
token = create_access_token(data={"sub": user_id, "role": "ADMIN"})
payload = decode_access_token(token)

# Protect Endpoints
@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

@router.get("/admin-only")
def admin_route(current_admin: dict = Depends(get_current_admin)):
    return {"admin": current_admin}

@router.get("/super-admin-only")
def super_admin_route(current_admin: dict = Depends(get_current_super_admin)):
    return {"super_admin": current_admin}
```

### 4. Logging (`app/core/logging.py`)

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# Log levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# With exception info
try:
    # some code
    pass
except Exception as e:
    logger.error("Error occurred", exc_info=True)
```

### 5. Dependencies (`app/api/deps.py`)

```python
from app.api.deps import (
    get_db,
    get_current_user,
    get_current_admin,
    get_current_super_admin
)

# Database Session
@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items

# Authentication
@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Admin Only
@router.post("/admin-action")
def admin_action(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    # Admin-only action
    pass
```

---

## 🔧 Common Patterns

### 1. Create a New Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.logging import get_logger
from app.core.constants import ErrorCode

router = APIRouter(prefix="/items", tags=["items"])
logger = get_logger(__name__)

@router.get("/")
def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching items: skip={skip}, limit={limit}")
    
    try:
        items = db.query(Item).offset(skip).limit(limit).all()
        return items
    except Exception as e:
        logger.error(f"Error fetching items: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch items"
        )
```

### 2. Use Configuration

```python
from app.core.config import settings

# In your code
if settings.DEBUG:
    print("Debug mode enabled")

# File upload
upload_path = os.path.join(settings.UPLOAD_DIR, "photos")
file_url = f"{settings.upload_url_base}/photos/{filename}"
```

### 3. Use Constants Instead of Magic Strings

```python
# ❌ Bad
if trip.status == "COMPLETED":
    pass

# ✅ Good
from app.core.constants import TripStatus

if trip.status == TripStatus.COMPLETED:
    pass
```

### 4. Implement Authentication

```python
from app.core.security import create_access_token, get_current_user
from app.api.deps import get_db

@router.post("/login")
def login(phone: str, password: str, db: Session = Depends(get_db)):
    # Verify credentials
    user = db.query(User).filter(User.phone == phone).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_access_token(data={
        "sub": user.id,
        "role": user.role
    })
    
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
```

---

## 📁 File Organization

### Where to Put New Code:

| Type | Location | Example |
|------|----------|---------|
| Configuration | `app/core/config.py` | Add new env variable |
| Constants | `app/core/constants.py` | Add new enum |
| Security | `app/core/security.py` | Add auth function |
| API Endpoint | `app/routers/` | Add new router |
| Business Logic | `app/services/` | Add service class |
| Database Query | `app/crud/` (Phase 2) | Add CRUD operation |
| Utility Function | `app/utils/` (Phase 7) | Add helper function |
| Middleware | `app/middleware/` (Phase 6) | Add middleware |

---

## 🎯 Best Practices

### 1. Always Use Dependencies
```python
# ✅ Good
from app.api.deps import get_db

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    pass

# ❌ Bad
from app.database import SessionLocal

@router.get("/items")
def get_items():
    db = SessionLocal()
    # ... forgot to close db
```

### 2. Use Logging
```python
# ✅ Good
from app.core.logging import get_logger

logger = get_logger(__name__)

@router.post("/items")
def create_item(item: ItemCreate):
    logger.info(f"Creating item: {item.name}")
    try:
        # create item
        logger.info(f"Item created successfully: {item.id}")
    except Exception as e:
        logger.error(f"Failed to create item: {e}", exc_info=True)
        raise

# ❌ Bad
@router.post("/items")
def create_item(item: ItemCreate):
    print("Creating item")  # Don't use print
```

### 3. Use Constants
```python
# ✅ Good
from app.core.constants import TripStatus, ErrorCode

if trip.status == TripStatus.COMPLETED:
    pass

raise HTTPException(
    status_code=404,
    detail={"error_code": ErrorCode.TRIP_NOT_FOUND}
)

# ❌ Bad
if trip.status == "COMPLETED":  # Magic string
    pass
```

### 4. Handle Errors Properly
```python
# ✅ Good
from app.core.logging import get_logger
from app.core.constants import ErrorCode

logger = get_logger(__name__)

@router.get("/items/{item_id}")
def get_item(item_id: str, db: Session = Depends(get_db)):
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=404,
                detail={"error_code": ErrorCode.ITEM_NOT_FOUND}
            )
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## 🔐 Environment Variables

### Required Variables:
```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=cab_booking

# Application
APP_NAME=Cab Booking API
APP_VERSION=1.0.0
DEBUG=False

# File Storage
UPLOAD_DIR=/root/chola_cabs_backend_dev/uploads
BASE_URL=https://api.cholacabs.in

# Security (NEW - Required for JWT)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Optional Variables:
```env
# S3 Storage
USE_S3_STORAGE=false
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_ENDPOINT_URL=
S3_BUCKET_NAME=

# FCM
FCM_SERVER_KEY=
MAX_FCM_TOKENS_PER_DRIVER=5

# Razorpay
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
```

---

## 📊 API Response Format

### Success Response:
```json
{
  "data": {...},
  "message": "Success"
}
```

### Error Response:
```json
{
  "detail": "Error message",
  "error_code": 1001
}
```

---

## 🧪 Testing

### Manual Testing:
```bash
# Start server
python -m uvicorn app.main:app --reload

# Test endpoint
curl http://localhost:8000/api/v1/drivers
```

### Using Postman:
- Import `Cab_Booking_API.postman_collection.json`
- Set base URL to `http://localhost:8000` or `https://api.cholacabs.in`

---

## 📝 Documentation

### Available Docs:
- `README.md` - Project overview
- `FOLDER_STRUCTURE.md` - Complete folder structure
- `PROJECT_ANALYSIS.md` - Detailed analysis
- `IMPLEMENTATION_SUMMARY.md` - Implementation progress
- `CURRENT_STRUCTURE.md` - Visual structure
- `QUICK_REFERENCE.md` - This guide

### API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🚨 Common Issues

### 1. Import Errors
```python
# ❌ Wrong
from core.config import settings

# ✅ Correct
from app.core.config import settings
```

### 2. Database Session Not Closed
```python
# ❌ Wrong
db = SessionLocal()
items = db.query(Item).all()
# Forgot to close!

# ✅ Correct
@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items
# Automatically closed by dependency
```

### 3. Missing Environment Variables
```bash
# Error: DB_HOST not set
# Solution: Check .env file exists and has all required variables
```

---

## 🎉 Phase 1 Complete!

### What's New:
- ✅ Centralized configuration
- ✅ Security utilities (JWT, password hashing)
- ✅ Structured logging
- ✅ Constants and enums
- ✅ Shared dependencies

### Next Steps:
- Phase 2: CRUD Layer
- Phase 3: Service Layer
- Phase 4: Split Models & Schemas

---

**Last Updated**: Phase 1 Complete
**Questions?** Check the documentation files or ask!
