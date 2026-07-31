from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_app.app.services.db import DatabaseService
from fastapi_app.app.models.llm_config import (
    LLMConfigCreate,
    LLMConfigResponse,
    VerifyLLMRequest,
    VerifyLLMResponse
)
from fastapi_app.app.services.llm_verification_service import verify_llm_config
from fastapi_app.app.utils.auth import get_current_user

router = APIRouter()


def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 4:
        return "****"
    return f"sk-...{api_key[-4:]}"


@router.post("/llm", response_model=LLMConfigResponse, status_code=status.HTTP_201_CREATED)
async def save_llm_config(
    config: LLMConfigCreate,
    db_service: DatabaseService = Depends(),
    current_user: str = Depends(get_current_user)
) -> LLMConfigResponse:
    """Save LLM configuration for the current user."""
    try:
        result = await db_service.save_llm_config(current_user, config)
        return LLMConfigResponse(
            provider=result["provider"],
            model=result["model"],
            is_valid=True,
            masked_api_key=mask_api_key(result["api_key"]),
            user_id=current_user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save LLM configuration: {str(e)}"
        )


@router.get("/llm", response_model=LLMConfigResponse)
async def get_llm_config(
    db_service: DatabaseService = Depends(),
    current_user: str = Depends(get_current_user)
) -> LLMConfigResponse:
    """Get LLM configuration for the current user."""
    try:
        config = await db_service.get_llm_config(current_user)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user"
            )
        return LLMConfigResponse(
            provider=config["provider"],
            model=config["model"],
            is_valid=True,
            masked_api_key=mask_api_key(config["api_key"]),
            user_id=current_user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve LLM configuration: {str(e)}"
        )


@router.post("/llm/verify", response_model=VerifyLLMResponse)
async def verify_llm(
    request: VerifyLLMRequest
) -> VerifyLLMResponse:
    """Verify LLM configuration."""
    return await verify_llm_config(request)
