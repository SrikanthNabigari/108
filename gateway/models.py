"""Pydantic models for the 108 Gateway API."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field


class AccessLevel(StrEnum):
    """Feature access levels."""

    FULL = "full"
    PREVIEW = "preview"
    LOCKED = "locked"


class SubscriptionTier(StrEnum):
    """User subscription tiers."""

    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class UserContext(BaseModel):
    """User context extracted from JWT and database."""

    id: UUID
    auth_id: str
    email: str
    phone: str | None = None
    name: str | None = None
    subscription_tier: SubscriptionTier
    revenuecat_id: str | None = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


T = TypeVar("T")


class GatedResponse(BaseModel, Generic[T]):
    """Generic response wrapper with access level and upgrade hint."""

    data: T
    access: AccessLevel
    upgrade_hint: str | None = None


class ChatRequest(BaseModel):
    """Chat message request."""

    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Chat message response."""

    message: str
    render_blocks: list[dict[str, Any]] = Field(default_factory=list)
    remaining_messages: int
    access: AccessLevel


class BirthDetailsUpdate(BaseModel):
    """Birth details update payload."""

    datetime: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone_offset: float = Field(..., ge=-12, le=12)
    place_name: str | None = None


class EventCreate(BaseModel):
    """Create a user life event."""

    event_date: str
    event_type: str
    event_description: str


class EventUpdate(BaseModel):
    """Update a user life event."""

    event_date: str | None = None
    event_type: str | None = None
    event_description: str | None = None


class EventResponse(BaseModel):
    """Life event response."""

    id: UUID
    user_id: UUID
    event_date: str
    event_type: str
    event_description: str
    correlation_score: float | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ReportGenerateRequest(BaseModel):
    """Generate a report request."""

    report_type: str


class ReportResponse(BaseModel):
    """Report response."""

    id: UUID
    user_id: UUID
    report_type: str
    title: str
    status: str
    credit_cost: int
    pdf_url: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class CreditBalance(BaseModel):
    """User credit wallet balance."""

    user_id: UUID
    balance: int
    currency: str = "credits"


class CreditTransaction(BaseModel):
    """Credit transaction history entry."""

    id: UUID
    user_id: UUID
    amount: int
    transaction_type: str
    description: str
    created_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ConfigResponse(BaseModel):
    """Application configuration response."""

    feature_gates: dict[str, dict[str, Any]]
    chat_limits: dict[str, int]
    subscription_tiers: dict[str, dict[str, Any]]
    credit_packs: list[dict[str, Any]]
    report_prices: dict[str, int]


class UserProfile(BaseModel):
    """User profile response."""

    id: UUID
    email: str
    name: str | None = None
    phone: str | None = None
    gender: str | None = None
    avatar_url: str | None = None
    subscription_tier: SubscriptionTier
    birth_datetime: datetime | None = None
    birth_latitude: float | None = None
    birth_longitude: float | None = None
    timezone_offset: float | None = None
    place_name: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Update user profile."""

    name: str | None = None
    gender: str | None = None
    avatar_url: str | None = None


class CompatibilityQuickRequest(BaseModel):
    """Quick compatibility check request."""

    partner_birth_datetime: datetime
    partner_latitude: float = Field(..., ge=-90, le=90)
    partner_longitude: float = Field(..., ge=-180, le=180)
    partner_timezone_offset: float = Field(..., ge=-12, le=12)


class CompatibilityFullRequest(BaseModel):
    """Full compatibility synastry request."""

    partner_birth_datetime: datetime
    partner_latitude: float = Field(..., ge=-90, le=90)
    partner_longitude: float = Field(..., ge=-180, le=180)
    partner_timezone_offset: float = Field(..., ge=-12, le=12)


class MuhurtaCheckRequest(BaseModel):
    """Muhurta quality check request."""

    datetime: datetime
    activity: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class MuhurtaFindRequest(BaseModel):
    """Find good muhurta dates request."""

    start_date: str
    end_date: str
    activity: str
    count: int = Field(default=5, ge=1, le=20)


class KPPredictionRequest(BaseModel):
    """KP (Krishnamurti Paddhati) prediction request."""

    event_type: str
    timing_preference: str = "next_30_days"


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str
    timestamp: datetime


class AppInfoResponse(BaseModel):
    """Root endpoint app info response."""

    name: str
    version: str
    description: str
    environment: str
    api_version: str
