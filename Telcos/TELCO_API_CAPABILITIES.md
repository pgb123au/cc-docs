# Telco API Capabilities & Data Warehouse Plan

## Current Implementation Status

### Zadarma API

| Endpoint | Data | Currently Pulling | Notes |
|----------|------|:-----------------:|-------|
| `/v1/info/balance/` | Account balance, currency | Yes | Real-time |
| `/v1/direct_numbers/` | Phone numbers, status, SIP routing, fees | Yes | All fields |
| `/v1/sip/` | SIP accounts, display names, caller IDs | Yes | All fields |
| `/v1/statistics/` | Call history (CDR) | **No** | Date range required |
| `/v1/statistics/callback_widget/` | Callback widget stats | No | Widget-specific |
| `/v1/pbx/statistics/` | PBX call statistics | **No** | More detailed than /statistics |
| `/v1/pbx/record/request/` | Call recordings (download) | **No** | Returns audio file URL |
| `/v1/sms/send/` | Send SMS | No | Write operation |
| `/v1/sms/get/` | SMS history | **No** | Inbound/outbound SMS |
| `/v1/pbx/` | PBX configuration | No | IVR/routing setup |
| `/v1/info/price/` | Pricing info | No | Per-destination rates |
| `/v1/webrtc/get_key/` | WebRTC credentials | No | For browser calling |

### Telnyx API

| Endpoint | Data | Currently Pulling | Notes |
|----------|------|:-----------------:|-------|
| `/v2/balance` | Account balance, credit limit | Yes | Real-time |
| `/v2/phone_numbers` | Phone numbers, status, connections | Yes | All fields |
| `/v2/fqdn_connections` | SIP connections | Yes | With FQDN details |
| `/v2/fqdns` | FQDN hostnames | Yes | For SIP routing |
| `/v2/outbound_voice_profiles` | Voice profiles | Yes | Partial |
| `/v2/messaging_profiles` | SMS/MMS profiles | No | For messaging setup |
| `/v2/call_control_applications` | Call control apps | **No** | Webhooks/routing |
| `/v2/calls` | Active calls | **No** | Real-time call state |
| `/v2/recordings` | Call recordings | **No** | Audio files |
| `/v2/cdr_requests` | CDR exports | **No** | Bulk call history |
| `/v2/reports/cdr` | Call detail records | **No** | Filterable call logs |
| `/v2/messages` | SMS/MMS messages | **No** | Message history |
| `/v2/billing` | Billing details | **No** | Invoices, charges |
| `/v2/number_orders` | Number ordering | No | Port/purchase status |
| `/v2/portout_requests` | Port-out requests | No | Number porting |
| `/v2/verify` | Phone verification | No | 2FA service |

### Retell AI API

| Endpoint | Data | Currently Pulling | Notes |
|----------|------|:-----------------:|-------|
| `phone_number.list()` | Phone numbers, agent mappings | Yes | All fields |
| `agent.list()` | Agent list (ID, name, voice) | Yes | Basic fields only |
| `agent.retrieve()` | Full agent config | **No** | Prompts, settings |
| `call.list()` | Call history | **No** | All calls with metadata |
| `call.retrieve()` | Single call details | **No** | Full transcript |
| `call.list_recordings()` | Call recordings | **No** | Audio URLs |
| `llm.list()` | LLM configurations | **No** | Custom LLM setups |
| `voice.list()` | Voice configurations | **No** | Custom voices |
| `webhook.list()` | Webhook endpoints | **No** | Event subscriptions |
| `concurrency.retrieve()` | Concurrency limits | **No** | Usage limits |
| Analytics (dashboard) | Call analytics | **No** | Via web scraping only |

---

## Data to Pull for Warehouse

### Priority 1 - Call History & CDRs

| Provider | Endpoint | Fields to Store |
|----------|----------|-----------------|
| **Zadarma** | `/v1/statistics/` | call_id, from, to, sip, disposition, duration, billsec, cost, calldate, clid |
| **Zadarma** | `/v1/pbx/statistics/` | pbx_call_id, caller_id, called_did, internal_number, wait_time, talk_time, recording_id |
| **Telnyx** | `/v2/reports/cdr` | id, call_leg_id, from, to, direction, duration, cost, start_time, end_time, status |
| **Retell** | `call.list()` | call_id, agent_id, from_number, to_number, direction, duration, status, transcript, created_at |

### Priority 2 - Call Recordings

| Provider | Endpoint | Storage Approach |
|----------|----------|------------------|
| **Zadarma** | `/v1/pbx/record/request/` | Store URL + metadata, optionally download to S3 |
| **Telnyx** | `/v2/recordings` | Store URL + metadata, optionally download to S3 |
| **Retell** | `call.list_recordings()` | Store URL + metadata, optionally download to S3 |

### Priority 3 - Billing & Usage

| Provider | Endpoint | Fields to Store |
|----------|----------|-----------------|
| **Zadarma** | `/v1/info/balance/` | balance, currency, timestamp |
| **Zadarma** | `/v1/statistics/` | Aggregate costs by day/month |
| **Telnyx** | `/v2/balance` | balance, credit_limit, timestamp |
| **Telnyx** | `/v2/billing` | invoice_id, amount, date, items |
| **Retell** | Dashboard | minutes_used, cost (manual or scrape) |

### Priority 4 - SMS/Messaging

| Provider | Endpoint | Fields to Store |
|----------|----------|-----------------|
| **Zadarma** | `/v1/sms/get/` | sms_id, from, to, message, status, timestamp |
| **Telnyx** | `/v2/messages` | id, from, to, text, direction, status, created_at |

---

## PostgreSQL Schema Design

### Database: `telco_warehouse`

Separate from n8n/Reignite data - new database or schema.

```sql
-- Option A: Separate database
CREATE DATABASE telco_warehouse;

-- Option B: Separate schema in existing DB
CREATE SCHEMA telco;
```

### Core Tables

```sql
-- ============================================================================
-- PROVIDERS & NUMBERS (Reference Data)
-- ============================================================================

CREATE TABLE telco.providers (
    provider_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,  -- 'zadarma', 'telnyx', 'retell'
    api_type VARCHAR(20),               -- 'rest', 'sdk'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE telco.phone_numbers (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    phone_number VARCHAR(20) NOT NULL,
    phone_number_e164 VARCHAR(20),      -- Normalized +61XXXXXXXXX
    nickname VARCHAR(100),
    status VARCHAR(20),
    city VARCHAR(50),
    monthly_cost DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    retell_agent_id VARCHAR(50),
    retell_agent_name VARCHAR(100),
    metadata JSONB,                      -- Provider-specific fields
    last_synced TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, phone_number)
);

-- ============================================================================
-- CALL DETAIL RECORDS (CDRs)
-- ============================================================================

CREATE TABLE telco.calls (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    external_call_id VARCHAR(100),       -- Provider's call ID

    -- Call parties
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    direction VARCHAR(10),               -- 'inbound', 'outbound'

    -- Timing
    started_at TIMESTAMPTZ,
    answered_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_seconds INT,                -- Total duration
    billable_seconds INT,                -- Billable duration

    -- Status
    status VARCHAR(30),                  -- 'completed', 'no_answer', 'busy', 'failed'
    disposition VARCHAR(50),             -- Provider-specific status
    hangup_cause VARCHAR(50),

    -- Cost
    cost DECIMAL(10,4),
    currency VARCHAR(3) DEFAULT 'USD',

    -- Retell-specific
    retell_agent_id VARCHAR(50),
    retell_agent_name VARCHAR(100),
    transcript TEXT,
    sentiment VARCHAR(20),

    -- Recording
    has_recording BOOLEAN DEFAULT FALSE,
    recording_url TEXT,
    recording_duration_seconds INT,

    -- Raw data
    raw_data JSONB,                      -- Full API response

    -- Metadata
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(provider_id, external_call_id)
);

CREATE INDEX idx_calls_started_at ON telco.calls(started_at);
CREATE INDEX idx_calls_from_number ON telco.calls(from_number);
CREATE INDEX idx_calls_to_number ON telco.calls(to_number);
CREATE INDEX idx_calls_provider_date ON telco.calls(provider_id, started_at);

-- ============================================================================
-- CALL RECORDINGS
-- ============================================================================

CREATE TABLE telco.recordings (
    id SERIAL PRIMARY KEY,
    call_id INT REFERENCES telco.calls(id),
    provider_id INT REFERENCES telco.providers(provider_id),
    external_recording_id VARCHAR(100),

    recording_url TEXT,
    duration_seconds INT,
    file_size_bytes BIGINT,
    format VARCHAR(10),                  -- 'mp3', 'wav'

    -- Local storage (if downloaded)
    s3_bucket VARCHAR(100),
    s3_key VARCHAR(255),
    local_path VARCHAR(255),

    transcription TEXT,
    transcription_confidence DECIMAL(3,2),

    created_at TIMESTAMPTZ,
    synced_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(provider_id, external_recording_id)
);

-- ============================================================================
-- SMS/MESSAGES
-- ============================================================================

CREATE TABLE telco.messages (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    external_message_id VARCHAR(100),

    from_number VARCHAR(20),
    to_number VARCHAR(20),
    direction VARCHAR(10),               -- 'inbound', 'outbound'

    message_type VARCHAR(10),            -- 'sms', 'mms'
    body TEXT,
    media_urls JSONB,                    -- For MMS

    status VARCHAR(30),
    segments INT,
    cost DECIMAL(10,4),
    currency VARCHAR(3) DEFAULT 'USD',

    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(provider_id, external_message_id)
);

-- ============================================================================
-- BILLING & BALANCE SNAPSHOTS
-- ============================================================================

CREATE TABLE telco.balance_snapshots (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),

    balance DECIMAL(10,2),
    currency VARCHAR(3),
    credit_limit DECIMAL(10,2),

    snapshot_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE telco.billing_items (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),

    invoice_id VARCHAR(50),
    invoice_date DATE,

    item_type VARCHAR(50),               -- 'call', 'number_rental', 'sms', 'recording'
    description TEXT,
    quantity DECIMAL(10,2),
    unit_price DECIMAL(10,4),
    total DECIMAL(10,2),
    currency VARCHAR(3),

    period_start DATE,
    period_end DATE,

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SYNC TRACKING
-- ============================================================================

CREATE TABLE telco.sync_log (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    sync_type VARCHAR(50),               -- 'calls', 'recordings', 'messages', 'billing'

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    records_fetched INT,
    records_inserted INT,
    records_updated INT,

    date_range_start TIMESTAMPTZ,
    date_range_end TIMESTAMPTZ,

    status VARCHAR(20),                  -- 'success', 'failed', 'partial'
    error_message TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- RETELL AGENTS (for reference)
-- ============================================================================

CREATE TABLE telco.retell_agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) UNIQUE,
    agent_name VARCHAR(100),
    voice_id VARCHAR(50),
    language VARCHAR(10),

    -- Stats (updated periodically)
    total_calls INT,
    total_minutes DECIMAL(10,2),
    avg_duration_seconds INT,

    last_synced TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- VIEWS FOR EASY QUERYING
-- ============================================================================

CREATE VIEW telco.daily_call_summary AS
SELECT
    DATE(started_at) as call_date,
    p.name as provider,
    direction,
    COUNT(*) as total_calls,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_calls,
    SUM(duration_seconds) as total_duration,
    SUM(billable_seconds) as total_billable,
    SUM(cost) as total_cost
FROM telco.calls c
JOIN telco.providers p ON c.provider_id = p.provider_id
GROUP BY DATE(started_at), p.name, direction;

CREATE VIEW telco.monthly_cost_summary AS
SELECT
    DATE_TRUNC('month', started_at) as month,
    p.name as provider,
    COUNT(*) as total_calls,
    SUM(cost) as call_costs,
    (SELECT SUM(monthly_cost) FROM telco.phone_numbers WHERE provider_id = c.provider_id) as number_rental
FROM telco.calls c
JOIN telco.providers p ON c.provider_id = p.provider_id
GROUP BY DATE_TRUNC('month', started_at), p.name, c.provider_id;
```

---

## Sync Scripts Architecture

### Folder Structure

```
CC/Telcos/
├── .credentials                    # API keys (git-ignored)
├── telco.py                        # Interactive menu (existing)
├── telco.bat                       # Launcher (existing)
│
├── sync/                           # Data warehouse sync scripts
│   ├── __init__.py
│   ├── config.py                   # DB connection, API setup
│   ├── models.py                   # SQLAlchemy models
│   │
│   ├── sync_calls.py               # Sync CDRs from all providers
│   ├── sync_recordings.py          # Sync recording metadata
│   ├── sync_messages.py            # Sync SMS history
│   ├── sync_billing.py             # Sync billing/balance
│   ├── sync_all.py                 # Master sync script
│   │
│   └── providers/
│       ├── zadarma_sync.py         # Zadarma-specific sync logic
│       ├── telnyx_sync.py          # Telnyx-specific sync logic
│       └── retell_sync.py          # Retell-specific sync logic
│
├── Telnyx/                         # Telnyx-specific scripts
│   └── ...
│
└── Zadarma/                        # Zadarma-specific scripts
    └── ...
```

### Sync Schedule (Recommended)

| Data Type | Frequency | Reason |
|-----------|-----------|--------|
| **Calls/CDRs** | Every 15 mins | Near real-time visibility |
| **Balance** | Every hour | Cost monitoring |
| **Recordings** | Every hour | After calls complete |
| **Messages** | Every 15 mins | If SMS in use |
| **Billing** | Daily | Monthly invoices |
| **Phone Numbers** | Daily | Rarely changes |

### Windows Task Scheduler

```batch
:: Run every 15 minutes
schtasks /create /sc MINUTE /mo 15 /tn "Telco-SyncCalls" /tr "python C:\Users\peter\Downloads\CC\Telcos\sync\sync_calls.py"

:: Run hourly
schtasks /create /sc HOURLY /tn "Telco-SyncBalance" /tr "python C:\Users\peter\Downloads\CC\Telcos\sync\sync_billing.py"

:: Run daily at 2am
schtasks /create /sc DAILY /st 02:00 /tn "Telco-SyncAll" /tr "python C:\Users\peter\Downloads\CC\Telcos\sync\sync_all.py"
```

---

## Implementation Phases

### Phase 1: Database Setup
1. Create `telco` schema in PostgreSQL
2. Run DDL to create all tables
3. Insert provider reference data
4. Test connection from Python

### Phase 2: Call History Sync
1. Implement Zadarma CDR sync (`/v1/statistics/`)
2. Implement Telnyx CDR sync (`/v2/reports/cdr`)
3. Implement Retell call sync (`call.list()`)
4. Test incremental sync (only new records)

### Phase 3: Recording Metadata
1. Sync recording URLs/metadata
2. Optional: Download recordings to S3/local
3. Optional: Transcription integration

### Phase 4: Billing & Analytics
1. Balance snapshot automation
2. Billing item sync
3. Build reporting views
4. Optional: Dashboard integration

### Phase 5: SMS/Messaging
1. Zadarma SMS sync (if used)
2. Telnyx message sync (if used)

---

## PostgreSQL Connection Details

```python
# Add to .credentials:
POSTGRES_HOST=your-ec2-instance.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=telco_warehouse  # or existing DB with 'telco' schema
POSTGRES_USER=telco_sync
POSTGRES_PASSWORD=secure_password
```

---

## Next Steps

1. **Confirm PostgreSQL approach**: New database vs new schema in existing DB?
2. **Confirm storage for recordings**: Keep URLs only, or download to S3?
3. **Confirm sync frequency**: Real-time vs hourly vs daily?
4. **Which phase to start with?**

---

*Last Updated: 2025-12-03*
