-- ╔══════════════════════════════════════════════════════════════════╗
-- ║ 108 — Life's Operating System · v20 Supabase bootstrap            ║
-- ║                                                                    ║
-- ║ Paste this entire file into the Supabase SQL editor                ║
-- ║ (Dashboard → SQL Editor → New Query → paste → Run)                 ║
-- ║                                                                    ║
-- ║ Idempotent — safe to re-run.                                       ║
-- ╚══════════════════════════════════════════════════════════════════╝

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Orders ──
CREATE TABLE IF NOT EXISTS los_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name        VARCHAR(255) NOT NULL,
    email            TEXT NOT NULL,
    phone            VARCHAR(20),
    gender           VARCHAR(10),
    birth_datetime   TIMESTAMP NOT NULL,
    birth_latitude   DECIMAL(10,6) NOT NULL,
    birth_longitude  DECIMAL(11,6) NOT NULL,
    birth_place_name VARCHAR(255),
    timezone         VARCHAR(64) DEFAULT 'Asia/Kolkata',
    pack_id          VARCHAR(40) NOT NULL,
    addons           JSONB DEFAULT '[]',
    user_question    TEXT,
    amount_inr       INTEGER NOT NULL,
    currency         CHAR(3) DEFAULT 'INR',
    status           VARCHAR(20) DEFAULT 'created'
        CHECK (status IN ('created','paid','generating','ready','delivered','flagged','refunded','failed')),
    needs_human_review INTEGER DEFAULT 0,
    error_message    TEXT,
    created_at       TIMESTAMP DEFAULT NOW(),
    paid_at          TIMESTAMP,
    generated_at     TIMESTAMP,
    delivered_at     TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_los_orders_email   ON los_orders(email);
CREATE INDEX IF NOT EXISTS idx_los_orders_status  ON los_orders(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_los_orders_created ON los_orders(created_at DESC);

-- ── Payments ──
CREATE TABLE IF NOT EXISTS los_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id         UUID NOT NULL REFERENCES los_orders(id) ON DELETE CASCADE,
    gateway          VARCHAR(20) NOT NULL
        CHECK (gateway IN ('razorpay','payu','cashfree','manual')),
    gateway_order_id   VARCHAR(255),
    gateway_payment_id VARCHAR(255),
    amount_inr       INTEGER NOT NULL,
    currency         CHAR(3) DEFAULT 'INR',
    status           VARCHAR(20) DEFAULT 'initiated'
        CHECK (status IN ('initiated','success','failed','cancelled','refunded')),
    raw_response     JSONB DEFAULT '{}',
    failure_reason   TEXT,
    created_at       TIMESTAMP DEFAULT NOW(),
    completed_at     TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_los_payments_order   ON los_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_los_payments_gateway ON los_payments(gateway, gateway_payment_id);

-- ── Generated Reports ──
CREATE TABLE IF NOT EXISTS los_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id         UUID NOT NULL REFERENCES los_orders(id) ON DELETE CASCADE,
    version          INTEGER DEFAULT 1,
    markdown_path    TEXT,
    pdf_path         TEXT,
    public_url       TEXT,
    chart_data       JSONB DEFAULT '{}',
    section_outputs  JSONB DEFAULT '{}',
    stitcher_output  JSONB DEFAULT '{}',
    page_count       INTEGER,
    file_size_bytes  INTEGER,
    backend          VARCHAR(20) DEFAULT 'claude_code'
        CHECK (backend IN ('claude_code','api','manual')),
    model_used       VARCHAR(80),
    generated_at     TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_los_reports_order ON los_reports(order_id, version DESC);

-- ── Notifications ──
CREATE TABLE IF NOT EXISTS los_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id         UUID REFERENCES los_orders(id) ON DELETE CASCADE,
    channel          VARCHAR(20) NOT NULL
        CHECK (channel IN ('email','sms','whatsapp')),
    template         VARCHAR(40),
    recipient        TEXT NOT NULL,
    subject          TEXT,
    body             TEXT,
    provider         VARCHAR(20),
    provider_msg_id  VARCHAR(255),
    status           VARCHAR(20) DEFAULT 'queued'
        CHECK (status IN ('queued','sent','failed','bounced')),
    error_message    TEXT,
    sent_at          TIMESTAMP,
    created_at       TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_los_notifications_order ON los_notifications(order_id, created_at DESC);

-- ── Service-role bypass: keep RLS off for these admin tables ──
ALTER TABLE los_orders        DISABLE ROW LEVEL SECURITY;
ALTER TABLE los_payments      DISABLE ROW LEVEL SECURITY;
ALTER TABLE los_reports       DISABLE ROW LEVEL SECURITY;
ALTER TABLE los_notifications DISABLE ROW LEVEL SECURITY;

-- ── Storage bucket for generated PDFs (idempotent) ──
INSERT INTO storage.buckets (id, name, public)
VALUES ('los-reports', 'los-reports', false)
ON CONFLICT (id) DO NOTHING;

-- Done. The Next.js app + admin pipeline will now read/write through these.
