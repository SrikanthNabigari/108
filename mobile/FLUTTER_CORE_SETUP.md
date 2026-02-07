# Flutter Core & Data Layer Files - Complete Setup

## Overview
Created all 28 core layer and data layer files for the 108 Vedic Astrology mobile app following the architecture documented in `MOBILE_ARCHITECTURE.md`.

## Files Created

### 1. Configuration & Dependencies
- **pubspec.yaml** - Project manifest with all dependencies (flutter_riverpod, supabase_flutter, purchases_flutter, firebase_messaging, etc.)

### 2. Core/Theme (Design System)
- **lib/core/theme/colors.dart** - CosmicColors class with complete cosmic palette
  - Deep space (#0a0a1a), Midnight (#1a1a2e), Nebula (#16213e)
  - Accents: Cosmic Purple, Stellar Blue, Solar Gold, Mars Red, Venus Green, Saturn Grey
  - Glass effects, Text colors, Status colors

- **lib/core/theme/text_styles.dart** - CosmicTextStyles typography scale
  - All styles use SpaceGrotesk font family
  - Heading1-3, Body1-2, Caption, Button, Overline, Accent, Metric

- **lib/core/theme/app_theme.dart** - Complete dark theme implementation
  - Material3 theme with glassmorphic elements
  - App bar (transparent, no elevation)
  - Card theme (16px rounded corners, translucent)
  - Input decoration (outlined, rounded)
  - Button themes (elevated, outlined, text)
  - Bottom nav (glassmorphic, dark)
  - Consistent accent colors throughout

### 3. Core/Router
- **lib/core/router/app_router.dart** - GoRouter with Riverpod integration
  - Auth guard: redirects to /auth if not authenticated
  - Routes: /auth, /auth/otp, /onboarding/profile, /onboarding/birth-details
  - Shell route with bottom nav for: /home, /chart, /chat, /calendar, /settings
  - Non-tab routes: /timeline, /reports, /reports/:id, /muhurta, /remedies, /compatibility, /paywall, /credit-store
  - Includes placeholder screen widgets for route generation

### 4. Core/Constants
- **lib/core/constants/api_constants.dart** - API configuration
  - BaseUrl, API version, all endpoint paths
  - Helper methods for headers and auth headers
  - Covers all gateway endpoints from architecture

### 5. Core/Utils
- **lib/core/utils/date_utils.dart** - Date/time utilities
  - formatDate, formatTime, formatDateTime, parseIso8601
  - timeAgo, getMonthYear, getWeekday
  - isToday, isTomorrow, startOfDay, endOfDay
  - formatDuration

- **lib/core/utils/format_utils.dart** - String/number formatting
  - formatScore (with color mapping 0-10)
  - formatCredits, formatPrice, truncateText
  - capitalizeFirst, snakeCaseToTitleCase, formatPercentage
  - formatArray, formatPlanetName, getSignEmoji
  - formatHouse (ordinal), getTrendIndicator

### 6. Data/Services
- **lib/data/services/api_service.dart** - HTTP client wrapper (singleton)
  - GET, POST, PUT, DELETE methods
  - Auto-attach Bearer token for authenticated requests
  - Error handling with custom ApiException
  - GatedResponse wrapper for feature gating
  - Rate limiting support (429 handling)

- **lib/data/services/supabase_service.dart** - Supabase client wrapper (singleton)
  - Initialize with URL + anonKey
  - Auth state stream, current user getter
  - Phone OTP: signInWithPhone, verifyOtp
  - Social: signInWithGoogle, signInWithApple
  - Sign out, getAccessToken
  - Update metadata, reset password, update password

- **lib/data/services/notification_service.dart** - FCM setup (singleton)
  - Initialize Firebase & FCM
  - Request permissions
  - Get FCM token
  - Listen for token refresh
  - Handle foreground & background messages
  - Show local notifications
  - Subscribe/unsubscribe from topics

### 7. Data/Models (All using Freezed)
- **lib/data/models/user_model.dart**
  - UserModel with: id, email, phone, name, gender, avatar, onboarding status
  - subscription tier, lagna/moon rashi/nakshatra, birth datetime, place, credit balance

- **lib/data/models/birth_chart_model.dart**
  - PlanetPosition: planet, longitude, sign, house, nakshatra, pada, degree, retrograde, latitude
  - BirthChartModel: ascendant, planets list, house cusps, moon data, ayanamsa

- **lib/data/models/chat_message_model.dart**
  - ChatBlock: type, content, data (for rendered content)
  - ChatMessageModel: id, role, content, content_type, metadata, blocks array, tokens_used, timestamp

- **lib/data/models/forecast_model.dart**
  - AreaRating: area, score (0-10), trend
  - PanchangaData: tithi, nakshatra, yoga, karana, vara
  - ForecastModel: type, date, day_rating, area_ratings map, recommendations, details, panchanga

- **lib/data/models/event_model.dart**
  - EventModel: id, title, event_date, event_time, event_type, category, description
  - muhurta_score, correlation_score, is_system_generated, metadata, timestamp

- **lib/data/models/report_model.dart**
  - ReportModel: id, report_type, title, content (JSONB), pdf_url, credits_charged, status, timestamp

- **lib/data/models/config_model.dart**
  - SubscriptionTier: id, name, price_monthly, price_yearly, features list
  - CreditPack: credits, price, label, badge
  - ReportPrice: report_type, credits, money, title
  - FeatureGates: feature availability by tier (free/pro/premium)
  - AppConfigModel: aggregates all config data

### 8. Data/Providers (All using Riverpod with code generation)

**Auth Providers:**
- **auth_provider.dart**
  - authStateProvider: Stream of Supabase auth state
  - currentUserProvider: Derived user from auth state
  - isAuthenticatedProvider: Boolean check
  - accessTokenProvider: Get JWT token
  - signOutProvider: Sign out function

**User Providers:**
- **user_provider.dart**
  - userProfileProvider: GET /api/v1/me
  - UpdateUserProfile: PUT /api/v1/me (with cache invalidation)
  - UpdateBirthDetails: PUT /api/v1/me/birth-details

**Config Providers:**
- **config_provider.dart**
  - appConfigProvider: GET /api/v1/config (cached)
  - chatMessageLimitProvider: Get limit for tier
  - isFeatureEnabledProvider: Check feature gate
  - reportPriceProvider: Get price for report type
  - creditPacksProvider: Get all credit packs

**Entitlement Providers:**
- **entitlement_provider.dart**
  - initializeRevenueCatProvider: Initialize SDK
  - customerInfoProvider: Stream of RevenueCat customer info
  - hasProProvider: Check "pro" entitlement
  - hasPremiumProvider: Check "premium" entitlement
  - PurchasePackageProvider: Purchase logic
  - PurchaseSubscriptionProvider: Subscribe logic
  - RestorePurchasesProvider: Restore logic
  - offeringsProvider: Get available products

**Chat Providers:**
- **chat_provider.dart**
  - ChatMessagesNotifier: StateNotifier for message list
  - chatMessagesProvider: Manage messages
  - remainingMessagesProvider: GET /api/v1/chat/remaining
  - SendChatMessageProvider: POST /api/v1/chat with rate limiting
  - chatHistoryProvider: GET paginated history

**Chart Providers:**
- **chart_provider.dart**
  - birthChartProvider: GET /api/v1/chart/full
  - chartSummaryProvider: GET /api/v1/chart/summary
  - divisionalChartProvider: GET /api/v1/chart/divisional/:d
  - d9ChartProvider, d10ChartProvider: Convenience providers
  - RefreshBirthChartProvider: Invalidate caches

**Forecast Providers:**
- **forecast_provider.dart**
  - dailyForecastProvider: GET /api/v1/forecast/daily
  - weeklyForecastProvider: GET /api/v1/forecast/weekly
  - monthlyForecastProvider: GET /api/v1/forecast/monthly
  - yearlyForecastProvider: GET /api/v1/forecast/yearly
  - RefreshForecastsProvider: Bulk invalidation

**Event Providers:**
- **events_provider.dart**
  - eventsForDateRangeProvider: GET with date filtering
  - allEventsProvider: GET all events
  - CreateEventProvider: POST /api/v1/events
  - UpdateEventProvider: PUT /api/v1/events/:id
  - DeleteEventProvider: DELETE /api/v1/events/:id
  - CorrelateEventProvider: POST /api/v1/events/correlate

**Credit Providers:**
- **credits_provider.dart**
  - CreditTransaction model (Freezed)
  - creditBalanceProvider: GET /api/v1/credits/balance
  - creditHistoryProvider: GET /api/v1/credits/history (paginated)
  - RefreshCreditsProvider: Invalidate caches

**Report Providers:**
- **reports_provider.dart**
  - ReportInfo model (Freezed)
  - availableReportsProvider: GET list of available reports
  - userReportsProvider: GET user's generated reports
  - reportDetailProvider: GET specific report
  - GenerateReportProvider: POST /api/v1/reports
  - reportPdfUrlProvider: Get download URL
  - RefreshUserReportsProvider: Cache invalidation

## Key Features Implemented

1. **Type Safety**: All models use Freezed for immutable, type-safe data classes
2. **State Management**: Riverpod with code generation for compile-time checked providers
3. **Auth Integration**: Supabase phone OTP + social (Google/Apple) with JWT handling
4. **Monetization**: RevenueCat integration for subscriptions and in-app purchases
5. **API Layer**: HTTP client with automatic auth token injection, error handling, rate limiting
6. **Push Notifications**: FCM with foreground/background message handling
7. **Feature Gating**: Config-driven feature access by subscription tier
8. **Caching**: Strategic invalidation patterns for data freshness
9. **Error Handling**: Custom ApiException with detailed error information
10. **Routing**: GoRouter with auth guards and deep linking support

## Next Steps

1. Run `flutter pub get` to install dependencies
2. Run `build_runner` to generate Freezed and Riverpod code:
   ```bash
   flutter pub run build_runner build --delete-conflicting-outputs
   ```
3. Create feature modules in `lib/features/` for screens and widgets
4. Implement shared widgets in `lib/shared/`
5. Create `main.dart` and `app.dart` entry points
6. Add environment-specific configurations (.env files)
7. Connect to actual Supabase and RevenueCat credentials

## Architecture Alignment

All files follow the architecture documented in `MOBILE_ARCHITECTURE.md`:
- ✅ Flutter 3.x + Dart 3.5
- ✅ Riverpod 2.x state management
- ✅ Supabase Auth (phone OTP, Google, Apple)
- ✅ RevenueCat billing integration
- ✅ Firebase Cloud Messaging
- ✅ GoRouter navigation with auth guards
- ✅ Dark cosmic theme with glassmorphic design
- ✅ Layered architecture (core → data → features)
- ✅ Modular, testable design
