"""Self-aware modules for 108 Vedic Astrology system.

Specialized analysis modules:
- Yoga detection (Raja, Dhana, Pancha Mahapurusha, etc.)
- Dosha detection and remedies
- Advanced chart interpretations
"""

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
    "detect_all_yogas",
    "detect_yoga",
    "evaluate_condition",
    "get_yoga_strength",
]
