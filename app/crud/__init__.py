"""
CRUD operations for all models
Centralized database access layer with optimizations
"""
from app.crud.base import CRUDBase
from app.crud.crud_driver import crud_driver
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_trip import crud_trip
from app.crud.crud_payment import crud_payment
from app.crud.crud_wallet import crud_wallet
from app.crud.crud_admin import crud_admin
from app.crud.crud_tariff import crud_tariff

__all__ = [
    "CRUDBase",
    "crud_driver",
    "crud_vehicle",
    "crud_trip",
    "crud_payment",
    "crud_wallet",
    "crud_admin",
    "crud_tariff",
]
