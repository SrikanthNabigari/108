# 108 Knowledge Architecture

## Overview

The knowledge base is divided into two categories:
- **DEFINITIONS**: Static reference data ("What is X?")
- **RULES**: Detection/calculation logic ("How to detect X?")

---

## DEFINITIONS (knowledge/definitions/)

### Currently Implemented ✅

| File | Content | Status |
|------|---------|--------|
| `planets.json` | 9 Grahas with nature, rulership, friends/enemies, karakas | ✅ Basic |
| `rashis.json` | 12 Signs with element, quality, ruler, body parts | ✅ Basic |
| `nakshatras.json` | 27 Nakshatras with lord, deity, symbol, padas | ✅ Complete |
| `houses.json` | 12 Bhavas with significations, karaka, category | ✅ Basic |

### Needed for V2 ❌

| File | Content | Priority | Source |
|------|---------|----------|--------|
| `aspects.json` | Planetary aspects (drishti) - full, 3/4, 1/2, 1/4 | HIGH | BPHS Ch. 28 |
| `dignities.json` | Complete dignity table - exalt, debilitate, mool trikona, own, friend/enemy signs | HIGH | BPHS Ch. 3 |
| `karakas.json` | Sthira & Chara karakas for all life areas | HIGH | Jaimini Sutras |
| `vargas.json` | 16 divisional charts (D1-D60) with significations | HIGH | BPHS Ch. 6-7 |
| `dashas.json` | Dasha system definitions - Vimshottari, Ashtottari, Yogini, Chara, Narayana | HIGH | BPHS Ch. 46 |
| `ayanamsas.json` | All ayanamsa systems with values and usage | MEDIUM | Various |
| `tithis.json` | 30 lunar days with deity, nature, activities | MEDIUM | Muhurta texts |
| `karanas.json` | 11 karanas (half-tithis) with nature | MEDIUM | Muhurta texts |
| `yogas_panchanga.json` | 27 Nitya yogas (not planetary yogas!) | MEDIUM | Muhurta texts |
| `varas.json` | 7 weekdays with planetary hora sequence | MEDIUM | BPHS |
| `upagrahas.json` | Sub-planets - Gulika, Mandi, Dhuma, Vyatipata, etc. | LOW | BPHS Ch. 25 |
| `fixed_stars.json` | Important fixed stars used in Jyotish | LOW | Traditional |
| `special_lagnas.json` | Hora, Ghati, Bhava, Varnada, Sree lagna | LOW | Jaimini |

---

## RULES (knowledge/rules/)

### Currently Implemented ✅

| File | Content | Count | Status |
|------|---------|-------|--------|
| `yoga_master.json` | Planetary yoga detection rules | 522 | ✅ Complete |
| `dosha_master.json` | Dosha detection rules | 55 | ✅ Complete |

### Needed for V2 ❌

| File | Content | Priority | Source |
|------|---------|----------|--------|
| `shadbala_rules.json` | 6-fold strength calculation formulas | HIGH | BPHS Ch. 27 |
| `ashtakavarga_rules.json` | Benefic point calculation for each planet | HIGH | BPHS Ch. 66 |
| `compatibility_rules.json` | Ashta Kuta matching (36 points system) | HIGH | Traditional |
| `muhurta_rules.json` | Electional astrology rules for activities | HIGH | Muhurta Chintamani |
| `transit_rules.json` | Gochara effects from Moon sign | HIGH | BPHS Ch. 65 |
| `dasha_effects.json` | MD/AD/PD interpretation rules | HIGH | BPHS Ch. 46-48 |
| `remedies_rules.json` | Gemstone, mantra, charity recommendations | MEDIUM | Traditional |
| `prediction_rules.json` | Event timing and probability rules | MEDIUM | Various |
| `longevity_rules.json` | Ayurdaya calculation methods | LOW | BPHS Ch. 44 |
| `arudha_rules.json` | Arudha pada calculation and effects | LOW | Jaimini |

---

## Detailed Specifications

### 1. aspects.json (DEFINITIONS)

```json
{
  "aspects": {
    "full_aspects": {
      "all_planets": [7],
      "mars": [4, 8],
      "jupiter": [5, 9],
      "saturn": [3, 10],
      "rahu": [5, 9],
      "ketu": [5, 9]
    },
    "partial_aspects": {
      "3_4_strength": "Planets aspect 3rd and 10th with 3/4 strength",
      "1_2_strength": "Planets aspect 4th and 8th with 1/2 strength",
      "1_4_strength": "Planets aspect 5th and 9th with 1/4 strength"
    }
  }
}
```

### 2. dignities.json (DEFINITIONS)

```json
{
  "dignities": {
    "sun": {
      "exaltation": {"sign": "aries", "degree": 10},
      "debilitation": {"sign": "libra", "degree": 10},
      "mool_trikona": {"sign": "leo", "degrees": [0, 20]},
      "own_signs": ["leo"],
      "friend_signs": ["aries", "sagittarius", "scorpio"],
      "enemy_signs": ["taurus", "libra", "capricorn", "aquarius"],
      "neutral_signs": ["gemini", "virgo", "cancer", "pisces"]
    }
    // ... for all 9 planets
  }
}
```

### 3. karakas.json (DEFINITIONS)

```json
{
  "sthira_karakas": {
    "sun": ["soul", "father", "government", "authority", "health", "ego"],
    "moon": ["mind", "mother", "emotions", "public", "water", "travel"],
    "mars": ["courage", "siblings", "property", "energy", "surgery", "military"],
    "mercury": ["intellect", "speech", "commerce", "writing", "friends", "skin"],
    "jupiter": ["wisdom", "children", "guru", "dharma", "wealth", "husband"],
    "venus": ["love", "wife", "arts", "luxury", "vehicles", "beauty"],
    "saturn": ["longevity", "servants", "sorrow", "discipline", "delays", "karma"],
    "rahu": ["foreign", "obsession", "illusion", "technology", "outcaste"],
    "ketu": ["moksha", "spirituality", "past_life", "detachment", "occult"]
  },
  "chara_karakas": {
    "description": "Based on highest to lowest degree (excluding Rahu/Ketu)",
    "order": ["atmakaraka", "amatyakaraka", "bhratrikaraka", "matrikaraka",
              "putrakaraka", "gnatikaraka", "darakaraka"],
    "calculation": "Sorted by longitude within sign (0-30)"
  },
  "bhava_karakas": {
    "1": "sun",
    "2": "jupiter",
    "3": "mars",
    "4": "moon",
    "5": "jupiter",
    "6": "mars",
    "7": "venus",
    "8": "saturn",
    "9": "jupiter",
    "10": "sun",
    "11": "jupiter",
    "12": "saturn"
  }
}
```

### 4. vargas.json (DEFINITIONS)

```json
{
  "divisional_charts": {
    "D1": {"name": "Rashi", "division": 1, "signifies": ["body", "general_life", "self"]},
    "D2": {"name": "Hora", "division": 2, "signifies": ["wealth", "resources"]},
    "D3": {"name": "Drekkana", "division": 3, "signifies": ["siblings", "courage"]},
    "D4": {"name": "Chaturthamsa", "division": 4, "signifies": ["property", "fortune"]},
    "D7": {"name": "Saptamsa", "division": 7, "signifies": ["children", "creativity"]},
    "D9": {"name": "Navamsa", "division": 9, "signifies": ["spouse", "dharma", "fortune"]},
    "D10": {"name": "Dasamsa", "division": 10, "signifies": ["career", "profession"]},
    "D12": {"name": "Dwadasamsa", "division": 12, "signifies": ["parents", "ancestry"]},
    "D16": {"name": "Shodasamsa", "division": 16, "signifies": ["vehicles", "happiness"]},
    "D20": {"name": "Vimsamsa", "division": 20, "signifies": ["spirituality", "upasana"]},
    "D24": {"name": "Chaturvimsamsa", "division": 24, "signifies": ["education", "learning"]},
    "D27": {"name": "Nakshatramsa", "division": 27, "signifies": ["strength", "weakness"]},
    "D30": {"name": "Trimsamsa", "division": 30, "signifies": ["evils", "misfortune"]},
    "D40": {"name": "Khavedamsa", "division": 40, "signifies": ["auspicious_effects"]},
    "D45": {"name": "Akshavedamsa", "division": 45, "signifies": ["all_matters"]},
    "D60": {"name": "Shashtiamsa", "division": 60, "signifies": ["past_karma", "all_matters"]}
  }
}
```

### 5. shadbala_rules.json (RULES)

```json
{
  "shadbala_components": {
    "sthana_bala": {
      "name": "Positional Strength",
      "sub_components": {
        "uccha_bala": "Exaltation strength (0-60 virupas)",
        "saptavargaja_bala": "Strength from 7 vargas",
        "ojhayugma_bala": "Odd-even sign strength",
        "kendra_bala": "Angular house strength",
        "drekkana_bala": "Decanate strength"
      },
      "max_value": 180
    },
    "dig_bala": {
      "name": "Directional Strength",
      "formula": "Based on planet's position from its directional strength house",
      "directions": {
        "sun": {"strong_house": 10, "weak_house": 4},
        "moon": {"strong_house": 4, "weak_house": 10},
        "mars": {"strong_house": 10, "weak_house": 4},
        "mercury": {"strong_house": 1, "weak_house": 7},
        "jupiter": {"strong_house": 1, "weak_house": 7},
        "venus": {"strong_house": 4, "weak_house": 10},
        "saturn": {"strong_house": 7, "weak_house": 1}
      },
      "max_value": 60
    },
    "kala_bala": {
      "name": "Temporal Strength",
      "sub_components": {
        "natonnata_bala": "Day/night strength",
        "paksha_bala": "Lunar phase strength",
        "tribhaga_bala": "Day/night thirds",
        "abda_bala": "Year lord strength",
        "masa_bala": "Month lord strength",
        "vara_bala": "Weekday lord strength",
        "hora_bala": "Hour lord strength",
        "ayana_bala": "Declination strength",
        "yuddha_bala": "Planetary war strength"
      },
      "max_value": 180
    },
    "chesta_bala": {
      "name": "Motional Strength",
      "description": "Based on planet's speed relative to mean motion",
      "max_value": 60
    },
    "naisargika_bala": {
      "name": "Natural Strength",
      "fixed_values": {
        "sun": 60, "moon": 51.43, "venus": 42.85,
        "jupiter": 34.28, "mercury": 25.71, "mars": 17.14, "saturn": 8.57
      }
    },
    "drik_bala": {
      "name": "Aspectual Strength",
      "description": "Based on aspects received from benefics/malefics",
      "max_value": 60
    }
  },
  "minimum_required": {
    "sun": 390, "moon": 360, "mars": 300,
    "mercury": 420, "jupiter": 390, "venus": 330, "saturn": 300
  }
}
```

### 6. ashtakavarga_rules.json (RULES)

```json
{
  "ashtakavarga": {
    "description": "Each planet contributes bindus (points) based on position from 8 reference points",
    "reference_points": ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "lagna"],
    "sun_contributions": {
      "from_sun": [1, 2, 4, 7, 8, 9, 10, 11],
      "from_moon": [3, 6, 10, 11],
      "from_mars": [1, 2, 4, 7, 8, 9, 10, 11],
      "from_mercury": [3, 5, 6, 9, 10, 11, 12],
      "from_jupiter": [5, 6, 9, 11],
      "from_venus": [6, 7, 12],
      "from_saturn": [1, 2, 4, 7, 8, 9, 10, 11],
      "from_lagna": [3, 4, 6, 10, 11, 12],
      "max_bindus": 48
    },
    // ... similar for moon, mars, mercury, jupiter, venus, saturn
    "sarvashtakavarga": {
      "description": "Sum of all planet bindus for each sign",
      "max_total": 337,
      "interpretation": {
        "above_28": "Excellent results",
        "25_to_28": "Good results",
        "22_to_25": "Average results",
        "below_22": "Challenging results"
      }
    }
  }
}
```

### 7. compatibility_rules.json (RULES)

```json
{
  "ashta_kuta": {
    "varna": {"max_points": 1, "description": "Spiritual compatibility"},
    "vashya": {"max_points": 2, "description": "Mutual attraction"},
    "tara": {"max_points": 3, "description": "Birth star compatibility"},
    "yoni": {"max_points": 4, "description": "Sexual compatibility"},
    "graha_maitri": {"max_points": 5, "description": "Mental compatibility"},
    "gana": {"max_points": 6, "description": "Temperament match"},
    "bhakoot": {"max_points": 7, "description": "Health & wealth"},
    "nadi": {"max_points": 8, "description": "Health of progeny"}
  },
  "total_points": 36,
  "minimum_required": 18,
  "interpretation": {
    "above_28": "Excellent match",
    "21_to_28": "Good match",
    "18_to_21": "Average match",
    "below_18": "Not recommended"
  },
  "dosha_exceptions": {
    "nadi_dosha": "Cancelled if same nakshatra different pada",
    "bhakoot_dosha": "Cancelled if lords are friends"
  }
}
```

### 8. dasha_effects.json (RULES)

```json
{
  "vimshottari_dasha": {
    "sun": {
      "duration_years": 6,
      "general_effects": ["Authority", "Government", "Father", "Health focus"],
      "positive": ["Recognition", "Leadership", "Vitality"],
      "negative": ["Ego conflicts", "Heart issues", "Authority problems"],
      "house_effects": {
        "1": "Self-confidence, health focus",
        "2": "Wealth from government, family prominence",
        "10": "Career peak, recognition"
      }
    },
    "moon": {
      "duration_years": 10,
      "general_effects": ["Mind", "Mother", "Public", "Emotions"],
      "positive": ["Popularity", "Emotional growth", "Travel"],
      "negative": ["Mental unrest", "Mother's health", "Mood swings"]
    },
    // ... for all 9 planets
  },
  "antardasha_modifications": {
    "friendly_lords": "Results enhanced by 25%",
    "enemy_lords": "Results reduced, obstacles",
    "neutral_lords": "Mixed results"
  }
}
```

---

## Implementation Priority

### Phase 1 (HIGH - Core Calculations)
1. `dignities.json` - Essential for strength calculations
2. `aspects.json` - Required for yoga/dosha detection
3. `shadbala_rules.json` - Planetary strength
4. `karakas.json` - Significator analysis

### Phase 2 (HIGH - Predictions)
5. `dasha_effects.json` - Timing predictions
6. `transit_rules.json` - Current influences
7. `ashtakavarga_rules.json` - Transit strength

### Phase 3 (MEDIUM - Compatibility & Muhurta)
8. `compatibility_rules.json` - Marriage matching
9. `muhurta_rules.json` - Electional astrology
10. `vargas.json` - Divisional charts

### Phase 4 (MEDIUM - Panchanga)
11. `tithis.json` - Lunar days
12. `karanas.json` - Half-tithis
13. `yogas_panchanga.json` - Nitya yogas
14. `varas.json` - Weekdays

### Phase 5 (LOW - Advanced)
15. `ayanamsas.json` - Multiple systems
16. `upagrahas.json` - Sub-planets
17. `remedies_rules.json` - Recommendations
18. `special_lagnas.json` - Jaimini lagnas

---

## File Naming Convention

- **DEFINITIONS**: `{concept}.json` (noun, plural)
  - `planets.json`, `nakshatras.json`, `karakas.json`

- **RULES**: `{concept}_rules.json` (noun + "_rules")
  - `shadbala_rules.json`, `compatibility_rules.json`

---

## Estimated Work

| Phase | Files | Est. Time |
|-------|-------|-----------|
| Phase 1 | 4 files | 2-3 hours |
| Phase 2 | 3 files | 2-3 hours |
| Phase 3 | 3 files | 2-3 hours |
| Phase 4 | 4 files | 1-2 hours |
| Phase 5 | 4 files | 2-3 hours |

**Total**: ~18 new files, ~10-14 hours of work
