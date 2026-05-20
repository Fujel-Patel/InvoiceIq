from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status as status_code

from fastapi_app.app.core.config import settings
from fastapi_app.app.models.invoice import ExtractedInvoice
from fastapi_app.app.schemas.extraction import ExtractionResponse
from fastapi_app.app.services.file_handler import FileHandler, validate_file, convert_to_base64, get_media_type
from fastapi_app.app.services.llm import ClaudeService
from fastapi_app.app.services.parser import parse_llm_response, determine_status
from fastapi_app.app.services.db import DatabaseService
from fastapi_app.app.utils.auth import get_current_user
from fastapi_app.app.utils.validators import check_file_size, check_file_type

router = APIRouter()


@router.post("/extract/upload", status_code=status_code.HTTP_201_CREATED)
async def upload_and_extract(
    file: UploadFile = File(...),
    file_handler: FileHandler = Depends(FileHandler),
    claude_service: ClaudeService = Depends(),
    db_service: DatabaseService = Depends(),
    current_user: str = Depends(get_current_user)
) -> ExtractionResponse:
    """
    Upload a file and extract invoice data using Claude Vision API.

    Args:
        file: The uploaded file (image or PDF)
        file_handler: Service for handling file operations
        claude_service: Service for Claude API interactions
        db_service: Service for database operations
        current_user: ID of the authenticated user

    Returns:
        ExtractionResponse with structured invoice data

    Raises:
        HTTPException: If file validation fails or processing errors occur
    """
    # Validate file using our service (checks extension)
    validate_file(file)

    # Read file content for size and type validation
    content = await file.read()
    await file.seek(0)

    # Validate file size using utility function
    if not check_file_size(len(content)):
        raise HTTPException(
            status_code=status_code.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )

    # Validate file type using utility function (checks actual content type)
    # Note: For UploadFile, we need to get the content type from the file
    # In a real scenario, you might also want to validate the actual file content
    # For now, we'll rely on extension validation in validate_file and
    # optionally check content-type if provided
    if file.content_type and not check_file_type(file.content_type):
        raise HTTPException(
            status_code=status_code.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(settings.ALLOWED_TYPES)}"
        )

    try:
        # Convert file to base64 using our service
        base64_content = await convert_to_base64(file)

        # Get media type using our service
        media_type = get_media_type(file.filename or "")

        # Extract invoice data using Claude Vision
        extraction_result = await claude_service.extract_invoice_data(
            base64_file=base64_content,
            media_type=media_type
        )

        # Parse and validate the extracted data using our parser
        validated_data: ExtractedInvoice = parse_llm_response(extraction_result)

        # Determine extraction status
        extraction_status = determine_status(validated_data)

        # Generate extraction ID
        extraction_id = str(uuid.uuid4())

        # Save to database
        extraction_record = await db_service.save_extraction(
            extraction_id=extraction_id,
            filename=file.filename or "unknown",
            user_id=current_user,
            data=validated_data,
            status=extraction_status
        )

        # Return ExtractionResponse format
        return ExtractionResponse(
            extraction_id=extraction_record["id"],
            status=extraction_status,
            data=validated_data,
            raw_text=None  # We don't store the raw text currently
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status_code.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during processing: {str(e)}"
        )


@router.get("/extract/{extraction_id}")
async def get_extraction(
    extraction_id: str,
    db_service: DatabaseService = Depends(),
    current_user: str = Depends(get_current_user)
) -> ExtractionResponse:
    """
    Retrieve an extraction record by its ID.

    Args:
        extraction_id: The ID of the extraction to retrieve
        db_service: Service for database operations
        current_user: ID of the authenticated user

    Returns:
        ExtractionResponse with the extraction data

    Raises:
        HTTPException: If extraction record is not found or not authorized
    """
    extraction_record = await db_service.get_extraction_by_id(extraction_id)

    if not extraction_record:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND,
            detail=f"Extraction with ID {extraction_id} not found"
        )

    # Check if the extraction belongs to the current user
    if extraction_record.get("user_id") != current_user:
        raise HTTPException(
            status_code=status_code.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this extraction"
        )

    # Convert the database record to ExtractionResponse format
    extracted_data = ExtractedInvoice(**extraction_record["full_data"])

    return ExtractionResponse(
        extraction_id=extraction_record["id"],
        status=extraction_record["status"],
        data=extracted_data,
        raw_text=None  # Raw text not stored in DB
    )


@router.put("/extract/{extraction_id}")
async def update_extraction(
    extraction_id: str,
    updated_data: ExtractedInvoice,
    db_service: DatabaseService = Depends(),
    current_user: str = Depends(get_current_user)
) -> ExtractionResponse:
    """
    Update an extraction record with new data.

    Args:
        extraction_id: The ID of the extraction to update
        updated_data: The updated invoice data
        db_service: Service for database operations
        current_user: ID of the authenticated user

    Returns:
        ExtractionResponse with the updated extraction data

    Raises:
        HTTPException: If extraction record is not found, not authorized, or update fails
    """
    # First check if the extraction exists and belongs to the user
    extraction_record = await db_service.get_extraction_by_id(extraction_id)

    if not extraction_record:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND,
            detail=f"Extraction with ID {extraction_id} not found"
        )

    # Check if the extraction belongs to the current user
    if extraction_record.get("user_id") != current_user:
        raise HTTPException(
            status_code=status_code.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this extraction"
        )

    # Update the extraction in the database
    updated_record = await db_service.update_extraction(extraction_id, updated_data)

    if not updated_record:
        raise HTTPException(
            status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update extraction"
        )

    # Convert the updated database record to ExtractionResponse format
    extracted_data = ExtractedInvoice(**updated_record["full_data"])

    return ExtractionResponse(
        extraction_id=updated_record["id"],
        status=updated_record["status"],
        data=extracted_data,
        raw_text=None  # Raw text not stored in DB
    )