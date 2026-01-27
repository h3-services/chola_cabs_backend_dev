"""
API Dependencies
Shared dependencies for API endpoints
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.security import get_current_user, get_current_admin, get_current_super_admin


def get_db() -> Generator:
    """
    Database session dependency
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Re-export authentication dependencies for convenience
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_admin",
    "get_current_super_admin"
]
