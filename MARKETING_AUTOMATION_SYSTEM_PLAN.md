# AUTOMATED MARKETING SYSTEM - MASTER PLAN

**Created:** 2025-12-12
**Purpose:** Fully automated marketing system leveraging existing infrastructure
**Goal:** Minimal ongoing input, maximum automation

---

## EXECUTIVE SUMMARY

Build a **Claude-powered marketing automation system** that:
1. Accepts XLS/CSV uploads of Victorian mobile/email databases
2. Automatically cleanses, deduplicates, and normalizes data
3. Runs multi-channel campaigns (AI Voice Calls + SMS + Email)
4. Tracks responses, conversions, and ROI automatically
5. Self-optimizes based on results

**Key Insight:** You already have 90% of the infrastructure. What's missing:
- Contact import pipeline
- Campaign orchestration layer
- Marketing-specific AI agent
- Reporting dashboard

---

## PHASE 1: CONTACT IMPORT SYSTEM

### 1.1 Simple Folder-Based Upload

**Location:** `C:\Users\peter\Downloads\CC\MARKETING\imports\`

```
MARKETING/
├── imports/           ← DROP XLS/CSV FILES HERE
│   ├── pending/       ← New files to process
│   ├── processed/     ← Successfully imported
│   └── errors/        ← Files with issues
├── campaigns/         ← Campaign definitions
├── templates/         ← Message templates
└── reports/           ← Auto-generated reports
```

**How It Works:**
1. Drop XLS/CSV files into `imports/pending/`
2. Scheduled n8n workflow scans folder every 5 minutes
3. Auto-detects column mappings (mobile, email, name, etc.)
4. Cleanses and normalizes data
5. Deduplicates against existing contacts
6. Loads into PostgreSQL `marketing_contacts` table
7. Moves file to `processed/` with import summary

### 1.2 Database Schema

```sql
-- New table: marketing_contacts
CREATE TABLE marketing_contacts (
    contact_id BIGSERIAL PRIMARY KEY,

    -- Identity
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),

    -- Contact methods
    mobile VARCHAR(20),
    mobile_normalized VARCHAR(15),  -- +61XXXXXXXXX format
    email VARCHAR(255),
    email_normalized VARCHAR(255),  -- lowercase, trimmed

    -- Australian location
    postcode VARCHAR(4),
    suburb VARCHAR(100),
    state VARCHAR(3),  -- VIC, NSW, etc.

    -- Segmentation
    source_file VARCHAR(255),       -- Original XLS/CSV filename
    source_campaign VARCHAR(100),   -- Which campaign imported from
    tags JSONB DEFAULT '[]',        -- Flexible tagging

    -- Status
    status VARCHAR(20) DEFAULT 'new',  -- new, contacted, interested, converted, do_not_contact
    do_not_call BOOLEAN DEFAULT FALSE,
    do_not_sms BOOLEAN DEFAULT FALSE,
    do_not_email BOOLEAN DEFAULT FALSE,

    -- Tracking
    last_call_at TIMESTAMP,
    last_sms_at TIMESTAMP,
    last_email_at TIMESTAMP,
    total_calls INTEGER DEFAULT 0,
    total_sms INTEGER DEFAULT 0,
    total_emails INTEGER DEFAULT 0,

    -- Conversion
    converted_at TIMESTAMP,
    converted_to VARCHAR(50),  -- 'patient', 'booking', etc.
    cliniko_patient_id BIGINT,  -- Link to patients table if converted

    -- Meta
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    imported_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_mobile UNIQUE (mobile_normalized),
    CONSTRAINT valid_state CHECK (state IN ('VIC', 'NSW', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT'))
);

-- Indexes for fast lookups
CREATE INDEX idx_mc_mobile ON marketing_contacts(mobile_normalized);
CREATE INDEX idx_mc_email ON marketing_contacts(email_normalized);
CREATE INDEX idx_mc_status ON marketing_contacts(status);
CREATE INDEX idx_mc_state ON marketing_contacts(state);
CREATE INDEX idx_mc_postcode ON marketing_contacts(postcode);
CREATE INDEX idx_mc_source ON marketing_contacts(source_file);
CREATE INDEX idx_mc_tags ON marketing_contacts USING GIN(tags);

-- Campaign tracking table
CREATE TABLE marketing_campaigns (
    campaign_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Channel config
    use_voice BOOLEAN DEFAULT FALSE,
    use_sms BOOLEAN DEFAULT FALSE,
    use_email BOOLEAN DEFAULT FALSE,

    -- Targeting
    target_state VARCHAR(3),        -- NULL = all states
    target_postcodes TEXT[],        -- Array of postcodes
    target_tags JSONB,              -- Tag-based targeting

    -- Timing
    start_date DATE,
    end_date DATE,
    call_start_hour INTEGER DEFAULT 9,   -- 9 AM
    call_end_hour INTEGER DEFAULT 17,    -- 5 PM
    max_calls_per_day INTEGER DEFAULT 100,

    -- Templates
    voice_agent_id VARCHAR(50),     -- RetellAI agent for calls
    sms_template TEXT,
    email_subject VARCHAR(200),
    email_template TEXT,

    -- Status
    status VARCHAR(20) DEFAULT 'draft',  -- draft, active, paused, completed

    -- Stats (auto-updated)
    total_contacts INTEGER DEFAULT 0,
    contacts_called INTEGER DEFAULT 0,
    contacts_sms INTEGER DEFAULT 0,
    contacts_emailed INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Campaign execution log
CREATE TABLE campaign_executions (
    execution_id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT REFERENCES marketing_campaigns(campaign_id),
    contact_id BIGINT REFERENCES marketing_contacts(contact_id),

    channel VARCHAR(10),  -- 'voice', 'sms', 'email'
    executed_at TIMESTAMP DEFAULT NOW(),

    -- Results
    status VARCHAR(20),  -- 'success', 'no_answer', 'busy', 'failed', 'delivered', 'bounced'
    duration_seconds INTEGER,  -- For calls
    retell_call_id VARCHAR(100),

    -- Outcome
    interested BOOLEAN,
    callback_requested BOOLEAN,
    do_not_contact BOOLEAN,
    notes TEXT,

    -- Cost tracking
    cost_cents INTEGER DEFAULT 0
);

CREATE INDEX idx_ce_campaign ON campaign_executions(campaign_id);
CREATE INDEX idx_ce_contact ON campaign_executions(contact_id);
CREATE INDEX idx_ce_executed ON campaign_executions(executed_at);
```

### 1.3 Import Workflow (n8n)

**Workflow:** `Marketing - Contact Import v1.0`

```
Trigger: Schedule (every 5 minutes)
    ↓
Scan: /MARKETING/imports/pending/ for XLS/CSV files
    ↓
For each file:
    ↓
Parse: Read XLS/CSV with openpyxl/pandas
    ↓
Map columns: Auto-detect or use header mapping
    ↓
For each row:
    ├── Normalize mobile: +61 format
    ├── Normalize email: lowercase, trim
    ├── Validate: Check format, Australian mobile
    ├── Deduplicate: Check existing in DB
    └── Insert/Update: Upsert to marketing_contacts
    ↓
Move file: → processed/ with summary
    ↓
Email: Import report to peter@yesai.au
```

**Column Auto-Detection:**
- Mobile: `mobile`, `phone`, `cell`, `mobile_number`, `contact_number`
- Email: `email`, `email_address`, `e-mail`
- Name: `name`, `full_name`, `first_name` + `last_name`
- Postcode: `postcode`, `post_code`, `zip`

---

## PHASE 2: CAMPAIGN ORCHESTRATION

### 2.1 Campaign Definition (Simple JSON)

Create campaigns by dropping a JSON file into `campaigns/`:

```json
{
  "name": "VIC Seniors Health Check 2025",
  "description": "Offer free health assessment to Victorian seniors",

  "channels": {
    "voice": true,
    "sms": true,
    "email": false
  },

  "targeting": {
    "state": "VIC",
    "postcodes": ["3000-3999"],
    "exclude_existing_patients": true,
    "exclude_contacted_last_days": 30
  },

  "timing": {
    "start_date": "2025-01-15",
    "call_hours": "9-17",
    "call_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "max_calls_per_day": 50
  },

  "voice": {
    "agent_id": "agent_marketing_health_check_v1",
    "intro_variables": {
      "offer": "complimentary health assessment",
      "clinic_name": "Reignite Health"
    }
  },

  "sms": {
    "template": "Hi {{first_name}}, this is Reignite Health. We're offering a FREE health assessment for Victorian seniors. Reply YES to book or call us on 02 8880 0226.",
    "send_before_call": true,
    "send_after_no_answer": true
  },

  "followup": {
    "no_answer_retry_hours": 24,
    "max_attempts": 3,
    "interested_handoff": "tool-add-to-followup"
  }
}
```

### 2.2 Campaign Execution Engine

**Daily Campaign Runner (n8n workflow):**

```
Trigger: Schedule (Daily 8:30 AM Sydney)
    ↓
Get active campaigns: status = 'active', today between start/end
    ↓
For each campaign:
    ├── Count today's executions
    ├── Calculate remaining capacity
    ├── Query eligible contacts (targeting rules)
    └── Queue contacts for execution
    ↓
Execute Voice Calls:
    ├── Create RetellAI outbound call
    ├── Pass campaign variables
    ├── Log to campaign_executions
    └── Rate limit: 1 call per 30 seconds
    ↓
Send SMS (pre-call or post-no-answer):
    ├── Template substitution
    ├── Send via Mobile Message API
    └── Log to campaign_executions
    ↓
Update Stats:
    └── Refresh campaign totals
```

### 2.3 Sequence Logic

**Multi-Touch Campaign Flow:**

```
Day 1:
  └── SMS: "Hi {{name}}, we're offering free health checks..."

Day 2:
  └── AI Voice Call (if no SMS reply)
      ├── Answered → Run conversation → Log outcome
      └── No Answer → Queue for Day 3

Day 3:
  └── AI Voice Call (retry #1, different time of day)
      └── No Answer → Queue for Day 5

Day 5:
  └── Final SMS: "We tried to reach you..."
      └── Mark as "exhausted" after no response
```

---

## PHASE 3: MARKETING AI VOICE AGENT

### 3.1 Agent Design

**Agent Name:** `Marketing_Outbound_Health_v1.0`

**Personality:**
- Warm, professional, Australian accent
- Quick to get to the point (outbound = limited patience)
- Clear value proposition upfront
- Respect "not interested" immediately

**Conversation Flow:**

```
START
  ↓
"Hi, this is Sarah calling from Reignite Health.
Am I speaking with {{first_name}}?"
  ↓
[Confirm Identity]
  ├── Yes → Continue
  ├── No/Wrong Person → "Sorry to bother you, goodbye"
  └── Who is this? → Brief explanation → Continue
  ↓
"The reason I'm calling is we're offering Victorian
seniors a complimentary health assessment this month.
Would you be interested in learning more?"
  ↓
[Interest Check]
  ├── Yes/Interested → Qualify → Book
  ├── Maybe/Questions → Answer → Re-offer
  ├── No → "No worries at all, have a great day"
  └── Do Not Call → Mark DNC → "I've removed you from our list"
  ↓
[If Interested]
"Great! I can book you in for a free 30-minute
assessment at our {{nearest_village}} clinic.
What day works best for you?"
  ↓
[Book via existing webhook]
  └── tool-book-appointment-compound
  ↓
"You're all set for {{date}} at {{time}}.
We'll send you an SMS confirmation.
Any questions before I let you go?"
  ↓
END
```

### 3.2 Agent Integration Points

**Webhooks to Reuse:**
- `lookup-caller-phone` → Check if already a patient
- `get-availability` → Find appointment slots
- `book-appointment-compound` → Create booking
- `send-sms` → Confirmation text
- `add-to-followup` → Interested but couldn't book now

**New Webhooks Needed:**
- `marketing-log-outcome` → Record call result to campaign_executions
- `marketing-update-contact` → Update contact status (DNC, interested, etc.)

### 3.3 Outbound Call API Integration

**Python Script:** `retell/scripts/marketing_outbound_call.py`

```python
import os
from retell import Retell

client = Retell(api_key=os.environ["RETELL_API_KEY"])

def make_marketing_call(contact, campaign):
    """Initiate outbound marketing call via RetellAI"""

    call = client.call.create_phone_call(
        from_number="+61288800226",  # Main Sydney number
        to_number=contact['mobile_normalized'],
        agent_id=campaign['voice_agent_id'],
        retell_llm_dynamic_variables={
            # Contact info
            "first_name": contact['first_name'],
            "last_name": contact['last_name'],

            # Campaign info
            "campaign_id": str(campaign['campaign_id']),
            "contact_id": str(contact['contact_id']),
            "offer": campaign['offer_description'],

            # Clinic info
            "nearest_village": get_nearest_village(contact['postcode']),
        }
    )

    return call.call_id
```

---

## PHASE 4: SMS & EMAIL AUTOMATION

### 4.1 SMS Templates

**Pre-Call Warm-Up:**
```
Hi {{first_name}}, this is Reignite Health. We'll be calling you
shortly about a free health assessment for Victorian seniors.
If now isn't a good time, reply LATER and we'll call tomorrow.
```

**Post-No-Answer:**
```
Hi {{first_name}}, we tried calling about your free health
assessment. Call us back on 02 8880 0226 or reply BOOK to
schedule at your convenience.
```

**Post-Interest:**
```
Thanks for chatting {{first_name}}! Your FREE health assessment
is booked for {{date}} at {{time}} at {{village}}.
Reply CHANGE to reschedule.
```

**DNC Confirmation:**
```
You've been removed from our call list as requested.
If you change your mind, call 02 8880 0226. - Reignite Health
```

### 4.2 SMS Handling (Inbound Replies)

**New Capability Needed:** Inbound SMS webhook

**Mobile Message API** supports inbound SMS forwarding:
- Configure webhook URL in Mobile Message dashboard
- n8n receives SMS replies
- Auto-route based on keywords:
  - `YES/BOOK` → Add to callback queue
  - `STOP/REMOVE/DNC` → Mark do_not_contact
  - `LATER` → Reschedule call attempt
  - Other → Forward to staff for manual review

### 4.3 Email Campaigns (Optional)

**Integration:** Already have Gmail OAuth2

**Template System:**
```
Subject: Free Health Assessment for Victorian Seniors

Hi {{first_name}},

I wanted to reach out personally about a special offer
we're running for Victorian seniors...

[HTML email with branding]
```

**Tracking:**
- Use unique tracking pixels
- Click tracking via redirects
- Unsubscribe link (mandatory)

---

## PHASE 5: REPORTING & OPTIMIZATION

### 5.1 Automated Daily Report

**Email to:** `peter@yesai.au`
**Time:** 6 PM daily (after calling hours)

```
📊 MARKETING CAMPAIGN DAILY REPORT - {{date}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMPAIGN: VIC Seniors Health Check 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TODAY'S ACTIVITY:
• Calls Made: 47
• Calls Answered: 31 (66%)
• Interested: 12 (39% of answered)
• Bookings Made: 8
• Do Not Call Requests: 3

SMS ACTIVITY:
• Sent: 52
• Replies Received: 7
• BOOK Requests: 4

CUMULATIVE (Campaign to Date):
• Total Contacts: 2,847
• Contacted: 412 (14%)
• Converted: 67 (2.4% overall, 16% of contacted)
• Remaining: 2,435

COST TODAY: $23.50 (calls) + $5.20 (SMS) = $28.70
COST PER BOOKING: $3.59

TOP PERFORMING:
• Best time: 10-11 AM (42% answer rate)
• Best postcode: 3000 (Melbourne CBD)
• Worst time: 4-5 PM (18% answer rate)

⚠️ ATTENTION NEEDED:
• 3 contacts requested callback (see follow-up queue)
• 1 complaint logged (details attached)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.2 Self-Optimization (Claude-Powered)

**Weekly Analysis Task:**

Claude reviews campaign data and suggests optimizations:
- Best calling times
- Message template A/B test results
- Postcode/suburb performance
- Agent script improvements

**Auto-Adjustments:**
- Shift call times to high-answer windows
- Pause low-performing postcodes
- Increase volume to high-converting segments

### 5.3 Compliance Reporting

**Monthly Compliance Report:**
- DNC list additions
- Complaint log
- Call recordings audit sample
- Consent documentation

---

## PHASE 6: FULL AUTOMATION ARCHITECTURE

### 6.1 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MARKETING AUTOMATION SYSTEM                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   IMPORT     │    │   CAMPAIGN   │    │   EXECUTE    │       │
│  │              │    │              │    │              │       │
│  │ • XLS/CSV    │───▶│ • Targeting  │───▶│ • Voice Call │       │
│  │ • Dedupe     │    │ • Scheduling │    │ • SMS Send   │       │
│  │ • Normalize  │    │ • Templates  │    │ • Email Send │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     PostgreSQL                           │    │
│  │  marketing_contacts │ marketing_campaigns │ executions   │    │
│  └─────────────────────────────────────────────────────────┘    │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   TRACK      │    │   ANALYZE    │    │   REPORT     │       │
│  │              │    │              │    │              │       │
│  │ • Outcomes   │◀──▶│ • Claude AI  │───▶│ • Daily      │       │
│  │ • Replies    │    │ • Optimize   │    │ • Weekly     │       │
│  │ • Converts   │    │ • A/B Test   │    │ • Compliance │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

EXTERNAL INTEGRATIONS:
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  RetellAI   │   Mobile    │   Gmail     │   Cliniko   │
│  (Voice)    │   Message   │   (Email)   │  (Convert)  │
│             │   (SMS)     │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### 6.2 Automation Schedule

| Time | Action | Frequency |
|------|--------|-----------|
| Every 5 min | Scan import folder | Continuous |
| 8:30 AM | Load daily call queue | Daily |
| 9:00 AM - 5:00 PM | Execute outbound calls | Business hours |
| 6:00 PM | Generate daily report | Daily |
| Sunday 8:00 AM | Weekly optimization analysis | Weekly |
| 1st of month | Compliance report | Monthly |

### 6.3 Minimal Human Input Required

**What You Do:**
1. Drop XLS/CSV files into `imports/pending/`
2. Review daily email reports
3. Approve weekly optimization suggestions (optional)

**What System Does Automatically:**
- Import and cleanse contact data
- Run campaigns on schedule
- Make AI voice calls
- Send SMS messages
- Track all outcomes
- Generate reports
- Self-optimize timing and targeting

---

## IMPLEMENTATION ROADMAP

### Week 1: Database & Import
- [ ] Create database tables (SQL above)
- [ ] Build import workflow (n8n)
- [ ] Test with sample XLS file
- [ ] Phone number normalization

### Week 2: Campaign Engine
- [ ] Campaign management tables
- [ ] Daily execution workflow
- [ ] Rate limiting logic
- [ ] Basic reporting

### Week 3: Voice Agent
- [ ] Create marketing agent (RetellAI)
- [ ] Outbound call script
- [ ] Webhook integrations
- [ ] Test with Peter Ball

### Week 4: SMS Integration
- [ ] SMS templates
- [ ] Inbound reply handling
- [ ] DNC automation
- [ ] Delivery tracking

### Week 5: Reporting & Polish
- [ ] Daily report workflow
- [ ] Weekly analysis
- [ ] Compliance features
- [ ] Documentation

### Week 6: Launch
- [ ] Pilot with small list (100 contacts)
- [ ] Monitor and adjust
- [ ] Scale to full database

---

## COST ESTIMATES

### Per Campaign (1,000 contacts)

| Item | Unit Cost | Quantity | Total |
|------|-----------|----------|-------|
| Voice calls (answered) | $0.50/min avg | 500 calls × 2 min | $500 |
| Voice calls (no answer) | $0.10/attempt | 500 attempts | $50 |
| SMS sent | $0.08/msg | 1,500 msgs | $120 |
| SMS received | $0.05/msg | 200 msgs | $10 |
| **Total** | | | **~$680** |

**Cost per conversion** (assuming 5% conversion): ~$13.60

### Monthly Infrastructure

| Item | Cost |
|------|------|
| n8n server (existing) | $0 |
| PostgreSQL (existing) | $0 |
| Phone numbers (existing) | ~$25 |
| RetellAI subscription | Usage-based |
| **Additional cost** | **$0** |

---

## COMPLIANCE CONSIDERATIONS

### Australian Regulations

1. **Do Not Call Register (DNCR)**
   - Must check numbers against DNCR before calling
   - API available: https://www.donotcall.gov.au/
   - Penalty: Up to $2.5M for corporations

2. **Spam Act 2003**
   - SMS/email requires consent or existing relationship
   - Must include sender ID and opt-out
   - Penalty: Up to $2.22M per day

3. **Privacy Act**
   - Collect only necessary data
   - Secure storage
   - Provide access on request

### System Safeguards

- [x] DNC flag in contact record
- [x] Automatic DNC on "STOP" keyword
- [x] Call recording consent announcement
- [x] Unsubscribe in all messages
- [ ] DNCR integration (to implement)
- [ ] Consent timestamp logging

---

## FILES TO CREATE

| File | Location | Purpose |
|------|----------|---------|
| `001_marketing_tables.sql` | `n8n/migrations/` | Database schema |
| `Marketing_Import_v1.0.json` | `n8n/JSON/active_workflows/` | Import workflow |
| `Marketing_Campaign_Runner_v1.0.json` | `n8n/JSON/active_workflows/` | Daily execution |
| `Marketing_Daily_Report_v1.0.json` | `n8n/JSON/active_workflows/` | Reporting |
| `marketing_outbound_call.py` | `retell/scripts/` | API wrapper |
| `Marketing_Outbound_Health_v1.0.json` | `retell/agents/` | Voice agent |
| `MARKETING_GUIDE.md` | `CC/` | User documentation |

---

## QUICK START GUIDE

Once implemented, here's how to run a campaign:

### 1. Import Contacts
```bash
# Simply drop your XLS/CSV file here:
C:\Users\peter\Downloads\CC\MARKETING\imports\pending\my_contacts.xlsx
```

### 2. Create Campaign
```bash
# Drop campaign config here:
C:\Users\peter\Downloads\CC\MARKETING\campaigns\vic_health_check.json
```

### 3. Activate Campaign
```sql
UPDATE marketing_campaigns
SET status = 'active'
WHERE name = 'VIC Seniors Health Check 2025';
```

### 4. Monitor
- Check daily email reports
- View real-time stats in database
- Adjust as needed

---

## NEXT STEPS

**To proceed, I need your approval on:**

1. **Database schema** - Create the tables as designed?
2. **Import workflow** - Build the XLS/CSV import system?
3. **Marketing agent** - Create outbound voice agent variant?
4. **SMS integration** - Set up inbound SMS handling?
5. **Compliance** - Add DNCR checking integration?

**Questions for you:**

1. What's your typical XLS/CSV format? (Can you share a sample header row?)
2. Primary offer/service for first campaign?
3. Volume expectations? (calls per day)
4. Any existing DNCR checking process?

---

*This plan leverages your existing n8n, RetellAI, Mobile Message, and PostgreSQL infrastructure. New development focuses on campaign orchestration and marketing-specific workflows.*
