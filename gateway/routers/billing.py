"""Billing and credits endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_current_user, get_db
from gateway.models import CreditBalance, CreditTransaction, UserContext

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/balance", response_model=CreditBalance)
async def get_credit_balance(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> CreditBalance:
    """
    Get user's credit wallet balance.

    Args:
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        CreditBalance: Current credit balance.

    Raises:
        HTTPException: 401 if not authenticated, 500 if query fails.
    """
    try:
        # Query credit wallet balance
        query = "SELECT balance FROM credit_wallets WHERE user_id = $1"
        row = await db.fetchrow(query, str(current_user.id))

        balance = 0
        if row:
            balance = row["balance"]

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
        ) from None


@router.get("/history")
async def get_credit_history(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
    skip: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Get paginated credit transaction history.

    Args:
        current_user: Authenticated user context.
        db: Database connection.
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

        # Query credit transactions
        query = """
            SELECT *
            FROM credit_transactions
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """

        rows = await db.fetch(query, str(current_user.id), limit, skip)

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM credit_transactions WHERE user_id = $1"
        count_row = await db.fetchrow(count_query, str(current_user.id))
        total = count_row["total"] if count_row else 0

        transactions = [
            CreditTransaction(
                id=row["id"],
                user_id=row["user_id"],
                amount=row["amount"],
                transaction_type=row["transaction_type"],
                description=row["description"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

        return {
            "transactions": [t.dict() for t in transactions],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        logger.error(f"Failed to retrieve credit history for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit history",
        ) from None
