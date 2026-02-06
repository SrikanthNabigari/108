"""Tests for Bhava Chalit chart calculations.

Tests calculate_bhava_chalit() and get_shifted_planets() from
packages/cosmos/src/bhava_chalit.py.
"""

from packages.cosmos.src.bhava_chalit import (
    calculate_bhava_chalit,
    get_shifted_planets,
)


def _equal_cusps(asc: float) -> list[float]:
    """Generate equal house cusps starting from ascendant."""
    return [(asc + i * 30) % 360 for i in range(12)]


class TestCalculateBhavaChalit:
    """Test calculate_bhava_chalit() function."""

    def test_no_shift_equal_cusps(self):
        """With equal cusps and planet at cusp center, no shift expected."""
        cusps = _equal_cusps(0.0)  # Cusps at 0, 30, 60, ...
        # Planet at 5 degrees Aries -- well within house 1 range (345 to 15 midpoints)
        planets = {"sun": {"longitude": 5.0}}
        result = calculate_bhava_chalit(planets, cusps, 0.0)
        assert result["sun"]["rashi_house"] == 1
        assert result["sun"]["bhava_chalit_house"] == 1
        assert result["sun"]["shifted"] is False

    def test_planet_at_cusp_may_shift(self):
        """Planet near a cusp boundary may shift in Bhava Chalit."""
        # Ascendant at 15 degrees Aries. Cusps at 15, 45, 75, ...
        _equal_cusps(15.0)
        # Planet at 1 degree Aries (longitude 1.0)
        # Rashi house: Aries = sign 0, Asc in Aries = sign 0, house = 1
        # But Bhava Chalit: midpoint between cusp[11]=345 and cusp[0]=15 = 0.
        # Planet at 1 is between 0 and midpoint(15,45)=30. So it's in house 1.
        # Actually midpoint of cusp[11]=345 and cusp[0]=15 = (345+15+360)/2 = 360 = 0.
        # So house 1 range: 0 to midpoint(15,45) = 30.
        # Planet at 1 -> house 1 in chalit too. No shift.

        # To test a shift: planet at 358 degrees.
        # Rashi house: 358/30 = 11 (Pisces), sign 11 - asc sign 0 + 1 = 12
        # Bhava Chalit: 358 is between midpoint(315,345)=330 and 0 (midpoint 345,15).
        # So 330 <= 358 < 0(=360), means house 12. Same = no shift.

        # Better: cusps NOT equal. Cusp 1 at 15, cusp 2 at 55 (wider house 1).
        # Then midpoints: (345+15)/2 = 0 (but wrap), (15+55)/2 = 35.
        # A planet at 30 (start of Taurus):
        # Rashi: sign 1 (Taurus) - sign 0 (Aries) + 1 = 2
        # Chalit: 30 is between midpoint[0]=0 and midpoint[1]=35 => house 1
        # So planet shifts from house 2 to house 1!
        unequal_cusps = [15, 55, 85, 115, 145, 175, 205, 235, 265, 295, 325, 345]
        planets = {"mars": {"longitude": 30.0}}
        result = calculate_bhava_chalit(planets, unequal_cusps, 15.0)
        # Mars at 30 deg: Rashi house 2 (Taurus from Aries asc)
        assert result["mars"]["rashi_house"] == 2
        # In bhava chalit, should shift
        assert result["mars"]["bhava_chalit_house"] != result["mars"]["rashi_house"]
        assert result["mars"]["shifted"] is True

    def test_multiple_planets(self):
        """Multiple planets should all be calculated."""
        cusps = _equal_cusps(0.0)
        planets = {
            "sun": {"longitude": 15.0},
            "moon": {"longitude": 45.0},
            "mars": {"longitude": 75.0},
        }
        result = calculate_bhava_chalit(planets, cusps, 0.0)
        assert len(result) == 3
        assert "sun" in result
        assert "moon" in result
        assert "mars" in result

    def test_cusps_as_dict(self):
        """Cusps passed as dict with 'cusps' key."""
        cusps_dict = {"cusps": _equal_cusps(0.0)}
        planets = {"sun": {"longitude": 15.0}}
        result = calculate_bhava_chalit(planets, cusps_dict, 0.0)
        assert "sun" in result
        assert result["sun"]["rashi_house"] == 1

    def test_planet_position_object(self):
        """Planet data with attribute access (like PlanetPosition)."""

        class MockPos:
            def __init__(self, lon):
                self.longitude = lon

        cusps = _equal_cusps(0.0)
        planets = {"venus": MockPos(185.0)}
        result = calculate_bhava_chalit(planets, cusps, 0.0)
        assert "venus" in result
        # 185 / 30 = 6 (Libra), house 7 from Aries
        assert result["venus"]["rashi_house"] == 7

    def test_planet_enum_keys(self):
        """Planet enum keys should be converted to string."""
        from packages.core.src.constants import Planet

        cusps = _equal_cusps(0.0)
        planets = {Planet.JUPITER: {"longitude": 248.0}}
        result = calculate_bhava_chalit(planets, cusps, 0.0)
        assert "jupiter" in result

    def test_empty_planets(self):
        """Empty planet dict returns empty result."""
        cusps = _equal_cusps(0.0)
        result = calculate_bhava_chalit({}, cusps, 0.0)
        assert result == {}

    def test_invalid_cusps_length(self):
        """Non-12 cusps returns empty result."""
        result = calculate_bhava_chalit({"sun": {"longitude": 15.0}}, [0, 30, 60], 0.0)
        assert result == {}

    def test_wrap_around_360(self):
        """Planet near 360/0 boundary handled correctly."""
        cusps = _equal_cusps(350.0)  # Asc near end of Pisces
        planets = {"saturn": {"longitude": 355.0}}
        result = calculate_bhava_chalit(planets, cusps, 350.0)
        assert "saturn" in result
        # Saturn in Pisces, Asc in Pisces -> house 1
        assert result["saturn"]["rashi_house"] == 1

    def test_ascendant_in_middle_of_sign(self):
        """Ascendant not at sign boundary."""
        # Asc at 15 Leo (135 degrees)
        cusps = _equal_cusps(135.0)
        planets = {
            "sun": {"longitude": 140.0},  # In Leo, house 1
            "moon": {"longitude": 170.0},  # In Virgo, house 2
        }
        result = calculate_bhava_chalit(planets, cusps, 135.0)
        assert result["sun"]["rashi_house"] == 1  # Same sign as Asc
        assert result["moon"]["rashi_house"] == 2


class TestGetShiftedPlanets:
    """Test get_shifted_planets() function."""

    def test_no_shifted_planets(self):
        """When no shifts, return empty list."""
        bhava_chalit = {
            "sun": {"rashi_house": 1, "bhava_chalit_house": 1, "shifted": False},
            "moon": {"rashi_house": 4, "bhava_chalit_house": 4, "shifted": False},
        }
        shifted = get_shifted_planets(bhava_chalit)
        assert shifted == []

    def test_one_shifted_planet(self):
        """One shifted planet returned."""
        bhava_chalit = {
            "sun": {"rashi_house": 1, "bhava_chalit_house": 1, "shifted": False},
            "mars": {"rashi_house": 2, "bhava_chalit_house": 1, "shifted": True},
        }
        shifted = get_shifted_planets(bhava_chalit)
        assert len(shifted) == 1
        assert shifted[0]["planet"] == "mars"
        assert shifted[0]["rashi_house"] == 2
        assert shifted[0]["bhava_chalit_house"] == 1

    def test_multiple_shifted_planets(self):
        """Multiple shifted planets returned."""
        bhava_chalit = {
            "sun": {"rashi_house": 1, "bhava_chalit_house": 12, "shifted": True},
            "moon": {"rashi_house": 4, "bhava_chalit_house": 4, "shifted": False},
            "mars": {"rashi_house": 7, "bhava_chalit_house": 8, "shifted": True},
        }
        shifted = get_shifted_planets(bhava_chalit)
        assert len(shifted) == 2
        names = {s["planet"] for s in shifted}
        assert names == {"sun", "mars"}

    def test_shifted_has_description(self):
        """Shifted planet entry has a description."""
        bhava_chalit = {
            "venus": {"rashi_house": 5, "bhava_chalit_house": 6, "shifted": True},
        }
        shifted = get_shifted_planets(bhava_chalit)
        assert len(shifted) == 1
        assert "description" in shifted[0]
        assert "Venus" in shifted[0]["description"]

    def test_empty_input(self):
        """Empty input returns empty list."""
        assert get_shifted_planets({}) == []
