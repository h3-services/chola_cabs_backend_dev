"""
Application Constants and Enumerations
"""
from enum import Enum


# KYC Status
class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# Trip Status
class TripStatus(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# Trip Driver Request Status
class TripDriverRequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


# Admin Roles
class AdminRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"


# Vehicle Types
class VehicleType(str, Enum):
    SEDAN = "Sedan"
    SUV = "SUV"
    MINI = "Mini"
    HATCHBACK = "Hatchback"
    TEMPO_TRAVELLER = "Tempo Traveller"


# Trip Types
class TripType(str, Enum):
    ONE_WAY = "One Way"
    ROUND_TRIP = "Round Trip"
    LOCAL = "Local"


# Payment Status
class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


# Payment Method
class PaymentMethod(str, Enum):
    CASH = "CASH"
    ONLINE = "ONLINE"
    UPI = "UPI"
    CARD = "CARD"
    WALLET = "WALLET"


# Wallet Transaction Type
class WalletTransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    REFUND = "REFUND"
    COMMISSION = "COMMISSION"


# File Upload Types
class DocumentType(str, Enum):
    DRIVER_PHOTO = "driver_photo"
    AADHAR = "aadhar"
    LICENCE = "licence"
    RC_BOOK = "rc_book"
    FC_CERTIFICATE = "fc_certificate"
    VEHICLE_PHOTO = "vehicle_photo"


# Vehicle Photo Positions
class VehiclePhotoPosition(str, Enum):
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"


# File Extensions
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS


# Upload Folders
class UploadFolder:
    DRIVER_PHOTOS = "drivers/photos"
    DRIVER_AADHAR = "drivers/aadhar"
    DRIVER_LICENCE = "drivers/licence"
    VEHICLE_RC = "vehicles/rc"
    VEHICLE_FC = "vehicles/fc"
    VEHICLE_FRONT = "vehicles/front"
    VEHICLE_BACK = "vehicles/back"
    VEHICLE_LEFT = "vehicles/left"
    VEHICLE_RIGHT = "vehicles/right"


# Error Codes
class ErrorCode:
    # Driver Errors (1000-1999)
    DRIVER_NOT_FOUND = 1001
    DRIVER_ALREADY_EXISTS = 1002
    DRIVER_NOT_APPROVED = 1003
    DRIVER_NOT_AVAILABLE = 1004
    INVALID_KYC_STATUS = 1005
    
    # Vehicle Errors (2000-2999)
    VEHICLE_NOT_FOUND = 2001
    VEHICLE_ALREADY_EXISTS = 2002
    VEHICLE_NOT_APPROVED = 2003
    INVALID_VEHICLE_TYPE = 2004
    
    # Trip Errors (3000-3999)
    TRIP_NOT_FOUND = 3001
    TRIP_ALREADY_ASSIGNED = 3002
    TRIP_ALREADY_STARTED = 3003
    TRIP_ALREADY_COMPLETED = 3004
    INVALID_TRIP_STATUS = 3005
    INVALID_ODOMETER_READING = 3006
    
    # Payment Errors (4000-4999)
    PAYMENT_NOT_FOUND = 4001
    PAYMENT_FAILED = 4002
    INSUFFICIENT_WALLET_BALANCE = 4003
    
    # Admin Errors (5000-5999)
    ADMIN_NOT_FOUND = 5001
    ADMIN_ALREADY_EXISTS = 5002
    UNAUTHORIZED = 5003
    FORBIDDEN = 5004
    
    # Upload Errors (6000-6999)
    INVALID_FILE_TYPE = 6001
    FILE_TOO_LARGE = 6002
    UPLOAD_FAILED = 6003
    
    # General Errors (9000-9999)
    DATABASE_ERROR = 9001
    VALIDATION_ERROR = 9002
    INTERNAL_SERVER_ERROR = 9003


# HTTP Status Messages
class StatusMessage:
    SUCCESS = "Operation completed successfully"
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    NOT_FOUND = "Resource not found"
    BAD_REQUEST = "Invalid request"
    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "Access denied"
    INTERNAL_ERROR = "Internal server error"


# Pagination
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000

# Fare Calculation
DEFAULT_BASE_FARE = 100.0
DEFAULT_PER_KM_RATE = 15.0
DEFAULT_DRIVER_COMMISSION_PERCENT = 10.0

# FCM
MAX_FCM_TOKENS_PER_DRIVER = 5
