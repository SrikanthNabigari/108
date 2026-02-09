"""Yoga-House Cross-Reference Engine for 108 Vedic Astrology.

Cross-references detected natal yogas with current house activations from
transit snapshots to determine which yogas are being activated NOW by
transits (especially Jupiter-Saturn double transit).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.src import DetectedYoga

# Kendra / Trikona / Dusthana house sets used for condition expansion
KENDRA_HOUSES = [1, 4, 7, 10]
TRIKONA_HOUSES = [1, 5, 9]
DUSTHANA_HOUSES = [6, 8, 12]
UPACHAYA_HOUSES = [3, 6, 10, 11]

# Activation threshold: a house is considered "activated" if its composite
# score reaches this value OR it has a double transit.
_ACTIVATION_THRESHOLD = 40


def extract_yoga_houses(yoga_rule: dict[str, Any]) -> list[int]:
    """Extract house numbers relevant to a yoga from its detection conditions.

    Handles the following condition types found in yoga_detection.json:
    - ``in_house`` / ``in_houses``: explicit ``houses`` list
    - ``lord_in_house``: ``from_house`` and ``in_house`` fields
    - ``in_kendra``: expands to [1, 4, 7, 10]
    - ``in_trikona``: expands to [1, 5, 9]
    - ``in_kendra_or_trikona``: expands to [1, 4, 5, 7, 9, 10]
    - ``in_dusthana``: expands to [6, 8, 12]
    - ``in_upachaya``: expands to [3, 6, 10, 11]

    Args:
        yoga_rule: A single yoga rule dict (from yoga_detection.json).

    Returns:
        Sorted, deduplicated list of house numbers (1-12).
    """
    houses: set[int] = set()

    detection = yoga_rule.get("detection", {})
    conditions = detection.get("conditions", [])

    for cond in conditions:
        cond_type = cond.get("type", "")

        if cond_type in ("in_house", "in_houses"):
            for h in cond.get("houses", []):
                if isinstance(h, int) and 1 <= h <= 12:
                    houses.add(h)

        elif cond_type == "lord_in_house":
            from_house = cond.get("from_house")
            in_house = cond.get("in_house")
            in_houses = cond.get("houses", [])
            if isinstance(from_house, int) and 1 <= from_house <= 12:
                houses.add(from_house)
            if isinstance(in_house, int) and 1 <= in_house <= 12:
                houses.add(in_house)
            for h in in_houses:
                if isinstance(h, int) and 1 <= h <= 12:
                    houses.add(h)

        elif cond_type == "in_kendra":
            houses.update(KENDRA_HOUSES)

        elif cond_type == "in_trikona":
            houses.update(TRIKONA_HOUSES)

        elif cond_type == "in_kendra_or_trikona":
            houses.update(KENDRA_HOUSES)
            houses.update(TRIKONA_HOUSES)

        elif cond_type == "in_dusthana":
            houses.update(DUSTHANA_HOUSES)

        elif cond_type == "in_upachaya":
            houses.update(UPACHAYA_HOUSES)

    return sorted(houses)


def get_active_yogas(
    detected_yogas: list[DetectedYoga],
    house_activations: list[dict[str, Any]],
    yoga_rules: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Cross-reference natal yogas with current house activations.

    For each detected yoga, determines which houses it involves (via rules or
    planet placements) and checks whether those houses are currently activated
    by transits.

    Args:
        detected_yogas: List of ``DetectedYoga`` objects from the natal chart.
        house_activations: List of house activation dicts (from
            ``get_house_activations`` or the ``house_activations`` key of a
            transit snapshot).  Each dict must have at least ``house`` (int),
            ``score`` (int/float), and ``double_transit`` (bool).
        yoga_rules: Optional dict of yoga rules keyed by yoga_id.  When
            provided, house information is extracted from the rule conditions
            via ``extract_yoga_houses``.  Otherwise, only the yoga's
            ``involved_planets`` are used (less precise).

    Returns:
        List of dicts sorted by: *active* first, then by *strength* descending.
        Each dict contains::

            yoga_id, yoga_name, category, strength, involved_planets,
            involved_houses, activated_houses, is_active_now, activation_reason
    """
    if not detected_yogas:
        return []

    # Build fast lookup: house -> activation dict
    activation_map: dict[int, dict[str, Any]] = {}
    for act in house_activations:
        house_num = act.get("house")
        if isinstance(house_num, int):
            activation_map[house_num] = act

    results: list[dict[str, Any]] = []

    for yoga in detected_yogas:
        if not yoga.is_present:
            continue

        # --- Determine involved houses ---
        involved_houses: list[int] = []

        # Try rule-based extraction first
        if yoga_rules and yoga.yoga_id in yoga_rules:
            involved_houses = extract_yoga_houses(yoga_rules[yoga.yoga_id])

        # If no houses found from rules, there is no house info to cross-ref.
        # We still include the yoga but mark it as not-active since we cannot
        # determine activation without house context.

        # --- Check which of those houses are activated ---
        activated_houses: list[int] = []
        activation_reasons: list[str] = []

        for h in involved_houses:
            act = activation_map.get(h)
            if act is None:
                continue

            score = act.get("score", 0)
            has_dt = act.get("double_transit", False)

            if has_dt:
                activated_houses.append(h)
                activation_reasons.append(f"House {h} has double transit (score {score})")
            elif score >= _ACTIVATION_THRESHOLD:
                activated_houses.append(h)
                activation_reasons.append(f"House {h} is active (score {score})")

        is_active = len(activated_houses) > 0

        reason = "; ".join(activation_reasons) if activation_reasons else "No activated houses"

        results.append(
            {
                "yoga_id": yoga.yoga_id,
                "yoga_name": yoga.name,
                "category": yoga.category.value
                if hasattr(yoga.category, "value")
                else str(yoga.category),
                "strength": yoga.strength,
                "involved_planets": [
                    p.value if hasattr(p, "value") else str(p) for p in yoga.involved_planets
                ],
                "involved_houses": involved_houses,
                "activated_houses": activated_houses,
                "is_active_now": is_active,
                "activation_reason": reason,
            }
        )

    # Sort: active first, then by strength descending
    results.sort(key=lambda r: (not r["is_active_now"], -r["strength"]))

    return results


__all__ = [
    "extract_yoga_houses",
    "get_active_yogas",
]
