# 108 Complete Build Specification

> This document is the SINGLE SOURCE OF TRUTH for building the 108 application.
> Any Claude Code or Cowork session can read this and autonomously build all components.

---

## TABLE OF CONTENTS

1. [Project Structure](#1-project-structure)
2. [Knowledge Base Schema](#2-knowledge-base-schema)
3. [All Calculations Required](#3-all-calculations-required)
4. [Data Models (Pydantic)](#4-data-models-pydantic)
5. [MCP Tools Specification](#5-mcp-tools-specification)
6. [Agent Architecture](#6-agent-architecture)
7. [Database Schema](#7-database-schema)
8. [Build Order](#8-build-order)

---

## 1. PROJECT STRUCTURE

```
108-core/
├── pyproject.toml                    # Root workspace config (uv)
├── CLAUDE.md                         # Project rules for Claude
├── .mcp.json                         # MCP server configuration
├── docker-compose.yml                # Local dev (postgres, redis)
│
├── knowledge/                        # ALL JYOTISH DATA (JSON)
│   ├── definitions/
│   │   ├── planets.json              # 9 grahas
│   │   ├── rashis.json               # 12 signs
│   │   ├── nakshatras.json           # 27 lunar mansions
│   │   ├── houses.json               # 12 bhavas
│   │   ├── aspects.json              # Drishti rules
│   │   ├── relationships.json        # Planet friendships
│   │   ├── dignities.json            # Own/exalted/debilitated
│   │   └── dashas.json               # Vimshottari periods
│   ├── rules/
│   │   ├── yoga_detection.json       # 317+ yoga rules
│   │   ├── dosha_detection.json      # Dosha rules
│   │   └── strength_rules.json       # Shadbala rules
│   └── interpretations/
│       ├── planets/                  # Planet meanings by context
│       ├── houses/                   # House significations
│       ├── nakshatras/               # Nakshatra meanings
│       └── yogas/                    # Yoga interpretations
│
├── packages/                         # PYTHON PACKAGES (uv workspace)
│   ├── core/                         # Shared types, utilities
│   │   └── src/
│   │       ├── __init__.py
│   │       ├── models.py             # Pydantic models
│   │       ├── constants.py          # Enums, constants
│   │       └── utils.py              # Helpers
│   ├── cosmos/                       # Ephemeris calculations
│   │   └── src/
│   │       ├── __init__.py
│   │       ├── ephemeris.py          # Swiss Ephemeris wrapper
│   │       ├── houses.py             # House calculations
│   │       ├── nakshatras.py         # Nakshatra calculations
│   │       ├── divisional.py         # Varga charts
│   │       └── panchanga.py          # Tithi, yoga, karana
│   ├── self/                         # Pattern detection
│   │   └── src/
│   │       ├── __init__.py
│   │       ├── yoga_detector.py      # Yoga detection engine
│   │       ├── dosha_detector.py     # Dosha detection
│   │       ├── strength.py           # Shadbala, Ashtakavarga
│   │       └── personality.py        # Personality analysis
│   ├── context/                      # Temporal analysis
│   │   └── src/
│   │       ├── __init__.py
│   │       ├── dasha.py              # Vimshottari dasha
│   │       ├── transits.py           # Gochara analysis
│   │       └── muhurta.py            # Auspicious timing
│   ├── guide/                        # AI Agent
│   │   └── src/
│   │       ├── __init__.py
│   │       ├── agent.py              # LangGraph agent
│   │       ├── prompts.py            # System prompts
│   │       └── tools.py              # Agent tools
│   └── memory/                       # Learning & persistence
│       └── src/
│           ├── __init__.py
│           ├── mem0_client.py        # Mem0 integration
│           ├── store.py              # PostgreSQL + pgvector
│           └── profiles.py           # User profiles
│
├── services/
│   ├── api/                          # FastAPI gateway
│   │   └── main.py
│   ├── mcp/                          # MCP servers
│   │   ├── ephemeris_server.py
│   │   ├── patterns_server.py
│   │   └── knowledge_server.py
│   └── workers/                      # Background jobs
│       └── daily_horoscope.py
│
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/                     # Test birth charts
```

---

## 2. KNOWLEDGE BASE SCHEMA

### 2.1 planets.json

```json
{
  "planets": {
    "<planet_id>": {
      "id": "string",
      "name": "string",
      "sanskrit": "string",
      "symbol": "string",
      "nature": "benefic|malefic|neutral",
      "gender": "masculine|feminine|neutral",
      "element": "fire|earth|air|water|ether",
      "owns_signs": ["string"],
      "exalted_in": "string",
      "exaltation_degree": "number",
      "debilitated_in": "string",
      "moolatrikona": {"sign": "string", "degrees": [start, end]},
      "friends": ["string"],
      "enemies": ["string"],
      "neutral": ["string"],
      "karaka_of": ["string"],
      "body_parts": ["string"],
      "day": "string",
      "gem": "string",
      "metal": "string",
      "color": "string",
      "direction": "string",
      "dasha_years": "number",
      "aspects": ["number"]
    }
  }
}
```

**Required planets:** sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu

### 2.2 rashis.json

```json
{
  "rashis": {
    "<rashi_id>": {
      "id": "string",
      "name": "string",
      "sanskrit": "string",
      "number": "1-12",
      "symbol": "string",
      "element": "fire|earth|air|water",
      "quality": "movable|fixed|dual",
      "gender": "masculine|feminine",
      "ruler": "string (planet_id)",
      "exalted_planet": "string|null",
      "debilitated_planet": "string|null",
      "direction": "string",
      "body_part": "string",
      "degrees": {"start": "number", "end": "number"}
    }
  }
}
```

**Required rashis (12):** aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces

### 2.3 nakshatras.json

```json
{
  "nakshatras": [
    {
      "number": "1-27",
      "id": "string",
      "name": "string",
      "sanskrit": "string",
      "ruler": "string (planet_id)",
      "deity": "string",
      "symbol": "string",
      "shakti": "string",
      "gana": "deva|manushya|rakshasa",
      "animal": "string",
      "bird": "string",
      "tree": "string",
      "sounds": ["string", "string", "string", "string"],
      "degrees": {"start": "number", "end": "number"},
      "padas": [
        {"number": 1, "navamsha_sign": "string", "degrees": {"start": "number", "end": "number"}},
        {"number": 2, "navamsha_sign": "string", "degrees": {"start": "number", "end": "number"}},
        {"number": 3, "navamsha_sign": "string", "degrees": {"start": "number", "end": "number"}},
        {"number": 4, "navamsha_sign": "string", "degrees": {"start": "number", "end": "number"}}
      ]
    }
  ]
}
```

**Required nakshatras (27):** Ashwini, Bharani, Krittika, Rohini, Mrigashira, Ardra, Punarvasu, Pushya, Ashlesha, Magha, Purva Phalguni, Uttara Phalguni, Hasta, Chitra, Swati, Vishakha, Anuradha, Jyeshtha, Mula, Purva Ashadha, Uttara Ashadha, Shravana, Dhanishtha, Shatabhisha, Purva Bhadrapada, Uttara Bhadrapada, Revati

### 2.4 houses.json

```json
{
  "houses": {
    "<house_number>": {
      "number": "1-12",
      "name": "string",
      "sanskrit": "string",
      "category": "kendra|trikona|dusthana|upachaya|maraka",
      "significations": ["string"],
      "body_parts": ["string"],
      "karaka": "string (planet_id)",
      "opposite_house": "number"
    }
  }
}
```

**Required houses (12):** 1 (Lagna), 2 (Dhana), 3 (Sahaja), 4 (Sukha), 5 (Putra), 6 (Ripu), 7 (Kalatra), 8 (Ayur), 9 (Dharma), 10 (Karma), 11 (Labha), 12 (Vyaya)

### 2.5 yoga_detection.json

```json
{
  "yoga_rules": {
    "<yoga_id>": {
      "id": "string",
      "name": "string",
      "sanskrit": "string",
      "category": "pancha_mahapurusha|raja|dhana|arishta|nabhasa|chandra|surya|other",
      "description": "string",
      "detection": {
        "type": "single_planet|multi_planet|house_based|lord_based",
        "planet": "string|null",
        "planets": ["string"]|null,
        "conditions": [
          {
            "type": "in_kendra|in_trikona|in_dusthana|in_sign|in_house|in_own_sign|in_exalted_sign|in_debilitated_sign|conjunct|aspected_by|aspects|lord_in_house|mutual_aspect|exchange",
            "from": "lagna|moon|sun|planet",
            "houses": [number],
            "signs": ["string"],
            "planets": ["string"],
            "house": "number",
            "target_house": "number"
          }
        ],
        "all_conditions_required": "boolean"
      },
      "effects": {
        "positive": ["string"],
        "negative": ["string"]
      },
      "strength_factors": ["string"],
      "cancellation": ["string"]
    }
  }
}
```

**Yoga categories to implement:**
1. **Pancha Mahapurusha (5):** Ruchaka, Bhadra, Hamsa, Malavya, Shasha
2. **Raja Yogas (20+):** Various kendra-trikona combinations
3. **Dhana Yogas (15+):** Wealth combinations
4. **Arishta Yogas (10+):** Misfortune combinations
5. **Chandra Yogas (10+):** Moon-based yogas
6. **Surya Yogas (5+):** Sun-based yogas
7. **Nabhasa Yogas (32):** Pattern-based yogas

### 2.6 dosha_detection.json

```json
{
  "dosha_rules": {
    "<dosha_id>": {
      "id": "string",
      "name": "string",
      "description": "string",
      "detection": {
        "conditions": [
          {
            "type": "planet_in_house|planet_in_sign|planets_hemmed|all_planets_between",
            "planet": "string",
            "houses": [number],
            "from": "lagna|moon|venus",
            "between": ["string", "string"]
          }
        ],
        "all_conditions_required": "boolean"
      },
      "severity": "mild|moderate|severe",
      "effects": ["string"],
      "remedies": ["string"],
      "cancellation": [
        {
          "condition": "string",
          "description": "string"
        }
      ]
    }
  }
}
```

**Required doshas:**
1. **Mangal Dosha (Kuja Dosha):** Mars in 1, 2, 4, 7, 8, 12 from Lagna/Moon/Venus
2. **Kaal Sarp Dosha:** All planets between Rahu-Ketu axis
3. **Pitra Dosha:** Sun afflicted by Rahu/Saturn in specific houses
4. **Grahan Dosha:** Sun/Moon with Rahu/Ketu
5. **Shani Dosha:** Saturn afflictions
6. **Guru Chandal Dosha:** Jupiter with Rahu

---

## 3. ALL CALCULATIONS REQUIRED

### 3.1 Ephemeris Calculations (packages/cosmos/)

| Function | Input | Output | Notes |
|----------|-------|--------|-------|
| `get_julian_day(datetime)` | datetime | float | Convert to JD |
| `get_ayanamsa(jd, system)` | jd, "lahiri" | float | Precession correction |
| `get_planet_position(planet, jd)` | planet_id, jd | PlanetPosition | Sidereal longitude |
| `get_all_planets(jd)` | jd | Dict[str, PlanetPosition] | All 9 grahas |
| `get_house_cusps(jd, lat, lon, system)` | jd, coords, "placidus" | HouseCusps | 12 cusps + angles |
| `get_ascendant(jd, lat, lon)` | jd, coords | float | Lagna degree |
| `get_nakshatra(longitude)` | float | Nakshatra | Name, pada, lord |
| `get_navamsha(longitude)` | float | NavamshaPosition | D9 chart position |
| `get_divisional_chart(planets, division)` | planets, D1-D60 | Dict | Varga chart |

### 3.2 Nakshatra Calculations

| Function | Input | Output |
|----------|-------|--------|
| `longitude_to_nakshatra(lon)` | 0-360 | {name, number, pada, lord, degree_in_nakshatra} |
| `get_nakshatra_lord(nakshatra)` | name | planet_id |
| `get_pada_navamsha(nakshatra, pada)` | name, 1-4 | rashi |
| `get_tarabala(birth_nakshatra, transit_nakshatra)` | name, name | {tara, effect} |

**Nakshatra span:** Each = 13°20' (13.333°), Each pada = 3°20' (3.333°)

### 3.3 House Calculations

| Function | Input | Output |
|----------|-------|--------|
| `get_house_for_longitude(lon, cusps)` | degree, cusps | 1-12 |
| `get_house_lord(house, lagna_sign)` | 1-12, rashi | planet_id |
| `get_planets_in_house(planets, house, cusps)` | planets, 1-12, cusps | [planet_id] |
| `get_house_from_reference(planet_sign, reference_sign)` | rashi, rashi | 1-12 |

### 3.4 Dasha Calculations (packages/context/)

| Function | Input | Output |
|----------|-------|--------|
| `get_dasha_balance_at_birth(moon_longitude, birth_datetime)` | lon, datetime | {lord, remaining_days} |
| `get_mahadasha_sequence(birth_datetime, moon_longitude)` | datetime, lon | [{lord, start, end}] |
| `get_current_dasha(birth_datetime, moon_longitude, query_datetime)` | datetime, lon, datetime | {maha, antar, pratyantar, remaining} |
| `get_antardasha_sequence(mahadasha_lord, maha_start, maha_end)` | planet, datetime, datetime | [{lord, start, end}] |

**Vimshottari Dasha Years:**
- Ketu: 7, Venus: 20, Sun: 6, Moon: 10, Mars: 7
- Rahu: 18, Jupiter: 16, Saturn: 19, Mercury: 17
- **Total: 120 years**

**Dasha sequence:** Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury → (repeat)

### 3.5 Transit Calculations

| Function | Input | Output |
|----------|-------|--------|
| `get_gochara(natal_moon_sign, transit_planet, transit_sign)` | rashi, planet, rashi | {house_from_moon, is_favorable, vedha} |
| `check_sade_sati(natal_moon_sign, saturn_sign)` | rashi, rashi | {active, phase} |
| `check_dhaiya(natal_moon_sign, saturn_sign)` | rashi, rashi | {active, type} |
| `get_transit_effects(natal_chart, transit_positions)` | chart, positions | [TransitEffect] |

**Gochara (favorable houses from Moon):**
- Sun: 3, 6, 10, 11
- Moon: 1, 3, 6, 7, 10, 11
- Mars: 3, 6, 11
- Mercury: 2, 4, 6, 8, 10, 11
- Jupiter: 2, 5, 7, 9, 11
- Venus: 1, 2, 3, 4, 5, 8, 9, 11, 12
- Saturn: 3, 6, 11

### 3.6 Strength Calculations

| Function | Input | Output |
|----------|-------|--------|
| `calculate_shadbala(planet, chart)` | planet_id, chart | {total, components: {sthana, dig, kala, chesta, naisargika, drik}} |
| `calculate_ashtakavarga(planet, chart)` | planet_id, chart | [int] * 12 (bindus per sign) |
| `calculate_sarvashtakavarga(chart)` | chart | [int] * 12 (total bindus) |
| `get_planet_dignity(planet, sign)` | planet_id, rashi | "own|exalted|debilitated|friend|enemy|neutral" |

### 3.7 Yoga Detection (packages/self/)

| Function | Input | Output |
|----------|-------|--------|
| `detect_all_yogas(chart)` | BirthChart | [DetectedYoga] |
| `detect_yoga(yoga_rule, chart)` | YogaRule, chart | DetectedYoga or None |
| `evaluate_condition(condition, chart)` | Condition, chart | bool |
| `get_yoga_strength(yoga, chart)` | DetectedYoga, chart | float 0-1 |

### 3.8 Panchanga Calculations

| Function | Input | Output |
|----------|-------|--------|
| `get_tithi(sun_lon, moon_lon)` | float, float | {number, name, paksha} |
| `get_yoga(sun_lon, moon_lon)` | float, float | {number, name} |
| `get_karana(tithi_number)` | int | {number, name} |
| `get_vara(datetime)` | datetime | {number, name, lord} |
| `get_panchanga(datetime, lat, lon)` | datetime, coords | {tithi, nakshatra, yoga, karana, vara} |

**Tithi:** (Moon - Sun) / 12° → 1-30 (15 Shukla + 15 Krishna)
**Yoga (27):** (Sun + Moon) / 13°20'
**Karana (11 types, 60 per month):** Half tithi

---

## 4. DATA MODELS (Pydantic)

```python
# packages/core/src/models.py

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class Planet(str, Enum):
    SUN = "sun"
    MOON = "moon"
    MARS = "mars"
    MERCURY = "mercury"
    JUPITER = "jupiter"
    VENUS = "venus"
    SATURN = "saturn"
    RAHU = "rahu"
    KETU = "ketu"

class Rashi(str, Enum):
    ARIES = "aries"
    TAURUS = "taurus"
    GEMINI = "gemini"
    CANCER = "cancer"
    LEO = "leo"
    VIRGO = "virgo"
    LIBRA = "libra"
    SCORPIO = "scorpio"
    SAGITTARIUS = "sagittarius"
    CAPRICORN = "capricorn"
    AQUARIUS = "aquarius"
    PISCES = "pisces"

class BirthData(BaseModel):
    datetime_utc: datetime
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str
    place_name: Optional[str] = None

class PlanetPosition(BaseModel):
    planet: Planet
    longitude: float = Field(ge=0, lt=360)
    latitude: float
    speed: float
    rashi: Rashi
    rashi_degree: float = Field(ge=0, lt=30)
    nakshatra: str
    nakshatra_pada: int = Field(ge=1, le=4)
    nakshatra_lord: Planet
    is_retrograde: bool
    house: int = Field(ge=1, le=12)

class HouseCusps(BaseModel):
    ascendant: float
    mc: float  # Midheaven
    cusps: List[float]  # 12 cusps

class BirthChart(BaseModel):
    user_id: str
    birth_data: BirthData
    planets: Dict[Planet, PlanetPosition]
    houses: HouseCusps
    lagna_rashi: Rashi
    moon_rashi: Rashi
    moon_nakshatra: str
    ayanamsa: float
    calculated_at: datetime

class DetectedYoga(BaseModel):
    yoga_id: str
    name: str
    category: str
    is_present: bool
    strength: float = Field(ge=0, le=1)
    involved_planets: List[Planet]
    description: str

class DashaPeriod(BaseModel):
    lord: Planet
    start_date: datetime
    end_date: datetime
    level: str  # "maha", "antar", "pratyantar"

class CurrentDasha(BaseModel):
    mahadasha: DashaPeriod
    antardasha: DashaPeriod
    pratyantardasha: Optional[DashaPeriod]
    days_remaining_in_antar: int

class UserProfile(BaseModel):
    user_id: str
    name: Optional[str]
    email: Optional[str]
    birth_data: BirthData
    birth_chart: Optional[BirthChart]
    detected_yogas: List[DetectedYoga] = []
    detected_doshas: List[str] = []
    personality_type: Optional[str]
    preferences: Dict[str, any] = {}
    created_at: datetime
    updated_at: datetime
```

---

## 5. MCP TOOLS SPECIFICATION

### 5.1 Ephemeris Server Tools

```python
@mcp.tool()
def planetary_positions(datetime_iso: str, latitude: float, longitude: float, ayanamsa: str = "lahiri") -> Dict:
    """Calculate sidereal planetary positions for all 9 Vedic planets."""

@mcp.tool()
def house_cusps(datetime_iso: str, latitude: float, longitude: float, house_system: str = "placidus") -> Dict:
    """Calculate house cusps and ascendant."""

@mcp.tool()
def nakshatra_details(longitude: float) -> Dict:
    """Get nakshatra, pada, and lord for a given longitude."""

@mcp.tool()
def divisional_chart(planets: Dict, division: int) -> Dict:
    """Calculate divisional chart (D1-D60)."""

@mcp.tool()
def panchanga(datetime_iso: str, latitude: float, longitude: float) -> Dict:
    """Calculate complete panchanga (tithi, nakshatra, yoga, karana, vara)."""
```

### 5.2 Patterns Server Tools

```python
@mcp.tool()
def detect_yogas(planets: Dict, lagna_rashi: str) -> List[Dict]:
    """Detect all yogas present in the birth chart."""

@mcp.tool()
def detect_doshas(planets: Dict, lagna_rashi: str) -> List[Dict]:
    """Detect all doshas present in the birth chart."""

@mcp.tool()
def calculate_strength(planet: str, chart: Dict) -> Dict:
    """Calculate Shadbala for a planet."""

@mcp.tool()
def ashtakavarga(chart: Dict) -> Dict:
    """Calculate Ashtakavarga for all planets."""
```

### 5.3 Context Server Tools

```python
@mcp.tool()
def current_dasha(birth_datetime: str, moon_longitude: float, query_datetime: str = None) -> Dict:
    """Get current Mahadasha, Antardasha, and Pratyantardasha."""

@mcp.tool()
def dasha_periods(birth_datetime: str, moon_longitude: float, years: int = 120) -> List[Dict]:
    """Get all Mahadasha periods for lifetime."""

@mcp.tool()
def transit_analysis(natal_moon_rashi: str, transit_positions: Dict) -> Dict:
    """Analyze current transits from natal Moon."""

@mcp.tool()
def sade_sati_status(natal_moon_rashi: str, saturn_rashi: str) -> Dict:
    """Check Sade Sati status and phase."""
```

### 5.4 Knowledge Server Tools

```python
@mcp.tool()
def lookup_planet(planet_id: str) -> Dict:
    """Get complete planet definition."""

@mcp.tool()
def lookup_nakshatra(nakshatra_name: str) -> Dict:
    """Get complete nakshatra definition."""

@mcp.tool()
def lookup_yoga(yoga_id: str) -> Dict:
    """Get yoga definition and interpretation."""

@mcp.tool()
def search_knowledge(query: str, category: str = None) -> List[Dict]:
    """Semantic search across knowledge base."""
```

---

## 6. AGENT ARCHITECTURE

### 6.1 LangGraph State

```python
class AgentState(TypedDict):
    messages: List[Message]
    user_id: str
    birth_chart: Optional[BirthChart]
    current_dasha: Optional[CurrentDasha]
    current_transits: Optional[Dict]
    detected_patterns: Optional[Dict]
    memories: List[Dict]
    intent: Optional[str]
    response: Optional[str]
```

### 6.2 Agent Nodes

```
START
  ↓
[classify_intent] → Determine user intent
  ↓
[load_context] → Load birth chart, dasha, transits
  ↓
[check_memory] → Recall relevant memories
  ↓
[route_by_intent]
  ├─→ [calculate] → Run ephemeris tools (if needed)
  ├─→ [analyze_patterns] → Detect yogas/doshas
  ├─→ [predict] → Make predictions with dasha/transits
  └─→ [general] → Answer general questions
  ↓
[interpret] → Generate personalized interpretation
  ↓
[save_memory] → Store important facts
  ↓
END → Return response
```

### 6.3 Personality Adaptation

Based on Lagna (ascendant), adapt communication:

| Lagna | Style |
|-------|-------|
| Aries | Direct, action-oriented |
| Taurus | Grounded, practical |
| Gemini | Curious, conversational |
| Cancer | Nurturing, supportive |
| Leo | Confident, inspiring |
| Virgo | Analytical, detailed |
| Libra | Balanced, diplomatic |
| Scorpio | Deep, transformative |
| Sagittarius | Philosophical, optimistic |
| Capricorn | Structured, goal-oriented |
| Aquarius | Innovative, unique |
| Pisces | Intuitive, compassionate |

---

## 7. DATABASE SCHEMA

```sql
-- PostgreSQL with pgvector extension

CREATE EXTENSION IF NOT EXISTS vector;

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Birth Data
CREATE TABLE birth_charts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    birth_datetime TIMESTAMP NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    place_name VARCHAR(255),
    ayanamsa DECIMAL(10, 6),
    lagna_rashi VARCHAR(20),
    moon_rashi VARCHAR(20),
    moon_nakshatra VARCHAR(30),
    planets JSONB,  -- Full planet positions
    houses JSONB,   -- House cusps
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Detected Patterns
CREATE TABLE detected_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    pattern_type VARCHAR(20),  -- 'yoga' or 'dosha'
    pattern_id VARCHAR(50),
    pattern_name VARCHAR(100),
    strength DECIMAL(3, 2),
    details JSONB,
    detected_at TIMESTAMP DEFAULT NOW()
);

-- Memories (with vector embeddings)
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    content TEXT,
    category VARCHAR(50),  -- 'fact', 'preference', 'event', 'prediction'
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Predictions (for validation)
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    prediction_text TEXT,
    category VARCHAR(50),
    timeframe_start DATE,
    timeframe_end DATE,
    confidence DECIMAL(3, 2),
    factors JSONB,  -- What factors led to this prediction
    outcome TEXT,
    accuracy DECIMAL(3, 2),
    validated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    messages JSONB,
    summary TEXT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_memories_user ON memories(user_id);
CREATE INDEX idx_memories_embedding ON memories USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_birth_charts_user ON birth_charts(user_id);
CREATE INDEX idx_predictions_user ON predictions(user_id);
```

---

## 8. BUILD ORDER

### Phase 1: Foundation
1. Create all `pyproject.toml` files for packages
2. Create `knowledge/definitions/` JSON files (planets, rashis, nakshatras, houses)
3. Implement `packages/core/` (models, constants, utils)
4. Run `uv sync` to verify workspace

### Phase 2: Calculations
5. Implement `packages/cosmos/ephemeris.py` (Swiss Ephemeris wrapper)
6. Implement `packages/cosmos/nakshatras.py`
7. Implement `packages/cosmos/houses.py`
8. Implement `packages/cosmos/panchanga.py`
9. Write tests for all calculations

### Phase 3: Patterns
10. Create `knowledge/rules/yoga_detection.json`
11. Create `knowledge/rules/dosha_detection.json`
12. Implement `packages/self/yoga_detector.py`
13. Implement `packages/self/dosha_detector.py`
14. Implement `packages/self/strength.py`

### Phase 4: Context
15. Implement `packages/context/dasha.py`
16. Implement `packages/context/transits.py`
17. Implement `packages/context/muhurta.py`

### Phase 5: MCP Servers
18. Implement `services/mcp/ephemeris_server.py`
19. Implement `services/mcp/patterns_server.py`
20. Implement `services/mcp/knowledge_server.py`
21. Test all MCP tools

### Phase 6: Memory & Agent
22. Set up PostgreSQL + pgvector
23. Implement `packages/memory/store.py`
24. Implement `packages/memory/mem0_client.py`
25. Implement `packages/guide/agent.py` (LangGraph)
26. Implement `packages/guide/tools.py`

### Phase 7: API & Integration
27. Implement `services/api/main.py` (FastAPI)
28. Implement authentication
29. End-to-end testing
30. Deploy

---

## VALIDATION CHECKLIST

Before considering any component complete:

- [ ] All required fields present in JSON definitions
- [ ] Pydantic models validate correctly
- [ ] Unit tests pass
- [ ] Integration with other components verified
- [ ] MCP tool returns correct format
- [ ] Edge cases handled (e.g., Ketu = Rahu + 180°)
- [ ] Ayanamsa applied correctly (Lahiri)
- [ ] Timezone handling correct (always use UTC internally)

---

*This specification is the contract. Build exactly what is specified here.*
