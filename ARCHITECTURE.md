# 108 Architecture & Knowledge Base

> This document captures the complete architecture, decisions, and context from the initial design sessions.

## Vision

**108** is not just an astrology app. It is a **Personal Life Operating System** that:
- Calculates all Vedic Jyotish elements with precision
- Predicts past, present, and future
- Adapts to each person through detected personality
- Guides with tasks and scheduled events
- Learns from every conversation
- Ultimate goal: "Decode how astrology is our complete operating system"

---

## The 5-Layer Architecture

| Layer | Name | Purpose | Technology |
|-------|------|---------|------------|
| 1 | **COSMOS** | Calculate all cosmic positions | Swiss Ephemeris (pyswisseph) |
| 2 | **SELF** | Detect yogas, doshas, personality | JSON rules, Pydantic |
| 3 | **CONTEXT** | Track transits, dasha, panchanga | Real-time calculations |
| 4 | **GUIDE** | AI interpretation & guidance | LangGraph + Claude |
| 5 | **MEMORY** | Learn and evolve | Mem0 + LangMem + pgvector |

### Layer 1: COSMOS (Calculation Engine)
- Planetary positions (sidereal with Lahiri ayanamsa)
- House cusps and ascendant calculations
- Nakshatra and pada determinations
- Vimshottari dasha calculations
- All 16 divisional charts (Varga)
- Panchanga (5 limbs of time)
- Transit positions and aspects
- Swarodaya (breath rhythm) calculations

### Layer 2: SELF (Pattern Recognition)
- 317+ yoga detection with machine-parseable rules
- Dosha identification (Mangal, Kaal Sarp, Pitra)
- Shadbala (six-fold strength) analysis
- Ashtakavarga scoring
- Chara Karakas (soul significators)
- Personality archetype detection

### Layer 3: CONTEXT (Temporal Dynamics)
- Current Mahadasha/Antardasha/Pratyantardasha
- Gochara (transit) analysis
- Sade Sati and Dhaiya tracking
- Daily Panchanga (tithi, nakshatra, yoga, karana)
- Inauspicious periods (Rahu Kaal, Yamaghanda)
- Current Swara and Tattwa

### Layer 4: GUIDE (AI Interpretation)
- LangGraph-powered conversational agent
- Personality-adapted communication style
- Context-aware interpretations
- Task generation and scheduling
- Remedial recommendations
- Muhurta (auspicious timing) suggestions

### Layer 5: MEMORY (Continuous Learning)
- Conversation history with semantic search
- User preferences and communication patterns
- Life events and prediction validations
- Feedback loops for accuracy improvement

---

## Tech Stack (2026 Modern Python)

### Package Management
- **uv** - Rust-based, 10-100x faster than Poetry
- **ruff** - All-in-one linter/formatter (replaces black, isort, flake8)
- **pydantic v2** - Data validation with type annotations

### Core Framework
- **FastAPI** - High-performance async API
- **LangGraph** - Stateful agent orchestration
- **FastMCP** - Model Context Protocol servers
- **Anthropic SDK** - Claude API integration

### Memory & Persistence
- **Mem0** - Universal memory layer (+26% accuracy)
- **LangMem** - Agent-controlled memory tools
- **PostgreSQL + pgvector** - Vector database for embeddings
- **Redis** - Fast cache and session store
- **asyncpg** - High-performance async Postgres driver

### Infrastructure
- **Temporal** - Durable workflow orchestration
- **Docker Compose** - Local development environment

---

## Key Jyotish Concepts

### The 9 Grahas (Planets)
Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu

### The 12 Rashis (Signs)
Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces

### The 27 Nakshatras (Lunar Mansions)
Each spans 13°20' with 4 padas of 3°20' each.

### Key Houses
- Kendras (1, 4, 7, 10) - Angular houses, strength
- Trikonas (1, 5, 9) - Trine houses, fortune
- Dusthanas (6, 8, 12) - Difficult houses

### Vimshottari Dasha Years
Ketu: 7, Venus: 20, Sun: 6, Moon: 10, Mars: 7, Rahu: 18, Jupiter: 16, Saturn: 19, Mercury: 17

---

## Yoga Detection Rule Format

Yogas are detected using machine-parseable JSON rules:

```json
{
  "yoga_id": {
    "name": "Shasha Yoga",
    "category": "pancha_mahapurusha",
    "detection": {
      "planet": "Saturn",
      "conditions": [
        {
          "type": "in_kendra",
          "houses": [1, 4, 7, 10],
          "from": "lagna"
        },
        {
          "type": "in_own_or_exalted_sign",
          "signs": ["Capricorn", "Aquarius", "Libra"]
        }
      ],
      "all_conditions_required": true
    }
  }
}
```

### Condition Types
- `in_kendra` - Planet in houses 1, 4, 7, 10
- `in_trikona` - Planet in houses 1, 5, 9
- `in_own_or_exalted_sign` - Planet in its own or exalted sign
- `planets_conjunct` - Two+ planets in same sign
- `lord_placement` - Lord of house X in house Y
- `aspected_by` - Planet aspected by specific planets

---

## User Profile (Srikanth)

- **Birth**: 1992-12-03T03:00:00+05:30
- **Location**: lat 16.726239, lon 81.288428
- **Lagna**: Libra
- **Moon Sign**: Aquarius
- **Nakshatra**: Purva Bhadrapada Pada 2
- **Detected Yoga**: Shasha Yoga (Saturn in Capricorn in 4th house)
- **Current Dasha**: Mercury-Ketu
- **Sade Sati**: Final phase

---

## Important Design Principles

1. **Single Source of Truth** - All Jyotish definitions in `knowledge/` JSON files
2. **Separation of Concerns** - Calculations (COSMOS) separate from interpretation (GUIDE)
3. **Memory as First-Class** - System learns and evolves with every interaction
4. **Personality-Driven** - Responses adapt to detected personality from birth chart
5. **Machine-Parseable Rules** - Never hardcode yoga/dosha conditions

---

## Lessons Learned (from previous implementation)

1. Don't hardcode yoga conditions - use JSON detection rules
2. Keep separate files for definitions vs detection rules vs interpretations
3. Always set ayanamsa before ephemeris calculations
4. Ketu = Rahu + 180° (not separate calculation)
5. Use UTC for all Julian day conversions
6. Memory/learning is what makes it a companion, not just a calculator
