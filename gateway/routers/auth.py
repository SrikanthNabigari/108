"""Authentication endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_current_user, get_db
from gateway.models import (
    BirthDetailsUpdate,
    UserContext,
    UserProfile,
    UserProfileUpdate,
)
from packages.cosmos.src import get_all_planets, get_house_cusps, longitude_to_nakshatra

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_user_profile(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> UserProfile:
    """
    Get authenticated user's profile.

    Returns user profile including birth details, subscription info,
    and basic chart summary.

    Args:
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        UserProfile: User profile data.

    Raises:
        HTTPException: 401 if not authenticated, 500 if query fails.
    """
    try:
        # Query user profile with birth chart and credit balance
        query = """
            SELECT
                u.*,
                bc.lagna_rashi,
                bc.moon_rashi,
                bc.moon_nakshatra,
                bc.birth_datetime,
                bc.place_name,
                bc.birth_latitude,
                bc.birth_longitude,
                bc.timezone_offset,
                cw.balance as credit_balance
            FROM users u
            LEFT JOIN birth_charts bc ON bc.user_id = u.id
            LEFT JOIN credit_wallets cw ON cw.user_id = u.id
            WHERE u.id = $1
        """

        row = await db.fetchrow(query, str(current_user.id))

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )

        return UserProfile(
            id=row["id"],
            email=row["email"],
            name=row.get("name"),
            phone=row.get("phone"),
            gender=row.get("gender"),
            avatar_url=row.get("avatar_url"),
            subscription_tier=row.get("subscription_tier", "free"),
            birth_datetime=row.get("birth_datetime"),
            birth_latitude=row.get("birth_latitude"),
            birth_longitude=row.get("birth_longitude"),
            timezone_offset=row.get("timezone_offset"),
            place_name=row.get("place_name"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile",
        ) from None


@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    update: UserProfileUpdate,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> UserProfile:
    """
    Update user profile information.

    Updates name, gender, and avatar URL.

    Args:
        update: Profile update payload.
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        UserProfile: Updated user profile.

    Raises:
        HTTPException: 401 if not authenticated, 500 if update fails.
    """
    try:
        # Build update query with only non-null fields
        set_clauses = []
        params = []
        param_idx = 1

        if update.name is not None:
            set_clauses.append(f"name = ${param_idx}")
            params.append(update.name)
            param_idx += 1

        if update.gender is not None:
            set_clauses.append(f"gender = ${param_idx}")
            params.append(update.gender)
            param_idx += 1

        if update.avatar_url is not None:
            set_clauses.append(f"avatar_url = ${param_idx}")
            params.append(update.avatar_url)
            param_idx += 1

        if not set_clauses:
            # No updates to make
            return await get_user_profile(current_user, db)

        set_clauses.append("updated_at = NOW()")
        params.append(str(current_user.id))

        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ${param_idx} RETURNING *"

        await db.execute(query, *params)

        # Return updated profile
        return await get_user_profile(current_user, db)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        ) from None


@router.put("/me/birth-details", response_model=UserProfile)
async def update_birth_details(
    update: BirthDetailsUpdate,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> UserProfile:
    """
    Update user's birth details.

    Updates birth datetime, location, and timezone. Triggers chart
    recalculation.

    Args:
        update: Birth details update payload.
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        UserProfile: Updated user profile.

    Raises:
        HTTPException: 401 if not authenticated, 400 if invalid data,
            500 if update fails.
    """
    try:
        # Calculate planets and houses for new birth data
        planets_data = get_all_planets(
            update.datetime.isoformat(),
            update.latitude,
            update.longitude,
            update.timezone_offset,
        )

        houses_data = get_house_cusps(
            update.datetime.isoformat(),
            update.latitude,
            update.longitude,
        )

        # Get lagna and moon info
        lagna_rashi = planets_data.get("ascendant", {}).get("sign", "aries")
        moon_lon = planets_data.get("moon", {}).get("longitude", 0)
        moon_rashi = planets_data.get("moon", {}).get("sign", "aries")

        moon_nakshatra_data = longitude_to_nakshatra(moon_lon)
        moon_nakshatra = moon_nakshatra_data.get("nakshatra_name", "ashwini")

        # Update birth_charts table
        chart_query = """
            INSERT INTO birth_charts
            (user_id, birth_datetime, birth_latitude, birth_longitude,
             timezone_offset, place_name, lagna_rashi, moon_rashi,
             moon_nakshatra, planets_data, houses_data, created_at,
             updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(),
                    NOW())
            ON CONFLICT (user_id) DO UPDATE SET
                birth_datetime = $2,
                birth_latitude = $3,
                birth_longitude = $4,
                timezone_offset = $5,
                place_name = $6,
                lagna_rashi = $7,
                moon_rashi = $8,
                moon_nakshatra = $9,
                planets_data = $10,
                houses_data = $11,
                updated_at = NOW()
            RETURNING *
        """

        import json

        await db.execute(
            chart_query,
            str(current_user.id),
            update.datetime,
            update.latitude,
            update.longitude,
            update.timezone_offset,
            update.place_name or "",
            lagna_rashi,
            moon_rashi,
            moon_nakshatra,
            json.dumps(planets_data),
            json.dumps(houses_data),
        )

        # Update user's profile with birth details
        user_query = """
            UPDATE users SET
                birth_datetime = $1,
                birth_latitude = $2,
                birth_longitude = $3,
                timezone_offset = $4,
                place_name = $5,
                updated_at = NOW()
            WHERE id = $6
            RETURNING *
        """

        await db.execute(
            user_query,
            update.datetime,
            update.latitude,
            update.longitude,
            update.timezone_offset,
            update.place_name or "",
            str(current_user.id),
        )

        # Return updated profile
        return await get_user_profile(current_user, db)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update birth details for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update birth details",
        ) from None


@router.delete("/me")
async def delete_account(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> dict[str, str]:
    """
    Delete user account and all associated data.

    Permanently deletes user record, birth chart data, events, reports,
    and all related data.

    Args:
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        dict: Deletion confirmation.

    Raises:
        HTTPException: 401 if not authenticated, 500 if deletion fails.
    """
    try:
        # Delete in cascade order (respecting foreign key constraints)
        user_id = str(current_user.id)

        # Delete related records in order
        await db.execute("DELETE FROM chat_messages WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM user_events WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM generated_reports WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM credit_transactions WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM credit_wallets WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM birth_charts WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM users WHERE id = $1", user_id)

        return {
            "status": "deleted",
            "message": "Your account and all data have been permanently deleted",
        }

    except Exception as e:
        logger.error(f"Failed to delete account for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account",
        ) from None
