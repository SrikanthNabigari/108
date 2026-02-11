# Swara Verification Framework — Empirical Design

> How we prove (or disprove) that Hora-Tattva-Nadi predictions correlate with actual mental states.
> This document turns philosophy into testable science.
> Date: February 10, 2026

---

## 1. The Core Hypothesis

**H₀ (Null):** Planetary hora has no correlation with active nadi, experienced tattva, or mental state. Predictions are no better than random chance.

**H₁ (Alternative):** Planetary hora predictions of nadi, tattva, and mental state are statistically better than chance, with accuracy improving when multiple astrological timeframes are in confluence.

**What "works" means, quantified:**
- **Nadi prediction accuracy:** >60% (chance = 50% for binary left/right)
- **Mental state prediction accuracy:** >35% (chance = 20% for 5 categories)
- **Cohen's Kappa:** κ ≥ 0.41 (moderate agreement) for predicted vs reported states
- **Confluence correlation:** Positive correlation (r > 0.3) between confluence score and prediction accuracy

---

## 2. What We're Testing — Five Layers

### Layer 1: Nadi Accuracy (Binary Test)
```
Question:  Does the predicted active nostril match the actual active nostril?
Predicted: Hora planet → Nadi mapping (Pingala/Ida/Sushumna)
Actual:    User self-report of dominant nostril
Test:      Chi-square goodness-of-fit
Chance:    50% (binary) or 33% (ternary with Sushumna)
Target:    >60% accuracy
```

### Layer 2: Tattva Cycle Accuracy (5-Category Test)
```
Question:  Does the predicted Tattva match the user's experienced element?
Predicted: Time within hora → Tattva cycle (Prithvi/Jala/Agni/Vayu/Akasha)
Actual:    User reports dominant quality (grounded/flowing/intense/restless/spacious)
Test:      Chi-square test of independence
Chance:    20% (5 categories)
Target:    >35% accuracy
```

### Layer 3: Mental State Prediction (Composite Test)
```
Question:  Does the predicted mental state match the actual reported state?
Predicted: Tattva × Nadi × Hora Planet Guna → specific state description
Actual:    User selects from curated state options or rates dimensions
Test:      Cohen's Kappa (categorical) or Pearson correlation (dimensional)
Chance:    Varies by number of categories
Target:    κ ≥ 0.41 (moderate agreement)
```

### Layer 4: Personal Resonance Validation
```
Question:  Do people with strong natal Mars feel Mars Hora more intensely?
Predicted: Shadbala score → resonance intensity
Actual:    Self-reported intensity rating during each hora
Test:      Pearson correlation between Shadbala and reported intensity
Chance:    r = 0 (no correlation)
Target:    r > 0.3 (moderate positive correlation)
```

### Layer 5: Confluence Effect
```
Question:  Are predictions more accurate when multiple systems agree?
Predicted: Confluence score (0-5) based on system agreement
Actual:    Prediction accuracy at each confluence level
Test:      Linear regression / Spearman rank correlation
Chance:    Flat (no relationship between confluence and accuracy)
Target:    Positive slope with p < 0.05
```

---

## 3. Data Collection Design

### 3.1 The Prompt — Experience Sampling Method (ESM)

Based on ecological momentary assessment best practices, each prompt takes **< 90 seconds**:

```
┌─────────────────────────────────────────────────┐
│  SWARA CHECK-IN  ⏱️ 12:34 PM                    │
│                                                   │
│  1. Which nostril feels more open right now?      │
│     ○ Left    ○ Right    ○ Both equal             │
│                                                   │
│  2. Your dominant feeling right now?              │
│     ○ Grounded/Stable     (Prithvi)              │
│     ○ Flowing/Emotional   (Jala)                 │
│     ○ Intense/Sharp       (Agni)                 │
│     ○ Restless/Moving     (Vayu)                 │
│     ○ Spacious/Empty      (Akasha)               │
│                                                   │
│  3. Energy level?                                 │
│     ① ② ③ ④ ⑤                                    │
│     Low        High                               │
│                                                   │
│  4. Mental clarity?                               │
│     ① ② ③ ④ ⑤                                    │
│     Foggy      Crystal                            │
│                                                   │
│  5. Emotional tone?                               │
│     ○ Peaceful  ○ Excited  ○ Anxious             │
│     ○ Sad       ○ Angry    ○ Neutral             │
│                                                   │
│  (Optional) Brief note:                           │
│  ┌─────────────────────────────────────┐         │
│  │ e.g., "just had coffee" or          │         │
│  │ "argument with colleague"           │         │
│  └─────────────────────────────────────┘         │
│                                                   │
│              [ Submit ✓ ]                         │
└─────────────────────────────────────────────────┘
```

### 3.2 Prompt Frequency

| Phase | Duration | Frequency | Total Check-ins |
|-------|----------|-----------|----------------|
| **Intensive (Phase 1)** | Days 1-7 | Every 60 min (waking hours, ~16/day) | ~112 |
| **Standard (Phase 2)** | Days 8-30 | Every 2 hours (~8/day) | ~184 |
| **Maintenance (Phase 3)** | Day 31+ | 4× daily (morning, noon, evening, night) | ~4/day ongoing |

**Total Phase 1+2 data points: ~296 check-ins per user**

This exceeds the chi-square minimum of ~100 observations for binary nadi testing and gives enough data for the 5-category tattva test.

### 3.3 Data Schema

Each check-in generates ONE record:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "timestamp": "2026-02-10T12:34:00+05:30",

  "// ─── USER-REPORTED (Ground Truth) ───",
  "reported_nostril": "left",
  "reported_feeling": "flowing_emotional",
  "reported_energy": 3,
  "reported_clarity": 4,
  "reported_emotion": "peaceful",
  "reported_note": "just finished lunch",

  "// ─── SYSTEM-PREDICTED (At time of check-in) ───",
  "predicted_hora": {
    "planet": "venus",
    "hora_number": 7,
    "hora_start": "2026-02-10T12:15:00+05:30",
    "hora_end": "2026-02-10T13:18:00+05:30",
    "minutes_elapsed": 19,
    "minutes_remaining": 44
  },
  "predicted_nadi": {
    "expected": "ida",
    "nostril": "left",
    "source": "hora_planet_mapping"
  },
  "predicted_tattva": {
    "current": "jala",
    "element": "water",
    "minutes_into_tattva": 3.2,
    "minutes_remaining": 12.8,
    "cycle_position": 2
  },
  "predicted_mental_state": {
    "primary": "Deep emotion, intuition, romantic feeling, creativity",
    "qualities": ["emotional", "creative", "gentle", "intuitive"],
    "energy_expected": 3,
    "best_for": ["art", "music", "intimacy", "counseling"],
    "guna": "rajas",
    "guna_effect": "Desire-driven, seeking beauty and connection"
  },

  "// ─── ASTROLOGICAL CONTEXT (Frozen at check-in time) ───",
  "context": {
    "paksha": "shukla",
    "tithi": 8,
    "tithi_name": "ashtami",
    "paksha_predicted_nadi": "ida",
    "transit_moon_nakshatra": "rohini",
    "transit_moon_sign": "taurus",
    "current_dasha": {
      "mahadasha": "mercury",
      "antardasha": "rahu",
      "pratyantardasha": "venus"
    },
    "dasha_lord_is_hora_planet": false,
    "panchanga_quality": "good",
    "choghadiya": "shubh",
    "ashtakavarga_hora_planet_score": 5
  },

  "// ─── CONFLUENCE SCORING ───",
  "confluence": {
    "score": 4,
    "max_possible": 6,
    "factors": {
      "hora_nadi_matches_paksha_nadi": true,
      "hora_planet_is_dasha_lord": false,
      "transit_moon_supports_mood": true,
      "choghadiya_agrees": true,
      "panchanga_quality_agrees": true,
      "ashtakavarga_strong": true
    }
  },

  "// ─── ACCURACY SCORING (Computed after user submits) ───",
  "accuracy": {
    "nadi_match": true,
    "tattva_match": true,
    "energy_delta": 0,
    "clarity_delta": 1,
    "emotion_category_match": false,
    "overall_score": 0.72
  },

  "// ─── CONFOUNDING VARIABLES ───",
  "confounders": {
    "time_of_day_bucket": "midday",
    "cortisol_phase": "declining",
    "hours_since_wake": 6.5,
    "day_of_week": "tuesday",
    "user_note_flags": ["food_recent"]
  }
}
```

---

## 4. Confounding Variable Controls

### 4.1 The Circadian Problem

If we predict "high energy during Sun Hora" and Sun Hora happens to be 7-8 AM (post-cortisol-peak), the accuracy might be due to biology, not planets. We MUST control for this.

**Known hormonal cycle (approximate):**

```
Hour    Cortisol    Melatonin   Serotonin   Expected State
─────   ────────    ─────────   ─────────   ──────────────
05:00   Rising ↑    Falling ↓   Low         Waking, groggy
06:00   Peak ★      Low         Rising ↑    Alert, clear
08:00   High        Gone        High        Peak focus
10:00   Declining   Gone        High        Productive
12:00   Moderate    Gone        Moderate    Sustained
14:00   Dip ↓       Gone        Dip ↓       Afternoon slump ★
16:00   Low         Gone        Moderate    Second wind
18:00   Low         Rising ↑    Declining   Winding down
20:00   Low         Moderate    Low         Relaxing
22:00   Minimum     High ★      Low         Sleepy
00:00   Minimum     Peak        Minimum     Deep sleep
02:00   Rising      Peak ★      Minimum     Deep sleep
```

**Control method: Time-of-Day Buckets**

Divide the day into 6 buckets and analyze Swara accuracy WITHIN each bucket:

| Bucket | Hours | Circadian State | Control Purpose |
|--------|-------|----------------|----------------|
| **Dawn** | 05:00-08:00 | Rising cortisol, peak alertness | High-energy predictions here might be circadian, not planetary |
| **Morning** | 08:00-11:00 | Sustained cortisol, high serotonin | Optimal performance window |
| **Midday** | 11:00-14:00 | Declining cortisol, approaching slump | Mixed zone |
| **Afternoon** | 14:00-17:00 | Cortisol dip, serotonin dip | Low-energy predictions here might be circadian |
| **Evening** | 17:00-20:00 | Low cortisol, rising melatonin | Wind-down period |
| **Night** | 20:00-23:00 | Melatonin dominant | Drowsiness predictions might be circadian |

**If Swara predictions are accurate ACROSS all buckets equally**, the signal is planetary, not circadian.
**If Swara predictions are only accurate in certain buckets**, the signal may be confounded.

### 4.2 Other Confounders to Track

| Confounder | How to Detect | How to Control |
|------------|--------------|---------------|
| **Caffeine** | User note flag "coffee/tea" | Exclude or tag check-ins within 2 hrs of caffeine |
| **Meal timing** | User note flag "just ate" | Postprandial state mimics Prithvi/Kapha — control for it |
| **Exercise** | User note flag "exercised" | Post-exercise state mimics Agni/Pingala |
| **Sleep quality** | Morning check-in question | Poor sleep biases toward Tamas states all day |
| **Weather** | Auto-detect from location API | Overcast/rain may correlate with Ida states |
| **Screen time** | Optional tracker integration | Blue light suppresses melatonin, distorts evening predictions |
| **Social context** | User note "alone/with people" | Social interaction naturally shifts arousal |

---

## 5. Statistical Analysis Framework

### 5.1 Primary Tests

#### Test 1: Nadi Accuracy (Binary)
```
Method:     Chi-square goodness-of-fit
H₀:        P(correct nadi prediction) = 0.50
H₁:        P(correct nadi prediction) > 0.50
α:          0.05 (significance level)
Power:      0.80 (β = 0.20)
Effect:     Medium (w = 0.30)
Min N:      88 observations (from G*Power calculation)
Our data:   ~296 check-ins → more than sufficient

Calculation:
  χ² = Σ (O - E)² / E
  Where O = observed correct predictions
        E = expected by chance (N/2 for binary)

  If χ² > 3.84 (df=1, α=0.05) → reject H₀
```

#### Test 2: Tattva Accuracy (5-Category)
```
Method:     Chi-square test of independence
H₀:        Predicted tattva is independent of reported feeling
H₁:        Predicted tattva correlates with reported feeling
α:          0.05
Min N:      5 × 5 × 5 = 125 minimum (5+ per cell in 5×5 table)
Our data:   ~296 check-ins → sufficient

Contingency table:
                 Reported Feeling
                 Ground  Flow  Intense  Restless  Spacious
Predicted  Prith   [  ]   [  ]   [  ]    [  ]      [  ]
Tattva     Jala    [  ]   [  ]   [  ]    [  ]      [  ]
           Agni    [  ]   [  ]   [  ]    [  ]      [  ]
           Vayu    [  ]   [  ]   [  ]    [  ]      [  ]
           Akash   [  ]   [  ]   [  ]    [  ]      [  ]
```

#### Test 3: Agreement Measure (Cohen's Kappa)
```
Method:     Cohen's Kappa
Purpose:    Measures agreement beyond chance
Input:      Predicted category vs Reported category
Threshold:  κ ≥ 0.41 = "Moderate" → system has real signal
            κ ≥ 0.61 = "Substantial" → system is reliable
            κ < 0.20 = "Slight" → system doesn't work

Formula:
  κ = (P_o - P_e) / (1 - P_e)
  Where P_o = observed agreement proportion
        P_e = expected agreement by chance
```

#### Test 4: Confluence Effect (Regression)
```
Method:     Ordinal logistic regression / Spearman correlation
IV:         Confluence score (0-6)
DV:         Prediction accuracy (binary correct/incorrect per check-in)
H₀:        No relationship between confluence and accuracy
H₁:        Higher confluence → higher accuracy

Also: Compare mean accuracy at each confluence level
  Confluence 0-1: expect ~baseline (chance-level)
  Confluence 2-3: expect ~moderate improvement
  Confluence 4-6: expect ~highest accuracy

If this gradient exists → multi-timeframe model validated
```

#### Test 5: Personal Resonance Correlation
```
Method:     Pearson correlation
IV:         Natal Shadbala of hora planet (continuous 0-500)
DV:         Reported intensity during that hora (1-5 scale)
H₀:        r = 0 (no correlation)
H₁:        r > 0 (positive correlation — stronger planet = felt more)
Threshold:  r > 0.3 (medium effect) with p < 0.05
```

### 5.2 Secondary Analyses

#### Analysis A: Circadian Confound Check
```
Run Test 1 (Nadi accuracy) separately for each time-of-day bucket.
If accuracy is similar across all buckets → signal is NOT circadian.
If accuracy varies significantly by bucket → signal may be confounded.
Use one-way ANOVA with bucket as factor, accuracy as DV.
```

#### Analysis B: Paksha vs Hora Nadi Agreement
```
The Shukla/Krishna Paksha rules and the Hora rules both predict Nadi.
Do they agree? When they disagree, which is more accurate?
Compute: P(correct | paksha_agrees_with_hora) vs P(correct | they_disagree)
If agreement predictions are more accurate → confluence validated.
```

#### Analysis C: Dasha Lord as Hora Planet
```
Special case: When the current Mahadasha/Antardasha lord IS the hora planet.
Is accuracy higher in these moments?
Two-sample t-test or Mann-Whitney U:
  Group 1: Check-ins where dasha_lord = hora_planet
  Group 2: Check-ins where dasha_lord ≠ hora_planet
```

#### Analysis D: Learning Effect
```
Does prediction accuracy improve over the 30-day period?
(Users may become more attuned to their own patterns)
Linear regression: Day number (1-30) vs accuracy
If positive slope → the system teaches awareness
If flat → accuracy is inherent, not learned
```

---

## 6. Heat Map Designs

### 6.1 Hora Accuracy Heat Map
```
         Mon   Tue   Wed   Thu   Fri   Sat   Sun
Sun  ☉  [   ] [   ] [   ] [   ] [   ] [   ] [   ]
Moon ☽  [   ] [   ] [   ] [   ] [   ] [   ] [   ]
Mars ♂  [   ] [   ] [   ] [   ] [   ] [   ] [   ]
Merc ☿  [   ] [   ] [   ] [   ] [   ] [   ] [   ]
Jup  ♃  [   ] [   ] [   ] [   ] [   ] [   ] [   ]
Ven  ♀  [   ] [   ] [   ] [   ] [   ] [   ] [   ]
Sat  ♄  [   ] [   ] [   ] [   ] [   ] [   ] [   ]

Color: 🟢 >70% accurate  🟡 50-70%  🔴 <50%

Reveals: Which planets YOU resonate with on which days.
Cross-reference: Does your chart explain the pattern?
```

### 6.2 Tattva × Time-of-Day Heat Map
```
            Dawn   Morn   Mid    Aftn   Eve    Night
Prithvi    [   ]  [   ]  [   ]  [   ]  [   ]  [   ]
Jala       [   ]  [   ]  [   ]  [   ]  [   ]  [   ]
Agni       [   ]  [   ]  [   ]  [   ]  [   ]  [   ]
Vayu       [   ]  [   ]  [   ]  [   ]  [   ]  [   ]
Akasha     [   ]  [   ]  [   ]  [   ]  [   ]  [   ]

Color: Frequency of ACTUAL reported tattva at each time.
Reveals: Your personal elemental rhythm across the day.
Compare: Against predicted tattva for circadian confound check.
```

### 6.3 Confluence vs Accuracy Scatter + Trend
```
Accuracy
  100% │                              ★
       │                         ★  ★
   80% │                    ★ ★
       │               ★ ★    ★
   60% │          ★ ★ ★   ★
       │     ★ ★ ★  ★
   40% │  ★ ★  ★
       │ ★ ★
   20% │★
       │
    0% └──────────────────────────────
       0    1    2    3    4    5    6
                Confluence Score

Trend line slope > 0 → MORE systems agreeing = MORE accurate
This is the SINGLE MOST IMPORTANT chart for validating the model.
```

### 6.4 Personal Resonance Map (Radar/Spider Chart)
```
                    Sun (Shadbala: 285)
                         ╱╲
                        ╱  ╲
              Sat ─────╱────╲───── Moon
             (310)   ╱  YOU  ╲   (220)
                    ╱          ╲
              Jup ─╱────────────╲── Mars
             (180)               (340)
                    ╲          ╱
              Ven ───╲────────╱─── Merc
             (260)    ╲      ╱    (295)
                       ╲    ╱
                        ╲  ╱
                         ╲╱

Overlay: Actual reported intensity during each planet's hora.
Match: If shape of "felt intensity" matches shape of Shadbala →
       Personal Resonance calculation validated.
```

### 6.5 Paksha Nadi Rhythm Map
```
Shukla Paksha Day 1-15:
  ┌─ Tithi 1 ─┬─ Tithi 2 ─┬─ Tithi 3 ─┬─ Tithi 4 ─┬─ Tithi 5 ─┐
  │  L L L L   │  L L L L   │  L L L L   │  R R R R   │  R R R R   │
  │ predicted  │ predicted  │ predicted  │ predicted  │ predicted  │
  │  L L R L   │  L L L R   │  L R L L   │  R R L R   │  R R R R   │
  │  actual    │  actual    │  actual    │  actual    │  actual    │
  └───────────┴───────────┴───────────┴───────────┴───────────┘

  L = Ida (Left)  R = Pingala (Right)
  Green highlight where predicted matches actual.

Reveals: Do the Shukla/Krishna Paksha rules hold for YOU?
```

---

## 7. Multi-Timeframe Confluence Scoring System

### 7.1 The Six Confluence Factors

Each factor scores 0 or 1. Total confluence = sum (0-6):

| # | Factor | Description | Score 1 if... |
|---|--------|-------------|--------------|
| 1 | **Hora-Paksha Nadi Agreement** | Do both systems predict the same active Nadi? | Hora Nadi = Paksha Nadi |
| 2 | **Dasha Lord = Hora Planet** | Is the current period lord the same as the hora planet? | MD or AD lord matches hora planet |
| 3 | **Transit Moon Supports Mood** | Does the Moon's current nakshatra support the predicted mental state? | Moon nakshatra lord is friendly to hora planet |
| 4 | **Choghadiya Agreement** | Does the Choghadiya quality match? | Choghadiya "good"/"excellent" when Sattva hora, "poor" when Tamas hora |
| 5 | **Panchanga Quality Matches** | Does the Tithi/Yoga/Karana/Vara support? | ≥3 of 5 Panchanga elements are favorable |
| 6 | **Ashtakavarga Strong** | Does the hora planet have strong transit support? | Hora planet's Ashtakavarga bindus ≥ 4 in current sign |

### 7.2 Confluence Interpretation

| Score | Label | Expected Accuracy | Interpretation |
|-------|-------|------------------|---------------|
| 0-1 | **Scattered** | ~Chance level | Systems disagree — prediction unreliable, mixed experience |
| 2-3 | **Partial** | ~Moderate | Some alignment — prediction has directional value |
| 4-5 | **Strong** | ~High | Systems converging — prediction should be felt clearly |
| 6 | **Perfect** | ~Very high | Full cosmic alignment — rare, powerful, unmistakable experience |

### 7.3 Trading Analogy (Multi-Timeframe Analysis)

```
TRADING                          SWARA
─────────────────                ─────────────────
Monthly chart trend     ←→       Mahadasha theme (years)
Weekly chart direction  ←→       Antardasha (months)
Daily chart setup       ←→       Transit + Gochara (days)
4-Hour chart pattern    ←→       Hora planet (hours)
15-Min chart entry      ←→       Tattva cycle (minutes)

TRADING RULE: Only enter when ALL timeframes agree.
SWARA RULE:  Prediction strongest when ALL systems agree.

In trading:  Confluence = higher probability trade
In swara:    Confluence = higher probability prediction
```

---

## 8. Momentum / Carry-Over Model

### 8.1 The Problem

A person doesn't reset at each hora boundary. If they've been in Saturn Hora (anxiety, restriction) for 63 minutes, they carry residue into the next hora. We need a **decay function**.

### 8.2 Exponential Decay Model

```
Current_State = (Current_Hora_Weight × Current_Prediction) +
                (Prev_Hora_Weight × Previous_Prediction) +
                (Prev2_Hora_Weight × Prediction_2_Ago)

Where weights follow exponential decay:
  Current:   w₀ = 0.60  (60% weight)
  Previous:  w₁ = 0.25  (25% weight)
  2 ago:     w₂ = 0.10  (10% weight)
  3+ ago:    w₃ = 0.05  (5% remainder — background dasha influence)

  Total: 0.60 + 0.25 + 0.10 + 0.05 = 1.00
```

### 8.3 State Transition Smoothness

Some Hora transitions are smooth (Venus → Moon = both Ida, Water → Water).
Others are jarring (Mars → Moon = Pingala→Ida, Fire → Water).

```
Transition ease = f(nadi_change, tattva_distance)

Same Nadi, same element family:     ease = 1.0 (seamless)
Same Nadi, different element:        ease = 0.7 (gentle shift)
Different Nadi, friendly elements:   ease = 0.4 (noticeable shift)
Different Nadi, hostile elements:    ease = 0.1 (jarring transition)

Mars Hora → Venus Hora:
  Pingala → Ida (nadi switch)
  Agni → Jala (fire → water = hostile)
  Ease = 0.1 → User will FEEL this transition strongly

  Prediction: "You may feel a sudden shift from intensity to softness.
               Allow 10-15 minutes to settle into the new energy."
```

---

## 9. Success Criteria — What Proves or Disproves the System

### 9.1 The System WORKS if:

| Criterion | Threshold | What It Means |
|-----------|----------|--------------|
| Nadi accuracy > 60% | χ² significant, p < 0.05 | Hora-Nadi mapping has real predictive value |
| Tattva κ ≥ 0.41 | Moderate agreement | Element cycle predictions beat chance meaningfully |
| Confluence r > 0.3 | Positive correlation | Multi-timeframe model adds value |
| Resonance r > 0.3 | Significant correlation | Personal chart modifies universal cycles |
| Circadian ANOVA p > 0.05 | NOT significant | Accuracy is NOT just circadian rhythm in disguise |

**If ALL five criteria are met:** The Swara system has genuine predictive power. Publish, scale, and integrate deeply into the app.

**If criteria 1-4 are met but NOT 5:** The system works but may be partially explained by circadian biology. Still valuable for the user, but frame as "biological rhythm awareness" not purely "planetary influence."

### 9.2 The System PARTIALLY WORKS if:

| Criterion | What It Means |
|-----------|--------------|
| Nadi accuracy > 60% but Tattva κ < 0.41 | Breath prediction works but element-to-feeling mapping needs refinement |
| Confluence works but base accuracy is low | The multi-timeframe model is the real insight — single-hora predictions aren't enough |
| Resonance works but overall accuracy is low | Personal chart is the key — universal rules are too generic |

### 9.3 The System DOESN'T WORK if:

| Criterion | What It Means |
|-----------|--------------|
| Nadi accuracy ≤ 55% | Not better than coin flip — Hora-Nadi mapping doesn't hold |
| Tattva κ < 0.20 | Slight/no agreement — element cycle is not felt by user |
| Confluence r ≤ 0 | No confluence effect — the multi-timeframe theory fails |
| All accuracy explained by circadian bucket | It's just biology, not astrology |

**If the system doesn't work:** We know with data, not opinion. The Swara layer becomes an "awareness tool" (track your own rhythms) rather than a "prediction engine." Still valuable — just framed differently.

---

## 10. Implementation Timeline for Verification

### Phase A: Build Prediction Engine (Week 1)
- `get_current_hora()`
- `get_current_tattva()`
- `hora_to_nadi()`
- `predict_mental_state()`
- `confluence_score()`
- All 6 knowledge JSON files

### Phase B: Build Logging Framework (Week 2)
- Database table: `swara_checkins` (schema from Section 3.3)
- Check-in prompt UI (Flutter)
- Automatic prediction computation at check-in time
- Confounding variable auto-detection (time bucket, day of week)

### Phase C: Personal Testing (Weeks 3-6)
- You (Srikanth) run the protocol for 30 days
- 296+ data points collected
- Daily accuracy dashboard visible in app

### Phase D: Statistical Analysis (Week 7)
- Run all 5 primary tests
- Generate all 5 heat maps
- Compute confluence correlation
- Run circadian confound check
- Write results report

### Phase E: Decision Point (Week 7 end)
```
Results → The system works     → Full integration into 108 app
Results → Partially works      → Refine mappings, retest with adjusted model
Results → Doesn't work         → Pivot to "awareness tool" framing
```

---

## 11. The Minimum Viable Test (For Srikanth, Starting Today)

Before building ANY code, you can start collecting data with a simple spreadsheet:

| Column | Description |
|--------|-------------|
| Timestamp | When you checked |
| Actual Nostril | L / R / Both |
| Actual Feeling | Grounded / Flowing / Intense / Restless / Spacious |
| Actual Energy | 1-5 |
| Actual Emotion | Peaceful / Excited / Anxious / Sad / Angry / Neutral |
| Note | Coffee, meal, exercise, argument, etc. |

Then AFTER collecting, compute what the hora/tattva/nadi SHOULD have been at each timestamp, and compare.

**Even 20 manual data points will show you whether the signal is there before we write a single line of code.**

---

## 12. Database Schema for Verification

```sql
CREATE TABLE swara_checkins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    checked_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- User-reported ground truth
    reported_nostril VARCHAR(10) NOT NULL,     -- 'left', 'right', 'both'
    reported_feeling VARCHAR(25) NOT NULL,      -- 'grounded', 'flowing', 'intense', 'restless', 'spacious'
    reported_energy INTEGER NOT NULL CHECK (reported_energy BETWEEN 1 AND 5),
    reported_clarity INTEGER NOT NULL CHECK (reported_clarity BETWEEN 1 AND 5),
    reported_emotion VARCHAR(20) NOT NULL,      -- 'peaceful', 'excited', 'anxious', 'sad', 'angry', 'neutral'
    reported_note TEXT,

    -- System predictions (frozen at check-in time)
    predicted_hora_planet VARCHAR(10) NOT NULL,
    predicted_hora_number INTEGER NOT NULL,
    predicted_nadi VARCHAR(15) NOT NULL,        -- 'ida', 'pingala', 'sushumna'
    predicted_nostril VARCHAR(10) NOT NULL,     -- 'left', 'right', 'both'
    predicted_tattva VARCHAR(15) NOT NULL,      -- 'prithvi', 'jala', 'agni', 'vayu', 'akasha'
    predicted_feeling VARCHAR(25) NOT NULL,
    predicted_energy INTEGER NOT NULL,
    predicted_guna VARCHAR(10) NOT NULL,        -- 'sattva', 'rajas', 'tamas'
    predicted_mental_state JSONB NOT NULL,

    -- Astrological context snapshot
    paksha VARCHAR(10) NOT NULL,               -- 'shukla', 'krishna'
    tithi INTEGER NOT NULL,
    paksha_predicted_nadi VARCHAR(15) NOT NULL,
    transit_moon_nakshatra VARCHAR(25) NOT NULL,
    transit_moon_sign VARCHAR(15) NOT NULL,
    current_mahadasha VARCHAR(10) NOT NULL,
    current_antardasha VARCHAR(10) NOT NULL,
    current_pratyantardasha VARCHAR(10),
    choghadiya_quality VARCHAR(15),
    ashtakavarga_score INTEGER,

    -- Confluence score
    confluence_score INTEGER NOT NULL CHECK (confluence_score BETWEEN 0 AND 6),
    confluence_factors JSONB NOT NULL,

    -- Computed accuracy (filled after submission)
    nadi_match BOOLEAN NOT NULL,
    tattva_match BOOLEAN NOT NULL,
    energy_delta INTEGER NOT NULL,
    clarity_delta INTEGER NOT NULL,
    emotion_match BOOLEAN NOT NULL,
    overall_accuracy FLOAT NOT NULL,

    -- Confounding variables
    time_bucket VARCHAR(15) NOT NULL,          -- 'dawn', 'morning', 'midday', 'afternoon', 'evening', 'night'
    cortisol_phase VARCHAR(15) NOT NULL,       -- 'rising', 'peak', 'declining', 'low', 'minimum'
    hours_since_wake FLOAT,
    confounder_flags TEXT[],                    -- ['caffeine', 'post_meal', 'exercise', 'poor_sleep']

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_swara_checkins_user ON swara_checkins(user_id, checked_at DESC);
CREATE INDEX idx_swara_checkins_hora ON swara_checkins(user_id, predicted_hora_planet);
CREATE INDEX idx_swara_checkins_confluence ON swara_checkins(user_id, confluence_score);
CREATE INDEX idx_swara_checkins_bucket ON swara_checkins(user_id, time_bucket);
```

---

## 13. Open Questions

1. **Notification timing:** Should check-in prompts fire at hora boundaries (testing hora transition accuracy) or at random times within horas (testing steady-state prediction)?
   **Recommendation:** Mix both. 70% random within hora, 30% at boundaries.

2. **User fatigue:** 16 check-ins/day in Phase 1 is demanding. Drop-off risk is high.
   **Mitigation:** Gamify with "Swara Streak" counter. Show live accuracy dashboard. Make it fascinating, not tedious.

3. **Observer effect:** Does checking your breath CHANGE your breath?
   **Yes, briefly.** The Swarodaya acknowledges this. Instruction to users: "Notice your breath for 3 seconds BEFORE the app prompt appears, then report what you noticed."

4. **Minimum viable dataset:** Can we draw conclusions from 1 user (Srikanth)?
   **For personal validation, yes.** For publishable statistical claims, we'd need 20-30 participants running the same protocol. Start with N=1 (yourself), then scale if results are promising.
