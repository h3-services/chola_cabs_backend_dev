"""
Wallet Transaction API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import WalletTransaction, Driver
from app.schemas import (
    WalletTransactionCreate, WalletTransactionUpdate, 
    WalletTransactionResponse, WalletTransactionType
)
from app.crud.crud_payment import crud_wallet
from app.crud.crud_driver import crud_driver

router = APIRouter(prefix="/wallet-transactions", tags=["wallet-transactions"])

@router.get("/", response_model=List[WalletTransactionResponse])
def get_all_wallet_transactions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all wallet transactions"""
    transactions = crud_wallet.get_multi(db, skip=skip, limit=limit)
    return transactions

@router.get("/{transaction_id}", response_model=WalletTransactionResponse)
def get_wallet_transaction_details(transaction_id: str, db: Session = Depends(get_db)):
    """Get wallet transaction details by ID"""
    transaction = crud_wallet.get(db, id=transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found"
        )
    return transaction

@router.post("/", response_model=WalletTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_wallet_transaction(transaction: WalletTransactionCreate, db: Session = Depends(get_db)):
    """Create a new wallet transaction"""
    # Check if driver exists
    driver = crud_driver.get(db, id=transaction.driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Generate UUID for wallet_id
    import uuid
    transaction_data = transaction.dict()
    transaction_data['wallet_id'] = str(uuid.uuid4())
    
    db_transaction = WalletTransaction(**transaction_data)
    
    # Update driver wallet balance
    if transaction.transaction_type in [WalletTransactionType.CREDIT, WalletTransactionType.ADMIN_CREDIT]:
        driver.wallet_balance += transaction.amount
    elif transaction.transaction_type in [WalletTransactionType.DEBIT, WalletTransactionType.ADMIN_DEBIT]:
        if driver.wallet_balance < transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient wallet balance"
            )
        driver.wallet_balance -= transaction.amount
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.put("/{transaction_id}", response_model=WalletTransactionResponse)
def update_wallet_transaction(
    transaction_id: str, 
    transaction_update: WalletTransactionUpdate, 
    db: Session = Depends(get_db)
):
    """Update wallet transaction information"""
    transaction = crud_wallet.get(db, id=transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found"
        )
    
    updated_transaction = crud_wallet.update(db, db_obj=transaction, obj_in=transaction_update)
    return updated_transaction

@router.delete("/{transaction_id}")
def delete_wallet_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Delete a wallet transaction"""
    transaction = crud_wallet.get(db, id=transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found"
        )
    
    crud_wallet.delete(db, id=transaction_id)
    db.commit()
    
    return {
        "message": "Wallet transaction deleted successfully",
        "transaction_id": transaction_id
    }

@router.get("/driver/{driver_id}", response_model=List[WalletTransactionResponse])
def get_wallet_transactions_by_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get all wallet transactions for a specific driver"""
    driver = crud_driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    transactions = crud_wallet.get_by_driver(db, driver_id=driver_id)
    return transactions