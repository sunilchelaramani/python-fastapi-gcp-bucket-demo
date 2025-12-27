from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from app.config import settings, get_allowed_extensions
from app.storage import storage_service
import logging
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GCP Bucket File API",
    description="API for uploading, downloading, and deleting files from GCP Cloud Storage",
    version="1.0.0"
)


def validate_file_size(file_size: int) -> None:
    """Validate file size against configured limit."""
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size} bytes) exceeds maximum allowed size ({settings.MAX_FILE_SIZE} bytes)"
        )


def validate_file_type(filename: str) -> None:
    """Validate file type against allowed extensions."""
    allowed_extensions = get_allowed_extensions()
    if allowed_extensions is None:
        return  # All types allowed
    
    file_ext = filename.split(".")[-1].lower() if "." in filename else ""
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to GCP bucket.
    
    - **file**: The file to upload (multipart/form-data)
    
    Returns file metadata including filename, size, and bucket path.
    """
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        validate_file_size(file_size)
        
        # Validate file type
        validate_file_type(file.filename)
        
        # Upload to GCP bucket
        result = storage_service.upload_file(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        logger.info(f"File uploaded successfully: {file.filename}")
        return {
            "message": "File uploaded successfully",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a file from GCP bucket.
    
    - **filename**: Name of the file to download
    
    Returns the file as a streaming response.
    """
    try:
        # Download file from bucket
        file_content = storage_service.download_file(filename)
        
        # Get file metadata for content type
        metadata = storage_service.get_file_metadata(filename)
        content_type = metadata.get("content_type", "application/octet-stream")
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.delete("/delete/{filename}")
async def delete_file(filename: str):
    """
    Delete a file from GCP bucket.
    
    - **filename**: Name of the file to delete
    
    Returns success message.
    """
    try:
        result = storage_service.delete_file(filename)
        logger.info(f"File deleted successfully: {filename}")
        return {
            "message": "File deleted successfully",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "GCP Bucket File API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload",
            "download": "/download/{filename}",
            "delete": "/delete/{filename}"
        }
    }

