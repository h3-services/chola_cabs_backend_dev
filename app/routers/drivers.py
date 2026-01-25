"""
Driver API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Driver, Vehicle, Trip
from app.schemas import DriverCreate, DriverUpdate, DriverResponse, FCMTokenRequest, FCMTokenResponse

class ApprovalRequest(BaseModel):
    is_approved: bool

router = APIRouter(prefix="/drivers", tags=["drivers"])

@router.get("/", response_model=None)
def get_all_drivers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all drivers with pagination"""
    drivers = db.query(Driver).offset(skip).limit(limit).all()
    # Convert to dict to avoid validation issues
    result = []
    for driver in drivers:
        result.append({
            "driver_id": driver.driver_id,
            "name": driver.name,
            "phone_number": str(driver.phone_number),
            "email": driver.email,
            "kyc_verified": driver.kyc_verified,
            "primary_location": driver.primary_location,
            "photo_url": driver.photo_url,
            "aadhar_url": driver.aadhar_url,
            "licence_url": driver.licence_url,
            "licence_number": driver.licence_number,
            "aadhar_number": driver.aadhar_number,
            "licence_expiry": driver.licence_expiry.isoformat() if driver.licence_expiry else None,
            "wallet_balance": float(driver.wallet_balance) if driver.wallet_balance else 0.0,
            "device_id": driver.device_id,
            "is_available": driver.is_available,
            "is_approved": driver.is_approved,
            "errors": driver.errors,
            "created_at": driver.created_at.isoformat() if driver.created_at else None,
            "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
        })
    return result

@router.get("/{driver_id}")
def get_driver_by_id(driver_id: str, db: Session = Depends(get_db)):
    """Get driver by ID"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    return {
        "driver_id": driver.driver_id,
        "name": driver.name,
        "phone_number": str(driver.phone_number),
        "email": driver.email,
        "kyc_verified": driver.kyc_verified,
        "primary_location": driver.primary_location,
        "photo_url": driver.photo_url,
        "aadhar_url": driver.aadhar_url,
        "licence_url": driver.licence_url,
        "licence_number": driver.licence_number,
        "aadhar_number": driver.aadhar_number,
        "licence_expiry": driver.licence_expiry.isoformat() if driver.licence_expiry else None,
        "wallet_balance": float(driver.wallet_balance) if driver.wallet_balance else 0.0,
        "device_id": driver.device_id,
        "is_available": driver.is_available,
        "is_approved": driver.is_approved,
        "errors": driver.errors,
        "created_at": driver.created_at.isoformat() if driver.created_at else None,
        "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    """Create a new driver"""
    # Check if phone number already exists
    existing_driver = db.query(Driver).filter(Driver.phone_number == driver.phone_number).first()
    if existing_driver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Generate UUID for driver_id
    import uuid
    driver_data = driver.dict()
    driver_data['driver_id'] = str(uuid.uuid4())
    
    db_driver = Driver(**driver_data)
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    
    return {
        "driver_id": db_driver.driver_id,
        "name": db_driver.name,
        "phone_number": str(db_driver.phone_number),
        "email": db_driver.email,
        "message": "Driver created successfully"
    }

@router.put("/{driver_id}")
def update_driver(
    driver_id: str, 
    driver_update: DriverUpdate, 
    db: Session = Depends(get_db)
):
    """Update driver information"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Update only provided fields
    update_data = driver_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(driver, field, value)
    
    db.commit()
    db.refresh(driver)
    return driver

@router.patch("/{driver_id}/availability")
def update_driver_availability(
    driver_id: str, 
    is_available: bool, 
    db: Session = Depends(get_db)
):
    """Update driver availability status"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    driver.is_available = is_available
    db.commit()
    db.refresh(driver)
    
    return {
        "message": f"Driver availability updated to {'available' if is_available else 'unavailable'}",
        "driver_id": driver_id,
        "is_available": is_available
    }

@router.patch("/{driver_id}/kyc-status")
def update_kyc_status(
    driver_id: str,
    kyc_status: str,
    db: Session = Depends(get_db)
):
    """Admin endpoint to approve/reject driver KYC"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if kyc_status not in ["pending", "approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid KYC status. Must be: pending, approved, or rejected"
        )
    
    driver.kyc_verified = kyc_status
    db.commit()
    db.refresh(driver)
    
    return {
        "message": f"Driver KYC status updated to {kyc_status}",
        "driver_id": driver_id,
        "kyc_verified": kyc_status
    }

@router.patch("/{driver_id}/approve")
def approve_driver(
    driver_id: str,
    is_approved: bool = Query(..., description="Set to true to approve driver, false to disapprove"),
    db: Session = Depends(get_db)
):
    """Admin endpoint to approve/disapprove driver"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    driver.is_approved = is_approved
    db.commit()
    db.refresh(driver)
    
    status_text = "approved" if is_approved else "disapproved"
    return {
        "message": f"Driver {status_text} successfully",
        "driver_id": driver_id,
        "is_approved": is_approved
    }

@router.get("/{driver_id}/wallet-balance")
def get_driver_wallet_balance(driver_id: str, db: Session = Depends(get_db)):
    """Get driver's current wallet balance"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    return {
        "driver_id": driver_id,
        "wallet_balance": float(driver.wallet_balance) if driver.wallet_balance else 0.0,
        "name": driver.name
    }

@router.patch("/{driver_id}/wallet-balance")
def update_wallet_balance(
    driver_id: str,
    new_balance: float,
    db: Session = Depends(get_db)
):
    """Direct wallet balance update (Admin only)"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    old_balance = float(driver.wallet_balance) if driver.wallet_balance else 0.0
    driver.wallet_balance = new_balance
    db.commit()
    db.refresh(driver)
    
    return {
        "message": "Wallet balance updated successfully",
        "driver_id": driver_id,
        "old_balance": old_balance,
        "new_balance": new_balance
    }

@router.delete("/{driver_id}")
def delete_driver(driver_id: str, db: Session = Depends(get_db)):
    """Delete a driver"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    db.delete(driver)
    db.commit()
    
    return {
        "message": "Driver deleted successfully",
        "driver_id": driver_id
    }

# FCM Token Management
@router.post("/{driver_id}/fcm-token", response_model=FCMTokenResponse)
def add_fcm_token(driver_id: str, token_request: FCMTokenRequest, db: Session = Depends(get_db)):
    """Add or update FCM token for driver with FIFO limit"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Get existing tokens or initialize empty list
    existing_tokens = driver.fcm_tokens or []
    
    # Remove token if already exists (to avoid duplicates)
    if token_request.fcm_token in existing_tokens:
        existing_tokens.remove(token_request.fcm_token)
    
    # Add new token to end (most recent)
    existing_tokens.append(token_request.fcm_token)
    
    # FIFO: Keep only last 20 tokens (remove oldest)
    MAX_TOKENS = 20
    if len(existing_tokens) > MAX_TOKENS:
        existing_tokens = existing_tokens[-MAX_TOKENS:]
    
    driver.fcm_tokens = existing_tokens
    db.commit()
    db.refresh(driver)
    
    return FCMTokenResponse(
        message="FCM token added successfully",
        driver_id=driver_id,
        tokens_count=len(existing_tokens)
    )

@router.get("/{driver_id}/fcm-tokens")
def get_fcm_tokens(driver_id: str, db: Session = Depends(get_db)):
    """Get all FCM tokens for driver"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    return {
        "driver_id": driver_id,
        "fcm_tokens": driver.fcm_tokens or [],
        "tokens_count": len(driver.fcm_tokens) if driver.fcm_tokens else 0
    }

@router.delete("/{driver_id}/fcm-token")
def remove_fcm_token(driver_id: str, token_request: FCMTokenRequest, db: Session = Depends(get_db)):
    """Remove specific FCM token for driver"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    existing_tokens = driver.fcm_tokens or []
    
    if token_request.fcm_token in existing_tokens:
        existing_tokens.remove(token_request.fcm_token)
        driver.fcm_tokens = existing_tokens
        db.commit()
        db.refresh(driver)
        message = "FCM token removed successfully"
    else:
        message = "FCM token not found"
    
    return {
        "message": message,
        "driver_id": driver_id,
        "tokens_count": len(existing_tokens)
    }

@router.delete("/{driver_id}/fcm-tokens/all")
def clear_all_fcm_tokens(driver_id: str, db: Session = Depends(get_db)):
    """Clear all FCM tokens for driver"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    driver.fcm_tokens = []
    db.commit()
    db.refresh(driver)
    
    return {
        "message": "All FCM tokens cleared successfully",
        "driver_id": driver_id,
        "tokens_count": 0
    }
        "message": "Driver deleted successfully",
        "driver_id": driver_id
    }

@router.patch("/{driver_id}/clear-errors")
def clear_driver_errors(driver_id: str, db: Session = Depends(get_db)):
    """Clear all errors for driver"""
    from sqlalchemy.orm.attributes import flag_modified
    
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    driver.errors = None
    driver.is_approved = True
    flag_modified(driver, 'errors')
    db.commit()
    
    return {"message": "Driver errors cleared", "driver_id": driver_id}