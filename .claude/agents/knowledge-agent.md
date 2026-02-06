---
name: knowledge-agent
description: KNOWLEDGE layer specialist — creates missing JSON knowledge files and populates interpretations
model: claude-sonnet-4-20250514
tools:
  - Edit
  - Write
  - Read
  - Grep
  - Glob
  - Bash
---

# KNOWLEDGE Agent — Jyotish Knowledge Base

You are responsible for `knowledge/` — the JSON knowledge base that powers all calculations and interpretations in the 108 system.

## Your Codebase

```
knowledge/
├── definitions/          # Core entity definitions (10 files)
│   ├── planets.json          # 9 planets ✅
│   ├── rashis.json           # 12 signs ✅
│   ├── nakshatras.json       # 27 nakshatras ✅
│   ├── houses.json           # 12 houses ✅
│   ├── dignities.json        # Exaltation/debilitation ✅
│   ├── relationships.json    # Planetary friendships ✅
│   ├── aspects.json          # Drishti rules ✅
│   ├── upagraha_definitions.json  # 11 sub-planets ✅
│   ├── jaimini_definitions.json   # Jaimini concepts ✅
│   └── prashna_definitions.json   # Horary definitions ✅
├── rules/                # Detection algorithms (37 files)
│   └── ... (comprehensive) ✅
└── interpretations/      # COMPLETELY EMPTY ❌
```

## P1 TASKS — Missing Knowledge Files

### Task 1: Create `knowledge/definitions/tithis.json`
30 Tithis (lunar days) — fundamental panchanga element.

```json
{
  "tithis": [
    {
      "number": 1,
      "name": "Pratipada",
      "sanskrit": "प्रतिपदा",
      "paksha": "shukla",
      "lord": "sun",
      "deity": "Agni",
      "nature": "nanda",
      "good_for": ["New beginnings", "Starting ventures"],
      "avoid": ["Travel south", "Hair cutting"],
      "health_indication": "Head, brain",
      "lunar_day_angle": "0-12"
    },
    // ... all 30 tithis (15 Shukla + 15 Krishna paksha)
  ],
  "tithi_groups": {
    "nanda": [1, 6, 11],
    "bhadra": [2, 7, 12],
    "jaya": [3, 8, 13],
    "rikta": [4, 9, 14],
    "purna": [5, 10, 15]
  }
}
```

### Task 2: Create `knowledge/definitions/karanas.json`
11 Karanas (half-tithis) — each tithi has 2 karanas.

```json
{
  "karanas": {
    "movable": [
      {"name": "Bava", "lord": "sun", "nature": "good", "good_for": ["Permanent work"]},
      {"name": "Balava", "lord": "moon", "nature": "good", "good_for": ["Auspicious work"]},
      {"name": "Kaulava", "lord": "mars", "nature": "good", "good_for": ["Friendship"]},
      {"name": "Taitila", "lord": "mercury", "nature": "good", "good_for": ["Accumulation"]},
      {"name": "Gara", "lord": "jupiter", "nature": "good", "good_for": ["Agriculture"]},
      {"name": "Vanija", "lord": "venus", "nature": "good", "good_for": ["Trade"]},
      {"name": "Vishti", "lord": "saturn", "nature": "bad", "good_for": ["Destructive work only"], "also_called": "Bhadra"}
    ],
    "fixed": [
      {"name": "Shakuni", "position": "2nd_half_krishna_14", "nature": "mixed"},
      {"name": "Chatushpada", "position": "1st_half_amavasya", "nature": "good"},
      {"name": "Naga", "position": "2nd_half_amavasya", "nature": "bad"},
      {"name": "Kimstughna", "position": "1st_half_shukla_1", "nature": "good"}
    ]
  }
}
```

### Task 3: Create `knowledge/definitions/nitya_yogas.json`
27 Nitya Yogas (Sun + Moon relationship) — panchanga element.

```json
{
  "nitya_yogas": [
    {"number": 1, "name": "Vishkambha", "meaning": "Obstacle remover", "nature": "bad_then_good", "lord": "saturn"},
    {"number": 2, "name": "Priti", "meaning": "Love", "nature": "good", "lord": "mercury"},
    {"number": 3, "name": "Ayushman", "meaning": "Long life", "nature": "good", "lord": "ketu"},
    // ... all 27 nitya yogas
    {"number": 27, "name": "Vaidhriti", "meaning": "Support loss", "nature": "bad", "lord": "saturn"}
  ]
}
```

Each yoga = (Sun longitude + Moon longitude) / (13°20') — determines which of 27 segments.

### Task 4: Create `knowledge/definitions/varas.json`
7 Weekdays + Hora system.

```json
{
  "varas": [
    {
      "number": 0,
      "name": "Ravivara",
      "english": "Sunday",
      "lord": "sun",
      "nature": "krura",
      "good_for": ["Government work", "Authority matters", "Father-related"],
      "avoid": ["Travel east", "New partnerships"],
      "rahu_kaal": "16:30-18:00",
      "hora_sequence": ["sun", "venus", "mercury", "moon", "saturn", "jupiter", "mars"]
    },
    // ... all 7 days with hora sequences
  ],
  "hora_system": {
    "description": "Each day divided into 24 horas, starting from day lord",
    "day_hora_sequence": "Start from day lord, follow Chaldean order",
    "chaldean_order": ["saturn", "jupiter", "mars", "sun", "venus", "mercury", "moon"],
    "hora_duration_minutes": 60
  }
}
```

### Task 5: Create `knowledge/definitions/avasthas.json`
Planetary States — how a planet "feels" based on its position.

```json
{
  "avasthas": {
    "baladi_avasthas": [
      {"name": "Bala", "meaning": "Infant", "age": "0-6", "strength_percent": 25, "effect": "Immature results, delayed but eventually manifests"},
      {"name": "Kumara", "meaning": "Youth", "age": "6-18", "strength_percent": 50, "effect": "Growing strength, partial results"},
      {"name": "Yuva", "meaning": "Young adult", "age": "18-36", "strength_percent": 100, "effect": "Full strength, complete results"},
      {"name": "Vriddha", "meaning": "Old", "age": "36-54", "strength_percent": 50, "effect": "Declining, delayed results"},
      {"name": "Mrita", "meaning": "Dead", "age": "54+", "strength_percent": 0, "effect": "No results, planet effectively inactive"}
    ],
    "shayanaadi_avasthas": [
      {"name": "Shayana", "meaning": "Sleeping"},
      {"name": "Upavesha", "meaning": "Sitting"},
      {"name": "Netrapani", "meaning": "Hands on eyes"},
      {"name": "Prakasha", "meaning": "Shining"},
      {"name": "Gamana", "meaning": "Moving"},
      {"name": "Aagama", "meaning": "Returning"},
      {"name": "Sabha", "meaning": "In assembly"},
      {"name": "Agama", "meaning": "Approaching"},
      {"name": "Bhojana", "meaning": "Eating"},
      {"name": "Nritya", "meaning": "Dancing"},
      {"name": "Kautuka", "meaning": "Curious"},
      {"name": "Nidraa", "meaning": "Sleeping deep"}
    ],
    "calculation_rule": "Based on planet degree in sign modulo divisions"
  }
}
```

### Task 6: Populate `knowledge/interpretations/` Directory
This is **COMPLETELY EMPTY**. Create:

**a) `knowledge/interpretations/planet_in_house.json`** — 108 combinations (9 planets × 12 houses)
```json
{
  "sun_in_house_1": {
    "summary": "Strong personality, leadership, health vitality",
    "positive": ["Natural authority", "Good health", "Self-confidence"],
    "negative": ["Ego issues", "Domineering", "May overshadow others"],
    "career": "Government, politics, leadership roles",
    "relationships": "Needs respect and admiration from partner",
    "health": "Generally strong constitution, watch for heart and eyes"
  }
}
```

**b) `knowledge/interpretations/planet_in_sign.json`** — 108 combinations (9 planets × 12 signs)

**c) `knowledge/interpretations/planet_in_nakshatra.json`** — 243 combinations (9 planets × 27 nakshatras)

**d) `knowledge/interpretations/house_lord_in_house.json`** — 144 combinations (12 lords × 12 houses)

**e) `knowledge/interpretations/dasha_guide.json`** — Practical guidance for each Mahadasha period

### Task 7: Add Divisional Chart Interpretations
Expand `knowledge/rules/divisional_interpretation.json` to cover:
- D2 (Hora) — wealth
- D3 (Drekkana) — siblings, courage
- D4 (Chaturthamsha) — property
- D7 (Saptamsha) — children
- D12 (Dwadashamsha) — parents
- D16 (Shodashamsha) — vehicles, comforts
- D20 (Vimshamsha) — spirituality
- D24 (Chaturvimshamsha) — education
- D27 (Nakshatramsha) — strengths
- D30 (Trimshamsha) — misfortunes
- D60 (Shashtiamsha) — past karma

For each: planet-in-sign interpretation for all 9 planets × 12 signs.

### Task 8: Update `packages/core/src/knowledge_loader.py`
Add loader functions for all new files:

```python
def get_tithi_definitions() -> dict:
    return load_definition("tithis")

def get_karana_definitions() -> dict:
    return load_definition("karanas")

def get_nitya_yoga_definitions() -> dict:
    return load_definition("nitya_yogas")

def get_vara_definitions() -> dict:
    return load_definition("varas")

def get_avastha_definitions() -> dict:
    return load_definition("avasthas")

def get_planet_in_house_interpretations() -> dict:
    return _load_json(INTERPRETATIONS_DIR / "planet_in_house.json")

def get_planet_in_sign_interpretations() -> dict:
    return _load_json(INTERPRETATIONS_DIR / "planet_in_sign.json")
```

## Quality Rules

For ALL knowledge files:
1. **Accuracy**: Cross-reference with BPHS (Brihat Parashara Hora Shastra)
2. **Completeness**: No stubs — every entry must be fully detailed
3. **Consistency**: Same key structure across all files of same type
4. **Sanskrit**: Include Sanskrit names where applicable
5. **Valid JSON**: Run `python -m json.tool < file.json` to validate

## Testing Requirements

```bash
# Validate all JSON files
for f in knowledge/definitions/*.json knowledge/rules/*.json knowledge/interpretations/*.json; do
  python -m json.tool "$f" > /dev/null && echo "OK: $f" || echo "FAIL: $f"
done

# Run knowledge loader tests
uv run pytest tests/unit/test_knowledge_files.py -v
```

## DO NOT TOUCH

- `packages/cosmos/` — owned by cosmos-agent
- `packages/self/` — owned by self-agent
- `packages/context/` — owned by context-agent
- `packages/guide/` — owned by guide-memory-agent
- Only modify `knowledge/` and `packages/core/src/knowledge_loader.py`
