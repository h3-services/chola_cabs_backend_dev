"""
Payment API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PaymentTransaction, Trip
from app.schemas import PaymentTransactionCreate, PaymentTransactionUpdate, PaymentTransactionResponse

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/", response_model=List[PaymentTransactionResponse])
def get_all_payments(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all payment transactions"""
    payments = db.query(PaymentTransaction).offset(skip).limit(limit).all()
    return payments

@router.get("/{payment_id}", response_model=PaymentTransactionResponse)
def get_payment_details(payment_id: str, db: Session = Depends(get_db)):
    """Get payment details by ID"""
    payment = db.query(PaymentTransaction).filter(PaymentTransaction.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment

@router.post("/", response_model=PaymentTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentTransactionCreate, db: Session = Depends(get_db)):
    """Create a new payment transaction"""
    # Check if driver exists
    from app.models import Driver
    driver = db.query(Driver).filter(Driver.driver_id == payment.driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Generate UUID for payment_id
    import uuid
    payment_data = payment.dict()
    payment_data['payment_id'] = str(uuid.uuid4())
    
    db_payment = PaymentTransaction(**payment_data)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.put("/{payment_id}", response_model=PaymentTransactionResponse)
def update_payment(
    payment_id: str, 
    payment_update: PaymentTransactionUpdate, 
    db: Session = Depends(get_db)
):
    """Update payment information"""
    payment = db.query(PaymentTransaction).filter(PaymentTransaction.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    update_data = payment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)
    
    db.commit()
    db.refresh(payment)
    return payment

@router.delete("/{payment_id}")
def delete_payment(payment_id: str, db: Session = Depends(get_db)):
    """Delete a payment transaction"""
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

@router.get("/driver/{driver_id}", response_model=List[PaymentTransactionResponse])
def get_payments_by_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get all payments for a specific driver"""
    from app.models import Driver
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    payments = db.query(PaymentTransaction).filter(PaymentTransaction.driver_id == driver_id).all()
    return payments