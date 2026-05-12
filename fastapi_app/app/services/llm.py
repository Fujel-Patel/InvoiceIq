from __future__ import annotations

import logging
from typing import Dict, Any
from ..services.llm_interface import create_llm_service
from ..core.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Wrapper service for LLM provider selection.
    This maintains backward compatibility while allowing flexible provider selection.
    """

    def __init__(self):
        # Determine which LLM provider to use based on configuration
        # Priority: explicit setting > default from config
        provider = getattr(settings, 'LLM_PROVIDER', None) or settings.DEFAULT_LLM_PROVIDER

        # Get API key based on provider
        api_key = self._get_api_key_for_provider(provider)
        if not api_key:
            logger.warning(f"No API key found for provider: {provider}")
            # Fallback to anthropic if available
            if settings.ANTHROPIC_API_KEY:
                provider = "anthropic"
                api_key = settings.ANTHROPIC_API_KEY
            else:
                raise ValueError(f"No API key configured for LLM provider: {provider}")

        # Get model based on provider
        model = self._get_model_for_provider(provider)

        # Create the LLM service instance
        self.llm_service = create_llm_service(provider, api_key, model)
        logger.info(f"Initialized LLM service with provider: {provider}, model: {model}")

    def _get_api_key_for_provider(self, provider: str) -> str:
        """Get API key for the specified provider."""
        provider = provider.lower()
        if provider == "anthropic":
            return settings.ANTHROPIC_API_KEY
        elif provider == "openai":
            return settings.OPENAI_API_KEY
        elif provider == "gemini":
            return settings.GEMINI_API_KEY
        elif provider == "groq":
            return settings.GROQ_API_KEY
        elif provider == "openrouter":
            return settings.OPENROUTER_API_KEY
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _get_model_for_provider(self, provider: str) -> str:
        """Get model for the specified provider."""
        provider = provider.lower()
        if provider == "anthropic":
            return settings.CLAUDE_MODEL
        elif provider == "openai":
            return settings.OPENAI_MODEL
        elif provider == "gemini":
            return settings.GEMINI_MODEL
        elif provider == "groq":
            return settings.GROQ_MODEL
        elif provider == "openrouter":
            return settings.OPENROUTER_MODEL
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def extract_invoice_data(self, base64_file: str, media_type: str) -> Dict[str, Any]:
        """
        Extract invoice data from an image or PDF using the configured LLM provider.

        Args:
            base64_file: Base64 encoded file content
            media_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')

        Returns:
            Dictionary with extracted invoice data
        """
        try:
            return await self.llm_service.extract_invoice_data(base64_file, media_type)
        except Exception as e:
            logger.error(f"Failed to extract invoice data: {str(e)}")
            # Return a dict with error information
            return {
                "error": f"Failed to extract invoice data: {str(e)}",
                "vendor_name": None,
                "invoice_number": None,
                "invoice_date": None,
                "due_date": None,
                "line_items": [],
                "subtotal": None,
                "tax": None,
                "total_amount": None,
                "currency": None
            }