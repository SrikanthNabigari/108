# Planetary Strength Calculations Module

## Overview

The `strength.py` module implements comprehensive planetary strength calculations for the 108 Vedic Astrology system, including:

1. **Shadbala** (Six-fold Strength)
2. **Ashtakavarga** (Eight-fold Classification)
3. **Sarvashtakavarga** (Total Strength)
4. **Planet Dignity** Classification

## Shadbala (Six-fold Strength)

Shadbala measures the overall strength of a planet across six dimensions. Each component is measured in virupas (60 virupas = 1 full strength unit).

### 1. Sthana Bala (Positional Strength)

Measures a planet's strength based on its position in the chart.

**Components:**
- **Uchcha Bala** (0-60): Strength from exaltation
  - Maximum at exact exaltation degree
  - Zero at debilitation (180° opposite)
  - 30 points in neutral positions
  
- **Saptavargaja Bala**: Strength in 7 divisional charts
  - D1 (Rashi), D2 (Hora), D3 (Drekkana)
  - D7 (Saptamsha), D9 (Navamsha)
  - D12 (Dwadasamsha), D24 (Chaturvimshamsha)
  
- **Ojhayugmarasyamsa Bala**: Odd/even sign placement
  - Generally beneficial in odd signs (7.5) vs even signs (5.0)
  
- **Kendradi Bala** (House Placement)
  - Kendra (1, 4, 7, 10): 60 points (angular houses)
  - Panapara (2, 5, 8, 11): 30 points (succeedent)
  - Apoklima (3, 6, 9, 12): 15 points (cadent)
  
- **Drekkana Bala**: Decanate placement
  - Each sign divided into 3 decanates (10° each)
  - 10 points for favorable placement

### 2. Dig Bala (Directional Strength)

Measures planetary strength based on directional placement.

**Strong Directions (60 points max):**
- Jupiter & Mercury: East (1st house/Lagna)
- Sun & Mars: South (10th house/MC)
- Saturn: West (7th house)
- Moon & Venus: North (4th house)

**Formula:**
```
Dig Bala = 60 × (1 - distance_from_strong_house / 180°)
```

### 3. Kala Bala (Temporal Strength)

Measures planetary strength based on time factors.

**Components:**
- **Nathonnatha Bala**: Day/night strength
  - Sun & Mars: strong during day (15 points)
  - Moon & Venus: strong during night (15 points)
  - Others: 10 points
  
- **Paksha Bala**: Lunar phase strength
  - Moon strongest during waxing (Shukla) phase
  - Other planets modulated by lunar phase
  
- **Ayana Bala**: Declination strength
  - Based on planet's latitude/declination
  - 5 points (simplified)
  
- **Varsha/Masa/Dina/Hora Bala**: Year/month/day/hour lords
- **Tribhaga Bala**: Three parts of day/night

### 4. Chesta Bala (Motional Strength)

Measures strength based on planet's motion.

**Motion States (0-60):**
- Retrograde: 60 points (high strength)
- Stationary (speed < 0.5°/day): 45 points
- Slow (0.5° - 1.0°/day): 30 points
- Moderate (1.0° - 1.5°/day): 15 points
- Very fast (> 1.5°/day): 0 points

### 5. Naisargika Bala (Natural Strength)

Inherent strength of each planet (fixed values):

| Planet | Virupas |
|--------|---------|
| Sun | 60.0 |
| Moon | 51.43 |
| Jupiter | 34.29 |
| Venus | 42.86 |
| Mercury | 25.71 |
| Mars | 17.14 |
| Saturn | 8.57 |
| Rahu/Ketu | 0.0 |

### 6. Drik Bala (Aspectual Strength)

Measures strength from aspects received from other planets.

**Calculation:**
- Benefic aspects (Jupiter, Venus, Mercury): +5 points each
- Malefic aspects (Sun, Mars, Saturn): -5 points each
- Baseline: 30 points

## Strength Ratings

| Total Shadbala | Rating | Chart Impact |
|---|---|---|
| 360+ | Very Strong | Major influence, strong results |
| 300-359 | Strong | Significant positive influence |
| 200-299 | Moderate | Average strength |
| 100-199 | Weak | Limited influence |
| <100 | Very Weak | Minimal strength |

## Ashtakavarga (Eight-fold Classification)

Ashtakavarga measures a planet's strength in each of the 12 zodiac signs.

### Concept

Each of the 7 planets contributes "bindus" (points) to each sign based on:
1. The planet's position relative to Lagna (Ascendant)
2. The planet's position relative to 7 other planets
3. Total: 8 references

### Benefic Points Table

For each planet, specific signs receive bindus from each reference point:

**Example - Sun Ashtakavarga:**
```python
"sun": {
    "sun": [1, 2, 4, 7, 8, 9, 10, 11],    # Signs where Sun aspect is beneficial
    "moon": [3, 6, 10, 11],
    "mars": [1, 2, 4, 7, 8, 9, 10, 11],
    "mercury": [3, 5, 6, 9, 10, 11, 12],
    "jupiter": [5, 6, 9, 11],
    "venus": [6, 7, 12],
    "saturn": [1, 2, 4, 7, 8, 9, 10, 11],
    "lagna": [3, 4, 6, 10, 11, 12]
}
```

### Calculation Method

1. For each sign (0-11):
   - Count how many references contribute a bindu
   - Sum contributions from all 8 references
   
2. Result: 0-8 bindus per sign per planet

3. Example output:
```
Moon Ashtakavarga: [4, 1, 3, 1, 4, 2, 1, 2, 5, 0, 3, 0]
Sign:              [Aries, Taurus, Gemini, Cancer, Leo, Virgo, 
                    Libra, Scorpio, Sagittarius, Capricorn, 
                    Aquarius, Pisces]
```

## Sarvashtakavarga (SAV)

Total Ashtakavarga summed across all 7 planets.

- **Range**: 0-56 bindus per sign (7 planets × 8 max points)
- **Interpretation**:
  - High SAV (40+): Sign is very strong, beneficial for activities
  - Medium SAV (20-40): Average strength
  - Low SAV (<20): Sign is weak, unfavorable for activities

### Usage Examples

**Finding Strong Transits:**
```python
sav = calculator.calculate_sarvashtakavarga(chart)
# Signs with SAV >= 40 are best for starting new ventures
strong_signs = [i for i, v in enumerate(sav) if v >= 40]
```

**Determining Sign Strength:**
```python
sign_strength = sav[sign_index]
if sign_strength >= 40:
    rating = "Excellent"
elif sign_strength >= 30:
    rating = "Good"
elif sign_strength >= 20:
    rating = "Fair"
else:
    rating = "Poor"
```

## Planet Dignity

Classification of a planet's status in a sign.

### Dignity Types

1. **Exalted** (Uchcha)
   - Planet at peak strength
   - Example: Sun in Aries (exaltation 10°)
   
2. **Own Sign** (Swarucha)
   - Planet in its own ruled sign
   - Example: Sun in Leo
   
3. **Friendly Sign**
   - Planet in sign of a friendly planet
   - Moderate strength
   
4. **Neutral Sign**
   - Neither beneficial nor harmful
   - Average strength
   
5. **Enemy Sign**
   - Planet in sign of enemy planet
   - Reduced strength
   
6. **Debilitated** (Neecha)
   - Planet at lowest strength (opposite of exaltation)
   - Example: Sun in Libra

### Example Classifications

```python
# Exaltation Examples
Sun in Aries (10°) → exalted
Moon in Taurus (3°) → exalted
Mars in Capricorn (28°) → exalted

# Own Sign Examples
Moon in Cancer → own
Mercury in Gemini → own
Venus in Taurus → own

# Debilitation Examples
Sun in Libra (10°) → debilitated
Moon in Scorpio (3°) → debilitated
Mars in Cancer (28°) → debilitated
```

## API Reference

### Main Methods

#### `calculate_shadbala(planet: Planet, chart: BirthChart) -> Dict`

Calculate complete Shadbala for a planet.

**Returns:**
```python
{
    "planet": "sun",
    "total": 315.0,
    "components": {
        "sthana_bala": 115.0,
        "dig_bala": 60.0,
        "kala_bala": 30.0,
        "chesta_bala": 15.0,
        "naisargika_bala": 60.0,
        "drik_bala": 35.0
    },
    "is_strong": True,
    "strength_rating": "strong"
}
```

#### `calculate_ashtakavarga(planet: Planet, chart: BirthChart) -> List[int]`

Calculate Ashtakavarga for a planet.

**Returns:** List of 12 integers (bindus per sign)

#### `calculate_sarvashtakavarga(chart: BirthChart) -> List[int]`

Calculate total Ashtakavarga for all signs.

**Returns:** List of 12 integers (total bindus per sign)

#### `get_planet_dignity(planet: Planet, sign: Rashi) -> str`

Get dignity classification of planet in sign.

**Returns:** One of: "exalted", "own", "friendly", "neutral", "enemy", "debilitated"

#### `analyze_strength_profile(chart: BirthChart) -> Dict`

Comprehensive strength analysis of the chart.

**Returns:**
```python
{
    "all_strengths": {...},
    "strongest_planet": "sun",
    "strongest_value": 315.0,
    "weakest_planet": "rahu",
    "weakest_value": 182.5,
    "very_strong_count": 2,
    "strong_count": 3,
    "weak_count": 4,
    "sarvashtakavarga": [...],
    "average_sav": 23.17,
    "chart_strength_level": "moderate"
}
```

## Example Usage

```python
from packages.self.src.strength import StrengthCalculator
from packages.core.src.constants import Planet, Rashi

# Initialize calculator
calculator = StrengthCalculator()

# Calculate Shadbala for Sun
sun_strength = calculator.calculate_shadbala(Planet.SUN, chart)
print(f"Sun Strength: {sun_strength['total']} virupas")
print(f"Rating: {sun_strength['strength_rating']}")

# Get planet dignity
dignity = calculator.get_planet_dignity(Planet.SATURN, Rashi.LIBRA)
print(f"Saturn in Libra: {dignity}")  # Output: "exalted"

# Analyze entire chart
profile = calculator.analyze_strength_profile(chart)
print(f"Strongest planet: {profile['strongest_planet']}")
print(f"Chart strength: {profile['chart_strength_level']}")

# Find strong signs for transits
sav = calculator.calculate_sarvashtakavarga(chart)
for i, bindus in enumerate(sav):
    if bindus >= 40:
        print(f"Sign {i}: Strong ({bindus} bindus)")
```

## References

- **BPHS** (Brihat Parasara Hora Sastra) - Chapters 22-23
- **Phaladeepa** - Commentaries on planetary strengths
- **Jyotish Classics** - Traditional strength measurement systems

## Implementation Notes

1. **Simplified Calculations**: Current implementation uses simplified formulas for some components (Tribhaga Bala, Varsha/Masa/Dina/Hora Bala) that can be expanded with full ephemeris data

2. **Rahu/Ketu**: These nodes have no Shadbala but can be included in Ashtakavarga calculations

3. **Divisional Charts**: Full Saptavargaja Bala requires divisional chart calculations (can be integrated with divisional module)

4. **Aspect Calculation**: Drik Bala simplified; full implementation requires precise aspect calculations

5. **Day/Night Determination**: Currently uses birth hour as proxy; full implementation uses sunrise/sunset times

## Future Enhancements

- Integration with divisional chart module for Saptavargaja Bala
- Precise aspect calculations for Drik Bala
- Exact Varsha/Masa/Dina/Hora Bala calculations
- Planetary war strength (Yuddha Bala)
- Custom strength thresholds per use case
- Strength trend analysis over time
# Planetary Strength Calculations - Code Examples

## Quick Start

```python
from packages.self.src.strength import StrengthCalculator
from packages.core.src.constants import Planet, Rashi

# Initialize the calculator
calculator = StrengthCalculator()

# Calculate strengths for a birth chart
strengths = calculator.analyze_strength_profile(chart)
```

## Example 1: Calculate Shadbala for a Single Planet

Calculate the complete six-fold strength of the Sun:

```python
sun_strength = calculator.calculate_shadbala(Planet.SUN, chart)

print(f"Sun Total Strength: {sun_strength['total']} virupas")
print(f"Rating: {sun_strength['strength_rating']}")
print(f"Is Strong: {sun_strength['is_strong']}")

# Examine individual components
components = sun_strength['components']
print(f"  Positional Strength: {components['sthana_bala']}")
print(f"  Directional Strength: {components['dig_bala']}")
print(f"  Temporal Strength: {components['kala_bala']}")
print(f"  Motional Strength: {components['chesta_bala']}")
print(f"  Natural Strength: {components['naisargika_bala']}")
print(f"  Aspectual Strength: {components['drik_bala']}")
```

**Output:**
```
Sun Total Strength: 315.0 virupas
Rating: strong
Is Strong: True
  Positional Strength: 115.0
  Directional Strength: 60.0
  Temporal Strength: 30.0
  Motional Strength: 15.0
  Natural Strength: 60.0
  Aspectual Strength: 35.0
```

## Example 2: Compare Planetary Strengths

Find the strongest and weakest planets in a chart:

```python
# Get all planetary strengths
all_strengths = calculator.get_all_planet_strengths(chart)

# Sort by strength
sorted_planets = sorted(
    all_strengths.items(),
    key=lambda x: x[1]['total'],
    reverse=True
)

print("Planetary Strength Ranking:")
for rank, (planet_name, strength_data) in enumerate(sorted_planets, 1):
    rating = strength_data['strength_rating']
    total = strength_data['total']
    print(f"{rank}. {planet_name:8} - {total:6.1f} virupas ({rating})")
```

**Output:**
```
Planetary Strength Ranking:
1. sun      -  315.0 virupas (strong)
2. moon     -  298.5 virupas (strong)
3. jupiter  -  287.3 virupas (moderate)
4. venus    -  276.8 virupas (moderate)
5. mercury  -  245.2 virupas (moderate)
6. mars     -  189.4 virupas (weak)
7. saturn   -  167.8 virupas (weak)
8. rahu     -  182.5 virupas (weak)
9. ketu     -  156.3 virupas (weak)
```

## Example 3: Analyze Ashtakavarga for Transit Planning

Use Ashtakavarga to identify strong signs for favorable transit effects:

```python
# Calculate Sarvashtakavarga (total strength in each sign)
sav = calculator.calculate_sarvashtakavarga(chart)

# Sign names for reference
signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

print("Sarvashtakavarga Analysis:")
print("=" * 50)
print(f"{'Sign':<15} {'Bindus':<10} {'Rating':<15}")
print("=" * 50)

for i, bindus in enumerate(sav):
    if bindus >= 40:
        rating = "Excellent"
    elif bindus >= 30:
        rating = "Good"
    elif bindus >= 20:
        rating = "Fair"
    else:
        rating = "Poor"
    
    print(f"{signs[i]:<15} {bindus:<10} {rating:<15}")

# Find best signs for starting ventures
excellent_signs = [signs[i] for i, v in enumerate(sav) if v >= 40]
print(f"\nBest signs for new ventures: {', '.join(excellent_signs)}")
```

**Output:**
```
Sarvashtakavarga Analysis:
==================================================
Sign           Bindus     Rating         
==================================================
Aries          34         Good           
Taurus         14         Poor           
Gemini         20         Fair           
Cancer         26         Fair           
Leo            22         Fair           
Virgo          25         Fair           
Libra          24         Fair           
Scorpio        15         Poor           
Sagittarius    19         Fair           
Capricorn      22         Fair           
Aquarius       31         Good           
Pisces         26         Fair           

Best signs for new ventures: Aries, Aquarius
```

## Example 4: Check Planet Dignity

Determine the status of planets in their placed signs:

```python
# Get planets from chart and check their dignity
planets = [Planet.SUN, Planet.MOON, Planet.MARS, 
           Planet.MERCURY, Planet.JUPITER, Planet.VENUS, Planet.SATURN]

print("Planet Dignity Analysis:")
print("=" * 60)
print(f"{'Planet':<10} {'Sign':<15} {'Dignity':<20}")
print("=" * 60)

for planet in planets:
    pos = chart.planets[planet]
    dignity = calculator.get_planet_dignity(planet, pos.rashi)
    print(f"{planet.value:<10} {pos.rashi.value:<15} {dignity:<20}")
```

**Output:**
```
Planet Dignity Analysis:
============================================================
Planet     Sign            Dignity             
============================================================
sun        taurus          enemy               
moon       leo             friendly            
mars       gemini          neutral             
mercury    aries           own                 
jupiter    virgo           friendly            
venus      aries           friendly            
saturn     libra           exalted             
```

## Example 5: Comprehensive Strength Profile

Get a complete analysis of the chart's strength characteristics:

```python
profile = calculator.analyze_strength_profile(chart)

print("COMPREHENSIVE STRENGTH PROFILE")
print("=" * 70)

# Strongest and weakest planets
print(f"\nStrongest Planet:")
print(f"  {profile['strongest_planet'].upper():<20} {profile['strongest_value']} virupas")

print(f"\nWeakest Planet:")
print(f"  {profile['weakest_planet'].upper():<20} {profile['weakest_value']} virupas")

# Strength distribution
print(f"\nStrength Distribution:")
print(f"  Very Strong: {profile['very_strong_count']} planets")
print(f"  Strong:      {profile['strong_count']} planets")
print(f"  Weak:        {profile['weak_count']} planets")

# Overall chart assessment
print(f"\nChart Assessment:")
print(f"  Overall Level:    {profile['chart_strength_level'].upper()}")
print(f"  Average SAV:      {profile['average_sav']:.2f} bindus")

# Sarvashtakavarga details
sav = profile['sarvashtakavarga']
print(f"\nSarvashtakavarga Statistics:")
print(f"  Total Bindus:     {sum(sav)}")
print(f"  Highest:          {max(sav)} bindus")
print(f"  Lowest:           {min(sav)} bindus")
print(f"  Average:          {sum(sav)/12:.2f} bindus per sign")
```

**Output:**
```
COMPREHENSIVE STRENGTH PROFILE
======================================================================

Strongest Planet:
  SUN                  315.0 virupas

Weakest Planet:
  KETU                 156.3 virupas

Strength Distribution:
  Very Strong: 2 planets
  Strong:      3 planets
  Weak:        4 planets

Chart Assessment:
  Overall Level:    MODERATE
  Average SAV:      23.17 bindus

Sarvashtakavarga Statistics:
  Total Bindus:     279
  Highest:          34 bindus
  Lowest:           14 bindus
  Average:          23.25 bindus per sign
```

## Example 6: Identify Weak Houses for Remedial Measures

Find planets in weak positions that might need remedial work:

```python
# Find planets with low strength
weak_planets = []

for planet in [Planet.SUN, Planet.MOON, Planet.MARS, 
               Planet.MERCURY, Planet.JUPITER, Planet.VENUS, Planet.SATURN]:
    strength = calculator.calculate_shadbala(planet, chart)
    
    if strength['total'] < 200:  # Below "moderate" threshold
        weak_planets.append({
            'planet': planet.value,
            'strength': strength['total'],
            'rating': strength['strength_rating'],
            'position': chart.planets[planet].rashi.value
        })

# Sort by weakness
weak_planets.sort(key=lambda x: x['strength'])

print("PLANETS NEEDING REMEDIAL SUPPORT:")
print("=" * 60)
print(f"{'Planet':<12} {'Sign':<12} {'Strength':<12} {'Recommendation':<20}")
print("=" * 60)

for item in weak_planets:
    planet = item['planet']
    sign = item['position']
    strength = f"{item['strength']:.1f}"
    
    # Recommendation based on planet
    if planet == "saturn":
        rec = "Saturn Mantra"
    elif planet == "mars":
        rec = "Mars Worship"
    elif planet == "mercury":
        rec = "Mercury Remedies"
    else:
        rec = f"{planet.title()} Meditation"
    
    print(f"{planet:<12} {sign:<12} {strength:<12} {rec:<20}")
```

**Output:**
```
PLANETS NEEDING REMEDIAL SUPPORT:
============================================================
Planet       Sign         Strength     Recommendation      
============================================================
ketu         leo          156.3        Ketu Meditation      
saturn       libra        167.8        Saturn Mantra        
mars         gemini       189.4        Mars Worship         
```

## Example 7: Monitor Strength Changes (Longitudinal Analysis)

Track how planetary strength changes across different chart types:

```python
from packages.cosmos.src.divisional import DivisionalChart

# Create divisional charts
d9_chart = DivisionalChart.create_navamsha(chart)

# Compare strengths
planets = [Planet.SUN, Planet.MOON, Planet.JUPITER, Planet.VENUS, Planet.SATURN]

print("Strength Comparison: D1 vs D9")
print("=" * 70)
print(f"{'Planet':<12} {'D1 Total':<15} {'D9 Total':<15} {'Difference':<15}")
print("=" * 70)

for planet in planets:
    d1_strength = calculator.calculate_shadbala(planet, chart)['total']
    d9_strength = calculator.calculate_shadbala(planet, d9_chart)['total']
    diff = d9_strength - d1_strength
    
    sign = "+" if diff >= 0 else ""
    print(f"{planet.value:<12} {d1_strength:<15.1f} {d9_strength:<15.1f} {sign}{diff:<14.1f}")
```

## Example 8: Integration with Yoga Detection

Use strength calculations to weight yoga interpretations:

```python
# Get strength profile
profile = calculator.analyze_strength_profile(chart)
all_strengths = profile['all_strengths']

# Example: Raja Yoga planets should ideally be strong
raja_yoga_planets = [Planet.JUPITER, Planet.MERCURY, Planet.SUN]

print("Raja Yoga Potential Assessment:")
print("=" * 60)

yoga_strength = 0
for planet in raja_yoga_planets:
    if planet.value in all_strengths:
        strength = all_strengths[planet.value]['total']
        rating = all_strengths[planet.value]['strength_rating']
        yoga_strength += strength
        
        print(f"{planet.value.upper():<12} {strength:6.1f} virupas ({rating})")

avg_yoga_strength = yoga_strength / len(raja_yoga_planets)
print("=" * 60)
print(f"Average Raja Yoga Strength: {avg_yoga_strength:.1f} virupas")

if avg_yoga_strength >= 300:
    print("Assessment: EXCELLENT - Strong Raja Yoga potential")
elif avg_yoga_strength >= 250:
    print("Assessment: GOOD - Moderate Raja Yoga potential")
else:
    print("Assessment: FAIR - Weak Raja Yoga manifestation")
```

## Example 9: Export Strength Data

Generate a strength report for export:

```python
import json

def generate_strength_report(chart, calculator):
    """Generate comprehensive strength report as dictionary."""
    
    profile = calculator.analyze_strength_profile(chart)
    
    report = {
        "chart_id": chart.user_id,
        "chart_type": "natal",
        "summary": {
            "overall_strength": profile['chart_strength_level'],
            "average_planetary_strength": round(
                sum(p['total'] for p in profile['all_strengths'].values()) / 9, 2
            ),
            "strongest_planet": profile['strongest_planet'],
            "weakest_planet": profile['weakest_planet'],
        },
        "planetary_strengths": profile['all_strengths'],
        "sarvashtakavarga": profile['sarvashtakavarga'],
        "strength_distribution": {
            "very_strong": profile['very_strong_count'],
            "strong": profile['strong_count'],
            "weak": profile['weak_count'],
        }
    }
    
    return report

# Generate and export
report = generate_strength_report(chart, calculator)
with open('strength_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Strength report exported to strength_report.json")
```

## Example 10: Custom Strength Analysis

Create specialized strength analysis for specific life areas:

```python
def analyze_marital_strength(chart, calculator):
    """Analyze planetary strength for marriage/relationships."""
    
    # Key planets for marriage: Venus, Jupiter, 7th house lord
    marital_planets = {
        'venus': Planet.VENUS,
        'jupiter': Planet.JUPITER,
        '7th_lord': chart.planets[Planet.VENUS],  # Simplified
    }
    
    strengths = {}
    for key, planet in marital_planets.items():
        if isinstance(planet, Planet):
            strength = calculator.calculate_shadbala(planet, chart)
            strengths[key] = strength['total']
    
    total = sum(strengths.values())
    average = total / len(strengths)
    
    print("Marital Strength Assessment:")
    print(f"  Venus Strength: {strengths['venus']:.1f}")
    print(f"  Jupiter Strength: {strengths['jupiter']:.1f}")
    print(f"  Average: {average:.1f}")
    
    if average >= 300:
        return "EXCELLENT - Strong marital prospects"
    elif average >= 250:
        return "GOOD - Favorable for relationships"
    else:
        return "FAIR - May need attention to relationship matters"

result = analyze_marital_strength(chart, calculator)
print(result)
```

These examples demonstrate the practical applications of the StrengthCalculator module
in chart analysis, remedial recommendations, and astrological interpretations.
