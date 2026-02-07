"""Muhurta (auspicious timing) endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_app_config, get_current_user
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import (
    AccessLevel,
    MuhurtaCheckRequest,
    MuhurtaFindRequest,
    UserContext,
)
from packages.context.src import evaluate_muhurta, find_next_good_muhurta

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/check")
async def check_muhurta_quality(
    request: MuhurtaCheckRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Check muhurta (auspicious timing) quality for a datetime.

    Gated feature - pro and premium tiers.

    Args:
        request: Muhurta check request with datetime and activity type.
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Muhurta quality score and analysis (gated by tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access("muhurta_check", current_user.subscription_tier, config)

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock muhurta analysis"},
                access,
                "Upgrade to Pro to unlock muhurta analysis",
            ).dict()

        # Evaluate muhurta quality
        muhurta_result = evaluate_muhurta(
            request.datetime.isoformat(),
            request.activity,
            request.latitude,
            request.longitude,
        )

        return {
            **muhurta_result,
            "access": "full",
        }

    except AccessLevel.LOCKED as e:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from None
    except Exception as e:
        logger.error(f"Failed to check muhurta for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check muhurta",
        ) from None


@router.post("/find")
async def find_good_muhurta(
    request: MuhurtaFindRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Find good muhurta dates for an activity.

    Gated feature - pro and premium tiers.

    Args:
        request: Find muhurta request with date range and activity type.
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: List of recommended muhurta dates (gated by tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access("muhurta_find", current_user.subscription_tier, config)

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock muhurta finder"},
                access,
                "Upgrade to Pro to unlock muhurta finder",
            ).dict()

        # Find good muhurta dates
        muhurta_result = find_next_good_muhurta(
            request.start_date,
            request.end_date,
            request.activity,
            request.count,
        )

        return {
            **muhurta_result,
            "access": "full",
        }

    except AccessLevel.LOCKED as e:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from None
    except Exception as e:
        logger.error(f"Failed to find muhurta for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find muhurta dates",
        ) from None
