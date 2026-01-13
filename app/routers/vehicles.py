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

@router.get("/", response_model=List[VehicleResponse])
def get_all_vehicles(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all vehicles with pagination"""
    vehicles = db.query(Vehicle).offset(skip).limit(limit).all()
    return vehicles

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_details(vehicle_id: int, db: Session = Depends(get_db)):
    """Get vehicle details by ID"""
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    return vehicle

@router.get("/driver/{driver_id}", response_model=List[VehicleResponse])
def get_vehicles_by_driver(driver_id: int, db: Session = Depends(get_db)):
    """Get all vehicles belonging to a specific driver"""
    # Check if driver exists
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    vehicles = db.query(Vehicle).filter(Vehicle.driver_id == driver_id).all()
    return vehicles

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def add_vehicle_to_driver(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """Add a new vehicle to a driver"""
    # Check if driver exists
    driver = db.query(Driver).filter(Driver.driver_id == vehicle.driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Check if vehicle number already exists
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
    return db_vehicle

@router.put("/{vehicle_id}", response_model=VehicleResponse)
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
    
    # Update only provided fields
    update_data = vehicle_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    
    db.commit()
    db.refresh(vehicle)
    return vehicle

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