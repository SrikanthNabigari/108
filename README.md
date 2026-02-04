# 108 - Personal Life Operating System

> "Decode how astrology is our complete operating system"

A Vedic Astrology-powered personal life operating system that calculates planetary positions, detects yogas and doshas, tracks dashas and transits, and provides personalized guidance through an AI agent.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GUIDE Layer                          │
│         (LangGraph Agent + Personality Adaptation)      │
├─────────────────────────────────────────────────────────┤
│                   MEMORY Layer                          │
│              (Mem0 + PostgreSQL + pgvector)             │
├─────────────────────────────────────────────────────────┤
│                   CONTEXT Layer                         │
│          (Dashas, Transits, Muhurta Timing)             │
├─────────────────────────────────────────────────────────┤
│                    SELF Layer                           │
│       (Yoga Detection, Dosha Analysis, Strengths)       │
├─────────────────────────────────────────────────────────┤
│                   COSMOS Layer                          │
│    (Swiss Ephemeris, Planetary Calculations, Houses)    │
└─────────────────────────────────────────────────────────┘
```

## Features

- **COSMOS**: Calculate all Vedic Jyotish elements with Swiss Ephemeris precision
- **SELF**: Detect yogas (Pancha Mahapurusha, Dhana, etc.) and doshas (Manglik, Kaal Sarp)
- **CONTEXT**: Track Vimshottari dashas, transits, Sade Sati, and muhurta timing
- **GUIDE**: AI agent that adapts communication style based on your Lagna
- **MEMORY**: Learn from every conversation with Mem0 integration

## Quick Start

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Start database services
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start API server
uv run uvicorn services.api.main:app --reload
```

API available at http://localhost:8000/docs

## Project Structure

```
108-core/
├── packages/                 # Core Python packages
│   ├── cosmos/              # Ephemeris, houses, nakshatras
│   ├── self/                # Yoga/dosha detection, strengths
│   ├── context/             # Dasha, transits, muhurta
│   ├── guide/               # LangGraph AI agent
│   └── memory/              # Mem0 + PostgreSQL storage
├── services/
│   ├── api/                 # FastAPI gateway (22 endpoints)
│   └── mcp/                 # MCP servers for Claude
├── knowledge/               # JSON definitions & rules
├── docs/                    # Documentation
└── examples/                # Example scripts
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/chart` | Calculate birth chart |
| `POST /api/v1/analysis/yogas` | Detect yogas |
| `POST /api/v1/analysis/doshas` | Detect doshas |
| `GET /api/v1/timing/transits` | Current planetary positions |
| `POST /api/v1/timing/dasha` | Vimshottari dasha periods |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Package Manager | uv |
| API | FastAPI |
| Agent | LangGraph |
| Memory | Mem0 + pgvector |
| Database | PostgreSQL |
| Ephemeris | pyswisseph |

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [108_BUILD_SPEC.md](108_BUILD_SPEC.md) - Build specification
- [CLAUDE.md](CLAUDE.md) - Project guidelines
- [docs/guides/](docs/guides/) - Usage guides

## License

MIT
