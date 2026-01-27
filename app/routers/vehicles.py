"""
Vehicle API endpoints - OPTIMIZED
Uses CRUD layer for production-ready performance
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import crud_vehicle, crud_driver
from app.schemas import VehicleCreate, VehicleUpdate, VehicleResponse
from app.core.logging import get_logger
from app.core.constants import ErrorCode
import uuid

logger = get_logger(__name__)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=List[VehicleResponse])
def get_all_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all vehicles with pagination - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD layer
        vehicles = crud_vehicle.get_multi(db, skip=skip, limit=limit)
        return vehicles
    except Exception as e:
        logger.error(f"Error fetching vehicles: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch vehicles"
        )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_by_id(vehicle_id: str, db: Session = Depends(get_db)):
    """Get vehicle by ID - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD layer
        vehicle = crud_vehicle.get(db, id=vehicle_id)
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": ErrorCode.VEHICLE_NOT_FOUND, "message": "Vehicle not found"}
            )
        
        return vehicle
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vehicle {vehicle_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch vehicle"
        )


@router.get("/driver/{driver_id}", response_model=List[VehicleResponse])
def get_vehicles_by_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get all vehicles for a specific driver - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Check driver exists
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # ✅ OPTIMIZED: Driver-specific query
        vehicles = crud_vehicle.get_by_driver(db, driver_id=driver_id)
        return vehicles
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vehicles for driver {driver_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch driver vehicles"
        )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VehicleResponse)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """Create a new vehicle - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Check driver exists
        driver = crud_driver.get(db, id=vehicle.driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # ✅ OPTIMIZED: Check vehicle number doesn't exist
        existing_vehicle = crud_vehicle.get_by_number(db, vehicle_number=vehicle.vehicle_number)
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle number already registered"
            )
        
        # Generate UUID
        vehicle_data = vehicle.dict()
        vehicle_data['vehicle_id'] = str(uuid.uuid4())
        
        # Create vehicle
        from app.models import Vehicle
        db_vehicle = Vehicle(**vehicle_data)
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        
        logger.info(f"Vehicle created: {db_vehicle.vehicle_id}")
        
        return db_vehicle
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vehicle: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create vehicle"
        )


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    db: Session = Depends(get_db)
):
    """Update vehicle information - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Get vehicle using CRUD
        vehicle = crud_vehicle.get(db, id=vehicle_id)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # ✅ OPTIMIZED: Update using CRUD
        updated_vehicle = crud_vehicle.update(db, db_obj=vehicle, obj_in=vehicle_update)
        logger.info(f"Vehicle updated: {vehicle_id}")
        
        return updated_vehicle
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vehicle {vehicle_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update vehicle"
        )


@router.patch("/{vehicle_id}/approve")
def approve_vehicle(
    vehicle_id: str,
    is_approved: bool,
    db: Session = Depends(get_db)
):
    """Approve or disapprove vehicle - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Get vehicle using CRUD
        vehicle = crud_vehicle.get(db, id=vehicle_id)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        vehicle.vehicle_approved = is_approved
        db.commit()
        db.refresh(vehicle)
        
        status_text = "approved" if is_approved else "disapproved"
        logger.info(f"Vehicle {vehicle_id} {status_text}")
        
        return {
            "message": f"Vehicle {status_text} successfully",
            "vehicle_id": vehicle_id,
            "vehicle_approved": is_approved
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving vehicle: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve vehicle"
        )


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Delete a vehicle - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Using CRUD
        vehicle = crud_vehicle.delete(db, id=vehicle_id)
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        logger.info(f"Vehicle deleted: {vehicle_id}")
        
        return {
            "message": "Vehicle deleted successfully",
            "vehicle_id": vehicle_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting vehicle: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete vehicle"
        )