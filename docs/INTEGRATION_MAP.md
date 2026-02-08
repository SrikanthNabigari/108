# 108 Integration Map

> Complete mapping of mobile app screens, gateway API endpoints, backend packages, MCP tools, database schema, and what is connected vs what is still a mockup.
>
> Generated: 2026-02-07

---

## Table of Contents

1. [Mobile App Screens](#1-mobile-app-screens)
2. [Gateway API Endpoints](#2-gateway-api-endpoints)
3. [Backend Packages](#3-backend-packages-packagessrc)
4. [MCP Servers and Tools](#4-mcp-servers-and-tools)
5. [Mobile to Gateway Wiring](#5-mobile-to-gateway-wiring)
6. [Connected vs Mockup Status](#6-connected-vs-mockup-status)
7. [Database Schema](#7-database-schema)
8. [Data Flow Architecture](#8-data-flow-architecture)

---

## 1. Mobile App Screens

The Flutter mobile app lives in `mobile/lib/features/`. It uses Riverpod for state management, GoRouter for navigation, and Supabase for authentication.

### 1.1 Auth Screens

| Screen | File | What It Shows | Data Source |
|--------|------|---------------|-------------|
| Phone Auth | `features/auth/screens/phone_auth_screen.dart` | Phone number input with country code, Send OTP button, skip option | **REAL** -- calls `SupabaseService().signInWithPhone()` |
| OTP Verify | `features/auth/screens/otp_verify_screen.dart` | 6-digit OTP input, resend timer, verify button | **REAL** -- calls `SupabaseService().verifyOtp()` |

**Widgets:**
- `features/auth/widgets/social_login_buttons.dart` -- Google/Apple sign-in buttons (calls `SupabaseService().signInWithGoogle()` / `signInWithApple()`)

### 1.2 Onboarding Screens

| Screen | File | What It Shows | Data Source |
|--------|------|---------------|-------------|
| Profile | `features/onboarding/screens/profile_screen.dart` | Name input, gender selection (Male/Female/Other) | **REAL** -- calls `ApiService().put(ApiConstants.userMe)` to save name/gender |
| Birth Details | `features/onboarding/screens/birth_details_screen.dart` | Date picker, time picker, place search with geocoding | **REAL** -- calls `ApiService().put(ApiConstants.userBirthDetails)` to save birth data |

**Widgets:**
- `features/onboarding/widgets/place_search_field.dart` -- Location autocomplete with lat/lon extraction

### 1.3 Main Tab Screens (Bottom Nav)

| Screen | File | Nav Index | What It Shows | Data Source |
|--------|------|-----------|---------------|-------------|
| Home | `features/home/screens/home_screen.dart` | 0 | Greeting, today's score, chart summary, life area ratings, panchanga | **REAL** -- calls `GET /api/v1/forecast/daily` and `GET /api/v1/chart/summary` via providers |
| Chart | `features/chart/screens/chart_screen.dart` | 1 | South Indian chart grid, planet list, divisional chart tabs (D1/D9/D10) | **MOCKUP** -- all planet data is hardcoded inline (Sun in Scorpio, Moon in Aquarius, etc.) |
| Chat | `features/chat/screens/chat_screen.dart` | 2 | AI chat interface, message counter, rate limiting | **MOCKUP** -- uses `Future.delayed(1s)` to simulate API; hardcoded bot response |
| Calendar | `features/calendar/screens/calendar_screen.dart` | 3 | Monthly calendar grid, upcoming events list | **MOCKUP** -- hardcoded events (Full Moon Feb 14, Mercury Retrograde Feb 22, etc.) |
| Settings | `features/settings/screens/settings_screen.dart` | 4 | Profile card, subscription tier, credits balance, app links, sign out | **MOCKUP** -- hardcoded "Seeker Name", "45 credits", "Nakshatra (Free)" plan |

### 1.4 Feature Screens (Non-Tab)

| Screen | File | What It Shows | Data Source |
|--------|------|---------------|-------------|
| Timeline | `features/timeline/screens/timeline_screen.dart` | Sade Sati alert, Mahadasha period cards (Mercury/Saturn/Venus/Sun) | **MOCKUP** -- all dasha periods and dates are hardcoded strings |
| Muhurta | `features/muhurta/screens/muhurta_screen.dart` | Activity picker, date picker, auspicious time results | **MOCKUP** -- results are hardcoded (Feb 18 score 9.2, Feb 22 score 8.5, etc.) |
| Remedies | `features/remedies/screens/remedies_screen.dart` | Urgent/recommended remedies, gemstone recommendations | **MOCKUP** -- hardcoded Saturn Sade Sati, Mars Strengthening, Blue Sapphire, Emerald |
| Compatibility | `features/compatibility/screens/compatibility_screen.dart` | Placeholder text "Compatibility" | **STUB** -- completely empty placeholder, no UI built |
| Reports Store | `features/reports/screens/reports_store_screen.dart` | Grid of 6 purchasable reports with prices | **MOCKUP** -- hardcoded report list (Year Ahead $4.99, Career Blueprint $5.99, etc.) |
| Report View | `features/reports/screens/report_view_screen.dart` | Placeholder showing "Report {id}" | **STUB** -- empty placeholder |
| Paywall | `features/paywall/screens/paywall_screen.dart` | 3 subscription tiers: Nakshatra/Graha/Rishi with feature comparison | **MOCKUP** -- hardcoded tier data and prices, no RevenueCat integration in UI |
| Credit Store | `features/paywall/screens/credit_store_screen.dart` | Credit balance, 3 credit packs, report price reference | **MOCKUP** -- hardcoded "45 Credits", pack prices, report prices |

### 1.5 Shared Widgets

| Widget | File | Description |
|--------|------|-------------|
| Today Score Card | `features/home/widgets/today_score_card.dart` | Circular score display (0-10) |
| Quick Cards Row | `features/home/widgets/quick_cards_row.dart` | Navigation shortcuts to features |
| Area Rating Bars | `features/home/widgets/area_rating_bars.dart` | Horizontal bars for life areas (Career, Finance, etc.) |
| Forecast Tabs | `features/home/widgets/forecast_tabs.dart` | Daily/Weekly/Monthly/Yearly tabs with lock icons for gated content |
| South Indian Chart | `features/chart/widgets/south_indian_chart.dart` | Traditional South Indian chart grid renderer |
| Planet List | `features/chart/widgets/planet_list.dart` | Scrollable planet detail rows |
| Planet Detail Sheet | `features/chart/widgets/planet_detail_sheet.dart` | Bottom sheet with planet details on tap |
| Chat Bubble | `features/chat/widgets/chat_bubble.dart` | Message bubble (user/bot) |
| Chat Input Bar | `features/chat/widgets/chat_input_bar.dart` | Text input with send button |
| Remaining Counter | `features/chat/widgets/remaining_counter.dart` | Chat quota counter display |
| Dasha Chapter Card | `features/timeline/widgets/dasha_chapter_card.dart` | Timeline card for a Mahadasha period |

---

## 2. Gateway API Endpoints

The gateway API is a single FastAPI application at `services/api/main.py`. It runs on `http://localhost:8001`.

### 2.1 Health and Root

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root endpoint with API info |
| GET | `/health` | Health check (status, version, timestamp) |

### 2.2 Chart (Birth Chart Calculations)

| Method | Path | Description | Backend Package |
|--------|------|-------------|-----------------|
| POST | `/api/v1/chart` | Calculate complete birth chart (planets, houses, ascendant, nakshatra) | `cosmos` |
| POST | `/api/v1/chart/divisional/{division}` | Calculate divisional chart D1-D60 | `cosmos` |

### 2.3 Analysis (Yogas, Doshas, Strength)

| Method | Path | Description | Backend Package |
|--------|------|-------------|-----------------|
| POST | `/api/v1/analysis` | Basic chart analysis (planets, navamsha) | `cosmos` |
| POST | `/api/v1/analysis/yogas` | Detect yogas in birth chart | `cosmos` + `self` |
| POST | `/api/v1/analysis/doshas` | Detect doshas in birth chart | `cosmos` + `self` |
| POST | `/api/v1/analysis/strength` | Calculate planetary and house strengths (Shadbala, Bhava Bala) | `cosmos` + `self` |
| POST | `/api/v1/analysis/aspects` | Calculate planetary aspects | `cosmos` |
| POST | `/api/v1/analysis/bhava-bala` | Bhava Bala house strength | `self` |
| POST | `/api/v1/analysis/yoga-cancellations` | Check yoga cancellation rules | `self` |
| POST | `/api/v1/analysis/neecha-bhanga` | Detect Neecha Bhanga (5-condition debilitation cancellation) | `self` |
| POST | `/api/v1/analysis/planetary-wars` | Detect planetary wars | `self` |
| POST | `/api/v1/analysis/bhava-chalit` | Calculate Bhava Chalit chart | `cosmos` |
| POST | `/api/v1/analysis/navamsha-spouse` | Navamsha spouse analysis | `self` |
| POST | `/api/v1/analysis/remedies` | Personalized chart remedies | `self` |
| POST | `/api/v1/analysis/synastry` | Synastry / composite chart analysis between two charts | `self` |
| POST | `/api/v1/analysis/gem-recommendation` | Gemstone recommendations based on lagna | `self` |
| POST | `/api/v1/analysis/atmakaraka` | Atmakaraka deep analysis (Jaimini) | `self` |

### 2.4 KP Analysis (Krishnamurti Paddhati)

| Method | Path | Description | Backend Package |
|--------|------|-------------|-----------------|
| GET | `/api/v1/analysis/kp-sublord` | Get KP sublord for a longitude | `self` |
| POST | `/api/v1/analysis/kp-significators` | Get KP significators | `self` |
| POST | `/api/v1/analysis/kp-prediction` | KP-based prediction | `self` |

### 2.5 Timing (Dasha, Transits, Muhurta)

| Method | Path | Description | Backend Package |
|--------|------|-------------|-----------------|
| POST | `/api/v1/timing` | Full timing analysis (dasha + sade sati + transits) | `context` |
| POST | `/api/v1/timing/dasha` | Get current Vimshottari dasha periods | `context` |
| GET | `/api/v1/timing/transits` | Get current transit positions | `context` |
| POST | `/api/v1/timing/muhurta` | Check muhurta for a specific activity/time | `context` |
| GET | `/api/v1/timing/abhijit-muhurta` | Get Abhijit muhurta window for a date/location | `context` |
| GET | `/api/v1/timing/brahma-muhurta` | Get Brahma muhurta window for a date/location | `context` |
| GET | `/api/v1/timing/eclipses/{year}/{month}` | Get eclipse periods for a month | `context` |
| POST | `/api/v1/dasha/ashtottari` | Calculate Ashtottari dasha system | `context` |
| POST | `/api/v1/progressions/current` | Get current secondary progressions | `context` |
| POST | `/api/v1/timing/dasha-transit` | Dasha-Transit cross-analysis (killer feature) | `context` |
| POST | `/api/v1/timing/transit-aspects` | Transit-to-natal aspects | `context` |
| POST | `/api/v1/timing/event-correlation` | Correlate life event to astrological factors | `context` |
| POST | `/api/v1/timing/upcoming-triggers` | Find upcoming transit triggers | `context` |
| POST | `/api/v1/timing/varshaphal` | Solar return / annual chart analysis | `context` |

### 2.6 Forecast (Daily/Weekly/Monthly)

| Method | Path | Description | Backend Package |
|--------|------|-------------|-----------------|
| POST | `/api/v1/forecast/daily` | Daily forecast with panchanga, day rating, area scores | `context` |
| POST | `/api/v1/forecast/weekly` | Weekly forecast with peak/challenging days | `context` |
| POST | `/api/v1/forecast/monthly` | Monthly forecast with retrogrades, major transits | `context` |

### 2.7 Chat (AI Agent)

| Method | Path | Description | Backend Package |
|--------|------|-------------|-----------------|
| POST | `/api/v1/chat` | Send message to LangGraph agent | `guide` + `memory` |

### 2.8 Users

| Method | Path | Description | Backend Package |
|--------|------|-------------|-----------------|
| GET | `/api/v1/users/{user_id}` | Get user profile + birth chart | `memory` |
| POST | `/api/v1/users` | Create new user with birth data | `memory` + `cosmos` |

### 2.9 Knowledge

| Method | Path | Description | Backend Package |
|--------|------|-------------|-----------------|
| GET | `/api/v1/knowledge/tithis/{number}` | Lookup tithi details | `core` (knowledge) |
| GET | `/api/v1/knowledge/karanas/{name}` | Lookup karana details | `core` (knowledge) |
| GET | `/api/v1/knowledge/varas/{name}` | Lookup vara (weekday) details | `core` (knowledge) |
| GET | `/api/v1/knowledge/avasthas/{planet}` | Lookup planetary avastha | `core` (knowledge) |
| GET | `/api/v1/knowledge/nitya-yogas/{number}` | Lookup nitya yoga details | `core` (knowledge) |
| GET | `/api/v1/knowledge/planets/{planet_id}` | Lookup planet details | `core` (knowledge) |
| GET | `/api/v1/knowledge/nakshatras/{nakshatra_name}` | Lookup nakshatra details | `core` (knowledge) |
| GET | `/api/v1/knowledge/rashis/{rashi_name}` | Lookup rashi details | `core` (knowledge) |

**Total: ~48 REST endpoints**

---

## 3. Backend Packages (`packages/*/src/`)

### 3.1 `packages/core/` -- Shared Types and Utilities

The foundation package. Contains no calculations, only types, enums, models, knowledge loaders, and utilities.

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `models.py` | Pydantic v2 models | `BirthChart`, `BirthData`, `PlanetPosition`, `HouseCusps`, `NakshatraInfo`, `Panchanga`, `DetectedYoga`, `DetectedDosha`, `CurrentDasha`, `DashaPeriod`, `UserProfile`, `PrashnaChart`, etc. |
| `constants.py` | Enums and constants | `Planet`, `Rashi`, `HouseSystem`, `AyanamsaType`, `DashaSystem`, `YogaCategory`, `CharaKaraka`, `YoginiName`, `DASHA_YEARS`, `DASHA_SEQUENCE` |
| `knowledge_loader.py` | JSON knowledge base loader | `load_definition()`, `load_rules()`, `get_yoga_rules()`, `get_dosha_rules()`, `get_planets()`, `get_rashis()`, `get_nakshatras()`, `get_houses()`, `get_muhurta_rules()`, etc. |
| `utils.py` | Zodiac math utilities | `longitude_to_rashi()`, `longitude_to_nakshatra()`, `normalize_degrees()`, `is_kendra()`, `is_trikona()`, `is_dusthana()`, `is_upachaya()` |

### 3.2 `packages/cosmos/` -- Ephemeris Calculations

Swiss Ephemeris-powered astronomical calculations. The computational engine of the system.

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `ephemeris.py` | Core planetary positions | `get_julian_day()`, `get_all_planets()`, `get_planet_position()`, `get_house_cusps()`, `get_ascendant()`, `get_ayanamsa()` |
| `nakshatras.py` | Lunar mansion calculations | `longitude_to_nakshatra()`, `get_nakshatra_lord()`, `get_pada_navamsha()`, `get_tarabala()` |
| `divisional.py` | Divisional charts D1-D60 | `get_divisional_chart()`, `get_navamsha()`, `get_dashamsha()`, `get_hora()`, `get_drekkana()`, `calculate_vimshopaka_bala()` |
| `houses.py` | House system calculations | `get_house_for_longitude()`, `get_house_lord()`, `get_planets_in_house()`, `get_house_analysis()` |
| `aspects.py` | Planetary aspects | `get_planet_aspects()`, `get_all_aspects()`, `get_aspect_strength()`, `get_houses_aspected_by()` |
| `panchanga.py` | Panchanga (5-element calendar) | `get_panchanga()`, `get_tithi()`, `get_vara()`, `get_yoga()`, `get_karana()` |
| `bhava_chalit.py` | Bhava Chalit chart | `calculate_bhava_chalit()`, `get_shifted_planets()` |
| `sunrise_sunset.py` | Sunrise/sunset times | `get_sunrise_sunset()`, `get_sunrise()`, `get_sunset()` |
| `upagrahas.py` | Sub-planetary points | `calculate_all_upagrahas()`, `calculate_gulika()`, `calculate_mandi()`, etc. |

### 3.3 `packages/self/` -- Pattern Detection

Analyzes birth charts to detect yogas, doshas, personality patterns, compatibility, and remedies.

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `yoga_detector.py` | Yoga detection engine | `YogaDetector`, `detect_all_yogas()`, `detect_yoga()`, `detect_neecha_bhanga()` |
| `dosha_detector.py` | Dosha detection engine | `DoshaDetector` |
| `yoga_cancellation.py` | Yoga cancellation rules | `check_yoga_cancellation()`, `apply_cancellations_to_chart()` |
| `strength.py` | Planetary strength (Shadbala) | `StrengthCalculator` |
| `ashtakavarga.py` | Ashtakavarga system | `calculate_bhinnashtakavarga()`, `calculate_sarvashtakavarga()` |
| `compatibility.py` | Ashta Kuta matching | `calculate_ashta_kuta()` (8 kuta scores) |
| `synastry.py` | Synastry and composite charts | `get_synastry_report()`, `calculate_cross_aspects()`, `calculate_house_overlay()`, `calculate_composite_chart()` |
| `gem_recommender.py` | Gemstone prescriptions | `recommend_gems()`, `check_gem_compatibility()`, `get_lagna_gem_map()` |
| `jaimini.py` | Jaimini astrology | `get_atmakaraka()`, `get_atmakaraka_analysis()`, `get_ishta_devata()`, `calculate_chara_karakas()`, `calculate_chara_dasha()`, `calculate_all_arudha_padas()` |
| `kp.py` | Krishnamurti Paddhati | `get_kp_sublord()`, `get_kp_significators()`, `get_kp_prediction()`, `get_cuspal_sublords()` |
| `prashna.py` | Prashna (horary) astrology | `analyze_prashna()`, `judge_prashna()`, `predict_timing()` |
| `divisional_interpreter.py` | Divisional chart interpretation | `interpret_d9_chart()`, `interpret_d10_chart()`, `get_divisional_analysis()` |
| `remedies.py` | Remedy recommendations | `recommend_remedies()`, `prioritize_remedies()`, `get_planet_remedies()` |
| `planetary_war.py` | Planetary war detection | `detect_planetary_wars()`, `get_war_effects()` |
| `combustion.py` | Combustion analysis | `check_combustion()`, `get_combustion_analysis()` |
| `retrograde.py` | Retrograde effects | `get_retrograde_analysis()`, `get_retrograde_effects()` |

### 3.4 `packages/context/` -- Timing and Transits

Dasha systems, transits, muhurta, forecasts, and event correlation.

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `dasha.py` | Vimshottari dasha system | `get_current_dasha()`, `get_mahadasha_sequence()`, `get_antardasha_sequence()`, `get_pratyantardasha_sequence()` |
| `transits.py` | Transit analysis | `get_transit_positions()`, `check_sade_sati()`, `check_dhaiya()`, `get_full_transit_analysis()` |
| `muhurta.py` | Muhurta (electional astrology) | `evaluate_muhurta()`, `find_next_good_muhurta()`, `calculate_rahu_kaal()`, `get_abhijit_muhurta()`, `get_brahma_muhurta()` |
| `daily_forecast.py` | Daily forecast engine | `get_daily_forecast()` |
| `weekly_forecast.py` | Weekly forecast engine | `get_weekly_forecast()` |
| `monthly_forecast.py` | Monthly forecast engine | `get_monthly_forecast()` |
| `dasha_transit.py` | Dasha-Transit cross-analysis | `cross_analyze()`, `find_activation_windows()` |
| `transit_aspects.py` | Transit-natal aspects | `get_transit_natal_aspects()`, `find_upcoming_aspects()` |
| `transit_tracker.py` | Upcoming transit triggers | `get_upcoming_triggers()` |
| `event_correlator.py` | Life event correlation | `correlate_event()`, `batch_correlate()` |
| `varshaphal.py` | Solar return (annual chart) | `get_varshaphal_analysis()`, `get_current_varshaphal()`, `detect_tajika_yogas()` |
| `ashtottari_dasha.py` | Ashtottari dasha system | `calculate_ashtottari_sequence()`, `get_current_ashtottari()` |
| `yogini_dasha.py` | Yogini dasha system | `calculate_yogini_sequence()`, `get_current_yogini_dasha()` |
| `narayana_dasha.py` | Narayana (Jaimini) dasha | `calculate_narayana_sequence()`, `get_current_narayana_dasha()` |
| `progressions.py` | Secondary progressions | `get_current_progressions()`, `calculate_progressed_positions()` |

### 3.5 `packages/guide/` -- AI Agent

LangGraph-powered conversational agent with personality adaptation.

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `agent.py` | LangGraph agent definition | `Guide`, `AgentState`, `initialize_guide()`, `get_guide()`, `ConversationManager`, `IntentType` |
| `tools.py` | Agent tool definitions | Tools for chart lookup, dasha query, transit check, yoga detection, remedy suggestion, forecast fetch |

**Note:** Requires `ANTHROPIC_API_KEY` and `langgraph` to be installed. Falls back gracefully when not available.

### 3.6 `packages/memory/` -- Semantic Memory

User memory, conversation history, and vector similarity search.

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `store.py` | PostgreSQL + pgvector store | `MemoryStore`, `Memory`, `SearchResult` |
| `embeddings.py` | Embedding providers | `EmbeddingService`, `OpenAIEmbeddings`, `VoyageEmbeddings`, `LocalEmbeddings`, `MockEmbeddings` |
| `mem0_client.py` | Mem0 cloud client (deprecated) | `Mem0Client`, `MemoryCategory`, `MemoryImportance` |
| `unified_memory.py` | Unified memory abstraction | `UnifiedMemory`, `UnifiedMemoryClient`, `create_memory_client()` |

**Note:** Requires `asyncpg` for PostgreSQL support. Mem0 Cloud was removed in Session 17 in favor of local pgvector.

---

## 4. MCP Servers and Tools

Four MCP (Model Context Protocol) servers provide tools for Claude Desktop and the Guide agent. Located in `services/mcp/`.

### 4.1 `108-ephemeris` (8 tools) -- `ephemeris_server.py`

| Tool | Description |
|------|-------------|
| `planetary_positions` | Calculate sidereal positions of all 9 Vedic planets |
| `house_cusps` | Calculate house cusps and ascendant |
| `nakshatra_details` | Get nakshatra info from a longitude |
| `divisional_chart` | Calculate any divisional chart D1-D60 |
| `panchanga` | Get full panchanga (tithi, vara, nakshatra, yoga, karana) |
| `sunrise_sunset` | Get sunrise/sunset times for a date/location |
| `planetary_aspects` | Calculate aspects between planets |
| `upagraha_positions` | Calculate sub-planetary points (Gulika, Mandi, etc.) |

### 4.2 `108-patterns` (39 tools) -- `patterns_server.py`

| Tool | Description |
|------|-------------|
| `detect_yogas` | Detect all yogas in a birth chart |
| `detect_doshas` | Detect all doshas in a birth chart |
| `calculate_strength` | Calculate Shadbala planetary strengths |
| `ashtakavarga` | Calculate Bhinnashtakavarga and Sarvashtakavarga |
| `kundali_matching` | Ashta Kuta marriage compatibility |
| `combustion_check` | Check planetary combustion |
| `retrograde_effects` | Analyze retrograde planet effects |
| `chara_karakas` | Calculate Jaimini Chara Karakas |
| `jaimini_aspects` | Get Jaimini rashi aspects |
| `arudha_padas` | Calculate all 12 Arudha Padas |
| `chara_dasha` | Calculate Chara Dasha periods |
| `prashna_analysis` | Horary astrology analysis |
| `vimshopaka_strength` | Vimshopaka Bala for a planet |
| `all_vimshopaka` | Vimshopaka Bala for all planets |
| `bhava_bala` | Bhava Bala for a house |
| `all_bhava_balas` | Bhava Bala for all 12 houses |
| `upapada_analysis` | Upapada Lagna interpretation |
| `check_yoga_cancellations` | Check if yogas are cancelled |
| `detect_neecha_bhanga_yoga` | 5-condition Neecha Bhanga detection |
| `detect_planetary_wars_tool` | Detect planetary wars |
| `bhava_chalit_chart` | Bhava Chalit chart calculation |
| `recommend_chart_remedies` | Personalized remedy recommendations |
| `navamsha_spouse_analysis` | D9-based spouse analysis |
| `synastry_analysis` | Synastry between two charts |
| `gem_recommendation` | Gemstone prescriptions |
| `atmakaraka_analysis` | Atmakaraka deep analysis |
| `check_gem_compatibility_tool` | Check gem compatibility/conflicts |
| `kp_sublord` | KP sublord lookup |
| `kp_cuspal_sublords` | KP cuspal sublords |
| `kp_significators` | KP significators |
| `kp_prediction` | KP-based prediction |
| *(+ additional helper/category tools)* | |

### 4.3 `108-context` (27 tools) -- `context_server.py`

| Tool | Description |
|------|-------------|
| `current_dasha` | Get current Vimshottari dasha/antardasha/pratyantardasha |
| `dasha_periods` | Get full Mahadasha sequence |
| `transit_analysis` | Analyze current transits against natal Moon |
| `sade_sati_status` | Check Sade Sati status and phase |
| `dhaiya_status` | Check Dhaiya (small panoti) |
| `muhurta_check` | Check muhurta quality for an activity |
| `find_good_muhurta` | Find next auspicious time |
| `antardasha_periods` | Get Antardasha sequence within a Mahadasha |
| `antardasha_effects` | Get interpretation of MD/AD combination |
| `pratyantardasha_effects` | Get Pratyantardasha effects |
| `enriched_transit` | Enriched transit analysis with effects |
| `yogini_dasha` | Calculate Yogini Dasha periods |
| `narayana_dasha` | Calculate Narayana (Jaimini) Dasha |
| `compare_dashas` | Compare multiple dasha systems side-by-side |
| `abhijit_muhurta` | Get Abhijit muhurta window |
| `brahma_muhurta` | Get Brahma muhurta window |
| `eclipse_periods` | Get eclipse dates for a month |
| `marana_kaal` | Get Marana Kaal timing |
| `ashtottari_dasha` | Calculate Ashtottari Dasha |
| `secondary_progressions` | Calculate secondary progressions |
| `dasha_transit_cross_analysis` | Dasha-Transit cross-analysis |
| `transit_natal_aspects_tool` | Transit-to-natal aspects |
| `correlate_life_event` | Correlate a life event with chart |
| `upcoming_transit_triggers` | Find upcoming transit triggers |
| `daily_forecast` | Generate daily forecast |
| `weekly_forecast` | Generate weekly forecast |
| `monthly_forecast` | Generate monthly forecast |

### 4.4 `108-knowledge` (15 tools) -- `knowledge_server.py`

| Tool | Description |
|------|-------------|
| `lookup_planet` | Get planet details from knowledge base |
| `lookup_rashi` | Get rashi/sign details |
| `lookup_nakshatra` | Get nakshatra details |
| `lookup_house` | Get house significations |
| `lookup_yoga` | Get yoga definition and effects |
| `lookup_dosha` | Get dosha details and remedies |
| `lookup_antardasha_effects` | Get MD/AD combination interpretation |
| `lookup_pratyantardasha_effects` | Get MD/AD/PD combination interpretation |
| `search_knowledge` | Full-text search across knowledge base |
| `list_all` | List all items in a category |
| `lookup_tithi` | Get tithi details |
| `lookup_karana` | Get karana details |
| `lookup_vara` | Get weekday (vara) details |
| `lookup_avastha` | Get planetary avastha |
| `lookup_nitya_yoga` | Get nitya yoga details |

**Total MCP tools: ~89**

---

## 5. Mobile to Gateway Wiring

### 5.1 API Constants (`mobile/lib/core/constants/api_constants.dart`)

The mobile app defines these endpoint paths, all targeting `http://localhost:8001`:

| Constant | Path | Method | Used By |
|----------|------|--------|---------|
| `authSignupPhone` | `/auth/signup-phone` | -- | Not used (Supabase handles auth directly) |
| `authVerifyOtp` | `/auth/verify-otp` | -- | Not used (Supabase handles auth directly) |
| `authLoginGoogle` | `/auth/login-google` | -- | Not used |
| `authLoginApple` | `/auth/login-apple` | -- | Not used |
| `userMe` | `/api/v1/me` | GET/PUT | `ProfileScreen`, `UserProvider` |
| `userBirthDetails` | `/api/v1/me/birth-details` | PUT | `BirthDetailsScreen`, `UserProvider` |
| `config` | `/api/v1/config` | GET | `ConfigProvider` |
| `chartSummary` | `/api/v1/chart/summary` | GET | `HomeScreen`, `ChartProvider` |
| `chartFull` | `/api/v1/chart/full` | GET | `ChartProvider` |
| `chartDivisional(d)` | `/api/v1/chart/divisional/{d}` | GET | `ChartProvider` |
| `forecastDaily` | `/api/v1/forecast/daily` | GET | `HomeScreen`, `ForecastProvider` |
| `forecastWeekly` | `/api/v1/forecast/weekly` | GET | `ForecastProvider` |
| `forecastMonthly` | `/api/v1/forecast/monthly` | GET | `ForecastProvider` |
| `forecastYearly` | `/api/v1/forecast/yearly` | GET | `ForecastProvider` |
| `analysisYogas` | `/api/v1/analysis/yogas` | GET | -- (defined but not used in screens yet) |
| `analysisDoshas` | `/api/v1/analysis/doshas` | GET | -- (defined but not used in screens yet) |
| `analysisDasha` | `/api/v1/analysis/dasha` | GET | -- (defined but not used in screens yet) |
| `analysisTransits` | `/api/v1/analysis/transits` | GET | -- (defined but not used in screens yet) |
| `analysisKp` | `/api/v1/analysis/kp` | GET | -- (defined but not used in screens yet) |
| `chat` | `/api/v1/chat` | POST | `ChatProvider` |
| `chatHistory` | `/api/v1/chat/history` | GET | `ChatProvider` |
| `chatRemaining` | `/api/v1/chat/remaining` | GET | `ChatProvider` |
| `compatibilityQuick` | `/api/v1/compatibility/quick` | POST | -- (defined but screen is a stub) |
| `compatibilityFull` | `/api/v1/compatibility/full` | POST | -- (defined but screen is a stub) |
| `muhurtaCheck` | `/api/v1/muhurta/check` | POST | -- (defined but screen uses hardcoded data) |
| `muhurtaFind` | `/api/v1/muhurta/find` | POST | -- (defined but screen uses hardcoded data) |
| `reports` | `/api/v1/reports` | GET/POST | `ReportsProvider` |
| `reportDetail(id)` | `/api/v1/reports/{id}` | GET | `ReportsProvider` |
| `reportPdf(id)` | `/api/v1/reports/{id}/pdf` | GET | `ReportsProvider` |
| `events` | `/api/v1/events` | GET/POST | `EventsProvider` |
| `eventDetail(id)` | `/api/v1/events/{id}` | GET/PUT/DELETE | `EventsProvider` |
| `eventsCorrelate` | `/api/v1/events/correlate` | POST | `EventsProvider` |
| `creditsBalance` | `/api/v1/credits/balance` | GET | `CreditsProvider` |
| `creditsHistory` | `/api/v1/credits/history` | GET | `CreditsProvider` |
| `remedies` | `/api/v1/remedies` | GET | -- (defined but screen uses hardcoded data) |
| `remediesGems` | `/api/v1/remedies/gems` | GET | -- (defined but screen uses hardcoded data) |
| `webhooksRevenuecat` | `/webhooks/revenuecat` | POST | -- (webhook endpoint) |

### 5.2 Endpoint Mismatch Analysis

The mobile app defines endpoints using **GET** (via `ApiService().get()`) but the gateway defines most endpoints as **POST** (requiring a `BirthDataRequest` body). This is the main architectural gap:

| Mobile Expects | Gateway Provides | Status |
|---------------|-----------------|--------|
| `GET /api/v1/chart/summary` | `POST /api/v1/chart` | **MISMATCH** -- Gateway needs a `GET` endpoint that reads birth data from the authenticated user's stored profile |
| `GET /api/v1/chart/full` | `POST /api/v1/chart` | **MISMATCH** -- same as above |
| `GET /api/v1/forecast/daily` | `POST /api/v1/forecast/daily` | **MISMATCH** -- Gateway needs to accept GET with user context |
| `GET /api/v1/forecast/weekly` | `POST /api/v1/forecast/weekly` | **MISMATCH** |
| `GET /api/v1/forecast/monthly` | `POST /api/v1/forecast/monthly` | **MISMATCH** |
| `GET /api/v1/forecast/yearly` | *(not implemented)* | **MISSING** |
| `PUT /api/v1/me` | *(not implemented)* | **MISSING** -- needs user profile CRUD |
| `PUT /api/v1/me/birth-details` | *(not implemented)* | **MISSING** -- needs birth details update |
| `GET /api/v1/config` | *(not implemented)* | **MISSING** -- app config endpoint |
| `POST /api/v1/chat` | `POST /api/v1/chat` | **MATCH** (but requires ANTHROPIC_API_KEY) |
| `GET /api/v1/chat/remaining` | *(not implemented)* | **MISSING** -- rate limit tracking |
| `GET /api/v1/chat/history` | *(not implemented)* | **MISSING** -- conversation history |
| `GET /api/v1/credits/balance` | *(not implemented)* | **MISSING** -- credits system |
| `GET /api/v1/credits/history` | *(not implemented)* | **MISSING** -- credits system |
| `GET /api/v1/reports` | *(not implemented)* | **MISSING** -- report generation |
| `GET /api/v1/events` | *(not implemented)* | **MISSING** -- event CRUD |
| `POST /api/v1/compatibility/*` | *(not implemented)* | **MISSING** -- compatibility endpoints |
| `POST /api/v1/muhurta/*` | `POST /api/v1/timing/muhurta` | **PATH MISMATCH** -- different URL paths |
| `GET /api/v1/remedies` | `POST /api/v1/analysis/remedies` | **PATH MISMATCH** |

### 5.3 Services

| Service | File | Purpose | Status |
|---------|------|---------|--------|
| `ApiService` | `mobile/lib/data/services/api_service.dart` | HTTP client with Bearer token auth | **REAL** -- generic GET/POST/PUT/DELETE with Supabase token injection |
| `SupabaseService` | `mobile/lib/data/services/supabase_service.dart` | Supabase auth wrapper | **REAL** -- phone OTP, Google/Apple OAuth, session management |
| `NotificationService` | `mobile/lib/data/services/notification_service.dart` | Push notifications | Placeholder |

### 5.4 Riverpod Providers (Data Layer)

| Provider | File | API Calls | Status |
|----------|------|-----------|--------|
| `authStateProvider` | `auth_provider.dart` | `SupabaseService().authStateChanges` | **WIRED** to Supabase |
| `userProfileProvider` | `user_provider.dart` | `GET /api/v1/me` | **WIRED** to gateway (endpoint not yet built) |
| `birthChartProvider` | `chart_provider.dart` | `GET /api/v1/chart/full` | **WIRED** to gateway (endpoint not yet built) |
| `chartSummaryProvider` | `chart_provider.dart` | `GET /api/v1/chart/summary` | **WIRED** to gateway (endpoint not yet built) |
| `dailyForecastProvider` | `forecast_provider.dart` | `GET /api/v1/forecast/daily` | **WIRED** to gateway (endpoint not yet built) |
| `weeklyForecastProvider` | `forecast_provider.dart` | `GET /api/v1/forecast/weekly` | **WIRED** to gateway (endpoint not yet built) |
| `monthlyForecastProvider` | `forecast_provider.dart` | `GET /api/v1/forecast/monthly` | **WIRED** to gateway (endpoint not yet built) |
| `chatMessagesProvider` | `chat_provider.dart` | `POST /api/v1/chat` | **WIRED** (but ChatScreen does not use this provider yet) |
| `remainingMessagesProvider` | `chat_provider.dart` | `GET /api/v1/chat/remaining` | **WIRED** (but ChatScreen does not use this provider yet) |
| `eventsForDateRangeProvider` | `events_provider.dart` | `GET /api/v1/events` | **WIRED** (but CalendarScreen does not use this provider yet) |
| `creditBalanceProvider` | `credits_provider.dart` | `GET /api/v1/credits/balance` | **WIRED** (but screens show hardcoded "45 credits") |
| `availableReportsProvider` | `reports_provider.dart` | `GET /api/v1/reports` | **WIRED** (but ReportsStoreScreen uses hardcoded data) |
| `entitlementProvider` | `entitlement_provider.dart` | RevenueCat SDK | **WIRED** to RevenueCat (placeholder API key) |

---

## 6. Connected vs Mockup Status

### Summary Table

| Screen | Auth | API Providers | Screen Uses Providers | End-to-End Status |
|--------|------|---------------|----------------------|-------------------|
| Phone Auth | Supabase | -- | Yes | **CONNECTED** |
| OTP Verify | Supabase | -- | Yes | **CONNECTED** |
| Profile | -- | `userProfileProvider` | Yes (direct ApiService call) | **CONNECTED** (if gateway has `/api/v1/me`) |
| Birth Details | -- | `updateBirthDetails` | Yes (direct ApiService call) | **CONNECTED** (if gateway has `/api/v1/me/birth-details`) |
| Home | -- | `dailyForecastDataProvider`, `chartSummaryDataProvider` | Yes (inline FutureProvider) | **PARTIALLY CONNECTED** -- calls real APIs but falls back to hardcoded defaults on error |
| Chart | -- | -- | No | **MOCKUP** -- hardcoded planet data |
| Chat | -- | -- | No | **MOCKUP** -- simulated delay, hardcoded response |
| Calendar | -- | -- | No | **MOCKUP** -- hardcoded events |
| Settings | -- | -- | No | **MOCKUP** -- hardcoded profile/credits |
| Timeline | -- | -- | No | **MOCKUP** -- hardcoded dasha periods |
| Muhurta | -- | -- | No | **MOCKUP** -- hardcoded results |
| Remedies | -- | -- | No | **MOCKUP** -- hardcoded remedies |
| Compatibility | -- | -- | No | **STUB** -- empty placeholder |
| Reports Store | -- | -- | No | **MOCKUP** -- hardcoded report list |
| Report View | -- | -- | No | **STUB** -- empty placeholder |
| Paywall | -- | -- | No | **MOCKUP** -- hardcoded tiers |
| Credit Store | -- | -- | No | **MOCKUP** -- hardcoded packs |

### What Needs to Happen for Full Connection

1. **Gateway user-aware endpoints**: The gateway needs endpoints that accept GET requests and look up the authenticated user's birth data from the database (instead of requiring `BirthDataRequest` in POST body every time). Specifically:
   - `GET /api/v1/me` -- return user profile
   - `PUT /api/v1/me` -- update user profile
   - `PUT /api/v1/me/birth-details` -- save birth data
   - `GET /api/v1/chart/summary` -- return chart summary for authenticated user
   - `GET /api/v1/chart/full` -- return full chart for authenticated user
   - `GET /api/v1/forecast/daily` -- daily forecast for authenticated user
   - `GET /api/v1/forecast/weekly` -- weekly forecast
   - `GET /api/v1/forecast/monthly` -- monthly forecast
   - `GET /api/v1/forecast/yearly` -- yearly forecast (not yet in gateway)

2. **Wire screens to providers**: The following screens have providers ready but do not use them:
   - `ChartScreen` -- should use `birthChartProvider` / `chartSummaryProvider`
   - `ChatScreen` -- should use `chatMessagesProvider` / `sendChatMessageProvider`
   - `CalendarScreen` -- should use `eventsForDateRangeProvider`
   - `SettingsScreen` -- should use `userProfileProvider` / `creditBalanceProvider`
   - `TimelineScreen` -- needs a dasha provider calling `/api/v1/analysis/dasha`
   - `MuhurtaScreen` -- needs to call `/api/v1/muhurta/check`
   - `RemediesScreen` -- needs to call `/api/v1/remedies`

3. **Missing gateway endpoints**: Credits, reports, events, chat history, config, compatibility -- these all need to be added to the gateway.

4. **Auth middleware**: The gateway needs JWT verification middleware that validates the Supabase access token and extracts the user ID.

---

## 7. Database Schema

Location: `database/schema.sql`

PostgreSQL with `pgvector` extension for semantic search.

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | User accounts | `id` (UUID), `email`, `name`, `created_at` |
| `birth_charts` | Birth chart data (1 per user) | `user_id`, `birth_datetime`, `latitude`, `longitude`, `timezone`, `lagna_rashi`, `moon_rashi`, `moon_nakshatra`, `planets` (JSONB), `houses` (JSONB) |
| `detected_patterns` | Detected yogas and doshas | `user_id`, `pattern_type` (yoga/dosha), `pattern_name`, `strength`, `severity`, `involved_planets`, `details` (JSONB) |
| `memories` | Semantic memories with embeddings | `user_id`, `content`, `category`, `embedding` (vector 1536), `importance`, `metadata` (JSONB) |
| `predictions` | System predictions for validation | `user_id`, `prediction_text`, `category`, `timeframe_start/end`, `confidence`, `factors` (JSONB), `outcome`, `accuracy` |
| `conversations` | Chat history with embeddings | `user_id`, `session_id`, `messages` (JSONB), `summary`, `topics`, `embedding` (vector 1536) |
| `user_preferences` | User settings | `user_id`, `preference_key`, `preference_value` (JSONB) |
| `dasha_timeline` | Precomputed dasha periods | `user_id`, `level` (maha/antar/pratyantar), `lord`, `start_date`, `end_date`, `parent_id` |

### Views

| View | Description |
|------|-------------|
| `user_complete_profile` | Joins users + birth_charts + aggregated counts of patterns, memories, predictions, conversations |

### Key Indexes

- `memories.embedding` -- IVFFlat cosine similarity index (pgvector)
- `conversations.embedding` -- IVFFlat cosine similarity index
- `dasha_timeline(user_id, start_date, end_date)` -- for efficient current dasha lookup
- `predictions(user_id, timeframe_start, timeframe_end)` -- for validation queries

---

## 8. Data Flow Architecture

```
+-------------------+     +------------------+     +-------------------+
|   Mobile App      |     |  Gateway API     |     |  Backend Packages |
|   (Flutter)       |     |  (FastAPI)       |     |  (Python)         |
+-------------------+     +------------------+     +-------------------+
|                   |     |                  |     |                   |
| Supabase Auth ----+---->| JWT Middleware   |     |  packages/core    |
|                   |     |  (TODO)          |     |   - models        |
| ApiService -------+---->| /api/v1/*        +---->|   - knowledge     |
|  GET/POST/PUT     |     |  48 endpoints    |     |                   |
|                   |     |                  |     |  packages/cosmos  |
| Providers --------+     | Database (PG)    |     |   - ephemeris     |
|  chart_provider   |     |  - users         |     |   - nakshatras    |
|  forecast_provider|     |  - birth_charts  |     |   - divisional    |
|  chat_provider    |     |  - memories      |     |                   |
|  events_provider  |     |  - predictions   |     |  packages/self    |
|  credits_provider |     |  - conversations |     |   - yoga_detector |
|  reports_provider |     |                  |     |   - dosha_detector|
|  auth_provider    |     +------------------+     |   - synastry      |
|                   |              |                |   - gem_recommender|
+-------------------+              |                |                   |
                                   |                |  packages/context |
+-------------------+              |                |   - dasha         |
|   MCP Servers     |              |                |   - transits      |
|   (Claude Desktop)|              |                |   - muhurta       |
+-------------------+              |                |   - daily_forecast|
|                   |              |                |                   |
| ephemeris (8)     |              |                |  packages/guide   |
| patterns  (39)    +--------------+                |   - LangGraph     |
| context   (27)    |  (same packages)              |                   |
| knowledge (15)    |                               |  packages/memory  |
|                   |                               |   - pgvector      |
+-------------------+                               +-------------------+
```

### Flow: Mobile User Opens Home Screen

1. Mobile app starts, checks Supabase auth state
2. If authenticated, GoRouter navigates to `/home`
3. `HomeScreen` watches `dailyForecastDataProvider` and `chartSummaryDataProvider`
4. Providers call `ApiService().get('/api/v1/forecast/daily')` with Bearer token
5. Gateway receives request, validates JWT, looks up user's birth chart in DB
6. Gateway calls `packages/context/src/daily_forecast.py::get_daily_forecast()`
7. Which internally calls `packages/cosmos/` for positions, `packages/context/` for dasha/transits
8. Response flows back: Gateway -> ApiService -> Provider -> HomeScreen widget

**Current gap:** Step 5 is not yet built -- the gateway does not have user-aware GET endpoints that look up stored birth data. The mobile app's providers are wired and ready, but the gateway endpoints they call do not exist yet.

---

## Appendix: File Counts

| Area | Count |
|------|-------|
| Mobile screen files | 17 (13 screens + 4 stubs/placeholders) |
| Mobile widget files | 13 |
| Mobile provider files | 10 |
| Mobile model files | 7 |
| Mobile service files | 3 |
| Gateway API endpoints | ~48 |
| MCP tools | ~89 |
| Backend package modules | ~30 |
| Database tables | 7 |
| Knowledge rule files | 43 |
| Knowledge definition files | 15 |
| Knowledge interpretation files | 5 |
| Total tests passing | 2,026 |
