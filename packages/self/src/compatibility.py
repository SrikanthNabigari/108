"""Kundali Matching (Ashta Kuta) compatibility analysis.

Implements the traditional eight-fold marriage compatibility system
using rules from knowledge/rules/compatibility_rules.json.
"""

from typing import Any

from packages.core.src.knowledge_loader import load_rules


def _get_rules() -> dict:
    """Load compatibility rules (JSON has no wrapper key)."""
    return load_rules("compatibility_rules")


# Rashi lords for Graha Maitri
RASHI_LORDS = {
    1: "Mars",
    2: "Venus",
    3: "Mercury",
    4: "Moon",
    5: "Sun",
    6: "Mercury",
    7: "Venus",
    8: "Mars",
    9: "Jupiter",
    10: "Saturn",
    11: "Saturn",
    12: "Jupiter",
}

# Rashi to Varna mapping
RASHI_VARNA = {
    1: "Kshatriya",
    2: "Vaishya",
    3: "Shudra",
    4: "Brahmin",
    5: "Kshatriya",
    6: "Vaishya",
    7: "Shudra",
    8: "Brahmin",
    9: "Kshatriya",
    10: "Vaishya",
    11: "Shudra",
    12: "Brahmin",
}

# Rashi to Vashya category mapping
RASHI_VASHYA = {
    1: "Pashava",
    2: "Pashava",
    3: "Manava",
    4: "Jalaja",
    5: "Vanaspatya",
    6: "Manava",
    7: "Manava",
    8: "Ketu",
    9: "Manava",
    10: "Jalaja",
    11: "Manava",
    12: "Jalaja",
}


def calculate_varna_score(boy_rashi: int, girl_rashi: int) -> float:
    """Calculate Varna Kuta score (max 1 point).

    Args:
        boy_rashi: Boy's Moon rashi (1-12)
        girl_rashi: Girl's Moon rashi (1-12)
    """
    rules = _get_rules()
    matrix = rules.get("varna_compatibility", {}).get("scoring_matrix", {})

    boy_varna = RASHI_VARNA.get(boy_rashi, "Shudra")
    girl_varna = RASHI_VARNA.get(girl_rashi, "Shudra")

    return matrix.get(boy_varna, {}).get(girl_varna, 0.5)


def calculate_vashya_score(boy_rashi: int, girl_rashi: int) -> float:
    """Calculate Vashya Kuta score (max 2 points).

    Args:
        boy_rashi: Boy's Moon rashi (1-12)
        girl_rashi: Girl's Moon rashi (1-12)
    """
    rules = _get_rules()
    dominance = rules.get("vashya_compatibility", {}).get("dominance_order", {})

    boy_vashya = RASHI_VASHYA.get(boy_rashi, "Manava")
    girl_vashya = RASHI_VASHYA.get(girl_rashi, "Manava")

    if boy_vashya == girl_vashya:
        return 2.0

    boy_dominates = girl_vashya in dominance.get(boy_vashya, [])
    girl_dominates = boy_vashya in dominance.get(girl_vashya, [])

    if boy_dominates and girl_dominates:
        return 1.0
    if boy_dominates or girl_dominates:
        return 1.0
    return 0.0


def calculate_tara_score(boy_nakshatra_idx: int, girl_nakshatra_idx: int) -> float:
    """Calculate Tara Kuta score (max 3 points).

    Args:
        boy_nakshatra_idx: Boy's nakshatra index (0-26)
        girl_nakshatra_idx: Girl's nakshatra index (0-26)
    """
    rules = _get_rules()
    taras = rules.get("tara_compatibility", {}).get("taras", [])

    # Count from boy's nakshatra to girl's
    diff = ((girl_nakshatra_idx - boy_nakshatra_idx) % 27) + 1
    tara_num = ((diff - 1) % 9) + 1

    for tara in taras:
        if tara["number"] == tara_num:
            return tara["points"]

    return 1.5  # Default moderate


def calculate_yoni_score(boy_nakshatra: str, girl_nakshatra: str) -> float:
    """Calculate Yoni Kuta score (max 4 points).

    Args:
        boy_nakshatra: Boy's nakshatra name
        girl_nakshatra: Girl's nakshatra name
    """
    rules = _get_rules()
    yoni_data = rules.get("yoni_compatibility", {})
    mapping = yoni_data.get("nakshatra_yoni_mapping", {})
    matrix = yoni_data.get("animal_compatibility_matrix", {})

    boy_info = mapping.get(boy_nakshatra, {})
    girl_info = mapping.get(girl_nakshatra, {})

    if not boy_info or not girl_info:
        return 2.0  # Default moderate

    boy_animal = boy_info.get("yoni", "")
    girl_animal = girl_info.get("yoni", "")
    boy_num = boy_info.get("animal_number", 0)

    # Look up in animal compatibility matrix
    key = f"{boy_num}_{boy_animal}"
    if key in matrix:
        raw_score = matrix[key].get(girl_animal, 2)
        return float(raw_score)

    return 2.0


def calculate_graha_maitri_score(boy_rashi: int, girl_rashi: int) -> float:
    """Calculate Graha Maitri score (max 5 points).

    Args:
        boy_rashi: Boy's Moon rashi (1-12)
        girl_rashi: Girl's Moon rashi (1-12)
    """
    rules = _get_rules()
    matrix = rules.get("graha_maitri", {}).get("friendship_matrix", {})

    boy_lord = RASHI_LORDS.get(boy_rashi, "Sun")
    girl_lord = RASHI_LORDS.get(girl_rashi, "Sun")

    return float(matrix.get(boy_lord, {}).get(girl_lord, 3))


def calculate_gana_score(boy_gana: str, girl_gana: str) -> float:
    """Calculate Gana Kuta score (max 6 points).

    Args:
        boy_gana: Boy's gana (Deva, Manushya, Rakshasa)
        girl_gana: Girl's gana (Deva, Manushya, Rakshasa)
    """
    rules = _get_rules()
    matrix = rules.get("gana_compatibility", {}).get("compatibility_matrix", {})

    boy_g = boy_gana.capitalize()
    girl_g = girl_gana.capitalize()

    return float(matrix.get(boy_g, {}).get(girl_g, 3))


def calculate_bhakoot_score(boy_rashi: int, girl_rashi: int) -> float:
    """Calculate Bhakoot Kuta score (max 7 points).

    Args:
        boy_rashi: Boy's Moon rashi (1-12)
        girl_rashi: Girl's Moon rashi (1-12)
    """
    rules = _get_rules()
    dosha_positions = (
        rules.get("bhakoot_compatibility", {}).get("rules", {}).get("dosha_positions", [])
    )

    # Check dosha positions (both directions)
    for dosha in dosha_positions:
        h = dosha.get("husband_rashi", 0)
        w = dosha.get("wife_rashi", 0)
        diff_hw = ((girl_rashi - boy_rashi) % 12) + 1
        diff_wh = ((boy_rashi - girl_rashi) % 12) + 1
        target_diff = ((w - h) % 12) + 1

        if diff_hw == target_diff or diff_wh == target_diff:
            return 0.0

    return 7.0


def calculate_nadi_score(boy_nadi: str, girl_nadi: str) -> float:
    """Calculate Nadi Kuta score (max 8 points).

    Args:
        boy_nadi: Boy's nadi (Adi, Madhya, Antya)
        girl_nadi: Girl's nadi (Adi, Madhya, Antya)
    """
    rules = _get_rules()
    matrix = rules.get("nadi_compatibility", {}).get("compatibility_matrix", {})

    boy_n = boy_nadi.capitalize()
    girl_n = girl_nadi.capitalize()

    return float(matrix.get(boy_n, {}).get(girl_n, 4))


def calculate_ashta_kuta(
    boy_rashi: int,
    girl_rashi: int,
    boy_nakshatra: str,
    girl_nakshatra: str,
    boy_nakshatra_idx: int,
    girl_nakshatra_idx: int,
    boy_gana: str,
    girl_gana: str,
    boy_nadi: str,
    girl_nadi: str,
) -> dict[str, Any]:
    """Calculate complete Ashta Kuta compatibility.

    Args:
        boy_rashi: Boy's Moon rashi (1-12)
        girl_rashi: Girl's Moon rashi (1-12)
        boy_nakshatra: Boy's nakshatra name
        girl_nakshatra: Girl's nakshatra name
        boy_nakshatra_idx: Boy's nakshatra index (0-26)
        girl_nakshatra_idx: Girl's nakshatra index (0-26)
        boy_gana: Boy's gana (Deva/Manushya/Rakshasa)
        girl_gana: Girl's gana (Deva/Manushya/Rakshasa)
        boy_nadi: Boy's nadi (Adi/Madhya/Antya)
        girl_nadi: Girl's nadi (Adi/Madhya/Antya)

    Returns:
        Complete compatibility result with all 8 kuta scores
    """
    scores = {
        "varna": {
            "name": "Varna",
            "score": calculate_varna_score(boy_rashi, girl_rashi),
            "max_score": 1.0,
            "description": "Spiritual compatibility",
        },
        "vashya": {
            "name": "Vashya",
            "score": calculate_vashya_score(boy_rashi, girl_rashi),
            "max_score": 2.0,
            "description": "Mutual attraction and dominance",
        },
        "tara": {
            "name": "Tara",
            "score": calculate_tara_score(boy_nakshatra_idx, girl_nakshatra_idx),
            "max_score": 3.0,
            "description": "Birth star compatibility",
        },
        "yoni": {
            "name": "Yoni",
            "score": calculate_yoni_score(boy_nakshatra, girl_nakshatra),
            "max_score": 4.0,
            "description": "Sexual and physical compatibility",
        },
        "graha_maitri": {
            "name": "Graha Maitri",
            "score": calculate_graha_maitri_score(boy_rashi, girl_rashi),
            "max_score": 5.0,
            "description": "Mental compatibility",
        },
        "gana": {
            "name": "Gana",
            "score": calculate_gana_score(boy_gana, girl_gana),
            "max_score": 6.0,
            "description": "Temperament compatibility",
        },
        "bhakoot": {
            "name": "Bhakoot",
            "score": calculate_bhakoot_score(boy_rashi, girl_rashi),
            "max_score": 7.0,
            "description": "Health, wealth, and progeny",
        },
        "nadi": {
            "name": "Nadi",
            "score": calculate_nadi_score(boy_nadi, girl_nadi),
            "max_score": 8.0,
            "description": "Genetic and health compatibility",
        },
    }

    total = sum(s["score"] for s in scores.values())
    verdict = get_compatibility_verdict(total)

    # Check critical doshas
    critical = []
    if scores["nadi"]["score"] == 0:
        critical.append({"dosha": "Nadi Dosha", "severity": "Critical"})
    if scores["bhakoot"]["score"] == 0:
        critical.append({"dosha": "Bhakoot Dosha", "severity": "High"})
    if scores["gana"]["score"] <= 1:
        critical.append({"dosha": "Gana Dosha", "severity": "High"})

    return {
        "total_score": total,
        "max_score": 36.0,
        "percentage": round((total / 36.0) * 100, 1),
        "verdict": verdict,
        "kuta_scores": scores,
        "critical_doshas": critical,
    }


def get_compatibility_verdict(total_score: float) -> str:
    """Get compatibility verdict based on total score.

    Args:
        total_score: Total Ashta Kuta score (0-36)

    Returns:
        Verdict string
    """
    if total_score >= 33:
        return "Excellent"
    if total_score >= 25:
        return "Good"
    if total_score >= 18:
        return "Average"
    return "Not Recommended"
