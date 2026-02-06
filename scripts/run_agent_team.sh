#!/bin/bash
# =============================================================================
# 108 Agent Team Orchestrator
# =============================================================================
# Uses Claude Code Agent Teams (Opus 4.6) to run 5 specialized agents in
# parallel, each owning a specific layer of the 108 architecture.
#
# Prerequisites:
#   - Claude Code installed: npm install -g @anthropic-ai/claude-code
#   - ANTHROPIC_API_KEY set in environment
#   - Agent Teams enabled (this script does it automatically)
#
# Usage:
#   ./scripts/run_agent_team.sh              # Run all agents
#   ./scripts/run_agent_team.sh cosmos       # Run only cosmos agent
#   ./scripts/run_agent_team.sh self context # Run self + context agents
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${PURPLE}"
echo "  ╔═══════════════════════════════════════════════════╗"
echo "  ║          108 — Agent Team Orchestrator            ║"
echo "  ║      Personal Life Operating System v0.16         ║"
echo "  ╚═══════════════════════════════════════════════════╝"
echo -e "${NC}"

# -----------------------------------------------------------------------------
# 1. Enable Agent Teams
# -----------------------------------------------------------------------------
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

echo -e "${GREEN}✓ Agent Teams enabled${NC}"
echo ""

# -----------------------------------------------------------------------------
# 2. Pre-flight checks
# -----------------------------------------------------------------------------
echo -e "${YELLOW}Pre-flight checks...${NC}"

# Check Claude Code installed
if ! command -v claude &> /dev/null; then
    echo -e "${RED}✗ Claude Code not found. Install: npm install -g @anthropic-ai/claude-code${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ Claude Code installed${NC}"

# Check API key
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    if [ -f .env ]; then
        source .env
        echo -e "${GREEN}  ✓ API key loaded from .env${NC}"
    else
        echo -e "${RED}  ✗ ANTHROPIC_API_KEY not set${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}  ✓ API key present${NC}"
fi

# Check uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}  ✗ uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi
echo -e "${GREEN}  ✓ uv installed${NC}"

# Run tests before starting
echo -e "${YELLOW}  Running pre-flight tests...${NC}"
TEST_RESULT=$(uv run pytest tests/ -q --tb=no 2>&1 | tail -1)
echo -e "${GREEN}  ✓ Tests: ${TEST_RESULT}${NC}"
echo ""

# -----------------------------------------------------------------------------
# 3. Agent Definitions
# -----------------------------------------------------------------------------
declare -A AGENTS
AGENTS[cosmos]="Fix COSMOS layer bugs (divisional.py exaltation, panchanga crash, houses stub) and add Parashari aspects"
AGENTS[self]="Fix SELF layer gaps (divisional interpreter D2-D60, Kala Bala, Bhava Bala, yoga cancellation, female Mangal Dosha)"
AGENTS[context]="Fix CONTEXT layer (complete varshaphal Tajika yogas, Yogini effects, Narayana stronger lord, transit aspects, muhurta)"
AGENTS[guide-memory]="Fix GUIDE+MEMORY (wire memory stubs, fix async/sync, remove Mem0 stubs, add conversation history, error handling)"
AGENTS[knowledge]="Create missing knowledge files (tithis, karanas, nitya yogas, varas, avasthas) and populate interpretations/ directory"

# Filter agents if specific ones requested
REQUESTED_AGENTS=("${@:-cosmos self context guide-memory knowledge}")

# -----------------------------------------------------------------------------
# 4. Launch Team
# -----------------------------------------------------------------------------
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo -e "${CYAN} Launching Agent Team${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════${NC}"
echo ""

TEAM_PROMPT="You are the team lead for the 108 Vedic Jyotish project. Your job is to coordinate 5 specialized agents working in parallel.

## Project Context
108 is a Personal Life Operating System built on Vedic Jyotish (astrology). It has 5 layers:
1. COSMOS - Swiss Ephemeris calculations (packages/cosmos/)
2. SELF - Pattern detection: yogas, doshas, strength (packages/self/)
3. CONTEXT - Timing: dashas, transits, muhurta (packages/context/)
4. GUIDE - LangGraph AI agent (packages/guide/)
5. MEMORY - PostgreSQL + pgvector persistence (packages/memory/)

## Current State
- 510+ tests passing, 0 lint errors
- Full audit completed (Session 16) — see docs/project_notes/work_log.md

## Your Task
Spawn a team with these agents. Each agent has a detailed prompt in .claude/agents/:

### Agent Assignments:
1. **cosmos-agent** — Fix P0 bugs in divisional.py, panchanga.py, houses.py. Add Parashari aspects.
2. **self-agent** — Complete divisional interpreter (D2-D60), fix Kala Bala, add Bhava Bala, yoga cancellation.
3. **context-agent** — Complete varshaphal (16 Tajika yogas), Yogini effects, transit aspects, muhurta additions.
4. **guide-memory-agent** — Wire memory stubs, fix async, add conversation history, decide on Mem0 vs pure Postgres.
5. **knowledge-agent** — Create tithis.json, karanas.json, nitya_yogas.json, varas.json, avasthas.json. Populate interpretations/.

## Coordination Rules
- Each agent owns ONLY their packages — no cross-boundary edits
- knowledge-agent should work FIRST or in parallel (others may need its output)
- After all agents complete: run full test suite, ruff check, update work_log.md
- Target: 0 ruff errors, all existing tests still passing, new tests for every change

## Communication
After spawning, periodically check in with each agent. When all done:
1. Run: uv run pytest tests/ -v
2. Run: uv run ruff check .
3. Report final counts to user
4. Update docs/project_notes/work_log.md with Session 17 entry

Begin by reading .claude/agents/*.md to understand each agent's full task list, then spawn the team."

echo -e "${BLUE}Starting Claude Code with team lead prompt...${NC}"
echo ""

# Launch Claude Code with the team lead prompt
claude --print "$TEAM_PROMPT"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN} Agent Team session complete${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"

# -----------------------------------------------------------------------------
# 5. Post-run verification
# -----------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}Running post-flight verification...${NC}"

echo -e "${CYAN}  Tests:${NC}"
uv run pytest tests/ -q --tb=short 2>&1 | tail -5

echo ""
echo -e "${CYAN}  Lint:${NC}"
uv run ruff check . 2>&1 | tail -3

echo ""
echo -e "${GREEN}Done! Check docs/project_notes/work_log.md for session summary.${NC}"
