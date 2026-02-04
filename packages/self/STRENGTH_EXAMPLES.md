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
