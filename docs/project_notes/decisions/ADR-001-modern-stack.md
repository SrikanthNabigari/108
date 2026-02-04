# ADR-001: Modern Python Stack Selection

## Status
Accepted

## Context
Building 108 as a Personal Life Operating System requires a modern, maintainable, and scalable architecture. The previous implementation had issues with:
- Hardcoded yoga conditions instead of JSON rules
- Confusion between multiple data sources
- No persistent memory system
- Package management with Poetry (slower)

## Decision
Adopt a modern Python stack for 2026:

### Package Management
- **uv** instead of Poetry (10-100x faster, Rust-based)
- Monorepo with uv workspaces

### Code Quality
- **ruff** for linting AND formatting (replaces black, isort, flake8, pylint)
- **mypy** for static type checking
- **pydantic v2** for data validation

### API & Agent
- **FastAPI** with asyncpg for high-performance async API
- **LangGraph** for stateful agent orchestration
- **FastMCP** for tool exposure

### Memory
- **Mem0** for automatic memory extraction
- **LangMem** for explicit agent-controlled memory
- **PostgreSQL + pgvector** for vector storage

### Workflows
- **Temporal** for durable workflow orchestration

## Consequences

### Positive
- Faster development iteration (uv)
- Single tool for linting/formatting (ruff)
- Production-ready agent framework (LangGraph)
- Memory that actually learns (+26% accuracy with Mem0)
- Durable workflows for scheduled tasks

### Negative
- Learning curve for new tools
- Migration effort from existing codebase
- Need to rewrite yoga detection logic

### Risks
- Mem0 is relatively new
- LangGraph API may change
- Temporal adds operational complexity

## Date
2026-02-04
