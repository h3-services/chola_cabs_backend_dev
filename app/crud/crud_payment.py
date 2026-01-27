"""
CRUD operations for Payment, Wallet, Admin, and Tariff models
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models import PaymentTransaction, WalletTransaction, Admin, VehicleTariffConfig
from app.schemas import (
    PaymentTransactionCreate, PaymentTransactionUpdate,
    WalletTransactionCreate, WalletTransactionUpdate,
    AdminCreate, AdminUpdate,
    VehicleTariffConfigCreate, VehicleTariffConfigUpdate
)


# Payment CRUD
class CRUDPayment(CRUDBase[PaymentTransaction, PaymentTransactionCreate, PaymentTransactionUpdate]):
    """CRUD operations for Payment model"""
    
    def get_by_driver(self, db: Session, driver_id: str, skip: int = 0, limit: int = 100) -> List[PaymentTransaction]:
        """Get payments for a driver"""
        return db.query(PaymentTransaction).filter(
            PaymentTransaction.driver_id == driver_id
        ).offset(skip).limit(limit).all()


# Wallet CRUD
class CRUDWallet(CRUDBase[WalletTransaction, WalletTransactionCreate, WalletTransactionUpdate]):
    """CRUD operations for Wallet model"""
    
    def get_by_driver(self, db: Session, driver_id: str, skip: int = 0, limit: int = 100) -> List[WalletTransaction]:
        """Get wallet transactions for a driver"""
        return db.query(WalletTransaction).filter(
            WalletTransaction.driver_id == driver_id
        ).order_by(WalletTransaction.created_at.desc()).offset(skip).limit(limit).all()


# Admin CRUD
class CRUDAdmin(CRUDBase[Admin, AdminCreate, AdminUpdate]):
    """CRUD operations for Admin model"""
    
    def get_by_phone(self, db: Session, phone_number: int) -> Optional[Admin]:
        """Get admin by phone number"""
        return db.query(Admin).filter(Admin.phone_number == phone_number).first()
    
    def get_active(self, db: Session, skip: int = 0, limit: int = 100) -> List[Admin]:
        """Get active admins"""
        return db.query(Admin).filter(Admin.is_active == True).offset(skip).limit(limit).all()


# Tariff CRUD
class CRUDTariff(CRUDBase[VehicleTariffConfig, VehicleTariffConfigCreate, VehicleTariffConfigUpdate]):
    """CRUD operations for Tariff model"""
    
    def get_by_vehicle_type(self, db: Session, vehicle_type: str) -> Optional[VehicleTariffConfig]:
        """Get active tariff for vehicle type"""
        return db.query(VehicleTariffConfig).filter(
            VehicleTariffConfig.vehicle_type == vehicle_type,
            VehicleTariffConfig.is_active == True
        ).first()
    
    def get_active(self, db: Session) -> List[VehicleTariffConfig]:
        """Get all active tariffs"""
        return db.query(VehicleTariffConfig).filter(
            VehicleTariffConfig.is_active == True
        ).all()


# Singleton instances
crud_payment = CRUDPayment(PaymentTransaction)
crud_wallet = CRUDWallet(WalletTransaction)
crud_admin = CRUDAdmin(Admin)
crud_tariff = CRUDTariff(VehicleTariffConfig)
