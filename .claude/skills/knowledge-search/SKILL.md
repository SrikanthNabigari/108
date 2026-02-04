---
name: knowledge-search
description: Search and retrieve Jyotish knowledge including planet meanings, nakshatra interpretations, yoga effects, and house significations
triggers:
  - meaning of
  - interpretation
  - what does
  - signifies
  - knowledge
  - lookup
globs:
  - "knowledge/**/*.json"
  - "knowledge/**/*.md"
---

# Knowledge Search Skill

You are responsible for retrieving accurate Jyotish knowledge from the 108 knowledge base.

## Knowledge Structure

```
knowledge/
├── definitions/              # Core definitions (JSON)
│   ├── planets.json         # 9 grahas with properties
│   ├── rashis.json          # 12 signs with properties
│   ├── nakshatras.json      # 27 lunar mansions
│   ├── houses.json          # 12 bhavas
│   ├── yogas.json           # 317+ yoga definitions
│   └── doshas.json          # Dosha definitions
├── interpretations/          # Detailed meanings (Markdown)
│   ├── planets/
│   │   ├── sun.md
│   │   ├── moon.md
│   │   └── ...
│   ├── nakshatras/
│   │   ├── ashwini.md
│   │   └── ...
│   └── yogas/
│       ├── pancha_mahapurusha/
│       └── raja_yogas/
└── rules/                    # Detection rules (JSON)
    ├── yoga_detection_rules.json
    └── dosha_detection_rules.json
```

## Definition Schema

### Planet Definition
```json
{
  "id": "sun",
  "name": "Sun",
  "sanskrit": "Surya",
  "nature": "malefic",
  "element": "fire",
  "gender": "masculine",
  "owns_signs": ["Leo"],
  "exalted_in": "Aries",
  "debilitated_in": "Libra",
  "friends": ["Moon", "Mars", "Jupiter"],
  "enemies": ["Venus", "Saturn"],
  "neutral": ["Mercury"],
  "karaka_of": ["soul", "father", "authority", "government"],
  "body_parts": ["heart", "eyes", "bones"],
  "day": "Sunday",
  "gem": "Ruby",
  "metal": "Gold",
  "direction": "East"
}
```

### Nakshatra Definition
```json
{
  "id": "ashwini",
  "name": "Ashwini",
  "sanskrit": "अश्विनी",
  "number": 1,
  "span": {"start": 0, "end": 13.333},
  "rashi": "Aries",
  "ruling_planet": "Ketu",
  "deity": "Ashwini Kumaras",
  "symbol": "Horse head",
  "nature": "deva",
  "gana": "deva",
  "animal": "Horse (male)",
  "qualities": ["healing", "swift action", "beginnings"],
  "padas": [
    {"number": 1, "navamsha": "Aries", "qualities": ["pioneering", "courageous"]},
    {"number": 2, "navamsha": "Taurus", "qualities": ["stable", "resourceful"]},
    {"number": 3, "navamsha": "Gemini", "qualities": ["communicative", "versatile"]},
    {"number": 4, "navamsha": "Cancer", "qualities": ["nurturing", "emotional"]}
  ]
}
```

### Yoga Definition
```json
{
  "id": "shasha_yoga",
  "name": "Shasha Yoga",
  "category": "pancha_mahapurusha",
  "planet": "Saturn",
  "conditions": {
    "type": "AND",
    "rules": [
      {"planet": "Saturn", "in_kendra": true},
      {"planet": "Saturn", "in_own_or_exalted": true}
    ]
  },
  "effects": {
    "positive": [
      "Leadership in service industries",
      "Success in agriculture and real estate",
      "Respected by common people"
    ],
    "challenges": [
      "May face early life hardships",
      "Success comes through perseverance"
    ]
  },
  "strength_modifiers": {
    "strong_if": ["Saturn in own sign", "Saturn aspected by Jupiter"],
    "weak_if": ["Saturn combust", "Saturn in enemy sign navamsha"]
  }
}
```

## Search Patterns

### By ID
```python
def get_planet(planet_id: str) -> dict:
    """Get planet definition by ID."""
    definitions = load_json("knowledge/definitions/planets.json")
    return definitions.get(planet_id.lower())
```

### By Property
```python
def find_planets_by_nature(nature: str) -> list:
    """Find all planets of a given nature."""
    definitions = load_json("knowledge/definitions/planets.json")
    return [p for p in definitions.values() if p["nature"] == nature]
```

### Semantic Search
```python
async def semantic_search(query: str, category: str = None, limit: int = 5) -> list:
    """Search knowledge base using embeddings."""
    # Uses pgvector for semantic similarity
    embedding = await get_embedding(query)
    results = await vector_store.similarity_search(
        embedding,
        filter={"category": category} if category else None,
        limit=limit
    )
    return results
```

## Interpretation Retrieval

```python
def get_interpretation(entity_type: str, entity_id: str) -> str:
    """Get detailed interpretation markdown."""
    path = f"knowledge/interpretations/{entity_type}/{entity_id}.md"
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None
```

## Common Queries

### "What does Sun in the 10th house mean?"
```python
def interpret_planet_in_house(planet: str, house: int) -> dict:
    planet_def = get_planet(planet)
    house_def = get_house(house)

    return {
        "planet": planet_def,
        "house": house_def,
        "interpretation": generate_interpretation(planet_def, house_def)
    }
```

### "What yogas does Saturn form?"
```python
def find_yogas_by_planet(planet: str) -> list:
    rules = load_yoga_detection_rules()
    return [y for y in rules.values() if y["detection"].get("planet") == planet]
```

### "Tell me about Purva Bhadrapada nakshatra"
```python
def get_nakshatra_full(nakshatra_name: str) -> dict:
    definition = get_nakshatra_by_name(nakshatra_name)
    interpretation = get_interpretation("nakshatras", definition["id"])

    return {
        "definition": definition,
        "interpretation": interpretation,
        "related_yogas": find_yogas_by_nakshatra(nakshatra_name)
    }
```

## Vector Embeddings

Knowledge is embedded for semantic search:

```python
# Embedding schema
{
    "id": "yoga_shasha_yoga",
    "content": "Shasha Yoga is formed when Saturn...",
    "metadata": {
        "type": "yoga",
        "category": "pancha_mahapurusha",
        "planet": "Saturn"
    },
    "embedding": [0.1, 0.2, ...]  # 1536 dimensions
}
```

## File Locations

- **Definitions**: `knowledge/definitions/`
- **Interpretations**: `knowledge/interpretations/`
- **Detection rules**: `knowledge/rules/`
- **Search code**: `packages/guide/src/knowledge_search.py`

## Best Practices

1. **Always cite sources** - Reference the specific definition/interpretation
2. **Combine with context** - Planet meaning changes based on house/sign
3. **Consider aspects** - Other planets influencing the interpretation
4. **Use strength modifiers** - Not all yogas are equally strong
5. **Cache frequently accessed** - Definitions don't change often
