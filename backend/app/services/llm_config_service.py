from __future__ import annotations

import uuid
from typing import Any, Dict, Optional
from loguru import logger
from supabase import create_client, Client
from ..core.config import settings
from ..models.llm_config import LLMConfigCreate, LLMConfigUpdate

# In-memory fallback store for dev mode when Supabase is unavailable
_fallback_llm_configs: Dict[str, Dict[str, Any]] = {}


class LLMConfigService:
    """Service for managing LLM configuration in the database."""

    def __init__(self):
        self.supabase: Optional[Client] = None
        self.table_name = "llm_configs"
        if settings.IS_DEVELOPMENT:
            logger.info("[dev-auth] LLMConfigService using local store (no Supabase)")
            return
        try:
            self.supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
        except Exception as e:
            logger.warning(f"Failed to connect to Supabase: {e}")

    async def create_llm_config(
        self,
        user_id: str,
        config: LLMConfigCreate
    ) -> Dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "provider": config.provider,
            "api_key": config.api_key,
            "model": config.model,
            "created_at": "now()",
            "updated_at": "now()"
        }

        if not self.supabase:
            _fallback_llm_configs[user_id] = record
            return record

        try:
            result = self.supabase.table(self.table_name).insert(record).execute()
        except Exception as e:
            logger.error(f"Supabase LLM config create failed: {e}")
            _fallback_llm_configs[user_id] = record
            return record

        if not result.data:
            _fallback_llm_configs[user_id] = record
            return record

        _fallback_llm_configs[user_id] = result.data[0]
        return result.data[0]

    async def get_llm_config_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not self.supabase:
            return _fallback_llm_configs.get(user_id)

        try:
            result = self.supabase.table(self.table_name).select("*").eq("user_id", user_id).execute()
        except Exception as e:
            logger.error(f"Supabase LLM config query failed: {e}")
            return _fallback_llm_configs.get(user_id)

        if not result.data:
            return _fallback_llm_configs.get(user_id)

        return result.data[0]

    async def update_llm_config(
        self,
        user_id: str,
        config_update: LLMConfigUpdate
    ) -> Optional[Dict[str, Any]]:
        existing = await self.get_llm_config_by_user_id(user_id)
        if not existing:
            return None

        update_data: Dict[str, Any] = {}
        if config_update.provider is not None:
            update_data["provider"] = config_update.provider
        if config_update.api_key is not None:
            update_data["api_key"] = config_update.api_key
        if config_update.model is not None:
            update_data["model"] = config_update.model
        update_data["updated_at"] = "now()"

        updated = {**existing, **update_data}

        if not self.supabase:
            _fallback_llm_configs[user_id] = updated
            return updated

        try:
            result = self.supabase.table(self.table_name).update(update_data).eq("user_id", user_id).execute()
        except Exception as e:
            logger.error(f"Supabase LLM config update failed: {e}")
            _fallback_llm_configs[user_id] = updated
            return updated

        if not result.data:
            _fallback_llm_configs[user_id] = updated
            return updated

        _fallback_llm_configs[user_id] = result.data[0]
        return result.data[0]

    async def delete_llm_config(self, user_id: str) -> bool:
        if not self.supabase:
            if user_id in _fallback_llm_configs:
                del _fallback_llm_configs[user_id]
                return True
            return False

        try:
            result = self.supabase.table(self.table_name).delete().eq("user_id", user_id).execute()
        except Exception as e:
            logger.error(f"Supabase LLM config delete failed: {e}")
            if user_id in _fallback_llm_configs:
                del _fallback_llm_configs[user_id]
                return True
            return False

        _fallback_llm_configs.pop(user_id, None)
        return len(result.data) > 0
