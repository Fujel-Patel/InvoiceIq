from __future__ import annotations

"""Utility functions for file validation."""

from typing import List

# Allowed MIME types for file uploads
ALLOWED_TYPES: List[str] = ["image/jpeg", "image/png", "application/pdf"]

# Maximum file size in megabytes
MAX_SIZE_MB: int = 10


def check_file_type(content_type: str) -> bool:
    """
    Check if the file content type is allowed.

    Args:
        content_type: The MIME type of the file

    Returns:
        True if file type is allowed, False otherwise
    """
    return content_type in ALLOWED_TYPES


def check_file_size(size_bytes: int) -> bool:
    """
    Check if the file size is within the allowed limit.

    Args:
        size_bytes: The file size in bytes

    Returns:
        True if file size is within limit, False otherwise
    """
    max_size_bytes = MAX_SIZE_MB * 1024 * 1024
    return size_bytes <= max_size_bytes