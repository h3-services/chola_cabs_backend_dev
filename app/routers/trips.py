"""
Trip API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models import Trip, Driver, TripDriverRequest, VehicleTariffConfig
from app.schemas import TripCreate, TripUpdate, TripResponse, TripDriverRequestCreate, TripDriverRequestUpdate
from decimal import Decimal

router = APIRouter(prefix="/trips", tags=["trips"])

@router.get("/", response_model=List[TripResponse])
def get_all_trips(
    skip: int = 0, 
    limit: int = 100, 
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """Get all trips with optional status filter"""
    query = db.query(Trip)
    
    if status_filter:
        query = query.filter(Trip.trip_status == status_filter)
    
    trips = query.offset(skip).limit(limit).all()
    return trips

@router.get("/{trip_id}", response_model=TripResponse)
def get_trip_details(trip_id: int, db: Session = Depends(get_db)):
    """Get trip details by ID"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    return trip

@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    """Create a new trip"""
    # Calculate fare based on tariff configuration
    tariff = db.query(VehicleTariffConfig).filter(
        and_(
            VehicleTariffConfig.vehicle_type == trip.vehicle_type,
            VehicleTariffConfig.is_active == True
        )
    ).first()
    
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No active tariff found for vehicle type: {trip.vehicle_type}"
        )
    
    # Create trip with calculated fare (basic calculation)
    db_trip = Trip(**trip.dict())
    
    # Set initial fare based on trip type and minimum km
    if trip.trip_type == "one_way":
        db_trip.fare = tariff.one_way_per_km * tariff.one_way_min_km + tariff.driver_allowance
    else:  # round_trip
        db_trip.fare = tariff.round_trip_per_km * tariff.round_trip_min_km + tariff.driver_allowance
    
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: int, 
    trip_update: TripUpdate, 
    db: Session = Depends(get_db)
):
    """Update trip information"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # Update only provided fields
    update_data = trip_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trip, field, value)
    
    db.commit()
    db.refresh(trip)
    return trip

@router.patch("/{trip_id}/assign-driver/{driver_id}")
def assign_driver_to_trip(
    trip_id: int, 
    driver_id: int, 
    db: Session = Depends(get_db)
):
    """Assign a driver to a trip"""
    # Check if trip exists
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # Check if driver exists and is available
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    if not driver.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver is not available"
        )
    
    if not driver.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver is not approved"
        )
    
    # Assign driver to trip
    trip.assigned_driver_id = driver_id
    trip.trip_status = "assigned"
    trip.is_manual_assignment = True
    
    # Make driver unavailable
    driver.is_available = False
    
    db.commit()
    db.refresh(trip)
    
    return {
        "message": "Driver assigned to trip successfully",
        "trip_id": trip_id,
        "driver_id": driver_id,
        "driver_name": driver.name,
        "trip_status": trip.trip_status
    }

@router.patch("/{trip_id}/status")
def update_trip_status(
    trip_id: int, 
    new_status: str, 
    db: Session = Depends(get_db)
):
    """Update trip status"""
    valid_statuses = ["pending", "assigned", "started", "completed", "cancelled"]
    
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Valid statuses: {', '.join(valid_statuses)}"
        )
    
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    old_status = trip.trip_status
    trip.trip_status = new_status
    
    # If trip is completed or cancelled, make driver available again
    if new_status in ["completed", "cancelled"] and trip.assigned_driver_id:
        driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
        if driver:
            driver.is_available = True
    
    db.commit()
    db.refresh(trip)
    
    return {
        "message": f"Trip status updated from {old_status} to {new_status}",
        "trip_id": trip_id,
        "old_status": old_status,
        "new_status": new_status
    }

@router.post("/{trip_id}/driver-requests", status_code=status.HTTP_201_CREATED)
def create_driver_request(
    trip_id: int,
    driver_id: int,
    db: Session = Depends(get_db)
):
    """Create a driver request for a trip"""
    # Check if trip exists
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # Check if driver exists
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Check if request already exists
    existing_request = db.query(TripDriverRequest).filter(
        and_(
            TripDriverRequest.trip_id == trip_id,
            TripDriverRequest.driver_id == driver_id
        )
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver request already exists for this trip"
        )
    
    # Create driver request
    driver_request = TripDriverRequest(
        trip_id=trip_id,
        driver_id=driver_id,
        status="pending"
    )
    
    db.add(driver_request)
    db.commit()
    db.refresh(driver_request)
    
    return {
        "message": "Driver request created successfully",
        "request_id": driver_request.request_id,
        "trip_id": trip_id,
        "driver_id": driver_id,
        "status": "pending"
    }

@router.get("/driver/{driver_id}", response_model=List[TripResponse])
def get_trips_by_driver(driver_id: int, db: Session = Depends(get_db)):
    """Get all trips assigned to a specific driver"""
    # Check if driver exists
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    trips = db.query(Trip).filter(Trip.assigned_driver_id == driver_id).all()
    return trips

@router.delete("/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    """Delete a trip"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # If trip has assigned driver, make them available again
    if trip.assigned_driver_id:
        driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
        if driver:
            driver.is_available = True
    
    db.delete(trip)
    db.commit()
    
    return {
        "message": "Trip deleted successfully",
        "trip_id": trip_id
    }