"""Chart endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_app_config, get_current_user
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import AccessLevel, UserContext

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary")
async def get_chart_summary(
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> dict[str, Any]:
    """
    Get basic birth chart summary.

    Available to all tiers. Returns basic chart information without
    full calculations.

    Args:
        current_user: Authenticated user context.

    Returns:
        dict: Basic chart summary.

    Raises:
        HTTPException: 401 if user is not authenticated, 500 if chart
            calculation fails.
    """
    try:
        # TODO: Call packages.cosmos.src functions to get chart summary
        # Import via: sys.path.insert(0, str(Path(__file__).parent.parent))
        # from packages.cosmos.src import calculate_chart_summary
        raise NotImplementedError("Chart calculation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate chart summary for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate chart",
        ) from e


@router.get("/full")
async def get_full_chart(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get full birth chart with all divisional charts.

    Free tier gets D1 only. Pro and premium get all divisional charts.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Full chart data (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "chart_divisional", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock full charts"},
                access,
                "Upgrade to Pro to unlock full charts",
            ).dict()

        # TODO: Call packages.cosmos.src to calculate full chart
        # If free tier and access=LOCKED, return only D1
        # If pro+ and access=FULL, return all divisional charts
        raise NotImplementedError("Chart calculation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate full chart for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate chart",
        ) from e


@router.get("/divisional/{division}")
async def get_divisional_chart(
    division: int,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get specific divisional chart.

    Divisional charts (D2, D3, D7, D9, D10, etc.) are gated by subscription.

    Args:
        division: Divisional chart number (2, 3, 7, 9, 10, 12, etc.).
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Divisional chart data (gated by subscription tier).

    Raises:
        HTTPException: 400 if invalid division, 401 if not authenticated,
            403 if locked for tier, 500 if calculation fails.
    """
    try:
        # Validate division number
        valid_divisions = [2, 3, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
        if division not in valid_divisions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid division. Valid values: {valid_divisions}",
            )

        access = await check_feature_access(
            "chart_divisional", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock divisional charts"},
                access,
                "Upgrade to Pro to unlock divisional charts",
            ).dict()

        # TODO: Call packages.cosmos.src divisional_chart function
        # Pass user's birth chart and division number
        raise NotImplementedError("Chart calculation integration required")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate D{division} chart for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate divisional chart",
        ) from e
