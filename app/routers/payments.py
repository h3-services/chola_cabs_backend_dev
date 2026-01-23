"""
Payment API endpoints with Razorpay integration
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PaymentTransaction
from app.schemas import PaymentTransactionCreate, PaymentTransactionUpdate, PaymentTransactionResponse
import uuid

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

@router.get("/", response_model=List[PaymentTransactionResponse])
def get_all_payments(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all payment transactions"""
    try:
        payments = db.query(PaymentTransaction).offset(skip).limit(limit).all()
        return payments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/{payment_id}", response_model=PaymentTransactionResponse)
def get_payment_details(payment_id: str, db: Session = Depends(get_db)):
    """Get payment details by ID"""
    try:
        payment = db.query(PaymentTransaction).filter(PaymentTransaction.payment_id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return payment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.post("/", response_model=PaymentTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentTransactionCreate, db: Session = Depends(get_db)):
    """Create a new payment transaction"""
    try:
        # Check if driver exists
        from app.models import Driver
        driver = db.query(Driver).filter(Driver.driver_id == payment.driver_id).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Create payment transaction
        db_payment = PaymentTransaction(
            payment_id=str(uuid.uuid4()),
            driver_id=payment.driver_id,
            amount=payment.amount,
            transaction_type=payment.transaction_type.value,
            status=payment.status.value,
            transaction_id=payment.transaction_id,
            razorpay_payment_id=payment.razorpay_payment_id,
            razorpay_order_id=payment.razorpay_order_id,
            razorpay_signature=payment.razorpay_signature
        )
        
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.put("/{payment_id}", response_model=PaymentTransactionResponse)
def update_payment(
    payment_id: str, 
    payment_update: PaymentTransactionUpdate, 
    db: Session = Depends(get_db)
):
    """Update payment information"""
    try:
        payment = db.query(PaymentTransaction).filter(PaymentTransaction.payment_id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Update fields
        update_data = payment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ["transaction_type", "status"] and hasattr(value, "value"):
                setattr(payment, field, value.value)
            else:
                setattr(payment, field, value)
        
        db.commit()
        db.refresh(payment)
        return payment
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete("/{payment_id}")
def delete_payment(payment_id: str, db: Session = Depends(get_db)):
    """Delete a payment transaction"""
    try:
        payment = db.query(PaymentTransaction).filter(PaymentTransaction.payment_id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        db.delete(payment)
        db.commit()
        
        return {
            "message": "Payment deleted successfully",
            "payment_id": payment_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/driver/{driver_id}", response_model=List[PaymentTransactionResponse])
def get_payments_by_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get all payments for a specific driver"""
    try:
        from app.models import Driver
        driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        payments = db.query(PaymentTransaction).filter(PaymentTransaction.driver_id == driver_id).all()
        return payments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/razorpay/{razorpay_payment_id}", response_model=PaymentTransactionResponse)
def get_payment_by_razorpay_id(razorpay_payment_id: str, db: Session = Depends(get_db)):
    """Get payment by Razorpay payment ID"""
    try:
        payment = db.query(PaymentTransaction).filter(
            PaymentTransaction.razorpay_payment_id == razorpay_payment_id
        ).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return payment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )