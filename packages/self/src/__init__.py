"""Self-aware modules for 108 Vedic Astrology system.

Specialized analysis modules:
- Yoga detection (Raja, Dhana, Pancha Mahapurusha, etc.)
- Dosha detection and remedies
- Advanced chart interpretations
"""

from .ashtakavarga import (
    calculate_bhinnashtakavarga,
    calculate_sarvashtakavarga,
    get_transit_ashtakavarga_analysis,
    get_transit_ashtakavarga_score,
    get_transit_strength_modifier,
    interpret_ashtakavarga_score,
)
from .compatibility import (
    calculate_ashta_kuta,
    calculate_bhakoot_score,
    calculate_gana_score,
    calculate_graha_maitri_score,
    calculate_nadi_score,
    calculate_tara_score,
    calculate_varna_score,
    calculate_vashya_score,
    calculate_yoni_score,
    get_compatibility_verdict,
)
from .dosha_detector import DoshaDetector
from .strength import StrengthCalculator
from .yoga_detector import (
    YogaDetector,
    detect_all_yogas,
    detect_yoga,
    evaluate_condition,
    get_yoga_strength,
)

__all__ = [
    "DoshaDetector",
    "StrengthCalculator",
    "YogaDetector",
    "calculate_ashta_kuta",
    "calculate_bhakoot_score",
    "calculate_bhinnashtakavarga",
    "calculate_gana_score",
    "calculate_graha_maitri_score",
    "calculate_nadi_score",
    "calculate_sarvashtakavarga",
    "calculate_tara_score",
    "calculate_varna_score",
    "calculate_vashya_score",
    "calculate_yoni_score",
    "detect_all_yogas",
    "detect_yoga",
    "evaluate_condition",
    "get_compatibility_verdict",
    "get_transit_ashtakavarga_analysis",
    "get_transit_ashtakavarga_score",
    "get_transit_strength_modifier",
    "get_yoga_strength",
    "interpret_ashtakavarga_score",
]
