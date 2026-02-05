"""Detailed examples and usage patterns for the Transits (Gochara) module.

This file demonstrates practical applications of the transit analysis system
for different scenarios and birth chart configurations.
"""

from packages.context.src.transits import (
    check_dhaiya,
    check_sade_sati,
    get_full_transit_analysis,
    get_gochara,
    get_transiting_planet_house,
    validate_transit_data,
)


def example_1_aquarius_moon_sade_sati():
    """Example 1: Aquarius Moon in Sade Sati final phase."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Aquarius Moon - Sade Sati Final Phase")
    print("=" * 70)

    # Native with Aquarius Moon (index 10)

    # Case 1: Saturn in Pisces (11) = 2nd from Moon = Setting Phase
    print("\nScenario: Saturn in Pisces (native's 2nd house from Moon)")
    result = check_sade_sati(natal_moon_rashi=10, saturn_rashi=11)

    print(f"Active: {result['active']}")
    print(f"Phase: {result['phase']}")
    print(f"Description: {result['description']}")
    print("Effects:")
    for effect in result["effects"]:
        print(f"  - {effect}")
    print("Remedies:")
    for remedy in result["remedies"]:
        print(f"  - {remedy}")

    # Case 2: Saturn in Aquarius (10) = 1st from Moon = Peak Phase
    print("\nScenario: Saturn in Aquarius (native's 1st house from Moon)")
    result = check_sade_sati(natal_moon_rashi=10, saturn_rashi=10)

    print(f"Phase: {result['phase']}")
    print(f"Description: {result['description']}")
    print("Most critical effects:")
    for effect in result["effects"]:
        print(f"  - {effect}")


def example_2_capricorn_moon_dhaiya():
    """Example 2: Capricorn Moon experiencing Dhaiya."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Capricorn Moon - Dhaiya Period")
    print("=" * 70)

    # Capricorn Moon (index 9)

    # Case 1: Saturn in Aries (0) = 4th from Moon = Kantaka Shani
    print("\nScenario: Saturn in Aries (4th from Capricorn Moon)")
    result = check_dhaiya(natal_moon_rashi=9, saturn_rashi=0)

    print(f"Active: {result['active']}")
    print(f"Type: {result['type']}")
    print(f"Description: {result['description']}")
    print("Likely Experiences:")
    for effect in result["effects"]:
        print(f"  - {effect}")

    # Case 2: Saturn in Taurus (1) = 8th from Moon = Ashtama Shani
    print("\nScenario: Saturn in Taurus (8th from Capricorn Moon)")
    result = check_dhaiya(natal_moon_rashi=9, saturn_rashi=1)

    print(f"Type: {result['type']}")
    print(f"Description: {result['description']}")
    print("Likely Experiences:")
    for effect in result["effects"]:
        print(f"  - {effect}")


def example_3_gochara_with_vedha():
    """Example 3: Gochara analysis with Vedha obstruction."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Gochara with Vedha - Jupiter Obstructed")
    print("=" * 70)

    # Jupiter favorable in 5th from Cancer
    # But Saturn in 4th acts as vedha
    transit_positions = {
        "jupiter": 8,  # Sagittarius = 5th from Cancer (3)
        "saturn": 7,  # Scorpio = 4th from Cancer (vedha point)
        "sun": 0,
        "moon": 1,
        "mars": 2,
        "mercury": 4,
        "venus": 5,
        "rahu": 6,
        "ketu": 9,
    }

    print("\nJupiter in Sagittarius (5th from Cancer Moon):")
    print("  - Naturally favorable position")
    print("  - Saturn in Scorpio (4th from Moon)")
    print("  - Saturn blocks Jupiter's beneficial results (vedha)")

    # Without vedha check
    result_without_vedha = get_gochara(
        natal_moon_rashi=3,
        transit_planet="jupiter",
        transit_rashi=8,
    )

    print("\nWithout vedha consideration:")
    print(f"  Is Favorable: {result_without_vedha['is_favorable']}")
    print(f"  Net Effect: {result_without_vedha['net_effect']}")

    # With vedha check
    result_with_vedha = get_gochara(
        natal_moon_rashi=3,
        transit_planet="jupiter",
        transit_rashi=8,
        all_transit_rashis=transit_positions,
    )

    print("\nWith vedha analysis:")
    print(f"  Is Favorable: {result_with_vedha['is_favorable']}")
    print(f"  Has Vedha: {result_with_vedha['has_vedha']}")
    print(f"  Obstructed by: {result_with_vedha['vedha_by']}")
    print(f"  Net Effect: {result_with_vedha['net_effect']}")
    print("  Jupiter's benefits are BLOCKED despite favorable position!")


def example_4_complete_transit_analysis():
    """Example 4: Complete multi-planet transit analysis."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Complete Transit Analysis - Leo Moon Native")
    print("=" * 70)

    # Leo Moon (index 4)
    natal_moon = 4

    # Simulated transit positions (as would come from ephemeris)
    transit_positions = {
        "sun": 1,  # Taurus
        "moon": 2,  # Gemini
        "mars": 4,  # Leo (same as Moon)
        "mercury": 5,  # Virgo
        "jupiter": 7,  # Scorpio
        "venus": 8,  # Sagittarius
        "saturn": 10,  # Aquarius
        "rahu": 11,  # Pisces
        "ketu": 5,  # Virgo
    }

    print("\nNatal Moon: Leo (4)")
    print("Current Transit Configuration:")
    for planet, rashi in sorted(transit_positions.items()):
        rashi_names = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]
        print(f"  {planet.capitalize():10} in {rashi_names[rashi]}")

    # Get full analysis
    analysis = get_full_transit_analysis(natal_moon, transit_positions)

    print("\n--- SATURN TRANSITS ---")
    print(f"Sade Sati Active: {analysis['sade_sati']['active']}")
    if not analysis["sade_sati"]["active"]:
        print(f"  Saturn is {analysis['sade_sati']['house_from_moon']} houses from Moon")
        print("  Not in Sade Sati period")

    print(f"\nDhaiya Active: {analysis['dhaiya']['active']}")
    if not analysis["dhaiya"]["active"]:
        print("  Saturn not in 4th or 8th from Moon")

    print("\n--- PLANETARY TRANSITS SUMMARY ---")
    print(f"Favorable: {analysis['summary']['favorable_count']}")
    print(f"Unfavorable: {analysis['summary']['unfavorable_count']}")
    print(f"Overall Trend: {analysis['summary']['overall_trend'].upper()}")

    print("\n--- DETAILED PLANET ANALYSIS ---")
    for planet in ["sun", "mars", "jupiter", "venus", "saturn"]:
        if planet in analysis["planet_transits"]:
            gochara = analysis["planet_transits"][planet]
            house = gochara["house_from_moon"]
            effect = gochara["net_effect"]
            favorable = "✓" if gochara["is_favorable"] else "✗"

            status = effect.upper()
            if gochara["has_vedha"]:
                status += f" (Obstructed by {gochara['vedha_by']})"

            print(f"\n{planet.upper()} - House {house} [{favorable}]")
            print(f"  Status: {status}")
            if gochara["effects"]:
                print(f"  Effects: {gochara['effects'][0]}")


def example_5_house_by_house_analysis():
    """Example 5: Understanding each house from Moon."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: House-by-House Transit Analysis")
    print("=" * 70)

    natal_moon = 5  # Virgo Moon

    print("\nFor a Virgo Moon (5), here's what each transit house means:\n")

    house_descriptions = {
        1: "Same sign as Moon - Conjunct - Very influential",
        2: "Next sign - Aspect of Sade Sati setting phase",
        3: "Favorable for most planets - Good position",
        4: "Dhaiya (Kantaka Shani) if Saturn",
        5: "Favorable for Jupiter - Trine from Moon",
        6: "Favorable for Mars, Saturn, Sun - 6th house benefits",
        7: "Opposite Moon - Opposition/Conflict",
        8: "Dhaiya (Ashtama Shani) if Saturn - Very challenging",
        9: "Favorable for Jupiter - Natural benefic position",
        10: "Favorable for Sun, Saturn - Powerful position",
        11: "Favorable for most planets - 11th house gains",
        12: "Sade Sati rising phase if Saturn",
    }

    for house, description in house_descriptions.items():
        print(f"House {house:2d}: {description}")

    print("\n--- TESTING EACH POSITION ---")
    for house in range(1, 13):
        # Calculate rashi that would be in this house
        test_rashi = (natal_moon + house - 1) % 12

        house_actual = get_transiting_planet_house(natal_moon, "sun", test_rashi)
        print(f"House {house:2d}: Rashi {test_rashi:2d} -> {house_actual}")


def example_6_validation_and_error_handling():
    """Example 6: Data validation and error handling."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Data Validation")
    print("=" * 70)

    # Test case 1: Valid data
    print("\nTest 1: Valid transit data")
    is_valid, msg = validate_transit_data(
        natal_moon_rashi=10, transit_positions={"sun": 0, "moon": 1, "mars": 2}
    )
    print(f"  Valid: {is_valid} - {msg}")

    # Test case 2: Invalid Moon rashi
    print("\nTest 2: Invalid Moon rashi (> 11)")
    is_valid, msg = validate_transit_data(natal_moon_rashi=12, transit_positions={"sun": 0})
    print(f"  Valid: {is_valid} - {msg}")

    # Test case 3: Invalid planet rashi
    print("\nTest 3: Invalid planet rashi (< 0)")
    is_valid, msg = validate_transit_data(natal_moon_rashi=10, transit_positions={"sun": -1})
    print(f"  Valid: {is_valid} - {msg}")

    # Test case 4: Empty positions
    print("\nTest 4: Empty transit positions")
    is_valid, msg = validate_transit_data(natal_moon_rashi=10, transit_positions={})
    print(f"  Valid: {is_valid} - {msg}")


def example_7_comparative_analysis():
    """Example 7: Compare transits for different scenarios."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Comparative Analysis - Two Different Scenarios")
    print("=" * 70)

    print("\nSCENARIO A: Favorable transits")
    transit_a = {
        "sun": 8,  # 3rd house - favorable
        "jupiter": 10,  # 5th house - favorable
        "venus": 11,  # 6th house - favorable
        "saturn": 0,  # 7th house - neutral
        "mars": 1,  # 8th house - challenging
        "mercury": 2,  # 9th house
        "moon": 3,  # 10th house - favorable
        "rahu": 4,  # 11th house - challenging
        "ketu": 5,  # 12th house - neutral
    }

    analysis_a = get_full_transit_analysis(6, transit_a)
    print("\nResult:")
    print(f"  Favorable planets: {analysis_a['summary']['favorable_count']}")
    print(f"  Unfavorable planets: {analysis_a['summary']['unfavorable_count']}")
    print(f"  Overall trend: {analysis_a['summary']['overall_trend']}")

    print("\n" + "-" * 70)
    print("\nSCENARIO B: Challenging transits")
    transit_b = {
        "sun": 3,  # 10th house - unfavorable
        "jupiter": 1,  # 8th house - unfavorable
        "venus": 2,  # 9th house - unfavorable
        "saturn": 5,  # 12th house - challenging
        "mars": 6,  # 1st house - unfavorable
        "mercury": 7,  # 2nd house - challenging
        "moon": 4,  # 11th house - favorable
        "rahu": 8,  # 3rd house - favorable
        "ketu": 9,  # 4th house - neutral
    }

    analysis_b = get_full_transit_analysis(6, transit_b)
    print("\nResult:")
    print(f"  Favorable planets: {analysis_b['summary']['favorable_count']}")
    print(f"  Unfavorable planets: {analysis_b['summary']['unfavorable_count']}")
    print(f"  Overall trend: {analysis_b['summary']['overall_trend']}")

    print("\n" + "-" * 70)
    print("\nCOMPARISON:")
    print(f"Scenario A is more {analysis_a['summary']['overall_trend']}")
    print(f"Scenario B is more {analysis_b['summary']['overall_trend']}")


def example_8_planet_specific_analysis():
    """Example 8: Analyze specific planets' transits."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Specific Planet Analysis - Venus Transits")
    print("=" * 70)

    natal_moon = 0  # Aries

    # Venus is very favorable (9 out of 12 houses)
    print("\nVenus favorable houses from Aries Moon:")
    favorable_houses = [1, 2, 3, 4, 5, 8, 9, 11, 12]

    for house in favorable_houses:
        # Calculate what rashi would be in this house
        rashi = (natal_moon + house - 1) % 12
        rashi_names = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]

        result = get_gochara(natal_moon_rashi=0, transit_planet="venus", transit_rashi=rashi)

        print(f"  House {house:2d} ({rashi_names[rashi]:11}) - {result['net_effect'].upper()}")

    print("\nVenus less favorable houses:")
    unfavorable_houses = [6, 7, 10]

    for house in unfavorable_houses:
        rashi = (natal_moon + house - 1) % 12
        rashi_names = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]

        result = get_gochara(natal_moon_rashi=0, transit_planet="venus", transit_rashi=rashi)

        print(f"  House {house:2d} ({rashi_names[rashi]:11}) - {result['net_effect'].upper()}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("GOCHARA (TRANSIT) ANALYSIS - COMPREHENSIVE EXAMPLES")
    print("=" * 70)

    example_1_aquarius_moon_sade_sati()
    example_2_capricorn_moon_dhaiya()
    example_3_gochara_with_vedha()
    example_4_complete_transit_analysis()
    example_5_house_by_house_analysis()
    example_6_validation_and_error_handling()
    example_7_comparative_analysis()
    example_8_planet_specific_analysis()

    print("\n" + "=" * 70)
    print("END OF EXAMPLES")
    print("=" * 70)
