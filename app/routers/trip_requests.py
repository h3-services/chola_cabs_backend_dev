"""
Trip Driver Requests API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TripDriverRequest, Trip, Driver
from app.schemas import TripDriverRequestCreate, TripDriverRequestUpdate, TripDriverRequestResponse

router = APIRouter(prefix="/trip-requests", tags=["trip-requests"])

@router.get("/")
def get_all_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all trip driver requests"""
    requests = db.query(TripDriverRequest).offset(skip).limit(limit).all()
    result = []
    for req in requests:
        driver = db.query(Driver).filter(Driver.driver_id == req.driver_id).first()
        trip = db.query(Trip).filter(Trip.trip_id == req.trip_id).first()
        result.append({
            "request_id": req.request_id,
            "trip_id": req.trip_id,
            "driver_id": req.driver_id,
            "driver_name": driver.name if driver else None,
            "customer_name": trip.customer_name if trip else None,
            "status": req.status,
            "created_at": req.created_at.isoformat() if req.created_at else None,
            "updated_at": req.updated_at.isoformat() if req.updated_at else None
        })
    return result

@router.get("/{request_id}")
def get_request_by_id(request_id: str, db: Session = Depends(get_db)):
    """Get trip driver request by ID"""
    request = db.query(TripDriverRequest).filter(TripDriverRequest.request_id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    driver = db.query(Driver).filter(Driver.driver_id == request.driver_id).first()
    trip = db.query(Trip).filter(Trip.trip_id == request.trip_id).first()
    
    return {
        "request_id": request.request_id,
        "trip_id": request.trip_id,
        "driver_id": request.driver_id,
        "driver_name": driver.name if driver else None,
        "customer_name": trip.customer_name if trip else None,
        "status": request.status,
        "created_at": request.created_at.isoformat() if request.created_at else None,
        "updated_at": request.updated_at.isoformat() if request.updated_at else None
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_request(trip_id: str, driver_id: str, db: Session = Depends(get_db)):
    """Driver creates request for a trip"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.trip_status != "OPEN":
        raise HTTPException(status_code=400, detail="Trip is not available")
    
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Check if request already exists
    existing = db.query(TripDriverRequest).filter(
        TripDriverRequest.trip_id == trip_id,
        TripDriverRequest.driver_id == driver_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Request already exists")
    
    import uuid
    request = TripDriverRequest(
        request_id=str(uuid.uuid4()),
        trip_id=trip_id,
        driver_id=driver_id,
        status="PENDING"
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    return {
        "message": "Trip request created",
        "request_id": request.request_id,
        "trip_id": trip_id,
        "driver_id": driver_id,
        "status": "PENDING"
    }

@router.patch("/{request_id}/status")
def update_request_status(
    request_id: str,
    new_status: str,
    db: Session = Depends(get_db)
):
    """Update request status (PENDING/ACCEPTED/REJECTED/CANCELLED)"""
    if new_status not in ["PENDING", "ACCEPTED", "REJECTED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    request = db.query(TripDriverRequest).filter(
        TripDriverRequest.request_id == request_id
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request.status = new_status
    db.commit()
    db.refresh(request)
    
    return {
        "message": f"Request status updated to {new_status}",
        "request_id": request_id,
        "status": new_status
    }

@router.patch("/{request_id}/approve")
def approve_request(request_id: str, db: Session = Depends(get_db)):
    """Admin approves request and assigns driver to trip"""
    request = db.query(TripDriverRequest).filter(
        TripDriverRequest.request_id == request_id
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    trip = db.query(Trip).filter(Trip.trip_id == request.trip_id).first()
    driver = db.query(Driver).filter(Driver.driver_id == request.driver_id).first()
    
    if trip.assigned_driver_id:
        raise HTTPException(status_code=400, detail="Trip already assigned")
    
    # Allow admin to assign both available and unavailable drivers
    # No availability check - admin has full control
    
    # Assign driver to trip
    trip.assigned_driver_id = request.driver_id
    trip.trip_status = "ASSIGNED"
    driver.is_available = False
    request.status = "ACCEPTED"
    
    # Reject other pending requests for this trip
    other_requests = db.query(TripDriverRequest).filter(
        TripDriverRequest.trip_id == request.trip_id,
        TripDriverRequest.request_id != request_id,
        TripDriverRequest.status == "PENDING"
    ).all()
    
    for other in other_requests:
        other.status = "REJECTED"
    
    db.commit()
    
    return {
        "message": "Request approved and driver assigned",
        "trip_id": trip.trip_id,
        "driver_id": driver.driver_id,
        "driver_name": driver.name
    }

@router.get("/trip/{trip_id}")
def get_requests_by_trip(trip_id: str, db: Session = Depends(get_db)):
    """Get all requests for a specific trip"""
    requests = db.query(TripDriverRequest).filter(
        TripDriverRequest.trip_id == trip_id
    ).all()
    
    result = []
    for req in requests:
        driver = db.query(Driver).filter(Driver.driver_id == req.driver_id).first()
        result.append({
            "request_id": req.request_id,
            "driver_id": req.driver_id,
            "driver_name": driver.name if driver else None,
            "driver_phone": str(driver.phone_number) if driver else None,
            "status": req.status,
            "created_at": req.created_at.isoformat() if req.created_at else None
        })
    return result

@router.get("/driver/{driver_id}")
def get_requests_by_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get all requests by a specific driver"""
    requests = db.query(TripDriverRequest).filter(
        TripDriverRequest.driver_id == driver_id
    ).all()
    
    result = []
    for req in requests:
        trip = db.query(Trip).filter(Trip.trip_id == req.trip_id).first()
        result.append({
            "request_id": req.request_id,
            "trip_id": req.trip_id,
            "customer_name": trip.customer_name if trip else None,
            "pickup_address": trip.pickup_address if trip else None,
            "drop_address": trip.drop_address if trip else None,
            "status": req.status,
            "created_at": req.created_at.isoformat() if req.created_at else None
        })
    return result

@router.patch("/{request_id}/cancel")
def cancel_request(request_id: str, db: Session = Depends(get_db)):
    """Cancel a trip driver request"""
    request = db.query(TripDriverRequest).filter(
        TripDriverRequest.request_id == request_id
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status in ["ACCEPTED", "REJECTED"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel request with status {request.status}")
    
    request.status = "CANCELLED"
    db.commit()
    db.refresh(request)
    
    return {
        "message": "Request cancelled successfully",
        "request_id": request_id,
        "status": "CANCELLED"
    }

@router.delete("/{request_id}")
def delete_request(request_id: str, db: Session = Depends(get_db)):
    """Delete a trip driver request"""
    request = db.query(TripDriverRequest).filter(
        TripDriverRequest.request_id == request_id
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    db.delete(request)
    db.commit()
    
    return {
        "message": "Request deleted successfully",
        "request_id": request_id
    }