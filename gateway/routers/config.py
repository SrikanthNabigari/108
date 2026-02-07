"""Configuration endpoint for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_app_config
from gateway.models import ConfigResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=ConfigResponse)
async def get_config(
    config: Annotated[dict, Depends(get_app_config)],
) -> ConfigResponse:
    """
    Get application configuration.

    Returns all feature gates, chat limits, subscription tiers, credit packs,
    and report prices from cached app_config.

    Args:
        config: Application configuration from cache.

    Returns:
        ConfigResponse: Application configuration.

    Raises:
        HTTPException: 500 if configuration is unavailable.
    """
    try:
        return ConfigResponse(
            feature_gates=config.get("feature_gates", {}),
            chat_limits=config.get("chat_limits", {}),
            subscription_tiers=config.get("subscription_tiers", {}),
            credit_packs=config.get("credit_packs", []),
            report_prices=config.get("report_prices", {}),
        )
    except Exception as e:
        logger.error(f"Failed to retrieve config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve configuration",
        ) from None
