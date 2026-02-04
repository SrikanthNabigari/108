"""Dosha detection engine for identifying afflictions in Vedic birth charts.

This module implements detection algorithms for major doshas including:
- Mangal Dosha (Mars affliction)
- Kaal Sarp Dosha (Rahu-Ketu axis affliction)
- Pitra Dosha (ancestral karma)
- Grahan Dosha (eclipse shadow affliction)
- Guru Chandal Dosha (Jupiter-Rahu affliction)

Doshas represent karmic challenges or afflictions that require remedial measures.
Each dosha detection includes severity assessment and cancellation conditions.
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass

from packages.core.src.models import BirthChart, PlanetPosition, DetectedDosha
from packages.core.src.constants import Planet, Rashi


@dataclass
class AspectInfo:
    """Information about planetary aspects."""
    planet1: Planet
    planet2: Planet
    distance: float  # Angular distance in degrees
    is_aspecting: bool
    aspect_type: str  # "conjunction", "opposition", "aspect"


class DoshaDetector:
    """Engine for detecting doshas (afflictions) in birth charts.

    Implements comprehensive dosha detection with support for:
    - Multiple viewpoints (Lagna, Moon, Venus)
    - Severity assessment
    - Cancellation conditions
    - Remedial recommendations

    Attributes:
        MANGAL_CRITICAL_HOUSES: Houses where Mars causes Mangal Dosha
        KAAL_SARP_TYPES: Mapping of Rahu house positions to dosha names
        CONJUNCTION_ORBS: Orb limits for conjunction aspects (in degrees)
        ASPECT_ORBS: Orb limits for major aspects (in degrees)
    """

    # Houses that trigger Mangal Dosha when Mars is present
    MANGAL_CRITICAL_HOUSES = [1, 2, 4, 7, 8, 12]

    # Kaal Sarp Dosha types based on Rahu position
    KAAL_SARP_TYPES = {
        1: "Anant",
        2: "Kulik",
        3: "Vasuki",
        4: "Shankpal",
        5: "Padma",
        6: "Mahapadma",
        7: "Takshak",
        8: "Karkotat",
        9: "Shankhchud",
        10: "Ghatak",
        11: "Vishdhar",
        12: "Sheshnag"
    }

    # Angular orbs for aspects (in degrees)
    CONJUNCTION_ORB = 8  # Conjunction allowance
    OPPOSITION_ORB = 8   # Opposition (180°) allowance
    TRINE_ORB = 6        # Trine (120°) allowance
    SQUARE_ORB = 6       # Square (90°) allowance
    SEXTILE_ORB = 4      # Sextile (60°) allowance

    # Mars exaltation and own sign details
    MARS_OWN_SIGNS = [Rashi.ARIES, Rashi.SCORPIO]
    MARS_EXALTED_SIGN = Rashi.CAPRICORN

    # Jupiter aspects (for cancellation and strengthening)
    JUPITER_FULL_ASPECT_DISTANCE = 120  # Jupiter's 5th and 9th aspect

    def __init__(self):
        """Initialize the dosha detector."""
        self.dosha_rules = self._load_dosha_rules()

    def _load_dosha_rules(self) -> Dict[str, Dict]:
        """Load dosha detection rules and thresholds.

        Returns:
            Dictionary containing dosha-specific rules and parameters
        """
        return {
            "mangal": {
                "critical_houses": self.MANGAL_CRITICAL_HOUSES,
                "severe_houses": [7, 8],
                "moderate_houses": [4, 12],
                "mild_houses": [1, 2],
                "viewpoints": ["lagna", "moon", "venus"],
                "cancellation_conditions": [
                    "mars_in_own_sign",
                    "mars_in_exalted_sign",
                    "mars_aspected_by_jupiter",
                    "mars_conjunct_jupiter",
                    "strong_mars_in_natal_chart"
                ]
            },
            "kaal_sarp": {
                "description": "All planets hemmed between Rahu-Ketu axis",
                "types": self.KAAL_SARP_TYPES,
                "cancellation_conditions": [
                    "rahu_in_12th_house",
                    "rahu_aspected_by_jupiter",
                    "ketu_in_6th_house",
                    "jupiter_conjunction_rahu"
                ]
            },
            "pitra": {
                "description": "Ancestral karma affliction",
                "triggers": ["sun_rahu_conjunction_in_trikona"],
                "severity_factors": ["sun_in_1st", "sun_in_5th", "sun_in_9th"]
            },
            "grahan": {
                "sun_triggers": ["sun_rahu", "sun_ketu"],
                "moon_triggers": ["moon_rahu", "moon_ketu"],
                "severity": "moderate"
            },
            "guru_chandal": {
                "description": "Jupiter-Rahu conjunction or opposition",
                "triggers": ["jupiter_rahu_conjunction", "jupiter_rahu_opposition"],
                "severity": "variable"
            }
        }

    def detect_all(self, chart: BirthChart) -> List[DetectedDosha]:
        """Detect all doshas present in the birth chart.

        Systematically checks all major doshas and returns a list
        of detected afflictions with severity and remedial measures.

        Args:
            chart: Complete birth chart with planetary positions

        Returns:
            List of detected doshas, may be empty if no doshas present
        """
        doshas = []

        # Check each major dosha type
        if mangal := self.detect_mangal_dosha(chart):
            doshas.append(mangal)

        if kaal_sarp := self.detect_kaal_sarp_dosha(chart):
            doshas.append(kaal_sarp)

        if pitra := self.detect_pitra_dosha(chart):
            doshas.append(pitra)

        if grahan := self.detect_grahan_dosha(chart):
            doshas.append(grahan)

        if guru_chandal := self.detect_guru_chandal_dosha(chart):
            doshas.append(guru_chandal)

        # Check for cancellation conditions for each dosha
        doshas = [
            d for d in doshas
            if not self.check_dosha_cancellation(d, chart)
        ]

        return doshas

    def detect_mangal_dosha(self, chart: BirthChart) -> Optional[DetectedDosha]:
        """Detect Mangal Dosha (Mars affliction).

        Mangal Dosha occurs when Mars is present in critical houses
        (1, 2, 4, 7, 8, 12) from Lagna, Moon, or Venus. The severity
        depends on the house position.

        Severity levels:
        - Mild: Mars in 1st or 2nd house
        - Moderate: Mars in 4th or 12th house
        - Severe: Mars in 7th or 8th house

        Cancellation conditions include:
        - Mars in own sign (Aries, Scorpio)
        - Mars in exalted sign (Capricorn)
        - Mars aspected by Jupiter
        - Mars conjunct Jupiter

        Args:
            chart: Birth chart to analyze

        Returns:
            DetectedDosha object if dosha is present, None otherwise
        """
        mars_pos = chart.planets[Planet.MARS]

        # Check Mars position from three viewpoints
        dosha_from_lagna = self._check_mars_in_critical_houses(
            mars_pos, chart.lagna_rashi, "Lagna"
        )

        dosha_from_moon = self._check_mars_in_critical_houses(
            mars_pos, chart.moon_rashi, "Moon"
        )

        # Get Venus position for third viewpoint
        venus_pos = chart.planets[Planet.VENUS]
        dosha_from_venus = self._check_mars_in_critical_houses(
            mars_pos, venus_pos.rashi, "Venus"
        )

        # Determine if dosha is present from any viewpoint
        all_checks = [
            (dosha_from_lagna, "Lagna"),
            (dosha_from_moon, "Moon"),
            (dosha_from_venus, "Venus")
        ]

        dosha_present_checks = [
            (house, viewpoint) for house, viewpoint in all_checks if house
        ]

        if not dosha_present_checks:
            return None

        # Use the most severe house position
        most_severe_house = max([h for h, _ in dosha_present_checks])
        severe_houses = [7, 8]
        moderate_houses = [4, 12]

        if most_severe_house in severe_houses:
            severity = "severe"
            severity_score = 3
        elif most_severe_house in moderate_houses:
            severity = "moderate"
            severity_score = 2
        else:
            severity = "mild"
            severity_score = 1

        # Determine description with viewpoint information
        viewpoints = [vp for _, vp in dosha_present_checks]
        from_text = ", ".join(viewpoints)

        description = (
            f"Mars is in {most_severe_house}th house (critical for Mangal Dosha) "
            f"as seen from {from_text}. "
        )

        # Add mitigation if present
        if mars_pos.rashi in self.MARS_OWN_SIGNS:
            description += "Mars is in its own sign, partially mitigating the dosha. "
        if mars_pos.rashi == self.MARS_EXALTED_SIGN:
            description += "Mars is in exalted sign, reducing dosha intensity. "

        return DetectedDosha(
            dosha_id="mangal_dosha",
            name="Mangal Dosha",
            is_present=True,
            severity=severity,
            involved_planets=[Planet.MARS],
            description=description.strip(),
            remedies=[
                "Chant Mangala Stotram daily",
                "Donate red items and copper articles",
                "Wear coral gemstone on Tuesday",
                "Perform Mangal puja or Hanuman worship",
                "Recite Hanuman Chalisa",
                "Fast on Tuesdays"
            ]
        )

    def detect_kaal_sarp_dosha(self, chart: BirthChart) -> Optional[DetectedDosha]:
        """Detect Kaal Sarp Dosha (Rahu-Ketu axis affliction).

        Kaal Sarp Dosha occurs when all planets (excluding Rahu and Ketu)
        are positioned between the Rahu-Ketu axis. This creates a powerful
        karmic blockage. The specific type depends on Rahu's house position.

        Twelve types:
        1. Anant (1st) - Spiritual obstacles
        2. Kulik (2nd) - Financial constraints
        3. Vasuki (3rd) - Relationship challenges
        4. Shankpal (4th) - Domestic instability
        5. Padma (5th) - Child-related issues
        6. Mahapadma (6th) - Health challenges
        7. Takshak (7th) - Marriage/partnership troubles
        8. Karkotat (8th) - Sudden losses
        9. Shankhchud (9th) - Spiritual confusion
        10. Ghatak (10th) - Career obstacles
        11. Vishdhar (11th) - Friendship betrayal
        12. Sheshnag (12th) - Spiritual stagnation

        Args:
            chart: Birth chart to analyze

        Returns:
            DetectedDosha object if dosha is present, None otherwise
        """
        rahu_pos = chart.planets[Planet.RAHU]
        ketu_pos = chart.planets[Planet.KETU]

        # Get all planet positions (excluding Rahu/Ketu)
        planet_positions = {
            p: chart.planets[p]
            for p in [Planet.SUN, Planet.MOON, Planet.MARS,
                     Planet.MERCURY, Planet.JUPITER, Planet.VENUS, Planet.SATURN]
        }

        # Check if all planets are between Rahu and Ketu
        all_between_forward = self._check_planets_between_axis(
            planet_positions, rahu_pos.longitude, ketu_pos.longitude
        )

        # Also check reverse direction
        all_between_reverse = self._check_planets_between_axis(
            planet_positions, ketu_pos.longitude, rahu_pos.longitude
        )

        if not (all_between_forward or all_between_reverse):
            return None

        # Determine dosha type based on Rahu's house
        rahu_house = rahu_pos.house
        dosha_type = self.KAAL_SARP_TYPES.get(rahu_house, "Unknown")

        # Build description with type-specific effects
        type_effects = {
            "Anant": "obstructing spiritual progress and inner peace",
            "Kulik": "causing financial constraints and business obstacles",
            "Vasuki": "creating relationship and communication challenges",
            "Shankpal": "destabilizing home and family matters",
            "Padma": "affecting children and progeny",
            "Mahapadma": "manifesting health issues and physical ailments",
            "Takshak": "causing marriage and partnership difficulties",
            "Karkotat": "bringing sudden losses and hidden dangers",
            "Shankhchud": "creating spiritual confusion and wrong guidance",
            "Ghatak": "obstructing career growth and public reputation",
            "Vishdhar": "causing betrayal by friends and associates",
            "Sheshnag": "leading to spiritual stagnation and isolation"
        }

        effect_text = type_effects.get(dosha_type, "creating general karmic obstacles")

        description = (
            f"{dosha_type} Kaal Sarp Dosha with Rahu in {rahu_house}th house, "
            f"{effect_text}. "
            f"All seven planets are hemmed between Rahu-Ketu axis, "
            f"indicating powerful karmic constraints."
        )

        return DetectedDosha(
            dosha_id=f"kaal_sarp_{dosha_type.lower().replace(' ', '_')}",
            name=f"Kaal Sarp Dosha ({dosha_type})",
            is_present=True,
            severity="severe",
            involved_planets=[Planet.RAHU, Planet.KETU],
            description=description,
            remedies=[
                "Perform Kaal Sarp Dosha puja/homa",
                "Rahu-Ketu shanti rituals",
                "Visit Trimbakeshwar temple (Nasik)",
                "Offer prayers at Kali temples",
                "Wear Blue Sapphire (if Rahu) or Hessonite (if Ketu)",
                "Chant Rahu and Ketu mantras",
                "Perform Rudra Abhishek",
                "Donate black items and iron"
            ]
        )

    def detect_pitra_dosha(self, chart: BirthChart) -> Optional[DetectedDosha]:
        """Detect Pitra Dosha (ancestral karma affliction).

        Pitra Dosha indicates unresolved ancestral karma and debt to ancestors.
        It manifests when:
        - Sun is afflicted by Rahu/Ketu (especially conjunction)
        - Sun is in dharma houses (1st, 5th, 9th) with affliction
        - 9th house lord (Pitrukaraka) is severely afflicted

        Typical manifestations:
        - Health issues, especially for male children
        - Financial difficulties without clear reason
        - Delays in marriage and progeny
        - Family conflicts and emotional pain
        - Repeated setbacks despite efforts

        Args:
            chart: Birth chart to analyze

        Returns:
            DetectedDosha object if dosha is present, None otherwise
        """
        sun_pos = chart.planets[Planet.SUN]
        rahu_pos = chart.planets[Planet.RAHU]
        ketu_pos = chart.planets[Planet.KETU]

        # Primary condition: Sun-Rahu/Ketu conjunction in dharma houses
        sun_rahu_conj = self._are_planets_conjunct(sun_pos, rahu_pos)
        sun_ketu_conj = self._are_planets_conjunct(sun_pos, ketu_pos)

        # Dharma houses are 1, 5, 9
        sun_in_dharma = sun_pos.house in [1, 5, 9]

        # Secondary condition: Sun in dharma house with Rahu/Ketu aspect
        sun_rahu_aspect = self._are_planets_aspecting(
            sun_pos, rahu_pos, self.OPPOSITION_ORB
        )
        sun_ketu_aspect = self._are_planets_aspecting(
            sun_pos, ketu_pos, self.OPPOSITION_ORB
        )

        # Determine if Pitra Dosha is present
        if not ((sun_rahu_conj or sun_ketu_conj) and sun_in_dharma):
            if not (sun_in_dharma and (sun_rahu_aspect or sun_ketu_aspect)):
                return None

        # Determine severity based on house
        if sun_pos.house == 1:
            severity = "severe"
        elif sun_pos.house == 9:
            severity = "moderate"
        else:
            severity = "mild"

        # Build description
        affliction_type = "Rahu" if sun_rahu_conj else ("Ketu" if sun_ketu_conj else "node aspect")
        description = (
            f"Sun is afflicted by {affliction_type} in the {sun_pos.house}th house (dharma house). "
            f"This indicates ancestral karma and unresolved debt to forefathers. "
            f"Manifestations may include health issues, financial setbacks, "
            f"and delays in progeny. Male progeny may be particularly affected."
        )

        return DetectedDosha(
            dosha_id="pitra_dosha",
            name="Pitra Dosha",
            is_present=True,
            severity=severity,
            involved_planets=[Planet.SUN, Planet.RAHU if sun_rahu_conj or sun_rahu_aspect else Planet.KETU],
            description=description,
            remedies=[
                "Perform Pitra Tarpan rituals",
                "Offer water and food to crows (ancestors)",
                "Visit pilgrimage sites and offer prayers",
                "Perform Shraddha (ancestral rites) regularly",
                "Chant Surya Namaskar and Sun mantras",
                "Donate to charitable causes",
                "Serve elderly people and parents with devotion",
                "Perform Rudrabhishek to appease ancestral spirits"
            ]
        )

    def detect_grahan_dosha(self, chart: BirthChart) -> Optional[DetectedDosha]:
        """Detect Grahan Dosha (eclipse shadow affliction).

        Grahan Dosha occurs when:
        - Sun is conjunct with Rahu or Ketu (Surya Grahan)
        - Moon is conjunct with Rahu or Ketu (Chandra Grahan)

        This creates an eclipse-like effect that obscures the planet's
        benefic nature. Manifestations depend on the affected luminary.

        Surya Grahan effects:
        - Career obstacles and lack of recognition
        - Health issues and low vitality
        - Lack of courage and confidence
        - Father's influence on life disrupted

        Chandra Grahan effects:
        - Mental disturbance and emotional instability
        - Loss of comfort and maternal care
        - Sleep disturbances and psychological issues
        - Female reproductive issues possible

        Args:
            chart: Birth chart to analyze

        Returns:
            DetectedDosha object if dosha is present, None otherwise
        """
        sun_pos = chart.planets[Planet.SUN]
        moon_pos = chart.planets[Planet.MOON]
        rahu_pos = chart.planets[Planet.RAHU]
        ketu_pos = chart.planets[Planet.KETU]

        # Check Sun-Rahu/Ketu conjunction
        sun_rahu_conj = self._are_planets_conjunct(sun_pos, rahu_pos)
        sun_ketu_conj = self._are_planets_conjunct(sun_pos, ketu_pos)

        if sun_rahu_conj or sun_ketu_conj:
            node_name = "Rahu" if sun_rahu_conj else "Ketu"
            return DetectedDosha(
                dosha_id="surya_grahan_dosha",
                name="Surya Grahan Dosha",
                is_present=True,
                severity="moderate",
                involved_planets=[Planet.SUN, Planet.RAHU if sun_rahu_conj else Planet.KETU],
                description=(
                    f"Sun is conjunct with {node_name}, creating an eclipse-like obscuration. "
                    f"This affects career, authority, and vital life force. "
                    f"May cause lack of recognition, health issues, and reduced confidence."
                ),
                remedies=[
                    "Chant Surya Namaskar daily",
                    "Perform Sun puja and rituals",
                    "Wear ruby gemstone",
                    "Meditate on Sun during sunrise",
                    "Fast on Sundays",
                    "Donate red items and wheat"
                ]
            )

        # Check Moon-Rahu/Ketu conjunction
        moon_rahu_conj = self._are_planets_conjunct(moon_pos, rahu_pos)
        moon_ketu_conj = self._are_planets_conjunct(moon_pos, ketu_pos)

        if moon_rahu_conj or moon_ketu_conj:
            node_name = "Rahu" if moon_rahu_conj else "Ketu"
            return DetectedDosha(
                dosha_id="chandra_grahan_dosha",
                name="Chandra Grahan Dosha",
                is_present=True,
                severity="moderate",
                involved_planets=[Planet.MOON, Planet.RAHU if moon_rahu_conj else Planet.KETU],
                description=(
                    f"Moon is conjunct with {node_name}, creating mental obscuration. "
                    f"This affects emotional stability, peace of mind, and comfort. "
                    f"May cause anxiety, sleep disturbances, and relationship challenges."
                ),
                remedies=[
                    "Chant Moon mantras and Soma mantras",
                    "Perform Moon puja",
                    "Wear pearl or moonstone",
                    "Meditate during full moon",
                    "Fast on Mondays",
                    "Donate white items and milk",
                    "Practice calming pranayama"
                ]
            )

        return None

    def detect_guru_chandal_dosha(self, chart: BirthChart) -> Optional[DetectedDosha]:
        """Detect Guru Chandal Dosha (Jupiter-Rahu affliction).

        Guru Chandal Dosha occurs when Jupiter and Rahu are in conjunction
        or opposition. Despite Jupiter's benevolence, Rahu's shadowy nature
        creates an affliction that manifests as:
        - Spiritual confusion and misguided beliefs
        - Inability to benefit from educational opportunities
        - Deception in financial and legal matters
        - Loss of dignity and reputation
        - Attraction to negative influences
        - Problems with gurus and authority figures

        Mild version: Jupiter and Rahu in same house
        Moderate: Jupiter and Rahu in opposition (7 houses apart)
        Can be cancelled if Jupiter is strong and in its own/exalted sign

        Args:
            chart: Birth chart to analyze

        Returns:
            DetectedDosha object if dosha is present, None otherwise
        """
        jupiter_pos = chart.planets[Planet.JUPITER]
        rahu_pos = chart.planets[Planet.RAHU]

        # Check conjunction (same rashi)
        jupiter_rahu_conj = self._are_planets_conjunct(jupiter_pos, rahu_pos)

        # Check opposition (opposite rashis or 7 houses apart)
        jupiter_rahu_opp = self._are_planets_in_opposition(jupiter_pos, rahu_pos)

        if not (jupiter_rahu_conj or jupiter_rahu_opp):
            return None

        # Determine severity
        if jupiter_rahu_conj:
            severity = "moderate"
            aspect_type = "conjunction"
        else:
            severity = "mild"
            aspect_type = "opposition"

        # Check if Jupiter is strong (own/exalted sign)
        jupiter_strong = (
            jupiter_pos.rashi in [Rashi.SAGITTARIUS, Rashi.PISCES] or
            jupiter_pos.rashi == Rashi.CANCER
        )

        description = (
            f"Jupiter and Rahu are in {aspect_type}, creating Guru Chandal Dosha. "
            f"This affects wisdom, spiritual growth, and correct understanding. "
            f"May cause deception, loss of direction, and problems with mentors. "
        )

        if jupiter_strong:
            description += "However, Jupiter's strong position provides some mitigation."

        return DetectedDosha(
            dosha_id="guru_chandal_dosha",
            name="Guru Chandal Dosha",
            is_present=True,
            severity=severity,
            involved_planets=[Planet.JUPITER, Planet.RAHU],
            description=description.strip(),
            remedies=[
                "Chant Jupiter mantras (Brihaspati Mantra)",
                "Perform Jupiter puja on Thursdays",
                "Wear yellow sapphire gemstone",
                "Donate yellow items and turmeric",
                "Fast on Thursdays",
                "Seek guidance from authentic gurus",
                "Study spiritual texts and philosophy",
                "Serve a true spiritual master"
            ]
        )

    def check_dosha_cancellation(self, dosha: DetectedDosha, chart: BirthChart) -> bool:
        """Check if a detected dosha has cancellation conditions.

        Doshas can be nullified or significantly mitigated by various
        astrological conditions. This method checks all relevant
        cancellation conditions for the detected dosha.

        Common cancellation conditions:
        - Afflicting planet in own or exalted sign
        - Afflicting planet aspected by benefics (Jupiter, Venus)
        - Benefic yoga overriding the dosha
        - Strong planet neutralizing affliction

        Args:
            dosha: The detected dosha to check
            chart: The birth chart containing planetary positions

        Returns:
            True if dosha is cancelled, False otherwise
        """
        dosha_id = dosha.dosha_id

        # Mangal Dosha cancellations
        if dosha_id == "mangal_dosha":
            mars_pos = chart.planets[Planet.MARS]
            jupiter_pos = chart.planets[Planet.JUPITER]

            # Mars in own sign
            if mars_pos.rashi in self.MARS_OWN_SIGNS:
                return True

            # Mars in exalted sign
            if mars_pos.rashi == self.MARS_EXALTED_SIGN:
                return True

            # Mars aspected by or conjunct Jupiter
            if self._are_planets_conjunct(mars_pos, jupiter_pos):
                return True

            if self._are_planets_aspecting(mars_pos, jupiter_pos, self.SQUARE_ORB):
                return True

            # Mars in 7th with a benefic in 7th (strong marriage combinations)
            if mars_pos.house == 7:
                venus_pos = chart.planets[Planet.VENUS]
                if venus_pos.house == 7 and self._are_planets_conjunct(mars_pos, venus_pos):
                    return True

        # Kaal Sarp Dosha cancellations
        if "kaal_sarp" in dosha_id:
            rahu_pos = chart.planets[Planet.RAHU]
            ketu_pos = chart.planets[Planet.KETU]
            jupiter_pos = chart.planets[Planet.JUPITER]

            # Rahu in 12th house (gate of liberation)
            if rahu_pos.house == 12:
                return True

            # Ketu in 6th house (enemy house)
            if ketu_pos.house == 6:
                return True

            # Jupiter conjunct or aspecting Rahu
            if self._are_planets_conjunct(jupiter_pos, rahu_pos):
                return True

        # Pitra Dosha cancellations
        if dosha_id == "pitra_dosha":
            sun_pos = chart.planets[Planet.SUN]
            jupiter_pos = chart.planets[Planet.JUPITER]

            # Sun aspected by Jupiter
            if self._are_planets_aspecting(sun_pos, jupiter_pos, self.TRINE_ORB):
                return True

            # Strong Sun in own sign
            if sun_pos.rashi == Rashi.LEO:
                return True

        # Grahan Dosha cancellations
        if "grahan" in dosha_id:
            if "surya" in dosha_id:
                sun_pos = chart.planets[Planet.SUN]
                # Sun in own sign (Leo) mitigates
                if sun_pos.rashi == Rashi.LEO:
                    return True
            elif "chandra" in dosha_id:
                moon_pos = chart.planets[Planet.MOON]
                # Moon in own sign (Cancer) mitigates
                if moon_pos.rashi == Rashi.CANCER:
                    return True

        # Guru Chandal Dosha cancellations
        if dosha_id == "guru_chandal_dosha":
            jupiter_pos = chart.planets[Planet.JUPITER]

            # Jupiter in own sign
            if jupiter_pos.rashi in [Rashi.SAGITTARIUS, Rashi.PISCES]:
                return True

            # Jupiter in exalted sign (Cancer)
            if jupiter_pos.rashi == Rashi.CANCER:
                return True

        return False

    # Helper methods

    def _check_mars_in_critical_houses(
        self,
        mars_pos: PlanetPosition,
        reference_rashi: Rashi,
        viewpoint_name: str
    ) -> Optional[int]:
        """Check if Mars is in critical houses from a given reference rashi.

        Args:
            mars_pos: Mars position in chart
            reference_rashi: Reference point (Lagna, Moon, or Venus rashi)
            viewpoint_name: Name of the viewpoint for reporting

        Returns:
            House number if Mars is in critical house, None otherwise
        """
        # Calculate house distance from reference rashi to Mars rashi
        house_distance = self._get_house_distance(
            reference_rashi, mars_pos.rashi
        )

        if house_distance in self.MANGAL_CRITICAL_HOUSES:
            return house_distance

        return None

    def _get_house_distance(self, from_rashi: Rashi, to_rashi: Rashi) -> int:
        """Calculate house distance between two rashis (1-12).

        Args:
            from_rashi: Starting rashi
            to_rashi: Ending rashi

        Returns:
            House distance (1-12) where 1 is same sign, 2 is next sign, etc.
        """
        rashi_order = [
            Rashi.ARIES, Rashi.TAURUS, Rashi.GEMINI, Rashi.CANCER,
            Rashi.LEO, Rashi.VIRGO, Rashi.LIBRA, Rashi.SCORPIO,
            Rashi.SAGITTARIUS, Rashi.CAPRICORN, Rashi.AQUARIUS, Rashi.PISCES
        ]

        from_idx = rashi_order.index(from_rashi)
        to_idx = rashi_order.index(to_rashi)

        # Calculate forward distance
        distance = (to_idx - from_idx) % 12
        return distance + 1 if distance >= 0 else distance + 13

    def _check_planets_between_axis(
        self,
        planets: Dict[Planet, PlanetPosition],
        axis_start: float,
        axis_end: float
    ) -> bool:
        """Check if all planets are between two axis points.

        Args:
            planets: Dictionary of planet positions
            axis_start: Starting longitude (Rahu or Ketu)
            axis_end: Ending longitude (Ketu or Rahu)

        Returns:
            True if all planets are between the axis, False otherwise
        """
        for planet_pos in planets.values():
            if not self._is_longitude_between(
                planet_pos.longitude, axis_start, axis_end
            ):
                return False
        return True

    def _is_longitude_between(
        self,
        longitude: float,
        start: float,
        end: float
    ) -> bool:
        """Check if a longitude is between start and end (considering zodiac wrap).

        Args:
            longitude: Longitude to check (0-360)
            start: Start longitude (0-360)
            end: End longitude (0-360)

        Returns:
            True if longitude is between start and end
        """
        # Normalize all values to 0-360
        longitude = longitude % 360
        start = start % 360
        end = end % 360

        if start < end:
            return start <= longitude <= end
        else:
            # Wraps around 0/360
            return longitude >= start or longitude <= end

    def _are_planets_conjunct(
        self,
        planet1: PlanetPosition,
        planet2: PlanetPosition,
        orb: float = None
    ) -> bool:
        """Check if two planets are in conjunction (same sign).

        Args:
            planet1: First planet position
            planet2: Second planet position
            orb: Angular orb in degrees (default: CONJUNCTION_ORB)

        Returns:
            True if planets are conjunct
        """
        if orb is None:
            orb = self.CONJUNCTION_ORB

        # Same rashi is conjunction
        if planet1.rashi == planet2.rashi:
            return True

        # Also check degree distance
        distance = abs(planet1.longitude - planet2.longitude)
        # Handle wrap-around at 360
        distance = min(distance, 360 - distance)

        return distance <= orb

    def _are_planets_aspecting(
        self,
        planet1: PlanetPosition,
        planet2: PlanetPosition,
        orb: float
    ) -> bool:
        """Check if two planets are aspecting each other (any major aspect).

        Args:
            planet1: First planet position
            planet2: Second planet position
            orb: Angular orb in degrees

        Returns:
            True if planets are aspecting
        """
        distance = abs(planet1.longitude - planet2.longitude)
        distance = min(distance, 360 - distance)

        # Check opposition (180°)
        return abs(distance - 180) <= orb

    def _are_planets_in_opposition(
        self,
        planet1: PlanetPosition,
        planet2: PlanetPosition,
        orb: float = None
    ) -> bool:
        """Check if two planets are in opposition (180° apart).

        Args:
            planet1: First planet position
            planet2: Second planet position
            orb: Angular orb in degrees (default: OPPOSITION_ORB)

        Returns:
            True if planets are in opposition
        """
        if orb is None:
            orb = self.OPPOSITION_ORB

        distance = abs(planet1.longitude - planet2.longitude)
        distance = min(distance, 360 - distance)

        return abs(distance - 180) <= orb
