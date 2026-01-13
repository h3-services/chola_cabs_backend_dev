"""
SQLAlchemy models for Cab Booking System
Based on existing MySQL database schema
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Driver(Base):
    __tablename__ = "drivers"
    
    driver_id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    kyc_verified = Column(Boolean, default=False)
    primary_location = Column(String(500), nullable=True)
    photo_url = Column(Text, nullable=True)
    wallet_balance = Column(DECIMAL(10, 2), default=0.00)
    licence_number = Column(String(50), nullable=True)
    aadhar_number = Column(String(20), nullable=True)
    licence_url = Column(Text, nullable=True)
    aadhar_url = Column(Text, nullable=True)
    licence_expiry = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    device_id = Column(String(255), nullable=True)
    is_available = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    errors = Column(Text, nullable=True)
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="driver")
    trips = relationship("Trip", back_populates="assigned_driver")
    trip_requests = relationship("TripDriverRequest", back_populates="driver")
    payment_transactions = relationship("PaymentTransaction", back_populates="driver")
    wallet_transactions = relationship("WalletTransaction", back_populates="driver")

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    vehicle_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    driver_id = Column(String(255), ForeignKey("drivers.driver_id"), nullable=False)
    vehicle_type = Column(String(50), nullable=False)
    vehicle_brand = Column(String(100), nullable=False)
    vehicle_model = Column(String(100), nullable=False)
    rc_expiry_date = Column(Date, nullable=True)
    fc_expiry_date = Column(Date, nullable=True)
    vehicle_number = Column(String(20), nullable=False, unique=True)
    vehicle_color = Column(String(50), nullable=True)
    seating_capacity = Column(Integer, nullable=True)
    rc_book_url = Column(Text, nullable=True)
    fc_certificate_url = Column(Text, nullable=True)
    vehicle_front_url = Column(Text, nullable=True)
    vehicle_back_url = Column(Text, nullable=True)
    vehicle_left_url = Column(Text, nullable=True)
    vehicle_right_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    errors = Column(Text, nullable=True)
    vehicle_approved = Column(Boolean, default=False)
    
    # Relationships
    driver = relationship("Driver", back_populates="vehicles")

class Trip(Base):
    __tablename__ = "trips"
    
    trip_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    pickup_address = Column(Text, nullable=False)
    drop_address = Column(Text, nullable=False)
    trip_type = Column(String(50), nullable=False)  # one_way, round_trip
    vehicle_type = Column(String(50), nullable=False)
    assigned_driver_id = Column(String(255), ForeignKey("drivers.driver_id"), nullable=True)
    trip_status = Column(String(50), default="pending")  # pending, assigned, started, completed, cancelled
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
    errors = Column(Text, nullable=True)
    
    # Relationships
    assigned_driver = relationship("Driver", back_populates="trips")
    trip_requests = relationship("TripDriverRequest", back_populates="trip")
    wallet_transactions = relationship("WalletTransaction", back_populates="trip")

class TripDriverRequest(Base):
    __tablename__ = "trip_driver_requests"
    
    request_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trip_id = Column(Integer, ForeignKey("trips.trip_id"), nullable=False)
    driver_id = Column(String(255), ForeignKey("drivers.driver_id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    trip = relationship("Trip", back_populates="trip_requests")
    driver = relationship("Driver", back_populates="trip_requests")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    payment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    driver_id = Column(String(255), ForeignKey("drivers.driver_id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    transaction_id = Column(String(255), nullable=True)
    transaction_type = Column(String(50), nullable=False)  # credit, debit
    status = Column(String(50), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=func.now())
    errors = Column(Text, nullable=True)
    
    # Relationships
    driver = relationship("Driver", back_populates="payment_transactions")

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    
    wallet_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    driver_id = Column(String(255), ForeignKey("drivers.driver_id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.trip_id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payment_transactions.payment_id"), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # credit, debit
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    driver = relationship("Driver", back_populates="wallet_transactions")
    trip = relationship("Trip", back_populates="wallet_transactions")

class VehicleTariffConfig(Base):
    __tablename__ = "vehicle_tariff_config"
    
    tariff_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_type = Column(String(50), nullable=False)
    one_way_per_km = Column(DECIMAL(8, 2), nullable=False)
    round_trip_per_km = Column(DECIMAL(8, 2), nullable=False)
    driver_allowance = Column(DECIMAL(8, 2), nullable=False)
    one_way_min_km = Column(Integer, nullable=False)
    round_trip_min_km = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ErrorHandling(Base):
    __tablename__ = "error_handling"
    
    error_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    error_type = Column(String(100), nullable=False)
    error_code = Column(String(50), nullable=False)
    error_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())