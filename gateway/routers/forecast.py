"""Forecast endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_app_config, get_current_user
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import AccessLevel, UserContext

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/daily")
async def get_daily_forecast(
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> dict[str, Any]:
    """
    Get daily forecast.

    Available to all tiers.

    Args:
        current_user: Authenticated user context.

    Returns:
        dict: Daily forecast data.

    Raises:
        HTTPException: 401 if not authenticated, 500 if calculation fails.
    """
    try:
        # TODO: Call packages.context.src daily_forecast function
        # Pass user's birth details and current date
        raise NotImplementedError("Forecast calculation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate daily forecast for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate forecast",
        ) from e


@router.get("/weekly")
async def get_weekly_forecast(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get weekly forecast.

    Available to pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Weekly forecast data (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "forecast_weekly", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock weekly forecasts"},
                access,
                "Upgrade to Pro to unlock weekly forecasts",
            ).dict()

        # TODO: Call packages.context.src weekly_forecast function
        raise NotImplementedError("Forecast calculation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate weekly forecast for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate forecast",
        ) from e


@router.get("/monthly")
async def get_monthly_forecast(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get monthly forecast.

    Available to pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Monthly forecast data (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "forecast_monthly", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock monthly forecasts"},
                access,
                "Upgrade to Pro to unlock monthly forecasts",
            ).dict()

        # TODO: Call packages.context.src monthly_forecast function
        raise NotImplementedError("Forecast calculation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate monthly forecast for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate forecast",
        ) from e


@router.get("/yearly")
async def get_yearly_forecast(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get yearly forecast.

    Available to premium tier only.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Yearly forecast data (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "forecast_yearly", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Premium only feature"},
                access,
                "Upgrade to Premium to unlock yearly forecasts",
            ).dict()

        # TODO: Call packages.context.src yearly_forecast function
        raise NotImplementedError("Forecast calculation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate yearly forecast for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate forecast",
        ) from e
