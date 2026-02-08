-- 000_initial_schema.sql
-- Base tables for the 108 Gateway

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_id VARCHAR(255) UNIQUE,
    email TEXT,
    phone VARCHAR(20),
    name VARCHAR(255),
    gender VARCHAR(10),
    avatar_url TEXT,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    birth_datetime TIMESTAMP,
    birth_latitude DECIMAL(10,6),
    birth_longitude DECIMAL(10,6),
    timezone_offset DECIMAL(4,2),
    place_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_auth_id ON users(auth_id);

-- Birth charts (calculated data)
CREATE TABLE IF NOT EXISTS birth_charts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    birth_datetime TIMESTAMP,
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    timezone VARCHAR(10),
    place_name VARCHAR(255),
    lagna_rashi VARCHAR(20),
    moon_rashi VARCHAR(20),
    moon_nakshatra VARCHAR(30),
    planets JSONB DEFAULT '{}',
    houses JSONB DEFAULT '{}',
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Credit wallets
CREATE TABLE IF NOT EXISTS credit_wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    balance INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Credit transactions
CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text',
    metadata JSONB DEFAULT '{}',
    blocks JSONB DEFAULT '[]',
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user ON chat_messages(user_id, created_at DESC);

-- User events
CREATE TABLE IF NOT EXISTS user_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_description TEXT,
    correlation_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Generated reports
CREATE TABLE IF NOT EXISTS generated_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    credit_cost INTEGER DEFAULT 0,
    content JSONB,
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
