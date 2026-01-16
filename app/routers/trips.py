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

@router.get("/available")
def get_available_trips(db: Session = Depends(get_db)):
    """Get all available trips (OPEN status, no driver assigned)"""
    trips = db.query(Trip).filter(
        Trip.trip_status == "OPEN",
        Trip.assigned_driver_id == None
    ).all()
    
    result = []
    for trip in trips:
        result.append({
            "trip_id": trip.trip_id,
            "customer_name": trip.customer_name,
            "pickup_address": trip.pickup_address,
            "drop_address": trip.drop_address,
            "trip_type": trip.trip_type,
            "vehicle_type": trip.vehicle_type,
            "passenger_count": trip.passenger_count,
            "fare": float(trip.fare) if trip.fare else None,
            "planned_start_at": trip.planned_start_at.isoformat() if trip.planned_start_at else None,
            "created_at": trip.created_at.isoformat() if trip.created_at else None
        })
    return result

@router.post("/request-trip")
def driver_request_trip(trip_id: str, driver_id: str, db: Session = Depends(get_db)):
    """Driver requests to accept a trip"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.trip_status != "OPEN":
        raise HTTPException(status_code=400, detail="Trip is not available")
    
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if not driver.is_available:
        raise HTTPException(status_code=400, detail="Driver is not available")
    
    # Check if request already exists
    existing = db.query(TripDriverRequest).filter(
        TripDriverRequest.trip_id == trip_id,
        TripDriverRequest.driver_id == driver_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Request already exists")
    
    import uuid
    request = TripDriverRequest(
        request_id=str(uuid.uuid4()),
        trip_id=trip_id,
        driver_id=driver_id,
        status="pending"
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    return {
        "message": "Trip request submitted",
        "request_id": request.request_id,
        "trip_id": trip_id,
        "status": "pending"
    }

@router.get("/requests/{trip_id}")
def get_trip_requests(trip_id: str, db: Session = Depends(get_db)):
    """Admin: Get all driver requests for a trip"""
    requests = db.query(TripDriverRequest).filter(
        TripDriverRequest.trip_id == trip_id
    ).all()
    
    result = []
    for req in requests:
        driver = db.query(Driver).filter(Driver.driver_id == req.driver_id).first()
        result.append({
            "request_id": req.request_id,
            "driver_id": req.driver_id,
            "driver_name": driver.name if driver else None,
            "driver_phone": str(driver.phone_number) if driver else None,
            "status": req.status,
            "created_at": req.created_at.isoformat() if req.created_at else None
        })
    return result

@router.patch("/requests/{request_id}/approve")
def approve_driver_request(request_id: str, db: Session = Depends(get_db)):
    """Admin: Approve driver request and assign to trip"""
    request = db.query(TripDriverRequest).filter(
        TripDriverRequest.request_id == request_id
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    trip = db.query(Trip).filter(Trip.trip_id == request.trip_id).first()
    driver = db.query(Driver).filter(Driver.driver_id == request.driver_id).first()
    
    if trip.assigned_driver_id:
        raise HTTPException(status_code=400, detail="Trip already assigned")
    
    # Assign driver to trip
    trip.assigned_driver_id = request.driver_id
    trip.trip_status = "ASSIGNED"
    driver.is_available = False
    request.status = "accepted"
    
    # Reject other pending requests
    other_requests = db.query(TripDriverRequest).filter(
        TripDriverRequest.trip_id == request.trip_id,
        TripDriverRequest.request_id != request_id,
        TripDriverRequest.status == "pending"
    ).all()
    
    for other in other_requests:
        other.status = "rejected"
    
    db.commit()
    
    return {
        "message": "Driver request approved",
        "trip_id": trip.trip_id,
        "driver_id": driver.driver_id,
        "driver_name": driver.name
    }

@router.get("/", response_model=None)
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
    result = []
    for trip in trips:
        result.append({
            "trip_id": trip.trip_id,
            "customer_name": trip.customer_name,
            "customer_phone": trip.customer_phone,
            "pickup_address": trip.pickup_address,
            "drop_address": trip.drop_address,
            "trip_type": trip.trip_type,
            "vehicle_type": trip.vehicle_type,
            "assigned_driver_id": trip.assigned_driver_id,
            "trip_status": trip.trip_status,
            "distance_km": float(trip.distance_km) if trip.distance_km else None,
            "odo_start": trip.odo_start,
            "odo_end": trip.odo_end,
            "fare": float(trip.fare) if trip.fare else None,
            "started_at": trip.started_at.isoformat() if trip.started_at else None,
            "ended_at": trip.ended_at.isoformat() if trip.ended_at else None,
            "planned_start_at": trip.planned_start_at.isoformat() if trip.planned_start_at else None,
            "planned_end_at": trip.planned_end_at.isoformat() if trip.planned_end_at else None,
            "is_manual_assignment": trip.is_manual_assignment,
            "passenger_count": trip.passenger_count,
            "errors": trip.errors,
            "created_at": trip.created_at.isoformat() if trip.created_at else None,
            "updated_at": trip.updated_at.isoformat() if trip.updated_at else None
        })
    return result

@router.get("/{trip_id}")
def get_trip_details(trip_id: str, db: Session = Depends(get_db)):
    """Get trip details by ID"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    return {
        "trip_id": trip.trip_id,
        "customer_name": trip.customer_name,
        "customer_phone": trip.customer_phone,
        "pickup_address": trip.pickup_address,
        "drop_address": trip.drop_address,
        "trip_type": trip.trip_type,
        "vehicle_type": trip.vehicle_type,
        "assigned_driver_id": trip.assigned_driver_id,
        "trip_status": trip.trip_status,
        "distance_km": float(trip.distance_km) if trip.distance_km else None,
        "odo_start": trip.odo_start,
        "odo_end": trip.odo_end,
        "fare": float(trip.fare) if trip.fare else None,
        "started_at": trip.started_at.isoformat() if trip.started_at else None,
        "ended_at": trip.ended_at.isoformat() if trip.ended_at else None,
        "planned_start_at": trip.planned_start_at.isoformat() if trip.planned_start_at else None,
        "planned_end_at": trip.planned_end_at.isoformat() if trip.planned_end_at else None,
        "is_manual_assignment": trip.is_manual_assignment,
        "passenger_count": trip.passenger_count,
        "errors": trip.errors,
        "created_at": trip.created_at.isoformat() if trip.created_at else None,
        "updated_at": trip.updated_at.isoformat() if trip.updated_at else None
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    """Create a new trip"""
    # Generate UUID for trip_id
    import uuid
    trip_data = trip.dict()
    trip_data['trip_id'] = str(uuid.uuid4())
    
    db_trip = Trip(**trip_data)
    db_trip.fare = 100.00  # Default fare
    
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    
    return {
        "trip_id": db_trip.trip_id,
        "customer_name": db_trip.customer_name,
        "trip_status": db_trip.trip_status,
        "fare": float(db_trip.fare),
        "message": "Trip created successfully"
    }

@router.put("/{trip_id}")
def update_trip(
    trip_id: str, 
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
    
    update_data = trip_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trip, field, value)
    
    db.commit()
    db.refresh(trip)
    
    return {
        "trip_id": trip.trip_id,
        "message": "Trip updated successfully"
    }

@router.patch("/{trip_id}/assign-driver/{driver_id}")
def assign_driver_to_trip(
    trip_id: str, 
    driver_id: str, 
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
    trip_id: str, 
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
    trip_id: str,
    driver_id: str,
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

@router.get("/driver/{driver_id}")
def get_trips_by_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get all trips assigned to a specific driver"""
    # Check if driver exists
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    trips = db.query(Trip).filter(Trip.assigned_driver_id == driver_id).all()
    result = []
    for trip in trips:
        result.append({
            "trip_id": trip.trip_id,
            "customer_name": trip.customer_name,
            "customer_phone": trip.customer_phone,
            "pickup_address": trip.pickup_address,
            "drop_address": trip.drop_address,
            "trip_type": trip.trip_type,
            "vehicle_type": trip.vehicle_type,
            "assigned_driver_id": trip.assigned_driver_id,
            "trip_status": trip.trip_status,
            "distance_km": float(trip.distance_km) if trip.distance_km else None,
            "odo_start": trip.odo_start,
            "odo_end": trip.odo_end,
            "fare": float(trip.fare) if trip.fare else None,
            "started_at": trip.started_at.isoformat() if trip.started_at else None,
            "ended_at": trip.ended_at.isoformat() if trip.ended_at else None,
            "planned_start_at": trip.planned_start_at.isoformat() if trip.planned_start_at else None,
            "planned_end_at": trip.planned_end_at.isoformat() if trip.planned_end_at else None,
            "is_manual_assignment": trip.is_manual_assignment,
            "passenger_count": trip.passenger_count,
            "errors": trip.errors,
            "created_at": trip.created_at.isoformat() if trip.created_at else None,
            "updated_at": trip.updated_at.isoformat() if trip.updated_at else None
        })
    return result

@router.delete("/{trip_id}")
def delete_trip(trip_id: str, db: Session = Depends(get_db)):
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