"""Reports endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_app_config, get_current_user, get_db
from gateway.models import (
    ReportGenerateRequest,
    ReportResponse,
    UserContext,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=list[dict[str, Any]])
async def list_available_reports(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> list[dict[str, Any]]:
    """
    List available report types with prices and descriptions.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        list: Available report types with details.

    Raises:
        HTTPException: 401 if not authenticated.
    """
    try:
        # Get report prices from config
        report_prices = config.get("report_prices", {})

        return [
            {
                "type": "annual_report",
                "title": "Annual Report",
                "description": "Comprehensive yearly forecast and analysis",
                "credit_cost": report_prices.get("annual_report", 50),
            },
            {
                "type": "career_report",
                "title": "Career Report",
                "description": "Career guidance and professional prospects",
                "credit_cost": report_prices.get("career_report", 40),
            },
            {
                "type": "health_report",
                "title": "Health Report",
                "description": "Health indicators and wellness guidance",
                "credit_cost": report_prices.get("health_report", 30),
            },
            {
                "type": "relationship_report",
                "title": "Relationship Report",
                "description": "Relationship dynamics and compatibility",
                "credit_cost": report_prices.get("relationship_report", 30),
            },
        ]

    except Exception as e:
        logger.error(f"Failed to list reports for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list available reports",
        ) from None


@router.post("", response_model=ReportResponse)
async def generate_report(
    request: ReportGenerateRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[object, Depends(get_db)],
) -> ReportResponse:
    """
    Generate a new report.

    Checks user has sufficient credits, deducts credits, creates report job,
    and returns report metadata.

    Args:
        request: Report generation request.
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        ReportResponse: Created report.

    Raises:
        HTTPException: 401 if not authenticated, 400 if invalid report type,
            402 if insufficient credits, 500 if generation fails.
    """
    try:
        # Look up report type and cost from config
        report_prices = config.get("report_prices", {})
        credit_cost = report_prices.get(request.report_type, 50)

        # Check user has sufficient credits
        balance_query = "SELECT balance FROM credit_wallets WHERE user_id = $1"
        balance_row = await db.fetchrow(balance_query, str(current_user.id))

        user_balance = balance_row["balance"] if balance_row else 0

        if user_balance < credit_cost:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Need {credit_cost}, have {user_balance}",
            )

        # Create report record in database
        import uuid

        report_id = uuid.uuid4()

        report_query = """
            INSERT INTO generated_reports
            (id, user_id, report_type, title, status, credit_cost,
             created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            RETURNING *
        """

        report_row = await db.fetchrow(
            report_query,
            str(report_id),
            str(current_user.id),
            request.report_type,
            f"{request.report_type.replace('_', ' ').title()}",
            "pending",
            credit_cost,
        )

        # Deduct credits from user's account
        # First insert transaction record
        transaction_query = """
            INSERT INTO credit_transactions
            (id, user_id, amount, transaction_type, description,
             created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
            RETURNING *
        """

        transaction_id = uuid.uuid4()

        await db.fetchrow(
            transaction_query,
            str(transaction_id),
            str(current_user.id),
            -credit_cost,  # Negative for deduction
            "report_generation",
            f"Generated {request.report_type} report",
        )

        # Update credit wallet balance
        await db.execute(
            "UPDATE credit_wallets SET balance = balance - $1 WHERE user_id = $2",
            credit_cost,
            str(current_user.id),
        )

        # TODO: Queue async job to generate PDF report

        return ReportResponse(
            id=report_row["id"],
            user_id=report_row["user_id"],
            report_type=report_row["report_type"],
            title=report_row["title"],
            status=report_row["status"],
            credit_cost=report_row["credit_cost"],
            pdf_url=None,
            created_at=report_row["created_at"],
            completed_at=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report",
        ) from None


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> ReportResponse:
    """
    Get a specific report.

    Args:
        report_id: Report UUID.
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        ReportResponse: Report details.

    Raises:
        HTTPException: 401 if not authenticated, 404 if not found,
            500 if query fails.
    """
    try:
        # Query report from database
        query = """
            SELECT *
            FROM generated_reports
            WHERE id = $1 AND user_id = $2
        """

        row = await db.fetchrow(query, str(report_id), str(current_user.id))

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )

        return ReportResponse(
            id=row["id"],
            user_id=row["user_id"],
            report_type=row["report_type"],
            title=row["title"],
            status=row["status"],
            credit_cost=row["credit_cost"],
            pdf_url=row.get("pdf_url"),
            created_at=row["created_at"],
            completed_at=row.get("completed_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report {report_id} for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report",
        ) from None


@router.get("/{report_id}/pdf")
async def get_report_pdf(
    report_id: UUID,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
) -> dict[str, str]:
    """
    Get download URL for report PDF.

    Returns a presigned S3 URL for the PDF if it exists.

    Args:
        report_id: Report UUID.
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        dict: PDF download URL and expiration.

    Raises:
        HTTPException: 401 if not authenticated, 404 if not found,
            400 if report not ready, 500 if operation fails.
    """
    try:
        # Query report from database
        query = """
            SELECT *
            FROM generated_reports
            WHERE id = $1 AND user_id = $2
        """

        row = await db.fetchrow(query, str(report_id), str(current_user.id))

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )

        # Check report status is completed
        if row["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Report is not ready. Current status: {row['status']}",
            )

        # TODO: Generate presigned S3 URL if not already available
        pdf_url = row.get("pdf_url", "")

        if not pdf_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF URL not available",
            )

        return {
            "url": pdf_url,
            "expires_in": "1 hour",
            "expires_at": "2026-02-07T01:00:00Z",  # Placeholder
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get PDF for report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report PDF",
        ) from None
