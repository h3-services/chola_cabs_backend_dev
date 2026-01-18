"""
Script to populate ErrorHandling table with predefined errors
"""
from app.database import SessionLocal
from app.models import ErrorHandling

def populate_predefined_errors():
    db = SessionLocal()
    
    predefined_errors = [
        # Document errors
        {"error_code": 1001, "error_type": "DOCUMENT", "error_description": "Driving licence is blurry or unclear"},
        {"error_code": 1002, "error_type": "DOCUMENT", "error_description": "Driving licence has expired"},
        {"error_code": 1003, "error_type": "DOCUMENT", "error_description": "Driving licence information doesn't match profile"},
        {"error_code": 1004, "error_type": "DOCUMENT", "error_description": "Aadhar card is blurry or unclear"},
        {"error_code": 1005, "error_type": "DOCUMENT", "error_description": "Aadhar card information doesn't match profile"},
        {"error_code": 1006, "error_type": "DOCUMENT", "error_description": "Profile photo is not clear"},
        {"error_code": 1007, "error_type": "DOCUMENT", "error_description": "RC book is blurry or unclear"},
        {"error_code": 1008, "error_type": "DOCUMENT", "error_description": "RC book has expired"},
        {"error_code": 1009, "error_type": "DOCUMENT", "error_description": "FC certificate is blurry or unclear"},
        {"error_code": 1010, "error_type": "DOCUMENT", "error_description": "FC certificate has expired"},
        {"error_code": 1011, "error_type": "DOCUMENT", "error_description": "Vehicle photos are not clear"},
        {"error_code": 1012, "error_type": "DOCUMENT", "error_description": "Wrong document uploaded"},
        
        # Profile errors
        {"error_code": 2001, "error_type": "PROFILE", "error_description": "Phone number verification required"},
        {"error_code": 2002, "error_type": "PROFILE", "error_description": "Email verification required"},
        {"error_code": 2003, "error_type": "PROFILE", "error_description": "Complete profile information required"},
        
        # Vehicle errors
        {"error_code": 3001, "error_type": "VEHICLE", "error_description": "Vehicle registration number mismatch"},
        {"error_code": 3002, "error_type": "VEHICLE", "error_description": "Vehicle type not supported"},
        {"error_code": 3003, "error_type": "VEHICLE", "error_description": "Vehicle condition not acceptable"},
    ]
    
    try:
        for error_data in predefined_errors:
            # Check if error already exists
            existing = db.query(ErrorHandling).filter(ErrorHandling.error_code == error_data["error_code"]).first()
            if not existing:
                import uuid
                error_data["error_id"] = str(uuid.uuid4())
                error = ErrorHandling(**error_data)
                db.add(error)
        
        db.commit()
        print("Predefined errors populated successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_predefined_errors()