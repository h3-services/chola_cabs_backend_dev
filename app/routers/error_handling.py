"""
Error Handling API endpoints
"""
from typing import List, Optional
import uuid
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, flag_modified
from app.database import get_db
from app.models import ErrorHandling, Driver
from app.schemas import ErrorHandlingCreate, ErrorHandlingResponse

# Document type mapping
DOCUMENT_TYPE_LABELS = {
    "licence": "Driving Licence",
    "aadhar": "Aadhar Card",
    "photo": "Profile Photo",
    "rc": "RC Book",
    "fc": "FC Certificate",
    "vehicle_photo": "Vehicle Photos"
}

logger = logging.getLogger(__name__)

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
        logger.info(f"Retrieved {len(errors)} errors from database")
        return errors
    except Exception as e:
        logger.error(f"Database error in get_all_errors: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

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

@router.post("/review-driver-documents")
def review_driver_documents(
    driver_id: str,
    action: str,  # "approve" or "reject"
    selected_error_codes: List[int] = None,  # Error codes selected by admin checkboxes
    db: Session = Depends(get_db)
):
    """Admin reviews driver documents and assigns predefined errors if rejecting"""
    try:
        # Get driver
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        if action == "approve":
            # Approve driver and clear any existing errors
            driver.is_approved = True
            driver.errors = None
            
            db.commit()
            db.refresh(driver)
            
            return {
                "message": f"Driver {driver.name} approved successfully",
                "driver_id": driver_id,
                "status": "approved"
            }
            
        elif action == "reject":
            if not selected_error_codes:
                raise HTTPException(status_code=400, detail="Error codes required for rejection")
            
            # Get error details from ErrorHandling table
            errors = db.query(ErrorHandling).filter(ErrorHandling.error_code.in_(selected_error_codes)).all()
            if len(errors) != len(selected_error_codes):
                raise HTTPException(status_code=400, detail="Some error codes not found")
            
            # Reject driver and assign selected errors
            driver.is_approved = False
            driver.errors = {"error_codes": [], "details": {}}
            
            # Add selected errors
            for error in errors:
                driver.errors["error_codes"].append(error.error_code)
                driver.errors["details"][str(error.error_code)] = {
                    "error_type": error.error_type,
                    "error_description": error.error_description,
                    "assigned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "status": "pending"
                }
            
            flag_modified(driver, 'errors')
            db.commit()
            db.refresh(driver)
            
            return {
                "message": f"Driver {driver.name} registration rejected",
                "driver_id": driver_id,
                "status": "rejected",
                "errors_assigned": len(selected_error_codes),
                "assigned_error_codes": selected_error_codes,
                "driver_errors": driver.errors
            }
        
        else:
            raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in review_driver_documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/predefined-errors")
def get_predefined_errors(db: Session = Depends(get_db)):
    """Get all predefined errors for admin checkbox selection"""
    try:
        errors = db.query(ErrorHandling).all()
        return {
            "errors": [
                {
                    "error_code": error.error_code,
                    "error_type": error.error_type,
                    "error_description": error.error_description
                }
                for error in errors
            ]
        }
    except Exception as e:
        logger.error(f"Database error in get_predefined_errors: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/assign-errors-to-driver")
def assign_errors_to_driver(
    driver_id: str,
    error_codes: List[int],  # List of error codes selected by admin
    db: Session = Depends(get_db)
):
    """Admin assigns predefined errors to driver by selecting checkboxes"""
    try:
        # Get driver
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Get error details from ErrorHandling table
        errors = db.query(ErrorHandling).filter(ErrorHandling.error_code.in_(error_codes)).all()
        if len(errors) != len(error_codes):
            raise HTTPException(status_code=400, detail="Some error codes not found")
        
        # Initialize or update driver errors
        if not driver.errors:
            driver.errors = {"error_codes": [], "details": {}}
        
        # Add new errors
        for error in errors:
            if error.error_code not in driver.errors["error_codes"]:
                driver.errors["error_codes"].append(error.error_code)
                driver.errors["details"][str(error.error_code)] = {
                    "error_type": error.error_type,
                    "error_description": error.error_description,
                    "assigned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "status": "pending"
                }
        
        # Mark driver as not approved if errors assigned
        driver.is_approved = False
        flag_modified(driver, 'errors')
        
        db.commit()
        db.refresh(driver)
        
        return {
            "message": f"Assigned {len(error_codes)} errors to driver {driver.name}",
            "driver_id": driver_id,
            "assigned_errors": error_codes,
            "driver_errors": driver.errors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Database error in assign_errors_to_driver: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
        
        # Get full error details with document info
        error_list = []
        for error_code in driver.errors.get("error_codes", []):
            error_detail = driver.errors.get("details", {}).get(str(error_code), {})
            error_item = {
                "error_code": error_code,
                "error_type": error_detail.get("error_type"),
                "error_description": error_detail.get("error_description"),
                "assigned_at": error_detail.get("assigned_at"),
                "status": error_detail.get("status", "pending")
            }
            
            # Add document type if it's a document error
            if error_detail.get("document_type"):
                error_item["document_type"] = error_detail.get("document_type")
                error_item["document_label"] = DOCUMENT_TYPE_LABELS.get(
                    error_detail.get("document_type"), 
                    error_detail.get("document_type")
                )
            
            error_list.append(error_item)
        
        return {
            "driver_id": driver_id,
            "driver_name": driver.name,
            "has_errors": len(error_list) > 0,
            "error_count": len(error_list),
            "errors": error_list,
            "message": "Please fix the document issues and re-upload" if error_list else "No errors found"
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
        
        flag_modified(driver, 'errors')
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
        
        logger.info(f"Deleting error log: {error_id}")
        db.delete(error)
        db.commit()
        
        return {"message": "Error log deleted successfully", "error_id": error_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
