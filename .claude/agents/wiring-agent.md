---
name: wiring-agent
description: Exposes all coded-but-hidden features as MCP tools and API endpoints, wires Guide agent to use all available features
model: claude-sonnet-4-20250514
tools:
  - Edit
  - Write
  - Read
  - Grep
  - Glob
  - Bash
---

# WIRING Agent — Expose Hidden Features + Wire Guide Agent

Many features were built in Session 17 but NEVER exposed as MCP tools or API endpoints. Your job is to wire everything up so the full system is accessible.

## Your Files

You modify ONLY:
- `services/mcp/ephemeris_server.py` — Add cosmos tools
- `services/mcp/patterns_server.py` — Add self tools
- `services/mcp/context_server.py` — Add context tools
- `services/mcp/knowledge_server.py` — Add knowledge lookup tools
- `services/api/main.py` — Add REST API endpoints
- `packages/guide/src/agent.py` — Wire agent to use all features
- Tests for all of the above

## TASK 1: MCP Tool Exposure

### 1a. Ephemeris Server — Add Parashari Aspects Tool

```python
@mcp.tool()
def planetary_aspects(
    planet_positions: dict[str, dict]
) -> dict[str, Any]:
    """
    Calculate Parashari Graha Drishti (planetary aspects) for all planets.

    Args:
        planet_positions: Dict of planet positions {name: {house: int, longitude: float}}

    Returns:
        Full aspect map showing which planets aspect which houses, with strength.
    """
    from packages.cosmos.src.aspects import get_all_aspects, get_houses_aspected_by
    aspects = get_all_aspects(planet_positions)
    houses_aspected = get_houses_aspected_by(planet_positions)
    return {"aspects": aspects, "houses_aspected": houses_aspected}
```

### 1b. Patterns Server — Add Bhava Bala Tool

```python
@mcp.tool()
def bhava_bala(
    house_number: int,
    planets: dict[str, dict],
    lagna_rashi: str
) -> dict[str, Any]:
    """
    Calculate Bhava Bala (house strength) for a specific house.

    Components: Bhavadhipati Bala, Dig Bala, Drishti Bala, Occupant strength.
    """
    # Build BirthChart from planets dict, call calculate_bhava_bala()

@mcp.tool()
def all_bhava_balas(
    planets: dict[str, dict],
    lagna_rashi: str
) -> dict[str, Any]:
    """Calculate Bhava Bala for all 12 houses."""
    # Build BirthChart, call get_all_bhava_balas()
```

### 1c. Context Server — Add Muhurta + Eclipse Tools

```python
@mcp.tool()
def abhijit_muhurta(
    datetime_iso: str,
    latitude: float,
    longitude: float
) -> dict[str, Any]:
    """Get Abhijit Muhurta (most auspicious universal muhurta, around noon)."""
    # Get sunrise/sunset, call get_abhijit_muhurta()

@mcp.tool()
def brahma_muhurta(
    datetime_iso: str,
    latitude: float,
    longitude: float
) -> dict[str, Any]:
    """Get Brahma Muhurta (96 min before sunrise, best for spiritual practices)."""
    # Get sunrise, call get_brahma_muhurta()

@mcp.tool()
def eclipse_periods(
    year: int,
    month: int
) -> dict[str, Any]:
    """Check for solar and lunar eclipses in a given month."""
    # Call get_eclipse_periods()

@mcp.tool()
def marana_kaal(
    weekday: int
) -> dict[str, Any]:
    """Get Marana Kaal (death-like inauspicious periods) for a weekday."""
    # Call get_marana_kaal()
```

### 1d. Knowledge Server — Add 5 New Lookup Tools

```python
@mcp.tool()
def lookup_tithi(tithi_number: int) -> dict:
    """Get tithi (lunar day) definition. Number 1-30."""
    from packages.core.src.knowledge_loader import get_tithi_definitions
    data = get_tithi_definitions()
    tithis = data.get("tithis", [])
    for t in tithis:
        if t.get("number") == tithi_number:
            return t
    return {"error": f"Tithi {tithi_number} not found"}

@mcp.tool()
def lookup_karana(karana_name: str) -> dict:
    """Get karana (half-tithi) definition."""
    from packages.core.src.knowledge_loader import get_karana_definitions
    # Search movable + fixed karanas

@mcp.tool()
def lookup_vara(day_name: str) -> dict:
    """Get vara (weekday) definition with hora sequence."""
    from packages.core.src.knowledge_loader import get_vara_definitions
    # Search by english or sanskrit name

@mcp.tool()
def lookup_avastha(planet: str, longitude: float) -> dict:
    """Get planetary avastha (state) based on longitude in sign."""
    from packages.core.src.knowledge_loader import get_avastha_definitions
    # Calculate Baladi avastha from degree

@mcp.tool()
def lookup_nitya_yoga(yoga_number: int) -> dict:
    """Get nitya yoga (daily yoga from Sun+Moon) definition. Number 1-27."""
    from packages.core.src.knowledge_loader import get_nitya_yoga_definitions
    # Search by number
```

## TASK 2: REST API Endpoints

Add to `services/api/main.py`:

```python
@app.post("/api/v1/analysis/aspects")
async def calculate_aspects(request: ChartRequest):
    """Calculate Parashari Graha Drishti for a birth chart."""

@app.post("/api/v1/analysis/bhava-bala")
async def calculate_bhava_bala(request: ChartRequest):
    """Calculate Bhava Bala (house strength) for all 12 houses."""

@app.get("/api/v1/timing/abhijit-muhurta")
async def get_abhijit(lat: float, lon: float, date: str = None):
    """Get today's Abhijit Muhurta."""

@app.get("/api/v1/timing/brahma-muhurta")
async def get_brahma(lat: float, lon: float, date: str = None):
    """Get today's Brahma Muhurta."""

@app.get("/api/v1/timing/eclipses/{year}/{month}")
async def get_eclipses(year: int, month: int):
    """Check for eclipses in a given month."""

@app.get("/api/v1/knowledge/tithis/{number}")
async def get_tithi(number: int):
    """Get tithi definition."""

@app.get("/api/v1/knowledge/karanas/{name}")
async def get_karana(name: str):
    """Get karana definition."""

@app.get("/api/v1/knowledge/varas/{name}")
async def get_vara(name: str):
    """Get vara/weekday definition."""

@app.get("/api/v1/knowledge/avasthas/{planet}")
async def get_avastha(planet: str, longitude: float):
    """Get planetary avastha."""

@app.get("/api/v1/knowledge/nitya-yogas/{number}")
async def get_nitya_yoga(number: int):
    """Get nitya yoga definition."""
```

## TASK 3: Wire Guide Agent

Update `packages/guide/src/agent.py` to use ALL available features:

### In `_calculate()` node — add aspect analysis:
```python
from packages.cosmos.src.aspects import get_all_aspects
aspects = get_all_aspects(planet_positions)
state["aspects"] = aspects
```

### In `_analyze_patterns()` node — add bhava bala + avasthas:
```python
from packages.self.src.strength import get_all_bhava_balas
bhava_balas = get_all_bhava_balas(chart)
state["bhava_balas"] = bhava_balas
```

### In context gathering — add panchanga details:
```python
from packages.core.src.knowledge_loader import get_tithi_definitions, get_vara_definitions
# Use current panchanga data to add tithi, karana, vara, nitya yoga context
```

### In muhurta-related queries — add special muhurtas:
```python
from packages.context.src.muhurta import get_abhijit_muhurta, get_brahma_muhurta, get_eclipse_periods
# When user asks "is today auspicious?" include these
```

## Testing Requirements

```bash
# After each change
uv run pytest tests/ -v --tb=short
uv run ruff check services/ packages/guide/
```

Write tests for every new MCP tool and API endpoint.

## DO NOT TOUCH
- `packages/cosmos/src/` — only READ for imports
- `packages/self/src/` — only READ for imports
- `packages/context/src/` — only READ for imports
- `knowledge/` — only READ
- Only MODIFY: services/mcp/*, services/api/main.py, packages/guide/src/agent.py, and tests
