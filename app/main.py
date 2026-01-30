"""
Main FastAPI application for Cab Booking System
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.database import engine, Base
from app.routers import drivers, vehicles, trips, payments, wallet_transactions, tariff_config, raw_data, uploads, error_handling, trip_requests, admins, analytics

# Load environment variables
load_dotenv()

# Create FastAPI app
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title=os.getenv("APP_NAME", "Cab Booking API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Production-ready Cab Booking Management System",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=ORJSONResponse
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created successfully")
except Exception as e:
    print(f"[ERROR] Error creating database tables: {e}")

# Mount static files for uploads
UPLOAD_DIR = "/var/www/projects/client_side/chola_cabs/backend/cab_app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(drivers.router, prefix="/api")
app.include_router(vehicles.router, prefix="/api")
app.include_router(trips.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(wallet_transactions.router, prefix="/api")
app.include_router(tariff_config.router, prefix="/api")
app.include_router(raw_data.router, prefix="/api")
app.include_router(error_handling.router, prefix="/api")
app.include_router(trip_requests.router, prefix="/api")
app.include_router(admins.router)
app.include_router(uploads.router)
app.include_router(analytics.router)

@app.get("/test-file/{filename}")
def test_file_exists(filename: str):
    """Test if uploaded file exists"""
    import os
    file_path = f"/var/www/projects/client_side/chola_cabs/backend/cab_app/uploads/drivers/photos/{filename}"
    exists = os.path.exists(file_path)
    if exists:
        size = os.path.getsize(file_path)
        return {"exists": True, "path": file_path, "size": size}
    else:
        return {"exists": False, "path": file_path}

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Cab Booking API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        from app.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": os.getenv("APP_VERSION", "1.0.0")
    }

@app.get("/api/stats")
def get_api_stats():
    """Get basic API statistics"""
    try:
        from app.database import SessionLocal
        from app.models import Driver, Vehicle, Trip
        
        db = SessionLocal()
        
        # Get counts
        total_drivers = db.query(Driver).count()
        active_drivers = db.query(Driver).filter(Driver.is_available == True).count()
        total_vehicles = db.query(Vehicle).count()
        approved_vehicles = db.query(Vehicle).filter(Vehicle.vehicle_approved == True).count()
        total_trips = db.query(Trip).count()
        pending_trips = db.query(Trip).filter(Trip.trip_status == "OPEN").count()
        completed_trips = db.query(Trip).filter(Trip.trip_status == "COMPLETED").count()
        
        db.close()
        
        return {
            "drivers": {
                "total": total_drivers,
                "active": active_drivers,
                "inactive": total_drivers - active_drivers
            },
            "vehicles": {
                "total": total_vehicles,
                "approved": approved_vehicles,
                "pending_approval": total_vehicles - approved_vehicles
            },
            "trips": {
                "total": total_trips,
                "pending": pending_trips,
                "completed": completed_trips
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )