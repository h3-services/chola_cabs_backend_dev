"""
Script to populate ErrorHandling table with predefined errors
"""
from app.database import SessionLocal
from app.models import ErrorHandling

def populate_static_errors():
    db = SessionLocal()
    
    static_errors = [
        # Document errors (1000-1999)
        {"error_code": 1001, "error_type": "DOCUMENT", "error_description": "Driving licence is blurry or unclear", "admin_description": "The uploaded driving license image is not clear enough for verification. Please upload a high-quality, well-lit photo."},
        {"error_code": 1002, "error_type": "DOCUMENT", "error_description": "Driving licence has expired", "admin_description": "The driving license has passed its expiry date. Please renew your license and upload the updated document."},
        {"error_code": 1003, "error_type": "DOCUMENT", "error_description": "Driving licence information doesn't match profile", "admin_description": "The name or details on the driving license do not match the profile information. Please ensure all details are consistent."},
        {"error_code": 1004, "error_type": "DOCUMENT", "error_description": "Aadhar card is blurry or unclear", "admin_description": "The Aadhar card image is not readable. Please upload a clear, high-resolution photo of your Aadhar card."},
        {"error_code": 1005, "error_type": "DOCUMENT", "error_description": "Aadhar card information doesn't match profile", "admin_description": "The personal details on Aadhar card do not match your profile. Please verify and update your information."},
        {"error_code": 1006, "error_type": "DOCUMENT", "error_description": "Profile photo is not clear", "admin_description": "Your profile photo is not clear or does not meet our quality standards. Please upload a recent, clear headshot."},
        {"error_code": 1007, "error_type": "DOCUMENT", "error_description": "RC book is blurry or unclear", "admin_description": "The vehicle RC book image is not legible. Please upload a clear photo showing all vehicle details."},
        {"error_code": 1008, "error_type": "DOCUMENT", "error_description": "RC book has expired", "admin_description": "Your vehicle registration certificate has expired. Please renew your RC and upload the updated document."},
        {"error_code": 1009, "error_type": "DOCUMENT", "error_description": "FC certificate is blurry or unclear", "admin_description": "The fitness certificate image is not clear. Please upload a high-quality photo of your valid FC certificate."},
        {"error_code": 1010, "error_type": "DOCUMENT", "error_description": "FC certificate has expired", "admin_description": "Your vehicle fitness certificate has expired. Please get a new FC done and upload the updated certificate."},
        {"error_code": 1011, "error_type": "DOCUMENT", "error_description": "Vehicle photos are not clear", "admin_description": "The vehicle photos do not clearly show the vehicle condition. Please upload clear photos from all required angles."},
        {"error_code": 1012, "error_type": "DOCUMENT", "error_description": "Wrong document uploaded", "admin_description": "You have uploaded an incorrect document. Please check the requirements and upload the correct document type."},
        
        # Profile errors (2000-2999)
        {"error_code": 2001, "error_type": "PROFILE", "error_description": "Phone number verification required", "admin_description": "Your phone number needs to be verified. Please complete the OTP verification process."},
        {"error_code": 2002, "error_type": "PROFILE", "error_description": "Email verification required", "admin_description": "Please verify your email address by clicking the verification link sent to your email."},
        {"error_code": 2003, "error_type": "PROFILE", "error_description": "Complete profile information required", "admin_description": "Your profile is incomplete. Please fill in all mandatory fields including personal and contact information."},
        
        # Vehicle errors (3000-3999)
        {"error_code": 3001, "error_type": "VEHICLE", "error_description": "Vehicle registration number mismatch", "admin_description": "The vehicle number in RC book does not match the number plate in photos. Please ensure consistency."},
        {"error_code": 3002, "error_type": "VEHICLE", "error_description": "Vehicle type not supported", "admin_description": "This vehicle type is not currently supported on our platform. Please check our supported vehicle categories."},
        {"error_code": 3003, "error_type": "VEHICLE", "error_description": "Vehicle condition not acceptable", "admin_description": "The vehicle condition does not meet our quality standards. Please ensure your vehicle is well-maintained and clean."},
    ]
    
    try:
        # Clear existing errors first
        db.query(ErrorHandling).delete()
        
        # Add static errors
        for error_data in static_errors:
            import uuid
            error_data["error_id"] = str(uuid.uuid4())
            error = ErrorHandling(**error_data)
            db.add(error)
        
        db.commit()
        print("Static error codes populated successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_static_errors()