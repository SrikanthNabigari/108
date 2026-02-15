"""Yoga detection engine for 108 Vedic Astrology application.

This module provides comprehensive yoga detection capabilities, including:
- Pancha Mahapurusha Yogas (5 great-person yogas)
- Raja Yogas (royal yogas)
- Dhana Yogas (wealth yogas)
- Custom yoga detection from rules
- Strength calculation for detected yogas
"""

import contextlib
import json
import logging
import re
from pathlib import Path
from typing import Any, ClassVar

from packages.core.src import (
    BirthChart,
    DetectedYoga,
    Planet,
    Rashi,
    YogaCategory,
    calculate_aspect_houses,
    is_dusthana,
    is_kendra,
    is_trikona,
    is_upachaya,
)

logger = logging.getLogger(__name__)


class YogaDetector:
    """Engine for detecting Vedic astrology yogas in birth charts.

    This detector evaluates planetary combinations against predefined yoga rules
    to identify auspicious and inauspicious yoga formations in a birth chart.
    """

    # Planet rulership: which signs each planet rules
    PLANET_RULERSHIP: ClassVar[dict[Planet, list[Rashi]]] = {
        Planet.SUN: [Rashi.LEO],
        Planet.MOON: [Rashi.CANCER],
        Planet.MARS: [Rashi.ARIES, Rashi.SCORPIO],
        Planet.MERCURY: [Rashi.GEMINI, Rashi.VIRGO],
        Planet.JUPITER: [Rashi.SAGITTARIUS, Rashi.PISCES],
        Planet.VENUS: [Rashi.TAURUS, Rashi.LIBRA],
        Planet.SATURN: [Rashi.CAPRICORN, Rashi.AQUARIUS],
        Planet.RAHU: [Rashi.TAURUS],
        Planet.KETU: [Rashi.SCORPIO],
    }

    # Planet exaltation signs
    PLANET_EXALTATION: ClassVar[dict[Planet, Rashi]] = {
        Planet.SUN: Rashi.ARIES,
        Planet.MOON: Rashi.TAURUS,
        Planet.MARS: Rashi.CAPRICORN,
        Planet.MERCURY: Rashi.VIRGO,
        Planet.JUPITER: Rashi.CANCER,
        Planet.VENUS: Rashi.PISCES,
        Planet.SATURN: Rashi.LIBRA,
        Planet.RAHU: Rashi.TAURUS,
        Planet.KETU: Rashi.SCORPIO,
    }

    # Planet debilitation (opposite of exaltation)
    PLANET_DEBILITATION: ClassVar[dict[Planet, Rashi]] = {
        Planet.SUN: Rashi.LIBRA,
        Planet.MOON: Rashi.SCORPIO,
        Planet.MARS: Rashi.CANCER,
        Planet.MERCURY: Rashi.PISCES,
        Planet.JUPITER: Rashi.CAPRICORN,
        Planet.VENUS: Rashi.VIRGO,
        Planet.SATURN: Rashi.ARIES,
        Planet.RAHU: Rashi.SCORPIO,
        Planet.KETU: Rashi.TAURUS,
    }

    def __init__(self):
        """Initialize the yoga detector with rules from JSON configuration."""
        self.yoga_rules: dict[str, dict[str, Any]] = self._load_yoga_rules()
        self.condition_evaluators = {
            "in_kendra": self._eval_in_kendra,
            "in_trikona": self._eval_in_trikona,
            "in_dusthana": self._eval_in_dusthana,
            "in_upachaya": self._eval_in_upachaya,
            "in_own_sign": self._eval_in_own_sign,
            "in_exalted_sign": self._eval_in_exalted_sign,
            "in_own_or_exalted_sign": self._eval_in_own_or_exalted,
            "in_sign": self._eval_in_sign,
            "in_house": self._eval_in_house,
            "in_houses": self._eval_in_houses,
            "conjunct": self._eval_conjunct,
            "aspected_by": self._eval_aspected_by,
            "lord_in_house": self._eval_lord_in_house,
            "exchange": self._eval_exchange,
            "in_kendra_or_trikona": self._eval_in_kendra_or_trikona,
            "all_in_beneficial_houses": self._eval_all_in_beneficial,
            # Aspect-target conditions (planet_aspects_target)
            "saturn_aspects_moon": self._eval_planet_aspects_target,
            "saturn_aspects_lagna": self._eval_planet_aspects_target,
            "mars_aspects_moon": self._eval_planet_aspects_target,
            "mars_aspects_lagna": self._eval_planet_aspects_target,
            "jupiter_aspects_moon": self._eval_planet_aspects_target,
            "jupiter_aspects_lagna": self._eval_planet_aspects_target,
            "jupiter_aspects_5th": self._eval_planet_aspects_target,
            "jupiter_aspects_7th": self._eval_planet_aspects_target,
            "jupiter_aspects_9th": self._eval_planet_aspects_target,
        }

    def _load_yoga_rules(self) -> dict[str, dict[str, Any]]:
        """Load yoga detection rules from JSON configuration file.

        Returns:
            Dictionary of yoga rules keyed by yoga ID
        """
        rules_path = (
            Path(__file__).parent.parent.parent.parent / "knowledge" / "rules" / "yoga_master.json"
        )

        if not rules_path.exists():
            logger.warning(f"Yoga rules file not found at {rules_path}")
            return {}

        try:
            with rules_path.open() as f:
                data = json.load(f)
            return data.get("yoga_rules", {})
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Error loading yoga rules: {e}")
            return {}

    def detect_all_yogas(self, chart: BirthChart) -> list[DetectedYoga]:
        """Detect all yogas present in a birth chart.

        Args:
            chart: The birth chart to analyze

        Returns:
            List of detected yogas present in the chart
        """
        detected = []

        for yoga_id, rule in self.yoga_rules.items():
            try:
                result = self.detect_yoga(rule, chart)
                if result and result.is_present:
                    detected.append(result)
            except Exception as e:
                logger.error(f"Error detecting yoga {yoga_id}: {e}")
                continue

        return detected

    def detect_yoga(self, rule: dict[str, Any], chart: BirthChart) -> DetectedYoga | None:
        """Detect a single yoga based on its detection rule.

        Args:
            rule: Yoga detection rule dictionary
            chart: The birth chart to analyze

        Returns:
            DetectedYoga if yoga is present, None otherwise
        """
        detection = rule.get("detection", {})
        conditions = detection.get("conditions", [])
        all_required = detection.get("all_conditions_required", True)

        if not conditions:
            return None

        # Get the main planet from the rule
        rule_planet = detection.get("planet")

        # Evaluate all conditions
        results = []
        for condition in conditions:
            try:
                # If condition doesn't specify a planet, use the rule's planet
                if "planet" not in condition and rule_planet:
                    condition = {**condition, "planet": rule_planet}
                result = self._evaluate_condition(condition, chart)
                results.append(result)
            except Exception as e:
                logger.warning(f"Error evaluating condition: {e}")
                results.append(False)

        # Determine if yoga is present based on condition logic
        is_present = all(results) if all_required else any(results)

        if not is_present:
            return None

        # Calculate strength
        strength = self._calculate_strength(rule, chart)

        # Check cancellation conditions
        if self._is_yoga_cancelled(rule, chart):
            strength *= 0.5  # Halve strength if cancelled

        # Build involved planets list
        involved = []
        planet = detection.get("planet")
        planets = detection.get("planets", [])

        if planet:
            with contextlib.suppress(ValueError):
                involved.append(Planet(planet))

        for p in planets:
            if p not in ["ninth_lord", "tenth_lord", "fifth_lord"]:
                with contextlib.suppress(ValueError):
                    involved.append(Planet(p))

        return DetectedYoga(
            yoga_id=rule.get("id", "unknown"),
            name=rule.get("name", "Unknown Yoga"),
            category=YogaCategory(rule.get("category", "other")),
            is_present=True,
            strength=max(0.0, min(1.0, strength)),
            involved_planets=involved,
            description=rule.get("description", ""),
        )

    # Planet names for dynamic pattern matching (longest first for greedy match)
    _PLANET_NAMES: ClassVar[tuple[str, ...]] = (
        "mercury",
        "jupiter",
        "saturn",
        "venus",
        "mars",
        "moon",
        "rahu",
        "ketu",
        "sun",
    )
    # Sign names for dynamic matching
    _SIGN_NAMES: ClassVar[tuple[str, ...]] = (
        "sagittarius",
        "capricorn",
        "aquarius",
        "scorpio",
        "pisces",
        "gemini",
        "cancer",
        "taurus",
        "libra",
        "aries",
        "virgo",
        "leo",
    )
    # Natural benefics and malefics
    _BENEFICS: ClassVar[tuple[str, ...]] = ("jupiter", "venus", "mercury", "moon")
    _MALEFICS: ClassVar[tuple[str, ...]] = ("saturn", "mars", "rahu", "ketu", "sun")

    def _evaluate_condition(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Evaluate a single condition against the chart.

        Args:
            condition: Condition dictionary with type and parameters
            chart: Birth chart to evaluate against

        Returns:
            True if condition is satisfied, False otherwise
        """
        cond_type = condition.get("type")
        evaluator = self.condition_evaluators.get(cond_type)

        if evaluator:
            return evaluator(condition, chart)

        # Try dynamic pattern matching for unregistered condition types
        result = self._eval_dynamic(cond_type, condition, chart)
        if result is not None:
            return result

        logger.debug(f"Unhandled condition type: {cond_type}")
        return False

    # ── Dynamic pattern evaluators ──────────────────────────────────

    def _parse_planet(self, name: str) -> Planet | None:
        """Try to parse a planet name string into a Planet enum."""
        try:
            return Planet(name)
        except ValueError:
            return None

    def _parse_house_num(self, s: str) -> int | None:
        """Parse '1st', '2nd', '3rd', '4th', ... '12th' or bare digits."""
        cleaned = re.sub(r"(st|nd|rd|th)$", "", s)
        try:
            n = int(cleaned)
            return n if 1 <= n <= 12 else None
        except ValueError:
            return None

    def _planet_in_chart(self, planet_name: str, chart: BirthChart) -> Any | None:
        """Get PlanetPosition from chart or None."""
        p = self._parse_planet(planet_name)
        return chart.planets.get(p) if p else None

    def _eval_dynamic(
        self,
        cond_type: str | None,
        condition: dict[str, Any],
        chart: BirthChart,
    ) -> bool | None:
        """Try pattern-based evaluation for condition types not in the registry.

        Returns True/False if handled, None if not recognized.
        """
        if not cond_type:
            return None

        # ── 1. {planet}_in_own  (e.g. mercury_in_own) ──
        for pname in self._PLANET_NAMES:
            if cond_type == f"{pname}_in_own":
                pos = self._planet_in_chart(pname, chart)
                if not pos:
                    return False
                return self._is_in_own_sign(Planet(pname), pos.rashi)

        # ── 2. {p1}_{p2}_conjunction  (e.g. sun_moon_conjunction) ──
        if cond_type.endswith("_conjunction"):
            stem = cond_type[: -len("_conjunction")]
            for p1 in self._PLANET_NAMES:
                if stem.startswith(p1 + "_"):
                    p2_name = stem[len(p1) + 1 :]
                    p2 = self._parse_planet(p2_name)
                    if p2 is not None:
                        pos1 = self._planet_in_chart(p1, chart)
                        pos2 = chart.planets.get(p2)
                        if not pos1 or not pos2:
                            return False
                        return pos1.rashi == pos2.rashi
            # lords_conjunction — handled separately below
            if stem == "lords":
                return self._eval_lords_conjunction(condition, chart)

        # ── 3. lords_conjunction_or_aspect ──
        if cond_type == "lords_conjunction_or_aspect":
            return self._eval_lords_conjunction_or_aspect(condition, chart)

        # ── 4. {planet}_strong ──
        for pname in self._PLANET_NAMES:
            if cond_type == f"{pname}_strong":
                pos = self._planet_in_chart(pname, chart)
                if not pos:
                    return False
                p = Planet(pname)
                return (
                    self._is_in_own_sign(p, pos.rashi)
                    or self._is_in_exalted_sign(p, pos.rashi)
                    or is_kendra(pos.house)
                    or is_trikona(pos.house)
                )

        # ── 5. {planet}_exalted ──
        for pname in self._PLANET_NAMES:
            if cond_type == f"{pname}_exalted":
                pos = self._planet_in_chart(pname, chart)
                if not pos:
                    return False
                return self._is_in_exalted_sign(Planet(pname), pos.rashi)

        # ── 6. {planet}_debilitated ──
        for pname in self._PLANET_NAMES:
            if cond_type == f"{pname}_debilitated":
                pos = self._planet_in_chart(pname, chart)
                if not pos:
                    return False
                return self._is_in_debilitated_sign(Planet(pname), pos.rashi)

        # ── 7. {planet}_retrograde ──
        for pname in self._PLANET_NAMES:
            if cond_type == f"{pname}_retrograde":
                pos = self._planet_in_chart(pname, chart)
                if not pos:
                    return False
                return getattr(pos, "is_retrograde", False)

        # ── 8. {planet}_combust ──
        for pname in self._PLANET_NAMES:
            if cond_type == f"{pname}_combust":
                p = self._parse_planet(pname)
                if not p:
                    return False
                return self._is_combust(p, chart)

        # ── 9. {planet}_vargottama ──
        for pname in self._PLANET_NAMES:
            if cond_type == f"{pname}_vargottama":
                pos = self._planet_in_chart(pname, chart)
                if not pos:
                    return False
                # Vargottama: same sign in D1 and D9
                # D9 sign = (navamsha_pada - 1) maps to sign
                lon = pos.longitude
                d1_sign = int(lon / 30) % 12
                # Vargottama: D9 sign == D1 sign
                navamsha_num = int(lon / (30 / 9)) % 12
                return navamsha_num == d1_sign

        # ── 10. {planet}_in_own_sign (e.g. jupiter_in_own_sign) ──
        if cond_type.endswith("_in_own_sign"):
            pname = cond_type[: -len("_in_own_sign")]
            p = self._parse_planet(pname)
            if p:
                pos = chart.planets.get(p)
                if not pos:
                    return False
                return self._is_in_own_sign(p, pos.rashi)

        # ── 11. {planet}_in_own_or_exalted ──
        if cond_type.endswith("_in_own_or_exalted"):
            pname = cond_type[: -len("_in_own_or_exalted")]
            p = self._parse_planet(pname)
            if p:
                pos = chart.planets.get(p)
                if not pos:
                    return False
                return self._is_in_own_sign(p, pos.rashi) or self._is_in_exalted_sign(p, pos.rashi)

        # ── 12. {planet}_in_{sign} (e.g. moon_in_cancer, sun_in_leo) ──
        for pname in self._PLANET_NAMES:
            prefix = f"{pname}_in_"
            if cond_type.startswith(prefix):
                rest = cond_type[len(prefix) :]
                # Check if rest is a sign name
                for sign in self._SIGN_NAMES:
                    if rest == sign:
                        pos = self._planet_in_chart(pname, chart)
                        if not pos:
                            return False
                        return pos.rashi == Rashi(sign)

        # ── 13. {planet}_in_{N}th (e.g. jupiter_in_5th, moon_in_2nd) ──
        for pname in self._PLANET_NAMES:
            prefix = f"{pname}_in_"
            if cond_type.startswith(prefix):
                rest = cond_type[len(prefix) :]
                house_num = self._parse_house_num(rest)
                if house_num is not None:
                    pos = self._planet_in_chart(pname, chart)
                    if not pos:
                        return False
                    return pos.house == house_num

        # ── 14. {planet}_in_lagna (e.g. jupiter_in_lagna) ──
        for pname in self._PLANET_NAMES:
            if cond_type == f"{pname}_in_lagna":
                pos = self._planet_in_chart(pname, chart)
                if not pos:
                    return False
                return pos.house == 1

        # ── 15. {N}th_lord_strong (e.g. 9th_lord_strong) ──
        if cond_type.endswith("_lord_strong"):
            prefix = cond_type[: -len("_lord_strong")]
            house_num = self._parse_house_num(prefix)
            if house_num:
                lord = self._get_house_lord(house_num, chart)
                if not lord or lord not in chart.planets:
                    return False
                pos = chart.planets[lord]
                return (
                    self._is_in_own_sign(lord, pos.rashi)
                    or self._is_in_exalted_sign(lord, pos.rashi)
                    or is_kendra(pos.house)
                    or is_trikona(pos.house)
                )

        # ── 16. {N}th_lord_in_{M}th (e.g. 9th_lord_in_10th) ──
        if "_lord_in_" in cond_type:
            parts = cond_type.split("_lord_in_")
            if len(parts) == 2:
                src_house = self._parse_house_num(parts[0])
                tgt_house = self._parse_house_num(parts[1])
                if src_house and tgt_house:
                    lord = self._get_house_lord(src_house, chart)
                    if not lord or lord not in chart.planets:
                        return False
                    return chart.planets[lord].house == tgt_house

        # ── 17. {N}th_lord_afflicted ──
        if cond_type.endswith("_lord_afflicted"):
            prefix = cond_type[: -len("_lord_afflicted")]
            house_num = self._parse_house_num(prefix)
            if house_num:
                lord = self._get_house_lord(house_num, chart)
                if not lord or lord not in chart.planets:
                    return False
                pos = chart.planets[lord]
                return (
                    self._is_in_debilitated_sign(lord, pos.rashi)
                    or is_dusthana(pos.house)
                    or self._is_combust(lord, chart)
                )

        # ── 18. {N}th_lord_debilitated ──
        if cond_type.endswith("_lord_debilitated"):
            prefix = cond_type[: -len("_lord_debilitated")]
            house_num = self._parse_house_num(prefix)
            if house_num:
                lord = self._get_house_lord(house_num, chart)
                if not lord or lord not in chart.planets:
                    return False
                pos = chart.planets[lord]
                return self._is_in_debilitated_sign(lord, pos.rashi)

        # ── 19. {N}th_lord_in_dusthana ──
        if cond_type.endswith("_lord_in_dusthana"):
            prefix = cond_type[: -len("_lord_in_dusthana")]
            house_num = self._parse_house_num(prefix)
            if house_num:
                lord = self._get_house_lord(house_num, chart)
                if not lord or lord not in chart.planets:
                    return False
                return is_dusthana(chart.planets[lord].house)

        # ── 20. {N}th_lord_in_kendra ──
        if cond_type.endswith("_lord_in_kendra"):
            prefix = cond_type[: -len("_lord_in_kendra")]
            house_num = self._parse_house_num(prefix)
            if house_num:
                lord = self._get_house_lord(house_num, chart)
                if not lord or lord not in chart.planets:
                    return False
                return is_kendra(chart.planets[lord].house)

        # ── 21. lagna_lord_strong ──
        if cond_type == "lagna_lord_strong" or cond_type == "strong_lagna_lord":
            lord = self._get_house_lord(1, chart)
            if not lord or lord not in chart.planets:
                return False
            pos = chart.planets[lord]
            return (
                self._is_in_own_sign(lord, pos.rashi)
                or self._is_in_exalted_sign(lord, pos.rashi)
                or is_kendra(pos.house)
            )

        # ── 22. lagna_lord_in_kendra / lagna_lord_in_kendra_or_trikona ──
        if cond_type == "lagna_lord_in_kendra":
            lord = self._get_house_lord(1, chart)
            if not lord or lord not in chart.planets:
                return False
            return is_kendra(chart.planets[lord].house)

        if cond_type == "lagna_lord_in_kendra_or_trikona":
            lord = self._get_house_lord(1, chart)
            if not lord or lord not in chart.planets:
                return False
            h = chart.planets[lord].house
            return is_kendra(h) or is_trikona(h)

        # ── 23. lagna_lord_exalted / lagna_lord_debilitated ──
        if cond_type == "lagna_lord_exalted":
            lord = self._get_house_lord(1, chart)
            if not lord or lord not in chart.planets:
                return False
            return self._is_in_exalted_sign(lord, chart.planets[lord].rashi)

        if cond_type == "lagna_lord_debilitated":
            lord = self._get_house_lord(1, chart)
            if not lord or lord not in chart.planets:
                return False
            return self._is_in_debilitated_sign(lord, chart.planets[lord].rashi)

        # ── 24. lagna_lord_afflicted ──
        if cond_type == "lagna_lord_afflicted":
            lord = self._get_house_lord(1, chart)
            if not lord or lord not in chart.planets:
                return False
            pos = chart.planets[lord]
            return (
                self._is_in_debilitated_sign(lord, pos.rashi)
                or is_dusthana(pos.house)
                or self._is_combust(lord, chart)
            )

        # ── 25. {planet}_aspects_{target} — dynamic aspect checking ──
        if "_aspects_" in cond_type:
            return self._eval_planet_aspects_target(condition, chart)

        # ── 26. benefics/malefics in houses patterns ──
        if cond_type.startswith("benefics_in_") or cond_type.startswith("all_benefics_in_"):
            return self._eval_group_in_houses(self._BENEFICS, cond_type, chart)

        if cond_type.startswith("malefics_in_") or cond_type.startswith("all_malefics_in_"):
            return self._eval_group_in_houses(self._MALEFICS, cond_type, chart)

        # ── 27. {planet}_strong_in_{N}th ──
        for pname in self._PLANET_NAMES:
            prefix = f"{pname}_strong_in_"
            if cond_type.startswith(prefix):
                rest = cond_type[len(prefix) :]
                house_num = self._parse_house_num(rest)
                if rest == "kendra":
                    pos = self._planet_in_chart(pname, chart)
                    if not pos:
                        return False
                    p = Planet(pname)
                    return is_kendra(pos.house) and (
                        self._is_in_own_sign(p, pos.rashi) or self._is_in_exalted_sign(p, pos.rashi)
                    )
                if house_num is not None:
                    pos = self._planet_in_chart(pname, chart)
                    if not pos:
                        return False
                    p = Planet(pname)
                    return pos.house == house_num and (
                        self._is_in_own_sign(p, pos.rashi) or self._is_in_exalted_sign(p, pos.rashi)
                    )

        # ── 28. {planet}_not_combust ──
        for pname in self._PLANET_NAMES:
            if cond_type == f"{pname}_not_combust":
                p = self._parse_planet(pname)
                if not p:
                    return False
                return not self._is_combust(p, chart)

        # ── 29. aspected_by_benefic / aspected_by_malefic ──
        if cond_type == "aspected_by_benefic":
            return self._eval_aspected_by_group(condition, chart, self._BENEFICS)

        if cond_type == "aspected_by_malefic":
            return self._eval_aspected_by_group(condition, chart, self._MALEFICS)

        # ── 30. all_planets_in_{pattern} ──
        if cond_type.startswith("all_planets_in_"):
            return self._eval_all_planets_pattern(cond_type, condition, chart)

        # ── 31. day_birth / night_birth ──
        if cond_type == "day_birth":
            sun_pos = chart.planets.get(Planet.SUN)
            return sun_pos is not None and 1 <= sun_pos.house <= 6

        if cond_type == "night_birth":
            sun_pos = chart.planets.get(Planet.SUN)
            return sun_pos is not None and 7 <= sun_pos.house <= 12

        # ── 32. moon_weak / moon_afflicted ──
        if cond_type == "moon_weak":
            pos = chart.planets.get(Planet.MOON)
            if not pos:
                return False
            return self._is_in_debilitated_sign(Planet.MOON, pos.rashi) or is_dusthana(pos.house)

        if cond_type == "moon_afflicted":
            pos = chart.planets.get(Planet.MOON)
            if not pos:
                return False
            # Moon is afflicted if conjunct with malefics
            for mal in ("saturn", "mars", "rahu", "ketu"):
                mal_pos = self._planet_in_chart(mal, chart)
                if mal_pos and mal_pos.rashi == pos.rashi:
                    return True
            return False

        # Not recognized
        return None

    def _eval_lords_conjunction(
        self,
        condition: dict[str, Any],
        chart: BirthChart,
    ) -> bool:
        """Check if lords of specified houses are conjunct."""
        houses = condition.get("houses", [])
        if len(houses) < 2:
            return False
        lords = []
        for h in houses:
            lord = self._get_house_lord(h, chart)
            if not lord or lord not in chart.planets:
                return False
            lords.append(chart.planets[lord].rashi)
        return len(set(lords)) == 1

    def _eval_lords_conjunction_or_aspect(
        self,
        condition: dict[str, Any],
        chart: BirthChart,
    ) -> bool:
        """Check if lords of specified houses are conjunct or mutually aspecting."""
        houses = condition.get("houses", [])
        if len(houses) < 2:
            return False

        lord_planets: list[tuple[Planet, Any]] = []
        for h in houses:
            lord = self._get_house_lord(h, chart)
            if not lord or lord not in chart.planets:
                return False
            lord_planets.append((lord, chart.planets[lord]))

        # Check conjunction (same sign)
        rashis = [pos.rashi for _, pos in lord_planets]
        if len(set(rashis)) == 1:
            return True

        # Check mutual aspect between any pair
        for i in range(len(lord_planets)):
            for j in range(i + 1, len(lord_planets)):
                p1, pos1 = lord_planets[i]
                p2, pos2 = lord_planets[j]
                asp1 = calculate_aspect_houses(p1, pos1.house)
                if pos2.house in asp1:
                    return True
                asp2 = calculate_aspect_houses(p2, pos2.house)
                if pos1.house in asp2:
                    return True
        return False

    def _eval_group_in_houses(
        self,
        group: tuple[str, ...],
        cond_type: str,
        chart: BirthChart,
    ) -> bool:
        """Check if benefics/malefics are in specified house positions."""
        # Extract house numbers from the condition name
        # e.g. "benefics_in_1_4_7" → [1, 4, 7]
        # e.g. "all_benefics_in_kendras" → kendra houses
        if "kendras" in cond_type or "kendra" in cond_type:
            target_houses = {1, 4, 7, 10}
        elif "trikona" in cond_type:
            target_houses = {1, 5, 9}
        elif "upachaya" in cond_type:
            target_houses = {3, 6, 10, 11}
        else:
            # Parse numbers from the string
            parts = cond_type.split("_in_")[-1].split("_")
            target_houses = set()
            for part in parts:
                try:
                    target_houses.add(int(part))
                except ValueError:
                    continue

        if not target_houses:
            return False

        # Check if at least one planet from the group is in the target houses
        for pname in group:
            pos = self._planet_in_chart(pname, chart)
            if pos and pos.house in target_houses:
                return True
        return False

    def _eval_aspected_by_group(
        self,
        condition: dict[str, Any],
        chart: BirthChart,
        group: tuple[str, ...],
    ) -> bool:
        """Check if the target planet is aspected by any planet in the group."""
        target_name = condition.get("planet")
        if not target_name:
            return False
        target = self._parse_planet(target_name)
        if not target or target not in chart.planets:
            return False
        target_house = chart.planets[target].house

        for pname in group:
            p = self._parse_planet(pname)
            if not p or p not in chart.planets or p == target:
                continue
            aspects = calculate_aspect_houses(p, chart.planets[p].house)
            if target_house in aspects:
                return True
        return False

    def _eval_all_planets_pattern(
        self,
        cond_type: str,
        _condition: dict[str, Any],
        chart: BirthChart,
    ) -> bool:
        """Evaluate all_planets_in_{pattern} conditions."""
        suffix = cond_type[len("all_planets_in_") :]

        # Collect all planet houses
        houses = []
        for p in Planet:
            pos = chart.planets.get(p)
            if pos:
                houses.append(pos.house)

        if not houses:
            return False

        if suffix == "kendras" or suffix == "kendras_only":
            return all(is_kendra(h) for h in houses)
        if suffix == "kendra_or_trikona":
            return all(is_kendra(h) or is_trikona(h) for h in houses)
        if suffix == "trikonas":
            return all(is_trikona(h) for h in houses)
        if suffix == "one_kendra":
            kendra = {1, 4, 7, 10}
            return any(all(h in kendra for h in houses) for _ in [None])
        if suffix == "different_signs":
            rashis = set()
            for p in Planet:
                pos = chart.planets.get(p)
                if pos:
                    rashis.add(pos.rashi)
            return len(rashis) == len(houses)

        # Consecutive houses patterns: "seven_consecutive_houses", etc.
        if "consecutive" in suffix:
            house_set = set(houses)
            # Try all starting positions
            for start in range(1, 13):
                for span in range(3, 10):
                    window = {((start + i - 1) % 12) + 1 for i in range(span)}
                    if house_set.issubset(window):
                        return True
            return False

        # Houses pattern: "1_5_9", "1_and_7_only", etc.
        # Extract numbers
        parts = suffix.replace("and_", "").replace("only", "").replace("_to_", "_").split("_")
        target_houses = set()
        for part in parts:
            try:
                target_houses.add(int(part))
            except ValueError:
                continue

        if target_houses:
            return all(h in target_houses for h in houses)

        return False

    def _calculate_strength(self, rule: dict[str, Any], chart: BirthChart) -> float:
        """Calculate yoga strength based on strength factors.

        Args:
            rule: Yoga rule
            chart: Birth chart

        Returns:
            Strength value between 0.0 and 1.0
        """
        strength = 0.7  # Base strength

        factors = rule.get("strength_factors", [])
        for factor in factors:
            strength += self._evaluate_strength_factor(factor, chart)

        return min(1.0, max(0.0, strength))

    def _evaluate_strength_factor(self, factor: dict[str, Any], chart: BirthChart) -> float:
        """Evaluate a strength factor and return boost value.

        Args:
            factor: Strength factor specification
            chart: Birth chart

        Returns:
            Strength boost value (usually 0.0-0.25)
        """
        factor_type = factor.get("type")
        boost = factor.get("strength_boost", 0.1)

        if factor_type == "planet_in_own_sign":
            planet_name = factor.get("planet")
            try:
                planet = Planet(planet_name)
                if planet in chart.planets:
                    pos = chart.planets[planet]
                    if self._is_in_own_sign(planet, pos.rashi):
                        return boost
            except (ValueError, AttributeError):
                pass

        elif factor_type == "planet_in_exalted_sign":
            planet_name = factor.get("planet")
            try:
                planet = Planet(planet_name)
                if planet in chart.planets:
                    pos = chart.planets[planet]
                    if self._is_in_exalted_sign(planet, pos.rashi):
                        return boost
            except (ValueError, AttributeError):
                pass

        elif factor_type == "mutual_aspect":
            planets = factor.get("planets", [])
            if len(planets) >= 2 and self._have_mutual_aspect(planets[0], planets[1], chart):
                return boost

        elif factor_type == "multiple_planets_in_houses":
            count = self._count_planets_in_houses(
                factor.get("planets", []),
                factor.get("houses", []),
                chart,
                factor.get("reference"),
            )
            if count >= 2:
                return boost

        return 0.0

    def _is_yoga_cancelled(self, rule: dict[str, Any], chart: BirthChart) -> bool:
        """Check if yoga has cancellation conditions that negate its benefits.

        Args:
            rule: Yoga rule
            chart: Birth chart

        Returns:
            True if yoga is cancelled, False otherwise
        """
        cancellations = rule.get("cancellation", [])

        for cancellation in cancellations:
            cancel_type = cancellation.get("type")
            planet_name = cancellation.get("planet")

            if not planet_name:
                continue

            try:
                planet = Planet(planet_name)
                if planet not in chart.planets:
                    continue

                pos = chart.planets[planet]

                if (cancel_type == "planet_combust" and self._is_combust(planet, chart)) or (
                    cancel_type == "planet_retrograde" and pos.is_retrograde
                ):
                    return True

            except ValueError:
                continue

        # Also run general cancellation checks on involved planets
        detection = rule.get("detection", {})
        planet_name = detection.get("planet")
        planets_list = detection.get("planets", [])

        all_planets = []
        if planet_name:
            all_planets.append(planet_name)
        all_planets.extend(planets_list)

        for pname in all_planets:
            if pname in ["ninth_lord", "tenth_lord", "fifth_lord"]:
                continue
            try:
                planet = Planet(pname)
                if planet in chart.planets and self._check_yoga_cancellation(chart, planet):
                    return True
            except ValueError:
                continue

        return False

    def _check_yoga_cancellation(self, chart: BirthChart, planet: Planet) -> bool:
        """Check if a yoga-forming planet's contribution is cancelled.

        A yoga is cancelled (Yoga Bhanga) when the forming planet is:
        1. Combust (too close to Sun) - fully cancels
        2. Debilitated WITHOUT Neecha Bhanga Raja Yoga - fully cancels
        3. Heavily afflicted by malefics (Saturn, Mars, Rahu conjunct) - cancels
        4. Retrograde - weakens but does not fully cancel (handled via strength)

        Args:
            chart: Birth chart
            planet: The yoga-forming planet to check

        Returns:
            True if the yoga is cancelled, False otherwise
        """
        if planet not in chart.planets:
            return False

        pos = chart.planets[planet]

        # 1. Combustion cancels yoga
        if self._is_combust(planet, chart):
            return True

        # 2. Debilitation without Neecha Bhanga cancels yoga
        if self._is_in_debilitated_sign(planet, pos.rashi) and not self._has_neecha_bhanga(
            planet, chart
        ):
            return True

        # 3. Severe malefic affliction (conjunction with 2+ malefics)
        malefics = [Planet.SATURN, Planet.MARS, Planet.RAHU, Planet.KETU]
        malefic_conjunctions = 0
        for malefic in malefics:
            if malefic == planet:
                continue
            if malefic in chart.planets:
                malefic_pos = chart.planets[malefic]
                if malefic_pos.rashi == pos.rashi:
                    malefic_conjunctions += 1

        return malefic_conjunctions >= 2

    def _has_neecha_bhanga(self, planet: Planet, chart: BirthChart) -> bool:
        """Check if a debilitated planet has Neecha Bhanga (cancellation of debilitation).

        Neecha Bhanga Raja Yoga conditions (any one suffices):
        1. The lord of the sign where the planet is debilitated is in kendra from lagna or moon
        2. The lord of the sign where the planet is exalted is in kendra from lagna or moon
        3. The planet is aspected by the lord of its debilitation sign
        4. The debilitated planet is conjunct an exalted planet
        5. The debilitated planet is in a kendra house

        Args:
            planet: The debilitated planet
            chart: Birth chart

        Returns:
            True if Neecha Bhanga conditions are met
        """
        if planet not in chart.planets:
            return False

        pos = chart.planets[planet]
        debil_sign = self.PLANET_DEBILITATION.get(planet)
        if not debil_sign or pos.rashi != debil_sign:
            return False

        # Sign lordship mapping
        sign_lords = {
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

        # Condition 1: Lord of debilitation sign in kendra from lagna or Moon
        debil_lord = sign_lords.get(debil_sign)
        if debil_lord and debil_lord in chart.planets:
            debil_lord_pos = chart.planets[debil_lord]
            # Check kendra from lagna
            house_from_lagna = self._get_house_from_reference(
                debil_lord_pos.rashi, chart.lagna_rashi
            )
            if is_kendra(house_from_lagna):
                return True
            # Check kendra from Moon
            house_from_moon = self._get_house_from_reference(debil_lord_pos.rashi, chart.moon_rashi)
            if is_kendra(house_from_moon):
                return True

        # Condition 2: Lord of exaltation sign in kendra
        exalt_sign = self.PLANET_EXALTATION.get(planet)
        if exalt_sign:
            exalt_lord = sign_lords.get(exalt_sign)
            if exalt_lord and exalt_lord in chart.planets:
                exalt_lord_pos = chart.planets[exalt_lord]
                house_from_lagna = self._get_house_from_reference(
                    exalt_lord_pos.rashi, chart.lagna_rashi
                )
                if is_kendra(house_from_lagna):
                    return True

        # Condition 3: Debilitated planet conjunct an exalted planet
        for other_planet, other_pos in chart.planets.items():
            if other_planet == planet:
                continue
            if other_pos.rashi == pos.rashi and self._is_in_exalted_sign(
                other_planet, other_pos.rashi
            ):
                return True

        # Condition 4: Debilitated planet in a kendra house
        return bool(is_kendra(pos.house))

    # Condition Evaluators

    def _eval_in_kendra(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is in kendra (1, 4, 7, 10) house."""
        planet_name = condition.get("planet")
        reference = condition.get("reference", "lagna")

        if not planet_name:
            return False

        try:
            planet = Planet(planet_name)
            if planet not in chart.planets:
                return False

            pos = chart.planets[planet]

            if reference == "lagna_or_moon":
                # Check from both Lagna and Moon (classical Pancha Mahapurusha rule)
                house_lagna = pos.house
                house_moon = self._get_house_from_reference(pos.rashi, chart.moon_rashi)
                return is_kendra(house_lagna) or is_kendra(house_moon)
            elif reference == "moon":
                # Calculate house from Moon instead of Lagna
                house = self._get_house_from_reference(pos.rashi, chart.moon_rashi)
            else:
                house = pos.house

            return is_kendra(house)

        except ValueError:
            return False

    def _eval_in_trikona(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is in trikona (1, 5, 9) house."""
        planet_name = condition.get("planet")
        reference = condition.get("reference", "lagna")

        if not planet_name:
            return False

        try:
            planet = Planet(planet_name)
            if planet not in chart.planets:
                return False

            pos = chart.planets[planet]

            if reference == "moon":
                house = self._get_house_from_reference(pos.rashi, chart.moon_rashi)
            else:
                house = pos.house

            return is_trikona(house)

        except ValueError:
            return False

    def _eval_in_dusthana(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is in dusthana (6, 8, 12) house."""
        planet_name = condition.get("planet")

        if not planet_name:
            return False

        try:
            planet = Planet(planet_name)
            if planet not in chart.planets:
                return False

            pos = chart.planets[planet]
            return is_dusthana(pos.house)

        except ValueError:
            return False

    def _eval_in_upachaya(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is in upachaya (3, 6, 10, 11) house."""
        planet_name = condition.get("planet")

        if not planet_name:
            return False

        try:
            planet = Planet(planet_name)
            if planet not in chart.planets:
                return False

            pos = chart.planets[planet]
            return is_upachaya(pos.house)

        except ValueError:
            return False

    def _eval_in_own_sign(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is in its own sign."""
        planet_name = condition.get("planet")

        if not planet_name:
            return False

        try:
            planet = Planet(planet_name)
            if planet not in chart.planets:
                return False

            pos = chart.planets[planet]
            return self._is_in_own_sign(planet, pos.rashi)

        except ValueError:
            return False

    def _eval_in_exalted_sign(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is in exalted sign."""
        planet_name = condition.get("planet")

        if not planet_name:
            return False

        try:
            planet = Planet(planet_name)
            if planet not in chart.planets:
                return False

            pos = chart.planets[planet]
            return self._is_in_exalted_sign(planet, pos.rashi)

        except ValueError:
            return False

    def _eval_in_own_or_exalted(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is in own or exalted sign."""
        planet_name = condition.get("planet")

        if not planet_name:
            return False

        try:
            planet = Planet(planet_name)
            if planet not in chart.planets:
                return False

            pos = chart.planets[planet]
            return self._is_in_own_sign(planet, pos.rashi) or self._is_in_exalted_sign(
                planet, pos.rashi
            )

        except ValueError:
            return False

    def _eval_in_sign(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is in specified sign(s)."""
        planet_name = condition.get("planet")
        signs = condition.get("signs", [])

        if not planet_name or not signs:
            return False

        try:
            planet = Planet(planet_name)
            if planet not in chart.planets:
                return False

            pos = chart.planets[planet]
            return pos.rashi in [Rashi(s) for s in signs]

        except ValueError:
            return False

    def _eval_in_house(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is in specified house(s)."""
        planet_name = condition.get("planet")
        houses = condition.get("houses", [])
        any_planet = condition.get("any_planet", False)

        if any_planet:
            # Check if any of specified planets are in houses
            planets = condition.get("planets", [])
            for p in planets:
                try:
                    planet = Planet(p)
                    if planet in chart.planets:
                        pos = chart.planets[planet]
                        if pos.house in houses:
                            return True
                except ValueError:
                    continue
            return False

        if not planet_name or not houses:
            return False

        try:
            planet = Planet(planet_name)
            if planet not in chart.planets:
                return False

            pos = chart.planets[planet]
            return pos.house in houses

        except ValueError:
            return False

    def _eval_in_houses(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planets are in specified houses from reference point."""
        planets = condition.get("planets", [])
        houses = condition.get("houses", [])
        reference = condition.get("reference", "lagna")
        any_planet = condition.get("any_planet", False)

        if not planets or not houses:
            return False

        ref_rashi = chart.moon_rashi if reference == "moon" else chart.lagna_rashi

        for planet_name in planets:
            try:
                planet = Planet(planet_name)
                if planet not in chart.planets:
                    if not any_planet:
                        return False
                    continue

                pos = chart.planets[planet]
                house = self._get_house_from_reference(pos.rashi, ref_rashi)

                if house in houses:
                    if any_planet:
                        return True
                elif not any_planet:
                    return False

            except ValueError:
                if not any_planet:
                    return False
                continue

        return not any_planet

    def _eval_conjunct(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planets are conjunct (in the same sign)."""
        planets = condition.get("planets", [])

        if len(planets) < 2:
            return False

        signs = []
        for planet_name in planets:
            try:
                planet = Planet(planet_name)
                if planet not in chart.planets:
                    return False
                pos = chart.planets[planet]
                signs.append(pos.rashi)
            except ValueError:
                return False

        return len(set(signs)) == 1  # All in same sign

    def _eval_aspected_by(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planet is aspected by specified planets."""
        target_planet = condition.get("planet")
        aspecting_planets = condition.get("planets", [])

        if not target_planet or not aspecting_planets:
            return False

        try:
            target = Planet(target_planet)
            if target not in chart.planets:
                return False

            target_pos = chart.planets[target]
            target_house = target_pos.house

            for aspecting_name in aspecting_planets:
                try:
                    aspecting = Planet(aspecting_name)
                    if aspecting not in chart.planets:
                        continue

                    aspects = calculate_aspect_houses(aspecting, chart.planets[aspecting].house)
                    if target_house in aspects:
                        return True

                except ValueError:
                    continue

            return False

        except ValueError:
            return False

    def _eval_lord_in_house(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if lord of a house is in specified house."""
        from_house = condition.get("from_house")
        in_house = condition.get("in_house")

        if not from_house or not in_house:
            return False

        lord = self._get_house_lord(from_house, chart)
        if not lord or lord not in chart.planets:
            return False

        return chart.planets[lord].house == in_house

    def _eval_exchange(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if two planets have exchange of lordship."""
        planet1_name = condition.get("planet1")
        planet2_name = condition.get("planet2")

        if not planet1_name or not planet2_name:
            return False

        try:
            planet1 = Planet(planet1_name)
            planet2 = Planet(planet2_name)

            if planet1 not in chart.planets or planet2 not in chart.planets:
                return False

            pos1 = chart.planets[planet1]
            pos2 = chart.planets[planet2]

            # Check if planet1 is in sign ruled by planet2 and vice versa
            return pos1.rashi in self.PLANET_RULERSHIP.get(
                planet2, []
            ) and pos2.rashi in self.PLANET_RULERSHIP.get(planet1, [])

        except ValueError:
            return False

    def _eval_in_kendra_or_trikona(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if planets form kendra or trikona relationship."""
        planets = condition.get("planets", [])

        if len(planets) < 2:
            return False

        try:
            planet_objs = [Planet(p) for p in planets]
            positions = [chart.planets.get(p) for p in planet_objs]

            if any(p is None for p in positions):
                return False

            houses = [self._get_house_from_reference(p.rashi, chart.lagna_rashi) for p in positions]

            # Check all pairs
            for i in range(len(houses)):
                for j in range(i + 1, len(houses)):
                    h1, h2 = houses[i], houses[j]
                    diff = abs(h1 - h2)

                    # Kendra relationship: 0, 3, 6, 9 houses apart
                    if diff in [3, 6, 9]:
                        return True
                    # Trikona relationship: 4, 8 houses apart (1-5, 1-9, etc.)
                    if diff in [4, 8]:
                        return True

            return False

        except ValueError:
            return False

    def _eval_all_in_beneficial(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if all planets are in beneficial houses."""
        planets = condition.get("planets", [])

        if not planets:
            return False

        beneficial = [1, 4, 5, 7, 9, 10]  # Kendra and trikona houses

        for planet_name in planets:
            try:
                planet = Planet(planet_name)
                if planet not in chart.planets:
                    return False

                pos = chart.planets[planet]
                if pos.house not in beneficial:
                    return False

            except ValueError:
                return False

        return True

    def _eval_planet_aspects_target(self, condition: dict[str, Any], chart: BirthChart) -> bool:
        """Check if a planet aspects a target (moon, lagna, or specific house).

        The condition type encodes planet and target:
          saturn_aspects_moon, mars_aspects_lagna, jupiter_aspects_5th, etc.
        """
        cond_type = condition.get("type", "")
        parts = cond_type.split("_aspects_")
        if len(parts) != 2:
            return False

        planet_name, target = parts

        try:
            planet = Planet(planet_name)
        except ValueError:
            return False

        if planet not in chart.planets:
            return False

        aspects = calculate_aspect_houses(planet, chart.planets[planet].house)

        if target == "moon":
            moon = chart.planets.get(Planet("moon"))
            return moon is not None and moon.house in aspects
        elif target == "lagna":
            return 1 in aspects
        else:
            # Numeric house target: "5th" → 5, "7th" → 7, "9th" → 9
            try:
                house_num = int(target.rstrip("stndrh"))
                return house_num in aspects
            except ValueError:
                return False

    # Helper methods

    def _is_in_own_sign(self, planet: Planet, rashi: Rashi) -> bool:
        """Check if planet is in its own sign."""
        return rashi in self.PLANET_RULERSHIP.get(planet, [])

    def _is_in_exalted_sign(self, planet: Planet, rashi: Rashi) -> bool:
        """Check if planet is in its exalted sign."""
        return rashi == self.PLANET_EXALTATION.get(planet)

    def _is_in_debilitated_sign(self, planet: Planet, rashi: Rashi) -> bool:
        """Check if planet is in its debilitated sign."""
        return rashi == self.PLANET_DEBILITATION.get(planet)

    def _is_combust(self, planet: Planet, chart: BirthChart) -> bool:
        """Check if planet is combust (too close to Sun)."""
        if planet == Planet.SUN or planet not in chart.planets:
            return False

        sun_pos = chart.planets.get(Planet.SUN)
        planet_pos = chart.planets[planet]

        if not sun_pos:
            return False

        # Combustion distance varies by planet (typically 8-12 degrees)
        combustion_distances = {
            Planet.MOON: 12,
            Planet.MERCURY: 7,
            Planet.VENUS: 8,
            Planet.MARS: 17,
            Planet.JUPITER: 11,
            Planet.SATURN: 15,
            Planet.RAHU: 10,
            Planet.KETU: 10,
        }

        distance = combustion_distances.get(planet, 10)

        # Calculate difference in longitude
        diff = abs(sun_pos.longitude - planet_pos.longitude)
        diff = min(diff, 360 - diff)  # Use shortest arc

        return diff < distance

    def _get_house_from_reference(self, planet_rashi: Rashi, reference_rashi: Rashi) -> int:
        """Get house number from reference rashi (e.g., Moon, Lagna)."""
        rashis = list(Rashi)
        planet_idx = rashis.index(planet_rashi)
        ref_idx = rashis.index(reference_rashi)
        house = ((planet_idx - ref_idx) % 12) + 1
        return house

    def _get_house_lord(self, house: int, chart: BirthChart) -> Planet | None:
        """Get the lord (ruling planet) of a house."""
        # Get the sign of the house cusp
        house_cusp_longitude = chart.houses.cusps[house - 1]

        # Determine which sign this cusp falls in
        sign_num = int(house_cusp_longitude / 30)
        rashi = list(Rashi)[sign_num % 12]

        # Find which planet rules this sign
        for planet, signs in self.PLANET_RULERSHIP.items():
            if rashi in signs:
                return planet

        return None

    def _have_mutual_aspect(self, planet1_name: str, planet2_name: str, chart: BirthChart) -> bool:
        """Check if two planets have mutual aspect."""
        try:
            p1 = Planet(planet1_name)
            p2 = Planet(planet2_name)

            if p1 not in chart.planets or p2 not in chart.planets:
                return False

            pos1 = chart.planets[p1]
            pos2 = chart.planets[p2]

            # Check if p1 aspects p2
            aspects1 = calculate_aspect_houses(p1, pos1.house)
            if pos2.house not in aspects1:
                return False

            # Check if p2 aspects p1
            aspects2 = calculate_aspect_houses(p2, pos2.house)
            return pos1.house in aspects2

        except ValueError:
            return False

    def _count_planets_in_houses(
        self,
        planets: list[str],
        houses: list[int],
        chart: BirthChart,
        reference: str | None = None,
    ) -> int:
        """Count how many planets are in specified houses."""
        count = 0
        ref_rashi = chart.moon_rashi if reference == "moon" else chart.lagna_rashi

        for planet_name in planets:
            try:
                planet = Planet(planet_name)
                if planet not in chart.planets:
                    continue

                pos = chart.planets[planet]
                house = self._get_house_from_reference(pos.rashi, ref_rashi)

                if house in houses:
                    count += 1

            except ValueError:
                continue

        return count

    def get_yoga_strength(self, yoga: DetectedYoga, _chart: BirthChart) -> float:
        """Get the current strength of a detected yoga.

        Args:
            yoga: The detected yoga
            _chart: The birth chart (reserved for future use)

        Returns:
            Strength value between 0.0 and 1.0
        """
        return yoga.strength


def detect_neecha_bhanga(
    planet: str,
    planet_data: dict,
    all_planets: dict,
    lagna_rashi: str,
    d9_positions: dict | None = None,
) -> dict:
    """Detect Neecha Bhanga Raja Yoga with full 5-condition check.

    A debilitated planet gains cancellation of debilitation (Neecha Bhanga)
    if ANY one of the following 5 conditions is met:

    1. Lord of the debilitation sign is in kendra from Lagna or Moon
    2. Lord of the exaltation sign is in kendra from Lagna or Moon
    3. Planet exalted in the debilitation sign aspects the debilitated planet
    4. Debilitated planet is retrograde
    5. Debilitated planet is in Navamsha of its exaltation sign

    Args:
        planet: Planet name (e.g., "mars", "jupiter")
        planet_data: Dict with keys like 'rashi', 'longitude', 'is_retrograde', 'house'
        all_planets: Dict of all planet positions keyed by planet name or Planet enum
        lagna_rashi: Ascendant sign name (e.g., "aries", "libra")
        d9_positions: Optional dict of Navamsha positions keyed by planet name,
                      each having a 'rashi' or 'rashi_name' field

    Returns:
        Dict with:
        - has_neecha_bhanga (bool): Whether any condition is met
        - conditions_met (list[str]): Descriptions of met conditions
        - strength_modifier (float): 0.0 = no bhanga, higher = stronger cancellation
    """
    result = {
        "has_neecha_bhanga": False,
        "conditions_met": [],
        "strength_modifier": 0.0,
    }

    # Exaltation/debilitation lookups
    debilitation_map = {
        "sun": "libra",
        "moon": "scorpio",
        "mars": "cancer",
        "mercury": "pisces",
        "jupiter": "capricorn",
        "venus": "virgo",
        "saturn": "aries",
    }
    exaltation_map = {
        "sun": "aries",
        "moon": "taurus",
        "mars": "capricorn",
        "mercury": "virgo",
        "jupiter": "cancer",
        "venus": "pisces",
        "saturn": "libra",
    }
    sign_lords = {
        "aries": "mars",
        "taurus": "venus",
        "gemini": "mercury",
        "cancer": "moon",
        "leo": "sun",
        "virgo": "mercury",
        "libra": "venus",
        "scorpio": "mars",
        "sagittarius": "jupiter",
        "capricorn": "saturn",
        "aquarius": "saturn",
        "pisces": "jupiter",
    }
    rashi_list = [
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
        "aquarius",
        "pisces",
    ]

    planet_lower = planet.lower()

    # Get planet's current rashi
    p_rashi = planet_data.get("rashi", "")
    if hasattr(p_rashi, "value"):
        p_rashi = p_rashi.value
    p_rashi = p_rashi.lower()

    # Check if planet is actually debilitated
    debil_sign = debilitation_map.get(planet_lower)
    if not debil_sign or p_rashi != debil_sign:
        return result

    exalt_sign = exaltation_map.get(planet_lower, "")

    def _get_rashi(key):
        """Extract rashi string from planet data in all_planets."""
        data = all_planets.get(key)
        if data is None:
            # Try Planet enum
            try:
                data = all_planets.get(Planet(key))
            except (ValueError, KeyError):
                return None
        if data is None:
            return None
        r = data.get("rashi", "") if isinstance(data, dict) else getattr(data, "rashi", "")
        if hasattr(r, "value"):
            r = r.value
        return r.lower() if r else None

    def _house_from_ref(planet_rashi_name, ref_rashi_name):
        """Calculate house number from reference."""
        if planet_rashi_name not in rashi_list or ref_rashi_name not in rashi_list:
            return 0
        p_idx = rashi_list.index(planet_rashi_name)
        r_idx = rashi_list.index(ref_rashi_name)
        return ((p_idx - r_idx) % 12) + 1

    kendra_houses = {1, 4, 7, 10}
    conditions_met = []

    # Get Moon rashi for checks from Moon
    moon_rashi = _get_rashi("moon")
    lagna_lower = lagna_rashi.lower() if isinstance(lagna_rashi, str) else str(lagna_rashi).lower()

    # Condition 1: Lord of debilitation sign in kendra from Lagna or Moon
    debil_lord = sign_lords.get(debil_sign)
    if debil_lord:
        lord_rashi = _get_rashi(debil_lord)
        if lord_rashi:
            h_lagna = _house_from_ref(lord_rashi, lagna_lower)
            h_moon = _house_from_ref(lord_rashi, moon_rashi) if moon_rashi else 0
            if h_lagna in kendra_houses or h_moon in kendra_houses:
                conditions_met.append(
                    f"Lord of debilitation sign ({debil_lord.title()}) in kendra "
                    f"from {'Lagna' if h_lagna in kendra_houses else 'Moon'}"
                )

    # Condition 2: Lord of exaltation sign in kendra from Lagna or Moon
    if exalt_sign:
        exalt_lord = sign_lords.get(exalt_sign)
        if exalt_lord:
            lord_rashi = _get_rashi(exalt_lord)
            if lord_rashi:
                h_lagna = _house_from_ref(lord_rashi, lagna_lower)
                h_moon = _house_from_ref(lord_rashi, moon_rashi) if moon_rashi else 0
                if h_lagna in kendra_houses or h_moon in kendra_houses:
                    conditions_met.append(
                        f"Lord of exaltation sign ({exalt_lord.title()}) in kendra "
                        f"from {'Lagna' if h_lagna in kendra_houses else 'Moon'}"
                    )

    # Condition 3: Planet exalted in the debilitation sign aspects the debilitated planet
    # Find which planet is exalted in the debilitation sign
    for p_name, ex_sign in exaltation_map.items():
        if ex_sign == debil_sign and p_name != planet_lower:
            # This planet is exalted in the debilitation sign
            aspecting_rashi = _get_rashi(p_name)
            if aspecting_rashi and p_rashi:
                # Check if it aspects the debilitated planet's sign
                # All planets aspect 7th house, special aspects for Mars/Jupiter/Saturn
                h = _house_from_ref(p_rashi, aspecting_rashi)
                aspects = {7}
                if p_name == "mars":
                    aspects.update({4, 8})
                elif p_name == "jupiter":
                    aspects.update({5, 9})
                elif p_name == "saturn":
                    aspects.update({3, 10})
                if h in aspects:
                    conditions_met.append(
                        f"{p_name.title()} (exalted in {debil_sign.title()}) "
                        f"aspects the debilitated {planet_lower.title()}"
                    )

    # Condition 4: Debilitated planet is retrograde
    is_retro = planet_data.get("is_retrograde", False)
    if hasattr(is_retro, "__bool__"):
        is_retro = bool(is_retro)
    if is_retro:
        conditions_met.append(f"{planet_lower.title()} is retrograde while debilitated")

    # Condition 5: Debilitated planet is in Navamsha of its exaltation sign
    if d9_positions and exalt_sign:
        d9_data = d9_positions.get(planet_lower) or d9_positions.get(planet)
        if d9_data:
            d9_rashi = d9_data.get("rashi_name", d9_data.get("rashi", ""))
            if hasattr(d9_rashi, "value"):
                d9_rashi = d9_rashi.value
            d9_rashi = d9_rashi.lower() if d9_rashi else ""
            if d9_rashi == exalt_sign:
                conditions_met.append(
                    f"{planet_lower.title()} is in Navamsha of exaltation sign ({exalt_sign.title()})"
                )

    if conditions_met:
        result["has_neecha_bhanga"] = True
        result["conditions_met"] = conditions_met
        # More conditions met = stronger cancellation
        result["strength_modifier"] = min(1.0, 0.3 * len(conditions_met))

    return result


def detect_all_yogas(chart: BirthChart) -> list[DetectedYoga]:
    """Convenience function to detect all yogas in a birth chart.

    Args:
        chart: Birth chart to analyze

    Returns:
        List of detected yogas
    """
    detector = YogaDetector()
    return detector.detect_all_yogas(chart)


def detect_yoga(yoga_rule: dict[str, Any], chart: BirthChart) -> DetectedYoga | None:
    """Convenience function to detect a single yoga.

    Args:
        yoga_rule: Yoga rule dictionary
        chart: Birth chart to analyze

    Returns:
        DetectedYoga if yoga is present, None otherwise
    """
    detector = YogaDetector()
    return detector.detect_yoga(yoga_rule, chart)


def evaluate_condition(condition: dict[str, Any], chart: BirthChart) -> bool:
    """Convenience function to evaluate a single condition.

    Args:
        condition: Condition specification
        chart: Birth chart to evaluate

    Returns:
        True if condition is met, False otherwise
    """
    detector = YogaDetector()
    return detector._evaluate_condition(condition, chart)


def get_yoga_strength(yoga: DetectedYoga, chart: BirthChart) -> float:
    """Convenience function to get yoga strength.

    Args:
        yoga: Detected yoga
        chart: Birth chart

    Returns:
        Strength value (0.0-1.0)
    """
    detector = YogaDetector()
    return detector.get_yoga_strength(yoga, chart)
