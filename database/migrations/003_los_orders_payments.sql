-- 003_los_orders_payments.sql
-- 108 — Life's Operating System purchase flow
-- Three-gateway-aware (Razorpay / PayU / Cashfree) + report generation lifecycle

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Orders ──
-- One row per customer purchase intent. Created when customer hits /checkout.
CREATE TABLE IF NOT EXISTS los_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    -- Customer identity
    full_name        VARCHAR(255) NOT NULL,
    email            TEXT NOT NULL,
    phone            VARCHAR(20),
    gender           VARCHAR(10),
    -- Birth details
    birth_datetime   TIMESTAMP NOT NULL,
    birth_latitude   DECIMAL(10,6) NOT NULL,
    birth_longitude  DECIMAL(11,6) NOT NULL,
    birth_place_name VARCHAR(255),
    timezone         VARCHAR(64) DEFAULT 'Asia/Kolkata',
    -- Product
    pack_id          VARCHAR(40) NOT NULL,         -- e.g. 'core', 'full', 'super'
    addons           JSONB DEFAULT '[]',            -- e.g. ['career','marriage','foreign']
    user_question    TEXT,                          -- optional single question
    amount_inr       INTEGER NOT NULL,              -- in paise (₹1 = 100)
    currency         CHAR(3) DEFAULT 'INR',
    -- Status lifecycle
    status           VARCHAR(20) DEFAULT 'created'  -- created | paid | generating | ready | delivered | flagged | refunded
        CHECK (status IN ('created','paid','generating','ready','delivered','flagged','refunded','failed')),
    needs_human_review INTEGER DEFAULT 0,
    error_message    TEXT,
    -- Timestamps
    created_at       TIMESTAMP DEFAULT NOW(),
    paid_at          TIMESTAMP,
    generated_at     TIMESTAMP,
    delivered_at     TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_los_orders_email      ON los_orders(email);
CREATE INDEX IF NOT EXISTS idx_los_orders_status     ON los_orders(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_los_orders_created    ON los_orders(created_at DESC);

-- ── Payments ──
-- One row per gateway attempt. An order may have multiple if first fails.
CREATE TABLE IF NOT EXISTS los_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id         UUID NOT NULL REFERENCES los_orders(id) ON DELETE CASCADE,
    gateway          VARCHAR(20) NOT NULL           -- razorpay | payu | cashfree
        CHECK (gateway IN ('razorpay','payu','cashfree','manual')),
    gateway_order_id VARCHAR(255),                  -- gateway-side order/payment-link ID
    gateway_payment_id VARCHAR(255),                -- gateway-side transaction ID
    amount_inr       INTEGER NOT NULL,              -- paise
    currency         CHAR(3) DEFAULT 'INR',
    status           VARCHAR(20) DEFAULT 'initiated' -- initiated | success | failed | cancelled | refunded
        CHECK (status IN ('initiated','success','failed','cancelled','refunded')),
    raw_response     JSONB DEFAULT '{}',            -- full gateway payload (debug + audit)
    failure_reason   TEXT,
    created_at       TIMESTAMP DEFAULT NOW(),
    completed_at     TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_los_payments_order   ON los_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_los_payments_gateway ON los_payments(gateway, gateway_payment_id);

-- ── Generated Reports ──
-- One row per produced PDF. An order can re-generate (e.g. correction) → newer row.
CREATE TABLE IF NOT EXISTS los_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id         UUID NOT NULL REFERENCES los_orders(id) ON DELETE CASCADE,
    version          INTEGER DEFAULT 1,              -- monotonic per order
    -- Pipeline output paths
    markdown_path    TEXT,                          -- where the assembled MD lives
    pdf_path         TEXT,                          -- final PDF path
    public_url       TEXT,                          -- Supabase Storage signed/public URL
    -- Pipeline data
    chart_data       JSONB DEFAULT '{}',
    section_outputs  JSONB DEFAULT '{}',
    stitcher_output  JSONB DEFAULT '{}',
    -- Stats
    page_count       INTEGER,
    file_size_bytes  INTEGER,
    -- Audit
    backend          VARCHAR(20) DEFAULT 'claude_code'  -- claude_code | api
        CHECK (backend IN ('claude_code','api','manual')),
    model_used       VARCHAR(80),
    generated_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_los_reports_order ON los_reports(order_id, version DESC);

-- ── Notification log ──
-- One row per email/SMS sent (for de-duplication + audit)
CREATE TABLE IF NOT EXISTS los_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id         UUID REFERENCES los_orders(id) ON DELETE CASCADE,
    channel          VARCHAR(20) NOT NULL           -- email | sms | whatsapp
        CHECK (channel IN ('email','sms','whatsapp')),
    template         VARCHAR(40),                   -- payment_confirmed | report_ready | refund_initiated
    recipient        TEXT NOT NULL,
    subject          TEXT,
    body             TEXT,
    provider         VARCHAR(20),                   -- smtp | cashfree | razorpay
    provider_msg_id  VARCHAR(255),
    status           VARCHAR(20) DEFAULT 'queued'   -- queued | sent | failed
        CHECK (status IN ('queued','sent','failed','bounced')),
    error_message    TEXT,
    sent_at          TIMESTAMP,
    created_at       TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_los_notifications_order ON los_notifications(order_id, created_at DESC);

-- ── Row-level security: disable for service-role admin operations ──
-- (Mobile app uses anon key with RLS later; admin pipeline uses service_role and bypasses RLS.)
ALTER TABLE los_orders        DISABLE ROW LEVEL SECURITY;
ALTER TABLE los_payments      DISABLE ROW LEVEL SECURITY;
ALTER TABLE los_reports       DISABLE ROW LEVEL SECURITY;
ALTER TABLE los_notifications DISABLE ROW LEVEL SECURITY;
