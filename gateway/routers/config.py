"""Configuration endpoint for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_app_config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def get_config(
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get application configuration.

    Transforms feature_gates from internal format to mobile-friendly format:
    Internal: {"feature": {"free": "full", "pro": "full"}}
    Mobile:   {"free": {"feature": true}, "pro": {"feature": true}}
    """
    try:
        # Transform feature gates: pivot from feature→tier→access to tier→feature→bool
        raw_gates = config.get("feature_gates", {})
        tiers = ["free", "pro", "premium"]
        transformed_gates: dict[str, dict[str, bool]] = {t: {} for t in tiers}

        for feature, tier_map in raw_gates.items():
            for tier in tiers:
                access = tier_map.get(tier, "locked")
                transformed_gates[tier][feature] = access != "locked"

        return {
            "featureGates": transformed_gates,
            "chatLimits": config.get("chat_limits", {}),
            "subscriptionTiers": config.get("subscription_tiers", {}),
            "creditPacks": config.get("credit_packs", []),
            "reportPrices": config.get("report_prices", {}),
        }
    except Exception as e:
        logger.error(f"Failed to retrieve config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve configuration",
        ) from None
