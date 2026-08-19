from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.core.database import get_db_service
from backend.app.services.db import DatabaseService
from backend.app.schemas.llm_config import (
    LLMConfigCreate,
    LLMConfigResponse,
    VerifyLLMRequest,
    VerifyLLMResponse,
)
from backend.app.services.llm_verification_service import verify_llm_config
from backend.app.utils.auth import get_current_user

router = APIRouter()


def get_user_id(current_user: dict) -> str:
    """Extract user_id from current_user dict."""
    return current_user["sub"]


def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 4:
        return "****"
    return f"sk-...{api_key[-4:]}"


@router.post("/llm", response_model=LLMConfigResponse, status_code=status.HTTP_201_CREATED)
async def save_llm_config(
    config: LLMConfigCreate,
    db_service: DatabaseService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user),
) -> LLMConfigResponse:
    """Save LLM configuration for the current user."""
    try:
        user_id = get_user_id(current_user)
        result = await db_service.save_llm_config(user_id, config)
        return LLMConfigResponse(
            provider=result["provider"],
            model=result["model"],
            is_valid=True,
            masked_api_key=mask_api_key(result["api_key"]),
            user_id=user_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save LLM configuration: {str(e)}",
        )


@router.get("/llm", response_model=LLMConfigResponse)
async def get_llm_config(
    db_service: DatabaseService = Depends(get_db_service),
    current_user: dict = Depends(get_current_user),
) -> LLMConfigResponse:
    """Get LLM configuration for the current user."""
    try:
        user_id = get_user_id(current_user)
        config = await db_service.get_llm_config(user_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user",
            )
        return LLMConfigResponse(
            provider=config["provider"],
            model=config["model"],
            is_valid=True,
            masked_api_key=mask_api_key(config["api_key"]),
            user_id=user_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve LLM configuration: {str(e)}",
        )


@router.post("/llm/verify", response_model=VerifyLLMResponse)
async def verify_llm(
    request: VerifyLLMRequest,
) -> VerifyLLMResponse:
    """Verify LLM configuration."""
    return await verify_llm_config(request)