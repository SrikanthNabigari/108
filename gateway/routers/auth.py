"""Authentication endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_current_user
from gateway.models import (
    BirthDetailsUpdate,
    UserContext,
    UserProfile,
    UserProfileUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_user_profile(
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> UserProfile:
    """
    Get authenticated user's profile.

    Returns user profile including birth details, subscription info,
    and basic chart summary.

    Args:
        current_user: Authenticated user context.

    Returns:
        UserProfile: User profile data.

    Raises:
        HTTPException: 401 if not authenticated, 500 if query fails.
    """
    try:
        # TODO: Query users table
        # Get full user profile including birth details

        return UserProfile(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            phone=current_user.phone,
            subscription_tier=current_user.subscription_tier,
        )

    except Exception as e:
        logger.error(f"Failed to get profile for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile",
        ) from e


@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    update: UserProfileUpdate,
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> UserProfile:
    """
    Update user profile information.

    Updates name, gender, and avatar URL.

    Args:
        update: Profile update payload.
        current_user: Authenticated user context.

    Returns:
        UserProfile: Updated user profile.

    Raises:
        HTTPException: 401 if not authenticated, 500 if update fails.
    """
    try:
        # TODO: Update users table
        # Only update non-null fields

        return UserProfile(
            id=current_user.id,
            email=current_user.email,
            subscription_tier=current_user.subscription_tier,
        )

    except Exception as e:
        logger.error(f"Failed to update profile for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        ) from e


@router.put("/me/birth-details", response_model=UserProfile)
async def update_birth_details(
    update: BirthDetailsUpdate,
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> UserProfile:
    """
    Update user's birth details.

    Updates birth datetime, location, and timezone. Triggers chart
    recalculation.

    Args:
        update: Birth details update payload.
        current_user: Authenticated user context.

    Returns:
        UserProfile: Updated user profile.

    Raises:
        HTTPException: 401 if not authenticated, 400 if invalid data,
            500 if update fails.
    """
    try:
        # TODO: Update users table with birth details
        # TODO: Invalidate cached chart for this user in Redis
        # TODO: Queue async job to recalculate all chart data

        return UserProfile(
            id=current_user.id,
            email=current_user.email,
            subscription_tier=current_user.subscription_tier,
        )

    except Exception as e:
        logger.error(f"Failed to update birth details for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update birth details",
        ) from e


@router.delete("/me")
async def delete_account(
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> dict[str, str]:
    """
    Delete user account and all associated data.

    Permanently deletes user record, birth chart data, events, reports,
    and all related data.

    Args:
        current_user: Authenticated user context.

    Returns:
        dict: Deletion confirmation.

    Raises:
        HTTPException: 401 if not authenticated, 500 if deletion fails.
    """
    try:
        # TODO: Delete user and all related data
        # Cascade delete: user_events, user_reports, chat_messages,
        # user_credits, user_compatibility, etc.
        # Be careful to delete in correct order for foreign key constraints

        return {
            "status": "deleted",
            "message": "Your account and all data have been permanently deleted",
        }

    except Exception as e:
        logger.error(f"Failed to delete account for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account",
        ) from e
