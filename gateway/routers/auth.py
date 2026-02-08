"""Authentication endpoints for the 108 Gateway."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import timedelta

from gateway.dependencies import get_current_user, get_db
from gateway.models import (
    BirthDetailsUpdate,
    UserContext,
    UserProfile,
    UserProfileUpdate,
)
from packages.cosmos.src import (
    get_all_planets,
    get_house_cusps,
    get_julian_day,
    longitude_to_nakshatra,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_user_profile(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> UserProfile:
    """Get authenticated user's profile."""
    try:
        # Query user profile — all needed columns live on users table now
        row = await db.fetchrow(
            "SELECT * FROM public.users WHERE id = $1",
            current_user.id,
        )

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )

        # Get credit balance separately (may not exist yet)
        _credit_row = await db.fetchrow(
            "SELECT balance FROM credit_wallets WHERE user_id = $1",
            current_user.id,
        )

        return UserProfile(
            id=row["id"],
            email=row.get("email") or "",
            name=row.get("name"),
            phone=row.get("phone"),
            gender=row.get("gender"),
            avatar_url=row.get("avatar_url"),
            subscription_tier=row.get("subscription_tier", "free"),
            birth_datetime=row.get("birth_datetime"),
            birth_latitude=float(row["birth_latitude"])
            if row.get("birth_latitude") is not None
            else None,
            birth_longitude=float(row["birth_longitude"])
            if row.get("birth_longitude") is not None
            else None,
            timezone_offset=float(row["timezone_offset"])
            if row.get("timezone_offset") is not None
            else None,
            place_name=row.get("place_name"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
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
    """Update user profile information."""
    try:
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
            return await get_user_profile(current_user, db)

        set_clauses.append("updated_at = NOW()")
        params.append(current_user.id)

        query = (
            f"UPDATE public.users SET {', '.join(set_clauses)} WHERE id = ${param_idx} RETURNING *"
        )

        await db.execute(query, *params)

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
    """Update user's birth details and recalculate chart."""
    try:
        signs = [
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        ]

        # Convert local time to UTC using timezone_offset, then get Julian Day
        dt_utc = update.datetime - timedelta(hours=update.timezone_offset)
        jd = get_julian_day(dt_utc)

        # Calculate planets and houses
        planets_data = get_all_planets(jd)
        houses_data = get_house_cusps(jd, update.latitude, update.longitude)

        # Get lagna and moon info from longitudes
        asc_lon = houses_data.get("ascendant", 0)
        lagna_rashi = signs[int(asc_lon / 30) % 12]

        moon_lon = planets_data.get("moon", {}).get("longitude", 0)
        moon_rashi = signs[int(moon_lon / 30) % 12]

        moon_nakshatra_data = longitude_to_nakshatra(moon_lon)
        moon_nakshatra = moon_nakshatra_data.get("name", "ashwini")

        # Upsert birth_charts table — use actual schema column names
        chart_query = """
            INSERT INTO birth_charts
            (user_id, birth_datetime, latitude, longitude,
             timezone, place_name, lagna_rashi, moon_rashi,
             moon_nakshatra, planets, houses, calculated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
            ON CONFLICT (user_id) DO UPDATE SET
                birth_datetime = $2,
                latitude = $3,
                longitude = $4,
                timezone = $5,
                place_name = $6,
                lagna_rashi = $7,
                moon_rashi = $8,
                moon_nakshatra = $9,
                planets = $10,
                houses = $11,
                calculated_at = NOW()
            RETURNING *
        """

        await db.execute(
            chart_query,
            current_user.id,
            update.datetime,
            update.latitude,
            update.longitude,
            str(update.timezone_offset),
            update.place_name or "",
            lagna_rashi,
            moon_rashi,
            moon_nakshatra,
            json.dumps(planets_data),
            json.dumps(houses_data),
        )

        # Also update user's profile with birth details
        user_query = """
            UPDATE public.users SET
                birth_datetime = $1,
                birth_latitude = $2,
                birth_longitude = $3,
                timezone_offset = $4,
                place_name = $5,
                updated_at = NOW()
            WHERE id = $6
        """

        await db.execute(
            user_query,
            update.datetime,
            update.latitude,
            update.longitude,
            update.timezone_offset,
            update.place_name or "",
            current_user.id,
        )

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
    """Delete user account and all associated data."""
    try:
        user_id = current_user.id

        # Delete related records (cascade should handle most, but be explicit)
        await db.execute("DELETE FROM chat_messages WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM user_events WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM generated_reports WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM credit_transactions WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM credit_wallets WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM birth_charts WHERE user_id = $1", user_id)
        await db.execute("DELETE FROM public.users WHERE id = $1", user_id)

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
