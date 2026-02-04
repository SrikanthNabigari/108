---
name: setup
description: Initialize the 108-core development environment
---

# Project Setup Command

Run this to set up the 108-core development environment.

## Steps

1. **Install uv** (if not installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Create virtual environment and install dependencies**
```bash
uv sync
```

3. **Install pre-commit hooks**
```bash
uv run pre-commit install
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your values
```

5. **Start PostgreSQL with Docker**
```bash
docker-compose up -d postgres redis
```

6. **Run database migrations**
```bash
uv run alembic upgrade head
```

7. **Verify setup**
```bash
uv run pytest tests/unit -v
```

## Verification Checklist

- [ ] `uv --version` shows version
- [ ] `uv run python --version` shows 3.11+
- [ ] `uv run ruff --version` works
- [ ] `uv run pytest --version` works
- [ ] PostgreSQL is running on port 5432
- [ ] Redis is running on port 6379
