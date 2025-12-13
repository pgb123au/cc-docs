# Telco Warehouse Database - CRM Integration Handoff

## Overview

A PostgreSQL database containing **74,107 voice calls** and **8 SMS messages** from multiple providers, **optimized for CRM use** with normalized contacts, pre-aggregated stats, and unified communication views.

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

## CRM-Optimized Objects

### New Tables
| Table | Purpose |
|-------|---------|
| `telco.contacts` | Normalized phone numbers with aggregated stats |
| `telco.business_numbers` | Your business phone lines with labels |

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

    -- CRM fields (for your use)
    notes               TEXT,
    tags                VARCHAR[],

    created_at          TIMESTAMPTZ,
    updated_at          TIMESTAMPTZ
);
```

### Sample Contact Data
```
61399997398: 37,540 calls (22,225 answered), business
61288800208:  8,800 calls (2,790 answered), business
61412111000:  1,385 calls (150 answered), 12 SMS, business
61403180200:     29 calls (11 answered), customer
```

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
-- Returns: contact with all aggregated stats
```

### 2. Get Full Communication History for Contact
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

### 3. Get Recent Communications (All Channels)
```sql
SELECT * FROM telco.v_communications
ORDER BY timestamp DESC
LIMIT 100;
```

### 4. Find Customers with Multiple Interactions
```sql
SELECT phone_normalized, phone_display, total_calls,
       answered_calls, total_sms, first_seen, last_seen
FROM telco.contacts
WHERE contact_type = 'customer' AND total_calls > 1
ORDER BY total_calls DESC;
```

### 5. Get Daily Call Stats
```sql
SELECT d.date, p.name as provider, d.total_calls, d.answered,
       d.total_seconds / 60 as minutes
FROM telco.mv_daily_stats d
JOIN telco.providers p ON d.provider_id = p.provider_id
WHERE d.date >= CURRENT_DATE - 30
ORDER BY d.date DESC, d.total_calls DESC;
```

### 6. Customer Summary Statistics
```sql
SELECT * FROM telco.mv_contact_summary;
-- Returns: contact_type, count, total_calls, answered, hours, repeat_contacts
```

### 7. Search by Partial Phone Number
```sql
SELECT * FROM telco.contacts
WHERE phone_normalized LIKE '6141%'
ORDER BY total_calls DESC;
```

### 8. Get Retell AI Calls with Transcripts
```sql
SELECT
    c.external_call_id,
    telco.normalize_phone(c.from_number) as customer,
    c.started_at,
    c.duration_seconds,
    c.retell_agent_name,
    c.transcript,
    c.full_transcript,
    c.raw_data->'call_analysis' as analysis
FROM telco.calls c
WHERE c.provider_id = 3  -- Retell
ORDER BY c.started_at DESC;
```

### 9. Link SMS to Calls (Same Customer)
```sql
-- Get all communications for customers who received SMS
WITH sms_customers AS (
    SELECT DISTINCT telco.normalize_phone(to_number) as phone
    FROM telco.messages
)
SELECT v.*
FROM telco.v_communications v
JOIN sms_customers s ON v.from_phone = s.phone OR v.to_phone = s.phone
ORDER BY v.timestamp DESC;
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
3. **Contact type** - 'business' = your numbers, 'customer' = external numbers
4. **Refresh views** - Run `SELECT telco.refresh_crm_views()` after syncing new data
5. **No API calls needed** - All data is in the database
6. **Timestamps are UTC** - With timezone info (TIMESTAMPTZ)

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
```

---

## Data Freshness

- **Last sync:** 2025-12-14
- **Sync frequency:** Manual (can be automated)
- **Contact stats:** Re-populate by re-running the contacts INSERT query or calling a refresh function
