# Knowledge Dump - Copy to Appropriate Locations

This file contains JSON definitions that need to be copied to the `knowledge/` subdirectories.
Run the script at the bottom to create all files automatically.

---

## knowledge/definitions/rashis.json

```json
{
  "rashis": {
    "aries": {
      "id": "aries", "name": "Aries", "sanskrit": "Mesha", "number": 1,
      "element": "fire", "quality": "movable", "gender": "masculine",
      "ruler": "Mars", "exalted_planet": "Sun", "debilitated_planet": "Saturn",
      "direction": "East", "body_part": "head",
      "degrees": {"start": 0, "end": 30}
    },
    "taurus": {
      "id": "taurus", "name": "Taurus", "sanskrit": "Vrishabha", "number": 2,
      "element": "earth", "quality": "fixed", "gender": "feminine",
      "ruler": "Venus", "exalted_planet": "Moon", "debilitated_planet": "Ketu",
      "direction": "South", "body_part": "face",
      "degrees": {"start": 30, "end": 60}
    },
    "gemini": {
      "id": "gemini", "name": "Gemini", "sanskrit": "Mithuna", "number": 3,
      "element": "air", "quality": "dual", "gender": "masculine",
      "ruler": "Mercury", "exalted_planet": "Rahu", "debilitated_planet": null,
      "direction": "West", "body_part": "arms",
      "degrees": {"start": 60, "end": 90}
    },
    "cancer": {
      "id": "cancer", "name": "Cancer", "sanskrit": "Karka", "number": 4,
      "element": "water", "quality": "movable", "gender": "feminine",
      "ruler": "Moon", "exalted_planet": "Jupiter", "debilitated_planet": "Mars",
      "direction": "North", "body_part": "chest",
      "degrees": {"start": 90, "end": 120}
    },
    "leo": {
      "id": "leo", "name": "Leo", "sanskrit": "Simha", "number": 5,
      "element": "fire", "quality": "fixed", "gender": "masculine",
      "ruler": "Sun", "exalted_planet": null, "debilitated_planet": null,
      "direction": "East", "body_part": "stomach",
      "degrees": {"start": 120, "end": 150}
    },
    "virgo": {
      "id": "virgo", "name": "Virgo", "sanskrit": "Kanya", "number": 6,
      "element": "earth", "quality": "dual", "gender": "feminine",
      "ruler": "Mercury", "exalted_planet": "Mercury", "debilitated_planet": "Venus",
      "direction": "South", "body_part": "waist",
      "degrees": {"start": 150, "end": 180}
    },
    "libra": {
      "id": "libra", "name": "Libra", "sanskrit": "Tula", "number": 7,
      "element": "air", "quality": "movable", "gender": "masculine",
      "ruler": "Venus", "exalted_planet": "Saturn", "debilitated_planet": "Sun",
      "direction": "West", "body_part": "lower abdomen",
      "degrees": {"start": 180, "end": 210}
    },
    "scorpio": {
      "id": "scorpio", "name": "Scorpio", "sanskrit": "Vrishchika", "number": 8,
      "element": "water", "quality": "fixed", "gender": "feminine",
      "ruler": "Mars", "exalted_planet": "Ketu", "debilitated_planet": "Moon",
      "direction": "North", "body_part": "genitals",
      "degrees": {"start": 210, "end": 240}
    },
    "sagittarius": {
      "id": "sagittarius", "name": "Sagittarius", "sanskrit": "Dhanu", "number": 9,
      "element": "fire", "quality": "dual", "gender": "masculine",
      "ruler": "Jupiter", "exalted_planet": null, "debilitated_planet": "Rahu",
      "direction": "East", "body_part": "thighs",
      "degrees": {"start": 240, "end": 270}
    },
    "capricorn": {
      "id": "capricorn", "name": "Capricorn", "sanskrit": "Makara", "number": 10,
      "element": "earth", "quality": "movable", "gender": "feminine",
      "ruler": "Saturn", "exalted_planet": "Mars", "debilitated_planet": "Jupiter",
      "direction": "South", "body_part": "knees",
      "degrees": {"start": 270, "end": 300}
    },
    "aquarius": {
      "id": "aquarius", "name": "Aquarius", "sanskrit": "Kumbha", "number": 11,
      "element": "air", "quality": "fixed", "gender": "masculine",
      "ruler": "Saturn", "exalted_planet": null, "debilitated_planet": null,
      "direction": "West", "body_part": "ankles",
      "degrees": {"start": 300, "end": 330}
    },
    "pisces": {
      "id": "pisces", "name": "Pisces", "sanskrit": "Meena", "number": 12,
      "element": "water", "quality": "dual", "gender": "feminine",
      "ruler": "Jupiter", "exalted_planet": "Venus", "debilitated_planet": "Mercury",
      "direction": "North", "body_part": "feet",
      "degrees": {"start": 330, "end": 360}
    }
  }
}
```

---

## knowledge/definitions/nakshatras.json

```json
{
  "nakshatras": [
    {"number": 1, "name": "Ashwini", "sanskrit": "अश्विनी", "ruler": "Ketu", "deity": "Ashwini Kumaras", "symbol": "Horse head", "rashi": "Aries", "degrees": [0, 13.333]},
    {"number": 2, "name": "Bharani", "sanskrit": "भरणी", "ruler": "Venus", "deity": "Yama", "symbol": "Yoni", "rashi": "Aries", "degrees": [13.333, 26.667]},
    {"number": 3, "name": "Krittika", "sanskrit": "कृत्तिका", "ruler": "Sun", "deity": "Agni", "symbol": "Razor", "rashi": "Aries/Taurus", "degrees": [26.667, 40]},
    {"number": 4, "name": "Rohini", "sanskrit": "रोहिणी", "ruler": "Moon", "deity": "Brahma", "symbol": "Cart", "rashi": "Taurus", "degrees": [40, 53.333]},
    {"number": 5, "name": "Mrigashira", "sanskrit": "मृगशिरा", "ruler": "Mars", "deity": "Soma", "symbol": "Deer head", "rashi": "Taurus/Gemini", "degrees": [53.333, 66.667]},
    {"number": 6, "name": "Ardra", "sanskrit": "आर्द्रा", "ruler": "Rahu", "deity": "Rudra", "symbol": "Teardrop", "rashi": "Gemini", "degrees": [66.667, 80]},
    {"number": 7, "name": "Punarvasu", "sanskrit": "पुनर्वसु", "ruler": "Jupiter", "deity": "Aditi", "symbol": "Bow", "rashi": "Gemini/Cancer", "degrees": [80, 93.333]},
    {"number": 8, "name": "Pushya", "sanskrit": "पुष्य", "ruler": "Saturn", "deity": "Brihaspati", "symbol": "Flower", "rashi": "Cancer", "degrees": [93.333, 106.667]},
    {"number": 9, "name": "Ashlesha", "sanskrit": "आश्लेषा", "ruler": "Mercury", "deity": "Nagas", "symbol": "Serpent", "rashi": "Cancer", "degrees": [106.667, 120]},
    {"number": 10, "name": "Magha", "sanskrit": "मघा", "ruler": "Ketu", "deity": "Pitris", "symbol": "Throne", "rashi": "Leo", "degrees": [120, 133.333]},
    {"number": 11, "name": "Purva Phalguni", "sanskrit": "पूर्व फाल्गुनी", "ruler": "Venus", "deity": "Bhaga", "symbol": "Hammock", "rashi": "Leo", "degrees": [133.333, 146.667]},
    {"number": 12, "name": "Uttara Phalguni", "sanskrit": "उत्तर फाल्गुनी", "ruler": "Sun", "deity": "Aryaman", "symbol": "Bed", "rashi": "Leo/Virgo", "degrees": [146.667, 160]},
    {"number": 13, "name": "Hasta", "sanskrit": "हस्त", "ruler": "Moon", "deity": "Savitar", "symbol": "Hand", "rashi": "Virgo", "degrees": [160, 173.333]},
    {"number": 14, "name": "Chitra", "sanskrit": "चित्रा", "ruler": "Mars", "deity": "Vishwakarma", "symbol": "Pearl", "rashi": "Virgo/Libra", "degrees": [173.333, 186.667]},
    {"number": 15, "name": "Swati", "sanskrit": "स्वाति", "ruler": "Rahu", "deity": "Vayu", "symbol": "Coral", "rashi": "Libra", "degrees": [186.667, 200]},
    {"number": 16, "name": "Vishakha", "sanskrit": "विशाखा", "ruler": "Jupiter", "deity": "Indra-Agni", "symbol": "Archway", "rashi": "Libra/Scorpio", "degrees": [200, 213.333]},
    {"number": 17, "name": "Anuradha", "sanskrit": "अनुराधा", "ruler": "Saturn", "deity": "Mitra", "symbol": "Lotus", "rashi": "Scorpio", "degrees": [213.333, 226.667]},
    {"number": 18, "name": "Jyeshtha", "sanskrit": "ज्येष्ठा", "ruler": "Mercury", "deity": "Indra", "symbol": "Earring", "rashi": "Scorpio", "degrees": [226.667, 240]},
    {"number": 19, "name": "Mula", "sanskrit": "मूल", "ruler": "Ketu", "deity": "Nirriti", "symbol": "Roots", "rashi": "Sagittarius", "degrees": [240, 253.333]},
    {"number": 20, "name": "Purva Ashadha", "sanskrit": "पूर्व आषाढ़ा", "ruler": "Venus", "deity": "Apas", "symbol": "Fan", "rashi": "Sagittarius", "degrees": [253.333, 266.667]},
    {"number": 21, "name": "Uttara Ashadha", "sanskrit": "उत्तर आषाढ़ा", "ruler": "Sun", "deity": "Vishvadevas", "symbol": "Tusk", "rashi": "Sagittarius/Capricorn", "degrees": [266.667, 280]},
    {"number": 22, "name": "Shravana", "sanskrit": "श्रवण", "ruler": "Moon", "deity": "Vishnu", "symbol": "Ear", "rashi": "Capricorn", "degrees": [280, 293.333]},
    {"number": 23, "name": "Dhanishtha", "sanskrit": "धनिष्ठा", "ruler": "Mars", "deity": "Vasus", "symbol": "Drum", "rashi": "Capricorn/Aquarius", "degrees": [293.333, 306.667]},
    {"number": 24, "name": "Shatabhisha", "sanskrit": "शतभिषा", "ruler": "Rahu", "deity": "Varuna", "symbol": "Circle", "rashi": "Aquarius", "degrees": [306.667, 320]},
    {"number": 25, "name": "Purva Bhadrapada", "sanskrit": "पूर्व भाद्रपद", "ruler": "Jupiter", "deity": "Aja Ekapada", "symbol": "Sword", "rashi": "Aquarius/Pisces", "degrees": [320, 333.333]},
    {"number": 26, "name": "Uttara Bhadrapada", "sanskrit": "उत्तर भाद्रपद", "ruler": "Saturn", "deity": "Ahir Budhnya", "symbol": "Twins", "rashi": "Pisces", "degrees": [333.333, 346.667]},
    {"number": 27, "name": "Revati", "sanskrit": "रेवती", "ruler": "Mercury", "deity": "Pushan", "symbol": "Fish", "rashi": "Pisces", "degrees": [346.667, 360]}
  ]
}
```

---

## knowledge/rules/yoga_detection_rules.json

```json
{
  "yoga_detection_rules": {
    "ruchaka_yoga": {
      "name": "Ruchaka Yoga",
      "category": "pancha_mahapurusha",
      "description": "Mars in kendra in own/exalted sign",
      "detection": {
        "planet": "Mars",
        "conditions": [
          {"type": "in_kendra", "houses": [1, 4, 7, 10], "from": "lagna"},
          {"type": "in_own_or_exalted_sign", "signs": ["Aries", "Scorpio", "Capricorn"]}
        ],
        "all_conditions_required": true
      },
      "effects": ["Courageous", "Leadership", "Military success", "Athletic"]
    },
    "bhadra_yoga": {
      "name": "Bhadra Yoga",
      "category": "pancha_mahapurusha",
      "description": "Mercury in kendra in own/exalted sign",
      "detection": {
        "planet": "Mercury",
        "conditions": [
          {"type": "in_kendra", "houses": [1, 4, 7, 10], "from": "lagna"},
          {"type": "in_own_or_exalted_sign", "signs": ["Gemini", "Virgo"]}
        ],
        "all_conditions_required": true
      },
      "effects": ["Intelligent", "Learned", "Good speaker", "Business success"]
    },
    "hamsa_yoga": {
      "name": "Hamsa Yoga",
      "category": "pancha_mahapurusha",
      "description": "Jupiter in kendra in own/exalted sign",
      "detection": {
        "planet": "Jupiter",
        "conditions": [
          {"type": "in_kendra", "houses": [1, 4, 7, 10], "from": "lagna"},
          {"type": "in_own_or_exalted_sign", "signs": ["Sagittarius", "Pisces", "Cancer"]}
        ],
        "all_conditions_required": true
      },
      "effects": ["Righteous", "Spiritual", "Wealthy", "Respected"]
    },
    "malavya_yoga": {
      "name": "Malavya Yoga",
      "category": "pancha_mahapurusha",
      "description": "Venus in kendra in own/exalted sign",
      "detection": {
        "planet": "Venus",
        "conditions": [
          {"type": "in_kendra", "houses": [1, 4, 7, 10], "from": "lagna"},
          {"type": "in_own_or_exalted_sign", "signs": ["Taurus", "Libra", "Pisces"]}
        ],
        "all_conditions_required": true
      },
      "effects": ["Attractive", "Wealthy", "Artistic", "Comfortable life"]
    },
    "shasha_yoga": {
      "name": "Shasha Yoga",
      "category": "pancha_mahapurusha",
      "description": "Saturn in kendra in own/exalted sign",
      "detection": {
        "planet": "Saturn",
        "conditions": [
          {"type": "in_kendra", "houses": [1, 4, 7, 10], "from": "lagna"},
          {"type": "in_own_or_exalted_sign", "signs": ["Capricorn", "Aquarius", "Libra"]}
        ],
        "all_conditions_required": true
      },
      "effects": ["Authority", "Leadership", "Land ownership", "Service industries"]
    },
    "gajakesari_yoga": {
      "name": "Gajakesari Yoga",
      "category": "wealth",
      "description": "Jupiter in kendra from Moon",
      "detection": {
        "planet": "Jupiter",
        "conditions": [
          {"type": "in_kendra", "houses": [1, 4, 7, 10], "from": "moon"}
        ],
        "all_conditions_required": true
      },
      "effects": ["Fame", "Wealth", "Intelligence", "Long life"]
    },
    "budhaditya_yoga": {
      "name": "Budhaditya Yoga",
      "category": "intelligence",
      "description": "Sun and Mercury conjunct",
      "detection": {
        "planets": ["Sun", "Mercury"],
        "conditions": [
          {"type": "planets_conjunct"}
        ],
        "all_conditions_required": true
      },
      "effects": ["Intelligence", "Fame", "Skill in arts", "Good reputation"]
    },
    "chandra_mangal_yoga": {
      "name": "Chandra Mangal Yoga",
      "category": "wealth",
      "description": "Moon and Mars conjunct",
      "detection": {
        "planets": ["Moon", "Mars"],
        "conditions": [
          {"type": "planets_conjunct"}
        ],
        "all_conditions_required": true
      },
      "effects": ["Wealth through business", "Industrious", "Prosperous"]
    }
  }
}
```

---

## Setup Script

Run this to create all files:

```bash
cd /Users/srikanth/Documents/SWARODAYA/108-core

# Create rashis.json
cat > knowledge/definitions/rashis.json << 'EOF'
# (paste rashis JSON from above)
EOF

# Create nakshatras.json
cat > knowledge/definitions/nakshatras.json << 'EOF'
# (paste nakshatras JSON from above)
EOF

# Create yoga detection rules
mkdir -p knowledge/rules
cat > knowledge/rules/yoga_detection_rules.json << 'EOF'
# (paste yoga rules JSON from above)
EOF
```

Or let Claude Code do it - just tell it to "read KNOWLEDGE_DUMP.md and create the JSON files in the appropriate locations".
