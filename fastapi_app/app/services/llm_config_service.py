from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from ..core.config import settings
from ..models.llm_config import LLMConfigCreate, LLMConfigUpdate, LLMConfigInDBBase


class LLMConfigService:
    """Service for managing LLM configuration in the database."""

    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.table_name = "llm_configs"

    async def create_llm_config(
        self,
        user_id: str,
        config: LLMConfigCreate
    ) -> Dict[str, Any]:
        """
        Create a new LLM configuration for a user.

        Args:
            user_id: ID of the user
            config: LLM configuration to create

        Returns:
            The created LLM configuration record
        """
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "provider": config.provider,
            "api_key": config.api_key,
            "model": config.model,
            "created_at": "now()",
            "updated_at": "now()"
        }

        result = self.supabase.table(self.table_name).insert(record).execute()

        if not result.data:
            raise Exception("Failed to create LLM configuration")

        return result.data[0]

    async def get_llm_config_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get LLM configuration for a user.

        Args:
            user_id: ID of the user

        Returns:
            The LLM configuration record if found, None otherwise
        """
        result = self.supabase.table(self.table_name).select("*").eq("user_id", user_id).execute()

        if not result.data:
            return None

        # Assuming there is at most one config per user, return the first
        return result.data[0]

    async def update_llm_config(
        self,
        user_id: str,
        config_update: LLMConfigUpdate
    ) -> Optional[Dict[str, Any]]:
        """
        Update LLM configuration for a user.

        Args:
            user_id: ID of the user
            config_update: LLM configuration update

        Returns:
            The updated LLM configuration record if found, None otherwise
        """
        # First, get the existing config to ensure it exists
        existing = await self.get_llm_config_by_user_id(user_id)
        if not existing:
            return None

        # Prepare update data
        update_data = {}
        if config_update.provider is not None:
            update_data["provider"] = config_update.provider
        if config_update.api_key is not None:
            update_data["api_key"] = config_update.api_key
        if config_update.model is not None:
            update_data["model"] = config_update.model
        update_data["updated_at"] = "now()"

        # Update the record
        result = self.supabase.table(self.table_name).update(update_data).eq("user_id", user_id).execute()

        if not result.data:
            return None

        return result.data[0]

    async def delete_llm_config(self, user_id: str) -> bool:
        """
        Delete LLM configuration for a user.

        Args:
            user_id: ID of the user

        Returns:
            True if deleted, False if not found
        """
        result = self.supabase.table(self.table_name).delete().eq("user_id", user_id).execute()
        return len(result.data) > 0