"""Kalachakra Dasha — BPHS Chapter 46.

Sign-based dasha system using navamsha (D-9) positions.
Two sequences: Savya (clockwise) and Apasavya (counter-clockwise).
Based on the Moon's nakshatra pada at birth.

The Kalachakra Dasha is a 173-year cycle that uses the Moon's navamsha position
as the starting point, with direction determined by the Moon's nakshatra.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

SIGNS = [
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
SIGN_TO_INDEX = {s.lower(): i for i, s in enumerate(SIGNS)}

NAKSHATRA_NAMES = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishtha",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

# Savya nakshatras (forward sequence) - specific BPHS list
# Ashwini(1), Mrigashira(5), Punarvasu(7), Pushya(8), Uttara Phalguni(12),
# Hasta(13), Anuradha(17), Uttara Ashadha(21), Shravana(22),
# Uttara Bhadrapada(26), Revati(27)
SAVYA_NAKSHATRAS = {0, 4, 6, 7, 11, 12, 16, 20, 21, 25, 26}  # 0-indexed

SAVYA_SEQUENCE = [
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

APASAVYA_SEQUENCE = [
    "Pisces",
    "Aquarius",
    "Capricorn",
    "Sagittarius",
    "Scorpio",
    "Libra",
    "Virgo",
    "Leo",
    "Cancer",
    "Gemini",
    "Taurus",
    "Aries",
]

DASHA_YEARS = {
    "Aries": 7,
    "Taurus": 16,
    "Gemini": 9,
    "Cancer": 21,
    "Leo": 5,
    "Virgo": 9,
    "Libra": 19,
    "Scorpio": 15,
    "Sagittarius": 12,
    "Capricorn": 27,
    "Aquarius": 21,
    "Pisces": 12,
}

TOTAL_CYCLE_YEARS = sum(DASHA_YEARS.values())  # 173 years


def _get_navamsha_sign(longitude: float) -> str:
    """Get navamsha sign for a longitude.

    Navamsha calculation: Each sign divided into 9 parts.
    For each sign, the navamsha sequence depends on the element.
    """
    lon = longitude % 360
    sign_idx = int(lon / 30)
    degree_in_sign = lon % 30
    nav_num = min(int(degree_in_sign / (30 / 9)), 8)
    element = sign_idx % 4  # 0=fire,1=earth,2=air,3=water
    start = [0, 9, 6, 3][element]  # Starting navamsha for each element
    return SIGNS[(start + nav_num) % 12]


def _get_nakshatra_index(longitude: float) -> tuple[int, int]:
    """Return (nakshatra_index_0, pada_index_0) for a longitude."""
    lon = longitude % 360
    nak_size = 360 / 27
    nak_idx = min(int(lon / nak_size), 26)
    degree_in_nak = lon % nak_size
    pada_idx = min(int(degree_in_nak / (nak_size / 4)), 3)
    return nak_idx, pada_idx


def _is_savya(moon_longitude: float) -> bool:
    """Determine if Moon's nakshatra is Savya (forward) or Apasavya (backward)."""
    nak_idx, _ = _get_nakshatra_index(moon_longitude)
    return nak_idx in SAVYA_NAKSHATRAS


def _get_elapsed_fraction(moon_longitude: float) -> float:
    """Get fraction of current navamsha already elapsed (for balance calc)."""
    lon = moon_longitude % 360
    degree_in_sign = lon % 30
    nav_num = min(int(degree_in_sign / (30 / 9)), 8)
    nav_start = nav_num * (30 / 9)
    nav_elapsed = degree_in_sign - nav_start
    return nav_elapsed / (30 / 9)  # 0.0 to 1.0


def get_kalachakra_dasha_periods(
    birth_datetime: str,
    moon_longitude: float,
    query_datetime: str | None = None,
    periods_count: int = 12,
) -> dict[str, Any]:
    """
    Calculate Kalachakra Dasha periods.

    Args:
        birth_datetime: ISO birth datetime
        moon_longitude: Moon's sidereal longitude at birth
        query_datetime: Date to check (default: now)
        periods_count: Number of dasha periods to return

    Returns:
        Current and upcoming Kalachakra Dasha periods with dates
    """
    # Parse birth datetime
    if "+" in birth_datetime or birth_datetime.endswith("Z"):
        birth_dt = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        birth_dt = birth_dt.replace(tzinfo=None)  # strip tz for naive arithmetic
    else:
        birth_dt = datetime.fromisoformat(birth_datetime)

    query_dt = datetime.now()
    if query_datetime:
        try:
            q = datetime.fromisoformat(query_datetime.replace("Z", "+00:00"))
            query_dt = q.replace(tzinfo=None)
        except Exception:
            query_dt = datetime.now()

    # Determine direction and starting sign
    is_savya = _is_savya(moon_longitude)
    sequence = SAVYA_SEQUENCE if is_savya else APASAVYA_SEQUENCE
    direction = "Savya (forward)" if is_savya else "Apasavya (backward)"

    # Starting sign = Moon's navamsha sign
    start_sign = _get_navamsha_sign(moon_longitude)
    try:
        start_idx_in_seq = sequence.index(start_sign)
    except ValueError:
        start_idx_in_seq = 0  # fallback

    # Balance: fraction already elapsed of first dasha
    elapsed_fraction = _get_elapsed_fraction(moon_longitude)
    first_sign = sequence[start_idx_in_seq]
    first_dasha_years = DASHA_YEARS[first_sign]
    balance_years = first_dasha_years * (1 - elapsed_fraction)

    # Generate all periods
    all_periods = []
    current_start = birth_dt
    seq_len = len(sequence)

    # First period (partial)
    first_end = current_start + timedelta(days=balance_years * 365.25)
    all_periods.append(
        {
            "sign": first_sign,
            "start_date": current_start.isoformat(),
            "end_date": first_end.isoformat(),
            "years": round(balance_years, 3),
            "total_years": first_dasha_years,
            "is_partial": True,
        }
    )
    current_start = first_end

    # Subsequent full periods
    for i in range(1, periods_count + 5):  # extra periods for safety
        seq_idx = (start_idx_in_seq + i) % seq_len
        sign = sequence[seq_idx]
        years = DASHA_YEARS[sign]
        end_dt = current_start + timedelta(days=years * 365.25)
        all_periods.append(
            {
                "sign": sign,
                "start_date": current_start.isoformat(),
                "end_date": end_dt.isoformat(),
                "years": years,
                "total_years": years,
                "is_partial": False,
            }
        )
        current_start = end_dt

    # Find current dasha
    current_period = None
    for period in all_periods:
        start = datetime.fromisoformat(period["start_date"])
        end = datetime.fromisoformat(period["end_date"])
        if start <= query_dt <= end:
            elapsed_days = (query_dt - start).days
            total_days = (end - start).days
            period["elapsed_years"] = round(elapsed_days / 365.25, 2)
            period["remaining_years"] = round((total_days - elapsed_days) / 365.25, 2)
            current_period = period
            break

    # Filter to show requested count
    relevant = all_periods[:periods_count]

    return {
        "success": True,
        "system": "Kalachakra Dasha",
        "source": "BPHS Chapter 46",
        "direction": direction,
        "moon_navamsha_sign": start_sign,
        "total_cycle_years": TOTAL_CYCLE_YEARS,
        "current_dasha": current_period,
        "all_periods": relevant,
        "moon_longitude": moon_longitude,
        "note": "Kalachakra Dasha is sign-based, using Moon's navamsha as starting point",
    }


def get_kalachakra_antardasha(mahadasha_period: dict) -> list[dict]:
    """Calculate antardasha periods within a Kalachakra mahadasha.

    Uses the same sequence as the mahadasha, with proportional durations.

    Args:
        mahadasha_period: Dict with sign, start_date, end_date from get_kalachakra_dasha_periods

    Returns:
        List of 12 antardasha periods with sign, start_date, end_date
    """
    start_dt = datetime.fromisoformat(mahadasha_period["start_date"])
    end_dt = datetime.fromisoformat(mahadasha_period["end_date"])
    total_days = (end_dt - start_dt).days

    # Get the mahadasha sign's position in the sequence
    maha_sign = mahadasha_period["sign"]

    # Use the same direction logic - for simplicity, use Savya sequence
    # In a full implementation, this would need to track the original direction
    sequence = SAVYA_SEQUENCE
    try:
        start_idx = sequence.index(maha_sign)
    except ValueError:
        start_idx = 0

    antardashas = []
    current_date = start_dt

    # Create 12 antardashas (all signs)
    for i in range(12):
        sign_idx = (start_idx + i) % 12
        sign = sequence[sign_idx]
        sign_years = DASHA_YEARS[sign]

        # Proportional duration
        ad_days = int((sign_years / TOTAL_CYCLE_YEARS) * total_days)
        ad_end = current_date + timedelta(days=ad_days)

        # Ensure we don't exceed the mahadasha end
        if ad_end > end_dt:
            ad_end = end_dt

        antardashas.append(
            {
                "sign": sign,
                "start_date": current_date.isoformat(),
                "end_date": ad_end.isoformat(),
                "years": round(sign_years * (total_days / (TOTAL_CYCLE_YEARS * 365.25)), 3),
            }
        )

        current_date = ad_end
        if current_date >= end_dt:
            break

    return antardashas


def get_current_kalachakra_dasha(
    birth_datetime: str,
    moon_longitude: float,
    query_datetime: str | None = None,
) -> dict[str, Any]:
    """Get current Kalachakra Dasha information.

    Args:
        birth_datetime: Birth datetime ISO string
        moon_longitude: Moon's sidereal longitude at birth
        query_datetime: Query date (defaults to now)

    Returns:
        Current Kalachakra Dasha period with timing details
    """
    result = get_kalachakra_dasha_periods(birth_datetime, moon_longitude, query_datetime, 20)

    if result["current_dasha"] is None:
        # Find the closest period if no exact match
        query_dt = datetime.now()
        if query_datetime:
            try:
                q = datetime.fromisoformat(query_datetime.replace("Z", "+00:00"))
                query_dt = q.replace(tzinfo=None)
            except Exception:
                pass

        # Return the first period that hasn't ended yet
        for period in result["all_periods"]:
            end_dt = datetime.fromisoformat(period["end_date"])
            if end_dt > query_dt:
                result["current_dasha"] = period
                break

    return {
        "success": result["success"],
        "system": "Kalachakra Dasha",
        "current_dasha": result["current_dasha"],
        "direction": result["direction"],
        "moon_navamsha_sign": result["moon_navamsha_sign"],
        "note": "Based on Moon's navamsha position and nakshatra direction",
    }


def get_kalachakra_effects(sign: str) -> dict[str, Any]:
    """Get interpretation effects for a Kalachakra Dasha sign period.

    Args:
        sign: Sign name (e.g., "Aries", "Taurus")

    Returns:
        Dictionary with effects and characteristics for the sign
    """
    effects_map = {
        "Aries": {
            "element": "Fire",
            "nature": "Movable",
            "lord": "Mars",
            "general": "Initiative, new beginnings, pioneering efforts, leadership",
            "positive": [
                "Quick action and results",
                "Leadership opportunities",
                "Courage and confidence",
                "Innovation and enterprise",
            ],
            "negative": [
                "Impulsive decisions",
                "Aggression and impatience",
                "Burnout from rushing",
                "Conflicts with authority",
            ],
            "areas": [
                "Career advancement",
                "Physical activities",
                "New ventures",
                "Competitive endeavors",
            ],
        },
        "Taurus": {
            "element": "Earth",
            "nature": "Fixed",
            "lord": "Venus",
            "general": "Stability, material accumulation, sensual pleasures, persistence",
            "positive": [
                "Financial gains and security",
                "Artistic achievements",
                "Stable relationships",
                "Property acquisition",
            ],
            "negative": [
                "Stubbornness and resistance to change",
                "Over-indulgence",
                "Material obsession",
                "Sluggishness",
            ],
            "areas": [
                "Wealth building",
                "Art and beauty",
                "Comfort and luxury",
                "Agricultural pursuits",
            ],
        },
        "Gemini": {
            "element": "Air",
            "nature": "Dual",
            "lord": "Mercury",
            "general": "Communication, versatility, learning, networking",
            "positive": [
                "Intellectual growth",
                "Communication success",
                "Travel opportunities",
                "Social connections",
            ],
            "negative": [
                "Inconsistency and scattered focus",
                "Nervous tension",
                "Superficial relationships",
                "Information overload",
            ],
            "areas": [
                "Education and learning",
                "Writing and media",
                "Business and trade",
                "Technology",
            ],
        },
        "Cancer": {
            "element": "Water",
            "nature": "Movable",
            "lord": "Moon",
            "general": "Emotions, nurturing, home, public connection",
            "positive": [
                "Family harmony",
                "Emotional fulfillment",
                "Public recognition",
                "Property gains",
            ],
            "negative": [
                "Mood swings",
                "Over-sensitivity",
                "Clinging behavior",
                "Past-focused thinking",
            ],
            "areas": ["Home and family", "Real estate", "Food and hospitality", "Public service"],
        },
        "Leo": {
            "element": "Fire",
            "nature": "Fixed",
            "lord": "Sun",
            "general": "Authority, recognition, creativity, self-expression",
            "positive": [
                "Leadership roles",
                "Creative success",
                "Recognition and fame",
                "Confidence boost",
            ],
            "negative": [
                "Ego conflicts",
                "Pride and arrogance",
                "Demanding nature",
                "Heart-related issues",
            ],
            "areas": [
                "Government and politics",
                "Entertainment",
                "Education",
                "Spiritual leadership",
            ],
        },
        "Virgo": {
            "element": "Earth",
            "nature": "Dual",
            "lord": "Mercury",
            "general": "Service, health, details, practical skills",
            "positive": [
                "Health improvement",
                "Skill development",
                "Service opportunities",
                "Analytical success",
            ],
            "negative": [
                "Over-criticism",
                "Perfectionism stress",
                "Health anxieties",
                "Nitpicking",
            ],
            "areas": [
                "Health and healing",
                "Service industries",
                "Research and analysis",
                "Agriculture",
            ],
        },
        "Libra": {
            "element": "Air",
            "nature": "Movable",
            "lord": "Venus",
            "general": "Balance, partnerships, harmony, justice",
            "positive": [
                "Successful partnerships",
                "Legal victories",
                "Aesthetic achievements",
                "Social harmony",
            ],
            "negative": [
                "Indecisiveness",
                "Relationship dependencies",
                "Compromise of values",
                "Superficial connections",
            ],
            "areas": ["Legal matters", "Partnerships", "Arts and design", "Diplomacy"],
        },
        "Scorpio": {
            "element": "Water",
            "nature": "Fixed",
            "lord": "Mars/Ketu",
            "general": "Transformation, research, hidden knowledge, intensity",
            "positive": [
                "Deep research success",
                "Transformation and healing",
                "Hidden wealth discovery",
                "Spiritual insights",
            ],
            "negative": [
                "Obsessive behavior",
                "Secretive nature",
                "Power struggles",
                "Emotional extremes",
            ],
            "areas": [
                "Research and investigation",
                "Occult sciences",
                "Psychology",
                "Mining and resources",
            ],
        },
        "Sagittarius": {
            "element": "Fire",
            "nature": "Dual",
            "lord": "Jupiter",
            "general": "Wisdom, teaching, travel, philosophy",
            "positive": [
                "Higher learning",
                "Spiritual growth",
                "Long-distance success",
                "Teaching opportunities",
            ],
            "negative": [
                "Over-optimism",
                "Dogmatic thinking",
                "Restlessness",
                "Cultural conflicts",
            ],
            "areas": [
                "Education and teaching",
                "Publishing",
                "Foreign trade",
                "Religious activities",
            ],
        },
        "Capricorn": {
            "element": "Earth",
            "nature": "Movable",
            "lord": "Saturn",
            "general": "Discipline, authority, patience, long-term goals",
            "positive": [
                "Career advancement",
                "Authority positions",
                "Long-term success",
                "Disciplined achievement",
            ],
            "negative": [
                "Delays and obstacles",
                "Cold and calculating nature",
                "Overwork",
                "Isolation",
            ],
            "areas": [
                "Government service",
                "Large organizations",
                "Mining and construction",
                "Elderly care",
            ],
        },
        "Aquarius": {
            "element": "Air",
            "nature": "Fixed",
            "lord": "Saturn/Rahu",
            "general": "Innovation, groups, humanitarian causes, unconventional thinking",
            "positive": [
                "Group achievements",
                "Technological success",
                "Humanitarian recognition",
                "Innovation rewards",
            ],
            "negative": [
                "Eccentric behavior",
                "Detachment from emotions",
                "Rebellious conflicts",
                "Unpredictable changes",
            ],
            "areas": [
                "Technology and innovation",
                "Social causes",
                "Group activities",
                "Scientific research",
            ],
        },
        "Pisces": {
            "element": "Water",
            "nature": "Dual",
            "lord": "Jupiter/Ketu",
            "general": "Spirituality, imagination, compassion, dissolution",
            "positive": [
                "Spiritual awakening",
                "Artistic inspiration",
                "Compassionate service",
                "Intuitive insights",
            ],
            "negative": [
                "Confusion and illusion",
                "Escapist tendencies",
                "Emotional overwhelm",
                "Lack of boundaries",
            ],
            "areas": [
                "Spiritual practices",
                "Arts and music",
                "Healthcare",
                "Water-related activities",
            ],
        },
    }

    return effects_map.get(sign, {})
