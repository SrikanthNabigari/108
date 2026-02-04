---
name: yoga-detector
description: Detect Vedic astrology yogas (planetary combinations) from birth chart data using machine-parseable JSON rules
triggers:
  - detect yogas
  - yoga analysis
  - chart patterns
  - pancha mahapurusha
  - raja yoga
  - dhana yoga
globs:
  - "packages/self/**/*.py"
  - "knowledge/rules/yoga_detection_rules.json"
  - "knowledge/definitions/yogas.json"
---

# Yoga Detector Skill

You are an expert in detecting Vedic astrology yogas from birth chart data.

## What is a Yoga?

A **yoga** is a specific planetary combination that produces particular results. There are 317+ yogas defined in the knowledge base.

## Detection Rule Format

All yoga detection rules are stored in `knowledge/rules/yoga_detection_rules.json`:

```json
{
  "yoga_detection_rules": {
    "shasha_yoga": {
      "name": "Shasha Yoga",
      "category": "pancha_mahapurusha",
      "detection": {
        "planet": "Saturn",
        "conditions": [
          {
            "type": "in_kendra",
            "houses": [1, 4, 7, 10],
            "from": "lagna"
          },
          {
            "type": "in_own_or_exalted_sign",
            "signs": ["Capricorn", "Aquarius", "Libra"]
          }
        ],
        "all_conditions_required": true
      }
    }
  }
}
```

## Condition Types

### in_kendra
Planet must be in a kendra house (1, 4, 7, 10):
```python
def check_in_kendra(planet_house: int, houses: list = [1, 4, 7, 10]) -> bool:
    return planet_house in houses
```

### in_own_or_exalted_sign
Planet must be in its own or exalted sign:
```python
OWN_SIGNS = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"]
}

EXALTED_SIGNS = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra"
}
```

### in_trikona
Planet must be in a trikona house (1, 5, 9):
```python
def check_in_trikona(planet_house: int) -> bool:
    return planet_house in [1, 5, 9]
```

### planets_conjunct
Two or more planets in the same sign:
```python
def check_conjunction(planets: dict, required_planets: list) -> bool:
    signs = [planets[p]["rashi"] for p in required_planets]
    return len(set(signs)) == 1
```

### lord_placement
Lord of a house is in a specific house:
```python
def check_lord_placement(lord_planet: str, planets: dict, required_house: int) -> bool:
    return planets[lord_planet]["house"] == required_house
```

## Detection Algorithm

```python
def detect_yogas(planets: dict, lagna_rashi: str) -> list[dict]:
    """Detect all yogas present in a birth chart."""
    detected = []
    rules = load_yoga_detection_rules()

    for yoga_id, yoga in rules.items():
        detection = yoga["detection"]
        planet = detection.get("planet")
        conditions = detection.get("conditions", [])
        all_required = detection.get("all_conditions_required", True)

        results = []
        for condition in conditions:
            result = evaluate_condition(condition, planet, planets, lagna_rashi)
            results.append(result)

        if all_required:
            is_present = all(results)
        else:
            is_present = any(results)

        if is_present:
            detected.append({
                "yoga_id": yoga_id,
                "name": yoga["name"],
                "category": yoga["category"],
                "involved_planets": get_involved_planets(detection, planets)
            })

    return detected
```

## Yoga Categories

1. **Pancha Mahapurusha** (5 Great Person Yogas)
   - Ruchaka (Mars), Bhadra (Mercury), Hamsa (Jupiter), Malavya (Venus), Shasha (Saturn)

2. **Raja Yogas** (Royal Combinations)
   - Kendra-Trikona lords conjunction/exchange

3. **Dhana Yogas** (Wealth Combinations)
   - 2nd/11th house connections

4. **Arishta Yogas** (Misfortune Combinations)
   - 6th/8th/12th house afflictions

5. **Nabhasa Yogas** (Celestial Patterns)
   - Akriti (shape), Sankhya (number), Ashraya (basis)

## File Locations

- **Detection rules**: `knowledge/rules/yoga_detection_rules.json`
- **Yoga definitions**: `knowledge/definitions/yogas.json`
- **Interpretations**: `knowledge/interpretations/yogas/`
- **Detection code**: `packages/self/src/yoga_detector.py`

## Testing

```python
def test_shasha_yoga():
    """Saturn in Capricorn in 4th house should trigger Shasha."""
    planets = {
        "saturn": {"rashi": "Capricorn", "house": 4}
    }
    lagna = "Libra"
    detected = detect_yogas(planets, lagna)
    assert any(y["yoga_id"] == "shasha_yoga" for y in detected)
```

## Important Notes

1. **Load rules from JSON** - never hardcode yoga conditions
2. **All conditions must be evaluated** before determining presence
3. **Strength matters** - some yogas have strength modifiers
4. **Context matters** - benefic/malefic nature affects interpretation
