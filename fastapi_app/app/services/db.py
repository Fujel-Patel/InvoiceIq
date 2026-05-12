from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from ..core.config import settings
from ..models.invoice import ExtractedInvoice


class DatabaseService:
    """Service for Supabase database operations."""

    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.table_name = "extractions"

    async def save_extraction(
        self,
        extraction_id: str,
        filename: str,
        user_id: str,
        data: ExtractedInvoice,
        status: str
    ) -> Dict[str, Any]:
        """
        Save an extraction record to the database.

        Args:
            extraction_id: Unique ID for the extraction
            filename: Original filename of the uploaded file
            user_id: ID of the user who uploaded the file
            data: Extracted invoice data
            status: Status of the extraction (success, partial, failed)

        Returns:
            The saved extraction record
        """
        record = {
            "id": extraction_id,
            "filename": filename,
            "user_id": user_id,
            "extracted_data": data.dict(),
            "status": status,
        }

        result = self.supabase.table(self.table_name).insert(record).execute()

        if not result.data:
            raise Exception("Failed to save extraction to database")

        return result.data[0]

    async def get_extraction_by_id(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an extraction record by its ID.

        Args:
            extraction_id: The UUID of the extraction to retrieve

        Returns:
            The extraction record if found, None otherwise
        """
        result = self.supabase.table(self.table_name).select("*").eq("id", extraction_id).execute()

        if not result.data:
            return None

        return result.data[0]

    async def update_extraction(self, extraction_id: str, data: ExtractedInvoice) -> Optional[Dict[str, Any]]:
        """
        Update an extraction record with new data.

        Args:
            extraction_id: The UUID of the extraction to update
            data: New extracted invoice data

        Returns:
            The updated extraction record if found, None otherwise
        """
        result = self.supabase.table(self.table_name).update({
            "extracted_data": data.dict(),
            "updated_at": "now()"  # Supabase will handle the timestamp
        }).eq("id", extraction_id).execute()

        if not result.data:
            return None

        return result.data[0]

    async def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get extraction history for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of extraction records for the user
        """
        result = self.supabase.table(self.table_name).select("*").eq("user_id", user_id).order("created_at", desc=True).execute()

        return result.data if result.data else []