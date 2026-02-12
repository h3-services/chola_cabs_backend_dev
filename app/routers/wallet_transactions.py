"""
Wallet Transaction API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import WalletTransaction, Driver
from app.schemas import WalletTransactionCreate, WalletTransactionUpdate, WalletTransactionResponse

router = APIRouter(prefix="/wallet-transactions", tags=["wallet-transactions"])

@router.get("/", response_model=List[WalletTransactionResponse])
def get_all_wallet_transactions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all wallet transactions"""
    transactions = db.query(WalletTransaction).offset(skip).limit(limit).all()
    return transactions

@router.get("/{transaction_id}", response_model=WalletTransactionResponse)
def get_wallet_transaction_details(transaction_id: str, db: Session = Depends(get_db)):
    """Get wallet transaction details by ID"""
    transaction = db.query(WalletTransaction).filter(WalletTransaction.wallet_id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found"
        )
    return transaction

 

@router.put("/{transaction_id}", response_model=WalletTransactionResponse)
def update_wallet_transaction(
    transaction_id: str, 
    transaction_update: WalletTransactionUpdate, 
    db: Session = Depends(get_db)
):
    """Update wallet transaction information"""
    transaction = db.query(WalletTransaction).filter(WalletTransaction.wallet_id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found"
        )
    
    update_data = transaction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}")
def delete_wallet_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Delete a wallet transaction"""
    transaction = db.query(WalletTransaction).filter(WalletTransaction.wallet_id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found"
        )
    
    db.delete(transaction)
    db.commit()
    
    return {
        "message": "Wallet transaction deleted successfully",
        "transaction_id": transaction_id
    }

@router.get("/driver/{driver_id}", response_model=List[WalletTransactionResponse])
def get_wallet_transactions_by_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get all wallet transactions for a specific driver"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    transactions = db.query(WalletTransaction).filter(WalletTransaction.driver_id == driver_id).all()
    return transactions