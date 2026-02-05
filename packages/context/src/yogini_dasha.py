"""Yogini Dasha calculations module for 108 Vedic Astrology app.

This module implements the Yogini Dasha system, an ancient 36-year cycle system
based on 8 Yoginis (female deities). Each Yogini rules a specific duration and
is associated with a planetary lord.

The Yogini Dasha system consists of 8 Yoginis totaling 36 years:
- Mangala: 1 year (Moon)
- Pingala: 2 years (Sun)
- Dhanya: 3 years (Jupiter)
- Bhramari: 4 years (Mars)
- Bhadrika: 5 years (Mercury)
- Ulka: 6 years (Saturn)
- Siddha: 7 years (Venus)
- Sankata: 8 years (Rahu)

The starting Yogini is determined by the Moon's nakshatra and pada at birth.
"""

from datetime import datetime, timedelta

from packages.core.src.constants import NAKSHATRA_SPAN, Planet, YoginiName
from packages.core.src.models import YoginiDashaPeriod

# Yogini data: (YoginiName, Planet lord, duration_years)
YOGINI_DATA = [
    (YoginiName.MANGALA, Planet.MOON, 1),
    (YoginiName.PINGALA, Planet.SUN, 2),
    (YoginiName.DHANYA, Planet.JUPITER, 3),
    (YoginiName.BHRAMARI, Planet.MARS, 4),
    (YoginiName.BHADRIKA, Planet.MERCURY, 5),
    (YoginiName.ULKA, Planet.SATURN, 6),
    (YoginiName.SIDDHA, Planet.VENUS, 7),
    (YoginiName.SANKATA, Planet.RAHU, 8),
]

TOTAL_CYCLE = 36  # years


def get_starting_yogini(nakshatra_num: int, pada: int) -> int:
    """Calculate the starting Yogini index based on Moon's nakshatra and pada.

    Formula: (nakshatra_pada_number + 3) % 8
    where nakshatra_pada_number = (nakshatra_num - 1) * 4 + pada

    Args:
        nakshatra_num: Nakshatra number (1-27)
        pada: Pada number (1-4)

    Returns:
        Index into YOGINI_DATA (0-7)

    Example:
        >>> get_starting_yogini(1, 1)  # Ashwini pada 1
        4  # Bhadrika
    """
    if not (1 <= nakshatra_num <= 27):
        raise ValueError(f"Nakshatra number must be 1-27, got {nakshatra_num}")
    if not (1 <= pada <= 4):
        raise ValueError(f"Pada must be 1-4, got {pada}")

    # Calculate the nakshatra pada number (1-108)
    nakshatra_pada_number = (nakshatra_num - 1) * 4 + pada

    # Apply formula
    yogini_index = (nakshatra_pada_number + 3) % 8

    return yogini_index


def get_yogini_balance_at_birth(nakshatra_num: int, pada: int, degree_in_nakshatra: float) -> dict:
    """Calculate how much of the starting yogini's period has elapsed at birth.

    Each nakshatra spans 13.333° (13°20'). The proportion of the nakshatra
    traversed determines how much of the starting yogini's period has elapsed.

    Args:
        nakshatra_num: Nakshatra number (1-27)
        pada: Pada number (1-4)
        degree_in_nakshatra: Degrees traversed in current nakshatra (0-13.333)

    Returns:
        Dictionary with:
            - yogini_index: int (0-7)
            - yogini: YoginiName
            - lord: Planet
            - total_years: int
            - elapsed_years: float
            - remaining_years: float

    Example:
        >>> balance = get_yogini_balance_at_birth(25, 3, 10.0)
        >>> balance['yogini']
        'sankata'
    """
    if not (0 <= degree_in_nakshatra < NAKSHATRA_SPAN):
        raise ValueError(
            f"Degree in nakshatra must be 0-{NAKSHATRA_SPAN}, got {degree_in_nakshatra}"
        )

    yogini_index = get_starting_yogini(nakshatra_num, pada)
    yogini_name, planet_lord, total_years = YOGINI_DATA[yogini_index]

    # Calculate proportion of nakshatra traversed
    proportion_traversed = degree_in_nakshatra / NAKSHATRA_SPAN

    # Calculate elapsed and remaining time
    elapsed_years = total_years * proportion_traversed
    remaining_years = total_years * (1 - proportion_traversed)

    return {
        "yogini_index": yogini_index,
        "yogini": yogini_name,
        "lord": planet_lord,
        "total_years": total_years,
        "elapsed_years": elapsed_years,
        "remaining_years": remaining_years,
    }


def calculate_yogini_sequence(
    birth_dt: datetime,
    nakshatra_num: int,
    pada: int,
    degree_in_nakshatra: float,
    cycles: int = 3,
) -> list[YoginiDashaPeriod]:
    """Generate the full sequence of Yogini dasha periods.

    Args:
        birth_dt: Birth datetime
        nakshatra_num: Moon's nakshatra number (1-27)
        pada: Moon's pada (1-4)
        degree_in_nakshatra: Degrees in nakshatra (0-13.333)
        cycles: Number of complete cycles to generate (default 3 = 108 years)

    Returns:
        List of YoginiDashaPeriod objects

    Example:
        >>> from datetime import datetime, UTC
        >>> periods = calculate_yogini_sequence(
        ...     datetime(1992, 12, 3, tzinfo=UTC), 25, 3, 10.0
        ... )
        >>> len(periods)
        24  # 8 yoginis x 3 cycles
    """
    balance = get_yogini_balance_at_birth(nakshatra_num, pada, degree_in_nakshatra)
    starting_index = balance["yogini_index"]
    remaining_years = balance["remaining_years"]

    periods: list[YoginiDashaPeriod] = []
    current_date = birth_dt

    # First period (partial, based on balance)
    yogini_name, planet_lord, total_years = YOGINI_DATA[starting_index]
    days_in_period = int(remaining_years * 365.25)
    end_date = current_date + timedelta(days=days_in_period)

    periods.append(
        YoginiDashaPeriod(
            yogini=yogini_name,
            planet_lord=planet_lord,
            start_date=current_date,
            end_date=end_date,
            duration_years=total_years,
        )
    )
    current_date = end_date

    # Calculate total periods needed (excluding the first partial period)
    total_periods = cycles * 8 - 1

    # Generate subsequent periods
    for i in range(total_periods):
        # Cycle through yoginis starting from the next one after starting_index
        yogini_index = (starting_index + 1 + i) % 8
        yogini_name, planet_lord, duration_years = YOGINI_DATA[yogini_index]

        days_in_period = int(duration_years * 365.25)
        end_date = current_date + timedelta(days=days_in_period)

        periods.append(
            YoginiDashaPeriod(
                yogini=yogini_name,
                planet_lord=planet_lord,
                start_date=current_date,
                end_date=end_date,
                duration_years=duration_years,
            )
        )
        current_date = end_date

    return periods


def get_current_yogini_dasha(
    birth_dt: datetime,
    nakshatra_num: int,
    pada: int,
    degree_in_nakshatra: float,
    query_dt: datetime | None = None,
) -> dict:
    """Get the current Yogini maha-dasha at a specific date.

    Args:
        birth_dt: Birth datetime
        nakshatra_num: Moon's nakshatra number (1-27)
        pada: Moon's pada (1-4)
        degree_in_nakshatra: Degrees in nakshatra (0-13.333)
        query_dt: Query datetime (defaults to now)

    Returns:
        Dictionary with:
            - yogini: YoginiName
            - lord: Planet
            - start_date: datetime
            - end_date: datetime
            - remaining_days: int

    Example:
        >>> from datetime import datetime, UTC
        >>> current = get_current_yogini_dasha(
        ...     datetime(1992, 12, 3, tzinfo=UTC),
        ...     25, 3, 10.0,
        ...     query_dt=datetime(2025, 1, 1, tzinfo=UTC)
        ... )
        >>> current['yogini']
        'ulka'
    """
    if query_dt is None:
        query_dt = datetime.now()

    # Ensure timezone consistency: strip tzinfo for comparison
    if query_dt.tzinfo is not None:
        query_dt = query_dt.replace(tzinfo=None)

    # Generate enough cycles to cover the query date
    # Assume max lifespan of 120 years (4 cycles)
    periods = calculate_yogini_sequence(
        birth_dt, nakshatra_num, pada, degree_in_nakshatra, cycles=4
    )

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
                "yogini": period.yogini,
                "lord": period.planet_lord,
                "start_date": period.start_date,
                "end_date": period.end_date,
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
        "yogini": last_period.yogini,
        "lord": last_period.planet_lord,
        "start_date": last_period.start_date,
        "end_date": last_period.end_date,
        "remaining_days": remaining_days,
    }


def get_yogini_antardasha(maha: YoginiDashaPeriod) -> list[dict]:
    """Subdivide a maha-dasha into 8 antardashas proportionally.

    The antardasha sequence starts from the maha-dasha yogini itself.
    Each antardasha duration = (antardasha_yogini_years / TOTAL_CYCLE) * maha_duration_days

    Args:
        maha: YoginiDashaPeriod for the maha-dasha

    Returns:
        List of dicts with yogini, lord, start_date, end_date

    Example:
        >>> from datetime import datetime, UTC
        >>> maha = YoginiDashaPeriod(
        ...     yogini=YoginiName.BHADRIKA,
        ...     planet_lord=Planet.MERCURY,
        ...     start_date=datetime(2020, 1, 1, tzinfo=UTC),
        ...     end_date=datetime(2025, 1, 1, tzinfo=UTC),
        ...     duration_years=5
        ... )
        >>> antardashas = get_yogini_antardasha(maha)
        >>> len(antardashas)
        8
    """
    # Find the starting index for this maha-dasha's yogini
    starting_index = None
    for i, (yogini_name, _, _) in enumerate(YOGINI_DATA):
        if yogini_name == maha.yogini:
            starting_index = i
            break

    if starting_index is None:
        raise ValueError(f"Invalid yogini name: {maha.yogini}")

    # Calculate total duration in days
    maha_duration_days = (maha.end_date - maha.start_date).days

    antardashas = []
    current_date = maha.start_date

    # Generate 8 antardashas starting from the maha yogini
    for i in range(8):
        yogini_index = (starting_index + i) % 8
        yogini_name, planet_lord, yogini_years = YOGINI_DATA[yogini_index]

        # Proportional duration
        antardasha_days = int((yogini_years / TOTAL_CYCLE) * maha_duration_days)

        # Ensure we don't exceed the maha end date
        end_date = current_date + timedelta(days=antardasha_days)
        if end_date > maha.end_date:
            end_date = maha.end_date

        antardashas.append(
            {
                "yogini": yogini_name,
                "lord": planet_lord,
                "start_date": current_date,
                "end_date": end_date,
            }
        )

        current_date = end_date

        # Stop if we've reached the maha end date
        if current_date >= maha.end_date:
            break

    return antardashas
