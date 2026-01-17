"""
Error Handling API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ErrorHandling, Driver, Vehicle, Trip
from app.schemas import ErrorHandlingCreate, ErrorHandlingResponse

router = APIRouter(prefix="/errors", tags=["error-handling"])

@router.get("/", response_model=List[ErrorHandlingResponse])
def get_all_errors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all error logs"""
    errors = db.query(ErrorHandling).offset(skip).limit(limit).all()
    return errors

@router.get("/{error_id}", response_model=ErrorHandlingResponse)
def get_error_by_id(error_id: int, db: Session = Depends(get_db)):
    """Get error log by ID"""
    error = db.query(ErrorHandling).filter(ErrorHandling.error_id == error_id).first()
    if not error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error log not found"
        )
    return error

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ErrorHandlingResponse)
def create_error_log(error: ErrorHandlingCreate, db: Session = Depends(get_db)):
    """Create a new error log"""
    # Check if error_code already exists
    existing_error = db.query(ErrorHandling).filter(ErrorHandling.error_code == error.error_code).first()
    if existing_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error code {error.error_code} already exists"
        )
    
    db_error = ErrorHandling(**error.dict())
    db.add(db_error)
    db.commit()
    db.refresh(db_error)
    return db_error

@router.post("/link-error")
def link_error_to_entity(
    entity_type: str,  # "driver" or "vehicle" or "trip"
    entity_id: str,
    error_id: int,
    db: Session = Depends(get_db)
):
    """Link an error from error_handling table to driver/vehicle/trip"""
    # Get the error details
    error = db.query(ErrorHandling).filter(ErrorHandling.error_id == error_id).first()
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    
    # Update the entity's errors field
    if entity_type == "driver":
        entity = db.query(Driver).filter(Driver.driver_id == entity_id).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Driver not found")
    elif entity_type == "vehicle":
        entity = db.query(Vehicle).filter(Vehicle.vehicle_id == entity_id).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Vehicle not found")
    elif entity_type == "trip":
        entity = db.query(Trip).filter(Trip.trip_id == entity_id).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Trip not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid entity_type. Use: driver, vehicle, trip")
    
    # Add error to entity's errors JSON field
    if entity.errors is None:
        entity.errors = {"error_codes": [], "details": {}}
    
    # Initialize structure if needed
    if "error_codes" not in entity.errors:
        entity.errors["error_codes"] = []
    if "details" not in entity.errors:
        entity.errors["details"] = {}
    
    # Add error code to list if not already present
    if error.error_code not in entity.errors["error_codes"]:
        entity.errors["error_codes"].append(error.error_code)
    
    # Store error details
    entity.errors["details"][str(error.error_code)] = {
        "error_id": error_id,
        "error_type": error.error_type,
        "error_description": error.error_description,
        "linked_at": error.created_at.isoformat()
    }
    
    db.commit()
    db.refresh(entity)
    
    return {
        "message": f"Error {error_id} (code: {error.error_code}) linked to {entity_type} {entity_id}",
        "error_details": {
            "error_id": error_id,
            "error_code": error.error_code,
            "error_type": error.error_type
        },
        "current_error_codes": ",".join(map(str, entity.errors["error_codes"]))
    }

@router.delete("/unlink-error")
def unlink_error_from_entity(
    entity_type: str,
    entity_id: str,
    error_id: int,
    db: Session = Depends(get_db)
):
    """Remove error link from driver/vehicle/trip"""
    # Get the entity
    if entity_type == "driver":
        entity = db.query(Driver).filter(Driver.driver_id == entity_id).first()
    elif entity_type == "vehicle":
        entity = db.query(Vehicle).filter(Vehicle.vehicle_id == entity_id).first()
    elif entity_type == "trip":
        entity = db.query(Trip).filter(Trip.trip_id == entity_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid entity_type")
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"{entity_type.title()} not found")
    
    # Remove error from errors JSON
    if entity.errors and "error_codes" in entity.errors and "details" in entity.errors:
        # Find error by error_id
        error_to_remove = db.query(ErrorHandling).filter(ErrorHandling.error_id == error_id).first()
        if error_to_remove and error_to_remove.error_code in entity.errors["error_codes"]:
            # Remove from error_codes array
            entity.errors["error_codes"].remove(error_to_remove.error_code)
            # Remove from details
            if str(error_to_remove.error_code) in entity.errors["details"]:
                del entity.errors["details"][str(error_to_remove.error_code)]
            
            db.commit()
            db.refresh(entity)
            return {
                "message": f"Error {error_id} (code: {error_to_remove.error_code}) unlinked from {entity_type} {entity_id}",
                "remaining_error_codes": ",".join(map(str, entity.errors["error_codes"])) if entity.errors["error_codes"] else "None"
            }
        else:
            raise HTTPException(status_code=404, detail="Error not linked to this entity")
    else:
        raise HTTPException(status_code=404, detail="No errors linked to this entity")

@router.get("/entity-errors/{entity_type}/{entity_id}")
def get_entity_errors(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    """Get all errors for a specific entity with full error details"""
    # Get the entity
    if entity_type == "driver":
        entity = db.query(Driver).filter(Driver.driver_id == entity_id).first()
    elif entity_type == "vehicle":
        entity = db.query(Vehicle).filter(Vehicle.vehicle_id == entity_id).first()
    elif entity_type == "trip":
        entity = db.query(Trip).filter(Trip.trip_id == entity_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid entity_type")
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"{entity_type.title()} not found")
    
    if not entity.errors or "error_codes" not in entity.errors:
        return {
            "entity_id": entity_id, 
            "entity_type": entity_type, 
            "error_codes": "",
            "errors": {}
        }
    
    # Get full error details from error_handling table
    result_errors = {}
    error_codes_list = entity.errors.get("error_codes", [])
    error_details = entity.errors.get("details", {})
    
    for error_code in error_codes_list:
        error = db.query(ErrorHandling).filter(ErrorHandling.error_code == error_code).first()
        if error:
            result_errors[str(error_code)] = {
                "error_id": error.error_id,
                "error_code": error.error_code,
                "error_type": error.error_type,
                "error_description": error.error_description,
                "created_at": error.created_at.isoformat(),
                "linked_at": error_details.get(str(error_code), {}).get("linked_at")
            }
    
    return {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "error_codes": ",".join(map(str, error_codes_list)),
        "errors": result_errors
    }

@router.delete("/{error_id}")
def delete_error_log(error_id: int, db: Session = Depends(get_db)):
    """Delete an error log"""
    error = db.query(ErrorHandling).filter(ErrorHandling.error_id == error_id).first()
    if not error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error log not found"
        )
    
    db.delete(error)
    db.commit()
    
    return {"message": "Error log deleted successfully", "error_id": error_id}
