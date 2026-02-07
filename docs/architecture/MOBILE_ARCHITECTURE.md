# 108 Mobile App Architecture

> Complete technical architecture for the 108 Flutter mobile app, backend gateway, and monetization system.
> All decisions locked. This is the single source of truth for implementation.

---

## 1. Tech Stack Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Mobile Framework** | Flutter 3.x + Dart | Cross-platform, single codebase for iOS + Android. Hot reload for fast iteration. Strong typing. |
| **State Management** | Riverpod 2.x | Type-safe, compile-time checked, testable. Provider-based but with code generation. Better than Bloc for this app (less boilerplate, more readable). |
| **Auth** | Supabase Auth | Phone OTP, Google Sign-In, Apple Sign-In. Postgres-native `auth.users` table. Row Level Security (RLS) built-in. |
| **Database** | Supabase Postgres | Extends existing pgvector schema. RLS for multi-user. Realtime subscriptions. Edge Functions for serverless logic. |
| **Realtime** | Supabase Realtime | WebSocket channels for chat streaming, transit alerts, live forecast updates. No extra infra. |
| **File Storage** | Supabase Storage | Generated PDF reports, user avatars. S3-compatible API. |
| **Billing** | RevenueCat | iOS + Android + Web subscriptions unified. Entitlements as feature flags. 1% after $2.5k/mo. Flutter SDK: `purchases_flutter`. |
| **Push Notifications** | Firebase Cloud Messaging (FCM) | Industry standard. Works alongside Supabase Auth. Supabase Edge Functions trigger FCM. |
| **Places API** | Google Places Autocomplete | Birth city search with lat/lon. Flutter package: `google_places_flutter` or raw HTTP. |
| **Remote Config** | Custom API endpoint | `/api/v1/config` returns all feature flags, limits, prices. Stored in `app_config` table. No Firebase dependency. |
| **Backend Compute** | FastAPI on Docker | Swiss Ephemeris binary requires Linux container. Existing 108-core runs as-is. Gateway layer added on top. |
| **Dev Hosting** | Local Docker Compose | Supabase local (supabase CLI), FastAPI, Redis. Zero cloud cost during dev. |
| **Prod Hosting** | AWS ECS Fargate | Containerized FastAPI. ALB for load balancing. Supabase Cloud for managed Postgres + Auth + Realtime. |
| **CDN** | CloudFront | Static assets, report PDFs, cached API responses. |
| **CI/CD** | GitHub Actions | Lint, test, build Flutter (iOS + Android), deploy Docker to ECS. |
| **Analytics** | PostHog (self-hosted on AWS) | Privacy-first. Funnels, retention, feature flags. No third-party data sharing. |
| **Error Tracking** | Sentry | Flutter + Python. Crash reports, performance monitoring. |

---

## 2. System Architecture

```
                    ┌─────────────────────────────────┐
                    │         FLUTTER APP              │
                    │  (iOS + Android)                 │
                    │                                  │
                    │  Riverpod State Management       │
                    │  RevenueCat SDK                  │
                    │  FCM Push                        │
                    │  Google Places SDK               │
                    └──────────┬──────────────────────┘
                               │ HTTPS / WSS
                               ▼
                    ┌──────────────────────────────────┐
                    │       SUPABASE CLOUD             │
                    │                                  │
                    │  Auth (Phone OTP, Google, Apple) │
                    │  Postgres (user data, config)    │
                    │  Realtime (chat, alerts)         │
                    │  Storage (reports, avatars)      │
                    │  Edge Functions (webhooks)       │
                    └──────────┬──────────────────────┘
                               │ Internal API
                               ▼
                    ┌──────────────────────────────────┐
                    │       API GATEWAY (FastAPI)       │
                    │                                  │
                    │  Auth Middleware (verify JWT)     │
                    │  Entitlements Check              │
                    │  Rate Limiter                    │
                    │  Response Formatter              │
                    │  Chat Orchestrator               │
                    └──────────┬──────────────────────┘
                               │ Direct import
                               ▼
                    ┌──────────────────────────────────┐
                    │       108-CORE ENGINE             │
                    │                                  │
                    │  COSMOS → SELF → CONTEXT → GUIDE │
                    │  (existing 2,100+ tests)         │
                    │  Swiss Ephemeris                  │
                    │  Knowledge Base (3.6MB)           │
                    └──────────────────────────────────┘
```

**Key insight:** The existing 108-core engine stays untouched. We add a gateway layer in front of it that handles users, auth, billing, and rate limiting. The Flutter app talks to Supabase directly for auth/realtime/storage, and to the FastAPI gateway for all astrological computations.

---

## 3. Database Schema (New Tables)

These tables extend the existing schema.sql. They live in Supabase Postgres alongside the existing tables.

### 3.1 Users (extends existing)

```sql
-- Supabase Auth handles auth.users automatically.
-- This is our application profile linked to auth.users.

ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_id UUID UNIQUE;  -- links to auth.users.id
ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(10);
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_complete BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free';  -- free, pro, premium
ALTER TABLE users ADD COLUMN IF NOT EXISTS revenuecat_id VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS fcm_token TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP DEFAULT NOW();

CREATE INDEX idx_users_auth_id ON users(auth_id);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_tier ON users(subscription_tier);
```

### 3.2 Credit Wallet

```sql
CREATE TABLE credit_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    balance INTEGER DEFAULT 0,
    lifetime_purchased INTEGER DEFAULT 0,
    lifetime_spent INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,              -- positive = credit, negative = debit
    balance_after INTEGER NOT NULL,       -- running balance
    transaction_type VARCHAR(20) NOT NULL, -- 'purchase', 'spend', 'refund', 'bonus'
    description TEXT,                      -- 'Career Timing Report', '50 Credit Pack'
    reference_id VARCHAR(100),             -- RevenueCat transaction ID or report ID
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_credit_wallets_user ON credit_wallets(user_id);
CREATE INDEX idx_credit_transactions_user ON credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_created ON credit_transactions(user_id, created_at DESC);
```

### 3.3 Chat Messages

```sql
-- Individual messages (not session-based like existing conversations table).
-- This is for the mobile chat UI — one row per message.

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL,            -- 'user' or 'assistant'
    content TEXT NOT NULL,                 -- raw text or markdown
    content_type VARCHAR(20) DEFAULT 'text', -- 'text', 'table', 'chart', 'card', 'report'
    metadata JSONB DEFAULT '{}',           -- render hints: {type: "score_card", data: {...}}
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_daily_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL,
    message_count INTEGER DEFAULT 0,
    UNIQUE(user_id, usage_date)
);

CREATE INDEX idx_chat_messages_user ON chat_messages(user_id, created_at DESC);
CREATE INDEX idx_chat_daily_usage_lookup ON chat_daily_usage(user_id, usage_date);
```

### 3.4 Generated Reports

```sql
CREATE TABLE generated_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,      -- 'year_ahead', 'career_blueprint', 'birth_chart_full', etc.
    title VARCHAR(200) NOT NULL,
    content JSONB NOT NULL,                -- structured report data
    pdf_url TEXT,                           -- Supabase Storage URL
    credits_charged INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'completed', -- 'generating', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reports_user ON generated_reports(user_id, created_at DESC);
CREATE INDEX idx_reports_type ON generated_reports(user_id, report_type);
```

### 3.5 Event Calendar

```sql
CREATE TABLE user_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME,
    event_type VARCHAR(30) NOT NULL,       -- 'personal', 'cosmic', 'muhurta', 'reminder'
    category VARCHAR(30),                   -- 'career', 'marriage', 'health', 'travel', etc.
    description TEXT,
    muhurta_score INTEGER,                  -- if muhurta was checked for this date
    correlation_score INTEGER,              -- if past event was correlated
    is_system_generated BOOLEAN DEFAULT FALSE,  -- cosmic events auto-populated
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_events_user_date ON user_events(user_id, event_date);
CREATE INDEX idx_user_events_type ON user_events(user_id, event_type);
```

### 3.6 App Configuration (Remote Config)

```sql
CREATE TABLE app_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Seed data
INSERT INTO app_config (config_key, config_value, description) VALUES
('chat_limits', '{"free": 5, "pro": 30, "premium": -1}', 'Daily chat message limits (-1 = unlimited)'),
('subscription_tiers', '{
    "free": {"name": "Nakshatra", "features": ["birth_chart_d1", "basic_daily", "basic_yoga_list"]},
    "pro": {"name": "Graha", "price_monthly": 6.99, "features": ["all_free", "full_forecasts", "muhurta", "event_calendar", "chat_30", "compatibility_basic", "yoga_dosha_full"]},
    "premium": {"name": "Rishi", "price_monthly": 14.99, "features": ["all_pro", "chat_unlimited", "yearly_forecast", "kp_predictions", "full_synastry", "atmakaraka", "soul_purpose", "all_remedies", "priority_ai"]}
}', 'Subscription tier definitions'),
('credit_packs', '[
    {"credits": 50, "price": 2.99, "label": "Starter"},
    {"credits": 200, "price": 9.99, "label": "Popular", "badge": "best_value"},
    {"credits": 500, "price": 19.99, "label": "Power User"}
]', 'Credit purchase options'),
('report_prices', '{
    "year_ahead": {"credits": 40, "money": 4.99, "title": "Your 2026 Year Ahead"},
    "birth_chart_full": {"credits": 50, "money": 7.99, "title": "Complete Birth Chart Analysis"},
    "career_blueprint": {"credits": 40, "money": 5.99, "title": "Career Blueprint"},
    "marriage_report": {"credits": 40, "money": 5.99, "title": "Marriage & Partner Report"},
    "soul_purpose": {"credits": 30, "money": 3.99, "title": "Soul Purpose & Spiritual Path"},
    "kp_question": {"credits": 15, "money": 1.99, "title": "KP Question Analysis"},
    "gem_prescription": {"credits": 20, "money": 2.99, "title": "Gem Prescription Guide"},
    "career_timing": {"credits": 30, "money": 3.99, "title": "Career Timing (12 months)"}
}', 'Report prices in credits and money'),
('feature_gates', '{
    "forecast_weekly": {"free": false, "pro": true, "premium": true},
    "forecast_monthly": {"free": false, "pro": true, "premium": true},
    "forecast_yearly": {"free": false, "pro": false, "premium": true},
    "chart_d9": {"free": false, "pro": true, "premium": true},
    "chart_d10": {"free": false, "pro": true, "premium": true},
    "chart_all_divisional": {"free": false, "pro": false, "premium": true},
    "yoga_interpretations": {"free": false, "pro": true, "premium": true},
    "dosha_remedies": {"free": false, "pro": true, "premium": true},
    "kp_predictions": {"free": false, "pro": false, "premium": true},
    "compatibility_synastry": {"free": false, "pro": false, "premium": true},
    "compatibility_basic": {"free": false, "pro": true, "premium": true},
    "atmakaraka_analysis": {"free": false, "pro": false, "premium": true},
    "gem_recommendations": {"free": false, "pro": true, "premium": true},
    "transit_alerts": {"free": false, "pro": true, "premium": true},
    "event_calendar": {"free": false, "pro": true, "premium": true},
    "push_notifications": {"free": false, "pro": true, "premium": true}
}', 'Feature access by tier (all dynamic, change without app update)');
```

### 3.7 Push Notification Preferences

```sql
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    daily_forecast BOOLEAN DEFAULT TRUE,
    transit_alerts BOOLEAN DEFAULT TRUE,
    dasha_changes BOOLEAN DEFAULT TRUE,
    muhurta_reminders BOOLEAN DEFAULT TRUE,
    event_reminders BOOLEAN DEFAULT TRUE,
    marketing BOOLEAN DEFAULT FALSE,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '07:00',
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API Gateway Layer

### 4.1 New Gateway Endpoints

These wrap the existing 108-core endpoints with auth + entitlements:

```
AUTH (Supabase handles directly — no FastAPI needed)
  POST /auth/signup-phone        → Supabase Auth
  POST /auth/verify-otp          → Supabase Auth
  POST /auth/login-google        → Supabase Auth
  POST /auth/login-apple         → Supabase Auth

USER PROFILE
  GET    /api/v1/me                → user profile + subscription + birth chart summary
  PUT    /api/v1/me                → update name, gender, avatar
  PUT    /api/v1/me/birth-details  → update birth date/time/place (recalculates chart)
  DELETE /api/v1/me                → delete account + all data (GDPR)

CONFIG
  GET  /api/v1/config              → all feature gates, limits, prices (cached 5 min)

CHART (gated by tier)
  GET  /api/v1/chart/summary       → basic chart for home dashboard (always available)
  GET  /api/v1/chart/full          → full chart with all planets (free: D1 only)
  GET  /api/v1/chart/divisional/:d → D2-D60 (pro: D1,D9,D10 | premium: all)

FORECAST (gated by tier)
  GET  /api/v1/forecast/daily      → free: score + 1 line | pro+: full breakdown
  GET  /api/v1/forecast/weekly     → pro+ only
  GET  /api/v1/forecast/monthly    → pro+ only
  GET  /api/v1/forecast/yearly     → premium only

ANALYSIS (gated by tier)
  GET  /api/v1/analysis/yogas      → free: names only | pro+: full interpretations
  GET  /api/v1/analysis/doshas     → free: names only | pro+: full + remedies
  GET  /api/v1/analysis/dasha      → free: current MD only | pro+: full timeline
  GET  /api/v1/analysis/transits   → free: basic | pro+: detailed + alerts
  POST /api/v1/analysis/kp         → premium only

CHAT
  POST /api/v1/chat                → send message, get AI response (rate limited)
  GET  /api/v1/chat/history        → paginated chat history
  GET  /api/v1/chat/remaining      → messages remaining today

COMPATIBILITY
  POST /api/v1/compatibility/quick   → Ashta Kuta only (pro+)
  POST /api/v1/compatibility/full    → full synastry (premium)

MUHURTA
  POST /api/v1/muhurta/check        → check specific date (pro+)
  POST /api/v1/muhurta/find         → find good dates (pro+)

REPORTS (credit-gated)
  GET  /api/v1/reports              → list available reports with prices
  POST /api/v1/reports/generate     → generate report (deducts credits)
  GET  /api/v1/reports/:id          → get generated report
  GET  /api/v1/reports/:id/pdf      → download PDF

EVENTS
  GET    /api/v1/events             → user events + cosmic events for date range
  POST   /api/v1/events             → create user event
  PUT    /api/v1/events/:id         → update event
  DELETE /api/v1/events/:id         → delete event
  POST   /api/v1/events/correlate   → correlate past event with chart

CREDITS
  GET  /api/v1/credits/balance      → current balance
  GET  /api/v1/credits/history      → transaction history

REMEDIES
  GET  /api/v1/remedies             → current active remedies (pro+)
  GET  /api/v1/remedies/gems        → gem recommendations (pro+)

WEBHOOKS (internal)
  POST /webhooks/revenuecat         → subscription status changes
```

### 4.2 Auth Middleware

```python
# Every request except /config and /webhooks requires a valid Supabase JWT.
# The middleware:
# 1. Extracts Bearer token from Authorization header
# 2. Verifies JWT with Supabase JWT secret
# 3. Looks up user in users table by auth_id
# 4. Attaches user object (with tier, credits) to request.state
# 5. If no user row exists, creates one (first login after signup)
```

### 4.3 Entitlements Middleware

```python
# After auth, before handler:
# 1. Load feature_gates from app_config (cached in Redis, 5 min TTL)
# 2. Check if requested feature is allowed for user's tier
# 3. If allowed → proceed with full response
# 4. If not allowed → return truncated response with access: "preview" or "locked"
#
# Response format:
# {
#   "data": { ... },          // full or truncated
#   "access": "full",         // "full" | "preview" | "locked"
#   "upgrade_hint": null      // or "Upgrade to Pro for full forecasts"
# }
```

### 4.4 Rate Limiter

```python
# Per-user rate limiting using Redis:
# 1. Key: rate:{user_id}:{date} → increment on each chat message
# 2. Check against chat_limits config for user's tier
# 3. TTL: midnight reset (user's timezone from birth data)
# 4. Returns X-RateLimit-Remaining header
# 5. When limit hit: 429 with upgrade_hint
```

---

## 5. Chat System Architecture

```
Flutter App
    │
    ├── POST /api/v1/chat  {message: "What about my career?"}
    │
    ▼
API Gateway
    │
    ├── 1. Auth check (JWT)
    ├── 2. Rate limit check (Redis counter)
    ├── 3. Load user context:
    │       - birth chart from DB
    │       - current dasha (calculated)
    │       - recent chat history (last 10 messages from DB)
    │       - subscription tier
    │
    ├── 4. Call Guide Agent:
    │       - classify intent
    │       - run calculations (108-core engine)
    │       - generate response with Claude
    │       - include render hints in metadata
    │
    ├── 5. Save messages to chat_messages table:
    │       - user message (role: 'user')
    │       - assistant response (role: 'assistant', content_type, metadata)
    │
    ├── 6. Increment daily usage counter
    │
    └── 7. Return response:
            {
              "message": {
                "content": "Your career is entering...",
                "content_type": "mixed",
                "metadata": {
                  "blocks": [
                    {"type": "text", "content": "Career analysis for Mercury MD / Venus AD:"},
                    {"type": "score_card", "data": {"score": 7.2, "label": "Career", "trend": "up"}},
                    {"type": "table", "data": {"headers": [...], "rows": [...]}},
                    {"type": "action_card", "data": {"text": "See full career report", "action": "open_report", "report_type": "career_blueprint"}}
                  ]
                }
              },
              "remaining_messages": 24,
              "access": "full"
            }
```

### Chat Content Types

The AI response includes `metadata.blocks` — an array of render instructions that the Flutter app interprets:

| Block Type | Flutter Widget | Description |
|-----------|---------------|-------------|
| `text` | `MarkdownBody` | Rich markdown text (headers, bold, lists) |
| `table` | `DataTable` | Structured data (planet positions, dasha periods) |
| `score_card` | Custom `ScoreCard` | Circular score with label and trend arrow |
| `timeline` | Custom `DashaTimeline` | Horizontal dasha period visualization |
| `alert` | Custom `AlertCard` | Transit warning or Sade Sati notice |
| `action_card` | Custom `ActionCard` | CTA button (open report, upgrade, navigate) |
| `expandable` | `ExpansionTile` | Technical details, collapsible |
| `divider` | `Divider` | Visual separator |

---

## 6. RevenueCat Integration

### 6.1 Product Setup

```
Apple App Store Connect:
  - 108_pro_monthly     ($6.99/mo auto-renew)
  - 108_pro_yearly      ($59.99/yr auto-renew)
  - 108_premium_monthly ($14.99/mo auto-renew)
  - 108_premium_yearly  ($119.99/yr auto-renew)
  - 108_credits_50      ($2.99 consumable)
  - 108_credits_200     ($9.99 consumable)
  - 108_credits_500     ($19.99 consumable)

Google Play Console:
  - Same product IDs

RevenueCat Entitlements:
  - "pro"     → granted by pro_monthly or pro_yearly
  - "premium" → granted by premium_monthly or premium_yearly
```

### 6.2 Webhook Flow

```
User subscribes in app
    → Apple/Google processes payment
    → RevenueCat receives receipt
    → RevenueCat calls POST /webhooks/revenuecat
    → Gateway updates users.subscription_tier
    → Gateway invalidates Redis cache for user
    → Next API call sees new tier immediately
```

### 6.3 Credit Purchase Flow

```
User buys credit pack in app
    → RevenueCat processes consumable purchase
    → Webhook fires with product_id = "108_credits_200"
    → Gateway:
        1. Lookup credit amount from app_config.credit_packs
        2. INSERT into credit_transactions (amount: +200)
        3. UPDATE credit_wallets SET balance = balance + 200
    → Flutter app polls /api/v1/credits/balance to confirm
```

---

## 7. Flutter App Structure

```
lib/
├── main.dart                    # App entry, Supabase init, RevenueCat init
├── app.dart                     # MaterialApp, theme, router
│
├── core/
│   ├── theme/
│   │   ├── app_theme.dart       # Dark theme, glassmorphic styles
│   │   ├── colors.dart          # Cosmic color palette
│   │   └── text_styles.dart     # Typography scale
│   ├── router/
│   │   └── app_router.dart      # GoRouter with auth guards
│   ├── constants/
│   │   └── api_constants.dart   # Base URLs, endpoints
│   └── utils/
│       ├── date_utils.dart
│       └── format_utils.dart
│
├── data/
│   ├── providers/
│   │   ├── auth_provider.dart       # Supabase auth state
│   │   ├── user_provider.dart       # User profile + birth chart
│   │   ├── config_provider.dart     # Remote config (feature gates)
│   │   ├── entitlement_provider.dart # RevenueCat entitlements
│   │   ├── chat_provider.dart       # Chat messages + rate limit
│   │   ├── forecast_provider.dart   # Daily/weekly/monthly/yearly
│   │   ├── chart_provider.dart      # Birth chart + divisional
│   │   ├── events_provider.dart     # Calendar events
│   │   ├── credits_provider.dart    # Wallet balance
│   │   └── reports_provider.dart    # Generated reports
│   ├── models/
│   │   ├── user_model.dart
│   │   ├── birth_chart_model.dart
│   │   ├── chat_message_model.dart
│   │   ├── forecast_model.dart
│   │   ├── event_model.dart
│   │   ├── report_model.dart
│   │   └── config_model.dart
│   └── services/
│       ├── api_service.dart         # HTTP client with auth headers
│       ├── supabase_service.dart    # Supabase client wrapper
│       └── notification_service.dart # FCM setup
│
├── features/
│   ├── auth/
│   │   ├── screens/
│   │   │   ├── phone_auth_screen.dart
│   │   │   └── otp_verify_screen.dart
│   │   └── widgets/
│   │       └── social_login_buttons.dart
│   │
│   ├── onboarding/
│   │   ├── screens/
│   │   │   ├── profile_screen.dart       # Name + Gender
│   │   │   └── birth_details_screen.dart  # Date + Time + Place
│   │   └── widgets/
│   │       ├── place_search_field.dart    # Google Places Autocomplete
│   │       └── time_picker_field.dart
│   │
│   ├── home/
│   │   ├── screens/
│   │   │   └── home_screen.dart          # Dashboard hub
│   │   └── widgets/
│   │       ├── today_score_card.dart      # Circular day rating
│   │       ├── quick_cards_row.dart       # Horizontal scroll cards
│   │       ├── forecast_tabs.dart         # Daily|Weekly|Monthly|Yearly
│   │       └── area_rating_bars.dart      # Career, finance, health bars
│   │
│   ├── chart/
│   │   ├── screens/
│   │   │   └── chart_screen.dart         # Birth chart viewer
│   │   └── widgets/
│   │       ├── south_indian_chart.dart    # D1 grid with planets
│   │       ├── planet_list.dart           # Planet detail list
│   │       ├── divisional_tabs.dart       # D1|D9|D10|More
│   │       └── planet_detail_sheet.dart   # Bottom sheet on tap
│   │
│   ├── chat/
│   │   ├── screens/
│   │   │   └── chat_screen.dart          # AI chat
│   │   └── widgets/
│   │       ├── chat_bubble.dart           # User/AI message bubble
│   │       ├── chat_table.dart            # Rendered data table
│   │       ├── chat_score_card.dart       # Inline score visualization
│   │       ├── chat_action_card.dart      # CTA button card
│   │       ├── chat_input_bar.dart        # Message input + send
│   │       └── remaining_counter.dart     # "12/30 messages today"
│   │
│   ├── timeline/
│   │   ├── screens/
│   │   │   └── timeline_screen.dart      # Life chapters
│   │   └── widgets/
│   │       ├── dasha_chapter_card.dart    # Period card
│   │       ├── nested_rings.dart          # MD/AD/PD rings
│   │       ├── transit_alert_banner.dart  # Sade Sati etc
│   │       └── event_pin.dart            # User event on timeline
│   │
│   ├── reports/
│   │   ├── screens/
│   │   │   ├── reports_store_screen.dart  # Browse reports
│   │   │   └── report_view_screen.dart   # View generated report
│   │   └── widgets/
│   │       ├── report_card.dart          # Report product card
│   │       └── generating_animation.dart  # Cosmic loader
│   │
│   ├── compatibility/
│   │   ├── screens/
│   │   │   └── compatibility_screen.dart
│   │   └── widgets/
│   │       ├── partner_input_form.dart
│   │       ├── kuta_score_ring.dart
│   │       └── kuta_breakdown.dart
│   │
│   ├── muhurta/
│   │   ├── screens/
│   │   │   └── muhurta_screen.dart
│   │   └── widgets/
│   │       ├── activity_picker.dart
│   │       ├── muhurta_calendar.dart
│   │       └── date_detail_sheet.dart
│   │
│   ├── calendar/
│   │   ├── screens/
│   │   │   └── calendar_screen.dart
│   │   └── widgets/
│   │       ├── cosmic_calendar.dart       # Month view
│   │       ├── day_detail_view.dart       # Tap day detail
│   │       └── add_event_sheet.dart
│   │
│   ├── remedies/
│   │   ├── screens/
│   │   │   └── remedies_screen.dart
│   │   └── widgets/
│   │       ├── remedy_card.dart
│   │       └── gem_card.dart
│   │
│   ├── settings/
│   │   ├── screens/
│   │   │   ├── settings_screen.dart
│   │   │   ├── subscription_screen.dart  # Manage subscription
│   │   │   └── notification_screen.dart  # Notification prefs
│   │   └── widgets/
│   │       └── birth_details_editor.dart
│   │
│   └── paywall/
│       ├── screens/
│       │   ├── paywall_screen.dart        # Full upgrade screen
│       │   └── credit_store_screen.dart   # Buy credits
│       └── widgets/
│           ├── tier_comparison.dart       # Side-by-side tiers
│           ├── locked_overlay.dart        # Blur + lock icon
│           └── credit_pack_card.dart
│
├── shared/
│   ├── widgets/
│   │   ├── star_background.dart          # Animated star particles
│   │   ├── glass_card.dart               # Glassmorphic container
│   │   ├── cosmic_loader.dart            # Loading animation
│   │   ├── planet_glyph.dart             # Planet icon/symbol
│   │   ├── bottom_nav_bar.dart           # Main navigation
│   │   └── locked_feature.dart           # Generic lock overlay
│   └── animations/
│       ├── star_field.dart               # Background star motion
│       └── chart_calculation.dart         # "Calculating..." animation
│
└── gen/                                   # Generated code (Riverpod, router, etc.)
```

### 7.1 Navigation Structure

```
BottomNavigationBar (5 tabs):
  ├── Home       (HomeScreen)
  ├── Chart      (ChartScreen)
  ├── Chat       (ChatScreen)        ← center, prominent
  ├── Calendar   (CalendarScreen)
  └── Profile    (SettingsScreen)

Accessed via navigation/buttons (not tabs):
  ├── Timeline    (from Home card)
  ├── Reports     (from Home or Chat action cards)
  ├── Muhurta     (from Calendar or Chat)
  ├── Remedies    (from Chart or Chat)
  ├── Compatibility (from Profile or Chat)
  └── Paywall     (from any locked feature)
```

### 7.2 Key Flutter Packages

```yaml
dependencies:
  flutter_riverpod: ^2.5.0
  riverpod_annotation: ^2.3.0
  go_router: ^14.0.0
  supabase_flutter: ^2.5.0
  purchases_flutter: ^7.0.0          # RevenueCat
  firebase_messaging: ^15.0.0        # FCM
  google_places_flutter: ^3.0.0      # Places autocomplete
  flutter_markdown: ^0.7.0           # Markdown rendering in chat
  geolocator: ^12.0.0               # Current location
  table_calendar: ^3.1.0             # Calendar widget
  fl_chart: ^0.68.0                  # Charts and score rings
  shimmer: ^3.0.0                    # Skeleton loading
  cached_network_image: ^3.4.0       # Image caching
  lottie: ^3.1.0                     # Animations
  share_plus: ^9.0.0                 # Share reports
  path_provider: ^2.1.0              # File storage
  intl: ^0.19.0                      # Date formatting
  flutter_local_notifications: ^17.0.0  # Local notifications
  freezed_annotation: ^2.4.0         # Immutable models
  json_annotation: ^4.9.0            # JSON serialization

dev_dependencies:
  riverpod_generator: ^2.4.0
  build_runner: ^2.4.0
  freezed: ^2.5.0
  json_serializable: ^6.8.0
  flutter_test:
    sdk: flutter
  mocktail: ^1.0.0
  golden_toolkit: ^0.15.0
```

---

## 8. Development Setup

### 8.1 Local Environment

```bash
# 1. Supabase local (handles Postgres + Auth + Realtime + Storage)
brew install supabase/tap/supabase
cd 108-core
supabase init
supabase start
# Outputs: API URL, anon key, service role key, DB URL

# 2. Apply existing schema + new tables
psql "postgresql://postgres:postgres@localhost:54322/postgres" < database/schema.sql
psql "postgresql://postgres:postgres@localhost:54322/postgres" < database/mobile_schema.sql

# 3. FastAPI gateway (existing 108-core + new gateway layer)
uv run uvicorn services.api.main:app --reload --port 8000

# 4. Redis (for rate limiting cache)
docker run -d --name 108-redis -p 6379:6379 redis:alpine

# 5. Flutter app
cd 108-app
flutter pub get
flutter run
```

### 8.2 Environment Variables

```env
# .env (FastAPI gateway)
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_KEY=eyJ...           # service role key (full access)
SUPABASE_JWT_SECRET=super-secret-...   # for JWT verification
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=sk-ant-...
REVENUECAT_WEBHOOK_SECRET=rc_...
FCM_SERVER_KEY=AAAA...

# Flutter app env
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=eyJ...
REVENUECAT_API_KEY_IOS=appl_...
REVENUECAT_API_KEY_ANDROID=goog_...
GOOGLE_PLACES_API_KEY=AIza...
```

---

## 9. Production Deployment (AWS)

```
┌─────────────────────────────────────────────────────┐
│                    AWS Account                       │
│                                                      │
│  CloudFront CDN                                      │
│       ↓                                              │
│  ALB (Application Load Balancer)                     │
│       ↓                                              │
│  ECS Fargate Cluster                                 │
│  ┌─────────────────────────────────────────────┐    │
│  │  Task: 108-api                               │    │
│  │  - FastAPI gateway container                 │    │
│  │  - Swiss Ephemeris binary included           │    │
│  │  - Auto-scaling: 2-10 tasks                  │    │
│  │  - CPU: 1 vCPU, RAM: 2GB per task           │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ElastiCache Redis (rate limiting + config cache)    │
│                                                      │
│  S3 (generated report PDFs, backups)                 │
│                                                      │
│  ECR (Docker image registry)                         │
│                                                      │
│  CloudWatch (logs, metrics, alerts)                  │
│                                                      │
│  Secrets Manager (API keys, JWT secrets)             │
│                                                      │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
            Supabase Cloud (managed)
            - Postgres (user data, config)
            - Auth (phone, Google, Apple)
            - Realtime (WebSocket)
            - Storage (files)
            - Edge Functions (webhooks)
```

### Estimated AWS costs (1,000 DAU):
- ECS Fargate (2 tasks): ~$60/mo
- ALB: ~$20/mo
- ElastiCache Redis (t3.micro): ~$15/mo
- CloudFront: ~$5/mo
- S3: ~$2/mo
- **Total AWS: ~$102/mo**

### Supabase Cloud (Pro plan): $25/mo
### RevenueCat: Free until $2.5k/mo revenue

**Total infrastructure at launch: ~$130/mo**

---

## 10. Security Checklist

- [ ] Supabase RLS policies on all tables (users can only read their own data)
- [ ] JWT verification on every API endpoint
- [ ] Rate limiting on chat and compute-heavy endpoints
- [ ] Input validation (birth dates, coordinates, text length)
- [ ] SQL injection prevention (parameterized queries via Supabase client)
- [ ] RevenueCat webhook signature verification
- [ ] HTTPS everywhere (Supabase + ALB + CloudFront)
- [ ] API keys in Secrets Manager, never in code
- [ ] FCM token rotation handling
- [ ] GDPR: account deletion removes all user data
- [ ] App Store / Play Store compliance for subscription disclosures

---

## 11. Implementation Order

### Phase 1: Backend Gateway (Week 1-2)
1. Set up Supabase project (local + cloud)
2. Create mobile_schema.sql with new tables
3. Add auth middleware to FastAPI
4. Add entitlements middleware
5. Add rate limiter (Redis)
6. Create /api/v1/config endpoint
7. Create /api/v1/me endpoints (profile CRUD)
8. Wrap existing chart/forecast/analysis endpoints with gating
9. Build chat endpoint with Guide agent integration
10. RevenueCat webhook handler
11. Credit wallet endpoints
12. Tests for all new endpoints

### Phase 2: Flutter Scaffold (Week 2-3)
1. Flutter project setup with folder structure
2. Riverpod providers setup
3. Supabase Flutter initialization
4. RevenueCat Flutter initialization
5. GoRouter with auth guards
6. Dark theme + glassmorphic design system
7. Star particle background animation
8. Glass card, planet glyph, locked overlay shared widgets
9. Bottom navigation skeleton

### Phase 3: Auth + Onboarding (Week 3)
1. Phone auth screen + OTP verification
2. Google + Apple sign-in buttons
3. Profile screen (name + gender)
4. Birth details screen with Places Autocomplete
5. Chart calculation loading animation
6. First-time user flow (auth → profile → birth → home)

### Phase 4: Core Screens (Week 4-5)
1. Home dashboard (today score, quick cards, forecast tabs)
2. Birth chart viewer (South Indian grid, planet list)
3. AI Chat (message bubbles, rich content rendering, rate limit counter)
4. Life Timeline (dasha chapters, nested rings)

### Phase 5: Features + Monetization (Week 6-7)
1. Paywall screen + tier comparison
2. Credit store
3. Reports store + generation + viewing
4. Event calendar
5. Muhurta finder
6. Compatibility screen
7. Remedies dashboard
8. Settings + subscription management

### Phase 6: Polish + Launch (Week 8)
1. Push notifications (FCM)
2. Onboarding tutorial/tooltips
3. Error handling + offline states
4. Performance optimization (lazy loading, caching)
5. App Store + Play Store assets (screenshots, description)
6. TestFlight / Internal testing
7. Launch
