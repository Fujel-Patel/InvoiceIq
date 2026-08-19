from __future__ import annotations
import anthropic
import openai
from google import genai
from groq import Groq
from fastapi import HTTPException
from backend.app.schemas.llm_config import LLMProvider, VerifyLLMRequest, VerifyLLMResponse

async def verify_llm_config(request: VerifyLLMRequest) -> VerifyLLMResponse:
    try:
        if request.provider == LLMProvider.ANTHROPIC:
            client = anthropic.AsyncAnthropic(api_key=request.api_key)
            await client.messages.create(
                model=request.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
        elif request.provider == LLMProvider.OPENAI:
            client = openai.AsyncOpenAI(api_key=request.api_key)
            await client.chat.completions.create(
                model=request.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
        elif request.provider == LLMProvider.GOOGLE:
            # Using google-genai 2.x API (synchronous)
            client = genai.Client(api_key=request.api_key)
            client.models.generate_content(
                model=request.model,
                contents="Hi"
            )
        elif request.provider == LLMProvider.GROQ:
            client = Groq(api_key=request.api_key)
            client.chat.completions.create(
                model=request.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")

        return VerifyLLMResponse(is_valid=True, message="Configuration verified", provider=request.provider)
    except Exception as e:
        return VerifyLLMResponse(is_valid=False, message=str(e), provider=request.provider)