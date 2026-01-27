"""
CRUD operations for Driver model
Optimized for production with eager loading and caching support
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.crud.base import CRUDBase
from app.models import Driver
from app.schemas import DriverCreate, DriverUpdate


class CRUDDriver(CRUDBase[Driver, DriverCreate, DriverUpdate]):
    """
    CRUD operations for Driver model with production optimizations
    """
    
    def get_by_phone(self, db: Session, phone_number: int) -> Optional[Driver]:
        """
        Get driver by phone number
        
        Args:
            db: Database session
            phone_number: Driver's phone number
        
        Returns:
            Driver instance or None
        """
        return db.query(Driver).filter(Driver.phone_number == phone_number).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[Driver]:
        """
        Get driver by email
        
        Args:
            db: Database session
            email: Driver's email
        
        Returns:
            Driver instance or None
        """
        return db.query(Driver).filter(Driver.email == email).first()
    
    def get_available_drivers(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Driver]:
        """
        Get all available drivers (approved and available)
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            List of available drivers
        """
        return db.query(Driver).filter(
            and_(
                Driver.is_available == True,
                Driver.is_approved == True
            )
        ).offset(skip).limit(limit).all()
    
    def get_pending_approval(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Driver]:
        """
        Get drivers pending approval
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            List of drivers pending approval
        """
        return db.query(Driver).filter(
            Driver.is_approved == False
        ).offset(skip).limit(limit).all()
    
    def get_with_vehicles(self, db: Session, driver_id: str) -> Optional[Driver]:
        """
        Get driver with all vehicles (eager loaded)
        
        Args:
            db: Database session
            driver_id: Driver ID
        
        Returns:
            Driver with vehicles or None
        """
        return db.query(Driver).options(
            joinedload(Driver.vehicles)
        ).filter(Driver.driver_id == driver_id).first()
    
    def get_with_trips(
        self,
        db: Session,
        driver_id: str,
        limit: int = 10
    ) -> Optional[Driver]:
        """
        Get driver with recent trips (eager loaded)
        
        Args:
            db: Database session
            driver_id: Driver ID
            limit: Maximum number of trips to load
        
        Returns:
            Driver with trips or None
        """
        from app.models import Trip
        
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if driver:
            # Load recent trips separately to apply limit
            driver.recent_trips = db.query(Trip).filter(
                Trip.assigned_driver_id == driver_id
            ).order_by(Trip.created_at.desc()).limit(limit).all()
        
        return driver
    
    def update_availability(
        self,
        db: Session,
        driver_id: str,
        is_available: bool
    ) -> Optional[Driver]:
        """
        Update driver availability status
        
        Args:
            db: Database session
            driver_id: Driver ID
            is_available: New availability status
        
        Returns:
            Updated driver or None
        """
        driver = self.get(db, id=driver_id)
        if driver:
            driver.is_available = is_available
            db.commit()
            db.refresh(driver)
        return driver
    
    def update_kyc_status(
        self,
        db: Session,
        driver_id: str,
        kyc_status: str
    ) -> Optional[Driver]:
        """
        Update driver KYC status
        
        Args:
            db: Database session
            driver_id: Driver ID
            kyc_status: New KYC status (pending/approved/rejected)
        
        Returns:
            Updated driver or None
        """
        driver = self.get(db, id=driver_id)
        if driver:
            driver.kyc_verified = kyc_status
            db.commit()
            db.refresh(driver)
        return driver
    
    def update_wallet_balance(
        self,
        db: Session,
        driver_id: str,
        new_balance: float
    ) -> Optional[Driver]:
        """
        Update driver wallet balance
        
        Args:
            db: Database session
            driver_id: Driver ID
            new_balance: New wallet balance
        
        Returns:
            Updated driver or None
        """
        driver = self.get(db, id=driver_id)
        if driver:
            driver.wallet_balance = new_balance
            db.commit()
            db.refresh(driver)
        return driver
    
    def search(
        self,
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Driver]:
        """
        Search drivers by name, phone, or email
        
        Args:
            db: Database session
            query: Search query string
            skip: Number of records to skip
            limit: Maximum number of records
        
        Returns:
            List of matching drivers
        """
        search_pattern = f"%{query}%"
        return db.query(Driver).filter(
            or_(
                Driver.name.ilike(search_pattern),
                Driver.email.ilike(search_pattern),
                Driver.phone_number.like(search_pattern)
            )
        ).offset(skip).limit(limit).all()


# Singleton instance
crud_driver = CRUDDriver(Driver)
