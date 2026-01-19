"""
File upload router for KYC documents and photos
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
from app.database import get_db
from app.models import Driver, Vehicle

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}

def save_file(file: UploadFile, folder: str) -> str:
    """Save uploaded file and return URL"""
    # Load environment variables inside function to ensure .env is loaded
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/root/cab_app/uploads")
    BASE_URL = os.getenv("BASE_URL", "https://api.cholacabs.in/uploads")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    folder_path = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)
    
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return f"{BASE_URL}/{folder}/{filename}"

@router.post("/driver/{driver_id}/photo")
async def upload_driver_photo(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/photos")
    driver.photo_url = url
    db.commit()
    return {"photo_url": url}

@router.post("/driver/{driver_id}/aadhar")
async def upload_aadhar(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/aadhar")
    driver.aadhar_url = url
    db.commit()
    return {"aadhar_url": url}

@router.post("/driver/{driver_id}/licence")
async def upload_licence(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/licence")
    driver.licence_url = url
    db.commit()
    return {"licence_url": url}

@router.post("/vehicle/{vehicle_id}/rc")
async def upload_rc(vehicle_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    url = save_file(file, "vehicles/rc")
    vehicle.rc_book_url = url
    db.commit()
    return {"rc_book_url": url}

@router.post("/vehicle/{vehicle_id}/fc")
async def upload_fc(vehicle_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    url = save_file(file, "vehicles/fc")
    vehicle.fc_certificate_url = url
    db.commit()
    return {"fc_certificate_url": url}

@router.post("/vehicle/{vehicle_id}/photo/{position}")
async def upload_vehicle_photo(vehicle_id: str, position: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    if position not in ["front", "back", "left", "right"]:
        raise HTTPException(400, "Invalid position")
    
    url = save_file(file, f"vehicles/{position}")
    setattr(vehicle, f"vehicle_{position}_url", url)
    db.commit()
    return {f"vehicle_{position}_url": url}
