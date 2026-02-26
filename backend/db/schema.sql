-- ============================================================
-- B2B Leads Table — Docker/PostgreSQL edition
-- Run on startup via backend/main.py -> init_db()
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS b2b_leads (
    -- Primary Key
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Company Info
    company_name        TEXT            NOT NULL,
    website_url         TEXT            NOT NULL UNIQUE,

    -- Contact Info
    decision_maker_name TEXT,
    verified_email      TEXT,
    whatsapp_number     TEXT,

    -- AI-Generated Content
    company_context     TEXT,           -- Miner Agent: scraped company summary
    icebreaker_text     TEXT,           -- Writer Agent: personalised opener

    -- Status Machine
    -- Values: Scouted | Mined | Drafted | Approved | Emailed | WhatsApped | Meeting_Booked | Nurture | Blacklisted | Converted | Rejected
    lead_status         TEXT            NOT NULL DEFAULT 'Scouted',

    -- Human-in-the-Loop Flag
    is_approved         BOOLEAN         NOT NULL DEFAULT FALSE,

    -- Outreach tracking
    last_contact_date   TIMESTAMPTZ,
    daily_send_count    INTEGER         NOT NULL DEFAULT 0,
    blacklisted         BOOLEAN         NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_updated_at ON b2b_leads;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON b2b_leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Indexes
CREATE INDEX IF NOT EXISTS idx_b2b_leads_lead_status  ON b2b_leads (lead_status);
CREATE INDEX IF NOT EXISTS idx_b2b_leads_is_approved  ON b2b_leads (is_approved);
CREATE INDEX IF NOT EXISTS idx_b2b_leads_blacklisted  ON b2b_leads (blacklisted);
CREATE INDEX IF NOT EXISTS idx_b2b_leads_created_at   ON b2b_leads (created_at DESC);
