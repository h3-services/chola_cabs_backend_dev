from sqlalchemy.orm import Session
from app.models import DriverLiveLocation
from app.schemas import DriverLocationUpdate
from datetime import datetime

class CRUDDriverLocation:
    def get(self, db: Session, driver_id: str):
        return db.query(DriverLiveLocation).filter(DriverLiveLocation.driver_id == driver_id).first()

    def update(self, db: Session, driver_id: str, location: DriverLocationUpdate):
        db_location = self.get(db, driver_id)
        if db_location:
            db_location.latitude = location.latitude
            db_location.longitude = location.longitude
            db_location.last_updated = datetime.now()
        else:
            db_location = DriverLiveLocation(
                driver_id=driver_id,
                latitude=location.latitude,
                longitude=location.longitude,
                last_updated=datetime.now()
            )
            db.add(db_location)
        
        db.commit()
        db.refresh(db_location)
        return db_location

    def get_all(self, db: Session):
        """Get all driver locations with driver details"""
        from sqlalchemy.orm import joinedload
        return db.query(DriverLiveLocation).options(
            joinedload(DriverLiveLocation.driver)
        ).all()

driver_location = CRUDDriverLocation()
