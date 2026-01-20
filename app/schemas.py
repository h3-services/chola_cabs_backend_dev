"""
Pydantic schemas for request/response validation
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum

# Enums
class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class TripStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TripDriverRequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

# Driver Schemas
class DriverBase(BaseModel):
    name: str
    phone_number: str
    email: Optional[str] = None
    primary_location: Optional[str] = None
    licence_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    licence_expiry: Optional[date] = None

class DriverCreate(DriverBase):
    device_id: Optional[str] = None

class DriverUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    primary_location: Optional[str] = None
    licence_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    licence_expiry: Optional[date] = None

class DriverResponse(DriverBase):
    driver_id: str
    kyc_verified: KYCStatus
    photo_url: Optional[str] = None
    aadhar_url: Optional[str] = None
    licence_url: Optional[str] = None
    wallet_balance: Decimal
    device_id: Optional[str] = None
    is_available: bool
    is_approved: bool
    errors: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Vehicle Schemas
class VehicleBase(BaseModel):
    vehicle_type: str
    vehicle_brand: str
    vehicle_model: str
    vehicle_number: str
    vehicle_color: Optional[str] = None
    seating_capacity: Optional[int] = None

class VehicleCreate(VehicleBase):
    driver_id: str
    rc_expiry_date: Optional[date] = None
    fc_expiry_date: Optional[date] = None

class VehicleUpdate(BaseModel):
    vehicle_type: Optional[str] = None
    vehicle_brand: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    seating_capacity: Optional[int] = None
    rc_expiry_date: Optional[date] = None
    fc_expiry_date: Optional[date] = None

class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    vehicle_id: str
    driver_id: Optional[str] = None
    vehicle_type: str
    vehicle_brand: str
    vehicle_model: str
    vehicle_number: str
    vehicle_color: Optional[str] = None
    seating_capacity: Optional[int] = None
    rc_expiry_date: Optional[date] = None
    fc_expiry_date: Optional[date] = None
    rc_book_url: Optional[str] = None
    fc_certificate_url: Optional[str] = None
    vehicle_front_url: Optional[str] = None
    vehicle_back_url: Optional[str] = None
    vehicle_left_url: Optional[str] = None
    vehicle_right_url: Optional[str] = None
    vehicle_approved: bool
    errors: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

# Trip Schemas
class TripBase(BaseModel):
    customer_name: str
    customer_phone: str
    pickup_address: str
    drop_address: str
    trip_type: str  # one_way, round_trip
    vehicle_type: str
    passenger_count: Optional[int] = 1
    planned_start_at: Optional[datetime] = None
    planned_end_at: Optional[datetime] = None

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    trip_status: Optional[str] = None
    assigned_driver_id: Optional[int] = None
    distance_km: Optional[Decimal] = None
    fare: Optional[Decimal] = None
    odo_start: Optional[int] = None
    odo_end: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

class TripStatusUpdate(BaseModel):
    status: str

class TripResponse(TripBase):
    trip_id: str
    assigned_driver_id: Optional[str] = None
    trip_status: TripStatus
    distance_km: Optional[Decimal] = None
    odo_start: Optional[int] = None
    odo_end: Optional[int] = None
    fare: Optional[Decimal] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    is_manual_assignment: bool
    errors: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Trip Driver Request Schemas
class TripDriverRequestCreate(BaseModel):
    trip_id: int
    driver_id: int

class TripDriverRequestUpdate(BaseModel):
    status: str  # accepted, rejected

class TripDriverRequestResponse(BaseModel):
    request_id: int
    trip_id: int
    driver_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Payment Schemas
class PaymentTransactionBase(BaseModel):
    driver_id: str
    amount: Decimal
    transaction_type: str  # credit, debit
    status: str = "pending"  # pending, completed, failed
    transaction_id: Optional[str] = None

class PaymentTransactionCreate(PaymentTransactionBase):
    pass

class PaymentTransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    transaction_id: Optional[str] = None

class PaymentTransactionResponse(BaseModel):
    payment_id: str
    driver_id: Optional[str] = None
    amount: Optional[Decimal] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Wallet Schemas
class WalletTransactionBase(BaseModel):
    driver_id: str
    transaction_type: str  # credit or debit
    amount: Decimal

class WalletTransactionCreate(WalletTransactionBase):
    pass

class WalletTransactionUpdate(BaseModel):
    transaction_type: Optional[str] = None
    amount: Optional[Decimal] = None

class WalletTransactionResponse(BaseModel):
    wallet_id: str
    driver_id: Optional[str] = None
    transaction_type: Optional[str] = None
    amount: Optional[Decimal] = None
    trip_id: Optional[str] = None
    payment_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Tariff Schemas
class VehicleTariffConfigBase(BaseModel):
    vehicle_type: str
    one_way_per_km: Decimal
    one_way_min_km: int
    round_trip_per_km: Decimal
    round_trip_min_km: int
    driver_allowance: Decimal
    is_active: bool = True

class VehicleTariffConfigCreate(VehicleTariffConfigBase):
    pass

class VehicleTariffConfigUpdate(BaseModel):
    vehicle_type: Optional[str] = None
    one_way_per_km: Optional[Decimal] = None
    one_way_min_km: Optional[int] = None
    round_trip_per_km: Optional[Decimal] = None
    round_trip_min_km: Optional[int] = None
    driver_allowance: Optional[Decimal] = None
    is_active: Optional[bool] = None

class VehicleTariffConfigResponse(VehicleTariffConfigBase):
    tariff_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Error Handling Schemas
class ErrorHandlingCreate(BaseModel):
    error_type: str
    error_code: int  # Changed to int for unique numeric codes
    error_description: str

class ErrorHandlingResponse(BaseModel):
    error_id: str  # Changed to str to match UUID in database
    error_type: str
    error_code: int  # Changed to int
    error_description: str
    created_at: datetime

    class Config:
        from_attributes = True

# Admin Schemas
class AdminRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"

class AdminBase(BaseModel):
    name: Optional[str] = None
    phone_number: int
    role: AdminRole = AdminRole.ADMIN

class AdminCreate(AdminBase):
    """Schema for creating a new admin (SUPER_ADMIN only)"""
    pass

class AdminUpdate(BaseModel):
    """Schema for updating admin details"""
    name: Optional[str] = None
    phone_number: Optional[int] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None

class AdminResponse(BaseModel):
    """Schema for admin response"""
    admin_id: str
    name: Optional[str] = None
    phone_number: int
    role: str
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AdminLoginRequest(BaseModel):
    """Schema for admin login - send OTP"""
    phone_number: int

class AdminVerifyOTPRequest(BaseModel):
    """Schema for OTP verification"""
    phone_number: int
    otp: str

class AdminLoginResponse(BaseModel):
    """Schema for successful login response"""
    access_token: str
    token_type: str = "bearer"
    admin: AdminResponse