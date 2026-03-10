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
from app.models import Driver, Vehicle, Trip
from app.crud.crud_driver import crud_driver
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_trip import crud_trip
import pathlib
from app.core.image_processing import compress_image

# Load environment variables with absolute path
env_path = pathlib.Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

router = APIRouter(prefix="/uploads", tags=["uploads"])

# Allowed file extensions - Synced with mobile formats
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".heic", ".webp"}

# Position mapping to handle various mobile labels
POSITION_MAPPING = {
    "front": "front", "frontview": "front", "front_view": "front",
    "back": "back", "backview": "back", "back_view": "back", "rear": "back",
    "left": "left", "leftview": "left", "left_view": "left", "leftsideview": "left", "left_side_view": "left",
    "right": "right", "rightview": "right", "right_view": "right", "rightsideview": "right", "right_side_view": "right",
    "inside": "inside", "insideview": "inside", "inside_view": "inside", "interior": "inside"
}

def save_file(file: UploadFile, folder: str, entity_type: str = None, entity_id: str = None, doc_type: str = None) -> str:
    """Save uploaded file and return URL"""
    # Use absolute path to ensure consistency
    UPLOAD_DIR = "/var/www/projects/client_side/chola_cabs/backend/cab_app/uploads"
    BASE_URL = "https://api.cholacabs.in/uploads"
    
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
    
    # Compress images, keep PDFs as is
    if ext in [".jpg", ".jpeg", ".png"]:
        try:
            compressed_buffer = compress_image(file)
            with open(file_path, "wb") as buffer:
                buffer.write(compressed_buffer.getvalue())
        except Exception as e:
            # Fallback to standard copy if compression fails
            file.file.seek(0)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
    else:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    return f"{BASE_URL}/{folder}/{filename}"

@router.post("/driver/{driver_id}/photo")
async def upload_driver_photo(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/photos", "driver", driver_id, "photo")
    driver.photo_url = url
    db.commit()
    return {"photo_url": url}

@router.post("/driver/{driver_id}/aadhar")
async def upload_aadhar(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/aadhar", "driver", driver_id, "aadhar")
    driver.aadhar_url = url
    db.commit()
    return {"aadhar_url": url}

@router.post("/driver/{driver_id}/licence")
async def upload_licence(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/licence", "driver", driver_id, "licence")
    driver.licence_url = url
    db.commit()
    return {"licence_url": url}

@router.post("/driver/{driver_id}/police_verification")
async def upload_police_verification(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/police_verification", "driver", driver_id, "police_verification")
    driver.police_verification_url = url
    db.commit()
    return {"police_verification_url": url}

@router.post("/trip/{trip_id}/odo_start")
async def upload_odo_start(trip_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    trip = crud_trip.get(db, id=trip_id)
    if not trip:
        raise HTTPException(404, "Trip not found")
    url = save_file(file, "trips/odo", "trip", trip_id, "odo_start")
    trip.odo_start_url = url
    db.commit()
    return {"odo_start_url": url}

@router.post("/trip/{trip_id}/odo_end")
async def upload_odo_end(trip_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    trip = crud_trip.get(db, id=trip_id)
    if not trip:
        raise HTTPException(404, "Trip not found")
    url = save_file(file, "trips/odo", "trip", trip_id, "odo_end")
    trip.odo_end_url = url
    db.commit()
    return {"odo_end_url": url}

@router.post("/vehicle/{vehicle_id}/rc")
async def upload_rc(vehicle_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    url = save_file(file, "vehicles/rc", "vehicle", vehicle_id, "rc")
    vehicle.rc_book_url = url
    db.commit()
    return {"rc_book_url": url}

@router.post("/vehicle/{vehicle_id}/fc")
async def upload_fc(vehicle_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    url = save_file(file, "vehicles/fc", "vehicle", vehicle_id, "fc")
    vehicle.fc_certificate_url = url
    db.commit()
    return {"fc_certificate_url": url}

@router.post("/vehicle/{vehicle_id}/photo/{position}")
async def upload_vehicle_photo(vehicle_id: str, position: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    # Normalize position string
    normalized_pos = POSITION_MAPPING.get(position.lower().replace(" ", "_"))
    if not normalized_pos:
        raise HTTPException(400, f"Invalid position: {position}. Allowed: {', '.join(set(POSITION_MAPPING.values()))}")
    
    url = save_file(file, f"vehicles/{normalized_pos}", "vehicle", vehicle_id, normalized_pos)
    setattr(vehicle, f"vehicle_{normalized_pos}_url", url)
    db.commit()
    return {f"vehicle_{normalized_pos}_url": url}

# RE-UPLOAD ENDPOINTS (PUT methods)

@router.put("/driver/{driver_id}/photo")
async def reupload_driver_photo(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/photos", "driver", driver_id, "photo")
    driver.photo_url = url
    db.commit()
    return {"photo_url": url, "message": "Driver photo re-uploaded successfully"}

@router.put("/driver/{driver_id}/aadhar")
async def reupload_aadhar(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/aadhar", "driver", driver_id, "aadhar")
    driver.aadhar_url = url
    db.commit()
    return {"aadhar_url": url, "message": "Aadhar document re-uploaded successfully"}

@router.put("/driver/{driver_id}/licence")
async def reupload_licence(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    url = save_file(file, "drivers/licence", "driver", driver_id, "licence")
    driver.licence_url = url
    db.commit()
    return {"licence_url": url, "message": "Licence document re-uploaded successfully"}

@router.put("/driver/{driver_id}/police_verification")
async def reupload_police_verification(driver_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")
    url = save_file(file, "drivers/police_verification", "driver", driver_id, "police_verification")
    driver.police_verification_url = url
    db.commit()
    return {"police_verification_url": url}


@router.put("/vehicle/{vehicle_id}/rc")
async def reupload_rc(vehicle_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    url = save_file(file, "vehicles/rc", "vehicle", vehicle_id, "rc")
    vehicle.rc_book_url = url
    db.commit()
    return {"rc_book_url": url, "message": "RC book re-uploaded successfully"}

@router.put("/vehicle/{vehicle_id}/fc")
async def reupload_fc(vehicle_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    url = save_file(file, "vehicles/fc", "vehicle", vehicle_id, "fc")
    vehicle.fc_certificate_url = url
    db.commit()
    return {"fc_certificate_url": url, "message": "FC certificate re-uploaded successfully"}

@router.put("/vehicle/{vehicle_id}/photo/{position}")
async def reupload_vehicle_photo(vehicle_id: str, position: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    vehicle = crud_vehicle.get(db, id=vehicle_id)
    if not vehicle:
        raise HTTPException(404, "Vehicle not found")
    
    # Normalize position string
    normalized_pos = POSITION_MAPPING.get(position.lower().replace(" ", "_"))
    if not normalized_pos:
        raise HTTPException(400, f"Invalid position: {position}. Allowed: {', '.join(set(POSITION_MAPPING.values()))}")
    
    url = save_file(file, f"vehicles/{normalized_pos}", "vehicle", vehicle_id, normalized_pos)
    setattr(vehicle, f"vehicle_{normalized_pos}_url", url)
    db.commit()
    return {f"vehicle_{normalized_pos}_url": url, "message": f"Vehicle {normalized_pos} photo re-uploaded successfully"}
