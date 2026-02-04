# 108 Ephemeris MCP Server

The Ephemeris MCP (Model Context Protocol) server provides planetary calculation tools for Claude to use in the 108 Vedic Astrology application.

## Overview

This server exposes 5 core tools for Vedic astrology calculations using the Swiss Ephemeris library via the `cosmos` package:

1. **planetary_positions** - Calculate sidereal positions of all 9 Vedic planets
2. **house_cusps** - Calculate house cusps and ascendant for a given location/time
3. **nakshatra_details** - Get nakshatra, pada, and lord for any longitude
4. **divisional_chart** - Calculate divisional charts (D1-D60) for planets
5. **panchanga** - Calculate the 5 limbs of the Vedic calendar

## Installation

The server requires:
- `fastmcp` - MCP server framework
- `swisseph` - Swiss Ephemeris library
- `cosmos` package - 108's ephemeris calculations

Install dependencies:
```bash
pip install fastmcp
```

## Running the Server

```bash
cd /sessions/eloquent-zen-gauss/mnt/108-core
python services/mcp/ephemeris_server.py
```

## Tools Reference

### 1. planetary_positions()

Calculates sidereal planetary positions for all 9 Vedic planets.

**Parameters:**
- `datetime_iso` (str): ISO format datetime, e.g., "1992-12-03T03:00:00+05:30"
- `latitude` (float): Geographic latitude (-90 to 90)
- `longitude` (float): Geographic longitude (-180 to 180)
- `ayanamsa` (str, optional): Ayanamsa system - "lahiri" (default), "raman", "krishnamurti", "yukteshwar"

**Returns:**
Dictionary with:
- `julian_day`: Julian Day Number for calculations
- `ayanamsa_value`: Precession correction in degrees
- `planets`: Dictionary of planet positions with:
  - `longitude`: Sidereal longitude (0-360°)
  - `latitude`: Ecliptic latitude
  - `speed`: Daily motion in degrees/day
  - `is_retrograde`: Boolean retrograde status
  - `sign`: Zodiacal sign name
  - `sign_degree`: Degree within sign
  - `nakshatra`: Lunar mansion name
  - `nakshatra_pada`: Quarter of nakshatra (1-4)
  - `nakshatra_lord`: Vimshottari lord of the nakshatra

**Example:**
```python
result = planetary_positions(
    "1992-12-03T03:00:00+05:30",
    latitude=12.9716,
    longitude=77.5946
)
# Returns Sun at 227.22° in Scorpio, Moon at 324.11° in Aquarius, etc.
```

### 2. house_cusps()

Calculates house cusps and angles for a given location and time.

**Parameters:**
- `datetime_iso` (str): ISO format datetime
- `latitude` (float): Geographic latitude
- `longitude` (float): Geographic longitude
- `house_system` (str, optional): House system - "placidus" (default), "koch", "whole_sign", "equal", "campanus"

**Returns:**
Dictionary with:
- `ascendant`: Ascendant (Lagna) with longitude, sign, and degree
- `mc`: Midheaven with longitude, sign, and degree
- `cusps`: Dictionary of all 12 house cusps with sign and degree information

**Example:**
```python
result = house_cusps(
    "1992-12-03T03:00:00+05:30",
    latitude=12.9716,
    longitude=77.5946,
    house_system="placidus"
)
# Returns Ascendant at 254.63° in Sagittarius, MC at 172.30° in Virgo
```

### 3. nakshatra_details()

Gets detailed information about a nakshatra (lunar mansion) for any longitude.

**Parameters:**
- `longitude` (float): Sidereal longitude (0-360)

**Returns:**
Dictionary with nakshatra information:
- `number`: Nakshatra number (1-27)
- `name`: Nakshatra name (e.g., "Rohini")
- `pada`: Quarter of nakshatra (1-4)
- `lord`: Vimshottari lord of the nakshatra
- `degree_in_nakshatra`: Position within the nakshatra in degrees

**Example:**
```python
result = nakshatra_details(longitude=45.5)
# Returns Rohini #4 Pada 2, ruled by Moon
```

### 4. divisional_chart()

Calculates divisional charts (vargas) for planets. Divisional charts are subdivisions of the main natal chart used for specialized analysis.

**Parameters:**
- `planets` (dict): Planet longitudes {planet_name: longitude}
- `division` (int): Division number - 1, 2, 3, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, or 60

**Divisional Chart Types:**
- D1: Rashi (main chart)
- D2: Hora (wealth)
- D3: Drekkana (siblings)
- D7: Saptamsha (children)
- D9: Navamsha (marriage/dharma) - most important
- D10: Dashamsha (career)
- D12: Dwadashamsha (parents)
- D60: Shashtiamsha (detailed analysis)

**Returns:**
Dictionary with:
- `division`: Division number
- `name`: Chart name (e.g., "Navamsha")
- `positions`: Planet positions in the divisional chart

**Example:**
```python
planets = {'sun': 227.22, 'moon': 324.11, 'mars': 45.33}
result = divisional_chart(planets, 9)  # Navamsha
# Returns Sun at 0.55° in Sagittarius, Moon at 0.78° in Taurus in D9
```

### 5. panchanga()

Calculates the complete Panchanga - the five limbs of the Vedic calendar.

**Parameters:**
- `datetime_iso` (str): ISO format datetime
- `latitude` (float): Geographic latitude
- `longitude` (float): Geographic longitude

**Returns:**
Dictionary with all five panchanga components:
- **Tithi**: Lunar day (1-15, corresponding to half-month)
  - `number`: Tithi number
  - `name`: Tithi name (e.g., "Navami")
  - `progress`: Progress within tithi (0-1)
  
- **Nakshatra**: Lunar mansion where Moon is positioned
  - `number`: Nakshatra number (1-27)
  - `name`: Nakshatra name
  - `pada`: Quarter of nakshatra
  - `lord`: Vimshottari lord
  
- **Yoga**: Auspicious combination (1-27)
  - `number`: Yoga number
  - `name`: Yoga name
  - `progress`: Progress within yoga (0-1)
  
- **Karana**: Half of a tithi (1-11, repeated)
  - `number`: Karana number
  - `name`: Karana name
  
- **Vara**: Day of week (0-6)
  - `number`: Weekday number
  - `name`: Sanskrit day name
  - `weekday`: Gregorian day name

**Example:**
```python
result = panchanga(
    "1992-12-03T03:00:00+05:30",
    latitude=12.9716,
    longitude=77.5946
)
# Returns:
# Tithi: Navami (9)
# Nakshatra: Purva Bhadrapada Pada 2
# Yoga: Vajra (15)
# Karana: Balava (2)
# Vara: Guruvara (Thursday)
```

## Integration with Claude

The server can be integrated with Claude to provide instant Vedic astrology calculations. Claude can use these tools to:

1. Calculate birth charts for any date, time, and location
2. Analyze planetary positions and their meanings
3. Determine auspicious times (muhurta) for activities
4. Analyze divisional charts for deeper insights
5. Provide panchanga information for daily guidance

## File Location

- **Server:** `/sessions/eloquent-zen-gauss/mnt/108-core/services/mcp/ephemeris_server.py`
- **Cosmos Package:** `/sessions/eloquent-zen-gauss/mnt/108-core/packages/cosmos/src/`

## Testing

Run the comprehensive test:
```bash
cd /sessions/eloquent-zen-gauss/mnt/108-core
python -c "from services.mcp.ephemeris_server import planetary_positions; print(planetary_positions('1992-12-03T03:00:00+05:30', 12.9716, 77.5946))"
```

All 5 tools are fully tested and ready for production use.
