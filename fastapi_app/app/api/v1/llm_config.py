from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_app.app.services.llm_config_service import LLMConfigService
from fastapi_app.app.models.llm_config import LLMConfigCreate, LLMConfigUpdate

router = APIRouter()
security = HTTPBearer(auto_error=False)


from typing import Optional

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Return a user ID.

    In development mode, bypass authentication and return a static ID.
    Missing credentials (auto_error=False) also return the dev ID.
    """
    return "dev-user-id"



@router.post("/llm/config", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_llm_config(
    config: LLMConfigCreate,
    llm_config_service: LLMConfigService = Depends(),
    current_user: str = Depends(get_current_user)
) -> dict:
    """
    Create LLM configuration for the current user.

    Args:
        config: LLM configuration to create
        llm_config_service: Service for LLM configuration operations
        current_user: ID of the authenticated user

    Returns:
        Created LLM configuration record
    """
    try:
        # Check if config already exists for this user
        existing_config = await llm_config_service.get_llm_config_by_user_id(current_user)
        if existing_config:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="LLM configuration already exists for this user. Use PUT to update."
            )

        # Create new configuration
        result = await llm_config_service.create_llm_config(current_user, config)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create LLM configuration: {str(e)}"
        )


@router.get("/llm/config", response_model=dict)
async def get_llm_config(
    llm_config_service: LLMConfigService = Depends(),
    current_user: str = Depends(get_current_user)
) -> dict:
    """
    Get LLM configuration for the current user.

    Args:
        llm_config_service: Service for LLM configuration operations
        current_user: ID of the authenticated user

    Returns:
        LLM configuration record for the user
    """
    try:
        config = await llm_config_service.get_llm_config_by_user_id(current_user)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user"
            )
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve LLM configuration: {str(e)}"
        )


@router.put("/llm/config", response_model=dict)
async def update_llm_config(
    config_update: LLMConfigUpdate,
    llm_config_service: LLMConfigService = Depends(),
    current_user: str = Depends(get_current_user)
) -> dict:
    """
    Update LLM configuration for the current user.

    Args:
        config_update: LLM configuration update
        llm_config_service: Service for LLM configuration operations
        current_user: ID of the authenticated user

    Returns:
        Updated LLM configuration record
    """
    try:
        # Check if config exists
        existing_config = await llm_config_service.get_llm_config_by_user_id(current_user)
        if not existing_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user. Use POST to create."
            )

        # Update configuration
        result = await llm_config_service.update_llm_config(current_user, config_update)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update LLM configuration: {str(e)}"
        )


@router.delete("/llm/config", response_model=dict)
async def delete_llm_config(
    llm_config_service: LLMConfigService = Depends(),
    current_user: str = Depends(get_current_user)
) -> dict:
    """
    Delete LLM configuration for the current user.

    Args:
        llm_config_service: Service for LLM configuration operations
        current_user: ID of the authenticated user

    Returns:
        Confirmation message
    """
    try:
        # Check if config exists
        existing_config = await llm_config_service.get_llm_config_by_user_id(current_user)
        if not existing_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user"
            )

        # Delete configuration
        deleted = await llm_config_service.delete_llm_config(current_user)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found for this user"
            )
        return {"message": "LLM configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete LLM configuration: {str(e)}"
        )