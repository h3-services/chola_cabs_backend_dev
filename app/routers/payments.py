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
def get_payment_details(payment_id: int, db: Session = Depends(get_db)):
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
    # Check if trip exists
    trip = db.query(Trip).filter(Trip.trip_id == payment.trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    db_payment = PaymentTransaction(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.put("/{payment_id}", response_model=PaymentTransactionResponse)
def update_payment(
    payment_id: int, 
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
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
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

@router.get("/trip/{trip_id}", response_model=List[PaymentTransactionResponse])
def get_payments_by_trip(trip_id: int, db: Session = Depends(get_db)):
    """Get all payments for a specific trip"""
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    payments = db.query(PaymentTransaction).filter(PaymentTransaction.trip_id == trip_id).all()
    return payments