"""
Tariff Configuration API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import VehicleTariffConfig
from app.schemas import VehicleTariffConfigCreate, VehicleTariffConfigUpdate, VehicleTariffConfigResponse
from app.crud.crud_payment import crud_tariff

router = APIRouter(prefix="/tariff-config", tags=["tariff-config"])

@router.get("/", response_model=List[VehicleTariffConfigResponse])
def get_all_tariff_configs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all tariff configurations"""
    configs = crud_tariff.get_multi(db, skip=skip, limit=limit)
    return configs

@router.get("/{config_id}", response_model=VehicleTariffConfigResponse)
def get_tariff_config_details(config_id: str, db: Session = Depends(get_db)):
    """Get tariff configuration details by ID"""
    config = crud_tariff.get(db, id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff configuration not found"
        )
    return config

@router.post("/", response_model=VehicleTariffConfigResponse, status_code=status.HTTP_201_CREATED)
def create_tariff_config(config: VehicleTariffConfigCreate, db: Session = Depends(get_db)):
    """Create a new tariff configuration"""
    # Generate UUID for tariff_id
    import uuid
    config_data = config.dict()
    config_data['tariff_id'] = str(uuid.uuid4())
    
    db_config = VehicleTariffConfig(**config_data)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.put("/{config_id}", response_model=VehicleTariffConfigResponse)
def update_tariff_config(
    config_id: str, 
    config_update: VehicleTariffConfigUpdate, 
    db: Session = Depends(get_db)
):
    """Update tariff configuration"""
    config = crud_tariff.get(db, id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff configuration not found"
        )
    
    updated_config = crud_tariff.update(db, db_obj=config, obj_in=config_update)
    return updated_config

@router.patch("/{config_id}/toggle-active", response_model=VehicleTariffConfigResponse)
def toggle_tariff_config_active(config_id: str, db: Session = Depends(get_db)):
    """Toggle is_active status for a tariff configuration"""
    config = crud_tariff.get(db, id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff configuration not found"
        )
    
    config.is_active = not config.is_active
    db.commit()
    db.refresh(config)
    return config

@router.delete("/{config_id}")
def delete_tariff_config(config_id: str, db: Session = Depends(get_db)):
    """Delete a tariff configuration"""
    config = crud_tariff.get(db, id=config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff configuration not found"
        )
    
    crud_tariff.delete(db, id=config_id)
    db.commit()
    
    return {
        "message": "Tariff configuration deleted successfully",
        "config_id": config_id
    }

@router.get("/vehicle-type/{vehicle_type}", response_model=List[VehicleTariffConfigResponse])
def get_tariff_configs_by_vehicle_type(vehicle_type: str, db: Session = Depends(get_db)):
    """Get tariff configurations for a specific vehicle type"""
    configs = crud_tariff.get_multi(db)
    configs = [c for c in configs if c.vehicle_type == vehicle_type]
    return configs

@router.get("/active/{vehicle_type}", response_model=VehicleTariffConfigResponse)
def get_active_tariff_config(vehicle_type: str, db: Session = Depends(get_db)):
    """Get active tariff configuration for a vehicle type"""
    config = crud_tariff.get_multi(db)
    config = next((c for c in config if c.vehicle_type == vehicle_type and c.is_active), None)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active tariff configuration found for vehicle type: {vehicle_type}"
        )
    
    return config