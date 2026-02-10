# State Map API — Complete Build Plan

## Overview

Build the backend APIs that power the State Map Flutter page. The frontend is already built at `mobile/lib/features/state_map/` with mock data — these APIs replace the mocks with real 108-core calculations.

**What already exists:** 90% of the computation is already in `packages/context/` and `packages/self/`. We need a thin scoring layer + API routes.

---

## File 1: `packages/context/src/state_engine.py` (NEW)

The core scoring/normalization layer. Takes raw 108-core outputs and normalizes everything to 0-10 scores.

### What it does

Computes a **StateVector** for any given datetime:
- 7 factor scores (0-10 each)
- 5 area scores (0-10 each)
- 1 composite score (weighted average)
- mental state label
- confluence measure (0-6)

### Functions to create

```python
"""State Vector Engine — normalizes 108-core outputs into 0-10 scores."""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any
import math

# ── Factor weights for composite calculation ──
FACTOR_WEIGHTS = {
    "panchanga": 0.15,
    "transit_moon": 0.15,
    "gochara": 0.15,
    "dasha": 0.20,
    "yoga_activation": 0.10,
    "shadbala": 0.10,
    "ashtakavarga": 0.15,
}

# ── Area → House mapping ──
AREA_HOUSES = {
    "career": [10, 6, 2],
    "relationships": [7, 5, 11],
    "health": [1, 6, 8],
    "finance": [2, 11, 5],
    "spiritual": [9, 12, 5],
}

AREA_PLANETS = {
    "career": "saturn",
    "relationships": "venus",
    "health": "sun",
    "finance": "jupiter",
    "spiritual": "ketu",
}


def compute_state_vector(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict[str, Any],
    moon_longitude: float,
    lagna_rashi: str,
    moon_rashi: str | None = None,
    query_datetime: str | None = None,
    location_lat: float | None = None,
    location_lon: float | None = None,
) -> dict[str, Any]:
    """
    Compute a full state vector for a single datetime.

    Calls existing 108-core functions and normalizes outputs to 0-10.

    Returns:
        {
            "date": "2026-02-10",
            "factors": [
                {"id": "panchanga", "name": "Panchanga", "short_name": "PAN",
                 "score": 7.2, "dominant_planet": "jupiter", "description": "..."},
                ... (7 total)
            ],
            "areas": [
                {"id": "career", "name": "Career", "score": 6.5,
                 "houses": [10, 6, 2], "insight": "...", "dominant_planet": "saturn"},
                ... (5 total)
            ],
            "composite": 6.8,
            "mental_state": "Flowing",
            "confluence": 4.2,
            "hora_lord": "jupiter",
        }
    """
    # Implementation calls these existing functions:

    # 1. PANCHANGA SCORE
    #    Call: from packages.cosmos.src import get_panchanga
    #    get_panchanga(query_datetime, lat, lon)
    #    Normalize: tithi.is_auspicious + vara quality + yoga quality + karana quality
    #    Each sub-component 0-2.5, sum to 0-10

    # 2. TRANSIT MOON SCORE
    #    Call: from packages.self.src import get_transit_ashtakavarga_score
    #    get_transit_ashtakavarga_score(natal_planets, moon_sign_index)
    #    Normalize: BAV bindus 0-8 → scale to 0-10 (bindus / 8 * 10)

    # 3. GOCHARA SCORE
    #    Call: from packages.context.src import get_full_transit_analysis
    #    get_full_transit_analysis(natal_moon_rashi_index, transit_positions)
    #    Normalize: favorable_count / (favorable + unfavorable) * 10
    #    Bonus: -2 if sade_sati peak, -1 if sade_sati rising/setting

    # 4. DASHA SCORE
    #    Call: from packages.context.src import get_current_dasha
    #    get_current_dasha(birth_dt, moon_longitude, query_dt)
    #    Normalize: Check MD/AD/PD lords' dignity (exalted=10, own=8, friend=6, neutral=5, enemy=3, debilitated=1)
    #    Weighted: MD dignity * 0.5 + AD dignity * 0.3 + PD dignity * 0.2

    # 5. YOGA ACTIVATION SCORE
    #    Call: from packages.self.src import get_active_yogas
    #    get_active_yogas(natal_planets, transit_planets, lagna_rashi)
    #    Normalize: sum of activated yoga strengths, capped at 10
    #    If no yogas active: base score 4.0

    # 6. SHADBALA SCORE
    #    Call: from packages.self.src import StrengthCalculator
    #    calc = StrengthCalculator()
    #    Get shadbala for the current hora lord (or lagna lord)
    #    Normalize: total_shadbala / 600 * 10 (300+ is "strong", so 600 = max practical)

    # 7. ASHTAKAVARGA SCORE
    #    Call: from packages.self.src import calculate_sarvashtakavarga
    #    calculate_sarvashtakavarga(natal_planets, lagna_rashi)
    #    Get SAV for the sign where transit Moon is
    #    Normalize: SAV bindus for that sign / 56 * 10 (max possible is 56)

    # ── HORA LORD ──
    #    Use _HORA_SEQUENCE from packages.self.src.strength
    #    hora_index = (hours_since_sunrise) % 7
    #    Needs sunrise time from packages.cosmos.src.sunrise_sunset

    # ── AREA SCORES ──
    #    For each area, average the SAV bindus for its houses
    #    Plus adjust by dasha lord's relationship to house lords

    # ── COMPOSITE ──
    #    Weighted average using FACTOR_WEIGHTS

    # ── MENTAL STATE ──
    #    composite >= 8 → "Thriving"
    #    composite >= 6.5 → "Flowing"
    #    composite >= 5 → "Steady"
    #    composite >= 3.5 → "Challenged"
    #    composite >= 2 → "Struggling"
    #    else → "Turbulent"

    # ── CONFLUENCE ──
    #    Count how many factors agree (all above 5 or all below 5)
    #    agreement = max(count_above_5, count_below_5)
    #    confluence = agreement / 7 * 6
    pass


def compute_state_range(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict[str, Any],
    moon_longitude: float,
    lagna_rashi: str,
    moon_rashi: str | None = None,
    start_date: str = None,
    end_date: str = None,
    resolution: str = "daily",
    location_lat: float | None = None,
    location_lon: float | None = None,
) -> dict[str, Any]:
    """
    Compute state vectors for a date range.

    Args:
        resolution: "hourly" | "daily" | "weekly" | "monthly" | "yearly"

    Returns:
        {
            "vectors": [... list of state vectors ...],
            "resolution": "daily",
            "events": []  # populated from DB if available
        }
    """
    # Step through dates at the given resolution
    # For each step, call compute_state_vector()
    #
    # OPTIMIZATION: For factors that don't change within a day (dasha, gochara,
    # yoga_activation, shadbala, ashtakavarga), cache and reuse.
    # Only panchanga and transit_moon change hourly.
    #
    # Resolution steps:
    #   hourly  → timedelta(hours=1), one day max
    #   daily   → timedelta(days=1)
    #   weekly  → timedelta(days=7)
    #   monthly → iterate month by month
    #   yearly  → iterate year by year
    pass


def _normalize_panchanga(panchanga: dict) -> tuple[float, str, str]:
    """Convert panchanga output to 0-10 score.

    Returns: (score, dominant_planet, description)
    """
    # tithi: auspicious tithis (2,3,5,7,10,11,13,full,new) score 2.5, others 1.0
    # vara: benefic days (Mon,Wed,Thu,Fri) score 2.5, others 1.5
    # yoga: auspicious yogas score 2.5, inauspicious 0.5
    # karana: movable karanas score 2.5, fixed 1.0
    pass


def _normalize_gochara(transit_result: dict) -> tuple[float, str, str]:
    """Convert gochara analysis to 0-10 score."""
    # favorable_count / total * 10, adjusted for sade sati
    pass


def _normalize_dasha(dasha_result: dict, natal_planets: dict) -> tuple[float, str, str]:
    """Convert current dasha to 0-10 based on lord dignities."""
    pass


def _get_hora_lord(query_dt: datetime, lat: float, lon: float) -> str:
    """Calculate the current hora lord.

    Uses _HORA_SEQUENCE from strength.py and sunrise from cosmos.
    The day starts at sunrise. Each hora = day_duration / 12 (day) or night_duration / 12 (night).
    Day lord determines the starting hora lord.
    """
    # from packages.cosmos.src import get_sunrise_sunset
    # sunrise_data = get_sunrise_sunset(query_dt.date(), lat, lon)
    # sunrise = sunrise_data["sunrise"]
    # sunset = sunrise_data["sunset"]
    #
    # _HORA_SEQUENCE = ["sun", "venus", "mercury", "moon", "saturn", "jupiter", "mars"]
    # DAY_LORD_INDEX = {0: 3, 1: 6, 2: 2, 3: 5, 4: 1, 5: 4, 6: 0}  # Mon=Moon(3), Tue=Mars(6)...
    #
    # if query_dt >= sunrise and query_dt < sunset:
    #     # Day hora
    #     hora_duration = (sunset - sunrise) / 12
    #     hora_number = int((query_dt - sunrise) / hora_duration)
    # else:
    #     # Night hora
    #     next_sunrise = sunrise + timedelta(days=1)
    #     hora_duration = (next_sunrise - sunset) / 12
    #     if query_dt >= sunset:
    #         hora_number = int((query_dt - sunset) / hora_duration) + 12
    #     else:
    #         prev_sunset = sunset - timedelta(days=1)
    #         hora_number = int((query_dt - prev_sunset) / hora_duration) + 12
    #
    # start_idx = DAY_LORD_INDEX[query_dt.weekday()]
    # lord_idx = (start_idx + hora_number) % 7
    # return _HORA_SEQUENCE[lord_idx]
    pass


def _mental_state_label(composite: float) -> str:
    """Map composite score to human-readable mental state."""
    if composite >= 8:
        return "Thriving"
    if composite >= 6.5:
        return "Flowing"
    if composite >= 5:
        return "Steady"
    if composite >= 3.5:
        return "Challenged"
    if composite >= 2:
        return "Struggling"
    return "Turbulent"
```

### Imports needed (all exist already)

```python
from packages.cosmos.src import get_panchanga, get_sunrise_sunset
from packages.context.src import (
    get_current_dasha,
    get_full_transit_analysis,
    get_daily_forecast,
)
from packages.self.src import (
    StrengthCalculator,
    get_active_yogas,
    calculate_sarvashtakavarga,
    get_transit_ashtakavarga_score,
)
```

### After creating, export from `packages/context/src/__init__.py`

Add to imports:
```python
from .state_engine import compute_state_vector, compute_state_range
```

Add to `__all__`:
```python
"compute_state_vector",
"compute_state_range",
```

---

## File 2: `gateway/routers/state.py` (NEW)

The API router. Follows exact same pattern as `gateway/routers/forecast.py`.

```python
"""State Map endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from gateway.dependencies import get_current_user, get_db
from gateway.models import UserContext

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.context.src import compute_state_vector, compute_state_range

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Reuse the same birth chart loader from forecast.py ──

async def _load_birth_chart(db: Any, user_id: str) -> dict[str, Any] | None:
    """Load user's birth chart from database."""
    try:
        row = await db.fetchrow(
            "SELECT * FROM birth_charts WHERE user_id = $1",
            user_id,
        )
        if not row:
            return None
        return {
            "birth_datetime": row["birth_datetime"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "timezone": row["timezone"],
            "planets": row["planets"] if row["planets"] else {},
            "lagna_rashi": row["lagna_rashi"],
            "moon_rashi": row["moon_rashi"],
            "moon_nakshatra": row["moon_nakshatra"],
        }
    except Exception as e:
        logger.error(f"Failed to load birth chart: {e}")
        return None


def _build_natal_planets(planets: dict) -> dict[str, Any]:
    result = {}
    for name, data in planets.items():
        if isinstance(data, dict):
            result[name] = {
                "longitude": float(data.get("longitude", 0)),
                "rashi": int(data.get("rashi", 0)),
                "house": int(data.get("house", 0)),
                "nakshatra": data.get("nakshatra"),
            }
    return result


def _extract_moon_longitude(planets: dict) -> float | None:
    moon_data = planets.get("moon", {})
    if isinstance(moon_data, dict) and "longitude" in moon_data:
        return float(moon_data["longitude"])
    return None


# ── Endpoints ──

@router.get("/now")
async def get_state_now(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get current state vector — the 'NOW' card data."""
    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(status_code=404, detail="Birth chart not found")

        natal_planets = _build_natal_planets(chart.get("planets", {}))
        moon_lon = _extract_moon_longitude(chart.get("planets", {}))
        if moon_lon is None:
            raise ValueError("Moon position not found")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        result = compute_state_vector(
            birth_datetime=birth_dt.isoformat(),
            birth_lat=chart["latitude"],
            birth_lon=chart["longitude"],
            natal_planets=natal_planets,
            moon_longitude=moon_lon,
            lagna_rashi=chart["lagna_rashi"],
            moon_rashi=chart.get("moon_rashi"),
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"State now failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to compute state")


@router.get("/date/{date_str}")
async def get_state_for_date(
    date_str: str,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get state vector for a specific date."""
    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    chart = await _load_birth_chart(db, str(current_user.id))
    if not chart:
        raise HTTPException(status_code=404, detail="Birth chart not found")

    natal_planets = _build_natal_planets(chart.get("planets", {}))
    moon_lon = _extract_moon_longitude(chart.get("planets", {}))

    birth_dt = chart["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)

    result = compute_state_vector(
        birth_datetime=birth_dt.isoformat(),
        birth_lat=chart["latitude"],
        birth_lon=chart["longitude"],
        natal_planets=natal_planets,
        moon_longitude=moon_lon,
        lagna_rashi=chart["lagna_rashi"],
        moon_rashi=chart.get("moon_rashi"),
        query_datetime=query_date.isoformat(),
    )
    return result


@router.get("/range")
async def get_state_range(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD"),
    resolution: str = Query("daily", description="hourly|daily|weekly|monthly|yearly"),
) -> dict[str, Any]:
    """Get state vectors for a date range — powers the heat map."""
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    if resolution not in ("hourly", "daily", "weekly", "monthly", "yearly"):
        raise HTTPException(status_code=400, detail="Invalid resolution")

    chart = await _load_birth_chart(db, str(current_user.id))
    if not chart:
        raise HTTPException(status_code=404, detail="Birth chart not found")

    natal_planets = _build_natal_planets(chart.get("planets", {}))
    moon_lon = _extract_moon_longitude(chart.get("planets", {}))

    birth_dt = chart["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)

    # Load user events for overlay
    events = []
    try:
        rows = await db.fetch(
            "SELECT * FROM user_events WHERE user_id = $1 "
            "AND event_date >= $2 AND event_date <= $3 "
            "ORDER BY event_date",
            str(current_user.id), start_date.date(), end_date.date(),
        )
        events = [
            {
                "id": str(row["id"]),
                "date": row["event_date"].isoformat() if row["event_date"] else "",
                "type": row["event_type"],
                "description": row["event_description"],
                "actual_rating": float(row["actual_rating"]) if row.get("actual_rating") else None,
            }
            for row in rows
        ]
    except Exception as e:
        logger.warning(f"Failed to load events: {e}")

    result = compute_state_range(
        birth_datetime=birth_dt.isoformat(),
        birth_lat=chart["latitude"],
        birth_lon=chart["longitude"],
        natal_planets=natal_planets,
        moon_longitude=moon_lon,
        lagna_rashi=chart["lagna_rashi"],
        moon_rashi=chart.get("moon_rashi"),
        start_date=start,
        end_date=end,
        resolution=resolution,
    )
    result["events"] = events
    return result
```

---

## File 3: Wire into `gateway/main.py`

Add to the router imports block (line ~231):

```python
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
    remedies,
    reports,
    state,        # ← ADD THIS
    webhooks,
)
```

Add to the router registration block (after line ~260):

```python
app.include_router(state.router, prefix="/api/v1/state", tags=["state"])
```

Add feature gate in `DEFAULT_APP_CONFIG["feature_gates"]` (line ~28):

```python
"state_map": {"free": "full", "pro": "full", "premium": "full"},
```

---

## File 4: Update `user_events` table (if needed)

The events router already exists at `gateway/routers/events.py` with POST/GET. But the Flutter `AddEventSheet` sends an `actual_rating` field. Check if the DB table has this column:

```sql
-- Run in Supabase SQL editor if column doesn't exist
ALTER TABLE user_events ADD COLUMN IF NOT EXISTS actual_rating NUMERIC(3,1);
```

---

## Summary of changes

| File | Action | What |
|------|--------|------|
| `packages/context/src/state_engine.py` | CREATE | Core scoring engine (2 public functions) |
| `packages/context/src/__init__.py` | EDIT | Add exports for `compute_state_vector`, `compute_state_range` |
| `gateway/routers/state.py` | CREATE | 3 endpoints: `/now`, `/date/{date}`, `/range` |
| `gateway/main.py` | EDIT | Import + register state router |
| DB migration | RUN | Add `actual_rating` column to `user_events` |

## After building

Update Flutter `state_map_screen.dart` → uncomment the real API calls in `_fetchData()` and remove mock data fallback:

```dart
// In _fetchData():
final data = await ApiService().get(
  ApiConstants.stateRange(
    start: _rangeStart.toIso8601String().split('T').first,
    end: _rangeEnd.toIso8601String().split('T').first,
    resolution: _resolution,
  ),
  fromJson: (json) => json as Map<String, dynamic>,
);
final mapData = StateMapData.fromJson(data);

final nowData = await ApiService().get(
  ApiConstants.stateNow,
  fromJson: (json) => json as Map<String, dynamic>,
);
final nowState = StateVector.fromJson(nowData);
```

## Existing functions being called (all tested, all working)

| Function | Package | What it returns |
|----------|---------|-----------------|
| `get_panchanga()` | cosmos | Tithi, vara, yoga, karana, nakshatra |
| `get_sunrise_sunset()` | cosmos | Sunrise/sunset times for hora calc |
| `get_current_dasha()` | context | MD/AD/PD lords + dates |
| `get_full_transit_analysis()` | context | Favorable/unfavorable counts, sade sati |
| `get_daily_forecast()` | context | day_rating 1-10 (can use as validation) |
| `StrengthCalculator.calculate_shadbala()` | self | Six-fold strength total |
| `get_active_yogas()` | self | Currently activated natal yogas |
| `calculate_sarvashtakavarga()` | self | SAV bindus per sign (0-56) |
| `get_transit_ashtakavarga_score()` | self | BAV score for transit position |
