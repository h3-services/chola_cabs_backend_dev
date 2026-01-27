"""
CRUD operations for Vehicle model
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models import Vehicle
from app.schemas import VehicleCreate, VehicleUpdate


class CRUDVehicle(CRUDBase[Vehicle, VehicleCreate, VehicleUpdate]):
    """CRUD operations for Vehicle model"""
    
    def get_by_driver(self, db: Session, driver_id: str) -> List[Vehicle]:
        """Get all vehicles for a driver"""
        return db.query(Vehicle).filter(Vehicle.driver_id == driver_id).all()
    
    def get_by_number(self, db: Session, vehicle_number: str) -> Optional[Vehicle]:
        """Get vehicle by vehicle number"""
        return db.query(Vehicle).filter(Vehicle.vehicle_number == vehicle_number).first()
    
    def get_approved(self, db: Session, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        """Get approved vehicles"""
        return db.query(Vehicle).filter(
            Vehicle.vehicle_approved == True
        ).offset(skip).limit(limit).all()
    
    def get_with_driver(self, db: Session, vehicle_id: str) -> Optional[Vehicle]:
        """Get vehicle with driver details (eager loaded)"""
        return db.query(Vehicle).options(
            joinedload(Vehicle.driver)
        ).filter(Vehicle.vehicle_id == vehicle_id).first()


crud_vehicle = CRUDVehicle(Vehicle)
