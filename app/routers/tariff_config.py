"""
Tariff Configuration API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import VehicleTariffConfig
from app.schemas import VehicleTariffConfigCreate, VehicleTariffConfigUpdate, VehicleTariffConfigResponse

router = APIRouter(prefix="/tariff-config", tags=["tariff-config"])

@router.get("/", response_model=List[VehicleTariffConfigResponse])
def get_all_tariff_configs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all tariff configurations"""
    configs = db.query(VehicleTariffConfig).offset(skip).limit(limit).all()
    return configs

@router.get("/{config_id}", response_model=VehicleTariffConfigResponse)
def get_tariff_config_details(config_id: int, db: Session = Depends(get_db)):
    """Get tariff configuration details by ID"""
    config = db.query(VehicleTariffConfig).filter(VehicleTariffConfig.config_id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff configuration not found"
        )
    return config

@router.post("/", response_model=VehicleTariffConfigResponse, status_code=status.HTTP_201_CREATED)
def create_tariff_config(config: VehicleTariffConfigCreate, db: Session = Depends(get_db)):
    """Create a new tariff configuration"""
    db_config = VehicleTariffConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.put("/{config_id}", response_model=VehicleTariffConfigResponse)
def update_tariff_config(
    config_id: int, 
    config_update: VehicleTariffConfigUpdate, 
    db: Session = Depends(get_db)
):
    """Update tariff configuration"""
    config = db.query(VehicleTariffConfig).filter(VehicleTariffConfig.config_id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff configuration not found"
        )
    
    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    return config

@router.delete("/{config_id}")
def delete_tariff_config(config_id: int, db: Session = Depends(get_db)):
    """Delete a tariff configuration"""
    config = db.query(VehicleTariffConfig).filter(VehicleTariffConfig.config_id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff configuration not found"
        )
    
    db.delete(config)
    db.commit()
    
    return {
        "message": "Tariff configuration deleted successfully",
        "config_id": config_id
    }

@router.get("/vehicle-type/{vehicle_type}", response_model=List[VehicleTariffConfigResponse])
def get_tariff_configs_by_vehicle_type(vehicle_type: str, db: Session = Depends(get_db)):
    """Get tariff configurations for a specific vehicle type"""
    configs = db.query(VehicleTariffConfig).filter(VehicleTariffConfig.vehicle_type == vehicle_type).all()
    return configs

@router.get("/active/{vehicle_type}", response_model=VehicleTariffConfigResponse)
def get_active_tariff_config(vehicle_type: str, db: Session = Depends(get_db)):
    """Get active tariff configuration for a vehicle type"""
    config = db.query(VehicleTariffConfig).filter(
        VehicleTariffConfig.vehicle_type == vehicle_type,
        VehicleTariffConfig.is_active == True
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active tariff configuration found for vehicle type: {vehicle_type}"
        )
    
    return config