from __future__ import annotations

from typing import Any, Dict, List, Optional
from loguru import logger
from supabase import create_client, Client
from ..core.config import settings
from ..models.invoice import ExtractedInvoice
from ..models.llm_config import LLMConfigCreate

# In-memory fallback store for dev mode when Supabase is unavailable
_fallback_extractions: Dict[str, Dict[str, Any]] = {}


class DatabaseService:
    """Service for Supabase database operations."""

    def __init__(self):
        self.supabase: Optional[Client] = None
        self.table_name = "extractions"
        self.llm_config_table = "llm_configs"
        try:
            self.supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
        except Exception as e:
            logger.warning(f"Failed to connect to Supabase: {e}")

    def _build_record(
        self,
        extraction_id: str,
        filename: str,
        user_id: str,
        data: ExtractedInvoice,
        status: str,
    ) -> Dict[str, Any]:
        return {
            "id": extraction_id,
            "filename": filename,
            "user_id": user_id,
            "status": status,
            "vendor_name": data.vendor_name,
            "invoice_number": data.invoice_number,
            "invoice_date": data.invoice_date,
            "due_date": data.due_date,
            "subtotal": data.subtotal,
            "tax": data.tax,
            "total_amount": data.total_amount,
            "currency": data.currency,
            "full_data": data.model_dump() if hasattr(data, 'model_dump') else data.dict(),
        }

    async def save_extraction(
        self,
        extraction_id: str,
        filename: str,
        user_id: str,
        data: ExtractedInvoice,
        status: str
    ) -> Dict[str, Any]:
        record = self._build_record(extraction_id, filename, user_id, data, status)

        if not self.supabase:
            logger.warning("Supabase unavailable, storing in-memory")
            _fallback_extractions[extraction_id] = record
            return record

        try:
            result = self.supabase.table(self.table_name).insert(record).execute()
        except Exception as e:
            logger.error(f"Supabase insert failed: {e}")
            _fallback_extractions[extraction_id] = record
            return record

        if not result.data:
            _fallback_extractions[extraction_id] = record
            return record

        return result.data[0]

    async def get_extraction_by_id(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        if not self.supabase:
            return _fallback_extractions.get(extraction_id)

        try:
            result = self.supabase.table(self.table_name).select("*").eq("id", extraction_id).execute()
        except Exception as e:
            logger.error(f"Supabase select failed: {e}")
            return _fallback_extractions.get(extraction_id)

        if not result.data:
            return _fallback_extractions.get(extraction_id)

        return result.data[0]

    async def update_extraction(self, extraction_id: str, data: ExtractedInvoice) -> Optional[Dict[str, Any]]:
        updated_fields = {
            "vendor_name": data.vendor_name,
            "invoice_number": data.invoice_number,
            "invoice_date": data.invoice_date,
            "due_date": data.due_date,
            "subtotal": data.subtotal,
            "tax": data.tax,
            "total_amount": data.total_amount,
            "currency": data.currency,
            "full_data": data.model_dump() if hasattr(data, 'model_dump') else data.dict(),
            "updated_at": "now()"
        }

        if not self.supabase:
            existing = _fallback_extractions.get(extraction_id)
            if existing:
                existing.update(updated_fields)
                return existing
            return None

        try:
            result = self.supabase.table(self.table_name).update(updated_fields).eq("id", extraction_id).execute()
        except Exception as e:
            logger.error(f"Supabase update failed: {e}")
            existing = _fallback_extractions.get(extraction_id)
            if existing:
                existing.update(updated_fields)
                return existing
            return None

        if not result.data:
            existing = _fallback_extractions.get(extraction_id)
            if existing:
                existing.update(updated_fields)
                return existing
            return None

        return result.data[0]

    async def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        if not self.supabase:
            return sorted(
                [r for r in _fallback_extractions.values() if r.get("user_id") == user_id],
                key=lambda r: r.get("created_at", ""),
                reverse=True,
            )

        try:
            result = self.supabase.table(self.table_name).select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        except Exception as e:
            logger.error(f"Supabase history query failed: {e}")
            return sorted(
                [r for r in _fallback_extractions.values() if r.get("user_id") == user_id],
                key=lambda r: r.get("created_at", ""),
                reverse=True,
            )

        return result.data if result.data else []

    async def save_llm_config(
        self,
        user_id: str,
        config: LLMConfigCreate
    ) -> Dict[str, Any]:
        existing = await self.get_llm_config(user_id)
        if existing:
            if not self.supabase:
                return existing

            try:
                result = self.supabase.table(self.llm_config_table).update({
                    "provider": config.provider,
                    "api_key": config.api_key,
                    "model": config.model,
                    "updated_at": "now()"
                }).eq("user_id", user_id).execute()
            except Exception as e:
                logger.error(f"Supabase LLM config update failed: {e}")
                return existing

            if not result.data:
                return existing

            return result.data[0]
        else:
            import uuid
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
                logger.warning("Supabase unavailable, returning in-memory LLM config record")
                return record

            try:
                result = self.supabase.table(self.llm_config_table).insert(record).execute()
            except Exception as e:
                logger.error(f"Supabase LLM config insert failed: {e}")
                return record

            if not result.data:
                return record

            return result.data[0]

    async def get_llm_config(self, user_id: str) -> Optional[Dict[str, Any]]:
        if not self.supabase:
            return None

        try:
            result = self.supabase.table(self.llm_config_table).select("*").eq("user_id", user_id).execute()
        except Exception as e:
            logger.error(f"Supabase LLM config query failed: {e}")
            return None

        if not result.data:
            return None

        return result.data[0]
