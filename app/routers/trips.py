"""
Trip API endpoints
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models import Trip, Driver, TripDriverRequest, VehicleTariffConfig, WalletTransaction
from app.schemas import TripCreate, TripUpdate, TripResponse, TripDriverRequestCreate, TripDriverRequestUpdate
from decimal import Decimal
import uuid

def _auto_manage_trip_status(trip: Trip, old_odo_start: int, old_odo_end: int, old_status: str, db: Session):
    """Auto-manage trip status based on odometer readings - optimized"""
    # Auto-start trip when odo_start is set and status is ASSIGNED
    if trip.odo_start and not old_odo_start and trip.trip_status == "ASSIGNED":
        trip.trip_status = "STARTED"
        trip.started_at = datetime.utcnow()
    
    # Auto-complete trip when odo_end is set and status is STARTED
    if trip.odo_start and trip.odo_end and trip.trip_status == "STARTED":
        # Calculate distance
        trip.distance_km = Decimal(str(trip.odo_end - trip.odo_start))
        
        # Complete trip
        trip.trip_status = "COMPLETED"
        trip.ended_at = datetime.utcnow()
        
        # Optimized tariff query with single database call
        tariff_config = db.query(VehicleTariffConfig).filter(
            VehicleTariffConfig.vehicle_type == trip.vehicle_type,
            VehicleTariffConfig.is_active == True
        ).first()
        
        if tariff_config:
            distance = float(trip.distance_km)
            
            if trip.trip_type and trip.trip_type.upper() == "ONE_WAY":
                per_km_rate = float(tariff_config.one_way_per_km or 0)
                min_km = float(tariff_config.one_way_min_km or 130)
                billable_km = max(distance, min_km)
                km_cost = billable_km * per_km_rate
            else:
                per_km_rate = float(tariff_config.round_trip_per_km or 0)
                min_km = float(tariff_config.round_trip_min_km or 250)
                billable_km = max(distance, min_km)
                km_cost = billable_km * per_km_rate
            
            driver_allowance = float(tariff_config.driver_allowance or 0)
            calculated_fare = km_cost + driver_allowance
            trip.fare = Decimal(str(calculated_fare))
            
            # Deduct 2% wallet fee from KM cost only
            if trip.assigned_driver_id and km_cost > 0:
                wallet_fee = km_cost * 0.02
                driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
                if driver:
                    driver.wallet_balance = (driver.wallet_balance or 0) - Decimal(str(wallet_fee))
                    
                    # Create wallet transaction record
                    wallet_transaction = WalletTransaction(
                        wallet_id=str(uuid.uuid4()),
                        driver_id=trip.assigned_driver_id,
                        trip_id=trip.trip_id,
                        amount=Decimal(str(wallet_fee)),
                        transaction_type="DEBIT"
                    )
                    db.add(wallet_transaction)
        else:
            # Fallback calculation if no tariff config found
            distance = float(trip.distance_km)
            # Default rates if no config
            per_km_rate = 15.0  # Default rate
            min_km = 130.0 if trip.trip_type and trip.trip_type.upper() == "ONE_WAY" else 250.0
            driver_allowance = 300.0  # Default allowance
            
            billable_km = max(distance, min_km)
            km_cost = billable_km * per_km_rate
            calculated_fare = km_cost + driver_allowance
            trip.fare = Decimal(str(calculated_fare))
            
            # Deduct 2% wallet fee from KM cost only
            if trip.assigned_driver_id and km_cost > 0:
                wallet_fee = km_cost * 0.02
                driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
                if driver:
                    driver.wallet_balance = (driver.wallet_balance or 0) - Decimal(str(wallet_fee))
                    
                    # Create wallet transaction record
                    wallet_transaction = WalletTransaction(
                        wallet_id=str(uuid.uuid4()),
                        driver_id=trip.assigned_driver_id,
                        trip_id=trip.trip_id,
                        amount=Decimal(str(wallet_fee)),
                        transaction_type="DEBIT"
                    )
                    db.add(wallet_transaction)
        
        # Make driver available again
        if trip.assigned_driver_id:
            driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
            if driver:
                driver.is_available = True

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
    
    # Get initial fare from tariff configuration or default to 0
    tariff_config = db.query(VehicleTariffConfig).filter(
        VehicleTariffConfig.vehicle_type == trip.vehicle_type,
        VehicleTariffConfig.is_active == True
    ).first()
    
    # Set initial fare based on driver allowance only (distance-based calculation happens at completion)
    db_trip.fare = tariff_config.driver_allowance if tariff_config else 0.00
    
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
    
    # Store old values for comparison
    old_odo_start = trip.odo_start
    old_odo_end = trip.odo_end
    old_status = trip.trip_status
    
    for field, value in update_data.items():
        setattr(trip, field, value)
    
    # Auto-manage trip status based on odometer readings
    _auto_manage_trip_status(trip, old_odo_start, old_odo_end, old_status, db)
    
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

@router.patch("/{trip_id}/odometer-start")
def update_odometer_start(trip_id: str, odo_start: int, db: Session = Depends(get_db)):
    """Update trip starting odometer reading and auto-start trip"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    old_odo_start = trip.odo_start
    old_status = trip.trip_status
    
    trip.odo_start = odo_start
    
    # Use auto-management function
    _auto_manage_trip_status(trip, old_odo_start, trip.odo_end, old_status, db)
    
    db.commit()
    db.refresh(trip)
    
    return {
        "message": "Trip started automatically with odometer reading",
        "trip_id": trip_id,
        "odo_start": odo_start,
        "trip_status": trip.trip_status,
        "started_at": trip.started_at.isoformat() if trip.started_at else None
    }

@router.patch("/{trip_id}/odometer-end")
def update_odometer_end(trip_id: str, odo_end: int, db: Session = Depends(get_db)):
    """Update trip ending odometer reading and auto-complete trip"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    old_odo_end = trip.odo_end
    old_status = trip.trip_status
    
    trip.odo_end = odo_end
    
    # Use auto-management function
    _auto_manage_trip_status(trip, trip.odo_start, old_odo_end, old_status, db)
    
    db.commit()
    db.refresh(trip)
    
    return {
        "message": "Trip completed automatically with fare calculation",
        "trip_id": trip_id,
        "odo_end": odo_end,
        "distance_km": float(trip.distance_km) if trip.distance_km else None,
        "trip_status": trip.trip_status,
        "fare": float(trip.fare) if trip.fare else None,
        "ended_at": trip.ended_at.isoformat() if trip.ended_at else None
    }

@router.patch("/fix-incomplete-trips")
def fix_incomplete_trips(db: Session = Depends(get_db)):
    """Fix trips that have both odometer readings but are still in STARTED status"""
    try:
        # Find trips with both odo readings but still STARTED
        incomplete_trips = db.query(Trip).filter(
            Trip.trip_status == "STARTED",
            Trip.odo_start.isnot(None),
            Trip.odo_end.isnot(None)
        ).all()
        
        fixed_count = 0
        for trip in incomplete_trips:
            old_status = trip.trip_status
            _auto_manage_trip_status(trip, None, None, old_status, db)
            fixed_count += 1
        
        db.commit()
        
        return {
            "message": f"Fixed {fixed_count} incomplete trips",
            "fixed_trips": fixed_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{trip_id}/fare-breakdown")
def get_fare_breakdown(trip_id: str, db: Session = Depends(get_db)):
    """Get detailed fare calculation breakdown for a trip"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if not trip.distance_km:
        raise HTTPException(status_code=400, detail="Trip distance not calculated yet")
    
    # Get tariff configuration
    tariff_config = db.query(VehicleTariffConfig).filter(
        VehicleTariffConfig.vehicle_type == trip.vehicle_type,
        VehicleTariffConfig.is_active == True
    ).first()
    
    if not tariff_config:
        raise HTTPException(status_code=404, detail=f"No active tariff found for {trip.vehicle_type}")
    
    distance = float(trip.distance_km)
    
    if trip.trip_type and trip.trip_type.upper() == "ONE_WAY":
        per_km_rate = float(tariff_config.one_way_per_km or 0)
        min_km = float(tariff_config.one_way_min_km or 130)
        trip_type_display = "One Way"
    else:
        per_km_rate = float(tariff_config.round_trip_per_km or 0)
        min_km = float(tariff_config.round_trip_min_km or 250)
        trip_type_display = "Round Trip"
    
    billable_km = max(distance, min_km)
    distance_fare = billable_km * per_km_rate
    driver_allowance = float(tariff_config.driver_allowance or 0)
    total_fare = distance_fare + driver_allowance
    
    return {
        "trip_id": trip_id,
        "vehicle_type": trip.vehicle_type,
        "trip_type": trip_type_display,
        "actual_distance_km": distance,
        "minimum_km_required": min_km,
        "billable_km": billable_km,
        "per_km_rate": per_km_rate,
        "distance_fare": distance_fare,
        "driver_allowance": driver_allowance,
        "total_fare": total_fare,
        "calculation": f"{billable_km} km × ₹{per_km_rate} + ₹{driver_allowance} allowance = ₹{total_fare}",
        "minimum_applied": distance < min_km
    }

@router.patch("/{trip_id}/recalculate-fare")
def recalculate_trip_fare(trip_id: str, db: Session = Depends(get_db)):
    """Manually recalculate fare for a completed trip"""
    try:
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        if not trip.distance_km:
            raise HTTPException(status_code=400, detail="Trip distance not available")
        
        # Get tariff configuration
        tariff_config = db.query(VehicleTariffConfig).filter(
            VehicleTariffConfig.vehicle_type == trip.vehicle_type,
            VehicleTariffConfig.is_active == True
        ).first()
        
        old_fare = float(trip.fare) if trip.fare else 0
        
        if tariff_config:
            distance = float(trip.distance_km)
            
            if trip.trip_type and trip.trip_type.upper() == "ONE_WAY":
                per_km_rate = float(tariff_config.one_way_per_km or 0)
                min_km = float(tariff_config.one_way_min_km or 130)
                billable_km = max(distance, min_km)
                km_cost = billable_km * per_km_rate
            else:
                per_km_rate = float(tariff_config.round_trip_per_km or 0)
                min_km = float(tariff_config.round_trip_min_km or 250)
                billable_km = max(distance, min_km)
                km_cost = billable_km * per_km_rate
            
            driver_allowance = float(tariff_config.driver_allowance or 0)
            calculated_fare = km_cost + driver_allowance
            trip.fare = Decimal(str(calculated_fare))
            
            # Deduct 2% wallet fee from KM cost only if trip is completed
            wallet_fee_deducted = 0
            if trip.trip_status == "COMPLETED" and trip.assigned_driver_id and km_cost > 0:
                wallet_fee = km_cost * 0.02
                driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
                if driver:
                    driver.wallet_balance = (driver.wallet_balance or 0) - Decimal(str(wallet_fee))
                    wallet_fee_deducted = wallet_fee
                    
                    # Create wallet transaction record
                    wallet_transaction = WalletTransaction(
                        wallet_id=str(uuid.uuid4()),
                        driver_id=trip.assigned_driver_id,
                        trip_id=trip.trip_id,
                        amount=Decimal(str(wallet_fee)),
                        transaction_type="DEBIT"
                    )
                    db.add(wallet_transaction)
        else:
            # Fallback calculation
            distance = float(trip.distance_km)
            per_km_rate = 15.0
            min_km = 130.0 if trip.trip_type and trip.trip_type.upper() == "ONE_WAY" else 250.0
            driver_allowance = 300.0
            
            billable_km = max(distance, min_km)
            km_cost = billable_km * per_km_rate
            calculated_fare = km_cost + driver_allowance
            trip.fare = Decimal(str(calculated_fare))
            
            wallet_fee_deducted = 0
            if trip.trip_status == "COMPLETED" and trip.assigned_driver_id and km_cost > 0:
                wallet_fee = km_cost * 0.02
                driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
                if driver:
                    driver.wallet_balance = (driver.wallet_balance or 0) - Decimal(str(wallet_fee))
                    wallet_fee_deducted = wallet_fee
                    
                    wallet_transaction = WalletTransaction(
                        wallet_id=str(uuid.uuid4()),
                        driver_id=trip.assigned_driver_id,
                        trip_id=trip.trip_id,
                        amount=Decimal(str(wallet_fee)),
                        transaction_type="DEBIT"
                    )
                    db.add(wallet_transaction)
        
        db.commit()
        db.refresh(trip)
        
        return {
            "message": "Fare recalculated successfully",
            "trip_id": trip_id,
            "old_fare": old_fare,
            "new_fare": float(trip.fare),
            "wallet_fee_deducted": wallet_fee_deducted,
            "distance_km": float(trip.distance_km)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
@router.patch("/{trip_id}/fix-status")
def fix_trip_status(trip_id: str, db: Session = Depends(get_db)):
    """Fix a specific trip's status based on its odometer readings"""
    try:
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        old_status = trip.trip_status
        
        # Apply auto-management logic
        _auto_manage_trip_status(trip, None, None, old_status, db)
        
        db.commit()
        db.refresh(trip)
        
        return {
            "message": f"Trip status updated from {old_status} to {trip.trip_status}",
            "trip_id": trip_id,
            "old_status": old_status,
            "new_status": trip.trip_status,
            "distance_km": float(trip.distance_km) if trip.distance_km else None,
            "fare": float(trip.fare) if trip.fare else None,
            "ended_at": trip.ended_at.isoformat() if trip.ended_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")