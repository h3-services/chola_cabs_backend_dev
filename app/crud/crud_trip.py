"""
CRUD operations for Trip model
Optimized for production with complex queries and eager loading
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from decimal import Decimal

from app.crud.base import CRUDBase
from app.models import Trip, Driver, VehicleTariffConfig
from app.schemas import TripCreate, TripUpdate
from app.core.constants import TripStatus, MIN_ONE_WAY_KM, MIN_ROUND_TRIP_KM


class CRUDTrip(CRUDBase[Trip, TripCreate, TripUpdate]):
    """
    CRUD operations for Trip model with production optimizations
    """
    
    def get_with_driver(self, db: Session, trip_id: str) -> Optional[Trip]:
        """
        Get trip with driver details (eager loaded)
        
        Args:
            db: Database session
            trip_id: Trip ID
        
        Returns:
            Trip with driver or None
        """
        return self._apply_soft_delete_filter(db.query(Trip)).options(
            joinedload(Trip.assigned_driver)
        ).filter(Trip.trip_id == trip_id).first()
    
    def get_available_trips(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Trip]:
        """
        Get all available trips (OPEN status, no driver assigned)
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            List of available trips
        """
        return self._apply_soft_delete_filter(db.query(Trip)).filter(
            and_(
                Trip.trip_status == TripStatus.OPEN,
                Trip.assigned_driver_id == None
            )
        ).order_by(Trip.updated_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_status(
        self,
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Trip]:
        """
        Get trips by status
        
        Args:
            db: Database session
            status: Trip status
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            List of trips with specified status
        """
        return self._apply_soft_delete_filter(db.query(Trip)).filter(
            Trip.trip_status == status
        ).offset(skip).limit(limit).all()
    
    def get_by_driver(
        self,
        db: Session,
        driver_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Trip]:
        """
        Get all trips for a specific driver
        
        Args:
            db: Database session
            driver_id: Driver ID
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            List of driver's trips
        """
        return self._apply_soft_delete_filter(db.query(Trip)).filter(
            Trip.assigned_driver_id == driver_id
        ).order_by(Trip.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_active_trips(
        self,
        db: Session,
        driver_id: Optional[str] = None
    ) -> List[Trip]:
        """
        Get active trips (ASSIGNED or STARTED)
        
        Args:
            db: Database session
            driver_id: Optional driver ID to filter by
        
        Returns:
            List of active trips
        """
        query = self._apply_soft_delete_filter(db.query(Trip)).filter(
            or_(
                Trip.trip_status == TripStatus.ASSIGNED,
                Trip.trip_status == TripStatus.STARTED
            )
        )
        
        if driver_id:
            query = query.filter(Trip.assigned_driver_id == driver_id)
        
        return query.all()
    
    def get_completed_trips(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        driver_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Trip]:
        """
        Get completed trips with optional date range and driver filter
        
        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            driver_id: Optional driver ID filter
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            List of completed trips
        """
        query = self._apply_soft_delete_filter(db.query(Trip)).filter(Trip.trip_status == TripStatus.COMPLETED)
        
        if start_date:
            query = query.filter(Trip.ended_at >= start_date)
        
        if end_date:
            query = query.filter(Trip.ended_at <= end_date)
        
        if driver_id:
            query = query.filter(Trip.assigned_driver_id == driver_id)
        
        return query.order_by(Trip.ended_at.desc()).offset(skip).limit(limit).all()
    
    def calculate_fare(
        self,
        db: Session,
        trip: Trip
    ) -> dict:
        """
        Calculate fare and chargeable distance for a trip with minimum KM rules
        
        Formula:
        If tripType = oneWay → chargeableDistance = max(distanceInKm, 130)
        If tripType = roundTrip → chargeableDistance = max(distanceInKm, 750)
        totalAmount = chargeableDistance × pricePerKm
        
        Returns:
            dict: { "fare": Decimal, "chargeable_distance": Decimal }
        """
        if trip.odo_start is None or trip.odo_end is None:
            return {"fare": Decimal("0"), "chargeable_distance": Decimal("0")}
        
        from app.models import VehicleTariffConfig
        
        # Get tariff config
        tariff = self._apply_soft_delete_filter(db.query(VehicleTariffConfig)).filter(
            VehicleTariffConfig.vehicle_type == trip.vehicle_type,
            VehicleTariffConfig.is_active == True
        ).first()
        
        if not tariff:
            return {"fare": Decimal("0"), "chargeable_distance": Decimal("0")}
        
        # Calculate actual distance
        actual_distance = Decimal(str(trip.odo_end - trip.odo_start))
        
        # Normalize trip type for robust comparison
        # Handles "One Way", "one_way", "oneWay", "round_trip", etc.
        trip_type_norm = (trip.trip_type or "").strip().lower().replace("_", "").replace(" ", "")
        
        # Apply Minimum KM Rules strictly from database tariff config
        if trip_type_norm in ["oneway", "onewaytrip"]:
            min_km = tariff.one_way_min_km or 0
            chargeable_distance = max(actual_distance, Decimal(str(min_km)))
            fare = chargeable_distance * tariff.one_way_per_km
            
        elif trip_type_norm in ["roundtrip", "roundtripway"]:
            min_km = tariff.round_trip_min_km or 0
            chargeable_distance = max(actual_distance, Decimal(str(min_km)))
            fare = chargeable_distance * tariff.round_trip_per_km
            
        else:
            # Default fallback (usually One Way logic)
            min_km = tariff.one_way_min_km or 0
            chargeable_distance = max(actual_distance, Decimal(str(min_km)))
            fare = chargeable_distance * tariff.one_way_per_km
            
        return {
            "fare": fare,
            "chargeable_distance": chargeable_distance
        }

    def calculate_total_amount(self, trip: Trip) -> Decimal:
        """
        Calculate total amount for a trip including fare and all extra charges
        """
        from decimal import Decimal
        
        fare = trip.fare or Decimal("0")
        waiting = trip.waiting_charges or Decimal("0")
        inter_state = trip.inter_state_permit_charges or Decimal("0")
        driver_allow = trip.driver_allowance or Decimal("0")
        luggage = trip.luggage_cost or Decimal("0")
        pet = trip.pet_cost or Decimal("0")
        toll = trip.toll_charges or Decimal("0")
        night = trip.night_allowance or Decimal("0")
        
        return fare + waiting + inter_state + driver_allow + luggage + pet + toll + night

    def update_status(
        self,
        db: Session,
        trip_id: str,
        new_status: str
    ) -> Optional[Trip]:
        """
        Update trip status with commission-only wallet deduction
        """
        from app.models import Driver, WalletTransaction
        from app.core.constants import DEFAULT_DRIVER_COMMISSION_PERCENT
        from decimal import Decimal, ROUND_HALF_UP
        import uuid
        
        trip = self.get(db, id=trip_id)
        if trip:
            trip.trip_status = new_status
            
            # Auto-set timestamps based on status
            if new_status == TripStatus.STARTED and not trip.started_at:
                trip.started_at = datetime.utcnow()
            elif new_status == TripStatus.COMPLETED and not trip.ended_at:
                trip.ended_at = datetime.utcnow()
                
                # Calculate fare if not set
                if not trip.fare:
                    fare_data = self.calculate_fare(db, trip)
                    trip.fare = fare_data["fare"]
                    trip.distance_km = fare_data["chargeable_distance"]
                
                # ✅ Calculate total amount (fare + extras)
                trip.total_amount = self.calculate_total_amount(trip)
                
                # ✅ ONLY DEBIT commission from wallet (Customer pays driver directly)
                if trip.fare and trip.assigned_driver_id:
                    # Get tariff for this vehicle type to use its specific commission rate
                    tariff = self._apply_soft_delete_filter(db.query(VehicleTariffConfig)).filter(
                        VehicleTariffConfig.vehicle_type == trip.vehicle_type,
                        VehicleTariffConfig.is_active == True
                    ).first()
                    
                    commission_rate = Decimal(str(tariff.driver_commission)) if tariff and tariff.driver_commission is not None else Decimal(str(DEFAULT_DRIVER_COMMISSION_PERCENT))
                    comm_pct = commission_rate / Decimal("100")
                    commission_amount = (trip.fare * comm_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    
                    # Get driver
                    driver = self._apply_soft_delete_filter(db.query(Driver)).filter(Driver.driver_id == trip.assigned_driver_id).first()
                    
                    if driver:
                        # Create DEBIT transaction for commission
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
            
            db.commit()
            db.refresh(trip)
        
        return trip
    
    def assign_driver(
        self,
        db: Session,
        trip_id: str,
        driver_id: str
    ) -> Optional[Trip]:
        """
        Assign a driver to a trip
        
        Args:
            db: Database session
            trip_id: Trip ID
            driver_id: Driver ID
        
        Returns:
            Updated trip or None
        """
        trip = self.get(db, id=trip_id)
        if trip:
            trip.assigned_driver_id = driver_id
            trip.trip_status = TripStatus.ASSIGNED
            db.commit()
            db.refresh(trip)
        
        return trip

    def unassign_driver(
        self,
        db: Session,
        trip_id: str
    ) -> Optional[Trip]:
        """
        Unassign driver from a trip and set status back to OPEN
        """
        trip = self.get(db, id=trip_id)
        if trip:
            trip.assigned_driver_id = None
            trip.trip_status = TripStatus.OPEN
            db.commit()
            db.refresh(trip)
        
        return trip
    
    def get_statistics(self, db: Session) -> dict:
        """
        Get trip statistics for dashboard
        
        Args:
            db: Database session
        
        Returns:
            Dictionary with trip statistics
        """
        total = self._apply_soft_delete_filter(db.query(Trip)).count()
        open_trips = self._apply_soft_delete_filter(db.query(Trip)).filter(Trip.trip_status == TripStatus.OPEN).count()
        assigned = self._apply_soft_delete_filter(db.query(Trip)).filter(Trip.trip_status == TripStatus.ASSIGNED).count()
        started = self._apply_soft_delete_filter(db.query(Trip)).filter(Trip.trip_status == TripStatus.STARTED).count()
        completed = self._apply_soft_delete_filter(db.query(Trip)).filter(Trip.trip_status == TripStatus.COMPLETED).count()
        cancelled = self._apply_soft_delete_filter(db.query(Trip)).filter(Trip.trip_status == TripStatus.CANCELLED).count()
        
        total_revenue = self._apply_soft_delete_filter(db.query(func.sum(Trip.fare))).filter(
            Trip.trip_status == TripStatus.COMPLETED
        ).scalar() or 0
        
        return {
            "total": total,
            "open": open_trips,
            "assigned": assigned,
            "started": started,
            "completed": completed,
            "cancelled": cancelled,
            "total_revenue": float(total_revenue)
        }


# Singleton instance
crud_trip = CRUDTrip(Trip)
