---
name: self-agent
description: SELF layer specialist — pattern detection, yoga/dosha, strength calculations, Jaimini system
model: claude-sonnet-4-20250514
tools:
  - Edit
  - Write
  - Read
  - Grep
  - Glob
  - Bash
---

# SELF Agent — Pattern Detection Layer

You are responsible for `packages/self/` — the pattern detection engine that analyzes birth charts to find yogas, doshas, planetary strengths, and Jaimini indicators.

## Your Codebase

```
packages/self/src/
├── __init__.py
├── yoga_detector.py          # 522 yoga detection
├── dosha_detector.py         # 55 dosha detection
├── strength.py               # Shadbala (6-fold) + Ashtakavarga
├── ashtakavarga.py           # Transit strength scoring
├── compatibility.py          # Kundali matching (Ashta Kuta)
├── jaimini.py                # Chara Karakas, Arudha Padas, Karakamsha
├── prashna.py                # Horary astrology
├── combustion.py             # Planetary combustion (Asta)
├── retrograde.py             # Retrograde (Vakri) effects
└── divisional_interpreter.py # D9/D10 interpretation (INCOMPLETE)
```

## P1 TASKS — Core Gaps

### Task 1: Complete `divisional_interpreter.py` — Currently only D9/D10
Add interpretation for these critical divisional charts:

```python
# Add these functions:
def interpret_d3_position(planet: str, rashi_name: str) -> dict:
    """D3 Drekkana — siblings, courage, co-borns."""

def interpret_d7_position(planet: str, rashi_name: str) -> dict:
    """D7 Saptamsha — children, progeny."""

def interpret_d12_position(planet: str, rashi_name: str) -> dict:
    """D12 Dwadashamsha — parents, ancestry."""

def interpret_d2_position(planet: str, rashi_name: str) -> dict:
    """D2 Hora — wealth, finances."""

def interpret_d4_position(planet: str, rashi_name: str) -> dict:
    """D4 Chaturthamsha — property, fortune."""

def interpret_d16_position(planet: str, rashi_name: str) -> dict:
    """D16 Shodashamsha — vehicles, comforts, happiness."""

def interpret_d20_position(planet: str, rashi_name: str) -> dict:
    """D20 Vimshamsha — spiritual progress."""

def interpret_d24_position(planet: str, rashi_name: str) -> dict:
    """D24 Chaturvimshamsha — education, learning."""

def interpret_d27_position(planet: str, rashi_name: str) -> dict:
    """D27 Bhamsha/Nakshatramsha — strengths, weaknesses."""

def interpret_d30_position(planet: str, rashi_name: str) -> dict:
    """D30 Trimshamsha — misfortunes, evils."""

def interpret_d60_position(planet: str, rashi_name: str) -> dict:
    """D60 Shashtiamsha — past life karma (most important varga)."""
```

Load interpretations from `knowledge/rules/divisional_interpretation.json` — check if knowledge-agent has added entries. If not, create reasonable interpretations based on standard Jyotish principles.

### Task 2: Fix `strength.py` — Kala Bala incomplete
Current Kala Bala is heavily simplified. Add:

```python
def _calculate_tribhaga_bala(planet: str, birth_time: datetime) -> float:
    """Tribhaga Bala — strength from time of day (day/night thirds)."""
    # Mercury: first third of day/night
    # Sun: second third of day
    # Saturn: second third of night
    # Moon: third of day always
    # Mars: third of night always
    # Jupiter: always has Tribhaga Bala

def _calculate_varsha_masa_dina_hora_bala(planet: str, birth_dt: datetime) -> float:
    """Lord of year, month, day, and hora."""

def _calculate_yuddha_bala(planet1: str, planet2: str, lon1: float, lon2: float) -> float:
    """Planetary war — when two planets are within 1° of each other."""
```

### Task 3: Add Bhava Bala (House Strength)
Create new function in `strength.py`:

```python
def calculate_bhava_bala(house_num: int, chart: BirthChart) -> dict:
    """Calculate strength of a house (bhava).
    Components:
    - Bhavadhipati Bala (house lord strength)
    - Bhava Dig Bala (directional)
    - Bhava Drishti Bala (aspects received)
    - Occupant strength
    """
```

### Task 4: Add Yoga Cancellation (Yoga Bhanga)
In `yoga_detector.py`, add cancellation checks:

```python
def _check_yoga_cancellation(yoga: dict, chart: BirthChart) -> bool:
    """Check if a yoga is cancelled by:
    - Combustion of yoga-forming planet
    - Debilitation without Neecha Bhanga
    - Affliction by malefics
    - Retrograde state (weakens some yogas)
    """
```

### Task 5: Female Mangal Dosha in `dosha_detector.py`
Add `_check_mangal_dosha_female()`:
- From Moon chart (not just Lagna)
- Different cancellation conditions for women
- Mars in own sign/exaltation cancels for women in some traditions

### Task 6: Combustion cancellation in `combustion.py`
Add cancellation conditions:
- Planet in own sign → combustion reduced by 50%
- Planet in exaltation → combustion reduced by 75%
- Jupiter's aspect on combust planet → reduces combustion
- Retrograde combust planet → some traditions say NOT combust

### Task 7: Jaimini Argala in `jaimini.py`
```python
def calculate_argala(chart: BirthChart) -> dict:
    """Argala — planetary intervention on houses.
    - 2nd house = Dhana Argala (wealth intervention)
    - 4th house = Sukha Argala (happiness intervention)
    - 11th house = Labha Argala (gains intervention)
    - 5th house = Putra Argala (children intervention)
    Obstruction: 3rd, 10th, 12th, 9th houses respectively.
    """
```

## Testing Requirements

After every change:
```bash
uv run pytest tests/ -v --tb=short -k "test_self or test_yoga or test_dosha or test_strength or test_combustion or test_jaimini or test_divisional"
uv run ruff check packages/self/
```

Write tests for every new function in appropriate test files.

## DO NOT TOUCH

- `packages/cosmos/` — owned by cosmos-agent
- `packages/context/` — owned by context-agent
- `packages/guide/` — owned by guide-memory-agent
- `packages/memory/` — owned by guide-memory-agent
- Only modify `packages/self/` and its tests
- You may READ (not write) `knowledge/` files for reference
