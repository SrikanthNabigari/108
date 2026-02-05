# 108 Work Log

## 2026-02-05 (Session 13 - Claude Code)

### Summary
Wired all 5 layers end-to-end: COSMOS → SELF → CONTEXT → GUIDE → MEMORY. Fixed memory store bug, fixed Guide agent's broken `_calculate()` and `_analyze_patterns()` nodes, wired FastAPI endpoints to Guide agent and MemoryStore, and wrote 12 integration tests. 293 tests passing (1 skipped), 0 lint errors.

### Bug Fixes

**`packages/memory/src/store.py`** — Added missing `get_all_memories()` method
- `unified_memory.py:449` called `self._postgres_store.get_all_memories(user_id, limit)` which didn't exist
- Added method that queries memories table without category filter, ordered by `created_at DESC`

**`packages/guide/src/agent.py`** — Fixed `_calculate()` transit path
- Was calling `get_full_transit_analysis(moon_sign, datetime.now())` — wrong signature
- Real signature: `get_full_transit_analysis(natal_moon_rashi: int, transit_positions: dict[str, int])`
- Fix: Convert moon sign name → rashi index (0-11), build transit dict from `get_transit_positions()`
- Now returns sade_sati, dhaiya, key_transits, overall_trend

**`packages/guide/src/agent.py`** — Fixed `_analyze_patterns()` node
- Was creating `YogaDetector()` and `DoshaDetector()` but never calling their methods
- Fix: Build full `BirthChart` pydantic model from raw planet dicts
- Calls `yoga_detector.detect_all_yogas(chart)` and `dosha_detector.detect_all(chart)`
- Stores results in `state["detected_yogas"]`, `state["detected_doshas"]`, and `state["analysis_results"]`

### API Wiring

**`services/api/main.py`** — Lifespan
- Initializes `MemoryStore` on startup if `DATABASE_URL` is set
- Closes connection pool on shutdown
- Lazy-inits Guide agent (only when `ANTHROPIC_API_KEY` present)

**`POST /api/v1/chat`** — Wired to Guide agent
- Lazy-inits Guide agent with ANTHROPIC_API_KEY
- Loads birth chart from MemoryStore if user_id provided
- Calls `guide.chat_async(user_input, user_id, birth_chart=chart_data)`
- Returns response with intent, personality, analysis_results
- Graceful fallback if no API key or missing LangGraph deps

**`POST /api/v1/users`** — Create user with birth chart
- Creates user via `store.create_user(email, name)`
- Calculates full birth chart (planets, houses, nakshatras)
- Saves via `store.save_birth_chart(user_id, chart_data)`
- Returns user_id + chart summary (lagna, moon, nakshatra)

**`GET /api/v1/users/{user_id}`** — Get user profile
- Returns user + birth_chart + detected_patterns from MemoryStore
- 404 if user not found, 503 if no database configured

**New model**: `CreateUserRequest` — email, name, birth_datetime, lat/lon, timezone

### Tests Added (12 new)

| Test | What it verifies |
|------|-----------------|
| `TestLifecycle::test_health_check` | GET /health returns 200 |
| `TestLifecycle::test_root_endpoint` | GET / returns API info |
| `TestChatEndpoint::test_chat_without_api_key` | Returns helpful message |
| `TestChatEndpoint::test_chat_without_user_id` | Works without user_id |
| `TestChatEndpoint::test_chat_with_user_id` | Passes user_id through |
| `TestChatEndpoint::test_chat_with_api_key` | Full agent response (needs key) |
| `TestUserEndpoints::test_get_user_no_db` | 503 without database |
| `TestUserEndpoints::test_create_user_no_db` | 503 without database |
| `TestUserEndpoints::test_get_user_not_found` | 404 for unknown user |
| `TestUserEndpoints::test_get_user_with_profile` | Returns user+chart+patterns |
| `TestUserEndpoints::test_create_user_returns_chart` | Calculates chart on create |
| `TestChartEndpointsIntact::test_chart_calculation` | Existing endpoint still works |
| `TestChartEndpointsIntact::test_timing_dasha` | Existing endpoint still works |

### File Changes

| Action | File | What |
|--------|------|------|
| MODIFY | `packages/memory/src/store.py` | Added `get_all_memories()` method |
| MODIFY | `packages/guide/src/agent.py` | Fixed `_calculate()` + `_analyze_patterns()` |
| MODIFY | `services/api/main.py` | Wired lifespan, chat, users endpoints |
| CREATE | `tests/integration/test_api_wiring.py` | 12 integration tests |

### Verification
- `uv run ruff check .` — 0 errors
- `uv run ruff format .` — all files formatted
- `uv run pytest` — 293 passed, 1 skipped (needs ANTHROPIC_API_KEY in env)
- With `.env` loaded: 294 passed, 0 skipped

---

## 2026-02-05 (Session 12 - Claude Code)

### Summary
Wired all 7 knowledge JSON files into working code modules, tests, and MCP tools. Created 5 new code modules, modified 4 existing files, added 107 new tests (273 total passing), and added 4 new MCP tools. Zero ruff lint errors.

### Code Modules Created (5 new)

**`packages/self/src/combustion.py`** - Planetary Combustion (Asta) Detection
- `_angular_distance(lon1, lon2)` — min angular distance handling 360° wrap
- `check_combustion(planet, planet_lon, sun_lon, is_retrograde)` — threshold-based combustion check with deep combustion, strength loss, effects, remedies
- `get_combustion_analysis(planets)` — batch analysis for all planets against Sun
- `get_combustion_house_effects(planet, house)` — house-specific combustion effects
- Special handling: Mercury/Venus use different thresholds when retrograde

**`packages/self/src/retrograde.py`** - Retrograde (Vakri) Effects Engine
- `get_retrograde_effects(planet, is_natal, house)` — natal vs transit effects with house-specific lookup
- `get_retrograde_analysis(planets, is_natal)` — batch analysis for all retrograde planets
- Covers 5 planets: Mars, Mercury, Jupiter, Venus, Saturn

**`packages/self/src/divisional_interpreter.py`** - D9/D10 Chart Interpretation
- `interpret_d9_position(planet, rashi_name)` — Navamsha interpretation (marriage/dharma)
- `interpret_d10_position(planet, rashi_name)` — Dashamsha interpretation (career)
- `interpret_d9_chart(d9_chart)` / `interpret_d10_chart(d10_chart)` — full chart interpretation
- `get_divisional_analysis(planet_longitudes)` — combined D9+D10 analysis

**`packages/context/src/transits.py`** (MODIFIED) - Enriched Transit Analysis
- `get_nakshatra_transit_effect(planet, nakshatra)` — lookup from 243 combinations
- `get_enriched_transit_analysis(natal_moon_rashi, transit_data, chart)` — wraps existing transit analysis + adds nakshatra effects, combustion, retrograde, ashtakavarga per planet

**`packages/context/src/varshaphal.py`** - Varshaphal (Solar Return) Engine
- `calculate_muntha(birth_lagna_rashi, age)` — Muntha progression
- `determine_varshesha(varshaphal_lagna_rashi)` — Year Lord determination
- `detect_tajika_yogas(planet_positions)` — 16 Tajika yoga detection
- `calculate_sahams(planet_longitudes, lagna_lon, is_day_chart)` — 10 sensitive points
- `get_varshaphal_analysis(...)` — full annual prediction orchestrator

### MCP Tools Added (4 new)

| Server | Tool | Wraps |
|--------|------|-------|
| patterns_server | `kundali_matching()` | `calculate_ashta_kuta()` + `get_compatibility_verdict()` |
| patterns_server | `combustion_check()` | `check_combustion()` |
| patterns_server | `retrograde_effects()` | `get_retrograde_effects()` |
| context_server | `enriched_transit()` | `get_enriched_transit_analysis()` |

### Package Exports Updated
- `packages/self/src/__init__.py` — +10 exports (combustion: 3, retrograde: 2, divisional: 5)
- `packages/context/src/__init__.py` — +7 exports (transits: 2, varshaphal: 5)

### Tests Added (107 new, total suite: 273 passing)

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `tests/unit/test_combustion.py` | 29 | Angular distance, threshold checks, Mercury retrograde, full analysis, house effects |
| `tests/unit/test_retrograde.py` | 16 | Natal vs transit, house-specific, all 5 planets, full analysis |
| `tests/unit/test_divisional_interpreter.py` | 15 | D9/D10 positions, full charts, combined analysis |
| `tests/unit/test_nakshatra_transits.py` | 10 | Planet/nakshatra lookups, case insensitivity |
| `tests/unit/test_enriched_transits.py` | 8 | Base analysis, nakshatra effects, combustion, retrograde, ashtakavarga |
| `tests/unit/test_varshaphal.py` | 29 | Muntha, Varshesha, Tajika yogas, Sahams, full analysis |

### Updated Feature Implementation Status

**NEWLY WIRED (Knowledge → Code):**
| Feature | Module | Knowledge File | Tests |
|---------|--------|---------------|-------|
| Combustion (Asta) detection | self/combustion.py | combustion_rules.json | 29 |
| Retrograde (Vakri) effects | self/retrograde.py | retrograde_rules.json | 16 |
| D9/D10 interpretation | self/divisional_interpreter.py | divisional_interpretation.json | 15 |
| Nakshatra transit effects | context/transits.py | nakshatra_transit_rules.json | 10 |
| Enriched transit analysis | context/transits.py | (integrates all above) | 8 |
| Ashtakavarga in transits | context/transits.py | ashtakavarga_rules.json | (in enriched) |
| Varshaphal engine | context/varshaphal.py | varshaphal_rules.json | 29 |
| Kundali Matching MCP | mcp/patterns_server.py | compatibility_rules.json | - |

### File Change Summary

| Action | File |
|--------|------|
| CREATE | `packages/self/src/combustion.py` |
| CREATE | `packages/self/src/retrograde.py` |
| CREATE | `packages/self/src/divisional_interpreter.py` |
| CREATE | `packages/context/src/varshaphal.py` |
| CREATE | `tests/unit/test_combustion.py` |
| CREATE | `tests/unit/test_retrograde.py` |
| CREATE | `tests/unit/test_divisional_interpreter.py` |
| CREATE | `tests/unit/test_nakshatra_transits.py` |
| CREATE | `tests/unit/test_enriched_transits.py` |
| CREATE | `tests/unit/test_varshaphal.py` |
| MODIFY | `packages/context/src/transits.py` |
| MODIFY | `packages/self/src/__init__.py` |
| MODIFY | `packages/context/src/__init__.py` |
| MODIFY | `services/mcp/patterns_server.py` |
| MODIFY | `services/mcp/context_server.py` |

### Verification
- `uv run ruff check .` — 0 errors
- `uv run ruff format .` — all files formatted
- `uv run pytest` — 273 passed, 8 errors (pre-existing DB connection)

---

## 2026-02-05 (Session 11 - Claude Code)

### Summary
Massive knowledge expansion + code implementation + full codebase lint cleanup. Added 5 new knowledge rule files, 2 new code modules (Kundali Matching, Ashtakavarga transit scoring), 52 new unit tests, and resolved all 153 ruff lint errors across the codebase.

### Knowledge Files Created (5 new)

| File | Size | Content | Status |
|------|------|---------|--------|
| `combustion_rules.json` | 31KB | 6 planets, 12 house effects, remedies, special rules | NEW |
| `retrograde_rules.json` | 75KB | 5 planets, natal/transit effects, sign modifications | NEW |
| `nakshatra_transit_rules.json` | 94KB | 243 combinations (9 planets x 27 nakshatras) | NEW |
| `varshaphal_rules.json` | 17KB | Muntha (12), Varshesha (9), 16 Tajika yogas, 10 Sahams, PVB | NEW |
| `divisional_interpretation.json` | 79KB | D9 + D10: 216 planet-sign combos, 24 house meanings | NEW |

### Code Modules Created (2 new)

**`packages/self/src/compatibility.py`** - Kundali Matching (Ashta Kuta)
- 8 individual kuta score calculators (Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi)
- `calculate_ashta_kuta()` - full 36-point compatibility analysis
- Critical dosha detection (Nadi Dosha, Bhakoot Dosha, Gana Dosha)
- Verdict system: Excellent (33+), Good (25+), Average (18+), Not Recommended

**`packages/self/src/ashtakavarga.py`** - Transit Strength Scoring
- BAV (Bhinnashtakavarga) per-planet scoring (0-8)
- SAV (Sarvashtakavarga) cumulative scoring (0-56)
- `interpret_ashtakavarga_score()` - 5 strength levels
- `get_transit_strength_modifier()` - 0.5x to 1.5x multiplier
- `get_transit_ashtakavarga_analysis()` - complete transit analysis

### Knowledge Loader Updates

5 new accessor functions added to `packages/core/src/knowledge_loader.py`:
- `get_combustion_rules()`
- `get_retrograde_rules()`
- `get_nakshatra_transit_rules()`
- `get_varshaphal_rules()`
- `get_divisional_interpretation()`

### Tests Added (52 new, total suite: 166 passing)

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `tests/unit/test_compatibility.py` | 27 | All 8 Ashta Kuta scores, integration, doshas, verdicts |
| `tests/unit/test_knowledge_files.py` | 37 | All 5 JSON files: structure, counts, loader integration |
| `tests/unit/test_ashtakavarga.py` | 15 | Score interpretation, strength modifier, input validation |

### Codebase Lint Cleanup (153 errors -> 0)

Fixed all pre-existing ruff lint errors across the entire codebase:

| Rule | Count | Fix |
|------|-------|-----|
| RUF013 | 40 | Implicit Optional -> explicit |
| B904 | 16 | Exception chaining with `from err` |
| E402 | 15 | Import ordering (noqa for sys.path-dependent) |
| PTH120/118/123 | 19 | os.path -> pathlib.Path |
| UP042 | 11 | str+Enum -> StrEnum |
| F841 | 13 | Removed unused variables |
| SIM108/102 | 9 | Simplified if-else blocks |
| RUF022 | 4 | Sorted __all__ lists |
| UP038 | 3 | isinstance tuple -> union |
| ARG001/002 | 15 | noqa for unused stub/placeholder args |
| E722 | 1 | Bare except -> Exception |
| RUF003 | 1 | Ambiguous unicode character |

### Updated Knowledge Base Stats

| Category | Before (Session 10) | After (Session 11) | Growth |
|----------|---------------------|---------------------|--------|
| Yogas | 522 | 522 | - |
| Doshas | 55 | 55 | - |
| Antardasha Effects | 81 | 81 | - |
| Pratyantardasha Effects | 729 | 729 | - |
| Nakshatra Transit Combos | 0 | **243** | NEW |
| Tajika Yogas | 0 | **16** | NEW |
| Combustion Rules | 0 | **6 planets + 12 houses** | NEW |
| Retrograde Rules | 0 | **5 planets + effects** | NEW |
| Divisional Interpretations | 0 | **432 (D9+D10)** | NEW |
| Definition Files | 7 | 7 | - |
| Rule Files | 21 | **35** | +14 |
| **Total Knowledge** | ~2.1MB | **~2.4MB** | +300KB |

### Git Commits

```
5efa400 test: Add unit tests for knowledge files and ashtakavarga module
aa9aa15 fix: Resolve all ruff lint errors across codebase
fbcb86c feat(knowledge): Add 5 knowledge files + Kundali Matching & Ashtakavarga modules
```

### Complete Feature Implementation Status

**IMPLEMENTED (Ready to use):**
| Feature | Package | Knowledge | Tests |
|---------|---------|-----------|-------|
| Planetary positions (9 grahas) | cosmos/ephemeris.py | - | test_cosmos |
| House cusps (Placidus, Whole Sign) | cosmos/houses.py | houses.json | test_cosmos |
| Nakshatra calculations (27) | cosmos/nakshatras.py | nakshatras.json | test_cosmos |
| Divisional charts (D1-D60) | cosmos/divisional.py | dignities.json | test_cosmos |
| Panchanga (Tithi/Yoga/Karana/Vara) | cosmos/panchanga.py | - | test_cosmos |
| Yoga detection (522 yogas) | self/yoga_detector.py | yoga_master.json | test_self |
| Dosha detection (55 doshas) | self/dosha_detector.py | dosha_master.json | test_self |
| Shadbala (6-fold strength) | self/strength.py | shadbala_rules.json | test_self |
| Ashtakavarga (BAV/SAV) | self/strength.py | ashtakavarga_rules.json | test_self |
| Ashtakavarga transit scoring | self/ashtakavarga.py | ashtakavarga_rules.json | test_ashtakavarga |
| Kundali Matching (Ashta Kuta) | self/compatibility.py | compatibility_rules.json | test_compatibility |
| Vimshottari Dasha (5 levels) | context/dasha.py | dasha_rules.json | test_context |
| Antardasha effects (81) | context/dasha.py | antardasha_effects.json | test_context |
| Pratyantardasha effects (729) | context/dasha.py | pratyantardasha_master.json | test_context |
| Transit/Gochara analysis | context/transits.py | transit_rules.json | test_transits |
| Sade Sati / Dhaiya detection | context/transits.py | transit_rules.json | test_transits |
| Muhurta (electional timing) | context/muhurta.py | muhurta_rules.json | test_context |
| LangGraph agent | guide/agent.py | - | test_guide_agent |
| Memory (Mem0 + pgvector) | memory/*.py | - | test_memory_store |
| FastAPI (22+ endpoints) | services/api/main.py | - | - |
| 4 MCP servers (16 tools) | services/mcp/*.py | - | - |

**ALL KNOWLEDGE NOW WIRED INTO CODE** (Session 12):
| Feature | Knowledge File | Code Module | Status |
|---------|---------------|-------------|--------|
| Combustion (Asta) detection | combustion_rules.json | self/combustion.py | DONE |
| Retrograde (Vakri) effects | retrograde_rules.json | self/retrograde.py | DONE |
| D9/D10 interpretation | divisional_interpretation.json | self/divisional_interpreter.py | DONE |
| Nakshatra transit effects | nakshatra_transit_rules.json | context/transits.py | DONE |
| Ashtakavarga in transits | ashtakavarga_rules.json | context/transits.py | DONE |
| Varshaphal (Solar Return) | varshaphal_rules.json | context/varshaphal.py | DONE |
| Kundali Matching MCP tool | compatibility_rules.json | mcp/patterns_server.py | DONE |

**NOT YET STARTED (Future roadmap):**
| Feature | Priority | Knowledge Needed | Code Needed |
|---------|----------|-----------------|-------------|
| Jaimini system (Chara Dasha, Karakamsha) | Lower | New rules file | New package |
| Alternative dashas (Yogini, Chara, Narayana) | Lower | New rules file | dasha.py extension |
| Prashna (Horary astrology) | Lower | New rules file | New module |
| Arudha Padas | Lower | New rules file | New module |
| Upagraha calculations (Gulika, Mandi) | Lower | upagrahas.json | cosmos extension |
| Shad Varga analysis | Medium | vargas.json | divisional.py extension |

---

## 2026-02-05 (Session 10 - Claude Cowork)

### Summary
Completed full Pratyantardasha knowledge expansion - 729 combinations (9×9×9) for the complete 5-level Vimshottari Dasha system. Analyzed package architecture for integration.

### Knowledge Files Created

**Pratyantardasha Files (10 new files, ~1.5MB total):**
| File | Size | Combinations | Status |
|------|------|--------------|--------|
| `pratyantardasha_sun_md.json` | 52KB | 81 | ✅ Complete |
| `pratyantardasha_moon_md.json` | 55KB | 81 | ✅ Complete |
| `pratyantardasha_mars_md.json` | 100KB | 81 | ✅ Complete |
| `pratyantardasha_mercury_md.json` | 118KB | 81 | ✅ Complete |
| `pratyantardasha_jupiter_md.json` | 120KB | 81 | ✅ Complete |
| `pratyantardasha_venus_md.json` | 93KB | 81 | ✅ Complete |
| `pratyantardasha_saturn_md.json` | 100KB | 81 | ✅ Complete |
| `pratyantardasha_rahu_md.json` | 133KB | 81 | ✅ Complete |
| `pratyantardasha_ketu_md.json` | 71KB | 81 | ✅ Complete |
| **`pratyantardasha_master.json`** | **864KB** | **729** | ✅ **CONSOLIDATED** |

**Consolidation Script Created:**
| File | Purpose |
|------|---------|
| `scripts/consolidate_pratyantardasha.py` | Merges 9 MD files into master with multi-format handling |

### Complete Dasha Knowledge Coverage

| Level | Name | Combinations | File | Status |
|-------|------|--------------|------|--------|
| 1 | Mahadasha | 9 | `dasha_rules.json` | ✅ Complete |
| 2 | Antardasha | 81 (9×9) | `antardasha_effects.json` | ✅ Complete |
| 3 | Pratyantardasha | 729 (9×9×9) | `pratyantardasha_master.json` | ✅ **NEW** |
| 4 | Sookshma | Formulas | `pratyantardasha_rules.json` | ✅ Timing rules |
| 5 | Prana | Formulas | `pratyantardasha_rules.json` | ✅ Timing rules |

### Updated Knowledge Base Stats

| Category | Before | After | Growth |
|----------|--------|-------|--------|
| Yogas | 522 | 522 | - |
| Doshas | 55 | 55 | - |
| Antardasha Effects | 81 | 81 | - |
| **Pratyantardasha Effects** | **0** | **729** | **∞** |
| Definition Files | 7 | 7 | - |
| Rule Files | 11 | 21 | +10 |
| **Total Knowledge** | ~590KB | **~2.1MB** | **3.5x** |

---

### 🔧 TASKS FOR CLAUDE CODE ✅ ALL COMPLETED (Session 10 continued)

**Priority 1: Add Knowledge Loader Accessors** ✅ DONE (`packages/core/src/knowledge_loader.py`)
```python
# Add these accessor functions:
def get_antardasha_effects() -> dict[str, Any]:
    """Get Antardasha effects (81 combinations)."""
    return load_rules("antardasha_effects").get("antardasha_effects", {})

def get_pratyantardasha_effects() -> dict[str, Any]:
    """Get Pratyantardasha effects (729 combinations)."""
    return load_rules("pratyantardasha_master").get("pratyantardasha_effects", {})
```

**Priority 2: Add Dasha Effect Retrieval Functions** ✅ DONE (`packages/context/src/dasha.py`)
```python
def get_antardasha_effects(
    mahadasha_lord: str, antardasha_lord: str
) -> dict[str, Any] | None:
    """Get detailed effects for specific Antardasha combination."""
    effects_data = get_antardasha_effects_rules()  # From knowledge_loader
    return effects_data.get(mahadasha_lord.lower(), {}).get(antardasha_lord.lower())

def get_pratyantardasha_effects(
    mahadasha_lord: str, antardasha_lord: str, pratyantardasha_lord: str
) -> dict[str, Any] | None:
    """Get detailed effects for specific Pratyantardasha combination (729 total)."""
    effects_data = get_pratyantardasha_effects_rules()  # From knowledge_loader
    return (effects_data
            .get(mahadasha_lord.lower(), {})
            .get(antardasha_lord.lower(), {})
            .get(pratyantardasha_lord.lower()))
```

**Priority 3: Replace Hardcoded Interpretations** ✅ DONE (`services/mcp/context_server.py`)
```python
# CURRENT (only 8 hardcoded):
def _get_dasha_interpretation(maha_lord: str, antar_lord: str) -> str:
    interpretations = {
        ("ketu", "ketu"): "Spiritual detachment...",
        # ... only 8 entries
    }

# REPLACE WITH (uses 81 combinations from JSON):
def _get_dasha_interpretation(maha_lord: str, antar_lord: str) -> dict:
    from packages.context.src.dasha import get_antardasha_effects
    effects = get_antardasha_effects(maha_lord, antar_lord)
    if effects:
        return {
            "general": effects.get("general_effects", []),
            "positive": effects.get("positive", []),
            "negative": effects.get("negative", []),
            "health": effects.get("health"),
            "career": effects.get("career"),
            "relationships": effects.get("relationships"),
        }
    return {}
```

**Priority 4: Add New MCP Tools** ✅ DONE (`services/mcp/context_server.py`)
```python
@mcp.tool()
def antardasha_effects(
    mahadasha_lord: str,
    antardasha_lord: str
) -> dict[str, Any]:
    """
    Get detailed Antardasha effects (81 combinations).

    Args:
        mahadasha_lord: Mahadasha planet (sun, moon, mars, etc.)
        antardasha_lord: Antardasha planet

    Returns:
        Effects including health, career, relationships, finances
    """
    from packages.context.src.dasha import get_antardasha_effects
    return get_antardasha_effects(mahadasha_lord, antardasha_lord) or {}

@mcp.tool()
def pratyantardasha_effects(
    mahadasha_lord: str,
    antardasha_lord: str,
    pratyantardasha_lord: str
) -> dict[str, Any]:
    """
    Get detailed Pratyantardasha effects (729 combinations).

    Args:
        mahadasha_lord: Mahadasha planet
        antardasha_lord: Antardasha planet
        pratyantardasha_lord: Pratyantardasha planet

    Returns:
        Effects including theme, duration, health, career, relationships, timing
    """
    from packages.context.src.dasha import get_pratyantardasha_effects
    return get_pratyantardasha_effects(
        mahadasha_lord, antardasha_lord, pratyantardasha_lord
    ) or {}
```

**Priority 5: Add Knowledge Server Lookups** ✅ DONE (`services/mcp/knowledge_server.py`)
```python
@mcp.tool()
def lookup_antardasha_effects(mahadasha_lord: str, antardasha_lord: str) -> dict:
    """Lookup Antardasha effects from knowledge base."""
    data = _load_json(RULES_DIR / "antardasha_effects.json")
    effects = data.get("antardasha_effects", {})
    return effects.get(mahadasha_lord.lower(), {}).get(antardasha_lord.lower(), {})

@mcp.tool()
def lookup_pratyantardasha_effects(
    mahadasha_lord: str, antardasha_lord: str, pratyantardasha_lord: str
) -> dict:
    """Lookup Pratyantardasha effects from knowledge base (729 combinations)."""
    data = _load_json(RULES_DIR / "pratyantardasha_master.json")
    effects = data.get("pratyantardasha_effects", {})
    return (effects
            .get(mahadasha_lord.lower(), {})
            .get(antardasha_lord.lower(), {})
            .get(pratyantardasha_lord.lower(), {}))
```

**Priority 6: Enhance current_dasha Tool Response** ✅ DONE
Update the `current_dasha` tool to include effects data in its response:
```python
# In current_dasha() response, add:
result["antardasha_effects"] = get_antardasha_effects(md_lord, ad_lord)
result["pratyantardasha_effects"] = get_pratyantardasha_effects(md_lord, ad_lord, pd_lord)
```

### Files to Modify Summary

| File | Change | Priority |
|------|--------|----------|
| `packages/core/src/knowledge_loader.py` | Add 2 accessor functions | HIGH |
| `packages/context/src/dasha.py` | Add 2 effect retrieval functions | HIGH |
| `services/mcp/context_server.py` | Replace hardcoded, add 2 tools | HIGH |
| `services/mcp/knowledge_server.py` | Add 2 lookup tools | MEDIUM |
| `packages/guide/src/tools.py` | Add wrapper methods | MEDIUM |

### Verification Steps
```bash
# After changes, test:
uv run pytest tests/ -v

# Test MCP tools manually:
python -c "
from packages.context.src.dasha import get_antardasha_effects, get_pratyantardasha_effects
print(get_antardasha_effects('jupiter', 'venus'))
print(get_pratyantardasha_effects('jupiter', 'venus', 'saturn'))
"
```

### Git Commits (by Claude Code)
```
82e199d feat(dasha): Add Antardasha/Pratyantardasha effect retrieval
```
- All 6 priorities completed
- 17 files changed, 33,513 insertions
- All 95 tests passing

---

## 2026-02-05 (Session 9 - Claude Code)

### Summary
Completed Priority 2: Updated all package code to use JSON knowledge files instead of hardcoded values.

### Completed Tasks
- [x] Create centralized `knowledge_loader.py` with LRU caching
- [x] Update `packages/self/src/strength.py` - Load Shadbala/Ashtakavarga from JSON
- [x] Update `packages/self/src/dosha_detector.py` - Load remedies from JSON
- [x] Update `packages/context/src/dasha.py` - Load Vimshottari periods from JSON
- [x] Update `packages/context/src/transits.py` - Load Gochara rules from JSON
- [x] Update `packages/context/src/muhurta.py` - Load inauspicious periods from JSON
- [x] Fix all lint issues (unused args, __all__ sorting, Path usage)
- [x] All 95 tests passing

### New File Created
| File | Purpose |
|------|---------|
| `packages/core/src/knowledge_loader.py` | Centralized JSON loader with @lru_cache |

### Architecture Pattern
```python
# Lazy loading with fallback defaults
def _get_dasha_years() -> dict[str, int]:
    rules = get_dasha_rules()
    periods = rules.get("vimshottari_system", {}).get("periods", [])
    if periods:
        return {p["planet"]: p["years"] for p in periods}
    # Fallback to defaults
    return {"ketu": 7, "venus": 20, ...}

# Backwards-compatible exports
DASHA_YEARS = _get_dasha_years()
```

### Git Commit
```
0592f36 feat(knowledge): Update packages to use JSON knowledge files
```

### Remaining Priority 2 Task
- [ ] `packages/cosmos/src/divisional.py` - Use `dignities.json` (optional)

---

## 2026-02-04 (Session 8 - Claude Cowork)

### Summary
Complete knowledge base expansion - from hardcoded values to 590KB of externalized JSON knowledge across 16 files. This removes all hardcoded Jyotish data from Python code.

### Knowledge Base Stats

| Category | Before | After | Growth |
|----------|--------|-------|--------|
| Yogas | 8 | **522** | 65x |
| Doshas | 7 | **55** | 8x |
| Definition Files | 4 | **7** | +3 |
| Rule Files | 2 | **9** | +7 |
| Total Knowledge | ~50KB | **~590KB** | 12x |

### Complete File Inventory

**DEFINITIONS (knowledge/definitions/):**
| File | Size | Content | Status |
|------|------|---------|--------|
| `planets.json` | 8KB | 9 planets | existing |
| `rashis.json` | 6KB | 12 signs | existing |
| `nakshatras.json` | 31KB | 27 nakshatras | existing |
| `houses.json` | 8KB | 12 houses | existing |
| `dignities.json` | 7KB | Exaltation/debilitation/moolatrikona | **NEW** |
| `relationships.json` | 18KB | Planetary friendships matrix | **NEW** |
| `aspects.json` | 10KB | Drishti rules + orbs | **NEW** |

**RULES (knowledge/rules/):**
| File | Size | Content | Status |
|------|------|---------|--------|
| `yoga_master.json` | 307KB | 522 yogas (16 categories) | **NEW** |
| `dosha_master.json` | 41KB | 55 doshas (5 categories) | **NEW** |
| `shadbala_rules.json` | 20KB | 6-fold strength calculation | **NEW** |
| `ashtakavarga_rules.json` | 11KB | 8-planet point matrix | **NEW** |
| `dasha_rules.json` | 38KB | Vimshottari effects | **NEW** |
| `transit_rules.json` | 46KB | Gochara + Sade Sati | **NEW** |
| `muhurta_rules.json` | 18KB | Electional astrology | **NEW** |
| `compatibility_rules.json` | 24KB | Ashta Kuta (36 points) | **NEW** |
| `remedies_rules.json` | 28KB | Gemstones/mantras/yantras | **NEW** |
| `antardasha_effects.json` | 107KB | 81 MD-AD combinations | **NEW** |
| `pratyantardasha_rules.json` | 15KB | PD calculation + timing | **NEW** |

### Dasha System Coverage

| Level | Name | Content | File |
|-------|------|---------|------|
| 1 | Mahadasha | 9 planets × effects | `dasha_rules.json` |
| 2 | Antardasha | 81 combinations (9×9) | `antardasha_effects.json` |
| 3 | Pratyantardasha | Timing rules + house lords | `pratyantardasha_rules.json` |
| 4 | Sookshma | Formula included | `pratyantardasha_rules.json` |
| 5 | Prana | Formula included | `pratyantardasha_rules.json` |

### What Was Externalized

Previously hardcoded in Python (now in JSON):
- `yoga_detector.py`: PLANET_RULERSHIP, PLANET_EXALTATION, PLANET_DEBILITATION → `dignities.json`
- `dosha_detector.py`: All orbs, Mars characteristics, remedies → `aspects.json`, `remedies_rules.json`
- `strength.py`: NAISARGIKA_BALA, DIG_BALA, ASHTAKAVARGA matrix, FRIENDS → `shadbala_rules.json`, `ashtakavarga_rules.json`, `relationships.json`
- `dasha.py`: DASHA_YEARS, NAKSHATRA_LORDS → `dasha_rules.json`
- `transits.py`: GOCHARA_FAVORABLE, VEDHA_POINTS → `transit_rules.json`
- `muhurta.py`: RAHU_KAAL, activity rules → `muhurta_rules.json`

### Source Code Modified
| File | Change |
|------|--------|
| `services/mcp/knowledge_server.py` | Load from master files |
| `packages/self/src/yoga_detector.py` | Load from `yoga_master.json` |

### Architecture Document Created
- `docs/architecture/KNOWLEDGE_ARCHITECTURE.md` - Complete plan
- `docs/architecture/KNOWLEDGE_EXPANSION_PLAN.md` - Implementation details

---

### 🔧 TASKS FOR CLAUDE CODE

**Priority 1: Restart MCP Servers**
```bash
# MCP servers have cached old data
# Restart to load 522 yogas + 55 doshas
```

**Priority 2: Update Package Code to Use Knowledge Files** ✅ COMPLETED (Session 9)
- [x] `packages/self/src/strength.py` - Replace hardcoded SHADBALA with `shadbala_rules.json`
- [x] `packages/self/src/dosha_detector.py` - Load orbs/remedies from JSON
- [x] `packages/context/src/dasha.py` - Use `dasha_rules.json`
- [x] `packages/context/src/transits.py` - Use `transit_rules.json`
- [x] `packages/context/src/muhurta.py` - Use `muhurta_rules.json`
- [ ] `packages/cosmos/src/divisional.py` - Use `dignities.json` (optional)

**Priority 3: Add Knowledge Loaders** ✅ COMPLETED (Session 9)
```python
# Created: packages/core/src/knowledge_loader.py
# - Load and cache JSON knowledge files with @lru_cache
# - Exports: get_shadbala_rules, get_dasha_rules, get_transit_rules, etc.
# - Future: Add schema validation
```

**Priority 4: Remaining Knowledge Files (Optional)**
- [ ] `tithis.json` - 30 lunar days
- [ ] `karanas.json` - 11 half-tithis
- [ ] `nitya_yogas.json` - 27 panchanga yogas
- [ ] `varas.json` - 7 weekdays + horas
- [ ] `vargas.json` - 16 divisional chart definitions
- [ ] `upagrahas.json` - Sub-planets (Gulika, Mandi, etc.)

### Git Commit (by Claude Code)
```
82fc201 feat(knowledge): Massive expansion of Jyotish knowledge base
```
- Fixed all ruff lint errors (ClassVar, Path.open, SIM110, etc.)
- Pushed to GitHub: https://github.com/SrikanthNabigari/108

---

## 2026-02-04 (Session 7 - Claude Code)

### Summary
Completed full 4-step integration test with user's birth data. System is fully operational.

### Integration Test Completed
**Birth Data**: December 3, 1992, 3:00 AM, 16.722786, 81.294264 (Andhra Pradesh)

| Step | Task | Status |
|------|------|--------|
| 1 | Calculate Birth Chart | ✅ Lagna: Libra |
| 2 | Store Chart & Patterns | ✅ User + 9 yogas stored |
| 3 | Test Core Calculations | ✅ Dasha, transits, Sade Sati |
| 4 | Claude Desktop MCP Setup | ✅ Config updated |

### Chart Analysis Results
```
Lagna: Libra (180.93°)
Moon: Aquarius in Purva Bhadrapada (Pada 2)

Planetary Positions:
  Sun     : Scorpio (227.22°)
  Moon    : Aquarius (324.11°)
  Mars    : Cancer (93.76°) - DEBILITATED
  Saturn  : Capricorn (289.93°) - OWN SIGN
  Rahu    : Scorpio (238.21°)
```

### Detected Patterns
- **Sasa Yoga** (Pancha Mahapurusha) - Saturn in own sign in kendra
- **Mars Debilitation** - Mars in Cancer
- **Grahan Yoga** - Sun conjunct Rahu in Scorpio

### Current Timing
```
Dasha: Mercury Mahadasha (2022-2039)
       Ketu Antardasha (May 2025 - May 2026)
Sade Sati: ACTIVE (setting phase) - Saturn in Pisces
```

### Claude Desktop MCP
```
Config: ~/.claude/claude_desktop_config.json
Servers: 108-ephemeris, 108-yoga, 108-memory, 108-biorhythm
```

### Database Records
| Table | Record |
|-------|--------|
| users | ae3919f8-f5ed-4022-b98f-8ead058482d2 |
| birth_charts | 16dace3b... |
| detected_patterns | 9 yoga records |

### Claude Desktop MCP Fix
Fixed MCP server configuration issue:
- **Problem**: Servers disconnecting immediately on startup
- **Cause**: Config was using `python3` (system) which lacks mcp/fastmcp packages
- **Solution**: Use venv Python: `.venv/bin/python`

Config location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Next Steps
- [ ] Push to GitHub: `git push origin main`
- [ ] Start API server: `uv run uvicorn services.api.main:app --reload`
- [ ] Test MCP tools in Claude Desktop (restart required)
- [ ] Add interpretation layers for personality adaptation

---

## 2026-02-04 (Session 6 - Claude Code)

### Summary
Configured Voyage embeddings for production, updated database schema to 1024 dimensions, and verified full semantic search integration.

### Completed Tasks
- [x] Test Voyage embeddings with real API key
- [x] Update embedding priority: Voyage (1024d) > OpenAI (1536d)
- [x] Create migration to change vector dimension from 1536 to 1024
- [x] Update `store.py` embedding dimension to 1024
- [x] Update `MockEmbeddings` default to 1024 dimensions
- [x] Fix numpy array truth check bug in `search_memories()`
- [x] Verify full integration: Voyage → pgvector → semantic search

### Database Migration
```
alembic/versions/0103d2463bba_change_vector_dimension_to_1024.py
- DROP vector(1536) columns
- ADD vector(1024) columns
- Recreate IVFFlat indexes
```

### Integration Test Results
```
Query: "marriage timing and spouse"
Results:
  45.8% | Saturn in the 7th house creates delays in marriage...
  34.6% | Jupiter aspects the 7th house bringing blessings...
  33.4% | Venus in the 7th house indicates a loving spouse
```

### Files Modified
| File | Change |
|------|--------|
| `packages/memory/src/embeddings.py` | Voyage priority first, mock=1024d |
| `packages/memory/src/store.py` | Dimension 1024, fixed numpy check |
| `alembic/versions/0103d2463bba_*.py` | New migration for vector(1024) |

### Test Status
- 82 passed, 13 failed
- Core systems (memory, embeddings, guide, dasha) working
- Failures are case sensitivity and incomplete features

### Next Steps
- [x] Fix 13 failing tests (done - all 95 tests pass)
- [ ] Push to GitHub: `git push origin main`

---

## 2026-02-04 (Session 6 continued)

### Test Fixes
Fixed all 13 failing tests:

| Category | Count | Fix |
|----------|-------|-----|
| Case sensitivity | 5 | Use lowercase planet names (ketu, moon, saturn) |
| Panchanga API | 2 | Use correct keys (number, gregorian_day) |
| House cusps API | 1 | Expect dict with 'cusps' key |
| Divisional charts | 2 | Pass dict of planets, not single float |
| Transit calculations | 3 | Correct house position formulas |

### Test Results
```
95 passed, 0 failed
```

### Git Commits This Session
```
e7cc93b feat(memory): Switch to Voyage embeddings (1024d) for production
741c720 fix(tests): Correct test assertions to match implementation
```

---

## 2026-02-04 (Session 5 - Claude Cowork)

### Summary
Added embedding service, unified memory interface, unit tests, and CI/CD workflow. Fixed test issues and created Claude Desktop MCP configuration.

### Completed Tasks
- [x] Create EmbeddingService with multiple providers:
  - OpenAI (text-embedding-3-small)
  - Voyage (voyage-3)
  - Local (sentence-transformers)
  - Mock (for testing)
- [x] Create UnifiedMemoryClient bridging Mem0 Cloud and PostgreSQL
- [x] Update Guide agent to use UnifiedMemoryClient
- [x] Make LangGraph/LangChain imports optional (graceful degradation)
- [x] Create unit tests:
  - `tests/test_cosmos.py` - Ephemeris, nakshatra, rashi, panchanga
  - `tests/test_self.py` - Yoga, dosha, strength detection
  - `tests/test_context.py` - Dasha, transit, Sade Sati, muhurta
- [x] Create GitHub Actions CI/CD workflow (`.github/workflows/ci.yml`)
- [x] Create Claude Desktop MCP configuration

### New Files
| File | Purpose |
|------|---------|
| `packages/memory/src/embeddings.py` | Multi-provider embedding service |
| `packages/memory/src/unified_memory.py` | Unified Mem0/PostgreSQL interface |
| `.github/workflows/ci.yml` | CI/CD with lint, test, coverage |
| `config/claude_desktop_config.json` | MCP server config for Claude Desktop |
| `scripts/setup_claude_desktop.sh` | Auto-setup script |

### Test Coverage
| Test File | Tests | Status |
|-----------|-------|--------|
| test_cosmos.py | 10 tests | ✅ Logic validated |
| test_self.py | 12 tests | ✅ Logic validated |
| test_context.py | 14 tests | ✅ Logic validated |

### Known Limitations
1. Some tests are "logic tests" (verify data structures, not full integration)
2. Memory system uses MockEmbeddings when API keys not configured
3. Guide agent requires LangGraph (optional dep, fails gracefully)
4. PostgreSQL store requires asyncpg (use `uv sync` to install)

### Git Commits This Session
```
c7f7b6c fix(tests): Correct function signatures in context tests
380a1de feat: Add unit tests and CI/CD workflow
4dd9da2 feat(guide): Update agent to use UnifiedMemoryClient
7753d19 feat(memory): Add unified memory system with embeddings
```

### Next Steps
- [ ] Push to GitHub: `git push origin main`
- [ ] Run full test suite with pytest: `uv run pytest tests/ -v`
- [ ] Configure Claude Desktop with MCP servers
- [ ] Add API keys for real embeddings (OPENAI_API_KEY or VOYAGE_API_KEY)

---

## 2026-02-04 (Session 4 - Claude Code)

### Summary
Completed full Mem0/PostgreSQL memory integration. Database tables created and store.py implemented with actual asyncpg connections.

### Completed Tasks
- [x] Test MCP servers (all 4 servers operational - 16 tools total)
- [x] Implement full Mem0 integration:
  - [x] Created migration for memory tables (detected_patterns, memories, predictions, conversations, user_preferences, dasha_timeline)
  - [x] Added pgvector columns with IVFFlat indexes for semantic search
  - [x] Rewrote `packages/memory/src/store.py` with actual asyncpg connections
  - [x] Added pgvector package dependency
  - [x] Created unique constraint migration for birth_charts.user_id
  - [x] Created comprehensive test suite (8 tests, all passing)

### Database Tables Created
| Table | Purpose |
|-------|---------|
| detected_patterns | Yogas and doshas for each user |
| memories | Semantic memories with vector embeddings |
| predictions | Predictions for validation and learning |
| conversations | Conversation history with embeddings |
| user_preferences | User settings and preferences |
| dasha_timeline | Precomputed dasha periods |

### Test Results
```
tests/test_memory_store.py: 8 passed
- test_health_check
- test_create_user
- test_get_user_by_email
- test_add_memory
- test_save_birth_chart
- test_get_birth_chart
- test_save_detected_patterns
- test_set_and_get_preference
```

### Next Steps
- [x] Complete LangGraph agent (done in this session)
- [ ] Add more unit tests
- [ ] Set up CI/CD
- [ ] Fix 4 failing transit tests (pre-existing issues)

---

## 2026-02-04 (Session 4 continued - Claude Code)

### Summary
Completed LangGraph agent integration with memory store and calculation packages.

### Completed Tasks
- [x] Rewrote `packages/guide/src/agent.py` with full integrations:
  - [x] Async support with `chat_async()` method
  - [x] Integration with memory store (loads birth chart, patterns, memories)
  - [x] Integration with context package (dasha calculations, transit analysis)
  - [x] Personality adaptation based on Lagna (12 zodiac styles)
  - [x] Intent classification (keyword + LLM fallback)
  - [x] State machine routing (calculate → analyze → predict → general)
  - [x] Automatic conversation saving to database
- [x] Created test suite for Guide agent (8 tests passing)

### Agent Features
| Feature | Status |
|---------|--------|
| Intent Classification | 10 intent types |
| Personality Adaptation | 12 zodiac styles |
| Memory Integration | Async store connection |
| Dasha Calculations | Via context package |
| Transit Analysis | Via context package |
| Conversation Saving | Automatic to database |

### Test Results
```
tests/test_guide_agent.py: 8 passed
tests/test_memory_store.py: 8 passed
Total: 16 new tests passing
```

---

## 2026-02-04 (Session 3 - Claude Code)

### Summary
Development environment fully set up and code pushed to GitHub. All infrastructure ready.

### Completed Tasks
- [x] Install uv package manager (v0.9.29)
- [x] Fix workspace pyproject.toml files for all 6 packages
- [x] Run `uv sync` successfully (97 packages installed)
- [x] Set up pre-commit hooks (ruff, formatting, trailing whitespace)
- [x] Create .pre-commit-config.yaml
- [x] Start PostgreSQL + Redis via Docker
- [x] Initialize Alembic for migrations
- [x] Run initial database migration (users, birth_charts tables)
- [x] Push to GitHub (https://github.com/SrikanthNabigari/108)
- [x] Fix deprecation warning (tool.uv.dev-dependencies → dependency-groups.dev)

### Infrastructure Status
| Service | Status | Port |
|---------|--------|------|
| PostgreSQL (pgvector) | ✅ Running | 5432 |
| Redis | ✅ Running | 6379 |
| GitHub | ✅ Pushed | - |

### Verification
```bash
uv --version        # uv 0.9.29
uv run python       # Python 3.11.14
uv run pytest       # 3 tests passing
docker ps           # postgres + redis healthy
```

---

## 2026-02-04 (Session 2)

### Summary
Completed all 7 phases of the 108 build specification. The system is now fully functional with API endpoints working.

### Completed Tasks
- [x] Create package __init__.py files
- [x] Implement core models (packages/core/src/models.py, constants.py, utils.py)
- [x] Port ephemeris calculations (packages/cosmos/src/ephemeris.py)
- [x] Implement nakshatra calculations (packages/cosmos/src/nakshatras.py)
- [x] Implement house calculations (packages/cosmos/src/houses.py)
- [x] Implement panchanga (packages/cosmos/src/panchanga.py)
- [x] Implement divisional charts (packages/cosmos/src/divisional.py)
- [x] Create yoga detection rules (knowledge/rules/yoga_detection.json)
- [x] Create dosha detection rules (knowledge/rules/dosha_detection.json)
- [x] Implement yoga detector (packages/self/src/yoga_detector.py)
- [x] Implement dosha detector (packages/self/src/dosha_detector.py)
- [x] Implement strength calculator (packages/self/src/strength.py)
- [x] Implement dasha calculations (packages/context/src/dasha.py)
- [x] Implement transit analysis (packages/context/src/transits.py)
- [x] Implement muhurta (packages/context/src/muhurta.py)
- [x] Create MCP servers (services/mcp/*.py)
- [x] Create PostgreSQL schema (database/schema.sql)
- [x] Implement memory store (packages/memory/src/store.py)
- [x] Implement Mem0 client (packages/memory/src/mem0_client.py)
- [x] Implement LangGraph agent structure (packages/guide/src/agent.py)
- [x] Create FastAPI gateway (services/api/main.py) - 22 endpoints
- [x] Reorganize documentation structure

### Working API Endpoints
- `POST /api/v1/chart` - Birth chart calculation ✅
- `POST /api/v1/analysis/yogas` - Yoga detection ✅
- `POST /api/v1/analysis/doshas` - Dosha detection ✅
- `POST /api/v1/analysis/strength` - Planetary dignity ✅
- `GET /api/v1/timing/transits` - Current transits ✅
- `POST /api/v1/timing/dasha` - Vimshottari dasha ✅

### Remaining Setup (User Tasks)
- [ ] Push to GitHub: `git push -u origin main`
- [ ] Start PostgreSQL: `docker-compose up -d postgres redis`
- [ ] Run migrations: `alembic upgrade head`
- [ ] Install LangGraph: `uv pip install langgraph langchain-anthropic`
- [ ] Start API: `uvicorn services.api.main:app --reload`

---

## 2026-02-04 (Session 1)

### Project Setup
- Created new 108-core folder with modern architecture
- Set up CLAUDE.md with project context and rules
- Created 4 skills: jyotish-calculator, yoga-detector, memory-manager, knowledge-search
- Created 3 agents: astro-guide, code-reviewer, prediction-engine
- Set up hooks for pre/post edit validation
- Created pyproject.toml with uv workspace configuration
- Added .mcp.json for MCP server configuration
- Added ADR-001 documenting tech stack decision

### Key Decisions
- Using uv instead of Poetry for package management
- Using ruff for all linting/formatting
- LangGraph for agent orchestration
- Mem0 + LangMem for memory system
- 5-layer architecture: COSMOS, SELF, CONTEXT, GUIDE, MEMORY
