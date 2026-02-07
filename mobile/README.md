# 108 Flutter Mobile App - Core & Data Layer

Complete implementation of the Flutter core layer and data layer for the 108 Personal Life Operating System, powered by Vedic Astrology.

## Project Status

✅ **Phase 1: Core & Data Layer - COMPLETE**

All 28 core and data layer files created and ready for code generation and feature implementation.

## Quick Start

### 1. Setup

```bash
cd /sessions/sharp-nifty-goldberg/mnt/108-core/mobile

# Install dependencies
flutter pub get

# Generate code (Freezed models + Riverpod providers + Router)
flutter pub run build_runner build --delete-conflicting-outputs
```

### 2. Configuration

Create environment files before running:

```bash
# .env.dev
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<your-anon-key>
REVENUECAT_API_KEY_IOS=<your-ios-key>
REVENUECAT_API_KEY_ANDROID=<your-android-key>
GOOGLE_PLACES_API_KEY=<your-api-key>
```

### 3. Run

```bash
flutter run
```

## Project Structure

```
lib/
├── core/              # Reusable layer (theme, routing, utils)
│   ├── theme/         # Colors, typography, app theme
│   ├── router/        # GoRouter configuration
│   ├── constants/     # API endpoints and configuration
│   └── utils/         # Date and format utilities
│
├── data/              # Data layer (services, models, state)
│   ├── services/      # API, Supabase, FCM clients
│   ├── models/        # Data models (Freezed)
│   └── providers/     # State management (Riverpod)
│
├── features/          # Feature modules (screens & widgets)
└── shared/            # Shared widgets & animations
```

## Key Technologies

| Technology | Purpose | Version |
|-----------|---------|---------|
| Flutter | Mobile Framework | 3.24.0+ |
| Dart | Language | 3.5.0+ |
| Riverpod | State Management | 2.5.0 |
| Freezed | Immutable Models | 2.5.0 |
| GoRouter | Navigation | 14.0.0 |
| Supabase | Auth & Database | 2.5.0 |
| RevenueCat | Billing | 7.0.0 |
| Firebase | Push Notifications | 15.0.0 |

## File Manifest

### Core Layer (7 files)
- `lib/core/theme/colors.dart` - Cosmic color palette
- `lib/core/theme/text_styles.dart` - Typography scale
- `lib/core/theme/app_theme.dart` - Material3 dark theme
- `lib/core/router/app_router.dart` - Navigation routes
- `lib/core/constants/api_constants.dart` - API configuration
- `lib/core/utils/date_utils.dart` - Date formatting
- `lib/core/utils/format_utils.dart` - String/number formatting

### Data Layer - Services (3 files)
- `lib/data/services/api_service.dart` - HTTP client wrapper
- `lib/data/services/supabase_service.dart` - Supabase wrapper
- `lib/data/services/notification_service.dart` - FCM setup

### Data Layer - Models (7 files)
- `lib/data/models/user_model.dart` - User profile
- `lib/data/models/birth_chart_model.dart` - Birth chart
- `lib/data/models/chat_message_model.dart` - Chat messages
- `lib/data/models/forecast_model.dart` - Forecasts
- `lib/data/models/event_model.dart` - Calendar events
- `lib/data/models/report_model.dart` - Generated reports
- `lib/data/models/config_model.dart` - App configuration

### Data Layer - Providers (10 files)
- `lib/data/providers/auth_provider.dart` - Authentication
- `lib/data/providers/user_provider.dart` - User data
- `lib/data/providers/config_provider.dart` - Configuration
- `lib/data/providers/entitlement_provider.dart` - Billing
- `lib/data/providers/chat_provider.dart` - Chat state
- `lib/data/providers/chart_provider.dart` - Chart data
- `lib/data/providers/forecast_provider.dart` - Forecasts
- `lib/data/providers/events_provider.dart` - Events
- `lib/data/providers/credits_provider.dart` - Credits
- `lib/data/providers/reports_provider.dart` - Reports

### Configuration
- `pubspec.yaml` - Project manifest

### Documentation
- `FLUTTER_CORE_SETUP.md` - Detailed feature overview
- `BUILD_COMMANDS.md` - Build and generation guide
- `DIRECTORY_STRUCTURE.md` - Complete project layout
- `IMPLEMENTATION_SUMMARY.md` - Status and checklist

## Architecture Highlights

### Authentication
- Phone OTP via Supabase
- Social login (Google, Apple)
- JWT token management
- Session persistence

### State Management
- Type-safe Riverpod providers
- Freezed immutable models
- Proper cache invalidation
- Real-time streams for auth

### API Integration
- HTTP client with automatic auth
- Feature gating support
- Rate limiting detection
- Error handling

### Monetization
- RevenueCat subscriptions
- Credit system
- In-app purchases
- Tier-based feature access

### Design System
- Dark cosmic theme
- Glassmorphic elements
- SpaceGrotesk typography
- Consistent color palette

## Next Steps

### Phase 2: Feature Implementation (4-6 weeks)
1. Create entry points (main.dart, app.dart)
2. Implement auth screens
3. Implement onboarding flow
4. Create main feature screens
5. Add shared widgets and animations
6. Integration testing

### Phase 3: Testing & Polish
1. Unit tests for services
2. Widget tests for screens
3. Integration tests
4. Performance optimization
5. App Store/Play Store assets

### Phase 4: Launch Preparation
1. TestFlight internal testing
2. Google Play internal testing
3. App Store/Play Store submission
4. Launch coordination

## References

- **Architecture**: See `/docs/architecture/MOBILE_ARCHITECTURE.md`
- **Build Guide**: See `BUILD_COMMANDS.md` in this directory
- **Directory Layout**: See `DIRECTORY_STRUCTURE.md` in this directory
- **Status Report**: See `IMPLEMENTATION_SUMMARY.md` in this directory

## Code Generation

After adding new models or providers, regenerate:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Or use watch mode during development:

```bash
flutter pub run build_runner watch
```

## Styling & Linting

```bash
# Format code
dart format .

# Run analyzer
flutter analyze

# Fix issues
dart fix --apply
```

## Testing

```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage
```

## Troubleshooting

### Missing generated code?
```bash
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### Can't find package?
```bash
flutter pub get
flutter pub upgrade
```

### Router not working?
Make sure you have the `go_router` package and proper GoRouter configuration.

## Architecture Principles

✅ Clean separation of concerns (Core → Data → Features)
✅ Type-safe with Dart 3.5 and Freezed
✅ Riverpod for compile-time checked state
✅ Modular feature structure
✅ Testable with dependency injection
✅ Performance-oriented with caching
✅ Error handling throughout

## File Sizes (Approximate)

| Category | Count | Size |
|----------|-------|------|
| Core Layer | 7 | 25 KB |
| Data Services | 3 | 18 KB |
| Data Models | 7 | 12 KB |
| Data Providers | 10 | 35 KB |
| Configuration | 1 | 2 KB |
| Documentation | 4 | 45 KB |
| **TOTAL** | **32** | **137 KB** |

## Credits

Built following the architectural principles in `MOBILE_ARCHITECTURE.md` (v1.0).

Implements the 108 core engine with:
- Vedic astrology calculations
- Personalized AI guidance
- Real-time insights
- Subscription tiers

## License

Proprietary - 108 Inc.

---

**Last Updated**: 2026-02-07
**Status**: Ready for Phase 2 (Feature Implementation)
**Maintainer**: Development Team

For questions, refer to the documentation files or the main architecture document.
