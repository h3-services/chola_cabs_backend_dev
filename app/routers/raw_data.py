"""
Raw data endpoints to bypass validation
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/raw", tags=["raw-data"])

@router.get("/drivers")
def get_drivers_raw(db: Session = Depends(get_db)):
    """Get drivers with raw SQL to bypass validation"""
    result = db.execute(text("SELECT * FROM drivers LIMIT 10"))
    drivers = []
    for row in result:
        drivers.append({
            "driver_id": row[0],
            "name": row[1],
            "phone_number": str(row[2]),
            "email": row[3],
            "kyc_verified": row[4],
            "primary_location": row[5],
            "wallet_balance": float(row[7]) if row[7] else 0.0,
            "is_available": row[12],
            "is_approved": row[13]
        })
    return drivers

@router.get("/vehicles")
def get_vehicles_raw(db: Session = Depends(get_db)):
    """Get vehicles with raw SQL"""
    result = db.execute(text("SELECT * FROM vehicles LIMIT 10"))
    vehicles = []
    for row in result:
        vehicles.append({
            "vehicle_id": row[0],
            "driver_id": row[1],
            "vehicle_type": row[2],
            "vehicle_brand": row[3],
            "vehicle_model": row[4],
            "vehicle_number": row[7],
            "vehicle_approved": row[17]
        })
    return vehicles

@router.get("/trips")
def get_trips_raw(db: Session = Depends(get_db)):
    """Get trips with raw SQL"""
    result = db.execute(text("SELECT * FROM trips LIMIT 10"))
    trips = []
    for row in result:
        trips.append({
            "trip_id": row[0],
            "customer_name": row[1],
            "customer_phone": row[2],
            "pickup_address": row[3],
            "drop_address": row[4],
            "trip_type": row[5],
            "vehicle_type": row[6],
            "trip_status": row[8]
        })
    return trips