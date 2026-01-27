"""
Application Configuration Management
Centralized configuration using Pydantic Settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = Field(default="Cab Booking API", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_PORT: int = Field(default=3306, env="DB_PORT")
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_NAME: str = Field(..., env="DB_NAME")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="/root/chola_cabs_backend_dev/uploads", env="UPLOAD_DIR")
    BASE_URL: str = Field(default="https://api.cholacabs.in", env="BASE_URL")
    
    # S3 Storage (Optional)
    USE_S3_STORAGE: bool = Field(default=False, env="USE_S3_STORAGE")
    S3_ACCESS_KEY: Optional[str] = Field(default=None, env="S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = Field(default=None, env="S3_SECRET_KEY")
    S3_ENDPOINT_URL: Optional[str] = Field(default=None, env="S3_ENDPOINT_URL")
    S3_REGION: str = Field(default="auto", env="S3_REGION")
    S3_BUCKET_NAME: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    S3_PUBLIC_URL: Optional[str] = Field(default=None, env="S3_PUBLIC_URL")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    CORS_ORIGINS: list = Field(default=["*"], env="CORS_ORIGINS")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=100, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=1000, env="MAX_PAGE_SIZE")
    
    # FCM (Firebase Cloud Messaging)
    FCM_SERVER_KEY: Optional[str] = Field(default=None, env="FCM_SERVER_KEY")
    MAX_FCM_TOKENS_PER_DRIVER: int = Field(default=5, env="MAX_FCM_TOKENS_PER_DRIVER")
    
    # Payment Gateway (Razorpay)
    RAZORPAY_KEY_ID: Optional[str] = Field(default=None, env="RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET: Optional[str] = Field(default=None, env="RAZORPAY_KEY_SECRET")
    
    @property
    def database_url(self) -> str:
        """Generate MySQL database URL"""
        from urllib.parse import quote_plus
        password = quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
        return f"mysql+pymysql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def upload_url_base(self) -> str:
        """Base URL for uploaded files"""
        return f"{self.BASE_URL}/uploads"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
