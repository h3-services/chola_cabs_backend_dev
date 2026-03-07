from app.database import SessionLocal
from app.models import ErrorHandling
import json

db = SessionLocal()
try:
    errors = db.query(ErrorHandling).all()
    print(f"Total errors: {len(errors)}")
    for error in errors:
        print(json.dumps({
            "error_id": error.error_id,
            "error_type": error.error_type,
            "error_code": error.error_code,
            "error_description": error.error_description,
            "created_at": str(error.created_at)
        }))
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
