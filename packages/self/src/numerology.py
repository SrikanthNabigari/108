"""Numerology calculator for 108 Vedic Astrology system.

Implements both Chaldean (primary for Vedic) and Pythagorean (Western)
numerology systems with Lo Shu grid analysis, personal cycles,
pinnacle/challenge numbers, compatibility, and Jyotish cross-referencing.

Core numbers:
- Psychic Number (Driver): day of birth reduced to 1-9
- Destiny Number (Life Path): full DOB reduced to 1-9
- Name Number: name converted via letter-number mapping and reduced

References:
- Cheiro's Book of Numbers
- Harish Johari - Numerology with Tantra, Ayurveda, and Astrology
- Sepharial - The Kabala of Numbers
"""

from __future__ import annotations

import contextlib
import logging
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Chaldean letter-to-number mapping (primary for Vedic numerology)
CHALDEAN_MAP: dict[str, int] = {
    "A": 1,
    "I": 1,
    "J": 1,
    "Q": 1,
    "Y": 1,
    "B": 2,
    "K": 2,
    "R": 2,
    "C": 3,
    "G": 3,
    "L": 3,
    "S": 3,
    "D": 4,
    "M": 4,
    "T": 4,
    "E": 5,
    "H": 5,
    "N": 5,
    "X": 5,
    "U": 6,
    "V": 6,
    "W": 6,
    "O": 7,
    "Z": 7,
    "F": 8,
    "P": 8,
}

# Pythagorean system (Western)
PYTHAGOREAN_MAP: dict[str, int] = {
    "A": 1,
    "J": 1,
    "S": 1,
    "B": 2,
    "K": 2,
    "T": 2,
    "C": 3,
    "L": 3,
    "U": 3,
    "D": 4,
    "M": 4,
    "V": 4,
    "E": 5,
    "N": 5,
    "W": 5,
    "F": 6,
    "O": 6,
    "X": 6,
    "G": 7,
    "P": 7,
    "Y": 7,
    "H": 8,
    "Q": 8,
    "Z": 8,
    "I": 9,
    "R": 9,
}

# Vedic planet mapping for each number
NUMBER_PLANET_MAP: dict[int, str] = {
    1: "sun",
    2: "moon",
    3: "jupiter",
    4: "rahu",
    5: "mercury",
    6: "venus",
    7: "ketu",
    8: "saturn",
    9: "mars",
}

# Lo Shu magic square layout (traditional 3x3)
LO_SHU_GRID: list[list[int]] = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
]

# Lo Shu grid position names mapped to (row, col)
LO_SHU_POSITIONS: dict[int, tuple[int, int]] = {
    4: (0, 0),
    9: (0, 1),
    2: (0, 2),
    3: (1, 0),
    5: (1, 1),
    7: (1, 2),
    8: (2, 0),
    1: (2, 1),
    6: (2, 2),
}

# Arrows of strength/weakness in Lo Shu grid
LO_SHU_ARROWS: dict[str, list[int]] = {
    "determination": [1, 5, 9],
    "compassion": [3, 5, 7],
    "intellect": [3, 6, 9],
    "spirituality": [2, 5, 8],
    "planner": [1, 2, 3],
    "willpower": [4, 5, 6],
    "activity": [7, 8, 9],
}

# Lo Shu plane groupings for dominant plane detection
_LO_SHU_PLANES: dict[str, list[int]] = {
    "mental": [4, 9, 2],  # top row
    "emotional": [3, 5, 7],  # middle row
    "practical": [8, 1, 6],  # bottom row
}

# Master numbers that are significant before final reduction
MASTER_NUMBERS: set[int] = {11, 22, 33}

# Vowels for soul urge calculations
_VOWELS: set[str] = {"A", "E", "I", "O", "U"}

# Compatibility matrix: (num1, num2) -> (score, nature)
# Symmetric - only store once with min,max ordering
_COMPATIBILITY_MATRIX: dict[tuple[int, int], tuple[int, str]] = {
    (1, 1): (70, "neutral"),
    (1, 2): (60, "moderate"),
    (1, 3): (85, "excellent"),
    (1, 4): (50, "challenging"),
    (1, 5): (80, "good"),
    (1, 6): (75, "good"),
    (1, 7): (55, "moderate"),
    (1, 8): (40, "difficult"),
    (1, 9): (90, "excellent"),
    (2, 2): (65, "neutral"),
    (2, 3): (70, "good"),
    (2, 4): (45, "challenging"),
    (2, 5): (75, "good"),
    (2, 6): (80, "excellent"),
    (2, 7): (85, "excellent"),
    (2, 8): (40, "difficult"),
    (2, 9): (70, "good"),
    (3, 3): (75, "good"),
    (3, 4): (45, "challenging"),
    (3, 5): (80, "excellent"),
    (3, 6): (90, "excellent"),
    (3, 7): (60, "moderate"),
    (3, 8): (50, "challenging"),
    (3, 9): (85, "excellent"),
    (4, 4): (55, "moderate"),
    (4, 5): (60, "moderate"),
    (4, 6): (70, "good"),
    (4, 7): (50, "challenging"),
    (4, 8): (80, "excellent"),
    (4, 9): (45, "challenging"),
    (5, 5): (65, "neutral"),
    (5, 6): (75, "good"),
    (5, 7): (60, "moderate"),
    (5, 8): (55, "moderate"),
    (5, 9): (80, "good"),
    (6, 6): (70, "neutral"),
    (6, 7): (55, "moderate"),
    (6, 8): (75, "good"),
    (6, 9): (85, "excellent"),
    (7, 7): (60, "neutral"),
    (7, 8): (45, "challenging"),
    (7, 9): (50, "challenging"),
    (8, 8): (55, "neutral"),
    (8, 9): (50, "challenging"),
    (9, 9): (75, "good"),
}

# Psychic-Destiny harmony table
_PSYCHIC_DESTINY_HARMONY: dict[tuple[int, int], str] = {}

# Populate harmony table from compatibility + planet friendships
for _k, (_s, _n) in _COMPATIBILITY_MATRIX.items():
    _harmony = "high" if _s >= 75 else ("medium" if _s >= 55 else "low")
    _PSYCHIC_DESTINY_HARMONY[_k] = _harmony
    # Symmetric
    if _k[0] != _k[1]:
        _PSYCHIC_DESTINY_HARMONY[(_k[1], _k[0])] = _harmony

# Number meaning summaries (used in personal cycle descriptions)
_NUMBER_MEANINGS: dict[int, str] = {
    1: "New beginnings, leadership, independence. Time to initiate projects and assert yourself.",
    2: "Cooperation, patience, diplomacy. Focus on partnerships and emotional balance.",
    3: "Creativity, expression, expansion. Social opportunities and artistic growth.",
    4: "Foundation, discipline, hard work. Build structures and attend to practical matters.",
    5: "Change, freedom, adventure. Travel, new experiences, and breaking old patterns.",
    6: "Responsibility, love, domestic harmony. Family obligations and nurturing relationships.",
    7: "Introspection, spirituality, analysis. Inner growth, study, and solitude benefit you.",
    8: "Power, achievement, material success. Career advancement and financial decisions.",
    9: "Completion, humanitarianism, wisdom. Let go of the old, prepare for transformation.",
}

# Compound number interpretations (key compounds)
_COMPOUND_MEANINGS: dict[int, str] = {
    10: "Wheel of Fortune - success and rise in life, all-or-nothing energy.",
    11: "Master Number - hidden dangers, treachery from others, high spiritual potential.",
    12: "Sacrifice - the victim, anxiety, suffering that leads to spiritual growth.",
    13: "Transformation - upheaval, power through regeneration, not unlucky in Vedic tradition.",
    14: "Temperance - movement, travel, risk from natural forces and speculation.",
    15: "The Magician - eloquence, gifts of music/art, charisma, but temptation risk.",
    16: "The Tower - sudden downfall, accidents, danger from love affairs and overconfidence.",
    17: "The Star - spirituality, immortality, peace, excellent for lasting fame.",
    18: "Conflict - family quarrels, deception, war energy, courage under fire.",
    19: "The Sun Prince - success, happiness, honor, fulfillment of ambitions.",
    20: "Awakening - delay but eventual success, spiritual calling, judgment day.",
    21: "The Universe - advancement, honors, elevation, success after long effort.",
    22: "Master Builder - grand plans, illusion vs reality, unreliable associates.",
    23: "The Royal Star - help from superiors, success through others, protection.",
    24: "Love and creativity - favorable for love, gain through opposite gender.",
    25: "Discrimination - strength through trials, early struggles lead to wisdom.",
    26: "Partnerships - warnings about partnerships, trust issues, eventual gain.",
    27: "The Scepter - command, authority, reward for merit, creative power.",
    28: "The Trusting Lamb - great promise lost to others, legal issues, start again.",
    29: "Grace Under Pressure - extremes of fortune, uncertainties, spiritual tests.",
    30: "The Loner - retrospection, mental superiority, indifference to material.",
    31: "The Recluse - lonely, self-contained, similar to 30 but more isolated.",
    33: "Master Teacher - selfless service, cosmic consciousness, high spiritual mission.",
}


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------


class NumerologyProfile(BaseModel):
    """Complete numerology profile for a person."""

    psychic_number: int = Field(ge=1, le=9, description="Birth day reduced (driver number)")
    destiny_number: int = Field(ge=1, le=9, description="Full DOB reduced (life path)")
    name_number: int | None = Field(
        default=None, ge=1, le=9, description="Name reduced via Chaldean"
    )
    name_number_pythagorean: int | None = Field(default=None, ge=1, le=9)
    compound_psychic: int | None = Field(default=None, description="Unreduced birth day (10-31)")
    compound_destiny: int | None = Field(default=None, description="Unreduced DOB sum")
    compound_name: int | None = Field(default=None, description="Unreduced name sum")
    psychic_planet: str = Field(description="Vedic planet ruling psychic number")
    destiny_planet: str = Field(description="Vedic planet ruling destiny number")
    name_planet: str | None = Field(default=None)
    master_numbers_found: list[int] = Field(
        default_factory=list, description="11, 22, 33 found before reduction"
    )
    personal_year: int = Field(ge=1, le=9)
    personal_month: int = Field(ge=1, le=9)
    personal_day: int = Field(ge=1, le=9)
    lo_shu_grid: dict[str, Any] = Field(description="Lo Shu grid analysis")
    missing_numbers: list[int] = Field(description="Numbers absent from DOB")
    repeated_numbers: dict[int, int] = Field(description="Number -> count for numbers appearing 2+")
    psychic_destiny_harmony: str = Field(
        description="high/medium/low harmony between psychic and destiny"
    )


class NameAnalysis(BaseModel):
    """Analysis of a name's numerological value."""

    full_name: str
    chaldean_value: int
    chaldean_reduced: int
    pythagorean_value: int
    pythagorean_reduced: int
    ruling_planet: str
    letter_breakdown: list[dict[str, Any]]


class PersonalCycles(BaseModel):
    """Personal year/month/day cycles."""

    personal_year: int
    personal_month: int
    personal_day: int
    year_planet: str
    month_planet: str
    day_planet: str
    year_meaning: str
    pinnacle_number: int
    challenge_number: int


class NumberCompatibility(BaseModel):
    """Compatibility between two numbers."""

    number_1: int
    number_2: int
    score: int = Field(ge=0, le=100)
    nature: str
    description: str
    planet_1: str
    planet_2: str


class LoShuGrid(BaseModel):
    """Lo Shu magic square analysis."""

    grid: list[list[dict[str, Any]]]
    present_numbers: list[int]
    missing_numbers: list[int]
    repeated_numbers: dict[int, int]
    arrows_present: list[str]
    arrows_missing: list[str]
    dominant_plane: str | None


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def _sum_digits(n: int) -> int:
    """Sum all digits of a non-negative integer."""
    return sum(int(d) for d in str(abs(n)))


def _get_date_digits(birth_date: date) -> list[int]:
    """Extract all individual digits from a date (DD+MM+YYYY).

    Zeros are skipped since they do not appear in the Lo Shu grid (1-9).
    """
    date_str = birth_date.strftime("%d%m%Y")
    return [int(d) for d in date_str if d != "0"]


def _get_all_date_digits(birth_date: date) -> list[int]:
    """Extract all individual digits from a date including zeros."""
    date_str = birth_date.strftime("%d%m%Y")
    return [int(d) for d in date_str]


# ---------------------------------------------------------------------------
# Core Calculation Functions
# ---------------------------------------------------------------------------


def reduce_to_single(n: int, respect_master: bool = True) -> tuple[int, int | None, list[int]]:
    """Reduce any number to a single digit (1-9) by summing digits repeatedly.

    Args:
        n: The number to reduce.
        respect_master: If True, records master numbers (11, 22, 33)
                        encountered during reduction.

    Returns:
        Tuple of (reduced_number, compound_or_None, master_numbers_found).
        If n is already 1-9, compound is None.
        If n >= 10, compound is the original value of n.
    """
    if n < 0:
        n = abs(n)

    compound = n if n >= 10 else None
    masters_found: list[int] = []
    current = n

    while current > 9:
        if respect_master and current in MASTER_NUMBERS:
            masters_found.append(current)
        current = _sum_digits(current)

    return current, compound, masters_found


def calculate_psychic_number(birth_day: int) -> tuple[int, int | None]:
    """Calculate the Psychic (Driver) number from the day of birth.

    The psychic number reveals personality, how you see yourself, and
    your natural tendencies. It is the most personal number.

    Args:
        birth_day: Day of birth (1-31).

    Returns:
        Tuple of (psychic_number 1-9, compound_number or None).

    Raises:
        ValueError: If birth_day is not in 1-31 range.
    """
    if not 1 <= birth_day <= 31:
        raise ValueError(f"birth_day must be 1-31, got {birth_day}")

    if birth_day <= 9:
        return birth_day, None

    # For double-digit days, sum digits until single
    compound = birth_day
    result = _sum_digits(birth_day)
    while result > 9:
        result = _sum_digits(result)
    return result, compound


def calculate_destiny_number(birth_date: date) -> tuple[int, int | None, list[int]]:
    """Calculate the Destiny (Life Path) number from the full date of birth.

    The destiny number shows your life's purpose, the path you must walk,
    and what the universe has in store. It is the most important number
    for predicting life events.

    Args:
        birth_date: Full date of birth.

    Returns:
        Tuple of (destiny_number 1-9, compound_or_None, master_numbers_found).
    """
    digits = _get_all_date_digits(birth_date)
    total = sum(digits)
    return reduce_to_single(total, respect_master=True)


def calculate_name_number(
    name: str, system: str = "chaldean"
) -> tuple[int, int, list[dict[str, Any]]]:
    """Calculate the numerological value of a name.

    In Vedic numerology, the Chaldean system is preferred because it maps
    letters to numbers based on sound vibration rather than alphabetical
    order.

    Args:
        name: Full name (spaces and non-alpha characters are ignored).
        system: "chaldean" (default, Vedic) or "pythagorean" (Western).

    Returns:
        Tuple of (reduced_value 1-9, compound_value, letter_breakdown).
        letter_breakdown is a list of dicts with "letter" and "value" keys.

    Raises:
        ValueError: If system is not "chaldean" or "pythagorean".
        ValueError: If name contains no alphabetic characters.
    """
    system = system.lower()
    if system not in ("chaldean", "pythagorean"):
        raise ValueError(f"system must be 'chaldean' or 'pythagorean', got '{system}'")

    char_map = CHALDEAN_MAP if system == "chaldean" else PYTHAGOREAN_MAP

    letter_breakdown: list[dict[str, Any]] = []
    total = 0
    has_alpha = False

    for ch in name.upper():
        if ch.isalpha():
            has_alpha = True
            value = char_map.get(ch, 0)
            letter_breakdown.append({"letter": ch, "value": value})
            total += value

    if not has_alpha:
        raise ValueError("Name must contain at least one alphabetic character")

    if total == 0:
        return 0, 0, letter_breakdown

    reduced, _, _ = reduce_to_single(total, respect_master=False)
    return reduced, total, letter_breakdown


def calculate_personal_year(birth_date: date, year: int) -> int:
    """Calculate the personal year number.

    Personal year = birth_day + birth_month + target_year digits, reduced.

    The personal year runs from birthday to birthday, not Jan-Dec.
    It reveals the theme and opportunities for that year.

    Args:
        birth_date: Date of birth.
        year: Target year.

    Returns:
        Personal year number (1-9).
    """
    total = _sum_digits(birth_date.day) + _sum_digits(birth_date.month) + _sum_digits(year)
    while total > 9:
        total = _sum_digits(total)
    return total


def calculate_personal_month(birth_date: date, year: int, month: int) -> int:
    """Calculate the personal month number.

    Personal month = personal_year + calendar_month digits, reduced.

    Args:
        birth_date: Date of birth.
        year: Target year.
        month: Target month (1-12).

    Returns:
        Personal month number (1-9).
    """
    py = calculate_personal_year(birth_date, year)
    total = py + _sum_digits(month)
    while total > 9:
        total = _sum_digits(total)
    return total


def calculate_personal_day(birth_date: date, target_date: date) -> int:
    """Calculate the personal day number.

    Personal day = personal_month + target_day digits, reduced.

    Args:
        birth_date: Date of birth.
        target_date: The date to calculate for.

    Returns:
        Personal day number (1-9).
    """
    pm = calculate_personal_month(birth_date, target_date.year, target_date.month)
    total = pm + _sum_digits(target_date.day)
    while total > 9:
        total = _sum_digits(total)
    return total


def calculate_pinnacle_numbers(birth_date: date) -> list[dict[str, Any]]:
    """Calculate the four pinnacle numbers and their age ranges.

    Pinnacles represent major life phases. The transition ages are
    determined by subtracting the destiny number from 36 (a full cycle).

    - First pinnacle: birth to (36 - destiny_number)
    - Second pinnacle: next 9 years
    - Third pinnacle: next 9 years
    - Fourth pinnacle: remainder of life

    First pinnacle = month + day (reduced)
    Second pinnacle = day + year (reduced)
    Third pinnacle = first + second (reduced)
    Fourth pinnacle = month + year (reduced)

    Args:
        birth_date: Date of birth.

    Returns:
        List of 4 dicts with keys: number, start_age, end_age.
    """
    destiny, _, _ = calculate_destiny_number(birth_date)

    # Reduce month, day, year individually
    month_r = _sum_digits(birth_date.month)
    while month_r > 9:
        month_r = _sum_digits(month_r)

    day_r = _sum_digits(birth_date.day)
    while day_r > 9:
        day_r = _sum_digits(day_r)

    year_r = _sum_digits(birth_date.year)
    while year_r > 9:
        year_r = _sum_digits(year_r)

    first_num = month_r + day_r
    while first_num > 9:
        first_num = _sum_digits(first_num)

    second_num = day_r + year_r
    while second_num > 9:
        second_num = _sum_digits(second_num)

    third_num = first_num + second_num
    while third_num > 9:
        third_num = _sum_digits(third_num)

    fourth_num = month_r + year_r
    while fourth_num > 9:
        fourth_num = _sum_digits(fourth_num)

    first_end = 36 - destiny
    return [
        {"number": first_num, "start_age": 0, "end_age": first_end},
        {"number": second_num, "start_age": first_end + 1, "end_age": first_end + 9},
        {"number": third_num, "start_age": first_end + 10, "end_age": first_end + 18},
        {"number": fourth_num, "start_age": first_end + 19, "end_age": None},
    ]


def calculate_challenge_numbers(birth_date: date) -> list[dict[str, Any]]:
    """Calculate the four challenge numbers and their age ranges.

    Challenges represent obstacles to overcome in each life phase.
    They are based on differences (absolute values) rather than sums.

    First challenge = |month - day|
    Second challenge = |day - year|
    Third challenge = |first - second|
    Fourth challenge = |month - year|

    Args:
        birth_date: Date of birth.

    Returns:
        List of 4 dicts with keys: number, start_age, end_age.
    """
    destiny, _, _ = calculate_destiny_number(birth_date)

    month_r = _sum_digits(birth_date.month)
    while month_r > 9:
        month_r = _sum_digits(month_r)

    day_r = _sum_digits(birth_date.day)
    while day_r > 9:
        day_r = _sum_digits(day_r)

    year_r = _sum_digits(birth_date.year)
    while year_r > 9:
        year_r = _sum_digits(year_r)

    first_num = abs(month_r - day_r)
    second_num = abs(day_r - year_r)
    third_num = abs(first_num - second_num)
    fourth_num = abs(month_r - year_r)

    # Challenge 0 is valid (it means mastery of all challenges)
    first_end = 36 - destiny
    return [
        {"number": first_num, "start_age": 0, "end_age": first_end},
        {"number": second_num, "start_age": first_end + 1, "end_age": first_end + 9},
        {"number": third_num, "start_age": first_end + 10, "end_age": first_end + 18},
        {"number": fourth_num, "start_age": first_end + 19, "end_age": None},
    ]


def calculate_lo_shu_grid(birth_date: date) -> LoShuGrid:
    """Analyze the Lo Shu magic square based on the birth date.

    The Lo Shu grid maps digits 1-9 into a 3x3 magic square. Each digit
    from the birth date is placed in its grid position. Numbers present
    indicate strengths; missing numbers indicate areas to develop.

    Arrows form when all numbers in a row, column, or diagonal are present
    (arrow of strength) or when all are absent (arrow of weakness/absence).

    Args:
        birth_date: Date of birth.

    Returns:
        LoShuGrid with grid layout, present/missing numbers, arrows, and
        dominant plane analysis.
    """
    digits = _get_date_digits(birth_date)
    digit_counts: dict[int, int] = {}
    for d in digits:
        if 1 <= d <= 9:
            digit_counts[d] = digit_counts.get(d, 0) + 1

    present_numbers = sorted(digit_counts.keys())
    missing_numbers = sorted(n for n in range(1, 10) if n not in digit_counts)
    repeated_numbers = {n: c for n, c in digit_counts.items() if c >= 2}

    # Build 3x3 grid
    grid: list[list[dict[str, Any]]] = []
    for row in LO_SHU_GRID:
        grid_row: list[dict[str, Any]] = []
        for num in row:
            grid_row.append(
                {
                    "number": num,
                    "count": digit_counts.get(num, 0),
                    "present": num in digit_counts,
                }
            )
        grid.append(grid_row)

    # Detect arrows
    arrows_present: list[str] = []
    arrows_missing: list[str] = []
    for arrow_name, arrow_nums in LO_SHU_ARROWS.items():
        if all(n in digit_counts for n in arrow_nums):
            arrows_present.append(arrow_name)
        elif all(n not in digit_counts for n in arrow_nums):
            arrows_missing.append(arrow_name)

    # Determine dominant plane
    plane_scores: dict[str, int] = {}
    for plane_name, plane_nums in _LO_SHU_PLANES.items():
        plane_scores[plane_name] = sum(digit_counts.get(n, 0) for n in plane_nums)

    dominant_plane: str | None = None
    if plane_scores:
        max_score = max(plane_scores.values())
        if max_score > 0:
            # Only set dominant if one plane clearly leads
            leaders = [p for p, s in plane_scores.items() if s == max_score]
            if len(leaders) == 1:
                dominant_plane = leaders[0]

    return LoShuGrid(
        grid=grid,
        present_numbers=present_numbers,
        missing_numbers=missing_numbers,
        repeated_numbers=repeated_numbers,
        arrows_present=arrows_present,
        arrows_missing=arrows_missing,
        dominant_plane=dominant_plane,
    )


def get_number_compatibility(num1: int, num2: int) -> NumberCompatibility:
    """Get compatibility analysis between two numerology numbers.

    Based on the traditional Vedic numerology compatibility matrix,
    which aligns with planetary friendships (since each number maps
    to a Vedic planet).

    Args:
        num1: First number (1-9).
        num2: Second number (1-9).

    Returns:
        NumberCompatibility with score, nature, and description.

    Raises:
        ValueError: If either number is not 1-9.
    """
    if not (1 <= num1 <= 9 and 1 <= num2 <= 9):
        raise ValueError(f"Numbers must be 1-9, got {num1} and {num2}")

    key = (min(num1, num2), max(num1, num2))
    score, nature = _COMPATIBILITY_MATRIX.get(key, (50, "neutral"))

    planet1 = NUMBER_PLANET_MAP[num1]
    planet2 = NUMBER_PLANET_MAP[num2]

    descriptions: dict[str, str] = {
        "excellent": (
            f"Numbers {num1} ({planet1}) and {num2} ({planet2}) share excellent "
            f"harmony. Their ruling planets are natural friends, creating a "
            f"supportive and growth-oriented connection."
        ),
        "good": (
            f"Numbers {num1} ({planet1}) and {num2} ({planet2}) have good "
            f"compatibility. The planetary energies complement each other "
            f"with minor adjustments needed."
        ),
        "moderate": (
            f"Numbers {num1} ({planet1}) and {num2} ({planet2}) have moderate "
            f"compatibility. There is neither strong attraction nor repulsion; "
            f"conscious effort can improve the bond."
        ),
        "neutral": (
            f"Numbers {num1} ({planet1}) and {num2} ({planet2}) are neutral. "
            f"The connection is neither particularly helpful nor harmful. "
            f"Other factors in the chart determine the outcome."
        ),
        "challenging": (
            f"Numbers {num1} ({planet1}) and {num2} ({planet2}) present "
            f"challenges. The planetary energies create friction that requires "
            f"patience and understanding to navigate."
        ),
        "difficult": (
            f"Numbers {num1} ({planet1}) and {num2} ({planet2}) have a "
            f"difficult dynamic. Their ruling planets are natural enemies, "
            f"requiring significant effort for harmony."
        ),
    }

    return NumberCompatibility(
        number_1=num1,
        number_2=num2,
        score=score,
        nature=nature,
        description=descriptions.get(nature, descriptions["neutral"]),
        planet_1=planet1,
        planet_2=planet2,
    )


def cross_reference_jyotish(
    psychic: int,
    destiny: int,
    birth_chart_planets: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Cross-reference numerology numbers with Vedic astrology chart data.

    Each number maps to a Vedic planet. This function checks whether the
    ruling planets of the psychic and destiny numbers are strong or weak
    in the actual birth chart, providing a bridge between numerology and
    Jyotish analysis.

    Args:
        psychic: Psychic number (1-9).
        destiny: Destiny number (1-9).
        birth_chart_planets: Optional dict of planet data from a birth chart.
            Expected format: {"sun": {"house": 10, "sign": "aries", "dignity": "exalted", ...}, ...}

    Returns:
        Dict with alignment analysis including planet strengths and recommendations.
    """
    psychic_planet = NUMBER_PLANET_MAP.get(psychic, "unknown")
    destiny_planet = NUMBER_PLANET_MAP.get(destiny, "unknown")

    result: dict[str, Any] = {
        "psychic_number": psychic,
        "destiny_number": destiny,
        "psychic_planet": psychic_planet,
        "destiny_planet": destiny_planet,
        "same_planet": psychic_planet == destiny_planet,
        "planet_friendship": _get_planet_friendship(psychic_planet, destiny_planet),
        "psychic_planet_strong": None,
        "destiny_planet_strong": None,
        "alignment": "unknown",
        "recommendations": [],
    }

    if birth_chart_planets is None:
        result["alignment"] = "chart data needed for full analysis"
        return result

    # Check psychic planet in chart
    p_data = birth_chart_planets.get(psychic_planet)
    if p_data:
        p_dignity = _extract_dignity(p_data)
        result["psychic_planet_strong"] = p_dignity in ("exalted", "own_sign", "moolatrikona")
        result["psychic_planet_dignity"] = p_dignity
        result["psychic_planet_house"] = _extract_value(p_data, "house")

    # Check destiny planet in chart
    d_data = birth_chart_planets.get(destiny_planet)
    if d_data:
        d_dignity = _extract_dignity(d_data)
        result["destiny_planet_strong"] = d_dignity in ("exalted", "own_sign", "moolatrikona")
        result["destiny_planet_dignity"] = d_dignity
        result["destiny_planet_house"] = _extract_value(d_data, "house")

    # Determine alignment
    p_strong = result.get("psychic_planet_strong")
    d_strong = result.get("destiny_planet_strong")

    if p_strong and d_strong:
        result["alignment"] = "excellent"
        result["recommendations"].append(
            "Both numerology rulers are strong in the chart. "
            "Name and birth numbers align well with the horoscope."
        )
    elif p_strong and not d_strong:
        result["alignment"] = "partial"
        result["recommendations"].append(
            f"Psychic planet ({psychic_planet}) is strong but destiny planet "
            f"({destiny_planet}) is weak. Consider strengthening {destiny_planet} "
            f"through its gemstone or mantra."
        )
    elif not p_strong and d_strong:
        result["alignment"] = "partial"
        result["recommendations"].append(
            f"Destiny planet ({destiny_planet}) is strong but psychic planet "
            f"({psychic_planet}) is weak. Personal confidence may need boosting; "
            f"strengthen {psychic_planet}."
        )
    elif p_strong is not None and d_strong is not None:
        result["alignment"] = "weak"
        result["recommendations"].append(
            f"Both numerology rulers ({psychic_planet}, {destiny_planet}) are weak "
            f"in the chart. Remedial measures for both planets are advised."
        )
    else:
        result["alignment"] = "incomplete"
        result["recommendations"].append("Insufficient chart data to fully assess planet strength.")

    return result


def calculate_full_profile(
    birth_date: date,
    name: str | None = None,
    target_date: date | None = None,
) -> NumerologyProfile:
    """Calculate the complete numerology profile for a person.

    This is the master function that calls all individual calculators and
    assembles a comprehensive NumerologyProfile.

    Args:
        birth_date: Date of birth.
        name: Optional full name for name number calculation.
        target_date: Date for personal cycles (defaults to today).

    Returns:
        Complete NumerologyProfile.
    """
    if target_date is None:
        target_date = date.today()

    # Core numbers
    psychic, compound_psychic = calculate_psychic_number(birth_date.day)
    destiny, compound_destiny, master_numbers = calculate_destiny_number(birth_date)

    # Name numbers
    name_num: int | None = None
    name_num_pyth: int | None = None
    compound_name: int | None = None
    name_planet: str | None = None

    if name:
        name_num, compound_name, _ = calculate_name_number(name, "chaldean")
        name_num_pyth, _, _ = calculate_name_number(name, "pythagorean")
        name_planet = NUMBER_PLANET_MAP.get(name_num) if name_num else None

    # Personal cycles
    py = calculate_personal_year(birth_date, target_date.year)
    pm = calculate_personal_month(birth_date, target_date.year, target_date.month)
    pd = calculate_personal_day(birth_date, target_date)

    # Lo Shu grid
    lo_shu = calculate_lo_shu_grid(birth_date)
    lo_shu_dict = lo_shu.model_dump()

    # Harmony
    harmony_key = (min(psychic, destiny), max(psychic, destiny))
    harmony = _PSYCHIC_DESTINY_HARMONY.get(harmony_key, "medium")

    return NumerologyProfile(
        psychic_number=psychic,
        destiny_number=destiny,
        name_number=name_num,
        name_number_pythagorean=name_num_pyth,
        compound_psychic=compound_psychic,
        compound_destiny=compound_destiny,
        compound_name=compound_name,
        psychic_planet=NUMBER_PLANET_MAP[psychic],
        destiny_planet=NUMBER_PLANET_MAP[destiny],
        name_planet=name_planet,
        master_numbers_found=master_numbers,
        personal_year=py,
        personal_month=pm,
        personal_day=pd,
        lo_shu_grid=lo_shu_dict,
        missing_numbers=lo_shu.missing_numbers,
        repeated_numbers=lo_shu.repeated_numbers,
        psychic_destiny_harmony=harmony,
    )


def get_personal_cycles(
    birth_date: date,
    target_date: date | None = None,
) -> PersonalCycles:
    """Get personal cycle analysis for a target date.

    Args:
        birth_date: Date of birth.
        target_date: Date to analyze (defaults to today).

    Returns:
        PersonalCycles with year/month/day numbers and interpretations.
    """
    if target_date is None:
        target_date = date.today()

    py = calculate_personal_year(birth_date, target_date.year)
    pm = calculate_personal_month(birth_date, target_date.year, target_date.month)
    pd = calculate_personal_day(birth_date, target_date)

    pinnacles = calculate_pinnacle_numbers(birth_date)
    challenges = calculate_challenge_numbers(birth_date)

    # Find current pinnacle based on age
    age = target_date.year - birth_date.year
    if (target_date.month, target_date.day) < (birth_date.month, birth_date.day):
        age -= 1

    current_pinnacle = pinnacles[-1]["number"]  # default to last
    for p in pinnacles:
        end = p["end_age"]
        if end is not None and age <= end:
            current_pinnacle = p["number"]
            break

    current_challenge = challenges[-1]["number"]
    for c in challenges:
        end = c["end_age"]
        if end is not None and age <= end:
            current_challenge = c["number"]
            break

    return PersonalCycles(
        personal_year=py,
        personal_month=pm,
        personal_day=pd,
        year_planet=NUMBER_PLANET_MAP[py],
        month_planet=NUMBER_PLANET_MAP[pm],
        day_planet=NUMBER_PLANET_MAP[pd],
        year_meaning=_NUMBER_MEANINGS.get(py, ""),
        pinnacle_number=current_pinnacle,
        challenge_number=current_challenge,
    )


def analyze_name(name: str) -> NameAnalysis:
    """Perform full name analysis with both Chaldean and Pythagorean systems.

    Args:
        name: The full name to analyze.

    Returns:
        NameAnalysis with values from both systems and letter breakdown.
    """
    ch_reduced, ch_compound, ch_breakdown = calculate_name_number(name, "chaldean")
    py_reduced, py_compound, _ = calculate_name_number(name, "pythagorean")

    return NameAnalysis(
        full_name=name,
        chaldean_value=ch_compound,
        chaldean_reduced=ch_reduced,
        pythagorean_value=py_compound,
        pythagorean_reduced=py_reduced,
        ruling_planet=NUMBER_PLANET_MAP.get(ch_reduced, "unknown"),
        letter_breakdown=ch_breakdown,
    )


def get_compound_meaning(compound: int | None) -> str:
    """Get the interpretation of a compound number.

    Args:
        compound: The compound (unreduced) number, or None.

    Returns:
        Meaning string, or empty string if no meaning available.
    """
    if compound is None:
        return ""
    return _COMPOUND_MEANINGS.get(compound, "")


# ---------------------------------------------------------------------------
# Private Helper Functions
# ---------------------------------------------------------------------------


def _get_planet_friendship(planet1: str, planet2: str) -> str:
    """Determine the friendship between two Vedic planets.

    Based on the classical naisargika (natural) friendship table.

    Returns:
        One of: "same", "friend", "neutral", "enemy".
    """
    if planet1 == planet2:
        return "same"

    # Natural friendships in Vedic astrology
    friendships: dict[str, dict[str, str]] = {
        "sun": {
            "moon": "friend",
            "mars": "friend",
            "jupiter": "friend",
            "venus": "enemy",
            "saturn": "enemy",
            "mercury": "neutral",
            "rahu": "enemy",
            "ketu": "neutral",
        },
        "moon": {
            "sun": "friend",
            "mercury": "friend",
            "jupiter": "neutral",
            "venus": "neutral",
            "saturn": "neutral",
            "mars": "neutral",
            "rahu": "neutral",
            "ketu": "neutral",
        },
        "mars": {
            "sun": "friend",
            "moon": "friend",
            "jupiter": "friend",
            "venus": "neutral",
            "saturn": "neutral",
            "mercury": "enemy",
            "rahu": "neutral",
            "ketu": "neutral",
        },
        "mercury": {
            "sun": "friend",
            "venus": "friend",
            "jupiter": "neutral",
            "moon": "enemy",
            "mars": "enemy",
            "saturn": "neutral",
            "rahu": "neutral",
            "ketu": "neutral",
        },
        "jupiter": {
            "sun": "friend",
            "moon": "friend",
            "mars": "friend",
            "venus": "enemy",
            "saturn": "neutral",
            "mercury": "enemy",
            "rahu": "enemy",
            "ketu": "neutral",
        },
        "venus": {
            "mercury": "friend",
            "saturn": "friend",
            "sun": "enemy",
            "moon": "enemy",
            "mars": "neutral",
            "jupiter": "neutral",
            "rahu": "neutral",
            "ketu": "neutral",
        },
        "saturn": {
            "mercury": "friend",
            "venus": "friend",
            "sun": "enemy",
            "moon": "enemy",
            "mars": "enemy",
            "jupiter": "neutral",
            "rahu": "friend",
            "ketu": "neutral",
        },
        "rahu": {
            "mercury": "friend",
            "venus": "friend",
            "saturn": "friend",
            "sun": "enemy",
            "moon": "enemy",
            "mars": "neutral",
            "jupiter": "enemy",
            "ketu": "enemy",
        },
        "ketu": {
            "mars": "friend",
            "jupiter": "friend",
            "saturn": "neutral",
            "sun": "neutral",
            "moon": "neutral",
            "mercury": "enemy",
            "venus": "enemy",
            "rahu": "enemy",
        },
    }

    planet_friends = friendships.get(planet1, {})
    return planet_friends.get(planet2, "neutral")


def _extract_dignity(planet_data: Any) -> str:
    """Extract dignity from planet data (handles dict or object)."""
    if isinstance(planet_data, dict):
        return str(planet_data.get("dignity", "neutral"))
    return str(getattr(planet_data, "dignity", "neutral"))


def _extract_value(planet_data: Any, key: str) -> Any:
    """Extract a value from planet data (handles dict or object)."""
    if isinstance(planet_data, dict):
        return planet_data.get(key)
    return getattr(planet_data, key, None)


# ---------------------------------------------------------------------------
# Optional knowledge file loading for enriched interpretations
# ---------------------------------------------------------------------------


def _load_numerology_knowledge() -> dict[str, Any]:
    """Attempt to load numerology knowledge files for enriched interpretations.

    Returns empty dict if files are not available (the module works fine
    without them, using built-in interpretations).
    """
    knowledge: dict[str, Any] = {}
    with contextlib.suppress(Exception):
        from packages.core.src.knowledge_loader import load_definition, load_rules

        defn = load_definition("numerology")
        if defn:
            knowledge["definitions"] = defn
        rules = load_rules("numerology_rules")
        if rules:
            knowledge["rules"] = rules
    return knowledge
