"""
File Upload API Routes

File upload and management endpoints.
"""

import logging
import os
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_async_session
from core.dependencies import get_current_active_user
from models.user import User
from services.file_service import FileService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    project_id: int = None,
    task_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Upload a file
    """
    try:
        # Validate file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes",
            )

        # Generate unique filename
        file_extension = Path(file.filename or "").suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_PATH)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = upload_dir / unique_filename

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Save file metadata to database
        file_service = FileService(db)
        file_record = await file_service.create_file_record(
            filename=file.filename or unique_filename,
            file_path=str(file_path),
            file_size=len(content),
            mime_type=file.content_type,
            uploaded_by=current_user.id,
            project_id=project_id,
            task_id=task_id,
        )

        logger.info(f"File uploaded by {current_user.name}: {file.filename}")

        return {
            "id": file_record.id,
            "filename": file_record.filename,
            "file_size": file_record.file_size,
            "mime_type": file_record.mime_type,
            "upload_date": file_record.created_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        # Clean up file if database operation failed
        if "file_path" in locals() and file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file",
        )


@router.get("/{file_id}")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Download a file
    """
    try:
        file_service = FileService(db)
        file_record = await file_service.get_file_with_access_check(
            file_id, current_user.id
        )

        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        file_path = Path(file_record.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk"
            )

        return FileResponse(
            path=str(file_path),
            filename=file_record.filename,
            media_type=file_record.mime_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download file",
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Delete a file
    """
    try:
        file_service = FileService(db)
        success = await file_service.delete_file(file_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        logger.info(f"File deleted by {current_user.name}: {file_id}")

        return {"message": "File deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file",
        )
