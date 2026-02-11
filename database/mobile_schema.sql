-- 108 Vedic Astrology App - Mobile Extension Schema
-- Extends the core schema.sql with mobile-specific features, monetization, and real-time capabilities
-- Compatible with Supabase PostgreSQL

-- ==============================================================================
-- MOBILE USER PROFILE EXTENSIONS
-- ==============================================================================

-- Alter users table to add mobile-specific columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_id UUID UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(10);
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_complete BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS revenuecat_id VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS fcm_token TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP DEFAULT NOW();

-- Create indexes for mobile user queries
CREATE INDEX IF NOT EXISTS idx_users_auth_id ON users(auth_id);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active_at DESC);

-- ==============================================================================
-- MONETIZATION TABLES
-- ==============================================================================

-- Credit Wallets: Track user credit balances for premium features
CREATE TABLE IF NOT EXISTS credit_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    balance INTEGER DEFAULT 0,
    lifetime_purchased INTEGER DEFAULT 0,
    lifetime_spent INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE credit_wallets IS 'Tracks user credit balances and spending for premium features';
COMMENT ON COLUMN credit_wallets.balance IS 'Current available credits (0-based, non-negative)';
COMMENT ON COLUMN credit_wallets.lifetime_purchased IS 'Total credits ever purchased by user';
COMMENT ON COLUMN credit_wallets.lifetime_spent IS 'Total credits ever spent/consumed by user';

CREATE INDEX IF NOT EXISTS idx_credit_wallets_user ON credit_wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_wallets_balance ON credit_wallets(balance DESC);

-- Trigger for credit_wallets updated_at
CREATE TRIGGER IF NOT EXISTS update_credit_wallets_updated_at BEFORE UPDATE ON credit_wallets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Credit Transactions: Audit log of all credit movements
CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    description TEXT,
    reference_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE credit_transactions IS 'Complete audit log of all credit transactions';
COMMENT ON COLUMN credit_transactions.amount IS 'Credit change amount (positive=credit, negative=debit)';
COMMENT ON COLUMN credit_transactions.transaction_type IS 'Type: purchase, spend, refund, or bonus';
COMMENT ON COLUMN credit_transactions.reference_id IS 'External reference (e.g., RevenueCat transaction ID, report ID)';

CREATE INDEX IF NOT EXISTS idx_credit_transactions_user ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_type ON credit_transactions(user_id, transaction_type);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created ON credit_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_reference ON credit_transactions(reference_id);

-- ==============================================================================
-- CHAT AND MESSAGING TABLES
-- ==============================================================================

-- Chat Messages: Individual messages in chat sessions
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text',
    metadata JSONB DEFAULT '{}',
    blocks JSONB DEFAULT '[]',
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE chat_messages IS 'Chat messages from user-assistant conversations';
COMMENT ON COLUMN chat_messages.role IS 'Message sender: user or assistant';
COMMENT ON COLUMN chat_messages.content_type IS 'Content format: text, table, chart, card, or report';
COMMENT ON COLUMN chat_messages.metadata IS 'Rendering hints and UI context (e.g., chart type, table columns)';
COMMENT ON COLUMN chat_messages.tokens_used IS 'LLM tokens consumed by this message';

CREATE INDEX IF NOT EXISTS idx_chat_messages_user ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(user_id, role);

-- Chat Daily Usage: Aggregated daily message counts
CREATE TABLE IF NOT EXISTS chat_daily_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL,
    message_count INTEGER DEFAULT 0,
    UNIQUE(user_id, usage_date)
);

COMMENT ON TABLE chat_daily_usage IS 'Daily aggregated chat message counts for rate limiting';

CREATE INDEX IF NOT EXISTS idx_chat_daily_usage_user ON chat_daily_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_daily_usage_date ON chat_daily_usage(usage_date DESC);

-- ==============================================================================
-- REPORT GENERATION TABLES
-- ==============================================================================

-- Generated Reports: Stored generated astrological reports
CREATE TABLE IF NOT EXISTS generated_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content JSONB NOT NULL,
    pdf_url TEXT,
    credits_charged INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE generated_reports IS 'Generated and stored astrological reports with full content';
COMMENT ON COLUMN generated_reports.report_type IS 'Report category (e.g., birth_chart, predictions, compatibility)';
COMMENT ON COLUMN generated_reports.content IS 'Full report data in JSONB format';
COMMENT ON COLUMN generated_reports.status IS 'Generation status: generating, completed, or failed';

CREATE INDEX IF NOT EXISTS idx_generated_reports_user ON generated_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_reports_type ON generated_reports(user_id, report_type);
CREATE INDEX IF NOT EXISTS idx_generated_reports_status ON generated_reports(user_id, status);
CREATE INDEX IF NOT EXISTS idx_generated_reports_created ON generated_reports(created_at DESC);

-- ==============================================================================
-- USER EVENTS AND REMINDERS
-- ==============================================================================

-- User Events: Personal and system-generated events
CREATE TABLE IF NOT EXISTS user_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME,
    event_type VARCHAR(30) NOT NULL,
    category VARCHAR(30),
    description TEXT,
    muhurta_score INTEGER,
    correlation_score INTEGER,
    is_system_generated BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE user_events IS 'Personal events and system-generated cosmic/muhurta events';
COMMENT ON COLUMN user_events.event_type IS 'Event category: personal, cosmic, muhurta, or reminder';
COMMENT ON COLUMN user_events.muhurta_score IS 'Auspiciousness score for muhurta events (0-100)';
COMMENT ON COLUMN user_events.correlation_score IS 'Correlation score linking event to astrological factors (0-100)';
COMMENT ON COLUMN user_events.is_system_generated IS 'Whether event was auto-generated by system (false=user-created)';

CREATE INDEX IF NOT EXISTS idx_user_events_user ON user_events(user_id);
CREATE INDEX IF NOT EXISTS idx_user_events_date ON user_events(user_id, event_date DESC);
CREATE INDEX IF NOT EXISTS idx_user_events_type ON user_events(user_id, event_type);
CREATE INDEX IF NOT EXISTS idx_user_events_created ON user_events(created_at DESC);

-- ==============================================================================
-- APPLICATION CONFIGURATION
-- ==============================================================================

-- App Config: Centralized configuration management for mobile app
CREATE TABLE IF NOT EXISTS app_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE app_config IS 'Centralized app configuration, pricing, feature gates';
COMMENT ON COLUMN app_config.config_key IS 'Configuration key (e.g., chat_limits, subscription_tiers, feature_gates)';
COMMENT ON COLUMN app_config.config_value IS 'Configuration value in JSONB format';

CREATE INDEX IF NOT EXISTS idx_app_config_key ON app_config(config_key);

-- Seed app configuration with defaults
INSERT INTO app_config (config_key, config_value, description) VALUES
('chat_limits', '{"free": 5, "nakshatra": 20, "graha": 50, "rishi": 999}'::jsonb, 'Daily message limits by subscription tier'),
('subscription_tiers', '{
  "free": {
    "name": "Free",
    "price": 0,
    "currency": "USD",
    "features": ["basic_readings", "daily_forecast", "chat_5_daily"]
  },
  "nakshatra": {
    "name": "Nakshatra",
    "price": 6.99,
    "currency": "USD",
    "features": ["birth_chart_analysis", "prediction_reports", "chat_20_daily", "no_ads"]
  },
  "graha": {
    "name": "Graha",
    "price": 6.99,
    "currency": "USD",
    "duration": "monthly",
    "features": ["birth_chart_analysis", "prediction_reports", "chat_50_daily", "no_ads", "compatibility_readings"]
  },
  "rishi": {
    "name": "Rishi",
    "price": 14.99,
    "currency": "USD",
    "duration": "monthly",
    "features": ["all_features", "chat_unlimited", "priority_support", "custom_reports", "advanced_predictions"]
  }
}'::jsonb, 'Available subscription tiers with pricing and features')
ON CONFLICT (config_key) DO NOTHING;

INSERT INTO app_config (config_key, config_value, description) VALUES
('credit_packs', '{
  "small": {"credits": 50, "price": 2.99, "bonus_credits": 5},
  "medium": {"credits": 200, "price": 9.99, "bonus_credits": 40},
  "large": {"credits": 500, "price": 19.99, "bonus_credits": 150}
}'::jsonb, 'Available credit purchase packages')
ON CONFLICT (config_key) DO NOTHING;

INSERT INTO app_config (config_key, config_value, description) VALUES
('report_prices', '{
  "birth_chart_analysis": 8,
  "yearly_predictions": 5,
  "compatibility_report": 6,
  "transit_forecast": 4,
  "dasha_insights": 5,
  "health_prediction": 5,
  "career_guidance": 6,
  "marriage_timing": 7
}'::jsonb, 'Credit costs for each report type')
ON CONFLICT (config_key) DO NOTHING;

INSERT INTO app_config (config_key, config_value, description) VALUES
('feature_gates', '{
  "birth_chart_analysis": {"free": false, "nakshatra": true, "graha": true, "rishi": true},
  "yearly_predictions": {"free": false, "nakshatra": true, "graha": true, "rishi": true},
  "compatibility_check": {"free": false, "nakshatra": false, "graha": true, "rishi": true},
  "transit_forecast": {"free": true, "nakshatra": true, "graha": true, "rishi": true},
  "dasha_timeline": {"free": true, "nakshatra": true, "graha": true, "rishi": true},
  "health_prediction": {"free": false, "nakshatra": false, "graha": true, "rishi": true},
  "career_guidance": {"free": false, "nakshatra": true, "graha": true, "rishi": true},
  "marriage_timing": {"free": false, "nakshatra": true, "graha": true, "rishi": true},
  "custom_reports": {"free": false, "nakshatra": false, "graha": false, "rishi": true},
  "advanced_analytics": {"free": false, "nakshatra": false, "graha": true, "rishi": true},
  "priority_support": {"free": false, "nakshatra": false, "graha": false, "rishi": true},
  "chat_history": {"free": true, "nakshatra": true, "graha": true, "rishi": true},
  "export_reports": {"free": false, "nakshatra": true, "graha": true, "rishi": true},
  "remove_ads": {"free": false, "nakshatra": true, "graha": true, "rishi": true},
  "monthly_digest": {"free": false, "nakshatra": true, "graha": true, "rishi": true},
  "astrological_events": {"free": true, "nakshatra": true, "graha": true, "rishi": true}
}'::jsonb, 'Feature availability by subscription tier')
ON CONFLICT (config_key) DO NOTHING;

-- ==============================================================================
-- NOTIFICATION PREFERENCES
-- ==============================================================================

-- Notification Preferences: User notification configuration
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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

COMMENT ON TABLE notification_preferences IS 'User push notification and alert preferences';
COMMENT ON COLUMN notification_preferences.quiet_hours_start IS 'Start of quiet hours (e.g., 22:00 for 10 PM)';
COMMENT ON COLUMN notification_preferences.quiet_hours_end IS 'End of quiet hours (e.g., 07:00 for 7 AM)';

CREATE INDEX IF NOT EXISTS idx_notification_preferences_user ON notification_preferences(user_id);

-- Trigger for notification_preferences updated_at
CREATE TRIGGER IF NOT EXISTS update_notification_preferences_updated_at BEFORE UPDATE ON notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================================================
-- RLS HELPER FUNCTION
-- ==============================================================================

-- Helper function to get current user's ID from Supabase auth
CREATE OR REPLACE FUNCTION get_current_user_id() RETURNS UUID AS $$
BEGIN
    RETURN (SELECT id FROM users WHERE auth_id = auth.uid());
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- ROW LEVEL SECURITY POLICIES
-- ==============================================================================

-- Enable RLS on all mobile-specific tables
ALTER TABLE credit_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_daily_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

-- Also enable RLS on extended users table if not already enabled
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Credit Wallets Policies
CREATE POLICY "Users can view own credit wallet"
    ON credit_wallets FOR SELECT
    USING (user_id = get_current_user_id());

CREATE POLICY "Users can update own credit wallet"
    ON credit_wallets FOR UPDATE
    USING (user_id = get_current_user_id());

-- Credit Transactions Policies
CREATE POLICY "Users can view own credit transactions"
    ON credit_transactions FOR SELECT
    USING (user_id = get_current_user_id());

-- Chat Messages Policies
CREATE POLICY "Users can view own chat messages"
    ON chat_messages FOR SELECT
    USING (user_id = get_current_user_id());

CREATE POLICY "Users can insert own chat messages"
    ON chat_messages FOR INSERT
    WITH CHECK (user_id = get_current_user_id());

-- Chat Daily Usage Policies
CREATE POLICY "Users can view own daily usage"
    ON chat_daily_usage FOR SELECT
    USING (user_id = get_current_user_id());

CREATE POLICY "Users can update own daily usage"
    ON chat_daily_usage FOR UPDATE
    USING (user_id = get_current_user_id());

-- Generated Reports Policies
CREATE POLICY "Users can view own generated reports"
    ON generated_reports FOR SELECT
    USING (user_id = get_current_user_id());

CREATE POLICY "Users can insert own generated reports"
    ON generated_reports FOR INSERT
    WITH CHECK (user_id = get_current_user_id());

CREATE POLICY "Users can update own generated reports"
    ON generated_reports FOR UPDATE
    USING (user_id = get_current_user_id());

-- User Events Policies
CREATE POLICY "Users can view own user events"
    ON user_events FOR SELECT
    USING (user_id = get_current_user_id());

CREATE POLICY "Users can insert own user events"
    ON user_events FOR INSERT
    WITH CHECK (user_id = get_current_user_id());

CREATE POLICY "Users can update own user events"
    ON user_events FOR UPDATE
    USING (user_id = get_current_user_id());

CREATE POLICY "Users can delete own user events"
    ON user_events FOR DELETE
    USING (user_id = get_current_user_id());

-- Notification Preferences Policies
CREATE POLICY "Users can view own notification preferences"
    ON notification_preferences FOR SELECT
    USING (user_id = get_current_user_id());

CREATE POLICY "Users can update own notification preferences"
    ON notification_preferences FOR UPDATE
    USING (user_id = get_current_user_id());

-- User Profile Policies (RLS for mobile auth_id field)
CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (auth_id = auth.uid());

CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (auth_id = auth.uid());

-- ==============================================================================
-- VIEWS
-- ==============================================================================

-- User Mobile Profile: Complete mobile user view with subscription and credit info
CREATE OR REPLACE VIEW user_mobile_profile AS
SELECT
    u.id,
    u.email,
    u.name,
    u.phone,
    u.gender,
    u.avatar_url,
    u.auth_id,
    u.subscription_tier,
    u.onboarding_complete,
    u.fcm_token,
    u.last_active_at,
    bc.lagna_rashi,
    bc.moon_rashi,
    bc.moon_nakshatra,
    bc.birth_datetime,
    bc.place_name,
    cw.balance as credit_balance,
    cw.lifetime_purchased as lifetime_credits_purchased,
    cw.lifetime_spent as lifetime_credits_spent,
    (SELECT COUNT(*) FROM chat_messages cm WHERE cm.user_id = u.id) as total_messages,
    (SELECT COUNT(*) FROM generated_reports gr WHERE gr.user_id = u.id) as total_reports,
    (SELECT COUNT(*) FROM user_events ue WHERE ue.user_id = u.id AND ue.is_system_generated = FALSE) as user_event_count,
    np.daily_forecast,
    np.transit_alerts,
    np.dasha_changes,
    np.quiet_hours_start,
    np.quiet_hours_end,
    u.created_at,
    u.updated_at
FROM users u
LEFT JOIN birth_charts bc ON bc.user_id = u.id
LEFT JOIN credit_wallets cw ON cw.user_id = u.id
LEFT JOIN notification_preferences np ON np.user_id = u.id;

COMMENT ON VIEW user_mobile_profile IS 'Complete user profile with subscription, credits, and notification preferences for mobile app';

-- ==============================================================================
-- TABLE DOCUMENTATION
-- ==============================================================================

COMMENT ON TABLE credit_wallets IS 'Tracks user credit balances for premium features and reports';
COMMENT ON TABLE credit_transactions IS 'Immutable audit log of all credit movements (purchases, usage, refunds)';
COMMENT ON TABLE chat_messages IS 'Individual chat messages between user and AI assistant';
COMMENT ON TABLE chat_daily_usage IS 'Daily message count tracking for rate limiting and analytics';
COMMENT ON TABLE generated_reports IS 'Generated and cached astrological reports (birth chart, predictions, etc)';
COMMENT ON TABLE user_events IS 'User-created events and system-generated cosmic/muhurta recommendations';
COMMENT ON TABLE notification_preferences IS 'Push notification settings and quiet hours configuration';
COMMENT ON TABLE app_config IS 'Centralized app configuration (tiers, pricing, features, limits)';
