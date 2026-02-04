"""Muhurta (auspicious timing) calculations for 108 Vedic Astrology app.

This module provides comprehensive Muhurta evaluation and calculations for
determining auspicious times to perform various activities based on Vedic
astrology principles.

Muhurta involves analyzing:
- Tithi (lunar day)
- Nakshatra (lunar mansion)
- Yoga (planetary combinations)
- Karana (half-lunar day)
- Vara (weekday)
- Inauspicious periods (Rahu Kaal, Yamaghanda, Gulika)
- Choghadiya (8 periods of day/night)

The module supports evaluation of various activities:
- Marriage (Vivaha)
- Travel (Yatra)
- Business start (Vyapara Simha)
- House entry (Grah Pravesh)
- Surgery (Bhishagya Karma)
- Vehicle purchase (Yantra Kray)
"""

from collections.abc import Callable
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from packages.core.src.knowledge_loader import get_muhurta_rules

# Module-level cache for muhurta rules
_muhurta_rules_cache: dict[str, Any] | None = None


def _get_muhurta_rules() -> dict[str, Any]:
    """Get cached muhurta rules from JSON."""
    global _muhurta_rules_cache
    if _muhurta_rules_cache is None:
        _muhurta_rules_cache = get_muhurta_rules()
    return _muhurta_rules_cache


def _get_inauspicious_slots(period_type: str) -> dict[str, int]:
    """Get inauspicious period slots from JSON with fallback."""
    rules = _get_muhurta_rules()
    periods = rules.get("inauspicious_periods", {})
    period_data = periods.get(period_type, {})
    return period_data.get("slots_by_weekday", {})


class MuhurtaQuality(Enum):
    """Enumeration of Muhurta quality levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class ActivityType(Enum):
    """Enumeration of supported activities for Muhurta evaluation."""

    MARRIAGE = "marriage"
    TRAVEL = "travel"
    BUSINESS_START = "business_start"
    HOUSE_ENTRY = "house_entry"
    SURGERY = "surgery"
    VEHICLE_PURCHASE = "vehicle_purchase"


# Rahu Kaal timing (portion of day to avoid)
# Hours from sunrise, each slot = day_duration/8
_DEFAULT_RAHU_KAAL = {
    "sunday": 8,
    "monday": 2,
    "tuesday": 7,
    "wednesday": 5,
    "thursday": 6,
    "friday": 4,
    "saturday": 3,
}

# Yamaghanda Kaal (even more inauspicious than Rahu Kaal)
_DEFAULT_YAMAGHANDA = {
    "sunday": 5,
    "monday": 4,
    "tuesday": 3,
    "wednesday": 2,
    "thursday": 1,
    "friday": 7,
    "saturday": 6,
}

# Gulika Kaal
_DEFAULT_GULIKA = {
    "sunday": 7,
    "monday": 6,
    "tuesday": 5,
    "wednesday": 4,
    "thursday": 3,
    "friday": 2,
    "saturday": 1,
}

# Backwards-compatible exports - try JSON first, then fall back to defaults
RAHU_KAAL = _get_inauspicious_slots("rahu_kaal") or _DEFAULT_RAHU_KAAL
YAMAGHANDA = _get_inauspicious_slots("yamaghanda") or _DEFAULT_YAMAGHANDA
GULIKA = _get_inauspicious_slots("gulika") or _DEFAULT_GULIKA

# Activity-specific Muhurta rules
ACTIVITY_RULES = {
    "marriage": {
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "avoid_tithis": [4, 6, 8, 9, 14, 15, 30],
        "good_nakshatras": [
            "Rohini",
            "Mrigashira",
            "Magha",
            "Uttara Phalguni",
            "Hasta",
            "Swati",
            "Anuradha",
            "Mula",
            "Uttara Ashadha",
            "Uttara Bhadrapada",
            "Revati",
        ],
        "avoid_nakshatras": ["Bharani", "Krittika", "Ashlesha", "Jyeshtha", "Mula"],
        "good_varas": ["monday", "wednesday", "thursday", "friday"],
        "avoid_varas": ["saturday"],
        "avoid_yogas": ["Vyatipata", "Vaidhriti"],
        "good_karana": ["Bava", "Balava", "Kaulava", "Taitila", "Gaja", "Vanija"],
    },
    "travel": {
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "avoid_tithis": [4, 6, 8, 9, 14, 15, 30],
        "good_nakshatras": [
            "Ashwini",
            "Mrigashira",
            "Punarvasu",
            "Pushya",
            "Hasta",
            "Anuradha",
            "Shravana",
            "Dhanishtha",
            "Revati",
        ],
        "good_varas": ["monday", "wednesday", "friday"],
        "avoid_varas": ["saturday"],
        "good_directions": {
            "sunday": "east",
            "monday": "northwest",
            "tuesday": "south",
            "wednesday": "north",
            "thursday": "northeast",
            "friday": "southeast",
            "saturday": "west",
        },
    },
    "business_start": {
        "good_tithis": [2, 3, 5, 6, 7, 10, 11, 12, 13],
        "avoid_tithis": [4, 8, 9, 14, 15, 30],
        "good_nakshatras": [
            "Ashwini",
            "Rohini",
            "Mrigashira",
            "Punarvasu",
            "Pushya",
            "Uttara Phalguni",
            "Hasta",
            "Chitra",
            "Swati",
            "Anuradha",
            "Uttara Ashadha",
            "Shravana",
            "Dhanishtha",
            "Shatabhisha",
            "Uttara Bhadrapada",
            "Revati",
        ],
        "good_varas": ["monday", "wednesday", "thursday", "friday"],
        "avoid_varas": ["saturday"],
    },
    "house_entry": {
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "avoid_tithis": [4, 6, 8, 9, 14, 15, 30],
        "good_nakshatras": [
            "Rohini",
            "Mrigashira",
            "Uttara Phalguni",
            "Hasta",
            "Chitra",
            "Swati",
            "Anuradha",
            "Uttara Ashadha",
            "Shravana",
            "Dhanishtha",
            "Shatabhisha",
            "Uttara Bhadrapada",
            "Revati",
        ],
        "good_varas": ["monday", "wednesday", "thursday", "friday"],
        "avoid_varas": ["saturday"],
    },
    "surgery": {
        "avoid_nakshatras": [
            "Bharani",
            "Krittika",
            "Ardra",
            "Ashlesha",
            "Magha",
            "Purva Phalguni",
            "Vishakha",
            "Jyeshtha",
            "Mula",
            "Purva Ashadha",
            "Purva Bhadrapada",
        ],
        "avoid_tithis": [4, 6, 8, 9, 14, 30],
        "good_varas": ["monday", "wednesday", "friday"],
        "avoid_varas": ["saturday"],
    },
    "vehicle_purchase": {
        "good_nakshatras": [
            "Ashwini",
            "Rohini",
            "Pushya",
            "Uttara Phalguni",
            "Hasta",
            "Chitra",
            "Swati",
            "Anuradha",
            "Uttara Ashadha",
            "Shravana",
            "Revati",
        ],
        "good_varas": ["wednesday", "thursday", "friday"],
        "avoid_varas": ["saturday"],
    },
}

# Choghadiya (8 periods of day and night with quality)
CHOGHADIYA_ORDER = {
    "day": {
        "sunday": ["Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],
        "monday": ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit"],
        "tuesday": ["Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
        "wednesday": ["Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh"],
        "thursday": ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh"],
        "friday": ["Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal"],
        "saturday": ["Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal"],
    },
    "night": {
        "sunday": ["Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh"],
        "monday": ["Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
        "tuesday": ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit"],
        "wednesday": ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh"],
        "thursday": ["Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal"],
        "friday": ["Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],
        "saturday": ["Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal"],
    },
}

# Choghadiya quality assessment
CHOGHADIYA_QUALITY = {
    "Amrit": "excellent",  # Nectar-like, very auspicious
    "Shubh": "good",  # Good, auspicious
    "Labh": "good",  # Gain-like, good for financial activities
    "Chal": "neutral",  # Mobile, good for travel and movement
    "Rog": "poor",  # Disease-like, inauspicious
    "Kaal": "poor",  # Death-like, inauspicious
    "Udveg": "poor",  # Agitation, inauspicious
}


def calculate_rahu_kaal(sunrise: datetime, sunset: datetime, weekday: str) -> dict[str, Any]:
    """Calculate Rahu Kaal timing for the day.

    Rahu Kaal is an inauspicious period of approximately 90 minutes
    that should be avoided for starting new ventures.

    Args:
        sunrise: Sunrise time for the day
        sunset: Sunset time for the day
        weekday: Day of the week (lowercase, e.g., "monday")

    Returns:
        Dictionary containing:
        - start: Datetime when Rahu Kaal begins
        - end: Datetime when Rahu Kaal ends
        - duration: Duration in seconds
        - weekday: The weekday provided
        - is_active: Callable to check if a datetime falls within Rahu Kaal

    Raises:
        ValueError: If weekday is not valid

    Example:
        >>> sunrise = datetime(2026, 2, 4, 6, 30)
        >>> sunset = datetime(2026, 2, 4, 18, 30)
        >>> rahu = calculate_rahu_kaal(sunrise, sunset, "monday")
        >>> rahu["start"]
        datetime.datetime(2026, 2, 4, 7, 45)
    """
    weekday_lower = weekday.lower()
    if weekday_lower not in RAHU_KAAL:
        raise ValueError(f"Invalid weekday: {weekday}. Must be Monday-Sunday (case-insensitive)")

    day_duration = (sunset - sunrise).total_seconds()
    slot_duration = day_duration / 8
    slot_num = RAHU_KAAL[weekday_lower]

    start = sunrise + timedelta(seconds=(slot_num - 1) * slot_duration)
    end = sunrise + timedelta(seconds=slot_num * slot_duration)

    def is_active(dt: datetime) -> bool:
        """Check if given datetime falls within Rahu Kaal."""
        return start <= dt <= end

    return {
        "start": start,
        "end": end,
        "duration": slot_duration,
        "weekday": weekday,
        "is_active": is_active,
    }


def calculate_yamaghanda(sunrise: datetime, sunset: datetime, weekday: str) -> dict[str, Any]:
    """Calculate Yamaghanda Kaal timing for the day.

    Yamaghanda is even more inauspicious than Rahu Kaal and should be
    strictly avoided for important activities.

    Args:
        sunrise: Sunrise time for the day
        sunset: Sunset time for the day
        weekday: Day of the week (lowercase, e.g., "monday")

    Returns:
        Dictionary with timing details (same structure as calculate_rahu_kaal)

    Raises:
        ValueError: If weekday is not valid
    """
    weekday_lower = weekday.lower()
    if weekday_lower not in YAMAGHANDA:
        raise ValueError(f"Invalid weekday: {weekday}. Must be Monday-Sunday (case-insensitive)")

    day_duration = (sunset - sunrise).total_seconds()
    slot_duration = day_duration / 8
    slot_num = YAMAGHANDA[weekday_lower]

    start = sunrise + timedelta(seconds=(slot_num - 1) * slot_duration)
    end = sunrise + timedelta(seconds=slot_num * slot_duration)

    def is_active(dt: datetime) -> bool:
        """Check if given datetime falls within Yamaghanda."""
        return start <= dt <= end

    return {
        "start": start,
        "end": end,
        "duration": slot_duration,
        "weekday": weekday,
        "is_active": is_active,
    }


def calculate_gulika(sunrise: datetime, sunset: datetime, weekday: str) -> dict[str, Any]:
    """Calculate Gulika Kaal timing for the day.

    Gulika Kaal is another inauspicious period that should be avoided,
    though less severe than Yamaghanda.

    Args:
        sunrise: Sunrise time for the day
        sunset: Sunset time for the day
        weekday: Day of the week (lowercase, e.g., "monday")

    Returns:
        Dictionary with timing details (same structure as calculate_rahu_kaal)

    Raises:
        ValueError: If weekday is not valid
    """
    weekday_lower = weekday.lower()
    if weekday_lower not in GULIKA:
        raise ValueError(f"Invalid weekday: {weekday}. Must be Monday-Sunday (case-insensitive)")

    day_duration = (sunset - sunrise).total_seconds()
    slot_duration = day_duration / 8
    slot_num = GULIKA[weekday_lower]

    start = sunrise + timedelta(seconds=(slot_num - 1) * slot_duration)
    end = sunrise + timedelta(seconds=slot_num * slot_duration)

    def is_active(dt: datetime) -> bool:
        """Check if given datetime falls within Gulika."""
        return start <= dt <= end

    return {
        "start": start,
        "end": end,
        "duration": slot_duration,
        "weekday": weekday,
        "is_active": is_active,
    }


def calculate_all_inauspicious(
    sunrise: datetime, sunset: datetime, weekday: str
) -> dict[str, dict[str, Any]]:
    """Calculate all inauspicious periods for the day.

    Args:
        sunrise: Sunrise time for the day
        sunset: Sunset time for the day
        weekday: Day of the week (lowercase, e.g., "monday")

    Returns:
        Dictionary containing:
        - rahu_kaal: Rahu Kaal timing
        - yamaghanda: Yamaghanda timing
        - gulika: Gulika timing

    Raises:
        ValueError: If weekday is not valid
    """
    return {
        "rahu_kaal": calculate_rahu_kaal(sunrise, sunset, weekday),
        "yamaghanda": calculate_yamaghanda(sunrise, sunset, weekday),
        "gulika": calculate_gulika(sunrise, sunset, weekday),
    }


def calculate_choghadiya(
    sunrise: datetime, sunset: datetime, weekday: str, is_night: bool = False
) -> list[dict[str, Any]]:
    """Calculate Choghadiya (8 periods) for the day or night.

    Choghadiya divides the day/night into 8 equal periods, each with
    specific qualities (Amrit, Shubh, Labh, Chal, Rog, Kaal, Udveg).

    Args:
        sunrise: Sunrise time for the day
        sunset: Sunset time for the day
        weekday: Day of the week (lowercase)
        is_night: If True, calculate night Choghadiya; otherwise day

    Returns:
        List of dictionaries, each containing:
        - period_number: 1-8
        - name: Name of the Choghadiya (Amrit, Shubh, etc.)
        - quality: Quality level (excellent, good, neutral, poor)
        - start: Start time of the period
        - end: End time of the period
        - duration: Duration in seconds
        - good_for: List of activities suitable for this period

    Raises:
        ValueError: If weekday is not valid
    """
    weekday_lower = weekday.lower()
    if weekday_lower not in CHOGHADIYA_ORDER["day"]:
        raise ValueError(f"Invalid weekday: {weekday}. Must be Monday-Sunday (case-insensitive)")

    period_type = "night" if is_night else "day"
    choghadiya_names = CHOGHADIYA_ORDER[period_type][weekday_lower]

    if is_night:
        # Night: from sunset to next sunrise (approximately)
        start_time = sunset
        end_time = sunset + timedelta(hours=12)  # Approximate night duration
    else:
        # Day: from sunrise to sunset
        start_time = sunrise
        end_time = sunset

    total_duration = (end_time - start_time).total_seconds()
    period_duration = total_duration / 8

    choghadiya_periods = []
    for i, name in enumerate(choghadiya_names):
        period_start = start_time + timedelta(seconds=i * period_duration)
        period_end = start_time + timedelta(seconds=(i + 1) * period_duration)

        quality = CHOGHADIYA_QUALITY.get(name, "neutral")
        good_for = _get_choghadiya_activities(name)

        choghadiya_periods.append(
            {
                "period_number": i + 1,
                "name": name,
                "quality": quality,
                "start": period_start,
                "end": period_end,
                "duration": period_duration,
                "good_for": good_for,
            }
        )

    return choghadiya_periods


def _get_choghadiya_activities(choghadiya_name: str) -> list[str]:
    """Get recommended activities for a specific Choghadiya.

    Args:
        choghadiya_name: Name of the Choghadiya period

    Returns:
        List of activities suitable for this period
    """
    activities_map = {
        "Amrit": [
            "all_activities",
            "marriage",
            "business",
            "surgery",
            "travel",
            "purchases",
        ],
        "Shubh": ["marriage", "business", "travel", "purchases", "property_deals"],
        "Labh": ["business", "trade", "financial_transactions", "collections"],
        "Chal": ["travel", "short_journeys", "communication"],
        "Rog": [],
        "Kaal": [],
        "Udveg": [],
    }
    return activities_map.get(choghadiya_name, [])


def evaluate_muhurta(
    activity: str, panchanga: dict[str, Any], datetime_obj: datetime
) -> dict[str, Any]:
    """Evaluate Muhurta quality for a specific activity.

    Calculates a comprehensive score based on Tithi, Nakshatra, Vara,
    Yoga, and Karana alignment with the activity requirements.

    Args:
        activity: Type of activity (e.g., "marriage", "travel", "business_start")
        panchanga: Dictionary containing:
            - tithi: {"number": int, "name": str, "paksha": str}
            - nakshatra: {"number": int, "name": str, "pada": int}
            - yoga: {"number": int, "name": str}
            - karana: {"number": int, "name": str}
            - vara: {"number": int, "name": str}
        datetime_obj: The datetime being evaluated

    Returns:
        Dictionary containing:
        - activity: The activity being evaluated
        - score: Score 0-100
        - quality: MuhurtaQuality enum value
        - favorable_factors: List of positive factors
        - unfavorable_factors: List of negative factors
        - recommendation: String with recommendation text

    Raises:
        KeyError: If required panchanga data is missing
        ValueError: If activity is not recognized
    """
    if activity not in ACTIVITY_RULES:
        raise ValueError(
            f"Unknown activity: {activity}. " f"Supported: {', '.join(ACTIVITY_RULES.keys())}"
        )

    rules = ACTIVITY_RULES[activity]
    score = 50  # Base score
    favorable = []
    unfavorable = []

    # Check Tithi (lunar day)
    tithi_num = panchanga["tithi"]["number"]
    tithi_name = panchanga["tithi"]["name"]

    if tithi_num in rules.get("good_tithis", []):
        score += 15
        favorable.append(f"Auspicious tithi: {tithi_name}")
    elif tithi_num in rules.get("avoid_tithis", []):
        score -= 20
        unfavorable.append(f"Inauspicious tithi: {tithi_name}")

    # Check Nakshatra (lunar mansion)
    nakshatra = panchanga["nakshatra"]["name"]

    if nakshatra in rules.get("good_nakshatras", []):
        score += 20
        favorable.append(f"Auspicious nakshatra: {nakshatra}")
    elif nakshatra in rules.get("avoid_nakshatras", []):
        score -= 25
        unfavorable.append(f"Inauspicious nakshatra: {nakshatra}")

    # Check Vara (weekday)
    vara = panchanga["vara"]["name"].lower()

    if vara in rules.get("good_varas", []):
        score += 15
        favorable.append(f"Auspicious day: {vara.capitalize()}")
    elif vara in rules.get("avoid_varas", []):
        score -= 15
        unfavorable.append(f"Inauspicious day: {vara.capitalize()}")

    # Check Yoga (planetary combination)
    yoga = panchanga["yoga"]["name"]

    if yoga in rules.get("avoid_yogas", []):
        score -= 20
        unfavorable.append(f"Inauspicious yoga: {yoga}")
    elif yoga in rules.get("good_yogas", []):
        score += 10
        favorable.append(f"Auspicious yoga: {yoga}")

    # Check Karana (half-lunar day)
    if "good_karana" in rules and "karana" in panchanga:
        karana_name = panchanga["karana"]["name"]
        if karana_name in rules["good_karana"]:
            score += 10
            favorable.append(f"Auspicious karana: {karana_name}")

    # Determine quality level
    score = min(100, max(0, score))
    if score >= 80:
        quality = MuhurtaQuality.EXCELLENT
    elif score >= 65:
        quality = MuhurtaQuality.GOOD
    elif score >= 45:
        quality = MuhurtaQuality.FAIR
    else:
        quality = MuhurtaQuality.POOR

    recommendation = _generate_recommendation(quality, activity)

    return {
        "activity": activity,
        "score": score,
        "quality": quality.value,
        "favorable_factors": favorable,
        "unfavorable_factors": unfavorable,
        "recommendation": recommendation,
        "evaluated_at": datetime_obj,
    }


def _generate_recommendation(quality: MuhurtaQuality, activity: str) -> str:
    """Generate a recommendation text based on quality and activity.

    Args:
        quality: The MuhurtaQuality level
        activity: The activity type

    Returns:
        Recommendation string
    """
    activity_friendly = activity.replace("_", " ").title()

    if quality == MuhurtaQuality.EXCELLENT:
        return (
            f"Excellent Muhurta for {activity_friendly}. "
            f"This is a highly auspicious time. Proceed with confidence."
        )
    elif quality == MuhurtaQuality.GOOD:
        return (
            f"Good Muhurta for {activity_friendly}. "
            f"This is a favorable time with positive indicators."
        )
    elif quality == MuhurtaQuality.FAIR:
        return (
            f"Fair Muhurta for {activity_friendly}. "
            f"Proceed but be aware of some unfavorable factors. "
            f"Consider waiting for a better time if possible."
        )
    else:
        return (
            f"Poor Muhurta for {activity_friendly}. "
            f"Multiple unfavorable factors present. "
            f"Strongly recommended to wait for a better time."
        )


def evaluate_with_inauspicious_check(
    activity: str,
    panchanga: dict[str, Any],
    datetime_obj: datetime,
    sunrise: datetime,
    sunset: datetime,
    weekday: str,
) -> dict[str, Any]:
    """Evaluate Muhurta including inauspicious period checks.

    Performs the standard Muhurta evaluation and also checks if the
    datetime falls within Rahu Kaal, Yamaghanda, or Gulika.

    Args:
        activity: Type of activity
        panchanga: Panchanga data (Tithi, Nakshatra, etc.)
        datetime_obj: The datetime to evaluate
        sunrise: Sunrise time for the day
        sunset: Sunset time for the day
        weekday: Day of the week

    Returns:
        Dictionary with standard evaluation fields plus:
        - in_rahu_kaal: Boolean
        - in_yamaghanda: Boolean
        - in_gulika: Boolean
        - inauspicious_periods: List of active inauspicious periods
    """
    # Get standard evaluation
    evaluation = evaluate_muhurta(activity, panchanga, datetime_obj)

    # Check inauspicious periods
    inauspicious = calculate_all_inauspicious(sunrise, sunset, weekday)

    in_rahu_kaal = inauspicious["rahu_kaal"]["is_active"](datetime_obj)
    in_yamaghanda = inauspicious["yamaghanda"]["is_active"](datetime_obj)
    in_gulika = inauspicious["gulika"]["is_active"](datetime_obj)

    active_periods = []
    if in_rahu_kaal:
        active_periods.append("Rahu Kaal")
        evaluation["score"] -= 20
    if in_yamaghanda:
        active_periods.append("Yamaghanda")
        evaluation["score"] -= 25
    if in_gulika:
        active_periods.append("Gulika")
        evaluation["score"] -= 10

    if active_periods:
        evaluation["unfavorable_factors"].extend(
            [f"Active inauspicious period: {p}" for p in active_periods]
        )
        evaluation["recommendation"] = (
            f"AVOID THIS TIME: {', '.join(active_periods)} is active. "
            f"Choose a different time for {activity.replace('_', ' ').title()}."
        )

    # Ensure score stays within bounds
    evaluation["score"] = min(100, max(0, evaluation["score"]))

    # Recalculate quality if score changed significantly
    if active_periods:
        if evaluation["score"] >= 80:
            evaluation["quality"] = MuhurtaQuality.EXCELLENT.value
        elif evaluation["score"] >= 65:
            evaluation["quality"] = MuhurtaQuality.GOOD.value
        elif evaluation["score"] >= 45:
            evaluation["quality"] = MuhurtaQuality.FAIR.value
        else:
            evaluation["quality"] = MuhurtaQuality.POOR.value

    evaluation["in_rahu_kaal"] = in_rahu_kaal
    evaluation["in_yamaghanda"] = in_yamaghanda
    evaluation["in_gulika"] = in_gulika
    evaluation["inauspicious_periods"] = active_periods

    return evaluation


def find_next_good_muhurta(
    activity: str,
    start_date: datetime,
    panchanga_calculator: Callable,
    sunrise_sunset_calculator: Callable,
    days_to_search: int = 30,
    max_results: int = 5,
    min_quality: str = "good",
) -> list[dict[str, Any]]:
    """Find upcoming good Muhurtas for a specific activity.

    Searches forward from start_date to find the best available times
    for performing an activity.

    Args:
        activity: The activity type (e.g., "marriage", "travel")
        start_date: Date to begin search from (datetime)
        panchanga_calculator: Callable that returns panchanga for a datetime
            signature: panchanga_calculator(datetime) -> dict
        sunrise_sunset_calculator: Callable that returns sunrise/sunset
            signature: sunrise_sunset_calculator(date) -> {"sunrise": dt, "sunset": dt}
        days_to_search: Number of days to search ahead (default 30)
        max_results: Maximum results to return (default 5)
        min_quality: Minimum quality to include ("excellent", "good", "fair", "poor")

    Returns:
        List of dictionaries, each containing:
        - date: The auspicious date
        - score: Muhurta score (0-100)
        - quality: Quality level
        - favorable_factors: List of positive indicators
        - unfavorable_factors: List of negative factors
        - recommendation: Recommendation text

    Raises:
        ValueError: If min_quality is not a valid quality level
    """
    quality_levels = ["excellent", "good", "fair", "poor"]
    if min_quality not in quality_levels:
        raise ValueError(f"min_quality must be one of: {', '.join(quality_levels)}")

    min_quality_score = {"excellent": 80, "good": 65, "fair": 45, "poor": 0}[min_quality]

    good_muhurtas = []
    current = start_date

    for _ in range(days_to_search):
        try:
            # Get panchanga for current date
            panchanga = panchanga_calculator(current)

            # Get sunrise/sunset for the day
            sun_times = sunrise_sunset_calculator(current.date())
            sunrise = sun_times["sunrise"]
            sunset = sun_times["sunset"]

            # Get weekday
            weekday = current.strftime("%A").lower()

            # Evaluate muhurta with inauspicious checks
            evaluation = evaluate_with_inauspicious_check(
                activity, panchanga, current, sunrise, sunset, weekday
            )

            if evaluation["score"] >= min_quality_score:
                good_muhurtas.append(
                    {
                        "date": current,
                        "score": evaluation["score"],
                        "quality": evaluation["quality"],
                        "favorable_factors": evaluation["favorable_factors"],
                        "unfavorable_factors": evaluation["unfavorable_factors"],
                        "recommendation": evaluation["recommendation"],
                    }
                )

                if len(good_muhurtas) >= max_results:
                    break

        except Exception:
            # Skip dates that cause calculation errors
            pass

        current += timedelta(days=1)

    # Sort by score (descending)
    return sorted(good_muhurtas, key=lambda x: x["score"], reverse=True)


def get_choghadiya_at_time(
    sunrise: datetime,
    sunset: datetime,
    weekday: str,
    query_time: datetime,
    is_night: bool = False,
) -> dict[str, Any] | None:
    """Get the Choghadiya period active at a specific time.

    Args:
        sunrise: Sunrise time for the day
        sunset: Sunset time for the day
        weekday: Day of the week
        query_time: The time to check
        is_night: Whether to check night Choghadiya (default False for day)

    Returns:
        Dictionary with Choghadiya details if found, None otherwise
    """
    choghadiyas = calculate_choghadiya(sunrise, sunset, weekday, is_night=is_night)

    for choghadiya in choghadiyas:
        if choghadiya["start"] <= query_time <= choghadiya["end"]:
            return choghadiya

    return None


def validate_muhurta_input(panchanga: dict[str, Any]) -> bool:
    """Validate that panchanga data contains required fields.

    Args:
        panchanga: Panchanga dictionary to validate

    Returns:
        True if all required fields are present

    Raises:
        KeyError: If required fields are missing
    """
    required_fields = {
        "tithi": ["number", "name"],
        "nakshatra": ["number", "name"],
        "yoga": ["number", "name"],
        "vara": ["number", "name"],
    }

    for field, subfields in required_fields.items():
        if field not in panchanga:
            raise KeyError(f"Missing required panchanga field: {field}")

        for subfield in subfields:
            if subfield not in panchanga[field]:
                raise KeyError(f"Missing required subfield: {field}.{subfield}")

    return True
