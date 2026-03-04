"""
Driver API endpoints - OPTIMIZED
Uses CRUD layer for production-ready performance
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db
from app.crud import crud_driver
from app.schemas import DriverCreate, DriverUpdate, FCMTokenRequest, FCMTokenResponse
from app.core.logging import get_logger
from app.core.constants import ErrorCode, KYCStatus
import uuid

logger = get_logger(__name__)


class ApprovalRequest(BaseModel):
    is_approved: bool


router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("", response_model=None, include_in_schema=False)
@router.get("/", response_model=None)
def get_all_drivers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all drivers with pagination - OPTIMIZED"""
    try:
        from sqlalchemy.orm import joinedload
        from app.models import Driver
        
        # ✅ OPTIMIZED: Using joinedload to get trips in one query for status calculation
        drivers = db.query(Driver).options(joinedload(Driver.trips)).offset(skip).limit(limit).all()
        
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
                "current_status": (
                    "driving" if any(t.trip_status == "STARTED" for t in driver.trips if t.trip_status in ["ASSIGNED", "STARTED"]) else
                    "busy" if any(t.trip_status == "ASSIGNED" for t in driver.trips if t.trip_status in ["ASSIGNED", "STARTED"]) else
                    "offline" if driver.is_available is False else "available"
                ),
                "is_approved": driver.is_approved,
                "errors": driver.errors,
                "created_at": driver.created_at.isoformat() if driver.created_at else None,
                "updated_at": driver.updated_at.isoformat() if driver.updated_at else None,
                "police_verification_url": driver.police_verification_url
            })
        return result
    except Exception as e:
        logger.error(f"Error fetching drivers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch drivers"
        )


@router.get("/locations")
def get_all_driver_locations(db: Session = Depends(get_db)):
    """Get all drivers with their real-time GPS location - ENHANCED with categories"""
    from app.models import Driver, DriverLiveLocation, Trip
    from sqlalchemy import and_
    
    # Query join between Driver and LiveLocation, and outer join with active Trips
    # We only care about trips that are currently ASSIGNED or STARTED
    results = db.query(
        Driver.driver_id,
        Driver.name.label("driver_name"),
        Driver.photo_url,
        Driver.phone_number,
        Driver.is_available,
        DriverLiveLocation.latitude,
        DriverLiveLocation.longitude,
        DriverLiveLocation.last_updated,
        Trip.trip_status.label("active_trip_status")
    ).join(
        DriverLiveLocation, Driver.driver_id == DriverLiveLocation.driver_id
    ).outerjoin(
        Trip, and_(
            Driver.driver_id == Trip.assigned_driver_id,
            Trip.trip_status.in_(["ASSIGNED", "STARTED"])
        )
    ).all()
    
    response = []
    for r in results:
        # Determine status category - Priority: Trip Activity > Manual Toggle
        if r.active_trip_status == "STARTED":
            status = "driving"
        elif r.active_trip_status == "ASSIGNED":
            status = "busy"
        elif r.is_available is False:
            status = "offline"
        else:
            status = "available"
            
        response.append({
            "driver_id": r.driver_id,
            "driver_name": r.driver_name,
            "photo_url": r.photo_url,
            "latitude": float(r.latitude),
            "longitude": float(r.longitude),
            "phone_number": str(r.phone_number),
            "current_status": status,
            "last_updated": r.last_updated.isoformat() if r.last_updated else None
        })
        
    return response


@router.post("/check-phone")
def check_phone_number(payload: dict, db: Session = Depends(get_db)):
    """Check if a phone number is registered as a driver (used for login)"""
    phone_number = payload.get("phone_number")
    if not phone_number:
        raise HTTPException(status_code=400, detail="phone_number is required")
    driver = crud_driver.get_by_phone(db, phone_number=int(phone_number))
    if not driver:
        return {"exists": False, "message": "Phone number not registered"}
    return {
        "exists": True,
        "driver_id": driver.driver_id,
        "name": driver.name,
        "is_approved": driver.is_approved
    }


@router.get("/{driver_id}")
def get_driver_by_id(driver_id: str, db: Session = Depends(get_db)):
    """Get driver by ID - OPTIMIZED"""
    try:
        from sqlalchemy.orm import joinedload
        from app.models import Driver
        
        # ✅ OPTIMIZED: Eager load trips for status calculation
        driver = db.query(Driver).options(joinedload(Driver.trips)).filter(Driver.driver_id == driver_id).first()
        
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
            "current_status": (
                "driving" if any(t.trip_status == "STARTED" for t in driver.trips if t.trip_status in ["ASSIGNED", "STARTED"]) else
                "busy" if any(t.trip_status == "ASSIGNED" for t in driver.trips if t.trip_status in ["ASSIGNED", "STARTED"]) else
                "offline" if driver.is_available is False else "available"
            ),
            "is_approved": driver.is_approved,
            "errors": driver.errors,
            "created_at": driver.created_at.isoformat() if driver.created_at else None,
            "updated_at": driver.updated_at.isoformat() if driver.updated_at else None,
            "police_verification_url": driver.police_verification_url
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
            "is_available": is_available,
            "current_status": "ready" if is_available else "offline"
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
    """Add or update FCM token for driver - simplified to store single token"""
    try:
        # ✅ OPTIMIZED: Using CRUD
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Set current fcm_token
        driver.fcm_tokens = token_request.fcm_token
        db.commit()
        db.refresh(driver)
        
        logger.info(f"FCM token updated for driver {driver_id}")
        
        return FCMTokenResponse(
            message="FCM token updated successfully",
            driver_id=driver_id,
            fcm_tokens=driver.fcm_tokens
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
    """Get FCM token for driver - simplified"""
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
            "fcm_tokens": driver.fcm_tokens or None,
            "tokens_count": 1 if driver.fcm_tokens else 0
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
def remove_fcm_token(driver_id: str, db: Session = Depends(get_db)):
    """Clear (remove) current FCM token for driver"""
    try:
        # ✅ OPTIMIZED: Using CRUD
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        driver.fcm_tokens = None
        db.commit()
        db.refresh(driver)
        logger.info(f"FCM token removed for driver {driver_id}")
        
        return {
            "message": "FCM token removed successfully",
            "driver_id": driver_id
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
    """Clear FCM token for driver (deprecated but kept for compatibility)"""
    return remove_fcm_token(driver_id, db)


@router.patch("/{driver_id}/device-id")
def update_driver_device_id(driver_id: str, payload: dict, db: Session = Depends(get_db)):
    """Update driver's device ID for push notifications and security"""
    device_id = payload.get("device_id")
    if not device_id:
        raise HTTPException(status_code=400, detail="device_id is required")
    
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    driver.device_id = device_id
    db.commit()
    return {"message": "Device ID updated successfully", "driver_id": driver_id, "device_id": device_id}


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





@router.post("/{driver_id}/location")
def update_driver_location(driver_id: str, payload: dict, db: Session = Depends(get_db)):
    """Update driver's real-time GPS location - saves to driver_live_location table"""
    from app.models import DriverLiveLocation
    from decimal import Decimal

    latitude = payload.get("latitude")
    longitude = payload.get("longitude")

    if latitude is None or longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="latitude and longitude are required"
        )

    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")

    # Upsert into driver_live_location
    existing = db.query(DriverLiveLocation).filter(
        DriverLiveLocation.driver_id == driver_id
    ).first()

    if existing:
        existing.latitude = Decimal(str(latitude))
        existing.longitude = Decimal(str(longitude))
    else:
        db.add(DriverLiveLocation(
            driver_id=driver_id,
            latitude=Decimal(str(latitude)),
            longitude=Decimal(str(longitude))
        ))

    db.commit()
    return {"status": "success", "message": "Location updated", "driver_id": driver_id, "latitude": latitude, "longitude": longitude}


@router.get("/{driver_id}/location")
def get_driver_location(driver_id: str, db: Session = Depends(get_db)):
    """Get driver's current real-time GPS location"""
    from app.models import DriverLiveLocation

    location = db.query(DriverLiveLocation).filter(
        DriverLiveLocation.driver_id == driver_id
    ).first()

    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not available for this driver")

    return {
        "driver_id": driver_id,
        "latitude": float(location.latitude),
        "longitude": float(location.longitude),
        "last_updated": location.last_updated.isoformat() if location.last_updated else None
    }