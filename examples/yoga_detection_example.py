"""
Usage Examples for Yoga Detection Engine
========================================

This file contains practical examples of how to use the yoga detection engine
in the 108 Vedic Astrology application.
"""


from packages.core.src import BirthChart
from packages.self.src import YogaDetector, detect_all_yogas

# ==============================================================================
# Example 1: Basic Yoga Detection
# ==============================================================================


def example_basic_yoga_detection():
    """Detect all yogas in a birth chart."""

    # Assume you have a birth chart (loaded from database or API)
    chart = BirthChart(...)

    # Method 1: Using convenience function
    yogas = detect_all_yogas(chart)

    # Print results
    for yoga in yogas:
        print(f"Name: {yoga.name}")
        print(f"Category: {yoga.category.value}")
        print(f"Strength: {yoga.strength:.0%}")
        print(f"Description: {yoga.description}")
        print()


# ==============================================================================
# Example 2: Using the YogaDetector Class
# ==============================================================================


def example_yoga_detector_class():
    """Use the YogaDetector class directly."""

    chart = BirthChart(...)

    # Initialize detector
    detector = YogaDetector()

    # Detect all yogas
    all_yogas = detector.detect_all_yogas(chart)

    # Filter by category
    raja_yogas = [y for y in all_yogas if y.category.value == "raja"]
    print(f"Found {len(raja_yogas)} Raja Yogas")

    # Sort by strength
    strongest_yogas = sorted(all_yogas, key=lambda y: y.strength, reverse=True)

    # Get strongest yoga
    if strongest_yogas:
        strongest = strongest_yogas[0]
        print(f"Strongest yoga: {strongest.name} ({strongest.strength:.0%})")


# ==============================================================================
# Example 3: Detect a Specific Yoga
# ==============================================================================


def example_detect_specific_yoga():
    """Detect a single yoga by ID."""

    chart = BirthChart(...)
    detector = YogaDetector()

    # Get specific yoga rule
    rule = detector.yoga_rules.get("gaj_kesari_yoga")

    if rule:
        # Detect this yoga
        yoga = detector.detect_yoga(rule, chart)

        if yoga and yoga.is_present:
            print("Gaj Kesari Yoga detected!")
            print(f"Strength: {yoga.strength:.1%}")
            print(f"Involved planets: {[p.value for p in yoga.involved_planets]}")
        else:
            print("Gaj Kesari Yoga not present in chart")


# ==============================================================================
# Example 4: Evaluate Custom Conditions
# ==============================================================================


def example_evaluate_conditions():
    """Evaluate custom planetary conditions."""

    chart = BirthChart(...)
    detector = YogaDetector()

    # Check if Jupiter is in kendra
    condition = {"type": "in_kendra", "planet": "jupiter"}
    is_jupiter_kendra = detector._evaluate_condition(condition, chart)
    print(f"Jupiter in Kendra: {is_jupiter_kendra}")

    # Check if Mars and Venus are conjunct
    condition = {"type": "conjunct", "planets": ["mars", "venus"]}
    are_conjunct = detector._evaluate_condition(condition, chart)
    print(f"Mars and Venus conjunct: {are_conjunct}")

    # Check if Mercury is in own or exalted sign
    condition = {"type": "in_own_or_exalted_sign", "planet": "mercury"}
    is_strong = detector._evaluate_condition(condition, chart)
    print(f"Mercury strong (own/exalted): {is_strong}")


# ==============================================================================
# Example 5: Analyze Pancha Mahapurusha Yogas
# ==============================================================================


def example_pancha_mahapurusha_yogas():
    """Detect and analyze all Pancha Mahapurusha yogas."""

    chart = BirthChart(...)
    detector = YogaDetector()

    # Get all Pancha Mahapurusha yogas
    all_yogas = detector.detect_all_yogas(chart)
    mahapurusha_yogas = [y for y in all_yogas if y.category.value == "pancha_mahapurusha"]

    if mahapurusha_yogas:
        print("Pancha Mahapurusha Yogas Present:")
        for yoga in mahapurusha_yogas:
            print(f"  - {yoga.name} (Strength: {yoga.strength:.0%})")
    else:
        print("No Pancha Mahapurusha yogas detected")


# ==============================================================================
# Example 6: Get Yoga Information
# ==============================================================================


def example_yoga_information():
    """Get detailed information about detected yogas."""

    chart = BirthChart(...)
    yogas = detect_all_yogas(chart)

    for yoga in yogas:
        print(f"Yoga: {yoga.name}")
        print(f"  ID: {yoga.yoga_id}")
        print(f"  Category: {yoga.category.value}")
        print(f"  Present: {yoga.is_present}")
        print(f"  Strength: {yoga.strength:.1%}")
        print(f"  Involved Planets: {[p.value for p in yoga.involved_planets]}")
        print(f"  Description: {yoga.description}")
        print()


# ==============================================================================
# Example 7: Check Yoga Strength
# ==============================================================================


def example_yoga_strength():
    """Get and analyze yoga strength."""

    chart = BirthChart(...)
    yogas = detect_all_yogas(chart)

    # Get yogas by strength level
    strong_yogas = [y for y in yogas if y.strength >= 0.8]
    moderate_yogas = [y for y in yogas if 0.5 <= y.strength < 0.8]
    weak_yogas = [y for y in yogas if y.strength < 0.5]

    print(f"Strong yogas (80%+): {len(strong_yogas)}")
    for yoga in strong_yogas:
        print(f"  - {yoga.name}: {yoga.strength:.0%}")

    print(f"\nModerate yogas (50-80%): {len(moderate_yogas)}")
    print(f"Weak yogas (<50%): {len(weak_yogas)}")


# ==============================================================================
# Example 8: List All Available Rules
# ==============================================================================


def example_list_available_rules():
    """Display all available yoga rules."""

    detector = YogaDetector()

    print("Available Yoga Rules:")
    print("-" * 60)

    for yoga_id, rule in detector.yoga_rules.items():
        category = rule.get("category", "unknown")
        name = rule.get("name", "Unknown")
        print(f"  {name:40} ({category})")
        print(f"    ID: {yoga_id}")
        print()


# ==============================================================================
# Example 9: Integration with Chart Analysis
# ==============================================================================


def example_integration_with_chart_analysis():
    """Integrate yoga detection into broader chart analysis."""

    chart = BirthChart(...)

    # Get yogas
    yogas = detect_all_yogas(chart)

    # Analyze chart
    analysis = {
        "lagna": chart.lagna_rashi.value,
        "moon": chart.moon_rashi.value,
        "moon_nakshatra": chart.moon_nakshatra,
        "yogas": [
            {
                "name": y.name,
                "category": y.category.value,
                "strength": y.strength,
            }
            for y in yogas
        ],
    }

    return analysis


# ==============================================================================
# Example 10: Filter Yogas by Category
# ==============================================================================


def example_filter_yogas_by_category():
    """Filter detected yogas by category."""

    chart = BirthChart(...)
    yogas = detect_all_yogas(chart)

    # Group by category
    by_category = {}
    for yoga in yogas:
        category = yoga.category.value
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(yoga)

    # Print grouped results
    for category, category_yogas in sorted(by_category.items()):
        print(f"\n{category.upper()} Yogas:")
        for yoga in category_yogas:
            print(f"  - {yoga.name} ({yoga.strength:.0%})")


# ==============================================================================
# Example 11: Export Yoga Data
# ==============================================================================


def example_export_yoga_data():
    """Export yoga detection results."""

    chart = BirthChart(...)
    yogas = detect_all_yogas(chart)

    # Export as JSON
    import json

    data = {
        "user_id": chart.user_id,
        "yogas": [
            {
                "id": y.yoga_id,
                "name": y.name,
                "category": y.category.value,
                "strength": y.strength,
                "planets": [p.value for p in y.involved_planets],
            }
            for y in yogas
        ],
        "total_count": len(yogas),
    }

    json_str = json.dumps(data, indent=2)
    print(json_str)

    return data


# ==============================================================================
# Example 12: Performance Testing
# ==============================================================================


def example_performance_testing():
    """Test performance of yoga detection."""

    import time

    chart = BirthChart(...)

    # Time the detection
    start = time.time()
    yogas = detect_all_yogas(chart)
    elapsed = time.time() - start

    print(f"Detection Time: {elapsed*1000:.2f}ms")
    print(f"Yogas Detected: {len(yogas)}")
    print(f"Average Time per Yoga: {(elapsed/len(yogas))*1000:.2f}ms")


# ==============================================================================
# Example 13: Custom Condition Evaluation
# ==============================================================================


def example_custom_condition():
    """Define and evaluate custom conditions."""

    chart = BirthChart(...)
    detector = YogaDetector()

    # Complex condition: Mercury in 2nd, 4th, 5th, 9th, or 10th
    condition = {"type": "in_house", "planet": "mercury", "houses": [2, 4, 5, 9, 10]}

    result = detector._evaluate_condition(condition, chart)
    print(f"Mercury in favorable houses: {result}")


# ==============================================================================
# Example 14: Planetary Position Analysis with Yogas
# ==============================================================================


def example_planetary_position_with_yogas():
    """Analyze planetary positions alongside yoga detection."""

    chart = BirthChart(...)
    detector = YogaDetector()

    # Get planet information
    for planet, position in chart.planets.items():
        print(f"\n{planet.value.upper()}:")
        print(f"  Rashi: {position.rashi.value}")
        print(f"  House: {position.house}")
        print(f"  Nakshatra: {position.nakshatra}")

        # Check this planet for yoga involvement
        involved_yogas = []
        for yoga in detector.detect_all_yogas(chart):
            if planet in yoga.involved_planets:
                involved_yogas.append(yoga.name)

        if involved_yogas:
            print(f"  Involved in: {', '.join(involved_yogas)}")


# ==============================================================================
# Example 15: Yoga Strength Interpretation
# ==============================================================================


def example_yoga_strength_interpretation():
    """Interpret yoga strength levels."""

    chart = BirthChart(...)
    yogas = detect_all_yogas(chart)

    def interpret_strength(strength):
        if strength >= 0.9:
            return "Very Strong"
        elif strength >= 0.75:
            return "Strong"
        elif strength >= 0.5:
            return "Moderate"
        else:
            return "Weak"

    for yoga in yogas:
        interpretation = interpret_strength(yoga.strength)
        print(f"{yoga.name}: {interpretation} ({yoga.strength:.0%})")


if __name__ == "__main__":
    print("Yoga Detection Engine Examples")
    print("=" * 60)
    print("\nThese examples show various ways to use the yoga detection engine.")
    print("Import the functions and adapt them to your use case.")
