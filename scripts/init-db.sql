-- 108 Database Initialization
-- Enable required extensions

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas for organization
CREATE SCHEMA IF NOT EXISTS cosmos;   -- Ephemeris calculations
CREATE SCHEMA IF NOT EXISTS self;     -- User profiles, patterns
CREATE SCHEMA IF NOT EXISTS context;  -- Transits, panchanga
CREATE SCHEMA IF NOT EXISTS memory;   -- Conversation memory

-- Grant permissions
GRANT ALL ON SCHEMA cosmos TO postgres;
GRANT ALL ON SCHEMA self TO postgres;
GRANT ALL ON SCHEMA context TO postgres;
GRANT ALL ON SCHEMA memory TO postgres;
