"""Narayana Dasha calculations module for 108 Vedic Astrology app.

This module implements the Narayana Dasha system, a sign-based (rashi) dasha
system used in Jaimini astrology. It is a 108-year cycle system where each sign
gets a variable duration based on the position of its lord.

The system has these characteristics:
- Total cycle: 108 years (12 signs with variable durations)
- Progression: Forward for odd signs, reverse for even signs
- Duration: 1-12 years per sign based on lord's position
- Starting point: Ascendant (Lagna)

Key differences from Vimshottari:
- Sign-based (not nakshatra-based)
- Variable duration per period
- Direction alternates based on sign's odd/even nature
"""

from datetime import datetime, timedelta

from packages.core.src.constants import Planet, Rashi
from packages.core.src.models import BirthChart, NarayanaDashaPeriod

# List of rashis in order
RASHI_LIST = [
    Rashi.ARIES,
    Rashi.TAURUS,
    Rashi.GEMINI,
    Rashi.CANCER,
    Rashi.LEO,
    Rashi.VIRGO,
    Rashi.LIBRA,
    Rashi.SCORPIO,
    Rashi.SAGITTARIUS,
    Rashi.CAPRICORN,
    Rashi.AQUARIUS,
    Rashi.PISCES,
]

TOTAL_CYCLE = 108

# Sign lords (primary lords)
SIGN_LORDS = {
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

# Co-lords for dual-lorded signs (modern/Jaimini considerations)
CO_LORDS = {
    Rashi.SCORPIO: Planet.KETU,
    Rashi.AQUARIUS: Planet.RAHU,
}


def is_odd_sign(rashi: Rashi) -> bool:
    """Determine if a rashi is odd-footed (odd sign in Jaimini).

    In Jaimini astrology, odd signs are at even indices (0, 2, 4, 6, 8, 10):
    Aries(0), Gemini(2), Leo(4), Libra(6), Sagittarius(8), Aquarius(10)

    Args:
        rashi: Rashi enum value

    Returns:
        True if odd sign, False if even sign

    Example:
        >>> is_odd_sign(Rashi.ARIES)
        True
        >>> is_odd_sign(Rashi.TAURUS)
        False
    """
    rashi_index = get_sign_index(rashi)
    # Even indices (0, 2, 4, 6, 8, 10) are odd signs
    return rashi_index % 2 == 0


def get_sign_index(rashi: Rashi) -> int:
    """Get the 0-11 index for a rashi.

    Args:
        rashi: Rashi enum value

    Returns:
        Index (0-11)

    Example:
        >>> get_sign_index(Rashi.ARIES)
        0
        >>> get_sign_index(Rashi.PISCES)
        11
    """
    return RASHI_LIST.index(rashi)


def get_progression_direction(lagna: Rashi) -> bool:
    """Determine the progression direction based on lagna.

    Args:
        lagna: Ascendant rashi

    Returns:
        True for forward progression, False for reverse

    Example:
        >>> get_progression_direction(Rashi.ARIES)
        True  # Odd sign, forward
        >>> get_progression_direction(Rashi.TAURUS)
        False  # Even sign, reverse
    """
    return is_odd_sign(lagna)


# Own signs for planets (rashi enum values)
_OWN_SIGNS: dict[Planet, set[Rashi]] = {
    Planet.SUN: {Rashi.LEO},
    Planet.MOON: {Rashi.CANCER},
    Planet.MARS: {Rashi.ARIES, Rashi.SCORPIO},
    Planet.MERCURY: {Rashi.GEMINI, Rashi.VIRGO},
    Planet.JUPITER: {Rashi.SAGITTARIUS, Rashi.PISCES},
    Planet.VENUS: {Rashi.TAURUS, Rashi.LIBRA},
    Planet.SATURN: {Rashi.CAPRICORN, Rashi.AQUARIUS},
    Planet.RAHU: set(),
    Planet.KETU: set(),
}

# Exaltation signs
_EXALTATION: dict[Planet, Rashi] = {
    Planet.SUN: Rashi.ARIES,
    Planet.MOON: Rashi.TAURUS,
    Planet.MARS: Rashi.CAPRICORN,
    Planet.MERCURY: Rashi.VIRGO,
    Planet.JUPITER: Rashi.CANCER,
    Planet.VENUS: Rashi.PISCES,
    Planet.SATURN: Rashi.LIBRA,
}


def _get_stronger_lord(rashi: Rashi, chart: BirthChart) -> Planet:
    """For co-lorded signs (Scorpio, Aquarius), determine which lord is stronger.

    Uses proper Jaimini rules in priority order:
    1. Planet in own sign > planet not in own sign
    2. Planet in exaltation > planet not exalted
    3. Planet with more aspects from other planets > fewer
    4. Planet in kendra (1, 4, 7, 10) > planet not in kendra
    5. Higher degree in sign > lower degree (last resort)

    Args:
        rashi: Rashi with co-lords
        chart: BirthChart with planet positions

    Returns:
        The stronger lord planet

    Example:
        >>> # If Mars is in own sign and Ketu is not, Mars is stronger
        >>> _get_stronger_lord(Rashi.SCORPIO, chart)
        Planet.MARS
    """
    if rashi not in CO_LORDS:
        return SIGN_LORDS[rashi]

    primary_lord = SIGN_LORDS[rashi]
    co_lord = CO_LORDS[rashi]

    # Get positions
    primary_pos = chart.planets.get(primary_lord)
    co_pos = chart.planets.get(co_lord)

    if not primary_pos or not co_pos:
        return primary_lord

    # Rule 1: Planet in own sign > not in own sign
    primary_in_own = primary_pos.rashi in _OWN_SIGNS.get(primary_lord, set())
    co_in_own = co_pos.rashi in _OWN_SIGNS.get(co_lord, set())
    if primary_in_own and not co_in_own:
        return primary_lord
    if co_in_own and not primary_in_own:
        return co_lord

    # Rule 2: Planet in exaltation > not exalted
    primary_exalted = _EXALTATION.get(primary_lord) == primary_pos.rashi
    co_exalted = _EXALTATION.get(co_lord) == co_pos.rashi
    if primary_exalted and not co_exalted:
        return primary_lord
    if co_exalted and not primary_exalted:
        return co_lord

    # Rule 3: Planet with more aspects from other planets
    primary_aspects = _count_aspects_on(primary_pos.house, chart)
    co_aspects = _count_aspects_on(co_pos.house, chart)
    if primary_aspects > co_aspects:
        return primary_lord
    if co_aspects > primary_aspects:
        return co_lord

    # Rule 4: Planet in kendra > not in kendra
    kendra_houses = {1, 4, 7, 10}
    primary_in_kendra = primary_pos.house in kendra_houses
    co_in_kendra = co_pos.house in kendra_houses
    if primary_in_kendra and not co_in_kendra:
        return primary_lord
    if co_in_kendra and not primary_in_kendra:
        return co_lord

    # Rule 5: Higher degree in sign (last resort)
    if primary_pos.rashi_degree > co_pos.rashi_degree:
        return primary_lord
    return co_lord


def _count_aspects_on(house: int, chart: BirthChart) -> int:
    """Count how many planets aspect a given house using Parashari aspects.

    Standard aspects: all planets aspect 7th house.
    Special: Mars aspects 4th and 8th. Jupiter aspects 5th and 9th. Saturn aspects 3rd and 10th.

    Args:
        house: Target house number (1-12)
        chart: BirthChart with planet positions

    Returns:
        Number of planets aspecting the target house
    """
    count = 0
    for planet, pos in chart.planets.items():
        p_house = pos.house
        if p_house == house:
            continue  # Conjunction, not aspect

        diff = ((house - p_house) % 12) or 12

        # All planets aspect 7th from themselves
        if diff == 7:
            count += 1
            continue

        # Mars special aspects: 4th and 8th
        if planet == Planet.MARS and diff in (4, 8):
            count += 1
            continue

        # Jupiter special aspects: 5th and 9th
        if planet == Planet.JUPITER and diff in (5, 9):
            count += 1
            continue

        # Saturn special aspects: 3rd and 10th
        if planet == Planet.SATURN and diff in (3, 10):
            count += 1
            continue

    return count


def calculate_period_duration(sign: Rashi, chart: BirthChart) -> int:
    """Calculate the duration in years for a sign's dasha period.

    Algorithm:
    1. Get sign's lord (use _get_stronger_lord for co-lorded signs)
    2. Find lord's rashi position in chart
    3. Count from sign to lord's rashi (forward, inclusive) = N
    4. If sign is odd: duration = N
    5. If sign is even: duration = 12 - N (if N > 0) or 12 (if N = 0)
    6. Special case: If lord is in its own sign: duration = 12

    Args:
        sign: The rashi whose duration is being calculated
        chart: BirthChart with planet positions

    Returns:
        Duration in years (1-12)

    Example:
        >>> # If Aries lord Mars is in Aries itself
        >>> calculate_period_duration(Rashi.ARIES, chart)
        12
    """
    # Get the lord of the sign
    lord = _get_stronger_lord(sign, chart)

    # Find lord's position
    lord_pos = chart.planets.get(lord)
    if not lord_pos:
        # Fallback: if we can't find the lord, use default 12
        return 12

    lord_rashi = lord_pos.rashi

    # Special case: lord in its own sign
    if lord_rashi == sign:
        return 12

    # Count from sign to lord's rashi (forward, inclusive)
    sign_index = get_sign_index(sign)
    lord_index = get_sign_index(lord_rashi)

    # Forward count from sign to lord's sign
    if lord_index >= sign_index:
        n = lord_index - sign_index + 1
    else:
        # Wrap around
        n = (12 - sign_index) + lord_index + 1

    # Apply duration formula
    duration = n if is_odd_sign(sign) else (12 - (n % 12) if (n % 12) != 0 else 12)

    # Ensure duration is 1-12
    if duration < 1:
        duration = 1
    if duration > 12:
        duration = 12

    return duration


def calculate_narayana_sequence(
    birth_dt: datetime, chart: BirthChart, cycles: int = 1
) -> list[NarayanaDashaPeriod]:
    """Generate the full sequence of Narayana dasha periods.

    Args:
        birth_dt: Birth datetime
        chart: BirthChart with lagna and planet positions
        cycles: Number of complete cycles to generate (default 1 = 108 years)

    Returns:
        List of NarayanaDashaPeriod objects

    Example:
        >>> from datetime import datetime, UTC
        >>> periods = calculate_narayana_sequence(
        ...     datetime(1992, 12, 3, tzinfo=UTC), chart
        ... )
        >>> len(periods)
        12  # One complete cycle
    """
    lagna = chart.lagna_rashi
    is_forward = get_progression_direction(lagna)

    periods: list[NarayanaDashaPeriod] = []
    current_date = birth_dt

    # Generate periods for the specified number of cycles
    for _cycle in range(cycles):
        lagna_index = get_sign_index(lagna)

        # Generate 12 periods for this cycle
        for i in range(12):
            # Calculate current sign based on direction
            current_sign_index = (lagna_index + i) % 12 if is_forward else (lagna_index - i) % 12

            current_sign = RASHI_LIST[current_sign_index]

            # Calculate duration for this sign
            duration_years = calculate_period_duration(current_sign, chart)

            # Calculate end date
            days_in_period = int(duration_years * 365.25)
            end_date = current_date + timedelta(days=days_in_period)

            periods.append(
                NarayanaDashaPeriod(
                    rashi=current_sign,
                    start_date=current_date,
                    end_date=end_date,
                    duration_years=duration_years,
                    is_forward=is_forward,
                )
            )

            current_date = end_date

    return periods


def get_current_narayana_dasha(
    birth_dt: datetime, chart: BirthChart, query_dt: datetime | None = None
) -> dict:
    """Find which Narayana dasha period is active at query_dt.

    Args:
        birth_dt: Birth datetime
        chart: BirthChart with lagna and planet positions
        query_dt: Query datetime (defaults to now)

    Returns:
        Dictionary with:
            - rashi: Rashi
            - start_date: datetime
            - end_date: datetime
            - duration_years: int
            - is_forward: bool
            - remaining_days: int

    Example:
        >>> from datetime import datetime, UTC
        >>> current = get_current_narayana_dasha(
        ...     datetime(1992, 12, 3, tzinfo=UTC),
        ...     chart,
        ...     query_dt=datetime(2025, 1, 1, tzinfo=UTC)
        ... )
        >>> current['rashi']
        'sagittarius'
    """
    if query_dt is None:
        query_dt = datetime.now()

    # Ensure timezone consistency: strip tzinfo for comparison
    if query_dt.tzinfo is not None:
        query_dt = query_dt.replace(tzinfo=None)

    # Generate enough cycles to cover the query date (assume max 120 years)
    # 108 years per cycle, so 2 cycles should be enough
    periods = calculate_narayana_sequence(birth_dt, chart, cycles=2)

    # Find the period that contains the query date
    for period in periods:
        # Strip timezone from period dates for comparison
        start = (
            period.start_date.replace(tzinfo=None)
            if period.start_date.tzinfo
            else period.start_date
        )
        end = period.end_date.replace(tzinfo=None) if period.end_date.tzinfo else period.end_date

        if start <= query_dt < end:
            remaining_days = (end - query_dt).days
            return {
                "rashi": period.rashi,
                "start_date": period.start_date,
                "end_date": period.end_date,
                "duration_years": period.duration_years,
                "is_forward": period.is_forward,
                "remaining_days": remaining_days,
            }

    # If query_dt is beyond all calculated periods, return the last period
    last_period = periods[-1]
    last_end = (
        last_period.end_date.replace(tzinfo=None)
        if last_period.end_date.tzinfo
        else last_period.end_date
    )
    remaining_days = max(0, (last_end - query_dt).days)
    return {
        "rashi": last_period.rashi,
        "start_date": last_period.start_date,
        "end_date": last_period.end_date,
        "duration_years": last_period.duration_years,
        "is_forward": last_period.is_forward,
        "remaining_days": remaining_days,
    }


def get_narayana_antardasha(maha: NarayanaDashaPeriod, chart: BirthChart) -> list[dict]:
    """Subdivide a maha-dasha into 12 sub-periods.

    The sub-period sequence follows the same direction as the maha-dasha.
    Each sub-period duration is proportional to its calculated duration:
    (sub_sign_duration / total_of_all_durations) * maha_duration

    Args:
        maha: NarayanaDashaPeriod for the maha-dasha
        chart: BirthChart for calculating sub-period durations

    Returns:
        List of dicts with rashi, start_date, end_date, duration_years

    Example:
        >>> from datetime import datetime, UTC
        >>> maha = NarayanaDashaPeriod(
        ...     rashi=Rashi.ARIES,
        ...     start_date=datetime(2020, 1, 1, tzinfo=UTC),
        ...     end_date=datetime(2032, 1, 1, tzinfo=UTC),
        ...     duration_years=12,
        ...     is_forward=True
        ... )
        >>> antardashas = get_narayana_antardasha(maha, chart)
        >>> len(antardashas)
        12
    """
    maha_rashi_index = get_sign_index(maha.rashi)
    is_forward = maha.is_forward

    # Calculate durations for all 12 sub-signs
    sub_durations = []
    for i in range(12):
        sub_sign_index = (maha_rashi_index + i) % 12 if is_forward else (maha_rashi_index - i) % 12

        sub_sign = RASHI_LIST[sub_sign_index]
        sub_duration = calculate_period_duration(sub_sign, chart)
        sub_durations.append((sub_sign, sub_duration))

    # Calculate total duration
    total_duration = sum(dur for _, dur in sub_durations)

    # Calculate total maha days
    maha_duration_days = (maha.end_date - maha.start_date).days

    # Generate antardashas
    antardashas = []
    current_date = maha.start_date

    for sub_sign, sub_duration in sub_durations:
        # Proportional duration
        antardasha_days = int((sub_duration / total_duration) * maha_duration_days)

        # Ensure we don't exceed the maha end date
        end_date = current_date + timedelta(days=antardasha_days)
        if end_date > maha.end_date:
            end_date = maha.end_date

        antardashas.append(
            {
                "rashi": sub_sign,
                "start_date": current_date,
                "end_date": end_date,
                "duration_years": sub_duration,
            }
        )

        current_date = end_date

        # Stop if we've reached the maha end date
        if current_date >= maha.end_date:
            break

    return antardashas
