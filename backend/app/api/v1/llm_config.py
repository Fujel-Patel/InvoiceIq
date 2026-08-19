from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.services.llm_config_service import LLMConfigService
from backend.app.services.llm_verification_service import verify_llm_config
from backend.app.schemas.llm_config import (
    LLMConfigCreate,
    LLMConfigUpdate,
    LLMConfigResponse,
    VerifyLLMRequest,
    VerifyLLMResponse,
)
from backend.app.utils.auth import get_current_user
from typing import Optional

router = APIRouter()


def get_user_id(current_user: dict) -> str:
    """Extract user_id from current_user dict."""
    return current_user["sub"]


def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 4:
        return "****"
    return f"sk-...{api_key[-4:]}"


@router.post("/llm/config", response_model=LLMConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_llm_config(
    config: LLMConfigCreate,
    llm_config_service: LLMConfigService = Depends(),
    current_user: dict = Depends(get_current_user),
) -> LLMConfigResponse:
    """Create LLM configuration for the current user."""
    try:
        user_id = get_user_id(current_user)
        existing_config = await llm_config_service.get_llm_config_by_user_id(user_id)
        if existing_config:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="LLM configuration already exists for this user. Use PUT to update.",
            )

        result = await llm_config_service.create_llm_config(user_id, config)
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
            detail=f"Failed to create LLM configuration: {str(e)}",
        )


@router.get("/llm/config")
async def get_llm_config(
    llm_config_service: LLMConfigService = Depends(),
    current_user: dict = Depends(get_current_user),
) -> Optional[LLMConfigResponse]:
    """Get LLM configuration for the current user. Returns null if not configured."""
    try:
        user_id = get_user_id(current_user)
        config = await llm_config_service.get_llm_config_by_user_id(user_id)
        if not config:
            return None
        return LLMConfigResponse(
            provider=config["provider"],
            model=config["model"],
            is_valid=True,
            masked_api_key=mask_api_key(config["api_key"]),
            user_id=user_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve LLM configuration: {str(e)}",
        )


@router.put("/llm/config", response_model=LLMConfigResponse)
async def update_llm_config(
    config_update: LLMConfigUpdate,
    llm_config_service: LLMConfigService = Depends(),
    current_user: dict = Depends(get_current_user),
) -> LLMConfigResponse:
    """Update LLM configuration for the current user."""
    try:
        user_id = get_user_id(current_user)
        existing_config = await llm_config_service.get_llm_config_by_user_id(user_id)
        if not existing_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user. Use POST to create.",
            )

        result = await llm_config_service.update_llm_config(user_id, config_update)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update LLM configuration",
            )
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
            detail=f"Failed to update LLM configuration: {str(e)}",
        )


@router.delete("/llm/config", response_model=dict[str, str])
async def delete_llm_config(
    llm_config_service: LLMConfigService = Depends(),
    current_user: dict = Depends(get_current_user),
) -> dict[str, str]:
    """Delete LLM configuration for the current user."""
    try:
        user_id = get_user_id(current_user)
        existing_config = await llm_config_service.get_llm_config_by_user_id(user_id)
        if not existing_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user",
            )

        deleted = await llm_config_service.delete_llm_config(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user",
            )
        return {"message": "LLM configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete LLM configuration: {str(e)}",
        )


@router.post("/llm/verify", response_model=VerifyLLMResponse)
async def verify_llm(
    request: VerifyLLMRequest,
) -> VerifyLLMResponse:
    """Verify LLM configuration."""
    return await verify_llm_config(request)