"""
Base CRUD class with generic database operations
Optimized for production use with eager loading and selective column loading
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session, Query
from sqlalchemy import inspect

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with generic database operations
    
    Features:
    - Generic CRUD operations (Create, Read, Update, Delete)
    - Pagination support
    - Selective column loading
    - Eager loading support
    - Optimized for production
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model class
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def get(
        self,
        db: Session,
        id: Any,
        eager_load: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """
        Get a single record by ID with optional eager loading
        
        Args:
            db: Database session
            id: Primary key value
            eager_load: List of relationship names to eager load
        
        Returns:
            Model instance or None
        """
        query = db.query(self.model)
        
        # Add eager loading if specified
        if eager_load:
            from sqlalchemy.orm import joinedload
            for relationship in eager_load:
                query = query.options(joinedload(getattr(self.model, relationship)))
        
        # Get primary key column name
        pk_column = inspect(self.model).primary_key[0]
        return query.filter(pk_column == id).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        eager_load: Optional[List[str]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination, filtering, and eager loading
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of column:value filters
            eager_load: List of relationship names to eager load
            order_by: Column name to order by (prefix with - for descending)
        
        Returns:
            List of model instances
        """
        query = db.query(self.model)
        
        # Apply filters
        if filters:
            for column, value in filters.items():
                if hasattr(self.model, column):
                    query = query.filter(getattr(self.model, column) == value)
        
        # Add eager loading
        if eager_load:
            from sqlalchemy.orm import joinedload
            for relationship in eager_load:
                if hasattr(self.model, relationship):
                    query = query.options(joinedload(getattr(self.model, relationship)))
        
        # Add ordering
        if order_by:
            if order_by.startswith('-'):
                # Descending order
                column_name = order_by[1:]
                if hasattr(self.model, column_name):
                    query = query.order_by(getattr(self.model, column_name).desc())
            else:
                # Ascending order
                if hasattr(self.model, order_by):
                    query = query.order_by(getattr(self.model, order_by))
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(
        self,
        db: Session,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Get count of records with optional filtering
        
        Args:
            db: Database session
            filters: Dictionary of column:value filters
        
        Returns:
            Count of records
        """
        query = db.query(self.model)
        
        if filters:
            for column, value in filters.items():
                if hasattr(self.model, column):
                    query = query.filter(getattr(self.model, column) == value)
        
        return query.count()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record
        
        Args:
            db: Database session
            obj_in: Pydantic schema with data to create
        
        Returns:
            Created model instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record
        
        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Pydantic schema or dict with update data
        
        Returns:
            Updated model instance
        """
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """
        Delete a record by ID
        
        Args:
            db: Database session
            id: Primary key value
        
        Returns:
            Deleted model instance or None
        """
        obj = self.get(db, id=id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def exists(self, db: Session, id: Any) -> bool:
        """
        Check if a record exists by ID
        
        Args:
            db: Database session
            id: Primary key value
        
        Returns:
            True if exists, False otherwise
        """
        pk_column = inspect(self.model).primary_key[0]
        return db.query(self.model).filter(pk_column == id).first() is not None
    
    def get_or_create(
        self,
        db: Session,
        *,
        defaults: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> tuple[ModelType, bool]:
        """
        Get an existing record or create a new one
        
        Args:
            db: Database session
            defaults: Default values for creation
            **kwargs: Filter criteria
        
        Returns:
            Tuple of (model instance, created boolean)
        """
        query = db.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        instance = query.first()
        
        if instance:
            return instance, False
        else:
            params = kwargs.copy()
            if defaults:
                params.update(defaults)
            instance = self.model(**params)
            db.add(instance)
            db.commit()
            db.refresh(instance)
            return instance, True
