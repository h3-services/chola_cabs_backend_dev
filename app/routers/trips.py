"""
Trip API endpoints
"""
from typing import List
from datetime import datetime
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
    """Full trip edit for admin panel"""
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
        "updated_at": trip.updated_at.isoformat() if trip.updated_at else None,
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
    trip.trip_status = "ASSIGNED"
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
    valid_statuses = ["OPEN", "ASSIGNED", "STARTED", "COMPLETED", "CANCELLED"]
    
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
    if new_status in ["COMPLETED", "CANCELLED"] and trip.assigned_driver_id:
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

@router.get("/stats")
def get_trip_statistics(db: Session = Depends(get_db)):
    """Get trip statistics for admin dashboard"""
    try:
        total_trips = db.query(Trip).count()
        pending_trips = db.query(Trip).filter(Trip.trip_status == "OPEN").count()
        assigned_trips = db.query(Trip).filter(Trip.trip_status == "ASSIGNED").count()
        started_trips = db.query(Trip).filter(Trip.trip_status == "STARTED").count()
        completed_trips = db.query(Trip).filter(Trip.trip_status == "COMPLETED").count()
        cancelled_trips = db.query(Trip).filter(Trip.trip_status == "CANCELLED").count()
        
        return {
            "total_trips": total_trips,
            "pending_trips": pending_trips,
            "assigned_trips": assigned_trips,
            "started_trips": started_trips,
            "completed_trips": completed_trips,
            "cancelled_trips": cancelled_trips,
            "active_trips": assigned_trips + started_trips
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/available-drivers")
def get_available_drivers_for_trip(trip_id: str = None, db: Session = Depends(get_db)):
    """Get available drivers for trip assignment"""
    try:
        # Get available and approved drivers
        drivers = db.query(Driver).filter(
            Driver.is_available == True,
            Driver.is_approved == True
        ).all()
        
        result = []
        for driver in drivers:
            result.append({
                "driver_id": driver.driver_id,
                "name": driver.name,
                "phone_number": str(driver.phone_number) if driver.phone_number else None,
                "primary_location": driver.primary_location,
                "wallet_balance": float(driver.wallet_balance) if driver.wallet_balance else 0.0,
                "is_available": driver.is_available,
                "created_at": driver.created_at.isoformat() if driver.created_at else None
            })
        
        return {
            "available_drivers": result,
            "total_available": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.patch("/{trip_id}/unassign-driver")
def unassign_driver_from_trip(trip_id: str, db: Session = Depends(get_db)):
    """Remove assigned driver from trip"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if not trip.assigned_driver_id:
        raise HTTPException(status_code=400, detail="No driver assigned to this trip")
    
    if trip.trip_status in ["STARTED", "COMPLETED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail=f"Cannot unassign driver from trip with status {trip.trip_status}")
    
    # Make driver available again
    driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
    if driver:
        driver.is_available = True
    
    old_driver_id = trip.assigned_driver_id
    trip.assigned_driver_id = None
    trip.trip_status = "OPEN"
    
    db.commit()
    
    return {
        "message": "Driver unassigned successfully",
        "trip_id": trip_id,
        "unassigned_driver_id": old_driver_id,
        "new_status": "OPEN"
    }

@router.patch("/{trip_id}/cancel")
def cancel_trip(trip_id: str, reason: str = "Cancelled by admin", db: Session = Depends(get_db)):
    """Cancel a trip"""
    try:
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        if trip.trip_status in ["COMPLETED", "CANCELLED"]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel trip with status {trip.trip_status}")
        
        old_status = trip.trip_status
        trip.trip_status = "CANCELLED"
        
        # Make assigned driver available again
        if trip.assigned_driver_id:
            driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
            if driver:
                driver.is_available = True
        
        db.commit()
        db.refresh(trip)
        
        return {
            "message": "Trip cancelled successfully",
            "trip_id": trip_id,
            "old_status": old_status,
            "new_status": "CANCELLED",
            "reason": reason
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.patch("/{trip_id}/start")
def start_trip(trip_id: str, odo_start: int = None, db: Session = Depends(get_db)):
    """Start a trip"""
    try:
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        if trip.trip_status != "ASSIGNED":
            raise HTTPException(status_code=400, detail=f"Cannot start trip with status {trip.trip_status}")
        
        trip.trip_status = "STARTED"
        trip.started_at = datetime.utcnow()
        if odo_start:
            trip.odo_start = odo_start
        
        db.commit()
        db.refresh(trip)
        
        return {
            "message": "Trip started successfully",
            "trip_id": trip_id,
            "status": "STARTED",
            "started_at": trip.started_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.patch("/{trip_id}/odometer-start")
def update_odometer_start(trip_id: str, odo_start: int, db: Session = Depends(get_db)):
    """Update trip starting odometer reading"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip.odo_start = odo_start
    db.commit()
    
    return {
        "message": "Odometer start updated successfully",
        "trip_id": trip_id,
        "odo_start": odo_start
    }

@router.patch("/{trip_id}/odometer-end")
def update_odometer_end(trip_id: str, odo_end: int, db: Session = Depends(get_db)):
    """Update trip ending odometer reading"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip.odo_end = odo_end
    
    # Auto-calculate distance if both readings available
    if trip.odo_start and trip.odo_end:
        trip.distance_km = Decimal(str(trip.odo_end - trip.odo_start))
    
    db.commit()
    
    return {
        "message": "Odometer end updated successfully",
        "trip_id": trip_id,
        "odo_end": odo_end,
        "distance_km": float(trip.distance_km) if trip.distance_km else None
    }

@router.patch("/{trip_id}/complete")
def complete_trip(
    trip_id: str, 
    odo_end: int = None, 
    distance_km: float = None,
    db: Session = Depends(get_db)
):
    """Complete a trip"""
    try:
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        if trip.trip_status != "STARTED":
            raise HTTPException(status_code=400, detail=f"Cannot complete trip with status {trip.trip_status}")
        
        trip.trip_status = "COMPLETED"
        trip.ended_at = datetime.utcnow()
        if odo_end:
            trip.odo_end = odo_end
        if distance_km:
            trip.distance_km = Decimal(str(distance_km))
        
        # Make driver available again
        if trip.assigned_driver_id:
            driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
            if driver:
                driver.is_available = True
        
        db.commit()
        db.refresh(trip)
        
        return {
            "message": "Trip completed successfully",
            "trip_id": trip_id,
            "status": "COMPLETED",
            "ended_at": trip.ended_at.isoformat(),
            "distance_km": float(trip.distance_km) if trip.distance_km else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")