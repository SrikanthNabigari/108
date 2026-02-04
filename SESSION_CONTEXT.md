# Session Context - For New Claude Sessions

> Read this file to understand the project context from previous design sessions.

## Quick Start for Claude

When starting work on this project:

1. **Read these files first:**
   - `CLAUDE.md` - Project rules and structure
   - `ARCHITECTURE.md` - 5-layer architecture and tech stack
   - `KNOWLEDGE_DUMP.md` - JSON definitions to create

2. **Setup the packages:**
   - Each package in `packages/` needs a `pyproject.toml`
   - Use the format specified in CLAUDE.md
   - Run `uv sync` after creating them

3. **Key principles:**
   - Single source of truth in `knowledge/` JSON files
   - Never hardcode yoga/dosha conditions
   - Use Lahiri ayanamsa for all calculations
   - Memory-first design - the app learns and evolves

---

## What Has Been Done

### ✅ Completed
- Project structure created
- CLAUDE.md with project context
- Skills defined (jyotish-calculator, yoga-detector, memory-manager, knowledge-search)
- Agents defined (astro-guide, code-reviewer, prediction-engine)
- pyproject.toml for root workspace
- .mcp.json for MCP servers
- docker-compose.yml for local dev
- planets.json definition

### ❌ Needs to be Done
- Create pyproject.toml for each package in `packages/`
- Create JSON files from KNOWLEDGE_DUMP.md
- Implement actual Python code in packages
- Set up MCP servers
- Connect to PostgreSQL + pgvector

---

## User Context

**User:** Srikanth (Full Stack Web Developer)
**Birth Data:** 1992-12-03T03:00:00+05:30, lat: 16.726239, lon: 81.288428
**Chart:** Libra Lagna, Aquarius Moon, Purva Bhadrapada Pada 2
**Active Yoga:** Shasha Yoga (Saturn in Capricorn in 4th house)
**Current Dasha:** Mercury-Ketu
**Sade Sati:** Final phase

**Personal Note from User:**
> "108 is not just an astrology app. It is a personal life operating system...
> decode how astrology is our complete operating system... this app is the 1st step"

---

## Previous Conversation Learnings

1. **Yoga Detection Bug:** Previous implementation hardcoded yoga conditions. Fixed by creating JSON detection rules.

2. **Data Source Confusion:** Had 3 different yoga data sources. Solution: Single source of truth in `knowledge/rules/yoga_detection_rules.json`.

3. **Path Issues:** MCP server imports failed due to wrong path calculation. Always verify SERVICES_ROOT path.

4. **Architecture Insight:** The 5-layer model (COSMOS → SELF → CONTEXT → GUIDE → MEMORY) provides clean separation.

5. **Memory is Key:** What makes this a "life operating system" vs just a calculator is the MEMORY layer - learning from every interaction.

---

## File Locations Reference

```
108-core/
├── CLAUDE.md              # Main project rules (READ FIRST)
├── ARCHITECTURE.md        # Technical architecture
├── KNOWLEDGE_DUMP.md      # JSON definitions to create
├── SESSION_CONTEXT.md     # This file
├── .claude/
│   ├── skills/            # Domain knowledge for Claude
│   ├── agents/            # Specialized agent definitions
│   └── commands/          # Slash commands
├── knowledge/
│   ├── definitions/       # JSON definitions (planets, rashis, etc.)
│   └── rules/             # Detection rules (yogas, doshas)
├── packages/
│   ├── core/              # Shared types, utilities
│   ├── cosmos/            # Ephemeris calculations
│   ├── self/              # Pattern detection
│   ├── context/           # Transits, dashas
│   ├── guide/             # LangGraph agent
│   └── memory/            # Mem0 + LangMem
└── services/
    ├── api/               # FastAPI gateway
    ├── mcp/               # MCP servers
    └── workers/           # Temporal workflows
```

---

## Commands for Claude Code

```bash
# Setup
uv sync                    # Install dependencies
uv run pytest             # Run tests
uv run ruff check .       # Lint
uv run ruff format .      # Format

# MCP Servers
uv run python -m services.mcp.ephemeris
uv run python -m services.mcp.biorhythm

# API
uv run uvicorn services.api.main:app --reload
```
