# 108 — Claude Code Task Spec (Session 22)
## Synastry, Gem Engine, Atmakaraka Deep Analysis, Daily/Weekly/Monthly Forecasts

> **Context:** 108 is a Vedic Jyotish engine with ~69 MCP tools, 522 yogas, 55 doshas, 1,653 tests.
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
│ (patterns)   │ (forecasts)      │ (interpretations)          │
│              │                  │                            │
│ • Synastry   │ • Daily Forecast │ • Atmakaraka interp rules  │
│   & Composite│   Engine         │ • Synastry interp rules    │
│ • Gem Recomm │ • Weekly Forecast│ • Gem prescription rules   │
│   Engine     │   Engine         │                            │
│ • Atmakaraka │ • Monthly        │                            │
│   Deep       │   Forecast       │                            │
│   Analysis   │   Engine         │                            │
├──────────────┴──────────────────┴────────────────────────────┤
│                     RUN AFTER ALL 3 COMPLETE                 │
├──────────────────────────────────────────────────────────────┤
│ Agent 4: WIRING                                              │
│ • MCP tools for all new features                             │
│ • API endpoints for all new features                         │
│ • Guide agent wiring (tools.py + agent.py)                   │
│ • Integration tests                                          │
│ • Update system_map.md                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## Agent 1: SELF (Pattern Detection — Synastry + Gems + Atmakaraka)

### 1.1 Synastry & Composite Chart Analysis
**File:** `packages/self/src/synastry.py` (NEW)
**Tests:** `tests/unit/test_synastry.py` (NEW)

**What it does:** Relationship analysis BEYOND Ashta Kuta. Overlays two charts and analyzes cross-aspects, house overlays, and midpoint composites.

**Three analysis modes:**

1. **House Overlay** — Place partner's planets in native's house framework
2. **Cross-Chart Aspects** — Find aspects between one person's planets and another's
3. **Composite Chart** — Calculate midpoints of both charts for relationship chart

**Function signatures:**
```python
def calculate_house_overlay(
    native_planets: dict,       # person 1's birth chart
    native_cusps: list[float],  # person 1's house cusps (12 floats)
    partner_planets: dict,      # person 2's birth chart
) -> list[dict]:
    """
    Place partner's planets in native's houses.
    Returns:
    [
        {
            "partner_planet": "venus",
            "partner_longitude": 245.3,
            "native_house": 7,
            "interpretation": "Partner's Venus in your 7th house — strong romantic attraction",
            "significance": "very_high"
        }
    ]
    """

def calculate_cross_aspects(
    native_planets: dict,       # {planet: {longitude, ...}}
    partner_planets: dict,
    orb: float = 8.0           # wider orb for synastry
) -> list[dict]:
    """
    Find all aspects between charts.
    Returns:
    [
        {
            "native_planet": "moon",
            "partner_planet": "venus",
            "aspect_type": "conjunction",
            "exact_degree": 0,
            "orb": 2.3,
            "quality": "harmonious",
            "interpretation": "Deep emotional-romantic connection"
        }
    ]
    """

def calculate_composite_chart(
    native_planets: dict,
    partner_planets: dict,
    native_ascendant: float,
    partner_ascendant: float
) -> dict:
    """
    Midpoints of both charts = the relationship's own chart.
    Returns:
    {
        "composite_planets": {planet: {longitude, sign, house}},
        "composite_ascendant": float,
        "relationship_themes": [...],
        "strengths": [...],
        "challenges": [...]
    }
    """

def get_synastry_report(
    native_planets: dict,
    native_cusps: list[float],
    partner_planets: dict,
    partner_cusps: list[float],
    native_ascendant: float,
    partner_ascendant: float,
    native_moon_nakshatra: int,  # for ashta kuta
    partner_moon_nakshatra: int
) -> dict:
    """Full synastry report combining all 3 modes + ashta kuta."""
```

**Rules:**
- Standard Ptolemaic aspects: conjunction (0°), sextile (60°), square (90°), trine (120°), opposition (180°)
- Wider orbs for synastry (8° for luminaries, 6° for other planets)
- Composite midpoint: `(lon1 + lon2) / 2` (handle 360° wraparound)
- Import `calculate_ashta_kuta` from compatibility module — include in full report
- Use knowledge rules from `synastry_rules.json` for interpretations

**Test count target:** 30+ tests

---

### 1.2 Gem Recommendation Engine
**File:** `packages/self/src/gem_recommender.py` (NEW)
**Tests:** `tests/unit/test_gem_recommender.py` (NEW)

**What it does:** Prescribe gems based on Lagna, weak planets, current dasha, and contraindications. Uses data from `knowledge/rules/remedies_rules.json` (gemstone section) + new `gem_prescription_rules.json`.

**Key Jyotish Rules for Gem Prescription:**
- Gems STRENGTHEN a planet — only wear gems for BENEFIC planets for your Lagna
- NEVER wear gems for functional malefics (6th, 8th, 12th lords)
- Yoga Karaka planet's gem is ALWAYS beneficial
- Dasha lord's gem amplifies current period
- Lagna lord's gem is universally beneficial
- Gems for natural malefics (Saturn, Mars, Rahu, Ketu) need careful consideration

```python
def recommend_gems(
    lagna_rashi: str,           # ascendant sign
    planets: dict,              # birth chart planets with houses
    shadbala: dict | None = None,  # optional strength scores
    current_dasha: dict | None = None,  # optional dasha info
    active_doshas: list[dict] | None = None  # optional dosha list
) -> dict:
    """
    Returns:
    {
        "primary_gem": {
            "planet": "saturn",
            "gem": "blue_sapphire",
            "reason": "Yoga Karaka for Libra Lagna — 4th+5th lord",
            "finger": "middle",
            "metal": "gold/silver",
            "minimum_carat": 3,
            "wearing_day": "saturday",
            "caution": "Try for 3 days first (Saturn gems can be intense)"
        },
        "secondary_gems": [...],
        "dasha_gem": {
            "planet": "mercury",
            "gem": "emerald",
            "reason": "Current Mercury Mahadasha lord — amplifies period",
            ...
        },
        "contraindicated": [
            {
                "planet": "mars",
                "gem": "red_coral",
                "reason": "Mars is 2nd+7th lord (Maraka) for Libra Lagna — gem may intensify health risks"
            }
        ],
        "general_advice": "For Libra Lagna, Saturn (Blue Sapphire) and Venus (Diamond) are most beneficial..."
    }
    """

def get_lagna_gem_map(lagna_rashi: str) -> dict:
    """Get beneficial/neutral/harmful gem classification for a specific Lagna."""

def check_gem_compatibility(
    gem_planet: str,
    lagna_rashi: str,
    planets: dict
) -> dict:
    """Check if a specific gem is safe to wear for this chart."""
```

**Lagna-wise Gem Rules (examples):**
- Libra Lagna: Saturn (Blue Sapphire) = Yoga Karaka gem ✅, Mars (Red Coral) = Maraka ❌
- Aries Lagna: Sun (Ruby) = 5th lord ✅, Saturn (Blue Sapphire) = 10th+11th lord, caution ⚠️
- Cancer Lagna: Mars (Red Coral) = Yoga Karaka ✅, Saturn (Blue Sapphire) = 7th+8th lord ❌

**Test count target:** 25+ tests

---

### 1.3 Atmakaraka Deep Analysis
**File:** `packages/self/src/jaimini.py` (EXTEND existing)
**Tests:** `tests/unit/test_atmakaraka_analysis.py` (NEW)

**What it does:** Extend the existing `get_karakamsha()` to provide a full soul-purpose narrative. Add Ishta Devata detection (12th from Karakamsha) and detailed Karakamsha analysis.

**Existing functions (DON'T MODIFY):**
- `get_atmakaraka(chart)` → returns CharaKarakaResult
- `get_karakamsha(chart)` → returns KarakamshaResult (sign + basic interp)

**New functions to ADD:**
```python
def get_atmakaraka_analysis(chart: BirthChart) -> dict:
    """
    Comprehensive Atmakaraka-based life purpose analysis.
    Returns:
    {
        "atmakaraka": {"planet": "venus", "degree": 29.8, "sign": "sagittarius"},
        "karakamsha": {"sign": "pisces", "house_from_lagna": 6},
        "soul_purpose": "Spiritual liberation through service — Venus as AK in Pisces Karakamsha...",
        "ishta_devata": {
            "sign_12th_from_km": "aquarius",
            "planet_in_12th": "saturn",
            "deity": "Lord Shani / Hanuman",
            "interpretation": "Devotion to Saturn-related deities for spiritual progress"
        },
        "planets_in_karakamsha": [
            {"planet": "jupiter", "effect": "Guru in Karakamsha — natural teacher, spiritual guide"}
        ],
        "planets_aspecting_karakamsha": [
            {"planet": "mars", "effect": "Mars aspects KM — driven, passionate pursuit of dharma"}
        ],
        "career_from_karakamsha": "Service-oriented profession, healing, charity work",
        "spiritual_path": "Bhakti yoga, devotional practices, selfless service"
    }
    """

def get_ishta_devata(chart: BirthChart) -> dict:
    """
    Determine the preferred deity from 12th sign from Karakamsha.
    The planet ruling/occupying the 12th from KM indicates the Ishta Devata.
    Returns: {sign, planet, deity, interpretation}
    """

def get_all_chara_karaka_analysis(chart: BirthChart) -> dict:
    """
    Full 7-karaka analysis: AK through DK with house positions and interpretations.
    Returns detailed analysis for each of the 7 Chara Karakas.
    """
```

**Rules for Ishta Devata (12th from Karakamsha):**
| Planet in 12th from KM | Ishta Devata |
|------------------------|--------------|
| Sun | Lord Shiva, Surya |
| Moon | Goddess Parvati, Durga |
| Mars | Lord Kartikeya (Skanda), Hanuman |
| Mercury | Lord Vishnu |
| Jupiter | Lord Vishnu, Dakshinamurthy |
| Venus | Goddess Lakshmi, Mahalakshmi |
| Saturn | Lord Shani, Hanuman, Vishnu |
| Rahu | Goddess Durga, Sarpa Devata |
| Ketu | Lord Ganesha, Matsya Avatar |

**Test count target:** 20+ tests

---

## Agent 2: CONTEXT (Forecast Engines)

### 2.1 Daily Forecast Engine
**File:** `packages/context/src/daily_forecast.py` (NEW)
**Tests:** `tests/unit/test_daily_forecast.py` (NEW)

**What it does:** Generate a comprehensive daily forecast by combining ALL available timing tools. This is the "Today's energy" feature.

**Data sources to combine:**
1. Panchanga (tithi, vara, yoga, karana, nakshatra) — from `packages/cosmos/src/panchanga.py`
2. Transit Moon position (sign, house from natal Moon, nakshatra) — from ephemeris
3. Choghadiya periods — from `packages/context/src/muhurta.py`
4. Rahu Kaal / Yamaghanda / Gulika — from muhurta
5. Ashtakavarga score for Moon's current sign — from `packages/self/src/ashtakavarga.py`
6. Current dasha (MD/AD/PD) — from `packages/context/src/dasha.py`
7. Transit aspects active today — from `packages/context/src/transit_aspects.py`
8. Any sign ingresses today — from transit_tracker

```python
def get_daily_forecast(
    birth_datetime: str,        # ISO format
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict,        # birth chart positions
    moon_longitude: float,      # natal moon for house counting
    lagna_rashi: str,
    query_date: str | None = None,  # defaults to today
    location_lat: float | None = None,  # current location (for panchanga)
    location_lon: float | None = None
) -> dict:
    """
    Returns:
    {
        "date": "2026-02-07",
        "day_rating": 7,         # 1-10 overall
        "summary": "A generally positive day with Moon in Gemini activating your 9th house...",
        "panchanga": {
            "tithi": "Shukla Dashami",
            "vara": "Saturday",
            "yoga": "Siddha",
            "karana": "Taitila",
            "nakshatra": "Punarvasu"
        },
        "moon_transit": {
            "sign": "gemini",
            "house_from_lagna": 9,
            "house_from_moon": 5,
            "nakshatra": "punarvasu",
            "ashtakavarga_score": 5,   # 0-8 BAV for Moon in this sign
            "quality": "favorable"
        },
        "active_dasha": {
            "mahadasha": "mercury",
            "antardasha": "ketu",
            "pratyantardasha": "venus",
            "theme": "Intellect meets detachment, with comfort seeking"
        },
        "transit_aspects_today": [
            {"transit": "jupiter", "natal": "saturn", "aspect": "trine", "orb": 1.2, "effect": "..."}
        ],
        "inauspicious_periods": {
            "rahu_kaal": {"start": "09:00", "end": "10:30"},
            "yamaghanda": {"start": "13:30", "end": "15:00"},
            "gulika": {"start": "06:00", "end": "07:30"}
        },
        "choghadiya_highlights": {
            "best_periods": [{"name": "Labh", "start": "10:30", "end": "12:00", "quality": "gain"}],
            "avoid_periods": [{"name": "Rog", "start": "15:00", "end": "16:30", "quality": "disease"}]
        },
        "recommendations": {
            "best_for": ["education", "travel", "spiritual"],
            "avoid": ["surgery", "legal"],
            "tip": "Moon in 9th + Saturday = good for disciplined spiritual practice"
        }
    }
    """
```

**Important implementation notes:**
- Use `get_panchanga()` from cosmos for tithi/vara/yoga/karana
- Use `get_planet_position()` from cosmos for current Moon position
- Use `calculate_choghadiya()` and `calculate_rahu_kaal()` from muhurta
- Use `get_transit_natal_aspects()` from transit_aspects for today's aspects
- Use `get_transit_ashtakavarga_score()` from ashtakavarga for Moon's BAV
- Use `get_current_dasha()` from dasha for active period
- Day rating algorithm: weighted sum of panchanga quality + moon BAV + aspect quality + dasha nature

**Test count target:** 25+ tests

---

### 2.2 Weekly Forecast Engine
**File:** `packages/context/src/weekly_forecast.py` (NEW)
**Tests:** `tests/unit/test_weekly_forecast.py` (NEW)

**What it does:** 7-day forecast with daily snapshots, weekly themes, peak days, and key transit events.

```python
def get_weekly_forecast(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict,
    moon_longitude: float,
    lagna_rashi: str,
    start_date: str | None = None,  # defaults to today
    location_lat: float | None = None,
    location_lon: float | None = None
) -> dict:
    """
    Returns:
    {
        "week_start": "2026-02-07",
        "week_end": "2026-02-13",
        "overall_rating": 6.5,       # average of daily ratings
        "weekly_theme": "Career expansion meets spiritual introspection",
        "peak_days": ["2026-02-10", "2026-02-12"],
        "challenging_days": ["2026-02-08"],
        "daily_forecasts": [
            {... daily forecast for each of 7 days ...}
        ],
        "key_transits_this_week": [
            {"date": "2026-02-10", "event": "Venus enters Pisces (exalted)", "impact": "very_positive"},
            {"date": "2026-02-12", "event": "Mercury conjuncts natal Jupiter", "impact": "positive"}
        ],
        "dasha_context": {
            "period": "Mercury-Ketu-Venus",
            "week_theme": "Dasha lords favor intellectual and creative pursuits"
        },
        "areas": {
            "career": {"rating": 7, "summary": "Good progress mid-week"},
            "finance": {"rating": 6, "summary": "Steady, avoid speculation on Saturday"},
            "relationships": {"rating": 5, "summary": "Communication gaps possible"},
            "health": {"rating": 7, "summary": "Energy levels moderate to high"},
            "spiritual": {"rating": 8, "summary": "Excellent for meditation and study"}
        }
    }
    """
```

**Implementation notes:**
- Call `get_daily_forecast()` for each of 7 days
- Use `find_upcoming_aspects()` for transit events this week
- Use `get_upcoming_triggers()` for ingresses/stations
- Aggregate daily ratings for weekly summary
- Identify peak/challenging days from daily ratings
- Area ratings: derive from house activations + dasha themes

**Test count target:** 20+ tests

---

### 2.3 Monthly Forecast Engine
**File:** `packages/context/src/monthly_forecast.py` (NEW)
**Tests:** `tests/unit/test_monthly_forecast.py` (NEW)

**What it does:** Month-long forecast with major transits, dasha transitions, area-wise analysis, and key dates.

```python
def get_monthly_forecast(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict,
    moon_longitude: float,
    lagna_rashi: str,
    month: int | None = None,      # 1-12, defaults to current
    year: int | None = None,       # defaults to current
    location_lat: float | None = None,
    location_lon: float | None = None
) -> dict:
    """
    Returns:
    {
        "month": "February",
        "year": 2026,
        "overall_rating": 6.8,
        "monthly_theme": "Financial expansion through career gains, with spiritual undertones",
        "dasha_context": {
            "mahadasha": "mercury",
            "antardasha": "ketu",
            "transitions": [
                {"date": "2026-02-18", "from": "Mercury-Ketu-Venus", "to": "Mercury-Ketu-Sun"}
            ]
        },
        "major_transits": [
            {
                "date": "2026-02-13",
                "event": "Sun enters Aquarius",
                "house": 5,
                "duration_days": 30,
                "effect": "11th lord in 5th — speculation gains, creative income"
            }
        ],
        "retrograde_status": {
            "planets_retrograde": ["mercury"],
            "dates": {"mercury": {"start": "2026-02-14", "end": "2026-03-06"}},
            "impact": "Mercury retrograde as your Mahadasha lord — communication delays"
        },
        "areas": {
            "career": {
                "rating": 7,
                "best_dates": ["2026-02-10", "2026-02-15", "2026-02-24"],
                "avoid_dates": ["2026-02-14"],
                "summary": "Strong mid-month. Avoid decisions during Mercury Rx start."
            },
            "finance": { ... },
            "relationships": { ... },
            "health": { ... },
            "spiritual": { ... }
        },
        "weekly_summaries": [
            {"week": 1, "dates": "Feb 1-7", "rating": 6, "theme": "Settling in"},
            {"week": 2, "dates": "Feb 8-14", "rating": 7, "theme": "Peak activity"},
            {"week": 3, "dates": "Feb 15-21", "rating": 5, "theme": "Mercury Rx caution"},
            {"week": 4, "dates": "Feb 22-28", "rating": 8, "theme": "Strong culmination"}
        ],
        "best_dates": {
            "career_moves": ["2026-02-10", "2026-02-24"],
            "financial": ["2026-02-15"],
            "travel": ["2026-02-12"],
            "spiritual": ["2026-02-20"],
            "avoid_important": ["2026-02-14", "2026-02-22"]
        }
    }
    """
```

**Implementation notes:**
- Use `find_upcoming_aspects(days_ahead=31)` for the month's transit aspects
- Use `get_upcoming_triggers(days_ahead=31)` for ingresses/stations
- Use `cross_analyze()` for dasha-transit activation scoring
- Use `get_dasha_periods_for_year()` to find dasha transitions in the month
- Weekly summaries: call `get_weekly_forecast()` for 4 weeks (or calculate lightweight summaries)
- Area ratings: aggregate transit effects by house rulership
- Retrograde detection: check planet speeds (negative = retrograde) from ephemeris

**Test count target:** 20+ tests

---

## Agent 3: KNOWLEDGE (Interpretation Data)

### 3.1 Atmakaraka Interpretation Rules
**File:** `knowledge/rules/atmakaraka_rules.json` (NEW)
**Tests:** `tests/unit/test_atmakaraka_rules.py` (NEW)

**Structure:**
```json
{
    "atmakaraka_rules": {
        "ak_by_planet": {
            "sun": {
                "soul_lesson": "Ego dissolution, true leadership through humility",
                "karmic_focus": "Authority, father, self-identity",
                "spiritual_path": "Raja Yoga, leadership in service"
            },
            "moon": { ... },
            ...  // 9 planets
        },
        "karakamsha_by_sign": {
            "aries": {
                "soul_purpose": "Pioneer, warrior of dharma, initiative",
                "career_direction": "Military, sports, engineering, surgery",
                "spiritual_expression": "Tapas (austerity), active meditation"
            },
            ... // 12 signs
        },
        "planets_in_karakamsha": {
            "sun": "Authority and power in soul's path, government connection",
            "moon": "Emotional fulfillment through soul purpose, public service",
            ... // 9 planets
        },
        "planets_aspecting_karakamsha": {
            "sun": "Soul purpose backed by authority and confidence",
            ... // 9 planets
        },
        "ishta_devata": {
            "sun": {"deity": "Lord Shiva / Surya", "worship": "Surya Namaskar, Aditya Hridayam"},
            "moon": {"deity": "Goddess Parvati / Durga", "worship": "Chandi Path, Lalita Sahasranama"},
            "mars": {"deity": "Lord Kartikeya / Hanuman", "worship": "Hanuman Chalisa, Mars mantras"},
            "mercury": {"deity": "Lord Vishnu", "worship": "Vishnu Sahasranama, Narayana mantras"},
            "jupiter": {"deity": "Lord Vishnu / Dakshinamurthy", "worship": "Guru mantras, Brihaspati Stotra"},
            "venus": {"deity": "Goddess Lakshmi / Mahalakshmi", "worship": "Sri Suktam, Lakshmi Stotra"},
            "saturn": {"deity": "Lord Shani / Hanuman / Vishnu", "worship": "Shani Stotra, Hanuman Chalisa"},
            "rahu": {"deity": "Goddess Durga / Sarpa Devata", "worship": "Durga Saptashati, Naga Puja"},
            "ketu": {"deity": "Lord Ganesha / Matsya Avatar", "worship": "Ganesha Atharvashirsha, fish charity"}
        },
        "ishta_devata_by_sign": {
            "aries": {"deity": "Lord Kartikeya", "element": "fire", "worship": "Skanda Shashthi"},
            ... // 12 signs
        }
    }
}
```

**Total rules: ~66** (9 AK by planet + 12 KM by sign + 9 planets in KM + 9 planets aspecting KM + 9 ishta devata by planet + 12 ishta devata by sign + 6 special combos)

**Test count target:** 15+ tests

---

### 3.2 Synastry Interpretation Rules
**File:** `knowledge/rules/synastry_rules.json` (NEW)
**Tests:** `tests/unit/test_synastry_rules.py` (NEW)

**Structure:**
```json
{
    "synastry_rules": {
        "cross_aspects": {
            "sun_moon": {
                "conjunction": {"quality": "very_harmonious", "interpretation": "Core identity meets emotional nature — deep soul recognition"},
                "trine": {"quality": "harmonious", "interpretation": "Natural understanding between ego and emotions"},
                "square": {"quality": "challenging", "interpretation": "Tension between will and feelings"},
                "opposition": {"quality": "complex", "interpretation": "Magnetic attraction with identity clashes"},
                "sextile": {"quality": "harmonious", "interpretation": "Gentle support between identity and feelings"}
            },
            "sun_venus": { ... },
            "sun_mars": { ... },
            "moon_venus": { ... },
            "moon_mars": { ... },
            "venus_mars": { ... },
            "sun_saturn": { ... },
            "moon_saturn": { ... },
            "venus_jupiter": { ... },
            "mars_saturn": { ... }
            // ~10 key planet pairs × 5 aspects = 50 rules
        },
        "house_overlay": {
            "sun": {
                "1": "Partner's Sun in your 1st — they energize your identity",
                "2": "Partner's Sun in your 2nd — they boost your wealth/confidence",
                ...  // 12 houses
            },
            "moon": { ... },
            "venus": { ... },
            "mars": { ... },
            "jupiter": { ... },
            "saturn": { ... }
            // 6 key planets × 12 houses = 72 rules
        },
        "composite_planets_in_signs": {
            "sun": {
                "aries": "Dynamic, action-oriented relationship",
                ... // 12 signs
            },
            ... // 7 planets × 12 signs = 84 rules
        }
    }
}
```

**Total rules: ~206** (50 cross-aspect + 72 house overlay + 84 composite)

**Test count target:** 15+ tests

---

### 3.3 Gem Prescription Rules
**File:** `knowledge/rules/gem_prescription_rules.json` (NEW)
**Tests:** `tests/unit/test_gem_prescription_rules.py` (NEW)

**Structure:**
```json
{
    "gem_prescription_rules": {
        "lagna_wise": {
            "aries": {
                "yoga_karaka": null,
                "primary_benefic": ["sun", "jupiter", "mars"],
                "functional_malefic": ["saturn", "mercury"],
                "neutral": ["moon", "venus"],
                "best_gem": {"planet": "sun", "gem": "ruby", "reason": "5th lord — intelligence, speculation, children"},
                "secondary_gems": [
                    {"planet": "jupiter", "gem": "yellow_sapphire", "reason": "9th lord — fortune, dharma"}
                ],
                "avoid_gems": [
                    {"planet": "saturn", "gem": "blue_sapphire", "reason": "10th+11th lord — functional malefic"}
                ],
                "conditional": [
                    {"planet": "mars", "gem": "red_coral", "condition": "Only if Mars is weak in Shadbala or debilitated", "reason": "Lagna lord — self, body"}
                ]
            },
            "taurus": { ... },
            ... // 12 lagnas
        },
        "general_rules": [
            {"rule": "never_wear_enemy_gems", "description": "Sun and Saturn gems should not be worn together"},
            {"rule": "never_wear_enemy_gems", "description": "Moon and Rahu gems should not be worn together"},
            {"rule": "trial_period", "description": "Saturn, Rahu, Ketu gems should have 3-day trial before committing"},
            {"rule": "yoga_karaka_priority", "description": "Yoga Karaka planet's gem is always the #1 recommendation"},
            {"rule": "dasha_lord_gem", "description": "Current Mahadasha lord's gem amplifies the period (if benefic)"},
            {"rule": "weak_planet_gem", "description": "Gems for weak benefic planets help strengthen them"},
            {"rule": "no_malefic_gem", "description": "Don't strengthen functional malefics with gems"}
        ],
        "enemy_gem_pairs": [
            ["ruby", "blue_sapphire"],
            ["ruby", "hessonite"],
            ["pearl", "hessonite"],
            ["red_coral", "emerald"],
            ["red_coral", "diamond"],
            ["yellow_sapphire", "diamond"],
            ["yellow_sapphire", "emerald"]
        ]
    }
}
```

**Total rules: ~150** (12 lagnas × ~10 gem rules each + 10 general rules + 7 enemy pairs)

**Test count target:** 15+ tests

---

## Agent 4: WIRING (After Agents 1-3 Complete)

### 4.1 New MCP Tools

**patterns_server.py (4 new tools):**
```python
@mcp.tool()
async def synastry_analysis(native_planets, native_cusps, partner_planets, partner_cusps, native_asc, partner_asc) -> dict

@mcp.tool()
async def gem_recommendation(lagna_rashi, planets, shadbala, current_dasha) -> dict

@mcp.tool()
async def atmakaraka_analysis(birth_data) -> dict

@mcp.tool()
async def check_gem_compatibility(gem_planet, lagna_rashi, planets) -> dict
```

**context_server.py (3 new tools):**
```python
@mcp.tool()
async def daily_forecast(birth_datetime, birth_lat, birth_lon, natal_planets, moon_longitude, lagna_rashi, query_date) -> dict

@mcp.tool()
async def weekly_forecast(birth_datetime, birth_lat, birth_lon, natal_planets, moon_longitude, lagna_rashi, start_date) -> dict

@mcp.tool()
async def monthly_forecast(birth_datetime, birth_lat, birth_lon, natal_planets, moon_longitude, lagna_rashi, month, year) -> dict
```

### 4.2 New API Endpoints

**services/api/main.py:**
```python
# Pattern upgrades
POST /api/v1/analysis/synastry
POST /api/v1/analysis/gem-recommendation
POST /api/v1/analysis/atmakaraka
POST /api/v1/analysis/gem-compatibility

# Forecast engines
GET  /api/v1/forecast/daily
GET  /api/v1/forecast/weekly
GET  /api/v1/forecast/monthly
```

### 4.3 Guide Agent Wiring

**packages/guide/src/tools.py — add:**
```python
def get_synastry_report(self, ...) -> dict
def get_gem_recommendation(self, ...) -> dict
def get_atmakaraka_analysis(self, ...) -> dict
def get_daily_forecast(self, ...) -> dict
def get_weekly_forecast(self, ...) -> dict
def get_monthly_forecast(self, ...) -> dict
```

**packages/guide/src/agent.py — extend:**
- `analyze` node: add atmakaraka analysis option
- `predict` node: integrate daily/weekly/monthly forecasts
- New intent type: `"compatibility"` → route to synastry (currently just ashta kuta)
- New intent type: `"forecast"` → route to daily/weekly/monthly based on timeframe
- Enhance `"remedy"` intent: include gem recommendations

### 4.4 Integration Tests

**tests/integration/test_session22_features.py:**
- End-to-end: two birth charts → synastry report with ashta kuta + cross aspects + composite
- End-to-end: birth chart → gem recommendation based on Lagna + dasha
- End-to-end: birth chart → atmakaraka analysis → ishta devata
- End-to-end: birth chart → daily forecast with all components
- End-to-end: birth chart → weekly forecast with 7 daily snapshots
- End-to-end: birth chart → monthly forecast with area analysis

**Test count target:** 25+ tests

### 4.5 Update system_map.md

Update the "WHAT'S MISSING" section and stats footer:
- Mark Composite charts (synastry) as ✅
- Mark Gem recommendation engine as ✅
- Mark Atmakaraka deep analysis as ✅
- Mark all user-facing forecast features as ✅
- Update MCP tool count, test count, API endpoint count

---

## Summary: What Gets Built

| # | Feature | Agent | Package | New Tests |
|---|---------|-------|---------|-----------|
| 1 | Synastry & Composite Charts | 1-SELF | `self/synastry.py` | 30 |
| 2 | Gem Recommendation Engine | 1-SELF | `self/gem_recommender.py` | 25 |
| 3 | Atmakaraka Deep Analysis | 1-SELF | `self/jaimini.py` (extend) | 20 |
| 4 | Daily Forecast Engine | 2-CONTEXT | `context/daily_forecast.py` | 25 |
| 5 | Weekly Forecast Engine | 2-CONTEXT | `context/weekly_forecast.py` | 20 |
| 6 | Monthly Forecast Engine | 2-CONTEXT | `context/monthly_forecast.py` | 20 |
| 7 | Atmakaraka Interp Rules | 3-KNOWLEDGE | `knowledge/rules/atmakaraka_rules.json` | 15 |
| 8 | Synastry Interp Rules | 3-KNOWLEDGE | `knowledge/rules/synastry_rules.json` | 15 |
| 9 | Gem Prescription Rules | 3-KNOWLEDGE | `knowledge/rules/gem_prescription_rules.json` | 15 |
| 10 | 7 MCP tools | 4-WIRING | `services/mcp/*.py` | — |
| 11 | 7 API endpoints | 4-WIRING | `services/api/main.py` | — |
| 12 | Guide agent wiring | 4-WIRING | `packages/guide/src/*.py` | — |
| 13 | Integration tests | 4-WIRING | `tests/integration/` | 25 |
| | **TOTAL** | | | **~235** |

---

## Execution Instructions

```bash
# STEP 1: Read this spec
# Read docs/project_notes/session22_task_spec.md

# STEP 2: Run agents 1, 2, 3 in parallel
# Agent 1 (SELF): packages/self/src/synastry.py + gem_recommender.py + jaimini.py extension
# Agent 2 (CONTEXT): packages/context/src/daily_forecast.py + weekly_forecast.py + monthly_forecast.py
# Agent 3 (KNOWLEDGE): knowledge/rules/atmakaraka_rules.json + synastry_rules.json + gem_prescription_rules.json

# STEP 3: After all 3 complete, run Agent 4 (WIRING):
# Agent 4: services/mcp/ + services/api/ + packages/guide/ + tests/integration/

# STEP 4: Verify
uv run ruff check .
uv run ruff format .
uv run pytest

# STEP 5: Commit
```

---

*Generated: Feb 7, 2026 | For Claude Code Session 22*
