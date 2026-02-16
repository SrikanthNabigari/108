"""Configuration management for the 108 Gateway using Pydantic Settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Supabase Configuration
    supabase_url: str = "http://localhost:54321"
    supabase_service_key: str = ""
    supabase_jwt_secret: str = ""

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"

    # Anthropic Configuration
    anthropic_api_key: str = ""

    # RevenueCat Configuration
    revenuecat_webhook_secret: str = ""

    # FCM Configuration (optional)
    fcm_server_key: str | None = None

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:54322/postgres"

    # CORS Configuration
    cors_origins: list[str] = ["*"]

    # Environment
    env: str = "development"

    # Dev tier override for local testing ("free" | "pro" | "premium")
    dev_tier: str = "free"

    # Dev user ID — skip auth in development mode and use this user
    dev_user_id: str = ""

    class Config:
        """Pydantic configuration."""

        env_file = ".env", "gateway/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
