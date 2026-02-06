---
name: self-agent
description: SELF layer specialist — Session 18 tasks — Prashna D9/D3 + Upapada interpretation
model: claude-sonnet-4-20250514
tools:
  - Edit
  - Write
  - Read
  - Grep
  - Glob
  - Bash
---

# SELF Agent — Session 18 (Final Features)

You are responsible for `packages/self/` — specifically finishing 2 remaining features.

## Session 17 completed: D2-D60 interpreter, Bhava Bala, yoga cancellation, female Mangal Dosha, combustion cancellation, Jaimini Argala. All working. DO NOT re-do these.

## TASK 1: Prashna Navamsha + Drekkana (D9/D3 in Horary)

The Prashna module (`packages/self/src/prashna.py`) does full horary analysis but does NOT use divisional charts. In Prashna Jyotish, the D9 (Navamsha) and D3 (Drekkana) of the Prashna lagna are critical for accurate judgments.

Add to `prashna.py`:

```python
def get_prashna_divisional_analysis(prashna_chart: PrashnaChart) -> dict:
    """Analyze D9 and D3 of the Prashna chart for deeper insight.

    D9 (Navamsha) in Prashna:
    - Shows the subtle/hidden dimension of the question
    - Navamsha lagna lord strength = inner truth of the situation
    - If D9 lagna is strong but D1 is weak = situation will improve
    - If D9 lagna is weak but D1 is strong = surface looks good but underlying weakness

    D3 (Drekkana) in Prashna:
    - Shows effort/courage required to achieve the outcome
    - 1st Drekkana (0-10°) = achievable with own effort
    - 2nd Drekkana (10-20°) = needs help from others
    - 3rd Drekkana (20-30°) = very difficult, requires divine grace
    """
    from packages.cosmos.src.divisional import get_divisional_chart

    # Get planet longitudes from prashna chart
    planet_longitudes = {p: data["longitude"] for p, data in prashna_chart.planets.items()}

    # Calculate D9 and D3
    d9 = get_divisional_chart(planet_longitudes, 9)
    d3 = get_divisional_chart(planet_longitudes, 3)

    # Analyze D9 lagna lord strength
    # Analyze D3 for effort level
    # Combine with existing prashna judgment

def _analyze_prashna_navamsha(d9_chart: dict, prashna_lagna_sign: str) -> dict:
    """Navamsha analysis specific to Prashna questions."""
    # D9 lagna sign = hidden dimension
    # D9 lagna lord placement = underlying reality
    # Benefics in D9 kendra = favorable hidden factors
    # Malefics in D9 kendra = hidden obstacles

def _analyze_prashna_drekkana(d3_chart: dict, lagna_degree: float) -> dict:
    """Drekkana analysis for effort assessment in Prashna."""
    # Which decanate is lagna in?
    decanate = int(lagna_degree % 30 / 10) + 1
    # 1st = self-effort, 2nd = with help, 3rd = very difficult
```

**Integration**: Update `analyze_prashna()` to call `get_prashna_divisional_analysis()` and include results in `PrashnaResult`.

Update the `PrashnaResult` model in `packages/core/src/models.py` to include:
```python
navamsha_analysis: dict | None = None
drekkana_analysis: dict | None = None
```

## TASK 2: Upapada Interpretation (Marriage from Jaimini)

The Upapada Lagna (UL) is calculated via `calculate_all_arudha_padas()` in `jaimini.py` — it's the Arudha of the 12th house. But there's NO interpretation.

Add to `jaimini.py`:

```python
def interpret_upapada(chart: BirthChart) -> dict:
    """Interpret Upapada Lagna (UL) for marriage and partnership.

    Upapada = Arudha Pada of 12th house (A12)
    It shows the IMAGE of marriage/partnerships.

    Analysis:
    1. UL sign = type of partner attracted
    2. UL lord placement = quality and direction of marriage
    3. Planets in/aspecting UL = influences on marriage
    4. 2nd from UL = sustenance of marriage (malefics here = separation risk)
    5. 7th from UL = nature of physical relationship
    6. Darakaraka in relation to UL = karmic connection
    """
    arudhas = calculate_all_arudha_padas(chart)
    upapada = arudhas[11]  # A12 = Upapada

    upapada_sign = upapada["sign"]
    upapada_lord = _get_sign_lord(upapada_sign)

    # Find lord's position in chart
    lord_house = chart.planets[upapada_lord].house
    lord_sign = chart.planets[upapada_lord].sign

    # Check 2nd from UL (marriage sustenance)
    second_from_ul = (RASHI_NAMES.index(upapada_sign) + 1) % 12
    planets_in_second = [p for p, data in chart.planets.items()
                         if data.rashi == second_from_ul]

    # Check Darakaraka (DK) relationship
    karakas = calculate_chara_karakas(chart)
    darakaraka = karakas[-1]  # Last = DK

    return {
        "upapada_sign": upapada_sign,
        "upapada_lord": upapada_lord,
        "lord_house": lord_house,
        "lord_sign": lord_sign,
        "partner_type": _interpret_upapada_sign(upapada_sign),
        "marriage_quality": _interpret_upapada_lord(upapada_lord, lord_house),
        "sustenance": _analyze_second_from_ul(planets_in_second),
        "separation_risk": _check_separation_indicators(planets_in_second),
        "darakaraka_connection": _analyze_dk_ul_connection(darakaraka, upapada),
        "timing": _marriage_timing_from_ul(upapada_lord, chart),
    }

def _interpret_upapada_sign(sign: str) -> str:
    """Partner characteristics based on UL sign."""
    interpretations = {
        "aries": "Energetic, independent, assertive partner. Quick marriage decisions.",
        "taurus": "Beautiful, artistic, wealthy partner. Stable marriage.",
        "gemini": "Intellectual, communicative partner. May marry someone younger.",
        "cancer": "Nurturing, emotional, family-oriented partner.",
        "leo": "Proud, dignified, authoritative partner. Grand marriage.",
        "virgo": "Analytical, service-minded partner. Practical marriage.",
        "libra": "Attractive, diplomatic, artistic partner. Harmonious relationship.",
        "scorpio": "Intense, secretive, transformative partner. Deep bond.",
        "sagittarius": "Philosophical, adventurous partner. May marry foreigner.",
        "capricorn": "Mature, responsible, status-conscious partner.",
        "aquarius": "Unconventional, humanitarian partner. Unique marriage.",
        "pisces": "Spiritual, compassionate, artistic partner. Karmic marriage.",
    }
    return interpretations.get(sign.lower(), "")
```

## Testing Requirements

```bash
uv run pytest tests/ -v --tb=short -k "test_prashna or test_jaimini or test_upapada"
uv run ruff check packages/self/
```

Write tests in `tests/unit/test_prashna_divisional.py` and `tests/unit/test_upapada.py`.

## DO NOT TOUCH
- `packages/cosmos/` — owned by others
- `packages/context/` — owned by context-agent
- `packages/guide/` — owned by wiring-agent
- `services/` — owned by wiring-agent
- Only modify `packages/self/`, `packages/core/src/models.py` (PrashnaResult only), and tests
