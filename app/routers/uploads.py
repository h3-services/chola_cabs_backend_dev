"""
File upload router for KYC documents and photos
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from dotenv import load_dotenv
from app.database import get_db
from app.models import Driver, Vehicle
import pathlib

# Load environment variables with absolute path
env_path = pathlib.Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}

def save_file(file: UploadFile, folder: str, entity_type: str = None, entity_id: str = None, doc_type: str = None) -> str:
    """Save uploaded file and return URL"""
    # Load environment variables inside function to ensure .env is loaded
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/root/chola_cabs_backend_dev/uploads")
    BASE_URL = os.getenv("BASE_URL", "https://api.cholacabs.in/uploads")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")
    
    # Generate filename with entity info if provided
    if entity_type and entity_id and doc_type:
        filename = f"{entity_type}_{entity_id}_{doc_type}{ext}"
    else:
        # Remove timestamp prefix if present
        filename = file.filename
        if '_' in filename and len(filename.split('_')[0]) == 8:
            parts = filename.split('_')
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
                filename = '_'.join(parts[2:])
    
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

# RE-UPLOAD ENDPOINTS (PUT methods)

@router.put("/driver/{driver_id}/photo")
async def reupload_driver_photo(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/photos", "driver", driver_id, "photo")
    driver.photo_url = url
    db.commit()
    return {"photo_url": url, "message": "Driver photo re-uploaded successfully"}

@router.put("/driver/{driver_id}/aadhar")
async def reupload_aadhar(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/aadhar", "driver", driver_id, "aadhar")
    driver.aadhar_url = url
    db.commit()
    return {"aadhar_url": url, "message": "Aadhar document re-uploaded successfully"}

@router.put("/driver/{driver_id}/licence")
async def reupload_licence(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/licence", "driver", driver_id, "licence")
    driver.licence_url = url
    db.commit()
    return {"licence_url": url, "message": "Licence document re-uploaded successfully"}

@router.put("/vehicle/{vehicle_id}/rc")
async def reupload_rc(vehicle_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    url = save_file(file, "vehicles/rc", "vehicle", vehicle_id, "rc")
    vehicle.rc_book_url = url
    db.commit()
    return {"rc_book_url": url, "message": "RC book re-uploaded successfully"}

@router.put("/vehicle/{vehicle_id}/fc")
async def reupload_fc(vehicle_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    url = save_file(file, "vehicles/fc", "vehicle", vehicle_id, "fc")
    vehicle.fc_certificate_url = url
    db.commit()
    return {"fc_certificate_url": url, "message": "FC certificate re-uploaded successfully"}

@router.put("/vehicle/{vehicle_id}/photo/{position}")
async def reupload_vehicle_photo(vehicle_id: str, position: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    if position not in ["front", "back", "left", "right"]:
        raise HTTPException(400, "Invalid position")
    
    url = save_file(file, f"vehicles/{position}", "vehicle", vehicle_id, position)
    setattr(vehicle, f"vehicle_{position}_url", url)
    db.commit()
    return {f"vehicle_{position}_url": url, "message": f"Vehicle {position} photo re-uploaded successfully"}
