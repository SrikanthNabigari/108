"""Life events endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_current_user, get_db
from gateway.models import (
    EventCreate,
    EventResponse,
    EventUpdate,
    UserContext,
)
from packages.context.src import correlate_event

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> EventResponse:
    """
    Create a new user life event.

    Args:
        event: Event creation payload.
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        EventResponse: Created event.

    Raises:
        HTTPException: 401 if not authenticated, 400 if invalid data,
            500 if creation fails.
    """
    try:
        import uuid

        event_id = uuid.uuid4()

        query = """
            INSERT INTO user_events
            (id, user_id, event_date, event_type, event_description,
             created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            RETURNING *
        """

        row = await db.fetchrow(
            query,
            str(event_id),
            str(current_user.id),
            event.event_date,
            event.event_type,
            event.event_description,
        )

        return EventResponse(
            id=row["id"],
            user_id=row["user_id"],
            event_date=row["event_date"],
            event_type=row["event_type"],
            event_description=row["event_description"],
            correlation_score=row.get("correlation_score"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    except Exception as e:
        logger.error(f"Failed to create event for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event",
        ) from None


@router.get("", response_model=list[EventResponse])
async def list_events(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
    skip: int = 0,
    limit: int = 50,
) -> list[EventResponse]:
    """
    List user's life events.

    Args:
        current_user: Authenticated user context.
        db: Database connection.
        skip: Number of events to skip (pagination offset).
        limit: Number of events to return (max 100).

    Returns:
        list: User's life events.

    Raises:
        HTTPException: 401 if not authenticated, 500 if query fails.
    """
    try:
        if limit > 100:
            limit = 100

        query = """
            SELECT *
            FROM user_events
            WHERE user_id = $1
            ORDER BY event_date DESC
            LIMIT $2 OFFSET $3
        """

        rows = await db.fetch(query, str(current_user.id), limit, skip)

        return [
            EventResponse(
                id=row["id"],
                user_id=row["user_id"],
                event_date=row["event_date"],
                event_type=row["event_type"],
                event_description=row["event_description"],
                correlation_score=row.get("correlation_score"),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"Failed to list events for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list events",
        ) from None


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> EventResponse:
    """
    Get a specific life event.

    Args:
        event_id: Event UUID.
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        EventResponse: Event details.

    Raises:
        HTTPException: 401 if not authenticated, 404 if not found,
            500 if query fails.
    """
    try:
        query = """
            SELECT *
            FROM user_events
            WHERE id = $1 AND user_id = $2
        """

        row = await db.fetchrow(query, str(event_id), str(current_user.id))

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        return EventResponse(
            id=row["id"],
            user_id=row["user_id"],
            event_date=row["event_date"],
            event_type=row["event_type"],
            event_description=row["event_description"],
            correlation_score=row.get("correlation_score"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get event {event_id} for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve event",
        ) from None


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    update: EventUpdate,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> EventResponse:
    """
    Update a life event.

    Args:
        event_id: Event UUID.
        update: Event update payload.
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        EventResponse: Updated event.

    Raises:
        HTTPException: 401 if not authenticated, 404 if not found,
            500 if update fails.
    """
    try:
        # Build update query with only non-null fields
        set_clauses = []
        params = []
        param_idx = 1

        if update.event_date is not None:
            set_clauses.append(f"event_date = ${param_idx}")
            params.append(update.event_date)
            param_idx += 1

        if update.event_type is not None:
            set_clauses.append(f"event_type = ${param_idx}")
            params.append(update.event_type)
            param_idx += 1

        if update.event_description is not None:
            set_clauses.append(f"event_description = ${param_idx}")
            params.append(update.event_description)
            param_idx += 1

        if not set_clauses:
            # No updates to make, return existing
            return await get_event(event_id, current_user, db)

        set_clauses.append("updated_at = NOW()")
        params.append(str(event_id))
        params.append(str(current_user.id))

        query = (
            f"UPDATE user_events SET {', '.join(set_clauses)} "
            f"WHERE id = ${param_idx} AND user_id = ${param_idx + 1} "
            f"RETURNING *"
        )

        row = await db.fetchrow(query, *params)

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        return EventResponse(
            id=row["id"],
            user_id=row["user_id"],
            event_date=row["event_date"],
            event_type=row["event_type"],
            event_description=row["event_description"],
            correlation_score=row.get("correlation_score"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update event {event_id} for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event",
        ) from None


@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> dict[str, str]:
    """
    Delete a life event.

    Args:
        event_id: Event UUID.
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        dict: Deletion confirmation.

    Raises:
        HTTPException: 401 if not authenticated, 404 if not found,
            500 if deletion fails.
    """
    try:
        # Verify event belongs to user before deleting
        query = """
            SELECT id FROM user_events
            WHERE id = $1 AND user_id = $2
        """

        row = await db.fetchrow(query, str(event_id), str(current_user.id))

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        # Delete the event
        await db.execute(
            "DELETE FROM user_events WHERE id = $1 AND user_id = $2",
            str(event_id),
            str(current_user.id),
        )

        return {"status": "deleted", "message": "Event deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete event {event_id} for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event",
        ) from None


@router.post("/{event_id}/correlate")
async def correlate_event_endpoint(
    event_id: UUID,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> dict[str, Any]:
    """
    Correlate a past event with birth chart.

    Analyzes the event date against the user's birth chart to find
    astrological correlations.

    Args:
        event_id: Event UUID.
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        dict: Correlation analysis.

    Raises:
        HTTPException: 401 if not authenticated, 404 if not found,
            500 if analysis fails.
    """
    try:
        # Get event from database
        event_query = """
            SELECT * FROM user_events
            WHERE id = $1 AND user_id = $2
        """

        event_row = await db.fetchrow(event_query, str(event_id), str(current_user.id))

        if not event_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )

        # Get user's birth chart
        chart_query = """
            SELECT * FROM birth_charts WHERE user_id = $1
        """

        chart_row = await db.fetchrow(chart_query, str(current_user.id))

        if not chart_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Birth chart not found. Please add your birth details.",
            )

        # Correlate event with birth chart
        correlation_result = correlate_event(
            event_row["event_date"],
            event_row["event_type"],
            event_row["event_description"],
            chart_row["birth_datetime"].isoformat(),
            eval(chart_row["planets_data"]),  # Convert JSON string to dict
            chart_row["moon_nakshatra"],
            chart_row["lagna_rashi"],
        )

        # Update event with correlation score
        update_query = """
            UPDATE user_events
            SET correlation_score = $1, updated_at = NOW()
            WHERE id = $2
            RETURNING *
        """

        updated_row = await db.fetchrow(
            update_query,
            correlation_result.get("correlation_score", 0),
            str(event_id),
        )

        return {
            **correlation_result,
            "event": {
                "id": updated_row["id"],
                "event_date": updated_row["event_date"],
                "event_type": updated_row["event_type"],
                "correlation_score": updated_row.get("correlation_score"),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to correlate event {event_id} for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to correlate event",
        ) from None
