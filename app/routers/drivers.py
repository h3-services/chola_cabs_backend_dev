"""
Driver API endpoints - OPTIMIZED
Uses CRUD layer for production-ready performance
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db
from app.crud import crud_driver, crud_driver_location
from app.schemas import DriverCreate, DriverUpdate, FCMTokenRequest, FCMTokenResponse, DriverLocationUpdate, DriverLocationResponse, DriverLocationWithDetails
from app.core.logging import get_logger
from app.core.constants import ErrorCode, KYCStatus
import uuid

logger = get_logger(__name__)


class ApprovalRequest(BaseModel):
    is_approved: bool


router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("/", response_model=None)
def get_all_drivers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all drivers with pagination - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD layer
        drivers = crud_driver.get_multi(db, skip=skip, limit=limit)
        
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
                "fcm_tokens": driver.fcm_tokens,
                "is_available": driver.is_available,
                "is_approved": driver.is_approved,
                "errors": driver.errors,
                "created_at": driver.created_at.isoformat() if driver.created_at else None,
                "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
            })
        return result
    except Exception as e:
        logger.error(f"Error fetching drivers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch drivers"
        )


@router.get("/locations/map", response_model=List[DriverLocationWithDetails])
def get_all_active_driver_locations(db: Session = Depends(get_db)):
    """Get all active driver locations for map view"""
    try:
        locations = crud_driver_location.driver_location.get_all(db)
        
        result = []
        for loc in locations:
            # Safely get driver details if relationship exists
            driver_name = loc.driver.name if loc.driver else "Unknown"
            phone = str(loc.driver.phone_number) if loc.driver else None
            is_available = loc.driver.is_available if loc.driver else False
            
            # Try to find vehicle if possible (optional)
            # This might need another query or assume relationship is loaded?
            # Driver model has vehicles relationship.
            vehicle_type = None
            if loc.driver and loc.driver.vehicles:
                # Get the first approved vehicle or just first
                vehicle = next((v for v in loc.driver.vehicles if v.vehicle_approved), None)
                if not vehicle and loc.driver.vehicles:
                    vehicle = loc.driver.vehicles[0]
                if vehicle:
                    vehicle_type = vehicle.vehicle_type

            result.append({
                "driver_id": loc.driver_id,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "last_updated": loc.last_updated,
                "driver_name": driver_name,
                "phone_number": phone,
                "is_available": is_available,
                "vehicle_type": vehicle_type
            })
            
        return result
    except Exception as e:
        logger.error(f"Error fetching map locations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch map locations"
        )


@router.get("/{driver_id}")
def get_driver_by_id(driver_id: str, db: Session = Depends(get_db)):
    """Get driver by ID - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD layer
        driver = crud_driver.get(db, id=driver_id)
        
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": ErrorCode.DRIVER_NOT_FOUND, "message": "Driver not found"}
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
            "fcm_tokens": driver.fcm_tokens,
            "is_available": driver.is_available,
            "is_approved": driver.is_approved,
            "errors": driver.errors,
            "created_at": driver.created_at.isoformat() if driver.created_at else None,
            "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching driver {driver_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch driver"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    """Create a new driver - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Check if phone exists using CRUD
        existing_driver = crud_driver.get_by_phone(db, phone_number=driver.phone_number)
        if existing_driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Generate UUID for driver_id
        driver_data = driver.dict()
        driver_data['driver_id'] = str(uuid.uuid4())
        
        # ✅ OPTIMIZED: Create using CRUD (but need to handle UUID manually)
        from app.models import Driver
        db_driver = Driver(**driver_data)
        db.add(db_driver)
        db.commit()
        db.refresh(db_driver)
        
        logger.info(f"Driver created: {db_driver.driver_id}")
        
        return {
            "driver_id": db_driver.driver_id,
            "name": db_driver.name,
            "phone_number": str(db_driver.phone_number),
            "email": db_driver.email,
            "message": "Driver created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating driver: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create driver"
        )


@router.put("/{driver_id}")
def update_driver(
    driver_id: str, 
    driver_update: DriverUpdate, 
    db: Session = Depends(get_db)
):
    """Update driver information - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Get driver using CRUD
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # ✅ OPTIMIZED: Update using CRUD
        updated_driver = crud_driver.update(db, db_obj=driver, obj_in=driver_update)
        logger.info(f"Driver updated: {driver_id}")
        
        return updated_driver
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating driver {driver_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update driver"
        )


@router.patch("/{driver_id}/availability")
def update_driver_availability(
    driver_id: str, 
    is_available: bool, 
    db: Session = Depends(get_db)
):
    """Update driver availability status - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Specialized method
        driver = crud_driver.update_availability(db, driver_id, is_available)
        
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        logger.info(f"Driver {driver_id} availability updated to {is_available}")
        
        return {
            "message": f"Driver availability updated to {'available' if is_available else 'unavailable'}",
            "driver_id": driver_id,
            "is_available": is_available
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating availability: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update availability"
        )


@router.patch("/{driver_id}/kyc-status")
def update_kyc_status(
    driver_id: str,
    kyc_status: str,
    db: Session = Depends(get_db)
):
    """Admin endpoint to approve/reject driver KYC - OPTIMIZED"""
    try:
        if kyc_status not in ["pending", "approved", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid KYC status. Must be: pending, approved, or rejected"
            )
        
        # ✅ OPTIMIZED: Specialized method
        driver = crud_driver.update_kyc_status(db, driver_id, kyc_status)
        
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        logger.info(f"Driver {driver_id} KYC status updated to {kyc_status}")
        
        return {
            "message": f"Driver KYC status updated to {kyc_status}",
            "driver_id": driver_id,
            "kyc_verified": kyc_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating KYC status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update KYC status"
        )


@router.patch("/{driver_id}/approve")
def approve_driver(
    driver_id: str,
    is_approved: bool = Query(..., description="Set to true to approve driver, false to disapprove"),
    db: Session = Depends(get_db)
):
    """Admin endpoint to approve/disapprove driver - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Get and update using CRUD
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        driver.is_approved = is_approved
        db.commit()
        db.refresh(driver)
        
        status_text = "approved" if is_approved else "disapproved"
        logger.info(f"Driver {driver_id} {status_text}")
        
        return {
            "message": f"Driver {status_text} successfully",
            "driver_id": driver_id,
            "is_approved": is_approved
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving driver: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve driver"
        )


@router.get("/{driver_id}/wallet-balance")
def get_driver_wallet_balance(driver_id: str, db: Session = Depends(get_db)):
    """Get driver's current wallet balance - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD
        driver = crud_driver.get(db, id=driver_id)
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching wallet balance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wallet balance"
        )


@router.patch("/{driver_id}/wallet-balance")
def update_wallet_balance(
    driver_id: str,
    new_balance: float,
    db: Session = Depends(get_db)
):
    """Direct wallet balance update (Admin only) - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Specialized method
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        old_balance = float(driver.wallet_balance) if driver.wallet_balance else 0.0
        driver = crud_driver.update_wallet_balance(db, driver_id, new_balance)
        
        logger.info(f"Wallet balance updated for driver {driver_id}: {old_balance} -> {new_balance}")
        
        return {
            "message": "Wallet balance updated successfully",
            "driver_id": driver_id,
            "old_balance": old_balance,
            "new_balance": new_balance
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating wallet balance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update wallet balance"
        )


@router.delete("/{driver_id}")
def delete_driver(driver_id: str, db: Session = Depends(get_db)):
    """Delete a driver - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD
        driver = crud_driver.delete(db, id=driver_id)
        
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        logger.info(f"Driver deleted: {driver_id}")
        
        return {
            "message": "Driver deleted successfully",
            "driver_id": driver_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting driver: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete driver"
        )


# FCM Token Management
@router.post("/{driver_id}/fcm-token", response_model=FCMTokenResponse)
def add_fcm_token(driver_id: str, token_request: FCMTokenRequest, db: Session = Depends(get_db)):
    """Add or update FCM token for driver with FIFO limit - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD
        driver = crud_driver.get(db, id=driver_id)
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
        
        logger.info(f"FCM token added for driver {driver_id}")
        
        return FCMTokenResponse(
            message="FCM token added successfully",
            driver_id=driver_id,
            fcm_tokens=existing_tokens
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding FCM token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add FCM token"
        )


@router.get("/{driver_id}/fcm-tokens")
def get_fcm_tokens(driver_id: str, db: Session = Depends(get_db)):
    """Get all FCM tokens for driver - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD
        driver = crud_driver.get(db, id=driver_id)
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching FCM tokens: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch FCM tokens"
        )


@router.delete("/{driver_id}/fcm-token")
def remove_fcm_token(driver_id: str, token_request: FCMTokenRequest, db: Session = Depends(get_db)):
    """Remove specific FCM token for driver - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD
        driver = crud_driver.get(db, id=driver_id)
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
            logger.info(f"FCM token removed for driver {driver_id}")
        else:
            message = "FCM token not found"
        
        return {
            "message": message,
            "driver_id": driver_id,
            "tokens_count": len(existing_tokens)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing FCM token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove FCM token"
        )


@router.delete("/{driver_id}/fcm-tokens/all")
def clear_all_fcm_tokens(driver_id: str, db: Session = Depends(get_db)):
    """Clear all FCM tokens for driver - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        driver.fcm_tokens = []
        db.commit()
        db.refresh(driver)
        
        logger.info(f"All FCM tokens cleared for driver {driver_id}")
        
        return {
            "message": "All FCM tokens cleared successfully",
            "driver_id": driver_id,
            "tokens_count": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing FCM tokens: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear FCM tokens"
        )


@router.patch("/{driver_id}/clear-errors")
def clear_driver_errors(driver_id: str, db: Session = Depends(get_db)):
    """Clear all errors for driver - OPTIMIZED"""
    try:
        from sqlalchemy.orm.attributes import flag_modified
        
        # ✅ OPTIMIZED: Using CRUD
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        driver.errors = None
        driver.is_approved = True
        flag_modified(driver, 'errors')
        db.commit()
        
        logger.info(f"Errors cleared for driver {driver_id}")
        
        return {"message": "Driver errors cleared", "driver_id": driver_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing driver errors: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear driver errors"
        )


@router.post("/{driver_id}/location", response_model=DriverLocationResponse)
def update_driver_location(
    driver_id: str,
    location: DriverLocationUpdate,
    db: Session = Depends(get_db)
):
    """Update driver's real-time location (High Frequency)"""
    try:
        # Check driver exists first (read-only check from drivers table)
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Update ONLY the location table
        db_location = crud_driver_location.driver_location.update(db, driver_id, location)
        
        return db_location
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating driver {driver_id} location: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update driver location"
        )


@router.get("/{driver_id}/location", response_model=DriverLocationResponse)
def get_driver_location(driver_id: str, db: Session = Depends(get_db)):
    """Get driver's real-time location"""
    try:
        # Check driver exists
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
            
        location = crud_driver_location.driver_location.get(db, driver_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found for this driver"
            )
            
        return location
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching driver {driver_id} location: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch driver location"
        )