"""
Driver API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Driver, Vehicle, Trip
from app.schemas import DriverCreate, DriverUpdate, DriverResponse

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
            "wallet_balance": float(driver.wallet_balance) if driver.wallet_balance else 0.0,
            "is_available": driver.is_available,
            "is_approved": driver.is_approved,
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
        "wallet_balance": float(driver.wallet_balance) if driver.wallet_balance else 0.0,
        "is_available": driver.is_available,
        "is_approved": driver.is_approved,
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