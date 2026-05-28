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

from gateway import __version__
from gateway.config import Settings
from gateway.models import AppInfoResponse, HealthResponse

logger = logging.getLogger(__name__)


# Default config used when Redis is unavailable or not yet cached.
DEFAULT_APP_CONFIG: dict[str, Any] = {
    "feature_gates": {
        "forecast_daily": {"free": "full", "pro": "full", "premium": "full"},
        "forecast_weekly": {"free": "full", "pro": "full", "premium": "full"},
        "forecast_monthly": {"free": "full", "pro": "full", "premium": "full"},
        "forecast_yearly": {"free": "locked", "pro": "locked", "premium": "full"},
        "chart_divisional": {"free": "full", "pro": "full", "premium": "full"},
        "analysis_yogas": {"free": "full", "pro": "full", "premium": "full"},
        "analysis_doshas": {"free": "full", "pro": "full", "premium": "full"},
        "analysis_dasha": {"free": "full", "pro": "full", "premium": "full"},
        "analysis_transits": {"free": "full", "pro": "full", "premium": "full"},
        "analysis_strength": {"free": "full", "pro": "full", "premium": "full"},
        "analysis_atmakaraka": {"free": "full", "pro": "full", "premium": "full"},
        "analysis_kp": {"free": "full", "pro": "full", "premium": "full"},
        "compatibility_quick": {"free": "full", "pro": "full", "premium": "full"},
        "compatibility_full": {"free": "locked", "pro": "locked", "premium": "full"},
        "state_map": {"free": "full", "pro": "full", "premium": "full"},
        "muhurta_check": {"free": "full", "pro": "full", "premium": "full"},
        "muhurta_find": {"free": "full", "pro": "full", "premium": "full"},
        "remedies": {"free": "full", "pro": "full", "premium": "full"},
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


async def initialize_redis(redis_url: str) -> Any:
    """Initialize Redis connection. Returns None if unavailable."""
    try:
        from redis.asyncio import from_url as redis_from_url

        redis = await redis_from_url(redis_url)
        await redis.ping()
        logger.info("Redis connected successfully")
        return redis
    except Exception as e:
        logger.warning(f"Redis unavailable, running without cache: {e}")
        return None


async def initialize_database(database_url: str) -> Any:
    """Initialize asyncpg connection pool."""
    try:
        import asyncpg

        pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            server_settings={"search_path": "public"},
        )
        # Startup self-test: verify public.users is accessible
        test_row = await pool.fetchrow(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name='users' AND column_name='auth_id'"
        )
        print(f"[STARTUP] DB URL: {database_url}")
        if test_row:
            print("[STARTUP] public.users.auth_id column VERIFIED")
        else:
            print("[STARTUP] ERROR: public.users.auth_id NOT FOUND!")
        return pool
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise RuntimeError(f"Database initialization failed: {e}") from e


async def load_app_config(redis: Any, db: Any) -> dict[str, Any]:
    """Load app configuration, caching to Redis if available."""
    config = DEFAULT_APP_CONFIG

    # Try to cache in Redis if available
    if redis is not None:
        try:
            cache_key = "app_config:v1"
            await redis.setex(cache_key, 300, json.dumps(config))
            logger.info("Application config loaded and cached in Redis")
        except Exception as e:
            logger.warning(f"Failed to cache config in Redis: {e}")
    else:
        logger.info("Application config loaded (no Redis cache)")

    return config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    settings = Settings()
    logger.info(f"Starting 108 Gateway in {settings.env} environment")

    try:
        # Redis is optional — gateway works without it
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
        if hasattr(app.state, "redis") and app.state.redis is not None:
            await app.state.redis.close()
        if hasattr(app.state, "db") and app.state.db is not None:
            await app.state.db.close()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
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
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            version=__version__,
            environment=settings.env,
            timestamp=datetime.utcnow(),
        )

    # Root Endpoint
    @app.get("/", response_model=AppInfoResponse)
    async def root() -> AppInfoResponse:
        """Root endpoint returning application information."""
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
        nadi,
        numerology,
        remedies,
        reports,
        state,
        webhooks,
    )

    # Auth router at /api/v1 (not /api/v1/auth) so /me is at /api/v1/me
    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
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
    app.include_router(state.router, prefix="/api/v1/state", tags=["state"])
    app.include_router(numerology.router, prefix="/api/v1/numerology", tags=["numerology"])
    app.include_router(nadi.router, prefix="/api/v1/nadi", tags=["nadi"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "gateway.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
