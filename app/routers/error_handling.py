"""
Error Handling API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ErrorHandling, Driver
from app.schemas import ErrorHandlingCreate, ErrorHandlingResponse

router = APIRouter(prefix="/errors", tags=["error-handling"])

@router.get("/", response_model=List[ErrorHandlingResponse])
def get_all_errors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all error logs"""
    try:
        errors = db.query(ErrorHandling).offset(skip).limit(limit).all()
        return errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{error_id}", response_model=ErrorHandlingResponse)
def get_error_by_id(error_id: str, db: Session = Depends(get_db)):
    """Get error log by ID"""
    try:
        error = db.query(ErrorHandling).filter(ErrorHandling.error_id == error_id).first()
        if not error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error log not found"
            )
        return error
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ErrorHandlingResponse)
def create_error_log(error: ErrorHandlingCreate, db: Session = Depends(get_db)):
    """Create a new error log"""
    import uuid
    
    try:
        # Check if error_code already exists
        existing_error = db.query(ErrorHandling).filter(ErrorHandling.error_code == error.error_code).first()
        if existing_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error code {error.error_code} already exists"
            )
        
        # Create error with UUID
        error_data = error.model_dump()
        error_data["error_id"] = str(uuid.uuid4())
        
        db_error = ErrorHandling(**error_data)
        db.add(db_error)
        db.commit()
        db.refresh(db_error)
        return db_error
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/assign-to-driver")
def assign_error_to_driver(
    driver_id: str,
    error_code: int,
    db: Session = Depends(get_db)
):
    """Admin assigns error to driver (for document issues)"""
    try:
        # Get driver
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Get error details
        error = db.query(ErrorHandling).filter(ErrorHandling.error_code == error_code).first()
        if not error:
            raise HTTPException(status_code=404, detail="Error code not found")
        
        # Initialize errors JSON if needed
        if driver.errors is None:
            driver.errors = {"error_codes": [], "details": {}}
        
        # Add error if not already present
        if error_code not in driver.errors.get("error_codes", []):
            driver.errors["error_codes"].append(error_code)
            driver.errors["details"][str(error_code)] = {
                "error_type": error.error_type,
                "error_description": error.error_description,
                "assigned_at": error.created_at.isoformat()
            }
        
        db.commit()
        db.refresh(driver)
        
        return {
            "message": f"Error {error_code} assigned to driver {driver_id}",
            "driver_errors": driver.errors
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/driver/{driver_id}")
def get_driver_errors(driver_id: str, db: Session = Depends(get_db)):
    """Get all errors for a driver (for driver app)"""
    try:
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        if not driver.errors or not driver.errors.get("error_codes"):
            return {
                "driver_id": driver_id,
                "driver_name": driver.name,
                "has_errors": False,
                "errors": []
            }
        
        # Get full error details
        error_list = []
        for error_code in driver.errors.get("error_codes", []):
            error_detail = driver.errors.get("details", {}).get(str(error_code), {})
            error_list.append({
                "error_code": error_code,
                "error_type": error_detail.get("error_type"),
                "error_description": error_detail.get("error_description"),
                "assigned_at": error_detail.get("assigned_at")
            })
        
        return {
            "driver_id": driver_id,
            "driver_name": driver.name,
            "has_errors": len(error_list) > 0,
            "error_count": len(error_list),
            "errors": error_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/remove-from-driver")
def remove_error_from_driver(
    driver_id: str,
    error_code: int,
    db: Session = Depends(get_db)
):
    """Admin removes error from driver"""
    try:
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        if not driver.errors or error_code not in driver.errors.get("error_codes", []):
            raise HTTPException(status_code=404, detail="Error not assigned to this driver")
        
        # Remove error
        driver.errors["error_codes"].remove(error_code)
        if str(error_code) in driver.errors.get("details", {}):
            del driver.errors["details"][str(error_code)]
        
        db.commit()
        db.refresh(driver)
        
        return {
            "message": f"Error {error_code} removed from driver {driver_id}",
            "remaining_errors": len(driver.errors.get("error_codes", []))
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{error_id}")
def delete_error_log(error_id: str, db: Session = Depends(get_db)):
    """Delete an error log"""
    try:
        error = db.query(ErrorHandling).filter(ErrorHandling.error_id == error_id).first()
        if not error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error log not found"
            )
        
        db.delete(error)
        db.commit()
        
        return {"message": "Error log deleted successfully", "error_id": error_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
