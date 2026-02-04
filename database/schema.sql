-- 108 Vedic Astrology App - PostgreSQL Database Schema
-- PostgreSQL with pgvector extension for semantic search and ML capabilities

-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================================================
-- CORE TABLES
-- ==============================================================================

-- Users: Core user accounts
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Birth Charts: Birth chart data with planet positions and houses
CREATE TABLE birth_charts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    birth_datetime TIMESTAMP NOT NULL,
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    place_name VARCHAR(255),
    ayanamsa DECIMAL(10, 6),
    lagna_rashi VARCHAR(20),
    moon_rashi VARCHAR(20),
    moon_nakshatra VARCHAR(30),
    moon_nakshatra_pada INTEGER,
    planets JSONB,  -- Full planet positions
    houses JSONB,   -- House cusps
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)  -- One birth chart per user
);

-- Detected Patterns: Detected yogas and doshas from birth chart analysis
CREATE TABLE detected_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pattern_type VARCHAR(20) NOT NULL,  -- 'yoga' or 'dosha'
    pattern_id VARCHAR(50) NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    strength DECIMAL(3, 2),
    severity VARCHAR(20),  -- For doshas: mild, moderate, severe
    involved_planets TEXT[],
    details JSONB,
    detected_at TIMESTAMP DEFAULT NOW()
);

-- ==============================================================================
-- SEMANTIC MEMORY & LEARNING TABLES
-- ==============================================================================

-- Memories: Semantic memories with vector embeddings for RAG
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,  -- 'fact', 'preference', 'event', 'prediction', 'feedback'
    embedding vector(1536),  -- OpenAI embedding dimension
    metadata JSONB DEFAULT '{}',
    importance DECIMAL(3, 2) DEFAULT 0.5,  -- 0-1 importance score
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Predictions: Predictions made by the system for validation and learning
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    prediction_text TEXT NOT NULL,
    category VARCHAR(50),  -- 'career', 'relationship', 'health', 'finance', etc.
    timeframe_start DATE,
    timeframe_end DATE,
    confidence DECIMAL(3, 2),  -- 0-1 confidence score
    factors JSONB,  -- What astrological factors led to this prediction
    dasha_period JSONB,  -- Current dasha at time of prediction
    transit_positions JSONB,  -- Key transits at time of prediction
    outcome TEXT,  -- User-provided outcome
    accuracy DECIMAL(3, 2),  -- 0-1 accuracy after validation
    validated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations: Conversation history with embeddings for context and learning
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    messages JSONB NOT NULL,  -- Array of {role, content, timestamp}
    summary TEXT,
    topics TEXT[],  -- Extracted topics
    embedding vector(1536),  -- Conversation embedding for similarity
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==============================================================================
-- CONFIGURATION TABLES
-- ==============================================================================

-- User Preferences: Explicit user settings and preferences
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    preference_key VARCHAR(100) NOT NULL,
    preference_value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, preference_key)
);

-- ==============================================================================
-- ASTROLOGICAL CALCULATION CACHE TABLES
-- ==============================================================================

-- Dasha Timeline: Precomputed Vimshottari dasha periods for quick access
CREATE TABLE dasha_timeline (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,  -- 'maha', 'antar', 'pratyantar'
    lord VARCHAR(20) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    parent_id UUID REFERENCES dasha_timeline(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==============================================================================
-- INDEXES FOR PERFORMANCE
-- ==============================================================================

-- Memories indexes
CREATE INDEX idx_memories_user ON memories(user_id);
CREATE INDEX idx_memories_category ON memories(user_id, category);
CREATE INDEX idx_memories_embedding ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_memories_created ON memories(created_at DESC);
CREATE INDEX idx_memories_importance ON memories(user_id, importance DESC);

-- Birth charts indexes
CREATE INDEX idx_birth_charts_user ON birth_charts(user_id);
CREATE INDEX idx_birth_charts_lagna ON birth_charts(user_id, lagna_rashi);

-- Predictions indexes
CREATE INDEX idx_predictions_user ON predictions(user_id);
CREATE INDEX idx_predictions_timeframe ON predictions(user_id, timeframe_start, timeframe_end);
CREATE INDEX idx_predictions_category ON predictions(user_id, category);
CREATE INDEX idx_predictions_confidence ON predictions(user_id, confidence DESC);

-- Conversations indexes
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_embedding ON conversations USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);

-- Detected patterns indexes
CREATE INDEX idx_detected_patterns_user ON detected_patterns(user_id);
CREATE INDEX idx_detected_patterns_type ON detected_patterns(user_id, pattern_type);
CREATE INDEX idx_detected_patterns_name ON detected_patterns(user_id, pattern_name);

-- Dasha timeline indexes
CREATE INDEX idx_dasha_timeline_user ON dasha_timeline(user_id);
CREATE INDEX idx_dasha_timeline_dates ON dasha_timeline(user_id, start_date, end_date);
CREATE INDEX idx_dasha_timeline_lord ON dasha_timeline(user_id, lord);

-- User preferences indexes
CREATE INDEX idx_user_preferences_user ON user_preferences(user_id);

-- Users indexes
CREATE INDEX idx_users_email ON users(email);

-- ==============================================================================
-- FUNCTIONS AND TRIGGERS
-- ==============================================================================

-- Function for automatic updated_at column updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Trigger for users updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for memories updated_at
CREATE TRIGGER update_memories_updated_at BEFORE UPDATE ON memories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for conversations updated_at
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_preferences updated_at
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================================================
-- VIEWS
-- ==============================================================================

-- View for user complete profile with aggregated statistics
CREATE VIEW user_complete_profile AS
SELECT
    u.id,
    u.email,
    u.name,
    bc.lagna_rashi,
    bc.moon_rashi,
    bc.moon_nakshatra,
    bc.birth_datetime,
    bc.place_name,
    (SELECT COUNT(*) FROM detected_patterns dp WHERE dp.user_id = u.id AND dp.pattern_type = 'yoga') as yoga_count,
    (SELECT COUNT(*) FROM detected_patterns dp WHERE dp.user_id = u.id AND dp.pattern_type = 'dosha') as dosha_count,
    (SELECT COUNT(*) FROM memories m WHERE m.user_id = u.id) as memory_count,
    (SELECT COUNT(*) FROM predictions p WHERE p.user_id = u.id) as prediction_count,
    (SELECT COUNT(*) FROM conversations c WHERE c.user_id = u.id) as conversation_count,
    u.created_at,
    u.updated_at
FROM users u
LEFT JOIN birth_charts bc ON bc.user_id = u.id;

-- ==============================================================================
-- TABLE DOCUMENTATION
-- ==============================================================================

COMMENT ON TABLE users IS 'Core user accounts for the 108 Vedic Astrology App';
COMMENT ON TABLE birth_charts IS 'Birth chart data with calculated planet positions and house cusps';
COMMENT ON TABLE detected_patterns IS 'Detected yogas and doshas from birth chart analysis';
COMMENT ON TABLE memories IS 'Semantic memories with vector embeddings for RAG-based learning';
COMMENT ON TABLE predictions IS 'Astrological predictions made by the system for validation and learning';
COMMENT ON TABLE conversations IS 'Conversation history with embeddings for semantic search';
COMMENT ON TABLE user_preferences IS 'Explicit user preferences and configuration settings';
COMMENT ON TABLE dasha_timeline IS 'Precomputed Vimshottari dasha periods for efficient querying';

-- Column documentation
COMMENT ON COLUMN birth_charts.planets IS 'JSONB object containing all calculated planet positions and details';
COMMENT ON COLUMN birth_charts.houses IS 'JSONB object containing all 12 house cusps and angles';
COMMENT ON COLUMN memories.embedding IS 'pgvector embedding for semantic similarity search (OpenAI 1536-dim)';
COMMENT ON COLUMN memories.category IS 'Memory category: fact, preference, event, prediction, or feedback';
COMMENT ON COLUMN memories.importance IS 'Importance score from 0.0 (least important) to 1.0 (most important)';
COMMENT ON COLUMN predictions.factors IS 'JSONB object with astrological factors contributing to the prediction';
COMMENT ON COLUMN predictions.dasha_period IS 'JSONB object with active dasha/antardasha at time of prediction';
COMMENT ON COLUMN predictions.transit_positions IS 'JSONB object with key transit planet positions at prediction time';
COMMENT ON COLUMN conversations.messages IS 'JSONB array of message objects with role, content, and timestamp';
COMMENT ON COLUMN conversations.embedding IS 'pgvector embedding for conversation similarity search';
COMMENT ON COLUMN dasha_timeline.level IS 'Dasha hierarchy level: maha (main), antar (sub), or pratyantar (sub-sub)';
COMMENT ON COLUMN user_preferences.preference_key IS 'Configuration key (e.g., language, notification_frequency, theme)';
COMMENT ON COLUMN user_preferences.preference_value IS 'JSONB value for the preference key';
