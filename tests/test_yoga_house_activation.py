"""Tests for yoga-house cross-reference (yoga_activation) module."""

from __future__ import annotations

from packages.core.src import DetectedYoga, Planet, YogaCategory
from packages.self.src.yoga_activation import (
    DUSTHANA_HOUSES,
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
    UPACHAYA_HOUSES,
    extract_yoga_houses,
    get_active_yogas,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_yoga(
    yoga_id: str = "test_yoga",
    name: str = "Test Yoga",
    category: str = "raja",
    strength: float = 0.8,
    planets: list[str] | None = None,
    is_present: bool = True,
) -> DetectedYoga:
    """Create a DetectedYoga for testing."""
    return DetectedYoga(
        yoga_id=yoga_id,
        name=name,
        category=YogaCategory(category),
        is_present=is_present,
        strength=strength,
        involved_planets=[Planet(p) for p in (planets or ["jupiter", "moon"])],
        description=f"Test yoga: {name}",
    )


def _make_activation(
    house: int,
    score: int = 50,
    grade: str = "active",
    double_transit: bool = False,
) -> dict:
    """Create a house activation dict for testing."""
    return {
        "house": house,
        "score": score,
        "grade": grade,
        "double_transit": double_transit,
        "planets_present": [],
        "planets_aspecting": [],
    }


# ---------------------------------------------------------------------------
# extract_yoga_houses tests
# ---------------------------------------------------------------------------


class TestExtractYogaHouses:
    """Tests for extract_yoga_houses."""

    def test_in_house_condition(self):
        rule = {
            "detection": {
                "conditions": [{"type": "in_house", "houses": [10]}],
            }
        }
        assert extract_yoga_houses(rule) == [10]

    def test_in_house_multiple(self):
        rule = {
            "detection": {
                "conditions": [{"type": "in_house", "houses": [2, 4, 5, 9, 10]}],
            }
        }
        assert extract_yoga_houses(rule) == [2, 4, 5, 9, 10]

    def test_in_houses_condition(self):
        rule = {
            "detection": {
                "conditions": [{"type": "in_houses", "houses": [1, 7]}],
            }
        }
        assert extract_yoga_houses(rule) == [1, 7]

    def test_in_kendra_condition(self):
        rule = {
            "detection": {
                "conditions": [{"type": "in_kendra"}],
            }
        }
        assert extract_yoga_houses(rule) == sorted(KENDRA_HOUSES)

    def test_in_trikona_condition(self):
        rule = {
            "detection": {
                "conditions": [{"type": "in_trikona"}],
            }
        }
        assert extract_yoga_houses(rule) == sorted(TRIKONA_HOUSES)

    def test_in_dusthana_condition(self):
        rule = {
            "detection": {
                "conditions": [{"type": "in_dusthana"}],
            }
        }
        assert extract_yoga_houses(rule) == sorted(DUSTHANA_HOUSES)

    def test_in_upachaya_condition(self):
        rule = {
            "detection": {
                "conditions": [{"type": "in_upachaya"}],
            }
        }
        assert extract_yoga_houses(rule) == sorted(UPACHAYA_HOUSES)

    def test_in_kendra_or_trikona_condition(self):
        rule = {
            "detection": {
                "conditions": [{"type": "in_kendra_or_trikona"}],
            }
        }
        expected = sorted(set(KENDRA_HOUSES) | set(TRIKONA_HOUSES))
        assert extract_yoga_houses(rule) == expected

    def test_lord_in_house_from_and_in(self):
        rule = {
            "detection": {
                "conditions": [
                    {"type": "lord_in_house", "from_house": 9, "in_house": 1},
                ],
            }
        }
        assert extract_yoga_houses(rule) == [1, 9]

    def test_lord_in_house_with_houses_list(self):
        rule = {
            "detection": {
                "conditions": [
                    {"type": "lord_in_house", "from_house": 9, "houses": [1, 4, 5, 7, 10]},
                ],
            }
        }
        assert extract_yoga_houses(rule) == [1, 4, 5, 7, 9, 10]

    def test_multiple_conditions_combined(self):
        rule = {
            "detection": {
                "conditions": [
                    {"type": "in_kendra"},
                    {"type": "in_house", "houses": [2, 11]},
                ],
            }
        }
        expected = sorted({1, 2, 4, 7, 10, 11})
        assert extract_yoga_houses(rule) == expected

    def test_empty_conditions(self):
        rule = {"detection": {"conditions": []}}
        assert extract_yoga_houses(rule) == []

    def test_no_detection_key(self):
        rule = {}
        assert extract_yoga_houses(rule) == []

    def test_unknown_condition_type(self):
        rule = {
            "detection": {
                "conditions": [{"type": "conjunct"}],
            }
        }
        assert extract_yoga_houses(rule) == []

    def test_deduplication(self):
        rule = {
            "detection": {
                "conditions": [
                    {"type": "in_kendra"},
                    {"type": "in_house", "houses": [1, 4]},
                ],
            }
        }
        # 1 and 4 appear in both, should not duplicate
        assert extract_yoga_houses(rule) == [1, 4, 7, 10]

    def test_invalid_house_numbers_filtered(self):
        rule = {
            "detection": {
                "conditions": [{"type": "in_house", "houses": [0, 1, 13, 7]}],
            }
        }
        assert extract_yoga_houses(rule) == [1, 7]


# ---------------------------------------------------------------------------
# get_active_yogas tests
# ---------------------------------------------------------------------------


class TestGetActiveYogas:
    """Tests for get_active_yogas."""

    def test_empty_yogas(self):
        result = get_active_yogas([], [_make_activation(1)])
        assert result == []

    def test_empty_activations(self):
        yogas = [_make_yoga()]
        rules = {
            "test_yoga": {
                "detection": {"conditions": [{"type": "in_kendra"}]},
            }
        }
        result = get_active_yogas(yogas, [], yoga_rules=rules)
        assert len(result) == 1
        assert result[0]["is_active_now"] is False

    def test_yoga_active_via_double_transit(self):
        yogas = [_make_yoga(yoga_id="sasa_yoga", name="Sasa Yoga")]
        rules = {
            "sasa_yoga": {
                "detection": {"conditions": [{"type": "in_house", "houses": [10]}]},
            }
        }
        activations = [_make_activation(10, score=78, double_transit=True)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        assert len(result) == 1
        assert result[0]["is_active_now"] is True
        assert 10 in result[0]["activated_houses"]
        assert "double transit" in result[0]["activation_reason"]

    def test_yoga_active_via_high_score(self):
        yogas = [_make_yoga()]
        rules = {
            "test_yoga": {
                "detection": {"conditions": [{"type": "in_house", "houses": [5]}]},
            }
        }
        activations = [_make_activation(5, score=55, double_transit=False)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        assert result[0]["is_active_now"] is True
        assert 5 in result[0]["activated_houses"]

    def test_yoga_not_active_low_score(self):
        yogas = [_make_yoga()]
        rules = {
            "test_yoga": {
                "detection": {"conditions": [{"type": "in_house", "houses": [3]}]},
            }
        }
        activations = [_make_activation(3, score=20, double_transit=False)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        assert result[0]["is_active_now"] is False
        assert result[0]["activated_houses"] == []

    def test_sorting_active_first(self):
        yogas = [
            _make_yoga(yoga_id="inactive_yoga", name="Inactive", strength=0.9),
            _make_yoga(yoga_id="active_yoga", name="Active", strength=0.5),
        ]
        rules = {
            "inactive_yoga": {
                "detection": {"conditions": [{"type": "in_house", "houses": [3]}]},
            },
            "active_yoga": {
                "detection": {"conditions": [{"type": "in_house", "houses": [10]}]},
            },
        }
        activations = [
            _make_activation(3, score=10),
            _make_activation(10, score=80, double_transit=True),
        ]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        assert result[0]["yoga_id"] == "active_yoga"
        assert result[0]["is_active_now"] is True
        assert result[1]["yoga_id"] == "inactive_yoga"
        assert result[1]["is_active_now"] is False

    def test_sorting_by_strength_within_active(self):
        yogas = [
            _make_yoga(yoga_id="weak", name="Weak Active", strength=0.4),
            _make_yoga(yoga_id="strong", name="Strong Active", strength=0.9),
        ]
        rules = {
            "weak": {
                "detection": {"conditions": [{"type": "in_house", "houses": [10]}]},
            },
            "strong": {
                "detection": {"conditions": [{"type": "in_house", "houses": [10]}]},
            },
        }
        activations = [_make_activation(10, score=60)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        assert result[0]["yoga_id"] == "strong"
        assert result[1]["yoga_id"] == "weak"

    def test_yoga_not_present_excluded(self):
        yogas = [_make_yoga(is_present=False)]
        rules = {
            "test_yoga": {
                "detection": {"conditions": [{"type": "in_kendra"}]},
            }
        }
        activations = [_make_activation(1, score=80, double_transit=True)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)
        assert result == []

    def test_no_rules_provided(self):
        yogas = [_make_yoga()]
        activations = [_make_activation(1, score=80, double_transit=True)]
        result = get_active_yogas(yogas, activations, yoga_rules=None)

        # Without rules, involved_houses is empty, so yoga is not active
        assert len(result) == 1
        assert result[0]["is_active_now"] is False
        assert result[0]["involved_houses"] == []

    def test_yoga_id_not_in_rules(self):
        yogas = [_make_yoga(yoga_id="missing_rule")]
        rules = {"other_yoga": {"detection": {"conditions": []}}}
        activations = [_make_activation(1, score=80)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        assert len(result) == 1
        assert result[0]["is_active_now"] is False

    def test_kendra_yoga_multiple_houses_activated(self):
        yogas = [_make_yoga(yoga_id="kendra_yoga")]
        rules = {
            "kendra_yoga": {
                "detection": {"conditions": [{"type": "in_kendra"}]},
            }
        }
        activations = [
            _make_activation(1, score=60),
            _make_activation(4, score=30),
            _make_activation(7, score=45),
            _make_activation(10, score=80, double_transit=True),
        ]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        assert result[0]["is_active_now"] is True
        # Houses 1, 7, 10 are activated (score >= 40 or double transit)
        assert 1 in result[0]["activated_houses"]
        assert 4 not in result[0]["activated_houses"]
        assert 7 in result[0]["activated_houses"]
        assert 10 in result[0]["activated_houses"]

    def test_output_fields_complete(self):
        yogas = [_make_yoga(yoga_id="gk", name="Gaj Kesari", category="raja", strength=0.85)]
        rules = {
            "gk": {
                "detection": {"conditions": [{"type": "in_house", "houses": [1]}]},
            }
        }
        activations = [_make_activation(1, score=50)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        r = result[0]
        assert r["yoga_id"] == "gk"
        assert r["yoga_name"] == "Gaj Kesari"
        assert r["category"] == "raja"
        assert r["strength"] == 0.85
        assert r["involved_planets"] == ["jupiter", "moon"]
        assert r["involved_houses"] == [1]
        assert r["activated_houses"] == [1]
        assert r["is_active_now"] is True
        assert isinstance(r["activation_reason"], str)

    def test_double_transit_low_score_still_activates(self):
        """Double transit should activate even if score is below threshold."""
        yogas = [_make_yoga(yoga_id="dt_yoga")]
        rules = {
            "dt_yoga": {
                "detection": {"conditions": [{"type": "in_house", "houses": [8]}]},
            }
        }
        activations = [_make_activation(8, score=25, double_transit=True)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        assert result[0]["is_active_now"] is True

    def test_multiple_yogas_mixed_activity(self):
        yogas = [
            _make_yoga(yoga_id="y1", name="Y1", strength=0.9),
            _make_yoga(yoga_id="y2", name="Y2", strength=0.7),
            _make_yoga(yoga_id="y3", name="Y3", strength=0.5),
        ]
        rules = {
            "y1": {"detection": {"conditions": [{"type": "in_house", "houses": [1]}]}},
            "y2": {"detection": {"conditions": [{"type": "in_house", "houses": [6]}]}},
            "y3": {"detection": {"conditions": [{"type": "in_house", "houses": [10]}]}},
        }
        activations = [
            _make_activation(1, score=80),
            _make_activation(6, score=20),
            _make_activation(10, score=60),
        ]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)

        # Y1 (active, 0.9) and Y3 (active, 0.5) first, Y2 (inactive) last
        assert result[0]["yoga_id"] == "y1"
        assert result[0]["is_active_now"] is True
        assert result[1]["yoga_id"] == "y3"
        assert result[1]["is_active_now"] is True
        assert result[2]["yoga_id"] == "y2"
        assert result[2]["is_active_now"] is False

    def test_activation_threshold_boundary(self):
        """Score exactly 40 should activate."""
        yogas = [_make_yoga(yoga_id="boundary")]
        rules = {
            "boundary": {
                "detection": {"conditions": [{"type": "in_house", "houses": [2]}]},
            }
        }
        activations = [_make_activation(2, score=40, double_transit=False)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)
        assert result[0]["is_active_now"] is True

    def test_activation_threshold_below(self):
        """Score 39 should NOT activate (without double transit)."""
        yogas = [_make_yoga(yoga_id="below")]
        rules = {
            "below": {
                "detection": {"conditions": [{"type": "in_house", "houses": [2]}]},
            }
        }
        activations = [_make_activation(2, score=39, double_transit=False)]
        result = get_active_yogas(yogas, activations, yoga_rules=rules)
        assert result[0]["is_active_now"] is False

    def test_import_from_package(self):
        """Verify functions are exported from the package."""
        from packages.self.src import extract_yoga_houses as eyh
        from packages.self.src import get_active_yogas as gay

        assert callable(eyh)
        assert callable(gay)
