# 108 — Claude Code Task Spec (Session 21)
## Complete the Missing Features & Tick Them Off

> **Context:** 108 is a Vedic Jyotish engine with 63 MCP tools, 522 yogas, 42 doshas, 1,477 tests.
> Architecture: `packages/cosmos/` (astronomy) → `packages/self/` (patterns) → `packages/context/` (timing) → `packages/guide/` (agent) → `services/mcp/` + `services/api/` (exposure)
> Every new feature must: (1) implement in the right package, (2) expose as MCP tool, (3) expose as API endpoint, (4) have unit tests, (5) wire into guide agent where relevant.

---

## Agent Plan: 3 Parallel Agents + 1 Sequential

```
┌──────────────────────────────────────────────────────────────┐
│                     RUN IN PARALLEL                          │
├──────────────┬──────────────────┬────────────────────────────┤
│ Agent 1      │ Agent 2          │ Agent 3                    │
│ SELF         │ CONTEXT          │ KNOWLEDGE                  │
│ (patterns)   │ (timing)         │ (interpretations)          │
│              │                  │                            │
│ • Yoga       │ • Dasha-Transit  │ • D2/D4/D7/D24 interps    │
│   cancellat° │   cross-analysis │ • D9 Navamsha spouse       │
│ • Neecha     │ • Transit-natal  │   interpretation rules     │
│   Bhanga     │   aspect engine  │ • Ashtakavarga transit     │
│ • Planetary  │ • Event          │   prediction rules         │
│   War        │   correlation    │ • Yoga cancellation        │
│ • Bhava      │ • Real-time      │   rules JSON               │
│   Chalit     │   transit tracker│ • Remedies recommendation  │
│              │ • Varshaphal     │   engine rules              │
│              │   current year   │                            │
├──────────────┴──────────────────┴────────────────────────────┤
│                     RUN AFTER ALL 3 COMPLETE                 │
├──────────────────────────────────────────────────────────────┤
│ Agent 4: WIRING                                              │
│ • MCP tools for all new features                             │
│ • API endpoints for all new features                         │
│ • Guide agent wiring (tools.py + agent.py)                   │
│ • Report generation templates                                │
│ • Integration tests                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Agent 1: SELF (Pattern Detection Upgrades)

### 1.1 Yoga Cancellation Engine
**File:** `packages/self/src/yoga_cancellation.py`
**Tests:** `tests/unit/test_yoga_cancellation.py` (already exists with ~15 tests, extend)

**What it does:** Check if detected yogas are actually cancelled by specific conditions.

**Cancellation rules to implement:**

| Yoga | Cancelled When |
|------|---------------|
| Pancha Mahapurusha (Sasa, Ruchaka, etc.) | Planet is combust (too close to Sun) |
| Pancha Mahapurusha | Planet is in Planetary War and loses |
| Raja Yoga | Yoga-forming planets are debilitated |
| Raja Yoga | Yoga-forming planets are in 6/8/12 from each other |
| Dhana Yoga | 2nd/11th lords afflicted by malefics |
| Gajakesari Yoga | Moon or Jupiter in dusthana (6/8/12) from Lagna |
| Neecha Bhanga | Cancellation itself gets cancelled if debilitated planet is combust |

**Function signatures:**
```python
def check_yoga_cancellation(
    yoga: dict,              # detected yoga from yoga_detector
    planets: dict,           # all planet positions with house/sign/longitude
    lagna_rashi: str,        # ascendant sign
    sun_longitude: float     # for combustion check
) -> dict:
    """Returns: {cancelled: bool, reason: str, partial: bool, modified_strength: float}"""

def get_cancellation_rules(yoga_type: str) -> list[dict]:
    """Load cancellation rules from knowledge base for a specific yoga type."""

def apply_cancellations_to_chart(
    yogas: list[dict],       # all detected yogas
    planets: dict,
    lagna_rashi: str,
    sun_longitude: float
) -> list[dict]:
    """Returns yogas with cancellation status added to each."""
```

**Knowledge file needed:** `packages/core/src/knowledge/rules/yoga_cancellation_rules.json`
Structure:
```json
{
  "pancha_mahapurusha": {
    "cancellation_conditions": [
      {"type": "combustion", "description": "Planet within combustion degrees of Sun"},
      {"type": "planetary_war", "description": "Planet loses Graha Yuddha"},
      {"type": "aspect_by_malefic", "description": "Aspected by natural malefic without benefic aspect"}
    ]
  },
  "raja_yoga": { ... },
  "dhana_yoga": { ... }
}
```

**Test count target:** 25+ tests

---

### 1.2 Neecha Bhanga Raja Yoga Detection
**File:** `packages/self/src/yoga_detector.py` (extend existing)

**What it does:** Detect when a debilitated planet's debilitation is cancelled, turning weakness into strength.

**5 conditions for Neecha Bhanga (ANY one = cancellation):**
1. Lord of the sign where planet is debilitated is in kendra from Lagna or Moon
2. Lord of the sign where planet is exalted is in kendra from Lagna or Moon
3. Planet that is exalted in the debilitation sign aspects the debilitated planet
4. Debilitated planet is retrograde
5. Debilitated planet is in Navamsha (D9) of its exaltation sign

**Example — Srikanth's chart:** Mars debilitated in Cancer (H10) BUT Mars is retrograde → Neecha Bhanga condition #4 met!

```python
def detect_neecha_bhanga(
    planet: str,
    planet_data: dict,       # longitude, sign, house, is_retrograde
    all_planets: dict,
    lagna_rashi: str,
    d9_positions: dict       # navamsha positions for condition #5
) -> dict:
    """Returns: {has_neecha_bhanga: bool, conditions_met: list, strength_modifier: float}"""
```

**Test count target:** 15+ tests (cover all 5 conditions + combinations)

---

### 1.3 Planetary War (Graha Yuddha)
**File:** `packages/self/src/planetary_war.py` (NEW)

**What it does:** When two planets (excluding Sun, Moon, Rahu, Ketu) are within 1° of each other, the one with lower longitude "wins." The loser's significations suffer.

**Rules:**
- Only between Mars, Mercury, Jupiter, Venus, Saturn
- Planets must be within 1° of each other
- Higher latitude planet loses (or alternative: brighter planet wins)
- Special: Venus always wins against other planets when retrograde

```python
def detect_planetary_wars(planets: dict) -> list[dict]:
    """Returns list of wars: {planet1, planet2, winner, loser, separation_degrees, effects}"""

def get_war_effects(winner: str, loser: str, houses: dict) -> dict:
    """Returns effects of the war on the loser's house lordships."""
```

**Test count target:** 12+ tests

---

### 1.4 Bhava Chalit Chart
**File:** `packages/cosmos/src/bhava_chalit.py` (NEW)

**What it does:** In the Rashi chart, planets are placed by sign. In Bhava Chalit, they're placed by the actual degree ranges of house cusps. A planet near a house cusp may shift to the adjacent house.

**Why it matters:** A planet showing in the 10th house in Rashi chart might actually function from the 9th or 11th in Bhava Chalit. This changes predictions.

```python
def calculate_bhava_chalit(
    planets: dict,           # planet longitudes
    cusps: dict,             # house cusp longitudes (from Placidus/KP)
    ascendant: float         # ascendant longitude
) -> dict:
    """Returns: {planet: {rashi_house: int, bhava_chalit_house: int, shifted: bool}}"""

def get_shifted_planets(bhava_chalit: dict) -> list[dict]:
    """Returns only planets that shifted houses between Rashi and Bhava Chalit."""
```

**Test count target:** 10+ tests

---

## Agent 2: CONTEXT (Timing Engine Upgrades)

### 2.1 Dasha-Transit Cross-Analysis Engine ⭐ MOST IMPORTANT
**File:** `packages/context/src/dasha_transit.py` (NEW)

**What it does:** The engine that answers "WHY is this happening NOW" by crossing current dasha lords with current transits.

**Logic:**
1. Get current MD/AD/PD lords
2. Check if transit planets are activating natal positions of dasha lords
3. Check if transit planets are in signs ruled by dasha lords
4. Check if dasha lords are transiting through significant natal houses
5. Score the activation strength

```python
def cross_analyze(
    natal_planets: dict,     # birth chart planet positions
    current_transits: dict,  # current planet positions
    current_dasha: dict,     # {mahadasha: str, antardasha: str, pratyantardasha: str}
    lagna_rashi: str,
    moon_rashi: str
) -> dict:
    """
    Returns:
    {
        "active_themes": [
            {
                "theme": "Career gains through intellect",
                "strength": 0.85,
                "dasha_trigger": "Mercury MD (9th lord) active",
                "transit_trigger": "Transit Jupiter in 9th house (fortune)",
                "houses_activated": [1, 5, 9],
                "yoga_activated": "Dhana Yoga (Sun 11th lord in 2nd)",
                "timing_window": "Feb 13-26, 2026"
            }
        ],
        "strongest_house": 5,
        "most_active_planet": "mercury",
        "overall_period_quality": "growth",
        "score": 72  # 0-100
    }
    """

def find_activation_windows(
    natal_planets: dict,
    current_dasha: dict,
    start_date: str,          # ISO
    end_date: str,            # ISO
    lagna_rashi: str
) -> list[dict]:
    """Find specific date windows when dasha lords get transit activation."""
```

**This is the killer feature** — it's what connects WHAT (yogas) to WHEN (dashas) to NOW (transits).

**Test count target:** 30+ tests

---

### 2.2 Transit-to-Natal Aspect Engine
**File:** `packages/context/src/transit_aspects.py` (NEW)

**What it does:** Calculate when transiting planets form aspects to natal planet positions.

```python
def get_transit_natal_aspects(
    natal_planets: dict,     # birth chart positions
    transit_planets: dict,   # current positions
    orb: float = 5.0         # degree orb for aspect
) -> list[dict]:
    """
    Returns:
    [
        {
            "transit_planet": "jupiter",
            "natal_planet": "saturn",
            "aspect_type": "trine",  # conjunction/opposition/trine/square/sextile
            "aspect_degree": 120,
            "orb": 2.3,
            "applying": true,       # getting closer (stronger) vs separating
            "exact_date": "2026-02-24",
            "transit_house": 9,
            "natal_house": 4,
            "effect": "Fortune planet activates Yoga Karaka — career/property gains"
        }
    ]
    """

def find_upcoming_aspects(
    natal_planets: dict,
    start_date: str,
    days_ahead: int = 30,
    latitude: float,
    longitude: float
) -> list[dict]:
    """Find all transit-natal aspects in the next N days with exact dates."""
```

**Aspect types:**
- Conjunction (0°), Opposition (180°), Trine (120°), Square (90°), Sextile (60°)
- Also Parashari special aspects: Mars 4th/8th, Jupiter 5th/9th, Saturn 3rd/10th

**Test count target:** 20+ tests

---

### 2.3 Event Correlation Engine
**File:** `packages/context/src/event_correlator.py` (NEW)

**What it does:** User inputs a past event with date → system finds which dasha/transit combination caused it → validates chart accuracy.

```python
def correlate_event(
    event_date: str,          # ISO date
    event_type: str,          # career, marriage, health, money, education, travel, loss
    event_description: str,
    birth_datetime: str,
    natal_planets: dict,
    moon_longitude: float,
    lagna_rashi: str,
    latitude: float,
    longitude: float
) -> dict:
    """
    Returns:
    {
        "event": "Got first job",
        "date": "2015-06-15",
        "dasha_at_event": {
            "mahadasha": "saturn",
            "antardasha": "mercury",
            "pratyantardasha": "venus"
        },
        "dasha_explanation": "Saturn MD (Yoga Karaka, 4th+5th lord) + Mercury AD (9th lord = fortune) — career through education and fortune",
        "transit_at_event": {
            "jupiter": {"sign": "leo", "house_from_lagna": 11, "note": "Jupiter in 11th = gains fulfilled"},
            "saturn": {"sign": "scorpio", "house_from_lagna": 2, "note": "Saturn in 2nd = building wealth"}
        },
        "yogas_active": ["Sasa Yoga (Saturn MD)", "Raja Yoga (4th+5th lords active)"],
        "correlation_score": 0.92,
        "explanation": "This event perfectly aligns with Saturn Mahadasha (Yoga Karaka activating career through discipline) combined with Mercury Antardasha (9th lord bringing fortune). Transit Jupiter in 11th house of gains confirms the positive career outcome."
    }
    """

def batch_correlate(
    events: list[dict],       # [{date, type, description}]
    birth_data: dict
) -> dict:
    """Correlate multiple life events and return chart accuracy score."""
```

**Test count target:** 15+ tests

---

### 2.4 Real-Time Transit Trigger Tracker
**File:** `packages/context/src/transit_tracker.py` (NEW)

**What it does:** Given a birth chart, find the next N significant transit events with exact dates.

```python
def get_upcoming_triggers(
    natal_planets: dict,
    lagna_rashi: str,
    moon_rashi: str,
    start_date: str,
    days_ahead: int = 30,
    latitude: float = 0,
    longitude: float = 0
) -> list[dict]:
    """
    Returns sorted list of upcoming transit triggers:
    [
        {
            "date": "2026-02-13",
            "days_from_now": 7,
            "trigger": "Sun enters Aquarius (your 5th house)",
            "type": "sign_ingress",
            "significance": "high",
            "effect": "11th lord (gains) enters 5th house (speculation) — income activation",
            "financial_impact": "positive",
            "career_impact": "positive"
        },
        {
            "date": "2026-02-24",
            "days_from_now": 18,
            "trigger": "Venus conjuncts natal Moon at 24° Aquarius",
            "type": "transit_conjunction",
            "significance": "very_high",
            "effect": "Lagna lord meets 10th lord — peak career moment"
        }
    ]
    """
```

**Trigger types to detect:**
1. Planet sign ingress (enters new sign/house)
2. Transit planet conjuncts natal planet (within 2° orb)
3. Transit planet aspects natal planet (Parashari aspects)
4. Retrograde station (planet stops and reverses)
5. Dasha period change (MD/AD/PD transitions)
6. Eclipse on natal positions

**Test count target:** 20+ tests

---

### 2.5 Varshaphal (Solar Return) for Current Year
**File:** `packages/context/src/varshaphal.py` (already exists, needs current-year function)

**Add function:**
```python
def get_current_varshaphal(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    query_date: str = None     # defaults to now
) -> dict:
    """Calculate Varshaphal for the current solar year.
    Returns: Muntha position, Varshesha (year lord), Tajika yogas, 5 Sahams."""
```

**Test count target:** 10+ tests

---

## Agent 3: KNOWLEDGE (Interpretation Data)

### 3.1 Divisional Chart Interpretations (D2, D4, D7, D24)
**File:** `packages/core/src/knowledge/rules/divisional_interpretation.json` (extend existing)

Currently has D9 (marriage) and D10 (career). Add:

| Chart | Rules | What It Shows |
|-------|-------|---------------|
| D2 (Hora) | 18 planet-in-hora rules | Wealth potential — Sun's Hora vs Moon's Hora |
| D4 (Chaturthamsha) | 108 planet-in-sign rules | Property, vehicles, fixed assets |
| D7 (Saptamsha) | 108 planet-in-sign rules | Children, progeny |
| D24 (Chaturvimshamsha) | 108 planet-in-sign rules | Education, learning, knowledge |

**Total new rules: ~342**

---

### 3.2 D9 Navamsha Spouse Interpretation
**File:** `packages/core/src/knowledge/rules/navamsha_spouse_rules.json` (NEW)

**Content needed:**
- 7th lord of D9 in each of 12 signs → spouse nature (84 rules)
- Venus in D9 signs → spouse appearance/qualities for male charts (12 rules)
- Jupiter in D9 signs → spouse appearance/qualities for female charts (12 rules)
- D9 Lagna in each sign → marriage quality (12 rules)
- Planets in 7th house of D9 → spouse characteristics (9 rules)
- Upapada cross-reference rules (12 rules)

**Total: ~141 interpretation rules**

---

### 3.3 Ashtakavarga Transit Prediction Rules
**File:** `packages/core/src/knowledge/rules/ashtakavarga_transit_rules.json` (NEW)

**Content:**
- SAV score thresholds for transit predictions (bindu ranges 0-56)
- BAV score interpretation for each planet in each sign
- Transit prediction modifiers based on bindu count
- Kaksha-level transit effects (8 sub-divisions per sign)

**Total: ~100 rules**

---

### 3.4 Remedies Recommendation Engine
**File:** `packages/self/src/remedies.py` (NEW)
**Rules:** `packages/core/src/knowledge/rules/remedies_rules.json` (already exists, needs engine)

```python
def recommend_remedies(
    current_dasha: dict,       # active MD/AD/PD
    active_doshas: list[dict], # detected doshas
    weak_planets: list[dict],  # planets with low Shadbala
    current_transits: dict,    # for transit-based remedies
    lagna_rashi: str
) -> dict:
    """
    Returns prioritized remedy recommendations:
    {
        "urgent": [
            {"planet": "saturn", "remedy_type": "mantra", "remedy": "Om Sham Shanicharaya Namah", "frequency": "108 times on Saturdays", "reason": "Sade Sati active"}
        ],
        "recommended": [
            {"planet": "mars", "remedy_type": "gemstone", "remedy": "Red Coral", "finger": "ring finger", "reason": "Mars debilitated in 10th - career struggles"}
        ],
        "optional": [...]
    }
    """
```

**Test count target:** 15+ tests

---

## Agent 4: WIRING (After Agents 1-3 Complete)

### 4.1 New MCP Tools

Add to the appropriate MCP servers:

**patterns_server.py (6 new tools):**
```python
@mcp.tool()
async def check_yoga_cancellations(planets, lagna_rashi, sun_longitude) -> dict
@mcp.tool()
async def detect_neecha_bhanga(planet, planet_data, all_planets, lagna_rashi, d9_positions) -> dict
@mcp.tool()
async def detect_planetary_wars(planets) -> list
@mcp.tool()
async def bhava_chalit_chart(planets, cusps, ascendant) -> dict
@mcp.tool()
async def recommend_remedies(current_dasha, active_doshas, weak_planets, lagna_rashi) -> dict
@mcp.tool()
async def navamsha_spouse_analysis(d9_planets, d9_lagna, gender) -> dict
```

**context_server.py (4 new tools):**
```python
@mcp.tool()
async def dasha_transit_cross_analysis(natal_planets, current_transits, current_dasha, lagna_rashi, moon_rashi) -> dict
@mcp.tool()
async def transit_natal_aspects(natal_planets, transit_planets, orb) -> list
@mcp.tool()
async def correlate_life_event(event_date, event_type, birth_datetime, natal_planets, moon_longitude, lagna_rashi, lat, lon) -> dict
@mcp.tool()
async def upcoming_transit_triggers(natal_planets, lagna_rashi, moon_rashi, days_ahead, lat, lon) -> list
```

### 4.2 New API Endpoints

**services/api/main.py:**
```python
# Pattern upgrades
POST /api/v1/analysis/yoga-cancellations
POST /api/v1/analysis/neecha-bhanga
POST /api/v1/analysis/planetary-wars
POST /api/v1/analysis/bhava-chalit
POST /api/v1/analysis/navamsha-spouse
POST /api/v1/analysis/remedies

# Timing upgrades
POST /api/v1/timing/dasha-transit
POST /api/v1/timing/transit-aspects
POST /api/v1/timing/event-correlation
POST /api/v1/timing/upcoming-triggers
GET  /api/v1/timing/varshaphal-current
```

### 4.3 Guide Agent Wiring

**packages/guide/src/tools.py — add:**
```python
def check_yoga_cancellations(self, ...) -> dict
def get_neecha_bhanga(self, ...) -> dict
def get_dasha_transit_analysis(self, ...) -> dict
def get_upcoming_triggers(self, ...) -> list
def correlate_event(self, ...) -> dict
def get_remedies(self, ...) -> dict
def get_navamsha_spouse(self, ...) -> dict
```

**packages/guide/src/agent.py — extend:**
- `analyze` node: call yoga cancellation after yoga detection
- `predict` node: call dasha-transit cross-analysis + upcoming triggers
- `calculate` node: add Bhava Chalit calculation
- New intent type: `"event_correlation"` → route to correlate_event
- New intent type: `"remedy"` → route to recommend_remedies (currently goes to general)

### 4.4 Memory Schema Extensions

**Why:** The memory system (PostgreSQL + pgvector) already stores birth charts, yogas, doshas, dashas, predictions, and conversations. But it does NOT store computed analysis results, event history, or remedy tracking. The new features need these.

**File:** `packages/memory/src/store.py` — extend with new tables/methods

**New tables to add:**

```sql
-- Store user-reported life events (for Event Correlation Engine)
CREATE TABLE life_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    event_date TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL,           -- career, marriage, health, money, education, travel, loss
    description TEXT NOT NULL,
    correlation_result JSONB,           -- output from event_correlator.py
    correlation_score FLOAT,
    dasha_at_event JSONB,              -- {mahadasha, antardasha, pratyantardasha}
    transits_at_event JSONB,           -- transit positions at event time
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cache computed analysis results (avoid recalculation)
CREATE TABLE analysis_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    analysis_type TEXT NOT NULL,        -- ashtakavarga, bhava_bala, shadbala, vimshopaka, transit_aspects
    result JSONB NOT NULL,
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,            -- NULL = never expires (natal), set for transits
    UNIQUE(user_id, analysis_type)
);

-- Track recommended remedies and user follow-up
CREATE TABLE remedy_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    planet TEXT NOT NULL,
    remedy_type TEXT NOT NULL,          -- mantra, gemstone, donation, fasting, pooja
    remedy TEXT NOT NULL,
    reason TEXT NOT NULL,
    priority TEXT NOT NULL,             -- urgent, recommended, optional
    recommended_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'suggested',    -- suggested, accepted, practicing, completed, skipped
    user_feedback TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily transit cache (avoid recalculating for same day)
CREATE TABLE transit_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_date DATE NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    positions JSONB NOT NULL,           -- all 9 planet positions
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(cache_date, latitude, longitude)
);
```

**New methods to add to MemoryStore:**

```python
# Life Events
async def save_life_event(self, user_id, event_date, event_type, description, correlation_result=None) -> str
async def get_life_events(self, user_id, event_type=None, limit=50) -> list
async def update_event_correlation(self, event_id, correlation_result, correlation_score) -> bool

# Analysis Cache
async def cache_analysis(self, user_id, analysis_type, result, expires_hours=None) -> str
async def get_cached_analysis(self, user_id, analysis_type) -> dict | None
async def invalidate_analysis_cache(self, user_id, analysis_type=None) -> int

# Remedy Tracking
async def save_remedy(self, user_id, planet, remedy_type, remedy, reason, priority) -> str
async def get_active_remedies(self, user_id) -> list
async def update_remedy_status(self, remedy_id, status, feedback=None) -> bool

# Transit Cache
async def cache_transits(self, date, latitude, longitude, positions) -> str
async def get_cached_transits(self, date, latitude, longitude) -> dict | None
```

**Extend UnifiedMemoryClient** (`packages/memory/src/unified_memory.py`):
```python
# Add convenience methods
async def remember_life_event(self, user_id, event_date, event_type, description) -> str
async def remember_remedy(self, user_id, planet, remedy_type, remedy, reason, priority) -> str
async def get_user_events(self, user_id) -> list
async def get_user_remedies(self, user_id) -> list
```

**Wire into Guide Agent** (`packages/guide/src/agent.py`):

1. **`_save_memory` node — extend:**
   - After event_correlation intent → save event to `life_events`
   - After remedy intent → save remedies to `remedy_tracking`
   - After analysis → cache results in `analysis_cache`

2. **`_check_memory` node — extend:**
   - Load cached analysis results before recalculating
   - Load active remedies for context
   - Load past events for correlation context

3. **`_load_context` node — extend:**
   - Check transit cache before calling ephemeris
   - Load analysis cache for natal results

**Test count target:** 15+ tests for memory extensions

### 4.5 Integration Tests

**tests/integration/test_new_features.py:**
- End-to-end: birth data → yoga detection → cancellation check → final yoga list
- End-to-end: birth data → dasha + transits → cross-analysis → triggers
- End-to-end: birth data + event → correlation → score
- End-to-end: birth data → doshas + dashas → remedies

**Test count target:** 20+ tests

---

## Summary: What Gets Built

| # | Feature | Agent | Package | New Tests |
|---|---------|-------|---------|-----------|
| 1 | Yoga cancellation engine | 1-SELF | `self/yoga_cancellation.py` | 25 |
| 2 | Neecha Bhanga detection | 1-SELF | `self/yoga_detector.py` | 15 |
| 3 | Planetary War | 1-SELF | `self/planetary_war.py` | 12 |
| 4 | Bhava Chalit chart | 1-SELF | `cosmos/bhava_chalit.py` | 10 |
| 5 | Dasha-Transit cross-analysis | 2-CONTEXT | `context/dasha_transit.py` | 30 |
| 6 | Transit-natal aspects | 2-CONTEXT | `context/transit_aspects.py` | 20 |
| 7 | Event correlation | 2-CONTEXT | `context/event_correlator.py` | 15 |
| 8 | Transit trigger tracker | 2-CONTEXT | `context/transit_tracker.py` | 20 |
| 9 | Varshaphal current year | 2-CONTEXT | `context/varshaphal.py` | 10 |
| 10 | D2/D4/D7/D24 interpretations | 3-KNOWLEDGE | `knowledge/rules/*.json` | 15 |
| 11 | D9 spouse rules | 3-KNOWLEDGE | `knowledge/rules/navamsha_spouse.json` | 10 |
| 12 | Ashtakavarga transit rules | 3-KNOWLEDGE | `knowledge/rules/ashtakavarga_transit.json` | 8 |
| 13 | Remedies engine | 3-KNOWLEDGE | `self/remedies.py` | 15 |
| 14 | 10 MCP tools | 4-WIRING | `services/mcp/*.py` | 10 |
| 15 | 11 API endpoints | 4-WIRING | `services/api/main.py` | 11 |
| 16 | Guide agent wiring | 4-WIRING | `packages/guide/src/*.py` | 10 |
| 17 | Memory schema extensions | 4-WIRING | `packages/memory/src/store.py` | 15 |
| 18 | Memory → Guide integration | 4-WIRING | `packages/guide/src/agent.py` + `unified_memory.py` | 10 |
| 19 | Integration tests | 4-WIRING | `tests/integration/` | 20 |
| | **TOTAL** | | | **~291** |

**After completion, update `docs/system_map.md`** — change all ❌ and ⚠️ to ✅ for completed items.

---

## Current Architecture: What Already Exists (Don't Rebuild)

### Guide Agent (LangGraph — ALREADY BUILT)
**File:** `packages/guide/src/agent.py` (~1100 lines)
- 9-node state machine: classify_intent → load_context → check_memory → [route] → interpret → save_memory
- Intent classification: 10 types (calculate, analyze, predict, dasha, transit, timing, remedy, personal, general, unknown)
- Personality adaptation: 12 zodiac-based communication styles
- ConversationManager: 20-turn history with auto-pruning
- ChartCache: birth chart caching by user_id

### Memory Store (PostgreSQL + pgvector — ALREADY BUILT)
**File:** `packages/memory/src/store.py` (~1550 lines)
- 8 tables: memories, users, birth_charts, detected_patterns, predictions, conversations, user_preferences, dasha_timeline
- Embedding: Voyage (1024d) / OpenAI (1536d) / Local (384d) / Mock
- Semantic search via cosine distance
- Full CRUD for all tables

### Agent Tools (ALREADY BUILT)
**File:** `packages/guide/src/tools.py`
- 50+ wrapped functions across all packages
- get_birth_chart, get_dasha_info, get_transit_analysis, detect_yogas, detect_doshas, get_planet_strength, check_muhurta, etc.

### API Chat Endpoint (ALREADY BUILT)
**File:** `services/api/main.py`
- POST /api/v1/chat — lazy-initializes Guide, loads birth chart from memory, returns response with metadata

**IMPORTANT:** Agent 4 (WIRING) extends these existing files. It does NOT create new agent infrastructure. The guide is a single LangGraph agent, not a multi-agent team. The memory store is a single PostgreSQL database. Keep it simple.

---

## Execution Instructions for Claude Code

```bash
# STEP 1: Read this spec
# Read docs/project_notes/claude_code_task_spec.md

# STEP 2: Run agents 1, 2, 3 in parallel
# Agent 1 (SELF): packages/self/ + packages/cosmos/bhava_chalit.py
# Agent 2 (CONTEXT): packages/context/
# Agent 3 (KNOWLEDGE): packages/core/src/knowledge/ + packages/self/remedies.py

# STEP 3: After all 3 complete, run Agent 4 (WIRING):
# Agent 4: services/mcp/ + services/api/ + packages/guide/ + packages/memory/ + tests/integration/

# STEP 4: Verify
uv run ruff check .
uv run ruff format .
uv run pytest

# STEP 5: Commit
# feat: Add yoga cancellation, dasha-transit engine, transit tracker, remedies, Neecha Bhanga, planetary war, Bhava Chalit, event correlation, memory extensions, D2/D4/D7/D24 interpretations, Navamsha spouse rules
```

---

*Generated: Feb 6, 2026 | For Claude Code Session 21*
