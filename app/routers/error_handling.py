"""
Error Handling API endpoints
"""
from typing import List, Optional
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

@router.post("/review-driver-registration")
def review_driver_registration(
    driver_id: str,
    action: str,  # "approve" or "reject"
    document_errors: List[dict] = None,  # [{"document_type": "licence", "error_message": "Blurry image"}]
    db: Session = Depends(get_db)
):
    """Admin reviews driver registration and assigns document errors if rejecting"""
    try:
        # Get driver
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        if action == "approve":
            # Approve driver and clear any existing errors
            driver.is_approved = True
            driver.errors = None  # Clear all errors
            
            db.commit()
            db.refresh(driver)
            
            return {
                "message": f"Driver {driver.name} approved successfully",
                "driver_id": driver_id,
                "status": "approved"
            }
            
        elif action == "reject":
            # Reject driver and assign document errors
            driver.is_approved = False
            
            # Initialize errors JSON
            driver.errors = {"error_codes": [], "details": {}}
            
            # Add document errors if provided
            if document_errors:
                import time
                for doc_error in document_errors:
                    error_code = int(f"9{int(time.time() * 1000) % 100000}")  # Unique code
                    
                    driver.errors["error_codes"].append(error_code)
                    driver.errors["details"][str(error_code)] = {
                        "error_type": "DOCUMENT",
                        "document_type": doc_error.get("document_type"),
                        "error_description": doc_error.get("error_message"),
                        "assigned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "status": "pending"
                    }
                    time.sleep(0.001)  # Ensure unique timestamps
            
            db.commit()
            db.refresh(driver)
            
            return {
                "message": f"Driver {driver.name} registration rejected",
                "driver_id": driver_id,
                "status": "rejected",
                "errors_assigned": len(document_errors) if document_errors else 0,
                "driver_errors": driver.errors
            }
        
        else:
            raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/document-types")
def get_document_error_types():
    """Get available document types for admin UI"""
    return {
        "document_types": [
            {"value": "licence", "label": "Driving Licence"},
            {"value": "aadhar", "label": "Aadhar Card"},
            {"value": "photo", "label": "Profile Photo"},
            {"value": "rc", "label": "RC Book"},
            {"value": "fc", "label": "FC Certificate"},
            {"value": "vehicle_photo", "label": "Vehicle Photos"}
        ],
        "common_errors": [
            "Document is blurry or unclear",
            "Document has expired",
            "Document information doesn't match profile",
            "Document is damaged or torn",
            "Wrong document uploaded",
            "Document is not readable"
        ]
    }

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
                error_item["document_label"] = {
                    "licence": "Driving Licence",
                    "aadhar": "Aadhar Card", 
                    "photo": "Profile Photo",
                    "rc": "RC Book",
                    "fc": "FC Certificate",
                    "vehicle_photo": "Vehicle Photos"
                }.get(error_detail.get("document_type"), error_detail.get("document_type"))
            
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
