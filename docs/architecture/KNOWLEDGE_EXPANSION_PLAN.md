# 108 Knowledge Expansion Plan (V2 Complete)

## Executive Summary

Current state has significant hardcoded knowledge across all packages. This plan externalizes everything to JSON for maintainability and accuracy.

---

## Current State Analysis

### Packages with Hardcoded Knowledge

| Package | File | Hardcoded Items | Priority |
|---------|------|-----------------|----------|
| **cosmos** | houses.py | HOUSE_SIGNIFICATIONS, HOUSE_KARAKAS, SIGN_RULERS | HIGH |
| **cosmos** | divisional.py | Planet rulerships (ERRORS!), exaltations (ERRORS!) | CRITICAL |
| **cosmos** | panchanga.py | TITHI_NAMES, YOGA_NAMES, KARANA_NAMES, VARA_NAMES | LOW |
| **self** | yoga_detector.py | PLANET_RULERSHIP, PLANET_EXALTATION, PLANET_DEBILITATION | HIGH |
| **self** | dosha_detector.py | All orbs, Mars characteristics, remedies, Kaal Sarp types | HIGH |
| **self** | strength.py | NAISARGIKA_BALA, DIG_BALA, ASHTAKAVARGA matrix, FRIENDS | CRITICAL |
| **context** | dasha.py | DASHA_YEARS, NAKSHATRA_LORDS | HIGH |
| **context** | transits.py | GOCHARA_FAVORABLE, VEDHA_POINTS, TRANSIT_EFFECTS | CRITICAL |
| **context** | muhurta.py | RAHU_KAAL, ACTIVITY_RULES, CHOGHADIYA, scoring | HIGH |

---

## Knowledge Architecture

```
knowledge/
├── definitions/                    # Static reference data ("What is X?")
│   ├── planets.json               ✅ EXISTS - needs expansion
│   ├── rashis.json                ✅ EXISTS - needs expansion
│   ├── nakshatras.json            ✅ EXISTS - needs expansion
│   ├── houses.json                ✅ EXISTS - needs expansion
│   ├── aspects.json               ❌ CREATE - planetary aspects/drishti
│   ├── dignities.json             ❌ CREATE - complete dignity table
│   ├── relationships.json         ❌ CREATE - planetary friendships
│   ├── karakas.json               ❌ CREATE - all karaka types
│   ├── vargas.json                ❌ CREATE - 16 divisional charts
│   ├── tithis.json                ❌ CREATE - 30 lunar days
│   ├── karanas.json               ❌ CREATE - 11 half-tithis
│   ├── nitya_yogas.json           ❌ CREATE - 27 panchanga yogas
│   ├── varas.json                 ❌ CREATE - weekdays + horas
│   └── upagrahas.json             ❌ CREATE - sub-planets
│
└── rules/                          # Detection/calculation logic
    ├── yoga_master.json           ✅ EXISTS (522 yogas)
    ├── dosha_master.json          ✅ EXISTS (55 doshas)
    ├── shadbala_rules.json        ❌ CREATE - 6-fold strength
    ├── ashtakavarga_rules.json    ❌ CREATE - 8-fold points
    ├── dasha_rules.json           ❌ CREATE - dasha effects/interpretations
    ├── transit_rules.json         ❌ CREATE - gochara effects
    ├── muhurta_rules.json         ❌ CREATE - electional astrology
    ├── compatibility_rules.json   ❌ CREATE - Ashta Kuta matching
    └── remedies_rules.json        ❌ CREATE - gemstones, mantras
```

---

## Detailed File Specifications

### PHASE 1: Core Definitions (Critical - Fix Errors)

#### 1.1 dignities.json
**Purpose:** Single source of truth for all planet dignities
**Eliminates hardcoding in:** yoga_detector.py, dosha_detector.py, strength.py, divisional.py

```json
{
  "metadata": {
    "source": "BPHS Chapter 3",
    "description": "Complete planetary dignity table"
  },
  "dignities": {
    "sun": {
      "own_signs": ["leo"],
      "exaltation": {"sign": "aries", "degree": 10, "orb": 3},
      "debilitation": {"sign": "libra", "degree": 10},
      "moolatrikona": {"sign": "leo", "start": 0, "end": 20},
      "combustion_distance": null,
      "dignity_strengths": {
        "exalted": 1.0,
        "moolatrikona": 0.75,
        "own_sign": 0.5,
        "friend_sign": 0.25,
        "neutral_sign": 0.0,
        "enemy_sign": -0.25,
        "debilitated": -1.0
      }
    },
    "moon": {
      "own_signs": ["cancer"],
      "exaltation": {"sign": "taurus", "degree": 3, "orb": 3},
      "debilitation": {"sign": "scorpio", "degree": 3},
      "moolatrikona": {"sign": "taurus", "start": 3, "end": 30},
      "combustion_distance": 12
    },
    // ... all 9 planets
  }
}
```

#### 1.2 relationships.json
**Purpose:** Planetary friendships and enmities
**Eliminates hardcoding in:** strength.py (FRIENDS dict)

```json
{
  "natural_relationships": {
    "sun": {
      "friends": ["moon", "mars", "jupiter"],
      "enemies": ["venus", "saturn"],
      "neutral": ["mercury"]
    },
    // ... all planets
  },
  "temporary_relationships": {
    "description": "Based on positions from each other",
    "rules": {
      "friends_positions": [2, 3, 4, 10, 11, 12],
      "enemies_positions": [1, 5, 6, 7, 8, 9]
    }
  },
  "compound_relationship": {
    "description": "Natural + Temporary combined",
    "matrix": {
      "friend_friend": "intimate_friend",
      "friend_neutral": "friend",
      "friend_enemy": "neutral",
      "neutral_friend": "friend",
      "neutral_neutral": "neutral",
      "neutral_enemy": "enemy",
      "enemy_friend": "neutral",
      "enemy_neutral": "enemy",
      "enemy_enemy": "bitter_enemy"
    }
  }
}
```

#### 1.3 aspects.json
**Purpose:** Complete aspect rules with strengths
**Eliminates hardcoding in:** yoga_detector.py, dosha_detector.py

```json
{
  "full_aspects": {
    "all_planets": {
      "houses": [7],
      "strength": 1.0,
      "description": "All planets aspect 7th house with full strength"
    },
    "mars": {
      "houses": [4, 7, 8],
      "strength": {"4": 0.75, "7": 1.0, "8": 0.75}
    },
    "jupiter": {
      "houses": [5, 7, 9],
      "strength": {"5": 1.0, "7": 1.0, "9": 1.0}
    },
    "saturn": {
      "houses": [3, 7, 10],
      "strength": {"3": 0.75, "7": 1.0, "10": 0.75}
    },
    "rahu": {"houses": [5, 7, 9], "strength": 1.0},
    "ketu": {"houses": [5, 7, 9], "strength": 1.0}
  },
  "aspect_orbs": {
    "conjunction": 8,
    "opposition": 8,
    "trine": 6,
    "square": 6,
    "sextile": 4
  }
}
```

---

### PHASE 2: Strength Calculations (Critical)

#### 2.1 shadbala_rules.json
**Purpose:** Complete Shadbala calculation rules
**Eliminates hardcoding in:** strength.py

```json
{
  "metadata": {
    "source": "BPHS Chapter 27",
    "total_components": 6,
    "unit": "virupas"
  },
  "sthana_bala": {
    "max_value": 180,
    "components": {
      "uchcha_bala": {
        "max": 60,
        "formula": "60 * (1 - distance_from_exaltation / 180)"
      },
      "saptavargaja_bala": {
        "max": 45,
        "vargas": ["D1", "D2", "D3", "D9", "D12", "D30", "D7"],
        "weights": [5, 2, 3, 9, 2, 4, 2.5]
      },
      "ojhayugma_bala": {
        "max": 15,
        "rules": {
          "odd_sign_odd_navamsa": {"benefic": 15, "malefic": 0},
          "even_sign_even_navamsa": {"benefic": 0, "malefic": 15}
        }
      },
      "kendradi_bala": {
        "max": 60,
        "values": {"kendra": 60, "panapara": 30, "apoklima": 15}
      },
      "drekkana_bala": {
        "max": 15,
        "rules": "Based on rising/culminating/setting decanate"
      }
    }
  },
  "dig_bala": {
    "max_value": 60,
    "strong_houses": {
      "sun": 10, "mars": 10,
      "moon": 4, "venus": 4,
      "mercury": 1, "jupiter": 1,
      "saturn": 7
    },
    "formula": "60 * (1 - angular_distance_from_strong_house / 180)"
  },
  "kala_bala": {
    "max_value": 180,
    "components": {
      "nathonnatha_bala": {
        "day_strong": ["sun", "jupiter", "venus"],
        "night_strong": ["moon", "mars", "saturn"],
        "always_strong": ["mercury"]
      },
      "paksha_bala": {
        "shukla_strong": ["moon", "jupiter", "venus", "mercury"],
        "krishna_strong": ["sun", "mars", "saturn"]
      },
      "hora_bala": 60,
      "vara_bala": 45,
      "masa_bala": 30,
      "abda_bala": 15,
      "ayana_bala": 30,
      "yuddha_bala": 60
    }
  },
  "chesta_bala": {
    "max_value": 60,
    "description": "Based on planetary motion (retrograde/direct/stationary)"
  },
  "naisargika_bala": {
    "description": "Natural permanent strength",
    "values": {
      "sun": 60.00,
      "moon": 51.43,
      "venus": 42.86,
      "jupiter": 34.29,
      "mercury": 25.71,
      "mars": 17.14,
      "saturn": 8.57
    }
  },
  "drik_bala": {
    "max_value": 60,
    "description": "Strength from aspects received"
  },
  "minimum_required": {
    "sun": 390, "moon": 360, "mars": 300,
    "mercury": 420, "jupiter": 390, "venus": 330, "saturn": 300
  }
}
```

#### 2.2 ashtakavarga_rules.json
**Purpose:** Complete Ashtakavarga point matrix
**Eliminates hardcoding in:** strength.py (ASHTAKAVARGA_POINTS - huge matrix!)

```json
{
  "metadata": {
    "source": "BPHS Chapter 66",
    "description": "Benefic points contributed by each reference point"
  },
  "reference_points": ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "lagna"],
  "contributions": {
    "sun": {
      "from_sun": [1, 2, 4, 7, 8, 9, 10, 11],
      "from_moon": [3, 6, 10, 11],
      "from_mars": [1, 2, 4, 7, 8, 9, 10, 11],
      "from_mercury": [3, 5, 6, 9, 10, 11, 12],
      "from_jupiter": [5, 6, 9, 11],
      "from_venus": [6, 7, 12],
      "from_saturn": [1, 2, 4, 7, 8, 9, 10, 11],
      "from_lagna": [3, 4, 6, 10, 11, 12]
    },
    "moon": {
      "from_sun": [3, 6, 7, 8, 10, 11],
      "from_moon": [1, 3, 6, 7, 10, 11],
      "from_mars": [2, 3, 5, 6, 9, 10, 11],
      "from_mercury": [1, 3, 4, 5, 7, 8, 10, 11],
      "from_jupiter": [1, 4, 7, 8, 10, 11, 12],
      "from_venus": [3, 4, 5, 7, 9, 10, 11],
      "from_saturn": [3, 5, 6, 11],
      "from_lagna": [3, 6, 10, 11]
    },
    // ... mars, mercury, jupiter, venus, saturn
  },
  "interpretation": {
    "sign_strength": {
      "0-22": "Very weak",
      "23-25": "Weak",
      "26-28": "Average",
      "29-32": "Good",
      "33+": "Excellent"
    }
  }
}
```

---

### PHASE 3: Timing & Context

#### 3.1 dasha_rules.json
**Purpose:** Dasha periods and interpretation rules
**Eliminates hardcoding in:** dasha.py

```json
{
  "vimshottari": {
    "total_years": 120,
    "periods": {
      "ketu": {"years": 7, "order": 1},
      "venus": {"years": 20, "order": 2},
      "sun": {"years": 6, "order": 3},
      "moon": {"years": 10, "order": 4},
      "mars": {"years": 7, "order": 5},
      "rahu": {"years": 18, "order": 6},
      "jupiter": {"years": 16, "order": 7},
      "saturn": {"years": 19, "order": 8},
      "mercury": {"years": 17, "order": 9}
    },
    "nakshatra_lords": {
      "1": "ketu", "2": "venus", "3": "sun",
      "4": "moon", "5": "mars", "6": "rahu",
      "7": "jupiter", "8": "saturn", "9": "mercury",
      "10": "ketu", "11": "venus", "12": "sun",
      // ... all 27
    }
  },
  "effects": {
    "sun": {
      "general": ["Authority", "Government", "Father", "Health"],
      "positive": ["Recognition", "Leadership", "Vitality"],
      "negative": ["Ego conflicts", "Heart issues", "Authority problems"],
      "by_house": {
        "1": "Self-confidence, health focus",
        "2": "Wealth from government",
        "10": "Career peak"
        // ... all 12 houses
      }
    }
    // ... all 9 planets
  }
}
```

#### 3.2 transit_rules.json
**Purpose:** Gochara effects and Sade Sati rules
**Eliminates hardcoding in:** transits.py (GOCHARA_FAVORABLE, VEDHA_POINTS, TRANSIT_EFFECTS)

```json
{
  "gochara_favorable": {
    "sun": [3, 6, 10, 11],
    "moon": [1, 3, 6, 7, 10, 11],
    "mars": [3, 6, 11],
    "mercury": [2, 4, 6, 8, 10, 11],
    "jupiter": [2, 5, 7, 9, 11],
    "venus": [1, 2, 3, 4, 5, 8, 9, 11, 12],
    "saturn": [3, 6, 11],
    "rahu": [3, 6, 10, 11],
    "ketu": [3, 6, 10, 11]
  },
  "vedha_points": {
    "sun": {"3": 9, "6": 12, "10": 4, "11": 5},
    "moon": {"1": 5, "3": 9, "6": 12, "7": 2, "10": 4, "11": 8},
    // ... all planets
  },
  "transit_effects": {
    "sun": {
      "1": {"positive": ["Authority", "Fame"], "negative": ["Health strain"]},
      "2": {"positive": [], "negative": ["Financial challenges", "Family tension"]},
      // ... all 12 houses
    }
    // ... all planets
  },
  "sade_sati": {
    "phases": {
      "rising": {"house_from_moon": 12, "duration_years": 2.5},
      "peak": {"house_from_moon": 1, "duration_years": 2.5},
      "setting": {"house_from_moon": 2, "duration_years": 2.5}
    },
    "effects_by_phase": {
      "rising": ["Mental stress", "Obstacles beginning"],
      "peak": ["Maximum pressure", "Transformation"],
      "setting": ["Financial pressure", "Gradual relief"]
    },
    "remedies": ["Shani mantra", "Blue sapphire (with caution)", "Saturday fasting"]
  },
  "dhaiya": {
    "positions": [4, 8],
    "duration_years": 2.5
  }
}
```

#### 3.3 muhurta_rules.json
**Purpose:** Electional astrology rules
**Eliminates hardcoding in:** muhurta.py

```json
{
  "rahu_kaal": {
    "sunday": 8, "monday": 2, "tuesday": 7, "wednesday": 5,
    "thursday": 6, "friday": 4, "saturday": 3
  },
  "yamaghanda": {
    "sunday": 5, "monday": 4, "tuesday": 3, "wednesday": 2,
    "thursday": 1, "friday": 7, "saturday": 6
  },
  "gulika": {
    "sunday": 7, "monday": 6, "tuesday": 5, "wednesday": 4,
    "thursday": 3, "friday": 2, "saturday": 1
  },
  "choghadiya": {
    "order": {
      "day": {
        "sunday": ["Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"]
        // ... all days
      },
      "night": { /* ... */ }
    },
    "quality": {
      "Amrit": "excellent",
      "Shubh": "good",
      "Labh": "good",
      "Chal": "neutral",
      "Rog": "poor",
      "Kaal": "poor",
      "Udveg": "poor"
    }
  },
  "activity_rules": {
    "marriage": {
      "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
      "avoid_tithis": [4, 6, 8, 9, 14, 15, 30],
      "good_nakshatras": ["Rohini", "Mrigashira", "Magha", "Uttara Phalguni",
                          "Hasta", "Swati", "Anuradha", "Mula", "Uttara Ashadha",
                          "Uttara Bhadrapada", "Revati"],
      "avoid_nakshatras": ["Bharani", "Krittika", "Ardra", "Ashlesha",
                           "Jyeshtha", "Moola"],
      "good_varas": ["monday", "wednesday", "thursday", "friday"],
      "avoid_varas": ["saturday", "tuesday"]
    }
    // ... travel, business_start, house_entry, surgery, etc.
  },
  "scoring": {
    "base_score": 50,
    "good_tithi": 15,
    "avoid_tithi": -20,
    "good_nakshatra": 20,
    "avoid_nakshatra": -25,
    "good_vara": 15,
    "avoid_vara": -15,
    "rahu_kaal_penalty": -20,
    "yamaghanda_penalty": -25,
    "gulika_penalty": -10
  }
}
```

---

### PHASE 4: Compatibility & Remedies

#### 4.1 compatibility_rules.json
**Purpose:** Ashta Kuta marriage matching

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
  "yoni_animals": {
    "Ashwini": "horse", "Bharani": "elephant", "Krittika": "goat",
    // ... all 27 nakshatras
  },
  "yoni_compatibility": {
    "horse": {"horse": 4, "elephant": 2, "goat": 2 /* ... */}
    // ... full matrix
  }
}
```

#### 4.2 remedies_rules.json
**Purpose:** Gemstones, mantras, and remedial measures

```json
{
  "gemstones": {
    "sun": {"primary": "ruby", "secondary": "garnet", "carat_min": 3},
    "moon": {"primary": "pearl", "secondary": "moonstone", "carat_min": 4},
    "mars": {"primary": "red_coral", "secondary": "carnelian", "carat_min": 5},
    "mercury": {"primary": "emerald", "secondary": "peridot", "carat_min": 3},
    "jupiter": {"primary": "yellow_sapphire", "secondary": "citrine", "carat_min": 4},
    "venus": {"primary": "diamond", "secondary": "white_sapphire", "carat_min": 1},
    "saturn": {"primary": "blue_sapphire", "secondary": "amethyst", "carat_min": 4},
    "rahu": {"primary": "hessonite", "secondary": "orange_zircon", "carat_min": 5},
    "ketu": {"primary": "cats_eye", "secondary": "tourmaline", "carat_min": 5}
  },
  "mantras": {
    "sun": "Om Suryaya Namaha",
    "moon": "Om Chandraya Namaha",
    // ... all planets
  },
  "charities": {
    "sun": ["wheat", "jaggery", "copper"],
    "moon": ["rice", "milk", "silver"],
    // ... all planets
  }
}
```

---

## Implementation Phases

### Phase 1: Critical Fixes (Day 1)
1. ✅ Create `dignities.json` - fix divisional.py errors
2. ✅ Create `relationships.json` - centralize friendships
3. ✅ Create `aspects.json` - standardize aspect rules
4. Update packages to load from these files

### Phase 2: Strength Calculations (Day 1-2)
5. Create `shadbala_rules.json`
6. Create `ashtakavarga_rules.json`
7. Update strength.py to use JSON

### Phase 3: Timing & Predictions (Day 2)
8. Create `dasha_rules.json`
9. Create `transit_rules.json`
10. Create `muhurta_rules.json`
11. Update context package

### Phase 4: Enhancements (Day 3)
12. Create `compatibility_rules.json`
13. Create `remedies_rules.json`
14. Expand existing definition files

### Phase 5: Panchanga (Day 3)
15. Create `tithis.json`
16. Create `karanas.json`
17. Create `nitya_yogas.json`
18. Create `varas.json`

---

## File Count Summary

| Category | Existing | To Create | Total |
|----------|----------|-----------|-------|
| Definitions | 4 | 10 | 14 |
| Rules | 2 | 7 | 9 |
| **TOTAL** | **6** | **17** | **23** |

---

## Agent Assignment

| Agent | Files | Est. Time |
|-------|-------|-----------|
| Agent 1 | dignities.json, relationships.json, aspects.json | 1 hour |
| Agent 2 | shadbala_rules.json, ashtakavarga_rules.json | 1.5 hours |
| Agent 3 | dasha_rules.json, transit_rules.json | 1 hour |
| Agent 4 | muhurta_rules.json, compatibility_rules.json | 1 hour |
| Agent 5 | remedies_rules.json, tithis.json, karanas.json | 1 hour |
| Agent 6 | nitya_yogas.json, varas.json, vargas.json | 1 hour |
