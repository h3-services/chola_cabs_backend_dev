"""
Vehicle API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Vehicle, Driver, Trip
from app.schemas import VehicleCreate, VehicleUpdate, VehicleResponse

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/", response_model=None)
def get_all_vehicles(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all vehicles with pagination"""
    vehicles = db.query(Vehicle).offset(skip).limit(limit).all()
    result = []
    for vehicle in vehicles:
        result.append({
            "vehicle_id": vehicle.vehicle_id,
            "driver_id": vehicle.driver_id,
            "vehicle_type": vehicle.vehicle_type,
            "vehicle_brand": vehicle.vehicle_brand,
            "vehicle_model": vehicle.vehicle_model,
            "vehicle_number": vehicle.vehicle_number,
            "vehicle_color": vehicle.vehicle_color,
            "seating_capacity": vehicle.seating_capacity,
            "vehicle_approved": vehicle.vehicle_approved,
            "created_at": vehicle.created_at.isoformat() if vehicle.created_at else None,
            "updated_at": vehicle.updated_at.isoformat() if vehicle.updated_at else None
        })
    return result

@router.get("/{vehicle_id}")
def get_vehicle_details(vehicle_id: int, db: Session = Depends(get_db)):
    """Get vehicle details by ID"""
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    return {
        "vehicle_id": vehicle.vehicle_id,
        "driver_id": vehicle.driver_id,
        "vehicle_type": vehicle.vehicle_type,
        "vehicle_brand": vehicle.vehicle_brand,
        "vehicle_model": vehicle.vehicle_model,
        "vehicle_number": vehicle.vehicle_number,
        "vehicle_color": vehicle.vehicle_color,
        "seating_capacity": vehicle.seating_capacity,
        "vehicle_approved": vehicle.vehicle_approved,
        "created_at": vehicle.created_at.isoformat() if vehicle.created_at else None,
        "updated_at": vehicle.updated_at.isoformat() if vehicle.updated_at else None
    }

@router.get("/driver/{driver_id}")
def get_vehicles_by_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get all vehicles belonging to a specific driver"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    vehicles = db.query(Vehicle).filter(Vehicle.driver_id == driver_id).all()
    result = []
    for vehicle in vehicles:
        result.append({
            "vehicle_id": vehicle.vehicle_id,
            "driver_id": vehicle.driver_id,
            "vehicle_type": vehicle.vehicle_type,
            "vehicle_brand": vehicle.vehicle_brand,
            "vehicle_model": vehicle.vehicle_model,
            "vehicle_number": vehicle.vehicle_number,
            "vehicle_approved": vehicle.vehicle_approved
        })
    return result

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_vehicle_to_driver(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """Add a new vehicle to a driver"""
    driver = db.query(Driver).filter(Driver.driver_id == vehicle.driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    existing_vehicle = db.query(Vehicle).filter(Vehicle.vehicle_number == vehicle.vehicle_number).first()
    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle number already registered"
        )
    
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    
    return {
        "vehicle_id": db_vehicle.vehicle_id,
        "driver_id": db_vehicle.driver_id,
        "vehicle_number": db_vehicle.vehicle_number,
        "message": "Vehicle created successfully"
    }

@router.put("/{vehicle_id}")
def update_vehicle(
    vehicle_id: int, 
    vehicle_update: VehicleUpdate, 
    db: Session = Depends(get_db)
):
    """Update vehicle information"""
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    update_data = vehicle_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    
    db.commit()
    db.refresh(vehicle)
    
    return {
        "vehicle_id": vehicle.vehicle_id,
        "message": "Vehicle updated successfully"
    }

@router.patch("/{vehicle_id}/approve")
def approve_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Approve a vehicle for operations"""
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    vehicle.vehicle_approved = True
    db.commit()
    db.refresh(vehicle)
    
    return {
        "message": "Vehicle approved successfully",
        "vehicle_id": vehicle_id,
        "vehicle_number": vehicle.vehicle_number,
        "approved": True
    }

@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Delete a vehicle"""
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    db.delete(vehicle)
    db.commit()
    
    return {
        "message": "Vehicle deleted successfully",
        "vehicle_id": vehicle_id,
        "vehicle_number": vehicle.vehicle_number
    }