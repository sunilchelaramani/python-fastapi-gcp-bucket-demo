from google.cloud import storage
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """Service for interacting with Google Cloud Storage."""
    
    def __init__(self):
        """Initialize GCP Storage client."""
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(settings.GCP_BUCKET_NAME)
            logger.info(f"Initialized storage client for bucket: {settings.GCP_BUCKET_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize storage client: {str(e)}")
            raise
    
    def upload_file(self, file_content: bytes, filename: str, content_type: str = None) -> dict:
        """
        Upload a file to GCP bucket.
        
        Args:
            file_content: File content as bytes
            filename: Name of the file
            content_type: MIME type of the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            blob = self.bucket.blob(filename)
            blob.upload_from_string(
                file_content,
                content_type=content_type
            )
            
            logger.info(f"Successfully uploaded file: {filename}")
            return {
                "filename": filename,
                "bucket": settings.GCP_BUCKET_NAME,
                "size": len(file_content),
                "content_type": content_type
            }
        except Exception as e:
            logger.error(f"Failed to upload file {filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    def download_file(self, filename: str) -> bytes:
        """
        Download a file from GCP bucket.
        
        Args:
            filename: Name of the file to download
            
        Returns:
            File content as bytes
        """
        try:
            blob = self.bucket.blob(filename)
            
            if not blob.exists():
                logger.warning(f"File not found: {filename}")
                raise HTTPException(
                    status_code=404,
                    detail=f"File '{filename}' not found in bucket"
                )
            
            file_content = blob.download_as_bytes()
            logger.info(f"Successfully downloaded file: {filename}")
            return file_content
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to download file {filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download file: {str(e)}"
            )
    
    def get_file_metadata(self, filename: str) -> dict:
        """
        Get metadata for a file in the bucket.
        
        Args:
            filename: Name of the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            blob = self.bucket.blob(filename)
            
            if not blob.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"File '{filename}' not found in bucket"
                )
            
            blob.reload()
            return {
                "filename": filename,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get metadata for file {filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get file metadata: {str(e)}"
            )
    
    def delete_file(self, filename: str) -> dict:
        """
        Delete a file from GCP bucket.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            Dictionary with success message
        """
        try:
            blob = self.bucket.blob(filename)
            
            if not blob.exists():
                logger.warning(f"File not found for deletion: {filename}")
                raise HTTPException(
                    status_code=404,
                    detail=f"File '{filename}' not found in bucket"
                )
            
            blob.delete()
            logger.info(f"Successfully deleted file: {filename}")
            return {
                "message": f"File '{filename}' deleted successfully",
                "filename": filename
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete file {filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file: {str(e)}"
            )


# Global storage service instance
storage_service = StorageService()

