"""Billing and credits endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_current_user
from gateway.models import CreditBalance, CreditTransaction, UserContext

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/balance", response_model=CreditBalance)
async def get_credit_balance(
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> CreditBalance:
    """
    Get user's credit wallet balance.

    Args:
        current_user: Authenticated user context.

    Returns:
        CreditBalance: Current credit balance.

    Raises:
        HTTPException: 401 if not authenticated, 500 if query fails.
    """
    try:
        # TODO: Query user_credits table
        # Select balance for current_user
        balance = 0

        return CreditBalance(
            user_id=current_user.id,
            balance=balance,
            currency="credits",
        )

    except Exception as e:
        logger.error(f"Failed to get credit balance for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit balance",
        ) from e


@router.get("/history")
async def get_credit_history(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Get paginated credit transaction history.

    Args:
        current_user: Authenticated user context.
        skip: Number of transactions to skip (pagination offset).
        limit: Number of transactions to return (max 100).

    Returns:
        dict: Paginated credit transactions with total count.

    Raises:
        HTTPException: 401 if not authenticated, 500 if query fails.
    """
    try:
        if limit > 100:
            limit = 100

        # TODO: Query credit_transactions table
        # Select transactions for current_user, ordered by created_at DESC
        # Apply skip and limit for pagination

        transactions: list[CreditTransaction] = []

        return {
            "transactions": [t.dict() for t in transactions],
            "total": len(transactions),
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        logger.error(f"Failed to retrieve credit history for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit history",
        ) from e
