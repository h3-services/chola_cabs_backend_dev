"""
Trip API endpoints - OPTIMIZED
Uses CRUD layer for production-ready performance
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import crud_trip, crud_driver
from app.schemas import TripCreate, TripUpdate, TripResponse
from app.core.logging import get_logger
from app.core.constants import TripStatus, ErrorCode
import uuid

logger = get_logger(__name__)

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/available", response_model=List[TripResponse])
def get_available_trips(db: Session = Depends(get_db)):
    """Get all available trips (OPEN status, no driver assigned) - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Specialized method
        trips = crud_trip.get_available_trips(db)
        return trips
    except Exception as e:
        logger.error(f"Error fetching available trips: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available trips"
        )


@router.get("/", response_model=None)
def get_all_trips(
    skip: int = 0, 
    limit: int = 100, 
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """Get all trips with optional status filter - OPTIMIZED"""
    try:
        if status_filter:
            # ✅ OPTIMIZED: Status-based query
            trips = crud_trip.get_by_status(db, status=status_filter, skip=skip, limit=limit)
        else:
            # ✅ OPTIMIZED: Using CRUD layer
            trips = crud_trip.get_multi(db, skip=skip, limit=limit, order_by="-created_at")
        
        # Convert to dict for response
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
                "trip_status": trip.trip_status,
                "assigned_driver_id": trip.assigned_driver_id,
                "distance_km": float(trip.distance_km) if trip.distance_km else None,
                "fare": float(trip.fare) if trip.fare else None,
                "odo_start": trip.odo_start,
                "odo_end": trip.odo_end,
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
    except Exception as e:
        logger.error(f"Error fetching trips: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch trips"
        )


@router.get("/{trip_id}")
def get_trip_details(trip_id: str, db: Session = Depends(get_db)):
    """Get trip details by ID with driver info - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Eager load driver (1 query instead of 2)
        trip = crud_trip.get_with_driver(db, trip_id)
        
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": ErrorCode.TRIP_NOT_FOUND, "message": "Trip not found"}
            )
        
        # Build response with driver info
        response = {
            "trip_id": trip.trip_id,
            "customer_name": trip.customer_name,
            "customer_phone": trip.customer_phone,
            "pickup_address": trip.pickup_address,
            "drop_address": trip.drop_address,
            "trip_type": trip.trip_type,
            "vehicle_type": trip.vehicle_type,
            "trip_status": trip.trip_status,
            "assigned_driver_id": trip.assigned_driver_id,
            "distance_km": float(trip.distance_km) if trip.distance_km else None,
            "fare": float(trip.fare) if trip.fare else None,
            "odo_start": trip.odo_start,
            "odo_end": trip.odo_end,
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
        
        # Add driver info if available (already loaded via eager loading)
        if trip.assigned_driver:
            response["driver"] = {
                "driver_id": trip.assigned_driver.driver_id,
                "name": trip.assigned_driver.name,
                "phone_number": str(trip.assigned_driver.phone_number),
                "is_available": trip.assigned_driver.is_available
            }
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trip {trip_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch trip"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    """Create a new trip - OPTIMIZED"""
    try:
        # Generate UUID
        trip_data = trip.dict()
        trip_data['trip_id'] = str(uuid.uuid4())
        trip_data['trip_status'] = TripStatus.OPEN
        
        # Create trip
        from app.models import Trip
        db_trip = Trip(**trip_data)
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        
        logger.info(f"Trip created: {db_trip.trip_id}")
        
        return {
            "trip_id": db_trip.trip_id,
            "customer_name": db_trip.customer_name,
            "trip_status": db_trip.trip_status,
            "message": "Trip created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating trip: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create trip"
        )


@router.put("/{trip_id}")
def update_trip(
    trip_id: str, 
    trip_update: TripUpdate, 
    db: Session = Depends(get_db)
):
    """Update trip information - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Get trip using CRUD
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        # ✅ OPTIMIZED: Update using CRUD
        updated_trip = crud_trip.update(db, db_obj=trip, obj_in=trip_update)
        logger.info(f"Trip updated: {trip_id}")
        
        return updated_trip
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trip {trip_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update trip"
        )


@router.patch("/{trip_id}/assign-driver/{driver_id}")
def assign_driver_to_trip(
    trip_id: str, 
    driver_id: str, 
    db: Session = Depends(get_db)
):
    """Assign a driver to a trip - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Check trip exists
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        # ✅ OPTIMIZED: Check driver exists and is available
        driver = crud_driver.get(db, id=driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # ✅ Removed driver.is_available check to allow manual assignment by admin
        
        if not driver.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver is not approved"
            )
        
        # ✅ OPTIMIZED: Assign driver using CRUD
        updated_trip = crud_trip.assign_driver(db, trip_id, driver_id)
        
        logger.info(f"Driver {driver_id} assigned to trip {trip_id}")
        
        return {
            "message": "Driver assigned successfully",
            "trip_id": trip_id,
            "driver_id": driver_id,
            "trip_status": updated_trip.trip_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning driver: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign driver"
        )


@router.patch("/{trip_id}/status")
def update_trip_status(
    trip_id: str, 
    new_status: str, 
    db: Session = Depends(get_db)
):
    """Update trip status - OPTIMIZED"""
    try:
        # Validate status
        valid_statuses = [TripStatus.OPEN, TripStatus.ASSIGNED, TripStatus.STARTED, TripStatus.COMPLETED, TripStatus.CANCELLED]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # ✅ OPTIMIZED: Update status using CRUD (auto-sets timestamps)
        trip = crud_trip.update_status(db, trip_id, new_status)
        
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        logger.info(f"Trip {trip_id} status updated to {new_status}")
        
        return {
            "message": f"Trip status updated to {new_status}",
            "trip_id": trip_id,
            "trip_status": new_status,
            "fare": float(trip.fare) if trip.fare else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trip status: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update trip status"
        )


@router.get("/driver/{driver_id}")
def get_trips_by_driver(driver_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all trips assigned to a specific driver - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Driver-specific query
        trips = crud_trip.get_by_driver(db, driver_id=driver_id, skip=skip, limit=limit)
        
        result = []
        for trip in trips:
            result.append({
                "trip_id": trip.trip_id,
                "customer_name": trip.customer_name,
                "pickup_address": trip.pickup_address,
                "drop_address": trip.drop_address,
                "trip_status": trip.trip_status,
                "fare": float(trip.fare) if trip.fare else None,
                "created_at": trip.created_at.isoformat() if trip.created_at else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Error fetching trips for driver {driver_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch driver trips"
        )


@router.get("/statistics/dashboard")
def get_trip_statistics(db: Session = Depends(get_db)):
    """Get trip statistics for admin dashboard - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Single method call for all stats
        stats = crud_trip.get_statistics(db)
        return stats
    except Exception as e:
        logger.error(f"Error fetching trip statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.patch("/{trip_id}/odometer/start")
def update_odometer_start(trip_id: str, odo_start: int, db: Session = Depends(get_db)):
    """Update trip starting odometer reading - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Get trip using CRUD
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        trip.odo_start = odo_start
        
        # Auto-start trip if not already started
        if trip.trip_status == TripStatus.ASSIGNED:
            trip.trip_status = TripStatus.STARTED
            trip.started_at = datetime.utcnow()
        
        db.commit()
        db.refresh(trip)
        
        logger.info(f"Trip {trip_id} odometer start updated to {odo_start}")
        
        return {
            "message": "Odometer start updated",
            "trip_id": trip_id,
            "odo_start": odo_start,
            "trip_status": trip.trip_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating odometer start: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update odometer"
        )


@router.patch("/{trip_id}/odometer/end")
def update_odometer_end(trip_id: str, odo_end: int, db: Session = Depends(get_db)):
    """Update trip ending odometer reading and auto-complete trip with commission calculation"""
    try:
        # Import required models and constants locally for safety
        from app.models import Driver, WalletTransaction
        from app.core.constants import DEFAULT_DRIVER_COMMISSION_PERCENT, WalletTransactionType
        from decimal import Decimal, ROUND_HALF_UP
        import uuid
        
        # ✅ Get trip using CRUD
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        if trip.odo_start is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set end odometer without start odometer"
            )
        
        if odo_end <= trip.odo_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End odometer must be greater than start odometer"
            )
        
        trip.odo_end = odo_end
        trip.distance_km = Decimal(odo_end - trip.odo_start)
        
        # Variables to track commission and earnings
        commission_amount = None
        driver_earnings = None
        
        # Auto-complete trip
        if trip.trip_status != TripStatus.COMPLETED:
            trip.trip_status = TripStatus.COMPLETED
            trip.ended_at = datetime.utcnow()
            
            # ✅ Calculate fare using CRUD (distance × per_km_rate only)
            fare = crud_trip.calculate_fare(db, trip)
            if fare:
                trip.fare = Decimal(fare).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                
                # ✅ Calculate 10% commission safely
                comm_pct = Decimal(str(DEFAULT_DRIVER_COMMISSION_PERCENT)) / Decimal("100")
                commission_amount = (trip.fare * comm_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                
                logger.info(f"Trip {trip_id}: Fare=₹{trip.fare}, Commission=₹{commission_amount}")
                
                # ✅ Create wallet transactions and update driver balance
                if trip.assigned_driver_id:
                    # Get driver
                    driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
                    
                    if driver:
                        # Create DEBIT transaction for commission (minus from balance)
                        wallet_commission = WalletTransaction(
                            wallet_id=str(uuid.uuid4()),
                            driver_id=trip.assigned_driver_id,
                            trip_id=trip.trip_id,
                            amount=commission_amount,
                            transaction_type="DEBIT"
                        )
                        db.add(wallet_commission)
                        
                        # Update driver wallet balance (Minus commission only)
                        driver.wallet_balance = (driver.wallet_balance or Decimal(0)) - commission_amount
                        
                        logger.info(f"Driver {trip.assigned_driver_id} wallet updated: -₹{commission_amount} (Commission deducted)")
                    else:
                        logger.warning(f"Driver {trip.assigned_driver_id} not found for wallet update")
        
        db.commit()
        db.refresh(trip)
        
        logger.info(f"Trip {trip_id} completed with fare {trip.fare}")
        
        # Build response with commission details
        response = {
            "message": "Trip completed successfully",
            "trip_id": trip_id,
            "odo_end": odo_end,
            "distance_km": float(trip.distance_km) if trip.distance_km else None,
            "fare": float(trip.fare) if trip.fare else None,
            "trip_status": trip.trip_status
        }
        
        # Add commission details if calculated
        if commission_amount is not None:
            response["commission_deducted"] = float(commission_amount)
            response["commission_percentage"] = DEFAULT_DRIVER_COMMISSION_PERCENT
            response["driver_collects_from_customer"] = float(trip.fare) if trip.fare else 0.0
            response["wallet_updated"] = True
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating odometer end: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update odometer"
        )


@router.post("/{trip_id}/recalculate-fare")
def recalculate_trip_fare(trip_id: str, db: Session = Depends(get_db)):
    """Manually recalculate fare for a completed trip and update wallet"""
    try:
        from app.models import Driver, WalletTransaction
        from app.core.constants import DEFAULT_DRIVER_COMMISSION_PERCENT, WalletTransactionType
        from decimal import Decimal
        import uuid
        
        # ✅ OPTIMIZED: Get trip using CRUD
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        # ✅ OPTIMIZED: Calculate fare using CRUD
        new_fare = crud_trip.calculate_fare(db, trip)
        
        if not new_fare:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot calculate fare. Missing odometer readings or tariff config."
            )
        
        old_fare = trip.fare or Decimal(0)
        
        # If fare hasn't changed, just return
        if old_fare == new_fare:
            return {
                "message": "Fare is already up to date",
                "trip_id": trip_id,
                "fare": float(new_fare)
            }

        # Calculate difference in COMMISSION to update wallet
        old_commission = (old_fare * Decimal(str(DEFAULT_DRIVER_COMMISSION_PERCENT)) / Decimal("100")).quantize(Decimal("0.01"))
        new_commission = (new_fare * Decimal(str(DEFAULT_DRIVER_COMMISSION_PERCENT)) / Decimal("100")).quantize(Decimal("0.01"))
        
        commission_difference = new_commission - old_commission
        
        # Update trip fare
        trip.fare = new_fare
        
        # Update wallet if a driver is assigned
        if trip.assigned_driver_id:
            driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
            if driver:
                # If commission increased, we need to DEBIT more from wallet
                # If commission decreased, we need to CREDIT some back
                adj_type = "DEBIT" if commission_difference > 0 else "CREDIT"
                
                adjustment = WalletTransaction(
                    wallet_id=str(uuid.uuid4()),
                    driver_id=trip.assigned_driver_id,
                    trip_id=trip.trip_id,
                    amount=abs(commission_difference),
                    transaction_type=adj_type
                )
                db.add(adjustment)
                
                # Update balance (Subtract the difference in commission)
                driver.wallet_balance = (driver.wallet_balance or Decimal(0)) - commission_difference
                
                logger.info(f"Trip {trip_id} recalculated. Commission adjusted by ₹{commission_difference}")

        db.commit()
        db.refresh(trip)
        
        return {
            "message": "Fare recalculated and wallet adjusted successfully",
            "trip_id": trip_id,
            "old_fare": float(old_fare),
            "new_fare": float(new_fare),
            "net_adjustment": float(net_difference)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalculating fare: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to recalculate fare"
        )