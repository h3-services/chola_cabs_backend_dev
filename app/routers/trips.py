"""
Trip API endpoints - OPTIMIZED
Uses CRUD layer for production-ready performance
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
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


@router.get("", response_model=None, include_in_schema=False)
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
                "waiting_charges": float(trip.waiting_charges) if trip.waiting_charges else 0.0,
                "inter_state_permit_charges": float(trip.inter_state_permit_charges) if trip.inter_state_permit_charges else 0.0,
                "driver_allowance": float(trip.driver_allowance) if trip.driver_allowance else 0.0,
                "luggage_cost": float(trip.luggage_cost) if trip.luggage_cost else 0.0,
                "pet_cost": float(trip.pet_cost) if trip.pet_cost else 0.0,
                "toll_charges": float(trip.toll_charges) if trip.toll_charges else 0.0,
                "night_allowance": float(trip.night_allowance) if trip.night_allowance else 0.0,
                "total_amount": float(trip.total_amount) if trip.total_amount else 0.0,
                "odo_start": trip.odo_start,
                "odo_end": trip.odo_end,
                "odo_start_url": trip.odo_start_url,
                "odo_end_url": trip.odo_end_url,
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
            "waiting_charges": float(trip.waiting_charges) if trip.waiting_charges else 0.0,
            "inter_state_permit_charges": float(trip.inter_state_permit_charges) if trip.inter_state_permit_charges else 0.0,
            "driver_allowance": float(trip.driver_allowance) if trip.driver_allowance else 0.0,
            "luggage_cost": float(trip.luggage_cost) if trip.luggage_cost else 0.0,
            "pet_cost": float(trip.pet_cost) if trip.pet_cost else 0.0,
            "toll_charges": float(trip.toll_charges) if trip.toll_charges else 0.0,
            "night_allowance": float(trip.night_allowance) if trip.night_allowance else 0.0,
            "total_amount": float(trip.total_amount) if trip.total_amount else 0.0,
            "odo_start": trip.odo_start,
            "odo_end": trip.odo_end,
            "odo_start_url": trip.odo_start_url,
            "odo_end_url": trip.odo_end_url,
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
                "is_available": trip.assigned_driver.is_available,
                "current_status": (
                    "driving" if trip.trip_status == "STARTED" else
                    "busy" if trip.trip_status == "ASSIGNED" else
                    "offline" if trip.assigned_driver.is_available is False else "available"
                )
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


@router.post("", status_code=status.HTTP_201_CREATED)
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


@router.patch("/{trip_id}/remind")
def remind_drivers(trip_id: str, db: Session = Depends(get_db)):
    """Bump the trip to the top of the available list (updates updated_at time)"""
    try:
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        # Only allow unassigned trips to be bumped
        if trip.assigned_driver_id is not None or trip.trip_status != TripStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only remind drivers for open, unassigned trips"
            )
        
        # Manually force the updated_at timestamp to now, to bump it to the top
        trip.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(trip)
        
        logger.info(f"Trip {trip_id} bumped/reminded. New updated_at: {trip.updated_at}")
        
        return {
            "message": "Trip bumped successfully. Drivers can now be notified.",
            "trip_id": trip_id,
            "updated_at": trip.updated_at.isoformat() if trip.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reminding drivers for trip {trip_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remind drivers"
        )


@router.patch("/{trip_id}/unassign")
def unassign_driver(trip_id: str, db: Session = Depends(get_db)):
    """Unassign driver from trip - OPTIMIZED"""
    try:
        trip = crud_trip.unassign_driver(db, trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": ErrorCode.TRIP_NOT_FOUND, "message": "Trip not found"}
            )
        return {
            "message": "Driver unassigned successfully",
            "trip_id": trip_id,
            "trip_status": trip.trip_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unassigning driver: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unassign driver"
        )


@router.delete("/{trip_id}")
def delete_trip(trip_id: str, db: Session = Depends(get_db)):
    """Delete a trip - OPTIMIZED"""
    try:
        trip = crud_trip.delete(db, id=trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": ErrorCode.TRIP_NOT_FOUND, "message": "Trip not found"}
            )
        return {"message": "Trip deleted successfully", "trip_id": trip_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting trip: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete trip"
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
def update_odometer_start(
    trip_id: str,
    odo_start: int,
    odo_start_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update trip starting odometer reading with optional photo URL - OPTIMIZED"""
    try:
        # ✅ OPTIMIZED: Get trip using CRUD
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        trip.odo_start = odo_start
        if odo_start_url is not None:
            trip.odo_start_url = odo_start_url
        
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
            "odo_start_url": trip.odo_start_url,
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
def update_odometer_end(
    trip_id: str,
    odo_end: int,
    waiting_charges: Optional[float] = 0.0,
    toll_charges: Optional[float] = 0.0,
    driver_allowance: Optional[float] = 0.0,
    night_allowance: Optional[float] = 0.0,
    inter_state_permit_charges: Optional[float] = 0.0,
    luggage_cost: Optional[float] = 0.0,
    pet_cost: Optional[float] = 0.0,
    db: Session = Depends(get_db)
):
    """Update trip ending odometer reading, save extra charges, and auto-complete trip."""
    try:
        from app.models import Driver, WalletTransaction
        from app.core.constants import DEFAULT_DRIVER_COMMISSION_PERCENT, WalletTransactionType
        from decimal import Decimal, ROUND_HALF_UP
        import uuid

        # ── Fetch trip ────────────────────────────────────────────────────
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

        # ── Save odometer end ─────────────────────────────────────────────
        trip.odo_end = odo_end
        trip.distance_km = Decimal(odo_end - trip.odo_start)

        # ── Save extra charges ────────────────────────────────────────────
        trip.waiting_charges            = Decimal(str(waiting_charges or 0))
        trip.toll_charges               = Decimal(str(toll_charges or 0))
        trip.driver_allowance           = Decimal(str(driver_allowance or 0))
        trip.night_allowance            = Decimal(str(night_allowance or 0))
        trip.inter_state_permit_charges = Decimal(str(inter_state_permit_charges or 0))
        trip.luggage_cost               = Decimal(str(luggage_cost or 0))
        trip.pet_cost                   = Decimal(str(pet_cost or 0))

        logger.info(
            f"Trip {trip_id}: Extras → toll=₹{trip.toll_charges}, waiting=₹{trip.waiting_charges}, "
            f"driver_allowance=₹{trip.driver_allowance}, night=₹{trip.night_allowance}, "
            f"interstate=₹{trip.inter_state_permit_charges}, luggage=₹{trip.luggage_cost}, pet=₹{trip.pet_cost}"
        )

        # ── Commission tracking ───────────────────────────────────────────
        commission_amount = None

        # ── Auto-complete trip ────────────────────────────────────────────
        if trip.trip_status != TripStatus.COMPLETED:
            trip.trip_status = TripStatus.COMPLETED
            trip.ended_at = datetime.utcnow()

            # Calculate fare (distance × rate, with min KM rules)
            fare_data = crud_trip.calculate_fare(db, trip)
            if fare_data.get("fare"):
                trip.fare = Decimal(fare_data["fare"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                trip.distance_km = fare_data["chargeable_distance"]

                # Deduct platform commission from driver wallet
                comm_pct = Decimal(str(DEFAULT_DRIVER_COMMISSION_PERCENT)) / Decimal("100")
                commission_amount = (trip.fare * comm_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                logger.info(f"Trip {trip_id}: Fare=₹{trip.fare}, Commission=₹{commission_amount}")

                if trip.assigned_driver_id:
                    driver = db.query(Driver).filter(Driver.is_deleted == False).filter(Driver.driver_id == trip.assigned_driver_id).first()
                    if driver:
                        wallet_commission = WalletTransaction(
                            wallet_id=str(uuid.uuid4()),
                            driver_id=trip.assigned_driver_id,
                            trip_id=trip.trip_id,
                            amount=commission_amount,
                            transaction_type="DEBIT"
                        )
                        db.add(wallet_commission)
                        driver.wallet_balance = (driver.wallet_balance or Decimal(0)) - commission_amount
                        logger.info(f"Driver {trip.assigned_driver_id} wallet: -₹{commission_amount} (commission)")
                    else:
                        logger.warning(f"Driver {trip.assigned_driver_id} not found for wallet update")

        # ── total_amount = fare + all extras ──────────────────────────────
        trip.total_amount = crud_trip.calculate_total_amount(trip)
        logger.info(f"Trip {trip_id}: total_amount=₹{trip.total_amount}")

        db.commit()
        db.refresh(trip)

        # ── Build response ────────────────────────────────────────────────
        response = {
            "message": "Trip completed successfully",
            "trip_id": trip_id,
            "odo_start": trip.odo_start,
            "odo_end": odo_end,
            "distance_km": float(trip.distance_km) if trip.distance_km else None,
            # ── Fare ──
            "fare": float(trip.fare) if trip.fare else 0.0,
            # ── Extras ──
            "waiting_charges":            float(trip.waiting_charges or 0),
            "toll_charges":               float(trip.toll_charges or 0),
            "driver_allowance":           float(trip.driver_allowance or 0),
            "night_allowance":            float(trip.night_allowance or 0),
            "inter_state_permit_charges": float(trip.inter_state_permit_charges or 0),
            "luggage_cost":               float(trip.luggage_cost or 0),
            "pet_cost":                   float(trip.pet_cost or 0),
            # ── Grand total ──
            "total_amount": float(trip.total_amount) if trip.total_amount else 0.0,
            "trip_status": trip.trip_status
        }

        if commission_amount is not None:
            response["commission_deducted"]          = float(commission_amount)
            response["commission_percentage"]         = DEFAULT_DRIVER_COMMISSION_PERCENT
            response["driver_collects_from_customer"] = float(trip.total_amount) if trip.total_amount else 0.0
            response["wallet_updated"]                = True

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


@router.patch("/{trip_id}/start")
def start_trip(trip_id: str, db: Session = Depends(get_db)):
    """Mark a trip as STARTED - convenience endpoint for driver app"""
    try:
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        trip.trip_status = TripStatus.STARTED
        trip.started_at = datetime.utcnow()
        db.commit()
        db.refresh(trip)
        logger.info(f"Trip started: {trip_id}")
        return {"message": "Trip started successfully", "trip_id": trip_id, "trip_status": "STARTED", "started_at": trip.started_at.isoformat()}
    except Exception as e:
        logger.error(f"Error starting trip {trip_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to start trip")


@router.patch("/{trip_id}/extras")
def update_trip_extras(trip_id: str, payload: dict, db: Session = Depends(get_db)):
    """Update trip extra charges (toll, waiting, etc.)"""
    from decimal import Decimal
    try:
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # Mapping payload to trip model fields
        fields_map = {
            "toll_charges": "toll_charges",
            "waiting_charges": "waiting_charges",
            "driver_allowance": "driver_allowance",
            "night_allowance": "night_allowance",
            "inter_state_permit_charges": "inter_state_permit_charges",
            "parking_charges": "toll_charges", # assuming parking goes to toll or similar if no dedicated field
        }
        
        for p_key, m_key in fields_map.items():
            if p_key in payload and payload[p_key] is not None:
                setattr(trip, m_key, Decimal(str(payload[p_key])))
        
        # ✅ Recalculate total amount
        trip.total_amount = crud_trip.calculate_total_amount(trip)
        
        db.commit()
        db.refresh(trip)
        return {"message": "Trip extras updated", "trip_id": trip_id, "total_amount": float(trip.total_amount)}
    except Exception as e:
        logger.error(f"Error updating extras for {trip_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update extras")


@router.patch("/{trip_id}/complete")
def complete_trip(trip_id: str, db: Session = Depends(get_db)):
    """Mark a trip as COMPLETED - convenience endpoint for driver app"""
    try:
        trip = crud_trip.get(db, id=trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        trip.trip_status = TripStatus.COMPLETED
        trip.ended_at = datetime.utcnow()
        db.commit()
        db.refresh(trip)

        logger.info(f"Trip completed: {trip_id}")

        return {
            "message": "Trip completed successfully",
            "trip_id": trip_id,
            "trip_status": "COMPLETED",
            "ended_at": trip.ended_at.isoformat() if trip.ended_at else None,
            "fare": float(trip.fare) if trip.fare else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing trip {trip_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete trip"
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
        fare_data = crud_trip.calculate_fare(db, trip)
        new_fare = fare_data["fare"]
        chargeable_distance = fare_data["chargeable_distance"]
        
        if not new_fare:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot calculate fare. Missing odometer readings or tariff config."
            )
        
        # Update distance_km to match chargeable distance
        trip.distance_km = chargeable_distance
        
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
        
        # ✅ Recalculate total amount
        trip.total_amount = crud_trip.calculate_total_amount(trip)
        
        # Update wallet if a driver is assigned
        if trip.assigned_driver_id:
            driver = db.query(Driver).filter(Driver.is_deleted == False).filter(Driver.driver_id == trip.assigned_driver_id).first()
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