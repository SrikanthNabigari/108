---
name: context-agent
description: CONTEXT layer specialist — Session 18 tasks — Ashtottari Dasha + Secondary Progressions
model: claude-sonnet-4-20250514
tools:
  - Edit
  - Write
  - Read
  - Grep
  - Glob
  - Bash
---

# CONTEXT Agent — Session 18 (Final Features)

You are responsible for `packages/context/` — specifically finishing 2 remaining features.

## Session 17 completed: 16 Tajika yogas, solar return calc, Yogini effects + pratyantardasha, Narayana stronger lord, transit aspects, Abhijit/Brahma muhurta, Marana Kaal, eclipse detection. All working. DO NOT re-do these.

## TASK 1: Ashtottari Dasha (108-year cycle)

Create `packages/context/src/ashtottari_dasha.py`:

The Ashtottari Dasha is an alternative to Vimshottari, used when **Rahu is in kendra (1,4,7,10) or trikona (1,5,9) from the Lagna lord**. It uses 8 planets (no Ketu) totaling 108 years.

```python
"""Ashtottari Dasha — 108-year planetary period system.

Usage condition: Rahu must be in kendra/trikona from Lagna lord.
8 planets (no Ketu): Sun(6), Moon(15), Mars(8), Mercury(17),
                      Saturn(10), Jupiter(19), Rahu(12), Venus(21)
Total: 108 years

Nakshatra-to-starting-lord mapping:
  Ardra, Punarvasu → Sun
  Pushya, Ashlesha → Moon
  Magha, Purva Phalguni → Mars
  Uttara Phalguni, Hasta → Mercury
  Chitra, Swati → Saturn
  Vishakha, Anuradha → Jupiter
  Jyeshtha, Moola → Rahu
  Purva Ashadha, Uttara Ashadha → Venus
  (Other nakshatras → Ashtottari not applicable)
"""

ASHTOTTARI_PERIODS = {
    "sun": 6, "moon": 15, "mars": 8, "mercury": 17,
    "saturn": 10, "jupiter": 19, "rahu": 12, "venus": 21,
}

ASHTOTTARI_SEQUENCE = ["sun", "moon", "mars", "mercury", "saturn", "jupiter", "rahu", "venus"]

NAKSHATRA_TO_LORD = {
    "ardra": "sun", "punarvasu": "sun",
    "pushya": "moon", "ashlesha": "moon",
    "magha": "mars", "purva_phalguni": "mars",
    "uttara_phalguni": "mercury", "hasta": "mercury",
    "chitra": "saturn", "swati": "saturn",
    "vishakha": "jupiter", "anuradha": "jupiter",
    "jyeshtha": "rahu", "moola": "rahu",
    "purva_ashadha": "venus", "uttara_ashadha": "venus",
}

def is_ashtottari_applicable(rahu_house: int, lagna_lord_house: int) -> bool:
    """Check if Ashtottari Dasha should be used.
    Condition: Rahu in kendra (1,4,7,10) or trikona (1,5,9) from lagna lord."""
    distance = (rahu_house - lagna_lord_house) % 12
    return distance in [0, 3, 6, 9, 4, 8]  # kendra + trikona

def get_starting_lord(moon_nakshatra: str) -> str | None:
    """Get starting dasha lord from Moon's nakshatra.
    Returns None if nakshatra is not in Ashtottari mapping."""
    return NAKSHATRA_TO_LORD.get(moon_nakshatra.lower().replace(" ", "_"))

def calculate_ashtottari_balance(moon_nakshatra: str, degree_in_nakshatra: float) -> dict:
    """Calculate remaining balance of first dasha period."""
    lord = get_starting_lord(moon_nakshatra)
    if not lord:
        return {"applicable": False, "reason": "Moon nakshatra not in Ashtottari system"}
    total_years = ASHTOTTARI_PERIODS[lord]
    elapsed_fraction = degree_in_nakshatra / 13.333
    remaining_years = total_years * (1 - elapsed_fraction)
    return {"lord": lord, "total_years": total_years, "remaining_years": remaining_years}

def calculate_ashtottari_sequence(birth_datetime: str, moon_nakshatra: str,
                                   degree_in_nakshatra: float, years: int = 108) -> list[dict]:
    """Calculate full Ashtottari Dasha sequence."""
    # Similar pattern to Vimshottari but with 8 planets, 108 years

def get_current_ashtottari(birth_datetime: str, moon_nakshatra: str,
                            degree_in_nakshatra: float,
                            query_datetime: str = None) -> dict:
    """Get current Ashtottari Mahadasha + Antardasha."""
    # Find which period covers the query date

def get_ashtottari_antardasha(birth_datetime: str, moon_nakshatra: str,
                               degree_in_nakshatra: float,
                               mahadasha_lord: str = None) -> list[dict]:
    """Get Antardasha breakdown for a Mahadasha period."""
    # 8 sub-periods within each Mahadasha, proportional to their years
```

**Effects**: Use the same knowledge base patterns as Vimshottari but note that Ashtottari is considered more suitable for nighttime births and for charts where Rahu is prominently placed.

**Models**: Add to `packages/core/src/models.py`:
```python
class AshtottariDashaPeriod(BaseModel):
    lord: str
    start_date: datetime
    end_date: datetime
    years: float
    is_current: bool = False
```

**Exports**: Update `packages/context/src/__init__.py` to export new functions.

## TASK 2: Secondary Progressions

Create `packages/context/src/progressions.py`:

Secondary progressions use the principle that **1 day after birth = 1 year of life**. So to see what happens at age 30, look at planetary positions 30 days after birth.

```python
"""Secondary Progressions — Day-for-a-Year system.

Principle: Each day after birth corresponds to one year of life.
To find progressed positions for age N: calculate positions for birth_date + N days.
"""

from datetime import datetime, timedelta
from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day

def calculate_progressed_positions(birth_datetime: str, birth_lat: float,
                                    birth_lon: float, target_age: float) -> dict:
    """Calculate progressed planetary positions for a given age.

    Args:
        birth_datetime: Birth datetime ISO format
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        target_age: Age in years (e.g., 30.5 for age 30 years 6 months)

    Returns:
        Progressed positions for all 9 planets + progressed Ascendant
    """
    birth_dt = datetime.fromisoformat(birth_datetime)
    progressed_dt = birth_dt + timedelta(days=target_age)
    jd = get_julian_day(progressed_dt)
    return get_all_planets(jd)

def calculate_progressed_to_natal_aspects(progressed: dict, natal: dict) -> list[dict]:
    """Find aspects between progressed and natal planets.

    Key aspects to check:
    - Progressed Sun to natal planets (major life themes)
    - Progressed Moon to natal planets (emotional themes, ~2.5yr cycle)
    - Progressed Ascendant to natal planets (self-expression changes)
    """
    # Check conjunction (0°), opposition (180°), trine (120°), square (90°), sextile (60°)
    # Use 1° orb for progressed aspects

def get_current_progressions(birth_datetime: str, birth_lat: float,
                              birth_lon: float, query_datetime: str = None) -> dict:
    """Get current progressed positions and active aspects."""
    birth_dt = datetime.fromisoformat(birth_datetime)
    query_dt = datetime.fromisoformat(query_datetime) if query_datetime else datetime.now()
    age_years = (query_dt - birth_dt).days / 365.25
    progressed = calculate_progressed_positions(birth_datetime, birth_lat, birth_lon, age_years)
    # Also get natal positions for aspect comparison
    natal_jd = get_julian_day(birth_dt)
    natal = get_all_planets(natal_jd)
    aspects = calculate_progressed_to_natal_aspects(progressed, natal)
    return {
        "age": age_years,
        "progressed_date": str(birth_dt + timedelta(days=age_years)),
        "progressed_positions": progressed,
        "active_aspects": aspects,
        "progressed_moon_sign": _get_sign(progressed["moon"]["longitude"]),
        "progressed_sun_sign": _get_sign(progressed["sun"]["longitude"]),
    }

def get_progression_timeline(birth_datetime: str, birth_lat: float,
                              birth_lon: float, start_age: int,
                              end_age: int) -> list[dict]:
    """Get progression timeline showing key aspect formations over a range of years."""
    # Useful for seeing upcoming major progressed aspects
```

**Models**: Add to `packages/core/src/models.py`:
```python
class ProgressedPosition(BaseModel):
    planet: str
    natal_longitude: float
    progressed_longitude: float
    sign_change: bool = False

class ProgressionResult(BaseModel):
    age: float
    progressed_positions: list[ProgressedPosition]
    active_aspects: list[dict]
    progressed_moon_sign: str
    progressed_sun_sign: str
```

**Exports**: Update `packages/context/src/__init__.py`.

## Testing Requirements

```bash
uv run pytest tests/ -v --tb=short -k "test_ashtottari or test_progression"
uv run ruff check packages/context/
```

Create `tests/unit/test_ashtottari_dasha.py` and `tests/unit/test_progressions.py`.
Use the standard test birth data: Dec 3, 1992, 3:00 AM, 16.722786, 81.294264

## DO NOT TOUCH
- `packages/cosmos/` — only READ for imports
- `packages/self/` — owned by self-agent
- `packages/guide/` — owned by wiring-agent
- `services/` — owned by wiring-agent
- Only modify `packages/context/`, `packages/core/src/models.py` (new models only), and tests
