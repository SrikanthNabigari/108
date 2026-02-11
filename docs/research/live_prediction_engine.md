# Live Prediction Engine — Implementation Design

> A multi-timeframe, multi-factor prediction system with visual heat maps.
> User can see live state, backtest any date range, and verify against real life.
> Date: February 10, 2026

---

## 1. What We're Building

A **State Vector Engine** that, for ANY datetime (past, present, or future), computes:

1. What the planets predict about your mental/emotional state
2. Which specific factors (transit, dasha, yoga, etc.) are driving the prediction
3. How confident the prediction is (confluence score)
4. Area-wise breakdown (career, relationships, health, finance, spiritual)

Then visualizes it as **interactive heat maps** across any timeframe:
- **Hourly** (24 columns) — for testing "do I feel different each hora?"
- **Daily** (7 columns) — for testing "was this week's mood pattern predicted?"
- **Monthly** (28-31 columns) — for testing "did the system predict my good/bad months?"
- **Yearly** (12 columns) — for testing "does the dasha-transit system explain my year?"
- **Custom range** — pick any start/end date

---

## 2. The State Vector — What Gets Computed

For each datetime, we compute 7 factor scores (0-10 each) plus 5 area scores:

### 2.1 Seven Prediction Factors

```
┌─────────────────────────────────────────────────────────────────┐
│                    STATE VECTOR at 2026-02-10 14:30              │
│                                                                  │
│  FACTOR              SCORE   WEIGHT   CONTRIBUTION               │
│  ─────────────────   ─────   ──────   ────────────               │
│  1. Panchanga        8/10    15%      Tithi: Shubha, Yoga: Siddha│
│  2. Transit Moon     6/10    15%      Moon in Taurus (4 bindus)  │
│  3. Gochara          7/10    20%      5 favorable, 2 unfavorable │
│  4. Dasha Quality    5/10    20%      Merc MD / Rahu AD = mixed  │
│  5. Yoga Activation  4/10    10%      1 of 8 yogas transit-active│
│  6. Shadbala Today   7/10    10%      Hora lord Venus strong(280)│
│  7. Ashtakavarga     6/10    10%      Current sign has 28 SAV    │
│  ─────────────────   ─────   ──────                              │
│  COMPOSITE SCORE:    6.3/10  100%                                │
│                                                                  │
│  AREAS:  Career: 7  Love: 5  Health: 8  Money: 6  Spirit: 4    │
│                                                                  │
│  PREDICTED STATE:                                                │
│    Energy: ███░░ (3/5)    Clarity: ████░ (4/5)                  │
│    Mood: Focused but anxious                                     │
│    Element: Air (Vayu) dominant                                  │
│    Guna: Rajas (active, restless)                                │
│    Best for: Communication, analysis, short tasks                │
│    Avoid: Long-term commitments, emotional decisions             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Factor Computation Details

**Factor 1: Panchanga Quality (0-10)**
```
Source:     panchanga() from 108-ephemeris
Components: Tithi quality (0-2), Vara quality (0-2), Yoga quality (0-2),
            Karana quality (0-2), Nakshatra quality (0-2)
Normalize:  Sum / 10 × 10
Already:    daily_forecast() computes this (30% weight) — EXTRACT it

Tithi scoring:
  Nanda tithis (1,6,11):     +2 (joy)
  Bhadra tithis (2,7,12):    +1.5 (auspicious)
  Jaya tithis (3,8,13):      +1.5 (victory)
  Rikta tithis (4,9,14):     +0.5 (loss)
  Purna tithis (5,10,15):    +2 (fullness)
  Amavasya/Purnima specials: ±1 adjustment

Vara scoring:
  Planet-day alignment bonuses
  Monday/Wednesday/Thursday/Friday: +1 general
  Saturday: -0.5 general (but +1 for Saturn-related work)
  Tuesday: neutral (depends on Mars dignity)
```

**Factor 2: Transit Moon Position (0-10)**
```
Source:     planetary_positions() + ashtakavarga()
Components: Moon's current sign, house from natal Moon,
            Ashtakavarga bindus for Moon in current sign (0-8)
Normalize:  BAV score mapped: 0-1 bindus → 1, 2-3 → 3, 4 → 5, 5-6 → 7, 7-8 → 9-10
Already:    daily_forecast() uses moon BAV (20% weight) — EXTRACT it

Moon nakshatra adds qualitative color:
  Deva nakshatras: +1 (gentler emotions)
  Manushya nakshatras: 0 (neutral)
  Rakshasa nakshatras: -1 (intense emotions)
```

**Factor 3: Gochara / Transit Analysis (0-10)**
```
Source:     transit_analysis() from 108-context
Components: Count of favorable vs unfavorable transits from Moon
            Sade Sati phase (-2 to -3)
            Dhaiya (-1)
Normalize:  (favorable - unfavorable + 5) clamped to 0-10
            Sade Sati: subtract 2-3 depending on phase
Already:    daily_forecast() uses transit aspects (30% weight)

Scoring:
  Each favorable transit: +1
  Each unfavorable transit: -1
  Sade Sati rising: -2
  Sade Sati peak: -3
  Sade Sati setting: -1.5
  Dhaiya active: -1
  Base: 5 (neutral)
```

**Factor 4: Dasha Quality (0-10)**
```
Source:     current_dasha() + antardasha_effects() from 108-context
Components: Nature of MD lord, AD lord, PD lord
            Their mutual relationship (friends/enemies)
            Their functional benefic/malefic status for the lagna
Normalize:  Composite score based on planet nature + relationship

Scoring per lord:
  Natural benefic (Jupiter, Venus, Moon, Mercury): +1.5
  Natural malefic (Saturn, Mars, Rahu, Ketu): -0.5
  Sun: +0.5 (mild benefic)

  Functional benefic for lagna: +1
  Functional malefic for lagna: -1

  MD-AD lords are friends: +1
  MD-AD lords are enemies: -1.5

  Normalize sum to 0-10 scale
```

**Factor 5: Yoga Activation (0-10)**
```
Source:     detect_yogas() + current transits
Logic:     A natal yoga is "activated" when:
           a) One of its involved planets is the current dasha lord, OR
           b) A transit planet aspects one of its involved planets, OR
           c) Transit planet is in the same sign as a yoga planet

Scoring:
  Count activated yogas / total natal yogas × 10
  Weight by yoga strength (0-1 from detector)
  Raja yoga activated: +2 bonus
  Dhana yoga activated: +1.5 bonus

  If 0 yogas activated: score = 2 (baseline)
  If 50%+ activated: score = 8-10 (powerful period)
```

**Factor 6: Shadbala of Dominant Planet (0-10)**
```
Source:     calculate_shadbala() from 108-patterns
Logic:     "Dominant planet" = the planet with most influence NOW
           Priority: Hora lord > AD lord > MD lord
           Get its natal Shadbala

Normalize: Shadbala total mapped:
  < 150: score 2 (weak — you fight this energy)
  150-200: score 4 (fair)
  200-250: score 5 (moderate)
  250-300: score 7 (strong — you flow with this energy)
  300-350: score 8 (very strong)
  > 350: score 10 (dominant — this energy defines you)
```

**Factor 7: Ashtakavarga Transit Strength (0-10)**
```
Source:     ashtakavarga() from 108-patterns
Logic:     Get Sarvashtakavarga (SAV) score for the sign where
           the current transit's most significant planet sits
           Also check individual BAV for dasha lord's current sign

Normalize: SAV score mapped:
  < 22: score 2 (weak sign — transit effects diminished)
  22-25: score 4 (below average)
  25-28: score 5 (average)
  28-32: score 7 (above average — transit effects amplified)
  > 32: score 9-10 (very strong sign)
```

### 2.3 Area Scoring (0-10 each)

Derived from which HOUSES are activated by current transits and dashas:

```
CAREER (Houses 10, 6, 2):
  score = avg(
    transit_impact_on_10th_lord,
    dasha_lord_relationship_to_10th_house,
    ashtakavarga_of_10th_sign
  )

RELATIONSHIPS (Houses 7, 5, 11):
  score = avg(
    transit_impact_on_7th_lord,
    venus_transit_strength,
    dasha_lord_relationship_to_7th_house
  )

HEALTH (Houses 1, 6, 8):
  score = avg(
    transit_impact_on_lagna_lord,
    malefic_transits_on_6th_8th,
    sun_transit_strength
  )

FINANCE (Houses 2, 11, 5):
  score = avg(
    transit_impact_on_2nd_lord,
    jupiter_transit_strength,
    dhana_yoga_activation
  )

SPIRITUAL (Houses 9, 12, 5):
  score = avg(
    transit_impact_on_9th_lord,
    jupiter_ketu_transit_strength,
    moksha_yoga_activation
  )
```

### 2.4 Predicted Mental State

Synthesized from all factors:

```
ENERGY LEVEL (1-5):
  High when: Composite > 7, Mars/Sun hora or dasha active, Agni tattva
  Low when: Composite < 4, Saturn/Moon hora, Tamas guna dominant

MENTAL CLARITY (1-5):
  High when: Mercury strong, Sattva guna, Panchanga > 7, no Sade Sati
  Low when: Rahu/Ketu dasha active, Tamas guna, Moon afflicted

EMOTIONAL TONE (categorical):
  Mapped from: Moon transit nakshatra + AD lord + dominant guna
  Options: Peaceful, Optimistic, Focused, Anxious, Frustrated,
           Melancholic, Restless, Inspired, Withdrawn, Neutral

DOMINANT ELEMENT:
  Mapped from: Hora planet → Tattva assignment (BPHS)

DOMINANT GUNA:
  Mapped from: Hora planet guna (BPHS Ch.3)
  Modified by: Dasha lord guna, Moon nakshatra guna
```

---

## 3. Heat Map Visualizations

### 3.1 Monthly Factor Heat Map (Primary View)

```
February 2026 — Factor Breakdown
                                                              Composite
Day:  1   2   3   4   5   6   7   8   9  10  11  12 ... 28    Avg
     ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───     ───┐
Pan  │ 7 │ 8 │ 6 │ 4 │ 9 │ 7 │ 5 │ 8 │ 7 │ 6 │ 8 │ 5 │   │6.7│ Panchanga
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───     ───┤
Moon │ 6 │ 5 │ 7 │ 8 │ 6 │ 4 │ 7 │ 5 │ 6 │ 7 │ 5 │ 8 │   │6.1│ Transit Moon
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───     ───┤
Goch │ 5 │ 5 │ 5 │ 6 │ 6 │ 7 │ 7 │ 7 │ 6 │ 5 │ 5 │ 4 │   │5.6│ Gochara
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───     ───┤
Dash │ 6 │ 6 │ 6 │ 6 │ 6 │ 6 │ 6 │ 6 │ 6 │ 6 │ 6 │ 6 │   │6.0│ Dasha
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───     ───┤
Yoga │ 3 │ 3 │ 3 │ 4 │ 5 │ 5 │ 4 │ 3 │ 3 │ 4 │ 5 │ 4 │   │3.8│ Yoga Active
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───     ───┤
Shad │ 7 │ 7 │ 7 │ 5 │ 5 │ 8 │ 8 │ 6 │ 6 │ 7 │ 7 │ 5 │   │6.5│ Shadbala
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───     ───┤
BAV  │ 5 │ 6 │ 6 │ 7 │ 7 │ 6 │ 5 │ 5 │ 6 │ 6 │ 7 │ 7 │   │6.0│ Ashtakavarga
     ╞═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══╪═══     ═══╡
COMP │5.6│5.7│5.7│5.7│6.3│6.1│6.0│5.7│5.7│5.9│6.1│5.3│   │5.8│ COMPOSITE
     └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───     ───┘

Color: 🟢 8-10  🟡 5-7  🔴 1-4

Click any cell → drill-down to detailed breakdown
```

### 3.2 Yearly Area Heat Map

```
2026 — Life Areas by Month
                                                               Year
Month: Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec  Avg
      ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
Career│ 6  │ 7  │ 5  │ 4  │ 8  │ 8  │ 7  │ 6  │ 5  │ 7  │ 8  │ 7  │6.5 │
      ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
Love  │ 5  │ 4  │ 7  │ 8  │ 6  │ 5  │ 4  │ 6  │ 7  │ 8  │ 6  │ 5  │5.9 │
      ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
Health│ 7  │ 7  │ 8  │ 7  │ 6  │ 5  │ 4  │ 5  │ 6  │ 7  │ 7  │ 8  │6.4 │
      ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
Money │ 5  │ 6  │ 6  │ 5  │ 7  │ 8  │ 7  │ 6  │ 5  │ 6  │ 7  │ 7  │6.3 │
      ├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
Spirit│ 4  │ 5  │ 6  │ 7  │ 5  │ 4  │ 5  │ 6  │ 8  │ 7  │ 5  │ 4  │5.5 │
      └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘

Overlay: Dasha period boundaries marked with vertical lines
         ▼ = Antardasha change  ▽ = Pratyantardasha change
```

### 3.3 Daily Hourly Heat Map (Hora-Level)

```
February 10, 2026 — Hour by Hour
            Sunrise: 06:42    Sunset: 18:12

Hour:  6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21  22
      ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
Hora  │ ☽ │ ♄ │ ♃ │ ♂ │ ☉ │ ♀ │ ☿ │ ☽ │ ♄ │ ♃ │ ♂ │ ☉ │ ♀ │ ☿ │ ☽ │ ♄ │ ♃ │
      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
Nadi  │ I │ P │ S │ P │ P │ I │ I │ I │ P │ S │ P │ P │ I │ I │ I │ P │ S │
      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
Elem  │ 💧│ 💨│ ✨│ 🔥│ 🔥│ 💧│ 🌍│ 💧│ 💨│ ✨│ 🔥│ 🔥│ 💧│ 🌍│ 💧│ 💨│ ✨│
      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
Guna  │ S │ T │ S │ T │ S │ R │ R │ S │ T │ S │ T │ S │ R │ R │ S │ T │ S │
      ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
Score │ 6 │ 4 │ 8 │ 5 │ 7 │ 7 │ 6 │ 6 │ 3 │ 8 │ 5 │ 7 │ 7 │ 6 │ 6 │ 3 │ 8 │
      └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

I=Ida  P=Pingala  S=Sushumna
S=Sattva  R=Rajas  T=Tamas

Current time marker: ▼ (14:30)
You are in: Saturn Hora → Pingala → Vayu → Tamas
Prediction: "Restricted, anxious energy. Discipline helps. Avoid big decisions."
```

### 3.4 Event Overlay View (Verification)

```
March 2025 (Backtest) — Predicted vs Actual Events

Day:  1   2   3   4   5   6   7   8   9  10  11  12 ... 31
     ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───     ───┐
COMP │5.6│5.7│5.7│5.7│6.3│6.1│6.0│5.7│3.2│3.0│2.8│4.3│   │5.1│
     └───┴───┴───┴───┴───┴───┴───┴───┴─▲─┴─▲─┴─▲─┴───     ───┘
                                        │   │   │
                              USER EVENTS MARKED:
                              Day 9:  "Got sick, fever"
                              Day 10: "Missed work, bedridden"
                              Day 11: "Still recovering"

     System predicted: Score dropped to 2.8-3.2 on days 9-11
     Reason: Saturn transit 8th from Moon + Rikta tithi + Ketu PD start
     MATCH: ✅ Health dip correctly predicted by transit + dasha

     ─────────────────────────────────────────────────────────
     Day 5 peak (6.3): "Got promotion news"
     System: Jupiter aspect on 10th lord + Raja Yoga activated
     MATCH: ✅ Career high correctly predicted
```

---

## 4. Implementation Architecture

### 4.1 What We Build (Backend — Python)

```
packages/swara/src/
├── state_engine.py          ← THE CORE: compute_state_vector()
├── factor_scores.py         ← Individual factor computations
├── area_scores.py           ← Career/Love/Health/Money/Spirit
├── batch_compute.py         ← Compute for date ranges
├── mental_state_mapper.py   ← Map scores → predicted state text
└── confluence.py            ← Multi-factor agreement scoring
```

**Core function signature:**
```python
def compute_state_vector(
    birth_datetime: str,          # ISO format
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict,          # {planet: {longitude, sign, house, ...}}
    moon_longitude: float,        # Natal moon longitude
    lagna_rashi: str,             # Ascendant sign
    query_datetime: str,          # When to predict for
    query_lat: float = None,      # Current location (optional)
    query_lon: float = None,
) -> StateVector:
    """
    Returns complete prediction state for a single moment.
    Calls existing 108-core functions internally.
    """
```

**Batch function:**
```python
def compute_range(
    birth_data: BirthData,
    start_date: str,              # "2026-01-01"
    end_date: str,                # "2026-12-31"
    resolution: str = "daily",    # "hourly" | "daily" | "weekly" | "monthly"
) -> list[StateVector]:
    """
    Computes state vectors for every point in the range.
    Daily: one per day at noon local time
    Hourly: one per hora boundary
    Weekly: average of 7 daily scores
    Monthly: average of ~30 daily scores
    """
```

### 4.2 What We Build (Frontend — React Visualization)

Single-page interactive React app with:

```
┌──────────────────────────────────────────────────────────────┐
│  108 STATE MAP                          [📅 Date Range ▼]    │
│                                                               │
│  View: [Hourly] [Daily] [Weekly] [Monthly] [Yearly]          │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                                                          │ │
│  │              HEAT MAP (main visualization)               │ │
│  │              Rows = Factors | Columns = Time             │ │
│  │                                                          │ │
│  │  Click any cell for drill-down                          │ │
│  │                                                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌──────────────────────┐ ┌──────────────────────────────┐  │
│  │ AREA SCORES          │ │ DETAIL PANEL (selected cell)  │  │
│  │ Career:  ████████░░  │ │                               │  │
│  │ Love:    █████░░░░░  │ │ Date: Feb 10, 2026           │  │
│  │ Health:  ███████░░░  │ │ Factor: Gochara              │  │
│  │ Money:   ██████░░░░  │ │ Score: 7/10                  │  │
│  │ Spirit:  ████░░░░░░  │ │                               │  │
│  └──────────────────────┘ │ Favorable: Sun(3), Jup(5)... │  │
│                            │ Unfavorable: Sat(8), Mars(6) │  │
│  ┌──────────────────────┐ │ Sade Sati: Not active        │  │
│  │ MY EVENTS            │ │                               │  │
│  │ + Add Event          │ │ [Full transit breakdown →]    │  │
│  │ Feb 5: Got promotion │ └──────────────────────────────┘  │
│  │ Feb 9: Felt anxious  │                                    │
│  │ Jan 15: Started gym  │                                    │
│  └──────────────────────┘                                    │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 What Calls What (Data Flow)

```
React App
  │
  ├── Loads precomputed JSON file (generated by Python batch)
  │   OR
  ├── Calls FastAPI endpoint (real-time single computation)
  │
  │   compute_state_vector()
  │       │
  │       ├── get_sunrise_sunset()         ← 108-ephemeris (exists)
  │       ├── get_all_planets()            ← 108-ephemeris (exists)
  │       ├── get_panchanga()              ← 108-ephemeris (exists)
  │       ├── get_current_dasha()          ← 108-context (exists)
  │       ├── get_antardasha_effects()     ← 108-context (exists)
  │       ├── get_full_transit_analysis()  ← 108-context (exists)
  │       ├── detect_all_yogas()           ← 108-patterns (exists)
  │       ├── calculate_shadbala()         ← 108-patterns (exists)
  │       ├── get_ashtakavarga()           ← 108-patterns (exists)
  │       ├── get_current_hora()           ← 108-swara (NEW — simple)
  │       │
  │       ├── factor_scores.py             ← NEW: normalizes to 0-10
  │       ├── area_scores.py               ← NEW: house-based areas
  │       ├── mental_state_mapper.py       ← NEW: scores → prediction text
  │       └── confluence.py                ← NEW: agreement scoring
  │
  └── Renders heat maps, allows event entry, shows drill-down
```

### 4.4 Dependencies from Existing 108-Core

Everything marked "exists" has been verified in the codebase:

| Function | Package | Status | Returns |
|----------|---------|--------|---------|
| `get_sunrise_sunset()` | cosmos | ✅ Built | sunrise, sunset datetimes |
| `get_all_planets()` | cosmos | ✅ Built | 9 planet positions |
| `get_tithi()` | cosmos | ✅ Built | tithi number, name |
| `get_vara()` | cosmos | ✅ Built | weekday info |
| `get_yoga()` | cosmos | ✅ Built | nitya yoga |
| `get_karana()` | cosmos | ✅ Built | karana |
| `get_panchanga()` | cosmos | ✅ Built | all 5 limbs |
| `get_current_dasha()` | context | ✅ Built | MD/AD/PD with dates |
| `get_antardasha_effects()` | context | ✅ Built | 81 combinations |
| `get_full_transit_analysis()` | context | ✅ Built | gochara + sade sati |
| `get_daily_forecast()` | context | ✅ Built | day_rating 1-10 |
| `detect_all_yogas()` | self | ✅ Built | list of yogas + strength |
| `detect_doshas()` | self | ✅ Built | list of doshas |
| `calculate_shadbala()` | self | ✅ Built | 6-fold strength |
| `get_ashtakavarga()` | self | ✅ Built | SAV + per-planet BAV |
| `get_current_hora()` | swara | ❌ NEW | hora planet + times |

**Only 1 new astronomical function needed. Everything else is scoring logic and visualization.**

---

## 5. What We're Actually Testing With This

### 5.1 Test: "Does the composite score predict my day quality?"

Look at the monthly heat map. Find your best days and worst days from memory.
Do they correspond to high/low composite scores?

If YES → The weighted combination of factors works.
If NO → The weights need adjustment, or additional factors matter.

### 5.2 Test: "Which factor is the most predictive for ME?"

Look at individual factor rows. Which one has the strongest correlation
with your actual good/bad days?

Possible findings:
- "Dasha is the strongest predictor" → Long-term cycles matter most for you
- "Transit Moon is the strongest" → You're emotionally lunar-driven
- "Panchanga is noise" → Tithi/Yoga/Karana don't affect you much
- "Ashtakavarga is highly predictive" → Your chart responds to transit strength

This finding is PERSONAL. Different charts may show different dominant factors.

### 5.3 Test: "Does confluence improve accuracy?"

Mark 20-30 actual life events (good days, bad days, arguments, promotions,
illness, inspiration moments). Check the confluence score on those dates.

If events cluster at high/low confluence → Multi-factor model works.
If events are random relative to confluence → Single factors matter but
their combination doesn't add value.

### 5.4 Test: "Do area scores match life-area events?"

Mark career events, relationship events, health events separately.
Check if the corresponding area score predicted correctly.

"I got promoted on March 5 — was the career score high?"
"I had a fight on April 12 — was the relationship score low?"
"I got sick on June 20 — was the health score low?"

### 5.5 Test: "Dasha transitions = life transitions?"

Look at the yearly view. Find Antardasha change dates.
Do they correspond to shifts in your life theme?

This is the MOST powerful validation because dasha changes are rare
(every few months) and should correspond to noticeable life shifts.

---

## 6. Implementation Order

### Step 1: get_current_hora() (2 hours)
The only new astronomical function. Extract from buried strength.py code,
make it public, add sunrise-based calculation.

### Step 2: factor_scores.py (4 hours)
7 functions, each calling existing 108-core functions and normalizing to 0-10.
Most of the logic is already in daily_forecast.py — extract and expand.

### Step 3: area_scores.py (3 hours)
5 area scoring functions based on house lords and their transit states.

### Step 4: state_engine.py + mental_state_mapper.py (3 hours)
The synthesis function that calls all factor scores and produces
the complete StateVector.

### Step 5: batch_compute.py (2 hours)
Loop over date range, compute daily states, output JSON.

### Step 6: React Heat Map Visualization (6-8 hours)
Interactive heat map with:
- Date range selector
- View toggle (hourly/daily/weekly/monthly/yearly)
- Cell click drill-down
- Event overlay (user marks actual events)
- Area score sidebar

### Step 7: Test with YOUR data (ongoing)
Run batch compute for the past 6-12 months.
Mark real life events from memory.
See if the patterns match.

**Total estimated build time: 20-24 hours of focused work.**

---

## 7. Database Tables for Event Logging

```sql
-- User marks real-life events to compare against predictions
CREATE TABLE life_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_date DATE NOT NULL,
    event_time TIME,
    event_type VARCHAR(20) NOT NULL,     -- 'career', 'relationship', 'health', 'finance', 'spiritual', 'general'
    quality VARCHAR(10) NOT NULL,         -- 'positive', 'negative', 'neutral'
    intensity INTEGER CHECK (intensity BETWEEN 1 AND 5),  -- how significant was this
    title VARCHAR(200) NOT NULL,          -- "Got promoted", "Had fever"
    description TEXT,
    tags TEXT[],                           -- ['work', 'money', 'stress']
    created_at TIMESTAMP DEFAULT NOW()
);

-- Precomputed daily state vectors (batch computed, cached)
CREATE TABLE daily_state_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,

    -- Factor scores (0-10)
    panchanga_score FLOAT NOT NULL,
    transit_moon_score FLOAT NOT NULL,
    gochara_score FLOAT NOT NULL,
    dasha_score FLOAT NOT NULL,
    yoga_activation_score FLOAT NOT NULL,
    shadbala_score FLOAT NOT NULL,
    ashtakavarga_score FLOAT NOT NULL,
    composite_score FLOAT NOT NULL,

    -- Area scores (0-10)
    career_score FLOAT,
    relationship_score FLOAT,
    health_score FLOAT,
    finance_score FLOAT,
    spiritual_score FLOAT,

    -- Predicted state
    predicted_energy INTEGER CHECK (predicted_energy BETWEEN 1 AND 5),
    predicted_clarity INTEGER CHECK (predicted_clarity BETWEEN 1 AND 5),
    predicted_emotion VARCHAR(20),
    predicted_element VARCHAR(10),
    predicted_guna VARCHAR(10),

    -- Context snapshot
    hora_sequence JSONB,              -- [{hour, planet, nadi, element}] for all 24 horas
    dasha_snapshot JSONB,             -- {md, ad, pd}
    active_yogas JSONB,              -- [{name, strength, activated}]
    transit_aspects JSONB,            -- [{transit, natal, aspect, effect}]
    sade_sati_active BOOLEAN DEFAULT FALSE,

    -- Confluence
    confluence_score INTEGER CHECK (confluence_score BETWEEN 0 AND 6),

    UNIQUE(user_id, forecast_date),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_state_vectors_user_date ON daily_state_vectors(user_id, forecast_date);
CREATE INDEX idx_state_vectors_composite ON daily_state_vectors(user_id, composite_score);
CREATE INDEX idx_life_events_user_date ON life_events(user_id, event_date);
CREATE INDEX idx_life_events_type ON life_events(user_id, event_type);
```

---

## 8. API Endpoints for the Visualization

```
STATE ENGINE
  GET  /api/v1/state/now              → current state vector (live)
  GET  /api/v1/state/date/:date       → state vector for specific date
  GET  /api/v1/state/range            → batch state vectors
       ?start=2026-01-01
       &end=2026-02-28
       &resolution=daily

EVENTS (for verification)
  GET    /api/v1/events               → user's life events
  POST   /api/v1/events               → add life event
  PUT    /api/v1/events/:id           → update event
  DELETE /api/v1/events/:id           → delete event

ANALYSIS (correlation computation)
  GET  /api/v1/analysis/correlation   → compute prediction vs events accuracy
       ?start=2025-01-01
       &end=2026-02-10
  GET  /api/v1/analysis/factor-rank   → which factor is most predictive for this user
  GET  /api/v1/analysis/area-accuracy → per-area prediction accuracy
```
