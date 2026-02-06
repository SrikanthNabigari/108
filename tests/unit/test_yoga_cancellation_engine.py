"""Tests for the comprehensive yoga cancellation engine (yoga_cancellation.py).

This is a SEPARATE test file from test_yoga_cancellation.py which tests
the YogaDetector internal methods. This tests the standalone engine.
"""

from packages.core.src.constants import Planet, Rashi
from packages.self.src.yoga_cancellation import (
    apply_cancellations_to_chart,
    check_yoga_cancellation,
    get_cancellation_rules,
)


def _make_planets(**kwargs):
    """Create a planet dict from keyword arguments.

    Each kwarg is planet_name=(rashi, longitude, house, is_retrograde).
    """
    planets = {}
    for name, vals in kwargs.items():
        rashi, lon, house = vals[0], vals[1], vals[2]
        is_retro = vals[3] if len(vals) > 3 else False
        planets[Planet(name)] = {
            "rashi": Rashi(rashi),
            "longitude": lon,
            "house": house,
            "is_retrograde": is_retro,
            "latitude": 0.0,
        }
    return planets


# ==========================================================
# Task 1: Yoga Cancellation Engine tests (25+ tests)
# ==========================================================


class TestGetCancellationRules:
    """Test loading cancellation rules from knowledge base."""

    def test_load_pancha_mahapurusha_rules(self):
        rules = get_cancellation_rules("pancha_mahapurusha")
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_load_raja_yoga_rules(self):
        rules = get_cancellation_rules("raja_yoga")
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_load_dhana_yoga_rules(self):
        rules = get_cancellation_rules("dhana_yoga")
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_load_gajakesari_rules(self):
        rules = get_cancellation_rules("gajakesari")
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_load_unknown_type_returns_general(self):
        rules = get_cancellation_rules("unknown_type_xyz")
        assert isinstance(rules, list)
        # Falls back to general cancellation conditions
        assert len(rules) > 0

    def test_alias_types_map_correctly(self):
        """Check that aliases like 'hamsa', 'ruchaka' map to pancha_mahapurusha."""
        r1 = get_cancellation_rules("hamsa")
        r2 = get_cancellation_rules("pancha_mahapurusha")
        assert r1 == r2


class TestCheckYogaCancellationCombustion:
    """Test yoga cancellation due to combustion."""

    def test_combust_planet_cancels_yoga(self):
        """Planet very close to Sun should cancel yoga."""
        planets = _make_planets(
            sun=("aries", 15.0, 1),
            mars=("aries", 14.0, 1),  # Mars 1 degree from Sun = combust
            moon=("taurus", 40.0, 2),
            jupiter=("leo", 128.0, 5),
        )
        yoga = {"category": "other", "involved_planets": ["mars"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 15.0)
        assert result["cancelled"] is True
        assert "combust" in result["reason"].lower()

    def test_non_combust_planet_not_cancelled(self):
        """Planet far from Sun should NOT cancel."""
        planets = _make_planets(
            sun=("aries", 15.0, 1),
            mars=("leo", 128.0, 5),  # Mars far from Sun
            moon=("taurus", 40.0, 2),
            jupiter=("sagittarius", 248.0, 9),
        )
        yoga = {"category": "other", "involved_planets": ["mars"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 15.0)
        assert result["cancelled"] is False

    def test_sun_cannot_be_combust(self):
        """Sun cannot be combust (it causes combustion)."""
        planets = _make_planets(
            sun=("aries", 15.0, 1),
            moon=("taurus", 40.0, 2),
        )
        yoga = {"category": "other", "involved_planets": ["sun"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 15.0)
        assert result["cancelled"] is False

    def test_rahu_ketu_not_combust(self):
        """Rahu/Ketu cannot be combust."""
        planets = _make_planets(
            sun=("aries", 15.0, 1),
            rahu=("aries", 14.0, 1),
            moon=("taurus", 40.0, 2),
        )
        yoga = {"category": "other", "involved_planets": ["rahu"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 15.0)
        assert result["cancelled"] is False


class TestCheckYogaCancellationDebilitation:
    """Test yoga cancellation due to debilitation."""

    def test_debilitated_without_neecha_bhanga_cancels(self):
        """Debilitated planet without Neecha Bhanga should cancel."""
        # Jupiter debilitated in Capricorn, house 3 (not kendra)
        # Saturn (lord of Cap) in Gemini house 6 (not kendra from Scorpio lagna)
        planets = _make_planets(
            sun=("leo", 130.0, 10),
            moon=("virgo", 160.0, 11),
            jupiter=("capricorn", 275.0, 3),
            saturn=("gemini", 70.0, 8),
            mars=("aries", 5.0, 6),
            mercury=("leo", 135.0, 10),
            venus=("cancer", 100.0, 9),
        )
        yoga = {"category": "other", "involved_planets": ["jupiter"]}
        result = check_yoga_cancellation(yoga, planets, "scorpio", 130.0)
        assert result["cancelled"] is True
        assert "debilitated" in result["reason"].lower()

    def test_debilitated_in_kendra_has_neecha_bhanga(self):
        """Debilitated in kendra = Neecha Bhanga, should NOT cancel."""
        # Jupiter debilitated in Capricorn but in house 10 (kendra)
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            jupiter=("capricorn", 275.0, 10),  # Kendra = NB
            saturn=("gemini", 70.0, 3),
            mars=("aries", 5.0, 1),
            mercury=("virgo", 165.0, 6),
            venus=("pisces", 345.0, 12),
        )
        yoga = {"category": "other", "involved_planets": ["jupiter"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        # Jupiter in kendra = Neecha Bhanga, not fully cancelled but may be partial
        assert result["cancelled"] is False

    def test_debilitated_retrograde_has_neecha_bhanga(self):
        """Debilitated + retrograde = Neecha Bhanga, should NOT fully cancel."""
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            mars=("cancer", 95.0, 3, True),  # Mars debilitated + retrograde
            mercury=("virgo", 165.0, 6),
            jupiter=("sagittarius", 248.0, 9),
            venus=("libra", 185.0, 7),
            saturn=("aquarius", 310.0, 11),
        )
        yoga = {"category": "other", "involved_planets": ["mars"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is False  # Has Neecha Bhanga (retrograde)


class TestCheckYogaCancellationMaleficAffliction:
    """Test yoga cancellation due to malefic affliction."""

    def test_two_malefics_conjunct_cancels(self):
        """Planet conjunct 2+ malefics should cancel."""
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            jupiter=("sagittarius", 248.0, 9),
            mars=("sagittarius", 250.0, 9),
            saturn=("sagittarius", 252.0, 9),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        yoga = {"category": "other", "involved_planets": ["jupiter"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is True
        assert "malefic" in result["reason"].lower()

    def test_one_malefic_not_cancelled(self):
        """Planet conjunct only 1 malefic should NOT cancel."""
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            jupiter=("sagittarius", 248.0, 9),
            saturn=("sagittarius", 252.0, 9),  # 1 malefic conjunct
            mars=("aries", 5.0, 1),  # Not in Sagittarius
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        yoga = {"category": "other", "involved_planets": ["jupiter"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is False
        # Should be partially weakened
        if result["partial"]:
            assert result["modified_strength"] < 1.0


class TestPanchaMahapurushaCancellation:
    """Test Pancha Mahapurusha-specific cancellation."""

    def test_ruchaka_yoga_cancelled_by_combustion(self):
        """Ruchaka Yoga (Mars) cancelled when Mars is combust."""
        planets = _make_planets(
            sun=("capricorn", 280.0, 10),
            mars=("capricorn", 279.0, 10),  # 1 degree from Sun
            moon=("taurus", 40.0, 2),
            jupiter=("leo", 128.0, 5),
            mercury=("aquarius", 310.0, 11),
            venus=("pisces", 345.0, 12),
            saturn=("libra", 185.0, 7),
        )
        yoga = {
            "category": "pancha_mahapurusha",
            "involved_planets": ["mars"],
            "name": "Ruchaka Yoga",
        }
        result = check_yoga_cancellation(yoga, planets, "aries", 280.0)
        assert result["cancelled"] is True


class TestRajaYogaCancellation:
    """Test Raja Yoga-specific cancellation."""

    def test_raja_yoga_cancelled_mutual_dusthana(self):
        """Raja Yoga cancelled when forming planets are in 6/8/12 from each other."""
        # Jupiter in Sagittarius, Saturn in Cancer (8th from Sagittarius)
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            jupiter=("sagittarius", 248.0, 9),
            saturn=("cancer", 95.0, 4),  # 8th from Sagittarius
            mars=("aries", 5.0, 1),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        yoga = {
            "category": "raja_yoga",
            "involved_planets": ["jupiter", "saturn"],
        }
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is True
        assert "dusthana" in result["reason"].lower()

    def test_raja_yoga_not_cancelled_good_placement(self):
        """Raja Yoga NOT cancelled when planets are in good mutual placement."""
        # Jupiter in Sagittarius, Saturn in Pisces (4th from Sagittarius = kendra)
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            jupiter=("sagittarius", 248.0, 9),
            saturn=("pisces", 345.0, 12),  # 4th from Sag = NOT dusthana
            mars=("aries", 5.0, 1),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        yoga = {
            "category": "raja_yoga",
            "involved_planets": ["jupiter", "saturn"],
        }
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is False


class TestDhanaYogaCancellation:
    """Test Dhana Yoga-specific cancellation."""

    def test_dhana_yoga_cancelled_lord_afflicted(self):
        """Dhana Yoga cancelled when forming planet afflicted by 2+ malefics."""
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            venus=("sagittarius", 250.0, 9),
            mars=("sagittarius", 248.0, 9),
            saturn=("sagittarius", 252.0, 9),
            rahu=("sagittarius", 255.0, 9),
            jupiter=("cancer", 95.0, 4),
            mercury=("virgo", 165.0, 6),
        )
        yoga = {
            "category": "dhana_yoga",
            "involved_planets": ["venus"],
        }
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is True


class TestGajakesariCancellation:
    """Test Gajakesari-specific cancellation."""

    def test_gajakesari_cancelled_moon_in_dusthana(self):
        """Gajakesari cancelled when Moon in 6th house."""
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("virgo", 165.0, 6),  # 6th house = dusthana
            jupiter=("virgo", 168.0, 6),  # Conjunct Moon
            mars=("aries", 5.0, 1),
            mercury=("leo", 135.0, 5),
            venus=("libra", 185.0, 7),
            saturn=("capricorn", 280.0, 10),
        )
        yoga = {
            "category": "gajakesari",
            "involved_planets": ["moon", "jupiter"],
        }
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is True
        assert "dusthana" in result["reason"].lower()

    def test_gajakesari_cancelled_jupiter_in_8th(self):
        """Gajakesari cancelled when Jupiter in 8th house."""
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("cancer", 95.0, 4),
            jupiter=("scorpio", 218.0, 8),  # 8th from Lagna
            mars=("aries", 5.0, 1),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
            saturn=("capricorn", 280.0, 10),
        )
        yoga = {
            "category": "gajakesari",
            "involved_planets": ["moon", "jupiter"],
        }
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is True

    def test_gajakesari_not_cancelled_good_placement(self):
        """Gajakesari NOT cancelled when both in good houses."""
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("cancer", 95.0, 4),  # 4th = kendra, good
            jupiter=("cancer", 98.0, 4),  # Exalted + 4th house
            mars=("aries", 5.0, 1),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
            saturn=("capricorn", 280.0, 10),
        )
        yoga = {
            "category": "gajakesari",
            "involved_planets": ["moon", "jupiter"],
        }
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is False


class TestApplyCancellationsToChart:
    """Test batch cancellation application."""

    def test_apply_to_multiple_yogas(self):
        """Apply cancellations to a list of yogas."""
        planets = _make_planets(
            sun=("aries", 15.0, 1),
            moon=("taurus", 40.0, 2),
            mars=("aries", 14.0, 1),  # Combust
            jupiter=("cancer", 95.0, 4),  # Exalted
            mercury=("virgo", 165.0, 6),
            venus=("pisces", 345.0, 12),
            saturn=("libra", 185.0, 7),
        )
        yogas = [
            {"category": "other", "involved_planets": ["mars"], "strength": 0.8},
            {"category": "other", "involved_planets": ["jupiter"], "strength": 0.9},
        ]
        results = apply_cancellations_to_chart(yogas, planets, "aries", 15.0)

        assert len(results) == 2
        # Mars is combust
        assert results[0]["cancellation"]["cancelled"] is True
        assert results[0]["effective_strength"] == 0.0
        # Jupiter is fine
        assert results[1]["cancellation"]["cancelled"] is False
        assert results[1]["effective_strength"] > 0

    def test_empty_yogas_returns_empty(self):
        planets = _make_planets(sun=("aries", 15.0, 1), moon=("taurus", 40.0, 2))
        results = apply_cancellations_to_chart([], planets, "aries", 15.0)
        assert results == []

    def test_yoga_with_no_involved_planets(self):
        planets = _make_planets(sun=("aries", 15.0, 1), moon=("taurus", 40.0, 2))
        yogas = [{"category": "other", "involved_planets": [], "strength": 0.5}]
        results = apply_cancellations_to_chart(yogas, planets, "aries", 15.0)
        assert len(results) == 1
        assert results[0]["cancellation"]["cancelled"] is False

    def test_result_has_effective_strength(self):
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            jupiter=("sagittarius", 248.0, 9),
            saturn=("sagittarius", 252.0, 9),
            mars=("aries", 5.0, 1),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        yogas = [{"category": "other", "involved_planets": ["jupiter"], "strength": 0.8}]
        results = apply_cancellations_to_chart(yogas, planets, "aries", 130.0)
        assert "effective_strength" in results[0]
        assert "cancellation" in results[0]


class TestPartialWeakening:
    """Test partial weakening (not full cancellation)."""

    def test_single_malefic_partial_weaken(self):
        """One malefic conjunct = partial weakening."""
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            jupiter=("sagittarius", 248.0, 9),
            saturn=("sagittarius", 252.0, 9),  # 1 malefic
            mars=("aries", 5.0, 1),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        yoga = {"category": "other", "involved_planets": ["jupiter"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is False
        assert result["partial"] is True
        assert result["modified_strength"] < 1.0

    def test_debilitated_with_bhanga_partial(self):
        """Debilitated with Neecha Bhanga = partial weakening only."""
        # Mars debilitated in Cancer, retrograde = Neecha Bhanga
        planets = _make_planets(
            sun=("leo", 130.0, 5),
            moon=("taurus", 40.0, 2),
            mars=("cancer", 95.0, 4, True),  # Retrograde = NB condition
            jupiter=("sagittarius", 248.0, 9),
            saturn=("aquarius", 310.0, 11),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        yoga = {"category": "other", "involved_planets": ["mars"]}
        result = check_yoga_cancellation(yoga, planets, "aries", 130.0)
        assert result["cancelled"] is False
        # Should be partially weakened
        assert result["partial"] is True
        assert 0 < result["modified_strength"] < 1.0
