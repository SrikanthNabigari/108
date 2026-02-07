"""Reports endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_current_user
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
) -> list[dict[str, Any]]:
    """
    List available report types with prices and descriptions.

    Args:
        current_user: Authenticated user context.

    Returns:
        list: Available report types with details.

    Raises:
        HTTPException: 401 if not authenticated.
    """
    try:
        # TODO: Query reports table or config
        # Return available report types with credit costs

        return [
            {
                "type": "annual_report",
                "title": "Annual Report",
                "description": "Comprehensive yearly forecast and analysis",
                "credit_cost": 50,
            },
            {
                "type": "career_report",
                "title": "Career Report",
                "description": "Career guidance and professional prospects",
                "credit_cost": 40,
            },
            {
                "type": "health_report",
                "title": "Health Report",
                "description": "Health indicators and wellness guidance",
                "credit_cost": 30,
            },
            {
                "type": "relationship_report",
                "title": "Relationship Report",
                "description": "Relationship dynamics and compatibility",
                "credit_cost": 30,
            },
        ]

    except Exception as e:
        logger.error(f"Failed to list reports for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list available reports",
        ) from e


@router.post("", response_model=ReportResponse)
async def generate_report(
    request: ReportGenerateRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> ReportResponse:
    """
    Generate a new report.

    Checks user has sufficient credits, deducts credits, creates report job,
    and returns report metadata.

    Args:
        request: Report generation request.
        current_user: Authenticated user context.

    Returns:
        ReportResponse: Created report.

    Raises:
        HTTPException: 401 if not authenticated, 400 if invalid report type,
            402 if insufficient credits, 500 if generation fails.
    """
    try:
        # TODO: Look up report type and cost from config
        # TODO: Check user has sufficient credits
        # If not, raise 402 Payment Required
        # TODO: Deduct credits from user_credits
        # TODO: Create job in user_reports table with status='pending'
        # TODO: Queue async job to generate PDF

        raise NotImplementedError("Report generation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report",
        ) from e


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> ReportResponse:
    """
    Get a specific report.

    Args:
        report_id: Report UUID.
        current_user: Authenticated user context.

    Returns:
        ReportResponse: Report details.

    Raises:
        HTTPException: 401 if not authenticated, 404 if not found,
            500 if query fails.
    """
    try:
        # TODO: Query user_reports table
        # Verify report belongs to current_user before returning

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report {report_id} for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report",
        ) from e


@router.get("/{report_id}/pdf")
async def get_report_pdf(
    report_id: UUID,
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> dict[str, str]:
    """
    Get download URL for report PDF.

    Returns a presigned S3 URL for the PDF if it exists.

    Args:
        report_id: Report UUID.
        current_user: Authenticated user context.

    Returns:
        dict: PDF download URL and expiration.

    Raises:
        HTTPException: 401 if not authenticated, 404 if not found,
            400 if report not ready, 500 if operation fails.
    """
    try:
        # TODO: Query user_reports table
        # Verify report belongs to current_user
        # Check report status is 'completed'
        # Generate presigned S3 URL for PDF if not already available

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get PDF for report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report PDF",
        ) from e
