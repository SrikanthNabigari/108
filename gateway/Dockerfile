FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pyswisseph
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv and dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache \
    fastapi uvicorn[standard] pydantic pydantic-settings \
    httpx asyncpg redis PyJWT python-dotenv \
    pyswisseph anthropic

# Copy application code
COPY gateway/ ./gateway/
COPY packages/ ./packages/
COPY knowledge/ ./knowledge/

# Expose port
EXPOSE 8000

# Run gateway
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
