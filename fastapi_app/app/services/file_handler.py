from __future__ import annotations

import base64
import mimetypes
from typing import Optional
import uuid
from fastapi import UploadFile, HTTPException, status
from pathlib import Path

from ..core.config import settings
from ..utils.validators import check_file_type, check_file_size


def validate_file(file: UploadFile) -> None:
    """
    Validate file type and size.

    Args:
        file: The uploaded file to validate

    Raises:
        HTTPException: If file type or size is invalid
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(settings.ALLOWED_TYPES)}"
        )


async def convert_to_base64(file: UploadFile) -> str:
    """
    Convert uploaded file to base64 string.

    Args:
        file: The uploaded file to convert

    Returns:
        Base64 encoded string of the file content
    """
    content = await file.read()
    # Reset file position for potential reuse
    await file.seek(0)
    return base64.b64encode(content).decode('utf-8')


def get_media_type(filename: str) -> str:
    """
    Get the correct MIME type for a filename.

    Args:
        filename: The name of the file

    Returns:
        MIME type string (e.g., 'image/jpeg', 'application/pdf')
    """
    # Initialize mimetypes if needed
    mimetypes.init()

    # Get MIME type
    media_type, _ = mimetypes.guess_type(filename)

    # Fallback mappings for common file types
    if media_type is None:
        extension = Path(filename).suffix.lower()
        fallback_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.pdf': 'application/pdf'
        }
        media_type = fallback_map.get(extension, 'application/octet-stream')

    return media_type


class FileHandler:
    """Service for handling file uploads and temporary storage."""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)

    async def save_upload_file(self, file: UploadFile) -> tuple[str, Path]:
        """
        Save an uploaded file to disk and return the file ID and path.

        Args:
            file: The uploaded file

        Returns:
            Tuple of (file_id, file_path)
        """
        # Generate a unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix if file.filename else ""
        safe_filename = f"{file_id}{file_extension}"
        file_path = self.upload_dir / safe_filename

        # Save the file
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        return file_id, file_path

    async def delete_file(self, file_path: Path) -> bool:
        """
        Delete a file from disk.

        Args:
            file_path: Path to the file to delete

        Returns:
            True if file was deleted, False if it didn't exist
        """
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except OSError:
            return False

    def get_file_path(self, file_id: str) -> Optional[Path]:
        """
        Get the file path for a given file ID.

        Args:
            file_id: The unique file ID

        Returns:
            Path to the file if found, None otherwise
        """
        # Find file with matching ID (any extension)
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file() and file_path.stem == file_id:
                return file_path
        return None