from __future__ import annotations

import anthropic
from typing import Any, Dict, Optional

from loguru import logger

from backend.app.core.config import settings
from .llm_config_service import LLMConfigService
from .llm_interface import create_llm_service


class LLMService:
    def __init__(self) -> None:
        self.llm_config_service = LLMConfigService()
        self.default_llm_provider = settings.DEFAULT_LLM_PROVIDER
        self.default_llm_model = settings.DEFAULT_LLM_MODEL

    def _get_api_key_for_provider(self, provider: str) -> Optional[str]:
        provider = provider.lower()
        key_mapping = {
            "anthropic": settings.ANTHROPIC_API_KEY,
            "openai": settings.OPENAI_API_KEY,
            "google": settings.GEMINI_API_KEY,
            "groq": settings.GROQ_API_KEY,
            "openrouter": settings.OPENROUTER_API_KEY,
        }
        return key_mapping.get(provider)

    async def get_llm_config(self, user_id: str) -> Dict[str, Any]:
        config = await self.llm_config_service.get_llm_config_by_user_id(user_id)
        if config:
            return {
                "provider": config["provider"],
                "model": config["model"],
                "api_key": config["api_key"],
            }
        else:
            api_key = self._get_api_key_for_provider(self.default_llm_provider)
            return {
                "provider": self.default_llm_provider,
                "model": self.default_llm_model,
                "api_key": api_key,
            }

    async def generate_text(self, prompt: str, user_id: str) -> str:
        config = await self.get_llm_config(user_id)
        provider = config["provider"]
        model = config["model"]
        api_key = config.get("api_key")

        if not api_key:
            raise ValueError(f"No API key configured for provider '{provider}'")

        if provider == "anthropic":
            client = anthropic.AsyncAnthropic(api_key=api_key)
            message = await client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        elif provider == "openai":
            import openai
            client = openai.AsyncOpenAI(api_key=api_key)
            completion = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        elif provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            return response.text
        elif provider == "groq":
            from groq import Groq
            client = Groq(api_key=api_key)
            chat_completion = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def extract_invoice_data(
        self, base64_file: str, media_type: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Extract invoice data from an image or PDF using the LLM Vision API.

        Args:
            base64_file: Base64 encoded file content
            media_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')
            user_id: User identifier to fetch provider config

        Returns:
            Dictionary with extracted invoice data
        """
        config = await self.get_llm_config(user_id)
        provider = config["provider"]
        model = config.get("model")
        api_key = config.get("api_key")

        if api_key is None or (isinstance(api_key, str) and api_key.strip().lower() in ("", "dummy", "your-api-key-here")):
            error_msg = f"No API key configured for provider '{provider}'. Add an API key in Settings."
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            llm_service = create_llm_service(provider, api_key, model)
            extracted_data = await llm_service.extract_invoice_data(base64_file, media_type)
            return extracted_data
        except Exception as e:
            logger.error(f"Failed to extract invoice data: {str(e)}")
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
                "currency": None,
            }


# Backward compatibility alias
ClaudeService = LLMService
