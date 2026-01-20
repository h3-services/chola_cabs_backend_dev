"""
Cloud Storage Service - S3-Compatible (AWS S3, Cloudflare R2, etc.)
Handles file uploads to cloud storage instead of local file system
"""
import os
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        # Configuration from environment variables
        self.use_s3 = os.getenv("USE_S3_STORAGE", "false").lower() == "true"
        
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
                endpoint_url=os.getenv("S3_ENDPOINT_URL"),  # For Cloudflare R2 or custom endpoint
                region_name=os.getenv("S3_REGION", "auto")
            )
            self.bucket_name = os.getenv("S3_BUCKET_NAME")
            self.base_url = os.getenv("S3_PUBLIC_URL", f"https://{self.bucket_name}.s3.amazonaws.com")
        else:
            # Fallback to local storage
            self.upload_dir = os.getenv("UPLOAD_DIR", "d:/cab_ap/uploads")
            self.base_url = os.getenv("BASE_URL", "http://localhost:8000/uploads")
    
    def save_file(self, file: UploadFile, folder: str) -> str:
        """
        Save file to cloud storage or local file system
        Returns: Public URL of the uploaded file
        """
        # Validate file extension
        allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(400, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = f"{folder}/{filename}"
        
        if self.use_s3:
            return self._upload_to_s3(file, file_path)
        else:
            return self._upload_to_local(file, folder, filename)
    
    def _upload_to_s3(self, file: UploadFile, file_path: str) -> str:
        """Upload file to S3-compatible storage"""
        try:
            # Determine content type
            content_type = file.content_type or "application/octet-stream"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                file_path,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'  # Make file publicly accessible
                }
            )
            
            # Generate public URL
            url = f"{self.base_url}/{file_path}"
            logger.info(f"File uploaded to S3: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise HTTPException(500, f"Failed to upload file to cloud storage: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            raise HTTPException(500, f"Upload failed: {str(e)}")
    
    def _upload_to_local(self, file: UploadFile, folder: str, filename: str) -> str:
        """Upload file to local file system (fallback)"""
        try:
            import shutil
            
            # Create directory if it doesn't exist
            folder_path = os.path.join(self.upload_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
            
            # Save file
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Generate URL
            url = f"{self.base_url}/{folder}/{filename}"
            logger.info(f"File uploaded locally: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Local upload failed: {str(e)}")
            raise HTTPException(500, f"Failed to save file: {str(e)}")
    
    def delete_file(self, file_url: str) -> bool:
        """Delete file from storage (optional, for cleanup)"""
        if self.use_s3:
            return self._delete_from_s3(file_url)
        else:
            return self._delete_from_local(file_url)
    
    def _delete_from_s3(self, file_url: str) -> bool:
        """Delete file from S3"""
        try:
            # Extract file path from URL
            file_path = file_url.replace(self.base_url + "/", "")
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            logger.info(f"File deleted from S3: {file_path}")
            return True
        except Exception as e:
            logger.error(f"S3 delete failed: {str(e)}")
            return False
    
    def _delete_from_local(self, file_url: str) -> bool:
        """Delete file from local storage"""
        try:
            # Extract file path from URL
            file_path = file_url.replace(self.base_url + "/", "")
            full_path = os.path.join(self.upload_dir, file_path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f"File deleted locally: {full_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Local delete failed: {str(e)}")
            return False

# Singleton instance
storage_service = StorageService()
