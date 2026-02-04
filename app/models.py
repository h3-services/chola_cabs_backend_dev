"""
SQLAlchemy models for Cab Booking System
Based on existing MySQL database schema
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, ForeignKey, DECIMAL, BigInteger, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Driver(Base):
    __tablename__ = "drivers"
    
    driver_id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(BigInteger, nullable=True)
    email = Column(String(100), nullable=True)
    kyc_verified = Column(String(20), default="pending")
    primary_location = Column(String(255), nullable=True)
    photo_url = Column(String(255), nullable=True)
    wallet_balance = Column(DECIMAL(10, 2), default=0.00)
    licence_number = Column(String(50), nullable=True)
    aadhar_number = Column(String(20), nullable=True)
    licence_url = Column(String(255), nullable=True)
    aadhar_url = Column(String(255), nullable=True)
    police_verification_url = Column(String(255), nullable=True)
    licence_expiry = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    device_id = Column(String(255), nullable=True)
    fcm_tokens = Column(JSON, nullable=True)
    is_available = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    errors = Column(JSON, nullable=True)
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="driver")
    trips = relationship("Trip", back_populates="assigned_driver")
    trip_requests = relationship("TripDriverRequest", back_populates="driver")
    payment_transactions = relationship("PaymentTransaction", back_populates="driver")
    wallet_transactions = relationship("WalletTransaction", back_populates="driver")

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    vehicle_id = Column(String(36), primary_key=True, index=True)
    driver_id = Column(String(36), ForeignKey("drivers.driver_id"), nullable=True)
    vehicle_type = Column(String(50), nullable=False)
    vehicle_brand = Column(String(100), nullable=False)
    vehicle_model = Column(String(100), nullable=False)
    rc_expiry_date = Column(Date, nullable=True)
    fc_expiry_date = Column(Date, nullable=True)
    vehicle_number = Column(String(20), nullable=False, unique=True)
    vehicle_color = Column(String(50), nullable=True)
    seating_capacity = Column(Integer, nullable=True)
    rc_book_url = Column(String(255), nullable=True)
    fc_certificate_url = Column(String(255), nullable=True)
    vehicle_front_url = Column(String(255), nullable=True)
    vehicle_back_url = Column(String(255), nullable=True)
    vehicle_left_url = Column(String(255), nullable=True)
    vehicle_right_url = Column(String(255), nullable=True)
    vehicle_inside_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    errors = Column(JSON, nullable=True)
    vehicle_approved = Column(Boolean, default=False)
    
    # Relationships
    driver = relationship("Driver", back_populates="vehicles")

class Trip(Base):
    __tablename__ = "trips"
    
    trip_id = Column(String(36), primary_key=True, index=True)
    customer_name = Column(String(100), nullable=True)
    customer_phone = Column(String(15), nullable=True)
    pickup_address = Column(Text, nullable=True)
    drop_address = Column(Text, nullable=True)
    trip_type = Column(String(50), nullable=True)  # ONE_WAY, ROUND_TRIP
    vehicle_type = Column(String(50), nullable=True)
    assigned_driver_id = Column(String(36), ForeignKey("drivers.driver_id"), nullable=True)
    trip_status = Column(String(50), default="OPEN")  # OPEN, ASSIGNED, STARTED, COMPLETED, CANCELLED
    distance_km = Column(DECIMAL(8, 2), nullable=True)
    odo_start = Column(Integer, nullable=True)
    odo_end = Column(Integer, nullable=True)
    fare = Column(DECIMAL(10, 2), nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    planned_start_at = Column(DateTime, nullable=True)
    planned_end_at = Column(DateTime, nullable=True)
    is_manual_assignment = Column(Boolean, default=False)
    passenger_count = Column(Integer, default=1)
    pet_count = Column(Integer, default=0)
    luggage_count = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
    
    # Relationships
    assigned_driver = relationship("Driver", back_populates="trips")
    trip_requests = relationship("TripDriverRequest", back_populates="trip")
    wallet_transactions = relationship("WalletTransaction", back_populates="trip")

class TripDriverRequest(Base):
    __tablename__ = "trip_driver_requests"
    
    request_id = Column(String(36), primary_key=True, index=True)
    trip_id = Column(String(36), ForeignKey("trips.trip_id"), nullable=True)
    driver_id = Column(String(36), ForeignKey("drivers.driver_id"), nullable=True)
    status = Column(String(50), default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    trip = relationship("Trip", back_populates="trip_requests")
    driver = relationship("Driver", back_populates="trip_requests")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    payment_id = Column(String(36), primary_key=True, index=True)
    driver_id = Column(String(36), ForeignKey("drivers.driver_id"), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    transaction_type = Column(String(50), nullable=True)  # CASH, ONLINE
    status = Column(String(50), nullable=True)  # SUCCESS, FAILED
    created_at = Column(DateTime, default=func.now())
    errors = Column(JSON, nullable=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    razorpay_order_id = Column(String(100), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    
    # Relationships
    driver = relationship("Driver", back_populates="payment_transactions")

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    
    wallet_id = Column(String(36), primary_key=True, index=True)
    driver_id = Column(String(36), ForeignKey("drivers.driver_id"), nullable=True)
    trip_id = Column(String(36), ForeignKey("trips.trip_id"), nullable=True)
    payment_id = Column(String(36), ForeignKey("payment_transactions.payment_id"), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=True)
    transaction_type = Column(String(50), nullable=True)  # CREDIT, DEBIT
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    driver = relationship("Driver", back_populates="wallet_transactions")
    trip = relationship("Trip", back_populates="wallet_transactions")

class VehicleTariffConfig(Base):
    __tablename__ = "vehicle_tariff_config"
    
    tariff_id = Column(String(36), primary_key=True, index=True)
    vehicle_type = Column(String(50), nullable=False)
    one_way_per_km = Column(DECIMAL(8, 2), nullable=False)
    round_trip_per_km = Column(DECIMAL(8, 2), nullable=False)
    driver_allowance = Column(DECIMAL(8, 2), nullable=False)
    one_way_min_km = Column(Integer, nullable=False)
    round_trip_min_km = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    driver_commission = Column(DECIMAL(5, 2), default=10.00, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ErrorHandling(Base):
    __tablename__ = "error_handling"
    
    error_id = Column(String(36), primary_key=True, index=True)  # Changed to String to match database
    error_type = Column(String(100), nullable=False)
    error_code = Column(Integer, nullable=False, unique=True)
    error_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

class Admin(Base):
    __tablename__ = "admins"
    
    admin_id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    phone_number = Column(BigInteger, nullable=False, unique=True)
    role = Column(String(20), nullable=False, default="ADMIN")  # SUPER_ADMIN, ADMIN
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime, nullable=True)
    created_by = Column(String(36), ForeignKey("admins.admin_id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Self-referential relationship
    creator = relationship("Admin", remote_side=[admin_id], backref="created_admins")

class DriverLiveLocation(Base):
    __tablename__ = "driver_live_location"
    
    driver_id = Column(String(36), ForeignKey("drivers.driver_id", ondelete="CASCADE"), primary_key=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship
    driver = relationship("Driver", backref="live_location")