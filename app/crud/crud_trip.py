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
from app.core.constants import TripStatus


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
        return db.query(Trip).options(
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
        return db.query(Trip).filter(
            and_(
                Trip.trip_status == TripStatus.OPEN,
                Trip.assigned_driver_id == None
            )
        ).offset(skip).limit(limit).all()
    
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
        return db.query(Trip).filter(
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
        return db.query(Trip).filter(
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
        query = db.query(Trip).filter(
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
        query = db.query(Trip).filter(Trip.trip_status == TripStatus.COMPLETED)
        
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
    ) -> Optional[Decimal]:
        """
        Calculate fare for a trip with minimum KM rules
        
        Rules:
        - One Way: Min 130 KM
        - Round Trip: Min 250 KM
        """
        if trip.odo_start is None or trip.odo_end is None:
            return None
        
        from app.models import VehicleTariffConfig
        
        # Get tariff config
        tariff = db.query(VehicleTariffConfig).filter(
            VehicleTariffConfig.vehicle_type == trip.vehicle_type,
            VehicleTariffConfig.is_active == True
        ).first()
        
        if not tariff:
            return None
        
        # Calculate actual distance
        actual_distance = Decimal(trip.odo_end - trip.odo_start)
        
        # Apply Minimum KM Rules
        if trip.trip_type == "One Way":
            billable_distance = max(actual_distance, Decimal("130"))
            fare = billable_distance * tariff.one_way_per_km
        elif trip.trip_type == "Round Trip":
            billable_distance = max(actual_distance, Decimal("250"))
            fare = billable_distance * tariff.round_trip_per_km
        else:
            billable_distance = max(actual_distance, Decimal("130"))
            fare = billable_distance * tariff.one_way_per_km
            
        return fare

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
                    trip.fare = self.calculate_fare(db, trip)
                
                # ✅ ONLY DEBIT commission from wallet (Customer pays driver directly)
                if trip.fare and trip.assigned_driver_id:
                    # Get dynamic commission percentage
                    commission_percent = Decimal(str(DEFAULT_DRIVER_COMMISSION_PERCENT))
                    
                    tariff_config = db.query(VehicleTariffConfig).filter(
                        VehicleTariffConfig.vehicle_type == trip.vehicle_type,
                        VehicleTariffConfig.is_active == True
                    ).first()
                    
                    if tariff_config and tariff_config.driver_commission is not None:
                        commission_percent = tariff_config.driver_commission
                    
                    comm_pct = commission_percent / Decimal("100")
                    commission_amount = (trip.fare * comm_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    
                    # Get driver
                    driver = db.query(Driver).filter(Driver.driver_id == trip.assigned_driver_id).first()
                    
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
    
    def get_statistics(self, db: Session) -> dict:
        """
        Get trip statistics for dashboard
        
        Args:
            db: Database session
        
        Returns:
            Dictionary with trip statistics
        """
        total = db.query(Trip).count()
        open_trips = db.query(Trip).filter(Trip.trip_status == TripStatus.OPEN).count()
        assigned = db.query(Trip).filter(Trip.trip_status == TripStatus.ASSIGNED).count()
        started = db.query(Trip).filter(Trip.trip_status == TripStatus.STARTED).count()
        completed = db.query(Trip).filter(Trip.trip_status == TripStatus.COMPLETED).count()
        cancelled = db.query(Trip).filter(Trip.trip_status == TripStatus.CANCELLED).count()
        
        total_revenue = db.query(func.sum(Trip.fare)).filter(
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
