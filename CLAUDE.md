# 108 - Personal Life Operating System

> "Decode how astrology is our complete operating system"

## Vision

108 is not just an astrology app. It is a **Personal Life Operating System** that:
- Calculates all Vedic Jyotish elements with precision
- Predicts past, present, and future
- Adapts to each person through detected personality
- Guides with tasks and scheduled events
- Learns from every conversation

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Package Manager | uv (Rust-based, 10-100x faster) |
| Linting | ruff (replaces black, isort, flake8) |
| Validation | pydantic v2 |
| API | FastAPI + asyncpg |
| Agent | LangGraph + MCP tools |
| Memory | Mem0 + LangMem + pgvector |
| Workflows | Temporal |
| Database | PostgreSQL + pgvector |
| Cache | Redis |

## Project Structure

```
108-core/
├── packages/           # Core Python packages (uv workspace)
│   ├── core/          # Shared types, utilities
│   ├── cosmos/        # Ephemeris calculations
│   ├── self/          # Pattern detection (yogas, doshas)
│   ├── context/       # Transits, dashas, panchanga
│   ├── guide/         # LangGraph agent
│   └── memory/        # Mem0 + LangMem integration
├── knowledge/         # Jyotish knowledge base
│   ├── definitions/   # JSON definitions (yogas, planets, etc.)
│   ├── interpretations/  # Detailed meanings
│   └── rules/         # Detection rules (machine-parseable)
├── services/          # Deployable services
│   ├── api/          # FastAPI gateway
│   ├── mcp/          # FastMCP servers
│   └── workers/      # Temporal workflows
├── apps/             # Frontend applications
│   ├── web/          # Next.js
│   └── mobile/       # React Native
└── tests/            # Test suites
```

## The 5-Layer Architecture

1. **COSMOS** - Calculate all cosmic positions (Swiss Ephemeris)
2. **SELF** - Detect yogas, doshas, personality patterns
3. **CONTEXT** - Track current transits, dasha, panchanga
4. **GUIDE** - LangGraph agent with personality adaptation
5. **MEMORY** - Continuous learning with every interaction

## Commands

```bash
# Install dependencies
uv sync

# Run API server
uv run uvicorn services.api.main:app --reload

# Run tests
uv run pytest

# Lint and format
uv run ruff check --fix .
uv run ruff format .

# Type check
uv run mypy packages/
```

## MCP Servers

Four MCP servers provide tools for Claude Desktop:

| Server | File | Tools |
|--------|------|-------|
| 108-ephemeris | `services/mcp/ephemeris_server.py` | planetary_positions, house_cusps, nakshatra_details, divisional_chart, panchanga |
| 108-patterns | `services/mcp/patterns_server.py` | detect_yogas, detect_doshas, calculate_strength, ashtakavarga |
| 108-context | `services/mcp/context_server.py` | current_dasha, dasha_periods, transit_analysis, sade_sati_status, muhurta_check |
| 108-knowledge | `services/mcp/knowledge_server.py` | lookup_planet, lookup_rashi, lookup_nakshatra, lookup_yoga, search_knowledge |

### Claude Desktop Configuration

Config location: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "108-ephemeris": {
      "command": "/path/to/108-core/.venv/bin/python",
      "args": ["/path/to/108-core/services/mcp/ephemeris_server.py"]
    }
  }
}
```

**Important**: Use the project's `.venv/bin/python` (not system python3) to ensure all dependencies are available.

## Code Style

- **Python 3.11+** required
- Use **type hints** everywhere
- Use **pydantic** for all data models
- Use **async/await** for I/O operations
- Keep functions **small and focused**
- Write **docstrings** for public functions
- Follow **ruff** suggestions

## IMPORTANT Rules

1. **Single Source of Truth**: All Jyotish definitions in `knowledge/`
2. **Separation of Concerns**: Calculations (cosmos) separate from interpretation (guide)
3. **Memory First**: Always consider what should be remembered
4. **Personality-Driven**: Adapt responses to detected personality
5. **Test Everything**: No code without tests
6. **Progressive Disclosure**: Don't load everything - fetch when needed

## Key Definitions

- **Yoga**: Beneficial planetary combination (317 defined)
- **Dosha**: Affliction or challenge (Mangal, Kaal Sarp, Pitra)
- **Dasha**: Planetary period system (Vimshottari)
- **Nakshatra**: Lunar mansion (27 total)
- **Rashi**: Zodiac sign (12 total)
- **Graha**: Planet (9 in Vedic: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)

## Skills Available

- `@jyotish-calculator` - Calculate planetary positions, houses, nakshatras
- `@yoga-detector` - Detect yogas from chart data
- `@knowledge-search` - Search interpretations and meanings
- `@memory-manager` - Save and recall user context

## Agents Available

### User-Facing Agents
- `/astro-guide` - Main conversational agent for users
- `/chart-analyzer` - Deep chart analysis specialist
- `/prediction-engine` - Future prediction with dasha/transit
- `/code-reviewer` - Code review for this project

### Development Agent Team (Claude Code Agent Teams)
5 specialized agents for parallel development. Enable with:
```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
# Or run: ./scripts/run_agent_team.sh
```

| Agent | Owns | Tasks |
|-------|------|-------|
| `cosmos-agent` | `packages/cosmos/` | Ephemeris bugs, aspects, panchanga fixes |
| `self-agent` | `packages/self/` | Divisional charts, strength, yoga cancellation |
| `context-agent` | `packages/context/` | Varshaphal, dasha effects, muhurta |
| `guide-memory-agent` | `packages/guide/` + `packages/memory/` | Memory wiring, async fix, conversation history |
| `knowledge-agent` | `knowledge/` | Missing JSON files, interpretations |

**Boundary rule**: Each agent modifies ONLY its owned packages. No cross-boundary edits.

See `docs/project_notes/work_log.md` Session 17 for full deliverables. Remaining: P2-P3 items only.

## When Starting a Task

1. Check if there's a relevant **skill** to invoke
2. Check `docs/project_notes/work_log.md` for past decisions and current task backlog
3. Run tests before and after changes: `uv run pytest tests/ -v`
4. Run lint after changes: `uv run ruff check .`
5. Update work_log.md after completing tasks
6. If using Agent Teams, respect package ownership boundaries

## Current Stats (Session 21)

- **1,653 tests passing**, 0 lint errors
- **522 yogas**, 55 doshas, 729 pratyantardasha combinations
- **4 MCP servers**, ~69 tools (+10 in Session 21)
- **~3.5MB** knowledge base (40 rule files, 15 definition files, 5 interpretation files)
- **23 REST API endpoints** (+11 in Session 21)
- **Dasha-Transit Cross-Analysis** engine (the "killer feature" connecting WHAT → WHEN → NOW)
- **Yoga Cancellation** + **Neecha Bhanga** 5-condition detection + **Planetary War**
- **Event Correlation** + **Transit Trigger Tracker** + **Remedies Engine**
- **Bhava Chalit** chart + **578 new interpretation rules** (D2/D4/D7/D24, Navamsha spouse, Ashtakavarga transit)

## Contact

Built with cosmic intention for decoding the operating system of life.
