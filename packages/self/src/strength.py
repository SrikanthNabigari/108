"""Planetary strength calculations module (Shadbala and Ashtakavarga).

This module implements comprehensive strength calculations for planets in Vedic astrology,
including Shadbala (six-fold strength) and Ashtakavarga (eight-fold classification).

References:
- BPHS (Brihat Parasara Hora Sastra) chapters 22-23
- Phaladeepa on planetary strengths
- Classical Jyotish texts
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from math import fabs

from packages.core.src.constants import Planet, Rashi
from packages.core.src.models import BirthChart, PlanetPosition


@dataclass
class ShadbalaComponents:
    """Components of Shadbala (six-fold strength)."""

    sthana_bala: float  # Positional strength (60)
    dig_bala: float  # Directional strength (60)
    kala_bala: float  # Temporal strength (60)
    chesta_bala: float  # Motional strength (60)
    naisargika_bala: float  # Natural strength (varies per planet)
    drik_bala: float  # Aspectual strength (60)

    @property
    def total(self) -> float:
        """Calculate total Shadbala."""
        return (
            self.sthana_bala
            + self.dig_bala
            + self.kala_bala
            + self.chesta_bala
            + self.naisargika_bala
            + self.drik_bala
        )


class StrengthCalculator:
    """Calculate planetary strengths using Shadbala and Ashtakavarga."""

    # Natural strength values (Naisargika Bala) in virupas (out of 60)
    NAISARGIKA_BALA = {
        Planet.SUN: 60.0,
        Planet.MOON: 51.43,
        Planet.MARS: 17.14,
        Planet.MERCURY: 25.71,
        Planet.JUPITER: 34.29,
        Planet.VENUS: 42.86,
        Planet.SATURN: 8.57,
        Planet.RAHU: 0.0,
        Planet.KETU: 0.0,
    }

    # Strong directions for Dig Bala (house number where planet gains strength)
    DIG_BALA_HOUSES = {
        Planet.JUPITER: 1,  # East (Lagna/1st house)
        Planet.MERCURY: 1,  # East
        Planet.SUN: 10,  # South (Midheaven/10th house)
        Planet.MARS: 10,  # South
        Planet.SATURN: 7,  # West (7th house)
        Planet.MOON: 4,  # North (4th house)
        Planet.VENUS: 4,  # North
        Planet.RAHU: 1,  # East (like Jupiter)
        Planet.KETU: 7,  # West (like Saturn)
    }

    # Exaltation points (rashi, degree within rashi)
    EXALTATION_POINTS = {
        Planet.SUN: (Rashi.ARIES, 10.0),
        Planet.MOON: (Rashi.TAURUS, 3.0),
        Planet.MARS: (Rashi.CAPRICORN, 28.0),
        Planet.MERCURY: (Rashi.VIRGO, 15.0),
        Planet.JUPITER: (Rashi.CANCER, 5.0),
        Planet.VENUS: (Rashi.PISCES, 27.0),
        Planet.SATURN: (Rashi.LIBRA, 20.0),
        Planet.RAHU: (Rashi.GEMINI, 20.0),  # Approximate
        Planet.KETU: (Rashi.SAGITTARIUS, 20.0),  # Approximate
    }

    # Debilitation points (opposite of exaltation)
    DEBILITATION_POINTS = {
        Planet.SUN: (Rashi.LIBRA, 10.0),
        Planet.MOON: (Rashi.SCORPIO, 3.0),
        Planet.MARS: (Rashi.CANCER, 28.0),
        Planet.MERCURY: (Rashi.PISCES, 15.0),
        Planet.JUPITER: (Rashi.CAPRICORN, 5.0),
        Planet.VENUS: (Rashi.VIRGO, 27.0),
        Planet.SATURN: (Rashi.ARIES, 20.0),
        Planet.RAHU: (Rashi.SAGITTARIUS, 20.0),
        Planet.KETU: (Rashi.GEMINI, 20.0),
    }

    # Own signs (Swarucha Rashi)
    OWN_SIGNS = {
        Planet.SUN: [Rashi.LEO],
        Planet.MOON: [Rashi.CANCER],
        Planet.MARS: [Rashi.ARIES, Rashi.SCORPIO],
        Planet.MERCURY: [Rashi.GEMINI, Rashi.VIRGO],
        Planet.JUPITER: [Rashi.SAGITTARIUS, Rashi.PISCES],
        Planet.VENUS: [Rashi.TAURUS, Rashi.LIBRA],
        Planet.SATURN: [Rashi.CAPRICORN, Rashi.AQUARIUS],
        Planet.RAHU: [Rashi.VIRGO],  # Exaltation sign
        Planet.KETU: [Rashi.PISCES],  # Exaltation sign
    }

    # Friendly planets by sign and ownership
    FRIENDS = {
        Planet.SUN: [Planet.MOON, Planet.MARS, Planet.JUPITER],
        Planet.MOON: [Planet.SUN, Planet.MERCURY],
        Planet.MARS: [Planet.SUN, Planet.MOON, Planet.JUPITER],
        Planet.MERCURY: [Planet.SUN, Planet.VENUS],
        Planet.JUPITER: [Planet.SUN, Planet.MOON, Planet.MARS],
        Planet.VENUS: [Planet.MERCURY, Planet.SATURN],
        Planet.SATURN: [Planet.MERCURY, Planet.VENUS],
        Planet.RAHU: [Planet.MERCURY, Planet.VENUS, Planet.SATURN],
        Planet.KETU: [Planet.MARS, Planet.SATURN, Planet.VENUS],
    }

    # Ashtakavarga points contributed by each planet to signs
    # Based on classical rules from BPHS
    ASHTAKAVARGA_POINTS = {
        Planet.SUN: {
            "sun": [1, 2, 4, 7, 8, 9, 10, 11],
            "moon": [3, 6, 10, 11],
            "mars": [1, 2, 4, 7, 8, 9, 10, 11],
            "mercury": [3, 5, 6, 9, 10, 11, 12],
            "jupiter": [5, 6, 9, 11],
            "venus": [6, 7, 12],
            "saturn": [1, 2, 4, 7, 8, 9, 10, 11],
            "lagna": [3, 4, 6, 10, 11, 12],
        },
        Planet.MOON: {
            "sun": [3, 6, 11],
            "moon": [3, 6, 10, 11],
            "mars": [6, 3, 11],
            "mercury": [4, 8, 12],
            "jupiter": [5, 9, 12],
            "venus": [4, 8, 12],
            "saturn": [2, 4, 8, 12],
            "lagna": [4, 8, 12],
        },
        Planet.MARS: {
            "sun": [1, 2, 4, 7, 8, 9, 10, 11],
            "moon": [3, 6, 10, 11],
            "mars": [1, 2, 4, 7, 8, 9, 10, 11],
            "mercury": [3, 5, 6, 9, 10, 11, 12],
            "jupiter": [5, 6, 9, 11],
            "venus": [6, 7, 12],
            "saturn": [1, 2, 4, 7, 8, 9, 10, 11],
            "lagna": [3, 6, 11],
        },
        Planet.MERCURY: {
            "sun": [3, 5, 6, 9, 10, 11, 12],
            "moon": [4, 8, 12],
            "mars": [3, 5, 6, 9, 10, 11, 12],
            "mercury": [3, 5, 6, 9, 10, 11, 12],
            "jupiter": [4, 5, 8, 9, 12],
            "venus": [3, 5, 6, 9, 10, 11, 12],
            "saturn": [3, 5, 6, 9, 10, 11, 12],
            "lagna": [3, 5, 6, 9, 10, 11, 12],
        },
        Planet.JUPITER: {
            "sun": [5, 6, 9, 11],
            "moon": [5, 9, 12],
            "mars": [5, 6, 9, 11],
            "mercury": [4, 5, 8, 9, 12],
            "jupiter": [5, 6, 9, 11],
            "venus": [5, 9, 12],
            "saturn": [5, 9, 12],
            "lagna": [5, 9, 12],
        },
        Planet.VENUS: {
            "sun": [6, 7, 12],
            "moon": [4, 8, 12],
            "mars": [6, 7, 12],
            "mercury": [3, 5, 6, 9, 10, 11, 12],
            "jupiter": [5, 9, 12],
            "venus": [6, 7, 12],
            "saturn": [3, 5, 6, 9, 10, 11, 12],
            "lagna": [1, 2, 12],
        },
        Planet.SATURN: {
            "sun": [1, 2, 4, 7, 8, 9, 10, 11],
            "moon": [2, 4, 8, 12],
            "mars": [1, 2, 4, 7, 8, 9, 10, 11],
            "mercury": [3, 5, 6, 9, 10, 11, 12],
            "jupiter": [5, 9, 12],
            "venus": [3, 5, 6, 9, 10, 11, 12],
            "saturn": [1, 2, 4, 7, 8, 9, 10, 11],
            "lagna": [3, 6, 11],
        },
    }

    def calculate_shadbala(self, planet: Planet, chart: BirthChart) -> Dict:
        """Calculate complete Shadbala (six-fold strength) for a planet.

        Args:
            planet: The planet to calculate strength for
            chart: The birth chart containing planetary positions

        Returns:
            Dictionary with total strength and component breakdown
        """
        if planet not in chart.planets:
            return {
                "planet": planet.value,
                "total": 0.0,
                "components": {},
                "note": "Planet not in chart",
            }

        pos = chart.planets[planet]

        # Calculate all six components
        sthana_bala = self._calc_sthana_bala(planet, pos, chart)
        dig_bala = self._calc_dig_bala(planet, pos, chart)
        kala_bala = self._calc_kala_bala(planet, pos, chart)
        chesta_bala = self._calc_chesta_bala(pos)
        naisargika_bala = self.NAISARGIKA_BALA.get(planet, 0.0)
        drik_bala = self._calc_drik_bala(planet, chart)

        components = {
            "sthana_bala": round(sthana_bala, 2),
            "dig_bala": round(dig_bala, 2),
            "kala_bala": round(kala_bala, 2),
            "chesta_bala": round(chesta_bala, 2),
            "naisargika_bala": round(naisargika_bala, 2),
            "drik_bala": round(drik_bala, 2),
        }

        total = sum(components.values())

        return {
            "planet": planet.value,
            "total": round(total, 2),
            "components": components,
            "is_strong": total > 300,  # Typical strength threshold
            "strength_rating": self._get_strength_rating(total),
        }

    def _calc_sthana_bala(self, planet: Planet, pos: PlanetPosition, chart: BirthChart) -> float:
        """Calculate Sthana Bala (positional strength).

        Components:
        - Uchcha Bala: Exaltation strength
        - Saptavargaja Bala: Strength in divisional charts
        - Ojhayugmarasyamsa Bala: Odd/even sign placement
        - Kendradi Bala: Angular house placement
        - Drekkana Bala: Decanate placement
        """
        uchcha_bala = self._calc_uchcha_bala(planet, pos.rashi, pos.rashi_degree)
        saptavargaja = self._calc_saptavargaja_bala(planet, pos.rashi)
        ojhayugma = self._calc_ojhayugma_bala(planet, pos.rashi)
        kendradi = self._calc_kendradi_bala(pos.house)
        drekkana = self._calc_drekkana_bala(pos.rashi_degree)

        return uchcha_bala + saptavargaja + ojhayugma + kendradi + drekkana

    def _calc_uchcha_bala(self, planet: Planet, rashi: Rashi, rashi_degree: float) -> float:
        """Calculate Uchcha Bala (exaltation strength, 0-60 virupas)."""
        if planet not in self.EXALTATION_POINTS:
            return 30.0  # Default for unknown planets

        exalt_rashi, exalt_deg = self.EXALTATION_POINTS[planet]

        # If planet is in exaltation sign, calculate strength based on degree
        if rashi == exalt_rashi:
            # Distance from exact exaltation degree
            distance = fabs(rashi_degree - exalt_deg)
            # Max strength at exaltation (60), zero at opposite point in sign
            strength = 60.0 * (1.0 - (distance / 30.0))
            return max(0.0, min(60.0, strength))

        # Check debilitation sign (opposite of exaltation)
        debil_rashi, debil_deg = self.DEBILITATION_POINTS.get(
            planet, (None, None)
        )
        if rashi == debil_rashi and debil_rashi is not None:
            distance = fabs(rashi_degree - debil_deg)
            strength = -60.0 * (1.0 - (distance / 30.0))
            return max(-60.0, min(0.0, strength))

        # Planet in neutral sign: moderate strength
        return 30.0

    def _calc_saptavargaja_bala(self, planet: Planet, rashi: Rashi) -> float:
        """Calculate Saptavargaja Bala (strength in 7 divisional charts).

        Based on planet's placement in D1, D2, D3, D7, D9, D12, D24 charts.
        """
        # Simplified calculation: 1 point for each benefic divisional placement
        # Full implementation requires divisional chart calculations
        base_strength = 10.0

        # If in own sign, add bonus
        if rashi in self.OWN_SIGNS.get(planet, []):
            base_strength += 5.0

        return base_strength

    def _calc_ojhayugma_bala(self, planet: Planet, rashi: Rashi) -> float:
        """Calculate Ojhayugmarasyamsa Bala (odd/even sign placement).

        Measures planet's strength in odd vs even signs.
        """
        # Rashi numbers: Aries=1, Taurus=2, ..., Pisces=12
        rashi_num = list(Rashi).index(rashi) + 1

        # Check if planet benefits from odd or even signs
        # This is generally beneficial for all planets in certain signs
        if rashi_num % 2 == 1:  # Odd sign
            return 7.5
        else:  # Even sign
            return 5.0

    def _calc_kendradi_bala(self, house: int) -> float:
        """Calculate Kendradi Bala (angular house placement).

        - Kendra (1, 4, 7, 10): 60 points
        - Panapara (2, 5, 8, 11): 30 points
        - Apoklima (3, 6, 9, 12): 15 points
        """
        if house in [1, 4, 7, 10]:
            return 60.0  # Kendra (angular)
        elif house in [2, 5, 8, 11]:
            return 30.0  # Panapara (succeedent)
        else:  # house in [3, 6, 9, 12]
            return 15.0  # Apoklima (cadent)

    def _calc_drekkana_bala(self, rashi_degree: float) -> float:
        """Calculate Drekkana Bala (decanate placement).

        Each sign is divided into 3 decanates (10° each).
        Different planets are strong in different decanates.
        """
        # Simplified: 10 points for favorable decanate placement
        return 10.0

    def _calc_dig_bala(self, planet: Planet, pos: PlanetPosition, chart: BirthChart) -> float:
        """Calculate Dig Bala (directional strength, 0-60 virupas).

        Each planet is strongest in a particular direction/house:
        - Jupiter & Mercury: East (1st/Lagna)
        - Sun & Mars: South (10th/MC)
        - Saturn: West (7th)
        - Moon & Venus: North (4th)

        Formula: 60 - (distance_from_strong_house * 60/180)
        """
        if planet not in self.DIG_BALA_HOUSES:
            return 0.0

        strong_house = self.DIG_BALA_HOUSES[planet]
        actual_house = pos.house

        # Calculate shortest distance between houses (considering circular nature)
        distance = abs(actual_house - strong_house)
        if distance > 6:
            distance = 12 - distance

        # Convert house distance to angle (each house = 30°)
        angle_distance = distance * 30.0

        # Calculate strength: max 60 at strong house, 0 at opposite (180° away)
        strength = 60.0 * (1.0 - (angle_distance / 180.0))
        return max(0.0, min(60.0, strength))

    def _calc_kala_bala(self, planet: Planet, pos: PlanetPosition, chart: BirthChart) -> float:
        """Calculate Kala Bala (temporal strength, 0-60 virupas).

        Components:
        - Nathonnatha Bala: Day/night strength
        - Paksha Bala: Lunar phase strength
        - Tribhaga Bala: Three parts of day/night
        - Varsha/Masa/Dina/Hora Bala: Year, month, day, hour lords
        - Ayana Bala: Declination strength
        - Yuddha Bala: Planetary war strength
        """
        # Simplified implementation of main temporal factors
        nathonnatha = self._calc_nathonnatha_bala(planet, chart)
        paksha = self._calc_paksha_bala(planet, chart)
        ayana = self._calc_ayana_bala(pos.latitude)

        return nathonnatha + paksha + ayana

    def _calc_nathonnatha_bala(self, planet: Planet, chart: BirthChart) -> float:
        """Day/night strength (Nathonnatha Bala).

        Sun and Mars are strong during day.
        Moon and Venus are strong during night.
        Mercury, Jupiter, Saturn get moderate strength.
        """
        # Check if birth is during day or night (simplified)
        # Full implementation requires sunrise/sunset times
        birth_hour = chart.birth_data.datetime_utc.hour

        if 6 <= birth_hour < 18:  # Day time
            if planet in [Planet.SUN, Planet.MARS]:
                return 15.0
            elif planet in [Planet.MOON, Planet.VENUS]:
                return 5.0
            else:
                return 10.0
        else:  # Night time
            if planet in [Planet.MOON, Planet.VENUS]:
                return 15.0
            elif planet in [Planet.SUN, Planet.MARS]:
                return 5.0
            else:
                return 10.0

    def _calc_paksha_bala(self, planet: Planet, chart: BirthChart) -> float:
        """Lunar phase strength (Paksha Bala).

        Moon is strong during waxing phase (Shukla Paksha).
        Other planets get variable strength based on Moon phase.
        """
        # Simplified: assign 10 points for moderate strength
        # Full implementation requires Tithi calculation
        return 10.0

    def _calc_ayana_bala(self, latitude: float) -> float:
        """Declination strength (Ayana Bala).

        Based on the declination of the planet.
        """
        # Simplified: latitude provides indirect declination measure
        return 5.0

    def _calc_chesta_bala(self, pos: PlanetPosition) -> float:
        """Calculate Chesta Bala (motional strength, 0-60 virupas).

        Based on planet's motion:
        - Retrograde: 60 (high strength)
        - Stationary (very slow): 45
        - Direct and slow: 30
        - Direct and fast: 15
        - Very fast: 0
        """
        if pos.is_retrograde:
            return 60.0  # Retrograde planets are strong

        # Motion strength based on speed (degrees per day)
        speed = pos.speed

        if speed < 0.5:
            return 45.0  # Nearly stationary
        elif speed < 1.0:
            return 30.0  # Slow
        elif speed < 1.5:
            return 15.0  # Moderate
        else:
            return 0.0  # Very fast (weak)

    def _calc_drik_bala(self, planet: Planet, chart: BirthChart) -> float:
        """Calculate Drik Bala (aspectual strength, 0-60 virupas).

        Strength from beneficial aspects and weakness from malefic aspects.
        """
        # Simplified calculation: 30 as baseline
        # Full implementation requires aspect calculations
        beneficial_aspects = 0
        malefic_aspects = 0

        # Count aspects from benefic planets (Jupiter, Venus, Mercury)
        benefics = [Planet.JUPITER, Planet.VENUS, Planet.MERCURY]
        # Count aspects from malefic planets (Sun, Mars, Saturn)
        malefics = [Planet.SUN, Planet.MARS, Planet.SATURN]

        for other_planet in chart.planets:
            if other_planet == planet:
                continue

            # Simplified: assume aspects occur (full calculation requires
            # angle analysis)
            if other_planet in benefics:
                beneficial_aspects += 5.0
            elif other_planet in malefics:
                malefic_aspects -= 5.0

        strength = 30.0 + beneficial_aspects + malefic_aspects
        return max(0.0, min(60.0, strength))

    def _get_strength_rating(self, total: float) -> str:
        """Get qualitative rating of planetary strength."""
        if total >= 360:
            return "very_strong"
        elif total >= 300:
            return "strong"
        elif total >= 200:
            return "moderate"
        elif total >= 100:
            return "weak"
        else:
            return "very_weak"

    def calculate_ashtakavarga(
        self, planet: Planet, chart: BirthChart
    ) -> List[int]:
        """Calculate Ashtakavarga for a planet (bindus in each sign).

        Ashtakavarga measures a planet's strength in each of the 12 signs
        based on beneficial placements from itself and other planets.

        Args:
            planet: The planet to calculate ashtakavarga for
            chart: The birth chart

        Returns:
            List of 12 integers (bindus for each sign, Aries=0 to Pisces=11)
        """
        bindus = [0] * 12

        if planet not in self.ASHTAKAVARGA_POINTS:
            return bindus

        planet_data = self.ASHTAKAVARGA_POINTS[planet]

        # Calculate contribution from each reference point
        references = {
            "sun": chart.planets[Planet.SUN].rashi,
            "moon": chart.planets[Planet.MOON].rashi,
            "mars": chart.planets[Planet.MARS].rashi,
            "mercury": chart.planets[Planet.MERCURY].rashi,
            "jupiter": chart.planets[Planet.JUPITER].rashi,
            "venus": chart.planets[Planet.VENUS].rashi,
            "saturn": chart.planets[Planet.SATURN].rashi,
            "lagna": chart.lagna_rashi,
        }

        # For each sign (0-11), count contributing references
        for sign_index in range(12):
            sign_num = sign_index + 1  # Signs are numbered 1-12

            for ref_name, ref_rashi in references.items():
                if ref_name in planet_data:
                    # Get the sign number of the reference
                    ref_sign_num = list(Rashi).index(ref_rashi) + 1

                    # Calculate distance from reference to target sign
                    distance = (sign_num - ref_sign_num) % 12
                    if distance == 0:
                        distance = 12

                    # Check if this distance is in the benefic list
                    if distance in planet_data[ref_name]:
                        bindus[sign_index] += 1

        return bindus

    def calculate_sarvashtakavarga(self, chart: BirthChart) -> List[int]:
        """Calculate Sarvashtakavarga (SAV) - total bindus for each sign.

        This is the sum of Ashtakavarga from all 7 planets.

        Args:
            chart: The birth chart

        Returns:
            List of 12 integers (total bindus per sign)
        """
        sav = [0] * 12

        for planet in [
            Planet.SUN,
            Planet.MOON,
            Planet.MARS,
            Planet.MERCURY,
            Planet.JUPITER,
            Planet.VENUS,
            Planet.SATURN,
        ]:
            planet_av = self.calculate_ashtakavarga(planet, chart)
            for i in range(12):
                sav[i] += planet_av[i]

        return sav

    def get_planet_dignity(self, planet: Planet, sign: Rashi) -> str:
        """Get the dignity (status) of a planet in a sign.

        Returns one of:
        - "exalted": Planet at highest strength
        - "own": Planet in its own sign
        - "friendly": Planet in a friend's sign
        - "neutral": Planet in a neutral sign
        - "enemy": Planet in an enemy's sign
        - "debilitated": Planet at lowest strength

        Args:
            planet: The planet
            sign: The rashi (zodiac sign)

        Returns:
            Dignity string
        """
        # Check exaltation
        if planet in self.EXALTATION_POINTS:
            exalt_rashi, _ = self.EXALTATION_POINTS[planet]
            if sign == exalt_rashi:
                return "exalted"

        # Check own sign
        if sign in self.OWN_SIGNS.get(planet, []):
            return "own"

        # Check debilitation
        if planet in self.DEBILITATION_POINTS:
            debil_rashi, _ = self.DEBILITATION_POINTS[planet]
            if sign == debil_rashi:
                return "debilitated"

        # Determine sign ruler (simplified)
        sign_rulers = {
            Rashi.ARIES: Planet.MARS,
            Rashi.TAURUS: Planet.VENUS,
            Rashi.GEMINI: Planet.MERCURY,
            Rashi.CANCER: Planet.MOON,
            Rashi.LEO: Planet.SUN,
            Rashi.VIRGO: Planet.MERCURY,
            Rashi.LIBRA: Planet.VENUS,
            Rashi.SCORPIO: Planet.MARS,
            Rashi.SAGITTARIUS: Planet.JUPITER,
            Rashi.CAPRICORN: Planet.SATURN,
            Rashi.AQUARIUS: Planet.SATURN,
            Rashi.PISCES: Planet.JUPITER,
        }

        sign_ruler = sign_rulers.get(sign)

        # Check if planet is friendly with sign ruler
        if sign_ruler and sign_ruler in self.FRIENDS.get(planet, []):
            return "friendly"

        # Check if planet is enemy with sign ruler
        if sign_ruler and sign_ruler not in self.FRIENDS.get(planet, []):
            # Check if they are mutual enemies
            if planet not in self.FRIENDS.get(sign_ruler, []):
                return "enemy"

        return "neutral"

    def get_all_planet_strengths(self, chart: BirthChart) -> Dict[str, Dict]:
        """Calculate Shadbala for all planets in the chart.

        Args:
            chart: The birth chart

        Returns:
            Dictionary mapping planet names to their strength calculations
        """
        strengths = {}

        for planet in [
            Planet.SUN,
            Planet.MOON,
            Planet.MARS,
            Planet.MERCURY,
            Planet.JUPITER,
            Planet.VENUS,
            Planet.SATURN,
            Planet.RAHU,
            Planet.KETU,
        ]:
            if planet in chart.planets:
                strengths[planet.value] = self.calculate_shadbala(
                    planet, chart
                )

        return strengths

    def analyze_strength_profile(self, chart: BirthChart) -> Dict:
        """Analyze overall strength profile of the chart.

        Returns a comprehensive analysis of planetary strengths.

        Args:
            chart: The birth chart

        Returns:
            Dictionary with strength analysis
        """
        all_strengths = self.get_all_planet_strengths(chart)

        # Find strongest and weakest planets
        planet_totals = {
            name: data["total"] for name, data in all_strengths.items()
        }
        strongest = max(
            planet_totals.items(), key=lambda x: x[1]
        )
        weakest = min(planet_totals.items(), key=lambda x: x[1])

        # Count planets in each strength category
        very_strong = sum(
            1
            for p in all_strengths.values()
            if p["is_strong"] and p["total"] >= 360
        )
        strong = sum(
            1
            for p in all_strengths.values()
            if p["is_strong"] and p["total"] < 360
        )
        weak = sum(
            1
            for p in all_strengths.values()
            if not p["is_strong"]
        )

        sav = self.calculate_sarvashtakavarga(chart)
        avg_sav = sum(sav) / 12 if sav else 0

        return {
            "all_strengths": all_strengths,
            "strongest_planet": strongest[0],
            "strongest_value": round(strongest[1], 2),
            "weakest_planet": weakest[0],
            "weakest_value": round(weakest[1], 2),
            "very_strong_count": very_strong,
            "strong_count": strong,
            "weak_count": weak,
            "sarvashtakavarga": sav,
            "average_sav": round(avg_sav, 2),
            "chart_strength_level": self._get_chart_strength_level(
                all_strengths
            ),
        }

    def _get_chart_strength_level(self, all_strengths: Dict) -> str:
        """Determine overall chart strength level."""
        totals = [p["total"] for p in all_strengths.values()]
        avg_total = sum(totals) / len(totals) if totals else 0

        if avg_total >= 300:
            return "excellent"
        elif avg_total >= 250:
            return "good"
        elif avg_total >= 200:
            return "moderate"
        elif avg_total >= 150:
            return "fair"
        else:
            return "weak"
