# Telco Warehouse Database - CRM Integration Handoff

## Overview

A PostgreSQL database containing **74,107 voice calls** and **8 SMS messages** from multiple providers, **optimized for CRM use** with normalized contacts, pre-aggregated stats, unified communication views, and **transcript analysis for DNC/lead classification**.

---

## Connection Details

```
Host:     96.47.238.189
Port:     5432
Database: telco_warehouse
User:     telco_sync
Password: TelcoSync2024!
Schema:   telco
```

### Python Connection
```python
import psycopg2
conn = psycopg2.connect(
    host='96.47.238.189',
    port=5432,
    database='telco_warehouse',
    user='telco_sync',
    password='TelcoSync2024!'
)
```

---

## Data Summary

| Provider | Type | Records | Date Range |
|----------|------|--------:|------------|
| Retell AI | Voice (AI) | 37,715 | 2025-05-16 to 2025-12-13 |
| Zadarma | Voice (SIP) | 35,690 | 2025-05-14 to 2025-12-04 |
| Telnyx | Voice (SIP) | 702 | 2025-12-02 to 2025-12-13 |
| MobileMessage | SMS | 8 | 2025-07-10 to 2025-10-07 |
| **TOTAL** | | **74,115** | |

**Contacts:** 27,882 unique phone numbers (6 business, 27,876 customers)

---

## IMPORTANT: Phone Number Format Differences

**Different providers store phone numbers in different formats:**

| Provider | Format | Example |
|----------|--------|---------|
| **Retell AI** | WITH `+` prefix | `+61412111000` |
| **Zadarma** | WITHOUT `+` prefix | `61412111000` |
| **Telnyx** | WITH `+` prefix | `+61412111000` |

**Always use `telco.normalize_phone()` for lookups** - it strips the `+` prefix and non-digits:

```sql
-- CORRECT: Use normalize_phone() for reliable matching
SELECT * FROM telco.contacts
WHERE phone_normalized = telco.normalize_phone('+61412111000');

-- CORRECT: Search raw calls table
SELECT * FROM telco.calls
WHERE telco.normalize_phone(from_number) = '61412111000'
   OR telco.normalize_phone(to_number) = '61412111000';

-- WRONG: Direct string matching may miss records
SELECT * FROM telco.calls WHERE from_number = '+61412111000';  -- Misses Zadarma calls!
```

---

## CRM-Optimized Objects

### Tables
| Table | Purpose |
|-------|---------|
| `telco.contacts` | Normalized phone numbers with aggregated stats + DNC/lead flags |
| `telco.business_numbers` | Your business phone lines with labels |
| `telco.call_classification` | **NEW:** Per-call transcript classification (taxonomy regex) |
| `telco.call_analysis` | Retell's built-in analysis (sentiment, summary, etc.) |

### Views
| View | Purpose |
|------|---------|
| `telco.v_communications` | Unified timeline of ALL calls + SMS |
| `telco.v_contact_history` | Full communication history per contact |

### Materialized Views (Pre-aggregated)
| Materialized View | Purpose |
|-------------------|---------|
| `telco.mv_daily_stats` | Daily call stats by provider |
| `telco.mv_contact_summary` | Contact statistics by type |

### Functions
| Function | Purpose |
|----------|---------|
| `telco.normalize_phone(phone)` | Strips `+` prefix, removes non-digits |
| `telco.refresh_crm_views()` | Refreshes materialized views |

---

## Key Schema: telco.contacts

**This is your primary CRM lookup table.** Phone numbers are normalized and stats are pre-aggregated.

```sql
CREATE TABLE telco.contacts (
    contact_id          SERIAL PRIMARY KEY,
    phone_normalized    VARCHAR(20) UNIQUE,  -- e.g., '61412111000' (no +)
    phone_display       VARCHAR(25),         -- e.g., '+61412111000'
    contact_type        VARCHAR(20),         -- 'customer' or 'business'

    -- Timeline
    first_seen          TIMESTAMPTZ,
    last_seen           TIMESTAMPTZ,

    -- Aggregated call stats
    total_calls         INTEGER,
    inbound_calls       INTEGER,
    outbound_calls      INTEGER,
    answered_calls      INTEGER,
    missed_calls        INTEGER,
    total_duration_sec  INTEGER,

    -- Provider breakdown
    retell_calls        INTEGER,
    zadarma_calls       INTEGER,
    telnyx_calls        INTEGER,

    -- SMS stats
    total_sms           INTEGER,
    sms_sent            INTEGER,

    -- Last interaction
    last_transcript     TEXT,
    last_disposition    VARCHAR(50),

    -- DNC & Lead Status (from transcript analysis)
    is_dnc              BOOLEAN DEFAULT FALSE,   -- Do Not Call flag
    dnc_reason          VARCHAR(50),             -- 'explicit_request', 'deceased', 'hostile', etc.
    contact_status      VARCHAR(30),             -- 'active', 'retired', 'closed', 'deceased', 'invalid'
    lead_score          SMALLINT,                -- 1-100 lead quality score
    hostile_interactions INTEGER DEFAULT 0,      -- Count of hostile calls

    -- CRM fields (for your use)
    notes               TEXT,
    tags                VARCHAR[],

    created_at          TIMESTAMPTZ,
    updated_at          TIMESTAMPTZ
);
```

### DNC Reasons
| Reason | Description | Action |
|--------|-------------|--------|
| `explicit_request` | Said "stop calling", "remove me from list" | Permanent DNC |
| `deceased` | Contact has passed away | Permanent suppression |
| `hostile` | Profanity, abuse, threats | Block number |
| `legal_threat` | Mentioned lawyers, police, suing | Escalate + DNC |
| `vulnerable` | Confused, elderly, incapacitated | Do not contact |

### Contact Status Values
| Status | Description |
|--------|-------------|
| `active` | Normal contact |
| `retired` | No longer working (B2B) |
| `closed` | Business closed down |
| `deceased` | Person passed away |
| `invalid` | Wrong number, disconnected |
| `vulnerable` | Vulnerable person - do not contact |
| `left_company` | No longer at that company |

---

## Key Schema: telco.call_classification

**Per-call transcript classification using taxonomy regex.** Links to `telco.calls` by `call_id`.

```sql
CREATE TABLE telco.call_classification (
    id                  SERIAL PRIMARY KEY,
    call_id             INTEGER UNIQUE,  -- Links to telco.calls.id

    -- DNC Flags
    is_dnc              BOOLEAN DEFAULT FALSE,
    dnc_reason          VARCHAR(50),

    -- Contact Status
    contact_status      VARCHAR(30) DEFAULT 'active',

    -- Lead Info
    lead_status         VARCHAR(30),    -- 'hot', 'warm', 'cold', 'lost', 'dnc'
    lead_score          SMALLINT,       -- 0-100
    callback_requested  BOOLEAN DEFAULT FALSE,

    -- From Retell (cached from call_analysis)
    retell_sentiment    VARCHAR(20),    -- 'Positive', 'Neutral', 'Negative', 'Unknown'
    retell_summary      TEXT,           -- Retell's call summary
    retell_successful   BOOLEAN,
    retell_voicemail    BOOLEAN,

    -- Flags
    hostile             BOOLEAN DEFAULT FALSE,
    voicemail_full      BOOLEAN DEFAULT FALSE,
    requires_escalation BOOLEAN DEFAULT FALSE,

    -- Raw analysis
    flags_detected      TEXT[],         -- Array of taxonomy flags matched

    -- Metadata
    analysis_method     VARCHAR(20),    -- 'taxonomy_regex', 'llm_gemini', etc.
    analyzed_at         TIMESTAMPTZ DEFAULT NOW()
);
```

## Key Schema: telco.call_analysis (Retell's Built-in)

**Retell's own call analysis.** Links to `telco.calls` by `external_call_id`.

```sql
-- Note: This table stores Retell's native analysis data
-- call_id here is VARCHAR (Retell's external_call_id), not INTEGER
CREATE TABLE telco.call_analysis (
    call_id             VARCHAR PRIMARY KEY,  -- Retell external_call_id
    user_sentiment      VARCHAR(20),          -- 'Positive', 'Neutral', 'Negative', 'Unknown'
    call_summary        TEXT,
    call_successful     BOOLEAN,
    in_voicemail        BOOLEAN,
    custom_analysis_data JSONB
);
```

### Lead Status Values
| Status | Score Range | Description |
|--------|-------------|-------------|
| `hot` | 81-100 | Ready to buy, appointment set |
| `warm` | 61-80 | Interested, callback requested |
| `cold` | 31-60 | Neutral, needs nurturing |
| `lost` | 1-30 | Not interested, hard objection |
| `dnc` | 0 | Do Not Call |

---

## Key Schema: telco.business_numbers

Your business phone lines with metadata.

```sql
CREATE TABLE telco.business_numbers (
    id                  SERIAL PRIMARY KEY,
    phone_normalized    VARCHAR(20) UNIQUE,
    phone_display       VARCHAR(25),
    label               VARCHAR(100),    -- 'Main Sydney Line'
    provider            VARCHAR(50),     -- 'telnyx', 'zadarma'
    number_type         VARCHAR(20),     -- 'inbound', 'outbound', 'both'
    is_active           BOOLEAN,
    notes               TEXT
);
```

### Current Business Numbers
| Number | Label | Provider | Type |
|--------|-------|----------|------|
| 61288800226 | Main Sydney - Retell Inbound | telnyx | inbound |
| 61240620999 | Secondary Sydney | telnyx | inbound |
| 61399997398 | Melbourne - Outbound Campaigns | zadarma | outbound |
| 61399997351 | Melbourne Secondary | zadarma | outbound |
| 61288800208 | Sydney Outbound | telnyx | outbound |
| 61412111000 | Test Mobile | telnyx | both |

---

## CRM Query Examples

### 1. Look Up Contact by Phone Number
```sql
SELECT * FROM telco.contacts
WHERE phone_normalized = telco.normalize_phone('+61 412 111 000');
-- Returns: contact with all aggregated stats + DNC status
```

### 2. Get All DNC Contacts
```sql
SELECT phone_normalized, phone_display, dnc_reason, contact_status,
       total_calls, last_seen
FROM telco.contacts
WHERE is_dnc = TRUE
ORDER BY last_seen DESC;
```

### 3. Get Hot Leads (High Priority Follow-up)
```sql
SELECT c.phone_normalized, c.phone_display, c.lead_score,
       c.total_calls, c.last_seen, cc.retell_summary
FROM telco.contacts c
JOIN telco.call_classification cc ON cc.call_id = (
    SELECT id FROM telco.calls
    WHERE telco.normalize_phone(from_number) = c.phone_normalized
       OR telco.normalize_phone(to_number) = c.phone_normalized
    ORDER BY started_at DESC LIMIT 1
)
WHERE c.lead_score >= 80 AND c.is_dnc = FALSE
ORDER BY c.lead_score DESC;
```

### 4. Get Contacts Needing Callback
```sql
SELECT c.phone_normalized, c.phone_display, cc.retell_summary,
       cl.started_at as last_call
FROM telco.contacts c
JOIN telco.calls cl ON telco.normalize_phone(cl.from_number) = c.phone_normalized
                    OR telco.normalize_phone(cl.to_number) = c.phone_normalized
JOIN telco.call_classification cc ON cc.call_id = cl.id
WHERE cc.callback_requested = TRUE
  AND c.is_dnc = FALSE
ORDER BY cl.started_at DESC;
```

### 5. Get Full Communication History for Contact
```sql
SELECT
    comm_type,           -- 'call' or 'sms'
    provider_name,       -- 'retell', 'zadarma', 'telnyx', 'mobilemessage'
    direction,           -- 'inbound' or 'outbound'
    timestamp,
    duration_seconds,
    status,
    content              -- transcript or SMS body
FROM telco.v_contact_history
WHERE phone_normalized = '61412111000'
ORDER BY timestamp DESC
LIMIT 50;
```

### 6. Get Retired/Closed Business Contacts
```sql
SELECT phone_normalized, phone_display, contact_status,
       total_calls, first_seen, last_seen
FROM telco.contacts
WHERE contact_status IN ('retired', 'closed')
ORDER BY last_seen DESC;
```

### 7. Get Hostile Interaction History
```sql
SELECT c.phone_normalized, c.phone_display, c.hostile_interactions,
       cc.flags_detected, cl.transcript, cl.started_at
FROM telco.contacts c
JOIN telco.calls cl ON telco.normalize_phone(cl.from_number) = c.phone_normalized
                    OR telco.normalize_phone(cl.to_number) = c.phone_normalized
JOIN telco.call_classification cc ON cc.call_id = cl.id
WHERE cc.hostile = TRUE
ORDER BY cl.started_at DESC;
```

### 8. Analysis Statistics Summary
```sql
SELECT
    COUNT(*) as total_analyzed,
    COUNT(*) FILTER (WHERE is_dnc = TRUE) as dnc_count,
    COUNT(*) FILTER (WHERE contact_status = 'retired') as retired,
    COUNT(*) FILTER (WHERE contact_status = 'deceased') as deceased,
    COUNT(*) FILTER (WHERE lead_status = 'hot') as hot_leads,
    COUNT(*) FILTER (WHERE callback_requested = TRUE) as callbacks,
    COUNT(*) FILTER (WHERE hostile = TRUE) as hostile
FROM telco.call_classification;
```

### 9. Get Retell AI Calls with Classification
```sql
SELECT
    c.external_call_id,
    telco.normalize_phone(c.from_number) as customer,
    c.started_at,
    c.duration_seconds,
    c.retell_agent_name,
    cc.lead_status,
    cc.lead_score,
    cc.is_dnc,
    cc.flags_detected,
    cc.retell_summary,
    ca.user_sentiment as retell_native_sentiment
FROM telco.calls c
LEFT JOIN telco.call_classification cc ON cc.call_id = c.id
LEFT JOIN telco.call_analysis ca ON ca.call_id = c.external_call_id
WHERE c.provider_id = 3  -- Retell
ORDER BY c.started_at DESC;
```

### 10. Refresh Aggregated Data
```sql
-- Run after new data is synced
SELECT telco.refresh_crm_views();
```

---

## Phone Number Normalization

**Important:** Always use `telco.normalize_phone()` when querying by phone number to ensure matches regardless of format.

```sql
-- These all return the same contact:
SELECT * FROM telco.contacts WHERE phone_normalized = '61412111000';
SELECT * FROM telco.contacts WHERE phone_normalized = telco.normalize_phone('+61412111000');
SELECT * FROM telco.contacts WHERE phone_normalized = telco.normalize_phone('61 412 111 000');
```

The function:
- Removes `+` prefix
- Removes spaces, dashes, parentheses
- Returns NULL for empty/NULL input

---

## Transcript Analysis

### Classification Taxonomy

Transcripts are analyzed using regex patterns from the **Master Telemarketing Classification Taxonomy** covering:

**Compliance & Legal Risk (Priority 1):**
- DNC Request - Explicit "stop calling" / "remove me"
- DNC Registry Mention - ACMA, TPS, FTC references
- Legal Threat - Lawyer, police, lawsuit mentions
- Vulnerable Customer - Confusion, elderly, distress
- Profanity/Abuse - Hostile language

**List Hygiene (Priority 2):**
- Retired - "I'm retired", "don't work anymore"
- Deceased - "passed away", "no longer with us"
- Out of Business - "closed down", "bankrupt"
- Wrong Number - "no one by that name"
- Minor/Underage - Child answering

**Sales Outcomes:**
- Sale Closed - "sign me up", "let's do it"
- Hard Objection - "not interested", "no thank you"
- Soft Objection/Callback - "call me back", "busy right now"
- Price Objection - "too expensive", "no budget"

**Sentiment:**
- Angry - Frustration indicators
- Positive - Interest, enthusiasm
- Confused - Lack of understanding

### Running Analysis

```bash
cd C:\Users\peter\Downloads\CC\Telcos\analysis

# Analyze all unanalyzed calls
python analyze_transcripts.py

# Analyze with limit
python analyze_transcripts.py --limit 100

# Re-analyze all calls
python analyze_transcripts.py --reanalyze

# Show statistics only
python analyze_transcripts.py --stats

# Test with sample transcripts
python analyze_transcripts.py --test
```

---

## Raw Data Tables

For detailed data beyond aggregates, use the original tables:

### telco.calls (All Voice Calls)
```sql
-- Key columns
id, provider_id, external_call_id, from_number, to_number, direction,
started_at, duration_seconds, disposition, transcript, full_transcript,
retell_agent_id, retell_agent_name, cost, raw_data (JSONB)
```

### telco.messages (All SMS)
```sql
-- Key columns
id, provider_id, external_message_id, from_number, to_number, direction,
body, status, cost, sent_at, raw_data (JSONB)
```

### telco.providers
| provider_id | name | api_type |
|-------------|------|----------|
| 1 | zadarma | rest |
| 2 | telnyx | rest |
| 3 | retell | sdk |
| 4 | mobilemessage | rest |

---

## Notes for CRM Integration

1. **Use contacts table first** - Pre-aggregated stats are much faster than counting calls
2. **Normalize phone numbers** - Always use `telco.normalize_phone()` for lookups
3. **Check DNC before calling** - Always filter `WHERE is_dnc = FALSE`
4. **Contact type** - 'business' = your numbers, 'customer' = external numbers
5. **Refresh views** - Run `SELECT telco.refresh_crm_views()` after syncing new data
6. **No API calls needed** - All data is in the database
7. **Timestamps are UTC** - With timezone info (TIMESTAMPTZ)
8. **Phone format varies** - Retell uses +61, Zadarma uses 61 - always normalize!

---

## Updating Contact Notes/Tags

The CRM can write to the contacts table:

```sql
-- Add notes to a contact
UPDATE telco.contacts
SET notes = 'VIP customer - handle with care',
    tags = ARRAY['vip', 'health-client'],
    updated_at = NOW()
WHERE phone_normalized = '61412111000';

-- Search by tag
SELECT * FROM telco.contacts WHERE 'vip' = ANY(tags);

-- Manually flag as DNC
UPDATE telco.contacts
SET is_dnc = TRUE,
    dnc_reason = 'manual_request',
    updated_at = NOW()
WHERE phone_normalized = '61412111000';
```

---

## File Locations

| File | Purpose |
|------|---------|
| `Telcos/analysis/telemarketing_taxonomy.py` | Classification library with regex patterns |
| `Telcos/analysis/analyze_transcripts.py` | Database analysis script |
| `Telcos/sync/sync_expanded.py` | Main sync script for all providers |
| `Telcos/TELCO_WAREHOUSE_CRM_HANDOFF.md` | This document |

---

## Data Freshness

- **Last sync:** 2025-12-14
- **Last analysis:** Run `python analyze_transcripts.py --stats` to check
- **Sync frequency:** Manual (can be automated via webhook)
- **Contact stats:** Re-populate by re-running the contacts INSERT query or calling a refresh function
