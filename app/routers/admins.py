"""
Admin Router - Authentication and Management
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin
from app.schemas import (
    AdminCreate, AdminUpdate, AdminResponse,
    AdminLoginRequest, AdminVerifyOTPRequest, AdminLoginResponse
)
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/admins", tags=["admins"])

# TODO: Implement OTP service
# TODO: Implement JWT authentication
# TODO: Implement role-based access control middleware

@router.get("/", response_model=List[AdminResponse])
def get_all_admins(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all admins (SUPER_ADMIN only)"""
    try:
        admins = db.query(Admin).offset(skip).limit(limit).all()
        return admins
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/{admin_id}", response_model=AdminResponse)
def get_admin_by_id(admin_id: str, db: Session = Depends(get_db)):
    """Get admin by ID"""
    try:
        admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        return admin
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AdminResponse)
def create_admin(
    admin: AdminCreate,
    db: Session = Depends(get_db)
    # TODO: Add current_admin: Admin = Depends(get_current_super_admin)
):
    """Create new admin (SUPER_ADMIN only)"""
    try:
        # Check if phone number already exists
        existing = db.query(Admin).filter(Admin.phone_number == admin.phone_number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Create new admin
        db_admin = Admin(
            admin_id=str(uuid.uuid4()),
            name=admin.name,
            phone_number=admin.phone_number,
            role=admin.role.value,
            is_active=True,
            # created_by=current_admin.admin_id  # TODO: Uncomment when auth is implemented
        )
        
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        
        return db_admin
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.patch("/{admin_id}", response_model=AdminResponse)
def update_admin(
    admin_id: str,
    admin_update: AdminUpdate,
    db: Session = Depends(get_db)
    # TODO: Add current_admin: Admin = Depends(get_current_admin)
):
    """Update admin details"""
    try:
        admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        # Update fields
        update_data = admin_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "role":
                setattr(admin, field, value.value)
            else:
                setattr(admin, field, value)
        
        db.commit()
        db.refresh(admin)
        
        return admin
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete("/{admin_id}")
def delete_admin(
    admin_id: str,
    db: Session = Depends(get_db)
    # TODO: Add current_admin: Admin = Depends(get_current_super_admin)
):
    """Delete admin (SUPER_ADMIN only)"""
    try:
        admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        # Prevent deleting yourself
        # if admin.admin_id == current_admin.admin_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Cannot delete yourself"
        #     )
        
        db.delete(admin)
        db.commit()
        
        return {"message": "Admin deleted successfully", "admin_id": admin_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/phone/{phone_number}", response_model=AdminResponse)
def get_admin_by_phone(phone_number: int, db: Session = Depends(get_db)):
    """Get admin by phone number"""
    try:
        admin = db.query(Admin).filter(Admin.phone_number == phone_number).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        return admin
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
