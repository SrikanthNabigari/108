"""Tests for Neecha Bhanga Raja Yoga detection (detect_neecha_bhanga).

Tests the standalone public function added to yoga_detector.py.
The existing _has_neecha_bhanga() internal method tests in
test_yoga_cancellation.py remain untouched.
"""

from packages.core.src.constants import Planet, Rashi
from packages.self.src.yoga_detector import detect_neecha_bhanga


def _planet_data(rashi, longitude, house, is_retrograde=False):
    """Helper to create planet data dict."""
    return {
        "rashi": rashi,
        "longitude": longitude,
        "house": house,
        "is_retrograde": is_retrograde,
    }


def _make_all_planets(**kwargs):
    """Create all_planets dict from kwargs: name=(rashi, lon, house, retro?)."""
    planets = {}
    for name, vals in kwargs.items():
        rashi = vals[0]
        lon = vals[1]
        house = vals[2]
        retro = vals[3] if len(vals) > 3 else False
        planets[name] = _planet_data(rashi, lon, house, retro)
    return planets


class TestNeechaBhangaCondition1:
    """Condition 1: Lord of debilitation sign in kendra from Lagna or Moon."""

    def test_mars_debilitated_moon_lord_in_kendra(self):
        """Mars debilitated in Cancer, Moon (lord of Cancer) in Aries (house 1 from Aries = kendra)."""
        all_planets = _make_all_planets(
            mars=("cancer", 95.0, 4),
            moon=("aries", 5.0, 1),
            sun=("leo", 130.0, 5),
            jupiter=("sagittarius", 248.0, 9),
            saturn=("aquarius", 310.0, 11),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        result = detect_neecha_bhanga("mars", all_planets["mars"], all_planets, "aries")
        assert result["has_neecha_bhanga"] is True
        assert any("Lord of debilitation" in c for c in result["conditions_met"])

    def test_jupiter_debilitated_saturn_lord_in_kendra_from_moon(self):
        """Jupiter debilitated in Capricorn, Saturn (lord of Cap) in Cancer (7th from Cap = kendra from Moon)."""
        all_planets = _make_all_planets(
            jupiter=("capricorn", 275.0, 3),
            saturn=("cancer", 95.0, 9),  # Kendra from Moon (Capricorn)
            moon=("capricorn", 278.0, 3),
            sun=("leo", 130.0, 10),
            mars=("aries", 5.0, 6),
            mercury=("virgo", 165.0, 11),
            venus=("pisces", 345.0, 5),
        )
        result = detect_neecha_bhanga("jupiter", all_planets["jupiter"], all_planets, "scorpio")
        assert result["has_neecha_bhanga"] is True


class TestNeechaBhangaCondition2:
    """Condition 2: Lord of exaltation sign in kendra from Lagna or Moon."""

    def test_sun_debilitated_mars_exalt_lord_in_kendra(self):
        """Sun debilitated in Libra. Sun exalts in Aries, lord of Aries = Mars.
        Mars in Libra = house 1 from Libra (kendra from Lagna Libra)."""
        all_planets = _make_all_planets(
            sun=("libra", 190.0, 1),
            mars=("libra", 195.0, 1),  # In Lagna = kendra
            moon=("taurus", 40.0, 8),
            jupiter=("leo", 128.0, 11),
            saturn=("gemini", 70.0, 9),
            mercury=("virgo", 165.0, 12),
            venus=("pisces", 345.0, 6),
        )
        result = detect_neecha_bhanga("sun", all_planets["sun"], all_planets, "libra")
        assert result["has_neecha_bhanga"] is True
        assert any("Lord of exaltation" in c for c in result["conditions_met"])


class TestNeechaBhangaCondition3:
    """Condition 3: Planet exalted in the debilitation sign aspects the debilitated planet."""

    def test_mars_debilitated_jupiter_exalted_in_cancer_aspects(self):
        """Mars debilitated in Cancer. Jupiter is exalted in Cancer.
        If Jupiter is placed such that it aspects Cancer via its special aspects,
        condition 3 is met."""
        # Jupiter in Scorpio aspects Cancer via 9th aspect (5th house forward = Cancer from Scorpio? No.)
        # Jupiter in Scorpio: 5th from Scorpio = Pisces, 9th from Scorpio = Cancer!
        # Actually: 9th house from Scorpio = Cancer (Scorpio->Sag->Cap->Aqu->Pis->Ari->Tau->Gem->Cancer = 9th)
        # Wait, let me count: Scorpio=1, Sag=2, Cap=3, Aqu=4, Pis=5, Ari=6, Tau=7, Gem=8, Cancer=9
        # Yes! Jupiter in Scorpio aspects Cancer (9th aspect). Jupiter is exalted in Cancer. Condition 3!

        # But actually: Cancer from Jupiter (in Scorpio): house of Cancer from Scorpio =
        # ((3 - 7) % 12) + 1 = ((-4) % 12) + 1 = 8 + 1 = 9. So Cancer is 9th from Scorpio.
        # Jupiter has special 9th aspect. Condition 3 met!

        all_planets = _make_all_planets(
            mars=("cancer", 95.0, 3),
            jupiter=("scorpio", 218.0, 7),  # Aspects Cancer via 9th aspect
            moon=("gemini", 70.0, 2),
            sun=("leo", 130.0, 4),
            saturn=("aquarius", 310.0, 10),
            mercury=("virgo", 165.0, 5),
            venus=("libra", 185.0, 6),
        )
        result = detect_neecha_bhanga("mars", all_planets["mars"], all_planets, "taurus")
        assert result["has_neecha_bhanga"] is True
        assert any("aspects" in c.lower() for c in result["conditions_met"])


class TestNeechaBhangaCondition4:
    """Condition 4: Debilitated planet is retrograde."""

    def test_mars_debilitated_retrograde(self):
        """Mars debilitated in Cancer and retrograde -- Srikanth's chart example!"""
        all_planets = _make_all_planets(
            mars=("cancer", 95.0, 10, True),  # Retrograde!
            moon=("aquarius", 326.85, 5),
            sun=("scorpio", 226.0, 2),
            jupiter=("virgo", 165.0, 12),
            saturn=("aquarius", 310.0, 5),
            mercury=("sagittarius", 248.0, 3),
            venus=("scorpio", 220.0, 2),
        )
        result = detect_neecha_bhanga("mars", all_planets["mars"], all_planets, "libra")
        assert result["has_neecha_bhanga"] is True
        assert any("retrograde" in c.lower() for c in result["conditions_met"])

    def test_saturn_debilitated_retrograde(self):
        """Saturn debilitated in Aries and retrograde."""
        all_planets = _make_all_planets(
            saturn=("aries", 10.0, 6, True),
            sun=("leo", 130.0, 10),
            moon=("taurus", 40.0, 7),
            mars=("gemini", 70.0, 8),
            jupiter=("sagittarius", 248.0, 2),
            mercury=("virgo", 165.0, 11),
            venus=("cancer", 100.0, 9),
        )
        result = detect_neecha_bhanga("saturn", all_planets["saturn"], all_planets, "scorpio")
        assert result["has_neecha_bhanga"] is True
        assert any("retrograde" in c.lower() for c in result["conditions_met"])


class TestNeechaBhangaCondition5:
    """Condition 5: Debilitated planet in Navamsha of exaltation sign."""

    def test_mars_debilitated_navamsha_exaltation(self):
        """Mars debilitated in Cancer, Navamsha in Capricorn (exaltation sign)."""
        all_planets = _make_all_planets(
            mars=("cancer", 95.0, 4),
            moon=("taurus", 40.0, 2),
            sun=("leo", 130.0, 5),
            jupiter=("sagittarius", 248.0, 9),
            saturn=("aquarius", 310.0, 11),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        d9_positions = {"mars": {"rashi_name": "Capricorn"}}
        result = detect_neecha_bhanga(
            "mars", all_planets["mars"], all_planets, "aries", d9_positions
        )
        assert result["has_neecha_bhanga"] is True
        assert any("navamsha" in c.lower() for c in result["conditions_met"])

    def test_no_navamsha_data_skips_condition5(self):
        """Without D9 data, condition 5 is skipped."""
        all_planets = _make_all_planets(
            mars=("cancer", 95.0, 3),
            moon=("gemini", 70.0, 2),
            sun=("leo", 130.0, 4),
            jupiter=("sagittarius", 248.0, 8),
            saturn=("aquarius", 310.0, 10),
            mercury=("virgo", 165.0, 5),
            venus=("libra", 185.0, 6),
        )
        result = detect_neecha_bhanga("mars", all_planets["mars"], all_planets, "taurus")
        # Without other conditions met, should NOT have condition 5
        has_navamsha_condition = any(
            "navamsha" in c.lower() for c in result.get("conditions_met", [])
        )
        assert not has_navamsha_condition


class TestNeechaBhangaNotDebilitated:
    """Test that non-debilitated planets return no Neecha Bhanga."""

    def test_exalted_planet_no_neecha_bhanga(self):
        """Mars exalted in Capricorn -- no Neecha Bhanga."""
        all_planets = _make_all_planets(
            mars=("capricorn", 280.0, 10),
            moon=("taurus", 40.0, 2),
            sun=("aries", 10.0, 1),
        )
        result = detect_neecha_bhanga("mars", all_planets["mars"], all_planets, "aries")
        assert result["has_neecha_bhanga"] is False
        assert result["conditions_met"] == []
        assert result["strength_modifier"] == 0.0

    def test_planet_in_own_sign_no_neecha_bhanga(self):
        """Jupiter in Sagittarius (own sign) -- no Neecha Bhanga."""
        all_planets = _make_all_planets(
            jupiter=("sagittarius", 248.0, 9),
            moon=("taurus", 40.0, 2),
            sun=("aries", 10.0, 1),
        )
        result = detect_neecha_bhanga("jupiter", all_planets["jupiter"], all_planets, "aries")
        assert result["has_neecha_bhanga"] is False


class TestNeechaBhangaMultipleConditions:
    """Test multiple conditions met simultaneously."""

    def test_multiple_conditions_increase_strength(self):
        """Multiple NB conditions = higher strength modifier."""
        # Mars debilitated in Cancer, retrograde (cond 4),
        # Moon (lord of Cancer) in Aries (cond 1 from kendra)
        all_planets = _make_all_planets(
            mars=("cancer", 95.0, 4, True),
            moon=("aries", 5.0, 1),
            sun=("leo", 130.0, 5),
            jupiter=("sagittarius", 248.0, 9),
            saturn=("aquarius", 310.0, 11),
            mercury=("virgo", 165.0, 6),
            venus=("libra", 185.0, 7),
        )
        result = detect_neecha_bhanga("mars", all_planets["mars"], all_planets, "aries")
        assert result["has_neecha_bhanga"] is True
        assert len(result["conditions_met"]) >= 2
        assert result["strength_modifier"] > 0.3  # Multiple conditions = higher

    def test_planet_enum_keys_work(self):
        """Test that Planet enum keys work in all_planets dict."""
        all_planets = {
            Planet.MARS: _planet_data("cancer", 95.0, 4, True),
            Planet.MOON: _planet_data("aries", 5.0, 1),
            Planet.SUN: _planet_data("leo", 130.0, 5),
            Planet.JUPITER: _planet_data("sagittarius", 248.0, 9),
            Planet.SATURN: _planet_data("aquarius", 310.0, 11),
            Planet.MERCURY: _planet_data("virgo", 165.0, 6),
            Planet.VENUS: _planet_data("libra", 185.0, 7),
        }
        result = detect_neecha_bhanga("mars", all_planets[Planet.MARS], all_planets, "aries")
        assert result["has_neecha_bhanga"] is True

    def test_rashi_enum_in_planet_data(self):
        """Test that Rashi enum values work in planet data."""
        all_planets = {
            "mars": {"rashi": Rashi.CANCER, "longitude": 95.0, "house": 4, "is_retrograde": True},
            "moon": {"rashi": Rashi.ARIES, "longitude": 5.0, "house": 1, "is_retrograde": False},
            "sun": {"rashi": Rashi.LEO, "longitude": 130.0, "house": 5, "is_retrograde": False},
        }
        result = detect_neecha_bhanga("mars", all_planets["mars"], all_planets, "aries")
        assert result["has_neecha_bhanga"] is True
