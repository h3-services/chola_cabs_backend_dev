"""
Simplified Error Handling API endpoints for testing
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ErrorHandling
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