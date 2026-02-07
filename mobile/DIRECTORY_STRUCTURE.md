# Flutter Mobile App - Directory Structure

## Complete Project Layout

```
mobile/
├── pubspec.yaml                          # Project manifest with dependencies
├── pubspec.lock                          # Locked dependency versions
│
├── lib/
│   ├── core/                             # Core layer (reusable utilities & configs)
│   │   ├── theme/
│   │   │   ├── app_theme.dart            # Dark theme with glassmorphic design
│   │   │   ├── colors.dart               # CosmicColors palette (✅ CREATED)
│   │   │   └── text_styles.dart          # CosmicTextStyles typography (✅ CREATED)
│   │   │
│   │   ├── router/
│   │   │   └── app_router.dart           # GoRouter config with auth guards (✅ CREATED)
│   │   │
│   │   ├── constants/
│   │   │   └── api_constants.dart        # API endpoints & configuration (✅ CREATED)
│   │   │
│   │   └── utils/
│   │       ├── date_utils.dart           # Date/time formatting (✅ CREATED)
│   │       └── format_utils.dart         # String/number formatting (✅ CREATED)
│   │
│   ├── data/                             # Data layer (services, models, providers)
│   │   ├── services/
│   │   │   ├── api_service.dart          # HTTP client wrapper with auth (✅ CREATED)
│   │   │   ├── supabase_service.dart     # Supabase auth & client wrapper (✅ CREATED)
│   │   │   └── notification_service.dart # FCM setup & push notifications (✅ CREATED)
│   │   │
│   │   ├── models/
│   │   │   ├── user_model.dart           # User profile model (✅ CREATED - Freezed)
│   │   │   ├── birth_chart_model.dart    # Birth chart & planet positions (✅ CREATED - Freezed)
│   │   │   ├── chat_message_model.dart   # Chat messages with render blocks (✅ CREATED - Freezed)
│   │   │   ├── forecast_model.dart       # Daily/weekly/monthly forecasts (✅ CREATED - Freezed)
│   │   │   ├── event_model.dart          # Calendar events model (✅ CREATED - Freezed)
│   │   │   ├── report_model.dart         # Generated reports model (✅ CREATED - Freezed)
│   │   │   └── config_model.dart         # App configuration model (✅ CREATED - Freezed)
│   │   │
│   │   └── providers/
│   │       ├── auth_provider.dart        # Supabase auth state (✅ CREATED - Riverpod)
│   │       ├── user_provider.dart        # User profile fetching (✅ CREATED - Riverpod)
│   │       ├── config_provider.dart      # Remote config & feature gates (✅ CREATED - Riverpod)
│   │       ├── entitlement_provider.dart # RevenueCat billing (✅ CREATED - Riverpod)
│   │       ├── chat_provider.dart        # Chat messages & rate limiting (✅ CREATED - Riverpod)
│   │       ├── chart_provider.dart       # Birth chart data (✅ CREATED - Riverpod)
│   │       ├── forecast_provider.dart    # Forecast fetching (✅ CREATED - Riverpod)
│   │       ├── events_provider.dart      # User events CRUD (✅ CREATED - Riverpod)
│   │       ├── credits_provider.dart     # Credit wallet & transactions (✅ CREATED - Riverpod)
│   │       └── reports_provider.dart     # Reports generation & management (✅ CREATED - Riverpod)
│   │
│   ├── features/                         # Feature modules (screens & widgets)
│   │   ├── auth/
│   │   │   ├── screens/
│   │   │   │   ├── phone_auth_screen.dart
│   │   │   │   └── otp_verify_screen.dart
│   │   │   └── widgets/
│   │   │       └── social_login_buttons.dart
│   │   │
│   │   ├── onboarding/
│   │   │   ├── screens/
│   │   │   │   ├── profile_screen.dart
│   │   │   │   └── birth_details_screen.dart
│   │   │   └── widgets/
│   │   │       ├── place_search_field.dart
│   │   │       └── time_picker_field.dart
│   │   │
│   │   ├── home/
│   │   │   ├── screens/
│   │   │   │   └── home_screen.dart
│   │   │   └── widgets/
│   │   │       ├── today_score_card.dart
│   │   │       ├── quick_cards_row.dart
│   │   │       ├── forecast_tabs.dart
│   │   │       └── area_rating_bars.dart
│   │   │
│   │   ├── chart/
│   │   │   ├── screens/
│   │   │   │   └── chart_screen.dart
│   │   │   └── widgets/
│   │   │       ├── south_indian_chart.dart
│   │   │       ├── planet_list.dart
│   │   │       ├── divisional_tabs.dart
│   │   │       └── planet_detail_sheet.dart
│   │   │
│   │   ├── chat/
│   │   │   ├── screens/
│   │   │   │   └── chat_screen.dart
│   │   │   └── widgets/
│   │   │       ├── chat_bubble.dart
│   │   │       ├── chat_table.dart
│   │   │       ├── chat_score_card.dart
│   │   │       ├── chat_action_card.dart
│   │   │       ├── chat_input_bar.dart
│   │   │       └── remaining_counter.dart
│   │   │
│   │   ├── calendar/
│   │   │   ├── screens/
│   │   │   │   └── calendar_screen.dart
│   │   │   └── widgets/
│   │   │       ├── cosmic_calendar.dart
│   │   │       ├── day_detail_view.dart
│   │   │       └── add_event_sheet.dart
│   │   │
│   │   ├── timeline/
│   │   │   ├── screens/
│   │   │   │   └── timeline_screen.dart
│   │   │   └── widgets/
│   │   │       ├── dasha_chapter_card.dart
│   │   │       ├── nested_rings.dart
│   │   │       ├── transit_alert_banner.dart
│   │   │       └── event_pin.dart
│   │   │
│   │   ├── reports/
│   │   │   ├── screens/
│   │   │   │   ├── reports_store_screen.dart
│   │   │   │   └── report_view_screen.dart
│   │   │   └── widgets/
│   │   │       ├── report_card.dart
│   │   │       └── generating_animation.dart
│   │   │
│   │   ├── compatibility/
│   │   │   ├── screens/
│   │   │   │   └── compatibility_screen.dart
│   │   │   └── widgets/
│   │   │       ├── partner_input_form.dart
│   │   │       ├── kuta_score_ring.dart
│   │   │       └── kuta_breakdown.dart
│   │   │
│   │   ├── muhurta/
│   │   │   ├── screens/
│   │   │   │   └── muhurta_screen.dart
│   │   │   └── widgets/
│   │   │       ├── activity_picker.dart
│   │   │       ├── muhurta_calendar.dart
│   │   │       └── date_detail_sheet.dart
│   │   │
│   │   ├── remedies/
│   │   │   ├── screens/
│   │   │   │   └── remedies_screen.dart
│   │   │   └── widgets/
│   │   │       ├── remedy_card.dart
│   │   │       └── gem_card.dart
│   │   │
│   │   ├── settings/
│   │   │   ├── screens/
│   │   │   │   ├── settings_screen.dart
│   │   │   │   ├── subscription_screen.dart
│   │   │   │   └── notification_screen.dart
│   │   │   └── widgets/
│   │   │       └── birth_details_editor.dart
│   │   │
│   │   └── paywall/
│   │       ├── screens/
│   │       │   ├── paywall_screen.dart
│   │       │   └── credit_store_screen.dart
│   │       └── widgets/
│   │           ├── tier_comparison.dart
│   │           ├── locked_overlay.dart
│   │           └── credit_pack_card.dart
│   │
│   ├── shared/                           # Shared widgets & animations
│   │   ├── widgets/
│   │   │   ├── star_background.dart
│   │   │   ├── glass_card.dart
│   │   │   ├── cosmic_loader.dart
│   │   │   ├── planet_glyph.dart
│   │   │   ├── bottom_nav_bar.dart
│   │   │   └── locked_feature.dart
│   │   │
│   │   └── animations/
│   │       ├── star_field.dart
│   │       └── chart_calculation.dart
│   │
│   ├── gen/                              # Generated code (do not edit)
│   │   ├── *.freezed.dart
│   │   ├── *.g.dart
│   │   └── app_router.g.dart
│   │
│   ├── main.dart                         # App entry point (TODO)
│   └── app.dart                          # MaterialApp configuration (TODO)
│
├── test/                                 # Unit & widget tests
│   ├── data/
│   │   ├── services/
│   │   │   ├── api_service_test.dart
│   │   │   └── supabase_service_test.dart
│   │   ├── models/
│   │   │   └── user_model_test.dart
│   │   └── providers/
│   │       └── auth_provider_test.dart
│   └── features/
│       └── (feature tests)
│
├── assets/                               # Static assets
│   ├── images/
│   │   ├── logo.png
│   │   └── onboarding/
│   ├── animations/
│   │   └── (Lottie JSON files)
│   ├── icons/
│   │   └── (SVG/PNG icons)
│   └── fonts/
│       └── SpaceGrotesk-*.ttf
│
├── ios/                                  # iOS-specific configuration
│   ├── Podfile
│   ├── Runner.xcworkspace/
│   └── Runner/
│
├── android/                              # Android-specific configuration
│   ├── build.gradle
│   ├── app/
│   │   └── build.gradle
│   └── gradle.properties
│
├── web/                                  # Web-specific configuration (optional)
│   ├── index.html
│   └── manifest.json
│
├── .gitignore
├── .github/
│   └── workflows/                        # CI/CD workflows (GitHub Actions)
│       ├── flutter_test.yml
│       └── flutter_build.yml
│
├── analysis_options.yaml                 # Dart linter configuration
├── FLUTTER_CORE_SETUP.md                 # Documentation of created files (✅ CREATED)
├── BUILD_COMMANDS.md                     # Build & code generation guide (✅ CREATED)
└── DIRECTORY_STRUCTURE.md                # This file (✅ CREATED)
```

## File Count Summary

- **Core Layer**: 8 files (theme, router, constants, utils)
- **Data Layer**: 16 files (services, models, providers)
- **Feature Screens**: ~40 placeholder files (to be implemented)
- **Shared Widgets**: 8 files
- **Generated Code**: Auto-generated from Freezed & Riverpod

## Files Created in This Session (✅)

### Core Layer (8 files)
1. `lib/core/theme/colors.dart`
2. `lib/core/theme/text_styles.dart`
3. `lib/core/theme/app_theme.dart`
4. `lib/core/router/app_router.dart`
5. `lib/core/constants/api_constants.dart`
6. `lib/core/utils/date_utils.dart`
7. `lib/core/utils/format_utils.dart`

### Data Layer (16 files)
**Services (3):**
8. `lib/data/services/api_service.dart`
9. `lib/data/services/supabase_service.dart`
10. `lib/data/services/notification_service.dart`

**Models (7):**
11. `lib/data/models/user_model.dart`
12. `lib/data/models/birth_chart_model.dart`
13. `lib/data/models/chat_message_model.dart`
14. `lib/data/models/forecast_model.dart`
15. `lib/data/models/event_model.dart`
16. `lib/data/models/report_model.dart`
17. `lib/data/models/config_model.dart`

**Providers (10):**
18. `lib/data/providers/auth_provider.dart`
19. `lib/data/providers/user_provider.dart`
20. `lib/data/providers/config_provider.dart`
21. `lib/data/providers/entitlement_provider.dart`
22. `lib/data/providers/chat_provider.dart`
23. `lib/data/providers/chart_provider.dart`
24. `lib/data/providers/forecast_provider.dart`
25. `lib/data/providers/events_provider.dart`
26. `lib/data/providers/credits_provider.dart`
27. `lib/data/providers/reports_provider.dart`

### Configuration Files (3)
28. `pubspec.yaml`
29. `FLUTTER_CORE_SETUP.md`
30. `BUILD_COMMANDS.md`

## Next Steps to Complete

### 1. Generate Code
```bash
cd mobile
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### 2. Create Entry Points
- `lib/main.dart` - App initialization (Supabase, RevenueCat, Firebase)
- `lib/app.dart` - MaterialApp with theme and router

### 3. Implement Feature Screens
- Auth flows (phone OTP, Google/Apple)
- Onboarding (profile, birth details)
- Main screens (home, chart, chat, calendar, settings)
- Supplementary screens (reports, muhurta, compatibility, remedies)

### 4. Add Shared Widgets
- Star background animation
- Glass card component
- Cosmic loader
- Planet glyph icons
- Bottom navigation bar
- Locked feature overlay

### 5. Testing & QA
- Unit tests for services
- Widget tests for screens
- Integration tests for flows
- UI/UX testing on device

## Architecture Principles

✅ **Clean Separation of Concerns**
- Core: Reusable utilities, theme, configuration
- Data: Services, models, state management
- Features: UI screens and feature-specific widgets
- Shared: Reusable components across features

✅ **Type Safety**
- All models use Freezed for immutability
- Riverpod provides compile-time checked providers
- Strong typing throughout

✅ **Testability**
- Dependency injection via Riverpod
- Services are mockable
- Clear separation enables unit testing

✅ **Scalability**
- Modular feature structure
- Each feature is self-contained
- Easy to add new features without affecting existing code

✅ **Maintenance**
- Consistent naming and structure
- Clear responsibility for each layer
- Documentation for setup and build process
