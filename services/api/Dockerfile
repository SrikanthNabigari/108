# 108 API Service Dockerfile
# FastAPI gateway for the Vedic Astrology system

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Swiss Ephemeris
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Copy package configurations
COPY pyproject.toml ./
COPY packages/ ./packages/
COPY knowledge/ ./knowledge/
COPY services/api/ ./services/api/

# Install dependencies
RUN uv pip install --system -e ".[api]" || pip install fastapi uvicorn pydantic pyswisseph

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API server
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
