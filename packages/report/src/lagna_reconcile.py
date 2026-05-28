"""Lagna reconciliation for sign-cusp edge cases.

Pure sidereal Lahiri ascendants within ~2° of a sign boundary often disagree
with the lagna shown by popular Indian commercial software (which sometimes
treats the cusp leniently or uses slightly different ayanamsa internally).

For the customer-facing 108 reports we default to the convention the customer
is most likely to have already seen elsewhere. This module decides:

- If the sidereal asc is ≥3° inside its sign → use that sign (no ambiguity)
- If within ≤3° of the next sign → check whether popular software would
  show the next sign (typical convention: tropical asc + sidereal planets);
  if so, use the next sign and emit a `lagna_note` for the report's
  Sources & Method section.

The reconciled lagna only changes house assignments — planet sidereal
positions stay identical.
"""

from __future__ import annotations

_RASHI = [
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


def reconcile_lagna(
    asc_sidereal: float,
    asc_tropical: float,
    cusp_tolerance: float = 1.5,
) -> tuple[int, float, str | None]:
    """Return (lagna_idx, lagna_degree, optional_note).

    MVP convention: use Lahiri sidereal. Emit a note ONLY when the asc is
    within `cusp_tolerance` degrees of a sign boundary (where commercial
    software routinely disagrees with us).

    Args:
        asc_sidereal: Pure sidereal asc in degrees (0-360).
        asc_tropical: Tropical asc (kept for future tropical/sidereal
            reconciliation policies; unused in MVP).
        cusp_tolerance: How close to a sign boundary (start or end) before
            we add a heads-up note.

    Returns:
        (lagna_idx 0-11, lagna_degree 0-30, optional reconciliation note)
    """
    sid_idx = int(asc_sidereal // 30) % 12
    sid_deg = asc_sidereal % 30

    # Distance to the nearest sign boundary
    deg_from_start = sid_deg
    deg_to_next = 30 - sid_deg

    note: str | None = None
    if deg_from_start <= cusp_tolerance:
        prev_sign = _RASHI[(sid_idx - 1) % 12].title()
        note = (
            f"Lagna at sign cusp ({sid_deg:.2f}° {_RASHI[sid_idx].title()}). "
            f"Some software may show this as late {prev_sign} — birth-time "
            f"accuracy of ±5 minutes can shift the lagna at a cusp."
        )
    elif deg_to_next <= cusp_tolerance:
        next_sign = _RASHI[(sid_idx + 1) % 12].title()
        note = (
            f"Lagna at sign cusp ({sid_deg:.2f}° {_RASHI[sid_idx].title()}). "
            f"Some software may show this as early {next_sign} — birth-time "
            f"accuracy of ±5 minutes can shift the lagna at a cusp."
        )

    return sid_idx, sid_deg, note
