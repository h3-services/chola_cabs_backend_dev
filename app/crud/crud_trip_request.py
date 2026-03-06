"""
CRUD operations for TripDriverRequest model
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models import TripDriverRequest

class CRUDTripRequest(CRUDBase[TripDriverRequest, None, None]):
    """CRUD operations for TripDriverRequest model"""
    
    def get_by_trip(self, db: Session, trip_id: str) -> List[TripDriverRequest]:
        """Get all requests for a trip"""
        return self._apply_soft_delete_filter(db.query(TripDriverRequest)).filter(
            TripDriverRequest.trip_id == trip_id
        ).all()
    
    def get_by_driver(self, db: Session, driver_id: str) -> List[TripDriverRequest]:
        """Get all requests for a driver"""
        return self._apply_soft_delete_filter(db.query(TripDriverRequest)).filter(
            TripDriverRequest.driver_id == driver_id
        ).all()

crud_trip_request = CRUDTripRequest(TripDriverRequest)
