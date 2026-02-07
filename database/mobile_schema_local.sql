-- 108 Mobile Extension Schema - Adapted for local Supabase
-- Maps to local DB where user table = "profiles" (profiles.id = auth.uid())
-- Original mobile_schema.sql targets "users" table from base schema.sql
-- This version adapts all references for the swara-chitta Supabase instance

-- ==============================================================================
-- PROFILE EXTENSIONS (add mobile-specific columns to existing profiles table)
-- ==============================================================================

ALTER TABLE profiles ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS revenuecat_id VARCHAR(100);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS fcm_token TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_profiles_phone ON profiles(phone);
CREATE INDEX IF NOT EXISTS idx_profiles_last_active ON profiles(last_active_at DESC);

-- ==============================================================================
-- HELPER FUNCTION
-- ==============================================================================

-- update_updated_at() already exists in this DB, so we skip creating it

-- ==============================================================================
-- MONETIZATION TABLES
-- ==============================================================================

CREATE TABLE IF NOT EXISTS credit_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    balance INTEGER DEFAULT 0,
    lifetime_purchased INTEGER DEFAULT 0,
    lifetime_spent INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_wallets_user ON credit_wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_wallets_balance ON credit_wallets(balance DESC);

CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    description TEXT,
    reference_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_user ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_type ON credit_transactions(user_id, transaction_type);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created ON credit_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_reference ON credit_transactions(reference_id);

-- ==============================================================================
-- CHAT AND MESSAGING TABLES
-- ==============================================================================

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text',
    metadata JSONB DEFAULT '{}',
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_user ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(user_id, role);

CREATE TABLE IF NOT EXISTS chat_daily_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL,
    message_count INTEGER DEFAULT 0,
    UNIQUE(user_id, usage_date)
);

CREATE INDEX IF NOT EXISTS idx_chat_daily_usage_user ON chat_daily_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_daily_usage_date ON chat_daily_usage(usage_date DESC);

-- ==============================================================================
-- REPORT GENERATION TABLES
-- ==============================================================================

CREATE TABLE IF NOT EXISTS generated_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content JSONB NOT NULL,
    pdf_url TEXT,
    credits_charged INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_generated_reports_user ON generated_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_reports_type ON generated_reports(user_id, report_type);
CREATE INDEX IF NOT EXISTS idx_generated_reports_status ON generated_reports(user_id, status);
CREATE INDEX IF NOT EXISTS idx_generated_reports_created ON generated_reports(created_at DESC);

-- ==============================================================================
-- USER EVENTS AND REMINDERS
-- ==============================================================================

CREATE TABLE IF NOT EXISTS user_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_user_events_user ON user_events(user_id);
CREATE INDEX IF NOT EXISTS idx_user_events_date ON user_events(user_id, event_date DESC);
CREATE INDEX IF NOT EXISTS idx_user_events_type ON user_events(user_id, event_type);
CREATE INDEX IF NOT EXISTS idx_user_events_created ON user_events(created_at DESC);

-- ==============================================================================
-- APPLICATION CONFIGURATION
-- ==============================================================================

CREATE TABLE IF NOT EXISTS app_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_app_config_key ON app_config(config_key);

-- Seed app configuration with defaults
INSERT INTO app_config (config_key, config_value, description) VALUES
('chat_limits', '{"free": 5, "nakshatra": 20, "graha": 50, "rishi": 999}'::jsonb, 'Daily message limits by subscription tier'),
('subscription_tiers', '{
  "free": {"name": "Free", "price": 0, "currency": "USD", "features": ["basic_readings", "daily_forecast", "chat_5_daily"]},
  "nakshatra": {"name": "Nakshatra", "price": 6.99, "currency": "USD", "features": ["birth_chart_analysis", "prediction_reports", "chat_20_daily", "no_ads"]},
  "graha": {"name": "Graha", "price": 6.99, "currency": "USD", "duration": "monthly", "features": ["birth_chart_analysis", "prediction_reports", "chat_50_daily", "no_ads", "compatibility_readings"]},
  "rishi": {"name": "Rishi", "price": 14.99, "currency": "USD", "duration": "monthly", "features": ["all_features", "chat_unlimited", "priority_support", "custom_reports", "advanced_predictions"]}
}'::jsonb, 'Available subscription tiers with pricing and features'),
('credit_packs', '{
  "small": {"credits": 50, "price": 2.99, "bonus_credits": 5},
  "medium": {"credits": 200, "price": 9.99, "bonus_credits": 40},
  "large": {"credits": 500, "price": 19.99, "bonus_credits": 150}
}'::jsonb, 'Available credit purchase packages'),
('report_prices', '{
  "birth_chart_analysis": 8, "yearly_predictions": 5, "compatibility_report": 6,
  "transit_forecast": 4, "dasha_insights": 5, "health_prediction": 5,
  "career_guidance": 6, "marriage_timing": 7
}'::jsonb, 'Credit costs for each report type'),
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

CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_notification_preferences_user ON notification_preferences(user_id);

-- ==============================================================================
-- ROW LEVEL SECURITY POLICIES
-- ==============================================================================

ALTER TABLE credit_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_daily_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

-- In this DB, profiles.id = auth.uid() directly (no auth_id indirection)
CREATE POLICY "Users can view own credit wallet"
    ON credit_wallets FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can update own credit wallet"
    ON credit_wallets FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can view own credit transactions"
    ON credit_transactions FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can view own chat messages"
    ON chat_messages FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own chat messages"
    ON chat_messages FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can view own daily usage"
    ON chat_daily_usage FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can update own daily usage"
    ON chat_daily_usage FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can view own generated reports"
    ON generated_reports FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own generated reports"
    ON generated_reports FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update own generated reports"
    ON generated_reports FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can view own user events"
    ON user_events FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can insert own user events"
    ON user_events FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Users can update own user events"
    ON user_events FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Users can delete own user events"
    ON user_events FOR DELETE USING (user_id = auth.uid());

CREATE POLICY "Users can view own notification preferences"
    ON notification_preferences FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can update own notification preferences"
    ON notification_preferences FOR UPDATE USING (user_id = auth.uid());

-- ==============================================================================
-- VIEW: user_mobile_profile
-- ==============================================================================

CREATE OR REPLACE VIEW user_mobile_profile AS
SELECT
    p.id,
    p.name,
    p.phone,
    p.gender,
    p.avatar_url,
    p.subscription_tier,
    p.onboarding_completed,
    p.revenuecat_id,
    p.fcm_token,
    p.last_active_at,
    p.lagna,
    p.moon_sign AS moon_rashi,
    p.moon_nakshatra,
    p.birth_datetime,
    p.birth_place AS place_name,
    cw.balance AS credit_balance,
    cw.lifetime_purchased AS lifetime_credits_purchased,
    cw.lifetime_spent AS lifetime_credits_spent,
    (SELECT COUNT(*) FROM chat_messages cm WHERE cm.user_id = p.id) AS total_messages,
    (SELECT COUNT(*) FROM generated_reports gr WHERE gr.user_id = p.id) AS total_reports,
    (SELECT COUNT(*) FROM user_events ue WHERE ue.user_id = p.id AND ue.is_system_generated = FALSE) AS user_event_count,
    np.daily_forecast,
    np.transit_alerts,
    np.dasha_changes,
    np.quiet_hours_start,
    np.quiet_hours_end,
    p.created_at,
    p.updated_at
FROM profiles p
LEFT JOIN credit_wallets cw ON cw.user_id = p.id
LEFT JOIN notification_preferences np ON np.user_id = p.id;
