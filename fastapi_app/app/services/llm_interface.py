from __future__ import annotations

import json
import base64
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    async def extract_invoice_data(self, base64_file: str, media_type: str) -> Dict[str, Any]:
        """
        Extract invoice data from an image or PDF using the LLM API.

        Args:
            base64_file: Base64 encoded file content
            media_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')

        Returns:
            Dictionary with extracted invoice data
        """
        pass

    def _extract_json_from_text(self, text: str) -> str:
        """
        Extract JSON from text that might contain markdown or other formatting.

        Args:
            text: Raw text from LLM response

        Returns:
            Clean JSON string
        """
        # Look for JSON block in markdown
        if "```json" in text:
            # Extract JSON from markdown code block
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                return text[start:end].strip()

        # Look for any JSON-like content (starts with { and ends with })
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != 0 and end > start:
            return text[start:end]

        # If we can't find JSON, return the text as-is (will cause JSON parse error)
        return text


class AnthropicLLMService(BaseLLMService):
    """Anthropic Claude LLM service implementation."""

    def __init__(self, api_key: str, model: str = "claude-opus-4-5-20251001"):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Anthropic LLM service with model: {self.model}")

    async def extract_invoice_data(self, base64_file: str, media_type: str) -> Dict[str, Any]:
        """
        Extract invoice data from an image or PDF using Claude Vision API.

        Args:
            base64_file: Base64 encoded file content
            media_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')

        Returns:
            Dictionary with extracted invoice data
        """
        try:
            # Call Claude Vision API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_file,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Extract all invoice data from this image and return ONLY a valid JSON object with these fields: vendor_name, invoice_number, invoice_date, due_date, line_items (array with description, quantity, unit_price, total), subtotal, tax, total_amount, currency. If a field is not found, set it to null.",
                            },
                        ],
                    }
                ],
            )

            # Extract text from response
            text_content = response.content[0].text

            # Try to parse JSON from the response
            # Claude might wrap JSON in markdown or add extra text, so we need to extract it cleanly
            json_str = self._extract_json_from_text(text_content)

            # Parse the JSON
            extracted_data = json.loads(json_str)

            return extracted_data

        except Exception as e:
            logger.error(f"Failed to extract invoice data with Anthropic: {str(e)}")
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


class OpenAILLMService(BaseLLMService):
    """OpenAI LLM service implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI LLM service with model: {self.model}")

    async def extract_invoice_data(self, base64_file: str, media_type: str) -> Dict[str, Any]:
        """
        Extract invoice data from an image or PDF using OpenAI Vision API.

        Args:
            base64_file: Base64 encoded file content
            media_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')

        Returns:
            Dictionary with extracted invoice data
        """
        try:
            # Call OpenAI Vision API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all invoice data from this image and return ONLY a valid JSON object with these fields: vendor_name, invoice_number, invoice_date, due_date, line_items (array with description, quantity, unit_price, total), subtotal, tax, total_amount, currency. If a field is not found, set it to null.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{base64_file}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )

            # Extract text from response
            text_content = response.choices[0].message.content

            # Try to parse JSON from the response
            json_str = self._extract_json_from_text(text_content)

            # Parse the JSON
            extracted_data = json.loads(json_str)

            return extracted_data

        except Exception as e:
            logger.error(f"Failed to extract invoice data with OpenAI: {str(e)}")
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


class GeminiLLMService(BaseLLMService):
    """Google Gemini LLM service implementation."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro-latest"):
        import google.generativeai as genai
        self.client = genai.GenerativeModel(model)
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Gemini LLM service with model: {self.model}")

    async def extract_invoice_data(self, base64_file: str, media_type: str) -> Dict[str, Any]:
        """
        Extract invoice data from an image or PDF using Gemini Vision API.

        Args:
            base64_file: Base64 encoded file content
            media_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')

        Returns:
            Dictionary with extracted invoice data
        """
        try:
            import google.generativeai as genai
            from PIL import Image
            import io

            # Configure the API key
            genai.configure(api_key=self.api_key)

            # Convert base64 to image
            image_data = base64.b64decode(base64_file)
            image = Image.open(io.BytesIO(image_data))

            # Call Gemini Vision API
            prompt = """
            Extract all invoice data from this image and return ONLY a valid JSON object with these fields:
            vendor_name, invoice_number, invoice_date, due_date, line_items (array with description, quantity, unit_price, total),
            subtotal, tax, total_amount, currency. If a field is not found, set it to null.
            """

            response = self.client.generate_content([prompt, image])
            text_content = response.text

            # Try to parse JSON from the response
            json_str = self._extract_json_from_text(text_content)

            # Parse the JSON
            extracted_data = json.loads(json_str)

            return extracted_data

        except Exception as e:
            logger.error(f"Failed to extract invoice data with Gemini: {str(e)}")
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


class GroqLLMService(BaseLLMService):
    """Groq LLM service implementation."""

    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        from groq import AsyncGroq
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Groq LLM service with model: {self.model}")

    async def extract_invoice_data(self, base64_file: str, media_type: str) -> Dict[str, Any]:
        """
        Extract invoice data from an image or PDF using Groq API.
        Note: Groq doesn't support vision directly, so we'll need to handle this appropriately.
        For now, we'll return an error indicating vision is not supported.

        Args:
            base64_file: Base64 encoded file content
            media_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')

        Returns:
            Dictionary with extracted invoice data or error
        """
        try:
            # Groq doesn't currently support vision models in the same way as OpenAI/Anthropic
            # This would require a different approach or using a vision-capable model through Groq
            # For now, returning an error as Groq vision support is limited
            raise NotImplementedError("Groq vision support is not currently implemented. Please use a provider with vision capabilities like Anthropic, OpenAI, or Gemini.")

        except Exception as e:
            logger.error(f"Failed to extract invoice data with Groq: {str(e)}")
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


class OpenRouterLLMService(BaseLLMService):
    """OpenRouter LLM service implementation."""

    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        from openai import AsyncOpenAI
        # OpenRouter uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
        logger.info(f"Initialized OpenRouter LLM service with model: {self.model}")

    async def extract_invoice_data(self, base64_file: str, media_type: str) -> Dict[str, Any]:
        """
        Extract invoice data from an image or PDF using OpenRouter API.

        Args:
            base64_file: Base64 encoded file content
            media_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')

        Returns:
            Dictionary with extracted invoice data
        """
        try:
            # Call OpenRouter API (OpenAI-compatible)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all invoice data from this image and return ONLY a valid JSON object with these fields: vendor_name, invoice_number, invoice_date, due_date, line_items (array with description, quantity, unit_price, total), subtotal, tax, total_amount, currency. If a field is not found, set it to null.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{base64_file}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )

            # Extract text from response
            text_content = response.choices[0].message.content

            # Try to parse JSON from the response
            json_str = self._extract_json_from_text(text_content)

            # Parse the JSON
            extracted_data = json.loads(json_str)

            return extracted_data

        except Exception as e:
            logger.error(f"Failed to extract invoice data with OpenRouter: {str(e)}")
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


# Factory function to create LLM service instances
def create_llm_service(provider: str, api_key: str, model: Optional[str] = None) -> BaseLLMService:
    """
    Factory function to create LLM service instances based on provider.

    Args:
        provider: LLM provider name ('anthropic', 'openai', 'gemini', 'groq', 'openrouter')
        api_key: API key for the provider
        model: Optional model name (uses provider default if not specified)

    Returns:
        BaseLLMService: Instance of the requested LLM service

    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.lower()

    if provider == "anthropic":
        return AnthropicLLMService(api_key, model or "claude-opus-4-5-20251001")
    elif provider == "openai":
        return OpenAILLMService(api_key, model or "gpt-4o")
    elif provider == "gemini":
        return GeminiLLMService(api_key, model or "gemini-1.5-pro-latest")
    elif provider == "groq":
        return GroqLLMService(api_key, model or "mixtral-8x7b-32768")
    elif provider == "openrouter":
        return OpenRouterLLMService(api_key, model or "anthropic/claude-3.5-sonnet")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers are: anthropic, openai, gemini, groq, openrouter")