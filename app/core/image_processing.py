from PIL import Image
import io
import os
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

def compress_image(file: UploadFile, max_size_kb: int = 500, quality: int = 80, max_dimension: int = 1200) -> io.BytesIO:
    """
    Compresses an image to a target size in KB while maintaining aspect ratio.
    
    Args:
        file: The uploaded file from FastAPI
        max_size_kb: Target maximum size in KB
        quality: Initial JPEG quality
        max_dimension: Maximum width or height of the image
        
    Returns:
        io.BytesIO: Buffer containing the compressed image data
    """
    # Read image data
    image_data = file.file.read()
    img = Image.open(io.BytesIO(image_data))
    
    # Reset file pointer for potential future reads (standard practice)
    file.file.seek(0)
    
    # Convert PNG/RGBA to RGB (JPEG doesn't support transparency)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # 1. Resize if image is too large
    width, height = img.size
    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")

    # 2. Compress and optimize
    output_buffer = io.BytesIO()
    
    # Save with initial quality
    img.save(output_buffer, format="JPEG", optimize=True, quality=quality)
    
    # 3. If still too large, reduce quality incrementally (up to a limit)
    while output_buffer.tell() > max_size_kb * 1024 and quality > 30:
        quality -= 10
        output_buffer = io.BytesIO()
        img.save(output_buffer, format="JPEG", optimize=True, quality=quality)
        logger.info(f"Reducing quality to {quality} to meet size limit of {max_size_kb}KB")

    output_buffer.seek(0)
    return output_buffer
