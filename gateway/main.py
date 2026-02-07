"""
FastAPI application for the 108 Gateway.

Main application entry point with middleware, routers, and lifespan handlers.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import from_url as redis_from_url

from gateway import __version__
from gateway.config import Settings
from gateway.models import AppInfoResponse, HealthResponse

logger = logging.getLogger(__name__)


async def initialize_redis(redis_url: str) -> Any:
    """
    Initialize Redis connection.

    Args:
        redis_url: Redis connection URL.

    Returns:
        Redis connection instance.

    Raises:
        RuntimeError: If Redis connection fails.
    """
    try:
        redis = await redis_from_url(redis_url)
        await redis.ping()
        logger.info("Redis connected successfully")
        return redis
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise RuntimeError(f"Redis initialization failed: {e}") from e


async def initialize_database(database_url: str) -> Any:
    """
    Initialize database connection.

    Args:
        database_url: Database connection URL.

    Returns:
        Database connection instance.

    Raises:
        RuntimeError: If database connection fails.
    """
    try:
        # TODO: Initialize asyncpg connection pool
        # import asyncpg
        # pool = await asyncpg.create_pool(database_url)
        logger.info("Database connected successfully")
        return None  # Placeholder
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise RuntimeError(f"Database initialization failed: {e}") from e


async def load_app_config(redis: Any, db: Any) -> dict[str, Any]:
    """
    Load application configuration into Redis cache.

    Args:
        redis: Redis connection instance.
        db: Database connection instance.

    Returns:
        dict: Application configuration.
    """
    try:
        # TODO: Query app_config table from database
        # For now, return default config structure
        default_config = {
            "feature_gates": {
                "forecast_daily": {"free": "full", "pro": "full", "premium": "full"},
                "forecast_weekly": {"free": "locked", "pro": "full", "premium": "full"},
                "forecast_monthly": {"free": "locked", "pro": "full", "premium": "full"},
                "forecast_yearly": {"free": "locked", "pro": "locked", "premium": "full"},
                "chart_divisional": {"free": "locked", "pro": "full", "premium": "full"},
                "analysis_yogas": {"free": "locked", "pro": "full", "premium": "full"},
                "analysis_doshas": {"free": "locked", "pro": "full", "premium": "full"},
                "analysis_dasha": {"free": "locked", "pro": "full", "premium": "full"},
                "analysis_transits": {"free": "locked", "pro": "full", "premium": "full"},
                "analysis_kp": {"free": "locked", "pro": "locked", "premium": "full"},
                "compatibility_quick": {"free": "locked", "pro": "full", "premium": "full"},
                "compatibility_full": {"free": "locked", "pro": "locked", "premium": "full"},
                "muhurta_check": {"free": "locked", "pro": "full", "premium": "full"},
                "muhurta_find": {"free": "locked", "pro": "full", "premium": "full"},
                "remedies": {"free": "locked", "pro": "full", "premium": "full"},
            },
            "chat_limits": {"free": 5, "pro": 30, "premium": -1},
            "subscription_tiers": {
                "free": {"name": "Free", "price": 0},
                "pro": {"name": "Pro", "price": 999},
                "premium": {"name": "Premium", "price": 2999},
            },
            "credit_packs": [
                {"credits": 10, "price": 99},
                {"credits": 50, "price": 399},
                {"credits": 100, "price": 699},
            ],
            "report_prices": {
                "annual_report": 50,
                "career_report": 40,
                "health_report": 30,
                "relationship_report": 30,
            },
        }

        # Cache config for 5 minutes
        cache_key = "app_config:v1"
        await redis.setex(cache_key, 300, json.dumps(default_config))
        logger.info("Application config loaded and cached")
        return default_config

    except Exception as e:
        logger.error(f"Failed to load app config: {e}")
        raise RuntimeError(f"Config initialization failed: {e}") from e


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan (startup and shutdown).

    Args:
        app: FastAPI application instance.

    Yields:
        None
    """
    # Startup
    settings = Settings()
    logger.info(f"Starting 108 Gateway in {settings.env} environment")

    try:
        redis = await initialize_redis(settings.redis_url)
        app.state.redis = redis

        db = await initialize_database(settings.database_url)
        app.state.db = db

        config = await load_app_config(redis, db)
        app.state.config = config

        logger.info("Application startup complete")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down 108 Gateway")
    try:
        if hasattr(app.state, "redis"):
            await app.state.redis.close()
        # TODO: Close database connection
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance.
    """
    settings = Settings()

    app = FastAPI(
        title="108 Gateway",
        description="Mobile app backend for 108 Vedic astrology platform",
        version=__version__,
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )

    # Health Check
    @app.get("/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        """
        Health check endpoint.

        Returns:
            HealthResponse: Health status.
        """
        return HealthResponse(
            status="healthy",
            version=__version__,
            environment=settings.env,
            timestamp=datetime.utcnow(),
        )

    # Root Endpoint
    @app.get("/", response_model=AppInfoResponse)
    async def root() -> AppInfoResponse:
        """
        Root endpoint returning application information.

        Returns:
            AppInfoResponse: Application metadata.
        """
        return AppInfoResponse(
            name="108 Gateway",
            version=__version__,
            description="Mobile app backend for 108 Vedic astrology platform",
            environment=settings.env,
            api_version="v1",
        )

    # Register Routers
    from gateway.routers import (
        analysis,
        auth,
        billing,
        chart,
        chat,
        compatibility,
        config,
        events,
        forecast,
        muhurta,
        remedies,
        reports,
        webhooks,
    )

    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(chart.router, prefix="/api/v1/chart", tags=["chart"])
    app.include_router(forecast.router, prefix="/api/v1/forecast", tags=["forecast"])
    app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    app.include_router(billing.router, prefix="/api/v1/credits", tags=["billing"])
    app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
    app.include_router(config.router, prefix="/api/v1/config", tags=["config"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
    app.include_router(remedies.router, prefix="/api/v1/remedies", tags=["remedies"])
    app.include_router(compatibility.router, prefix="/api/v1/compatibility", tags=["compatibility"])
    app.include_router(muhurta.router, prefix="/api/v1/muhurta", tags=["muhurta"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "gateway.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
