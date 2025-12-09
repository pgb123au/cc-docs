# Debug Combined Booking Flow (Individual + Class)

Create a comprehensive debug package for diagnosing BOTH individual appointment AND class booking issues from a single call.

**Output:** 3 folders with no duplicate files + GEMINI subfolders in each.

## CRITICAL: Always Fetch Fresh Data

**This command MUST fetch live data from servers every time it runs:**
- Fetch live agent from RetellAI API (not from local files)
- Fetch workflows from n8n API (not from local downloads folder)
- Query live database state via SSH
- Test webhooks against production endpoints

**Never use cached/local copies of server data.**

## IMPORTANT: Diagnosis Only

**This command is for DIAGNOSIS ONLY. DO NOT fix anything.**

## Output Folder Structure

Create: `retell/Testing/[YYYY-MM-DD]-combined-debug-[HHMMSS]/`

```
[YYYY-MM-DD]-combined-debug-[HHMMSS]/
├── SHARED/                          # Files used by both debug types
│   ├── agent_[version]_LIVE.json    # Live agent (>200KB)
│   ├── call_[id]_full.json          # Full call data
│   ├── REFERENCE_DOCS.md            # All 5 essential docs concatenated
│   └── GEMINI/                      # Empty subfolder
│
├── individual-booking-debug/        # Individual appointment workflows
│   ├── RetellAI_-_Book_Appointment_Compound_*.json
│   ├── RetellAI_-_Get_Practitioner_Availability_*.json
│   ├── RetellAI_-_Create_or_Get_Patient_*.json
│   ├── RetellAI_-_Lookup_Caller_by_Phone_*.json      # (also used by class)
│   ├── RetellAI_-_Check_Funding_Eligibility_*.json   # (also used by class)
│   ├── LIVE_DIAGNOSTICS.txt
│   ├── DIAGNOSTIC_SUMMARY.md
│   └── GEMINI/                      # Empty subfolder
│
└── class-booking-debug/             # Class booking workflows
    ├── RetellAI_-_Enroll_Class_Single_*.json
    ├── RetellAI_-_Get_Class_Schedule_*.json
    ├── RetellAI_-_Lookup_Caller_by_Phone_*.json      # (also used by individual)
    ├── RetellAI_-_Check_Funding_Eligibility_*.json   # (also used by individual)
    ├── LIVE_DIAGNOSTICS.txt
    ├── DIAGNOSTIC_SUMMARY.md
    └── GEMINI/                      # Empty subfolder
```

**Note:** Lookup and Check Funding workflows appear in BOTH debug folders (they're used by both flows). Agent and call data are in SHARED only.

## Execution Steps

### Step 1: Create folder structure

```bash
mkdir -p "retell/Testing/[YYYY-MM-DD]-combined-debug-[HHMMSS]/SHARED/GEMINI"
mkdir -p "retell/Testing/[YYYY-MM-DD]-combined-debug-[HHMMSS]/individual-booking-debug/GEMINI"
mkdir -p "retell/Testing/[YYYY-MM-DD]-combined-debug-[HHMMSS]/class-booking-debug/GEMINI"
```

### Step 2: Fetch live agent from RetellAI API

**MUST fetch from API - do not use local files.**

```python
from retell import Retell
import json

# Load API key from C:\Users\peter\Downloads\Retell_API_Key.txt
client = Retell(api_key=api_key)

# Get production agent from phone number
numbers = client.phone_number.list()
for n in numbers:
    if hasattr(n, 'inbound_agent_id') and n.inbound_agent_id:
        agent_id = n.inbound_agent_id
        break

# Get agent details
agent = client.agent.retrieve(agent_id=agent_id)

# Get conversation flow
cf_id = agent.response_engine.conversation_flow_id
flow = client.conversation_flow.retrieve(cf_id)

# Combine into single export with full conversation flow
# Save to SHARED folder
```

**VERIFY file size is >200KB** (small files = missing conversation flow)

Save as: `SHARED/agent_[version]_LIVE.json`

### Step 3: Fetch call data

Get the most recent call (or specific call_id if provided):

```python
# Get most recent call or use provided call_id
calls = client.call.list(limit=5)
call_id = calls[0].call_id  # or use provided call_id

call = client.call.retrieve(call_id)
# Save full call data to SHARED folder
```

Save as: `SHARED/call_[call_id]_full.json`

### Step 4: Create REFERENCE_DOCS.md in SHARED (all 5 essential docs)

**IMPORTANT:** Combine ALL 5 ESSENTIAL reference documents into a SINGLE file.

Read these files IN ORDER and concatenate with section headers:

1. `retell/RETELLAI_REFERENCE.md` - Platform reference (API, events, variables)
2. `retell/RETELLAI_JSON_SCHEMAS.md` - JSON validation rules
3. `retell/AGENT_DEVELOPMENT_GUIDE.md` - Development rules & patterns
4. `retell/WHITELISTED_PATTERNS.md` - Intentional patterns (DO NOT "fix")
5. `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` - Webhook endpoints

Save as: `[output]/SHARED/REFERENCE_DOCS.md`

Structure:
```markdown
# Reference Documentation (5 Essential Docs)
Generated: [timestamp]
Agent Version: [from Step 2]

---

## TABLE OF CONTENTS
1. RetellAI Platform Reference
2. RetellAI JSON Schemas
3. Agent Development Guide
4. Whitelisted Patterns (Do Not Fix)
5. Webhook API Reference

---

# SECTION 1: RetellAI Platform Reference
Source: retell/RETELLAI_REFERENCE.md

[FULL CONTENTS]

---

# SECTION 2: RetellAI JSON Schemas
Source: retell/RETELLAI_JSON_SCHEMAS.md

[FULL CONTENTS]

---

# SECTION 3: Agent Development Guide
Source: retell/AGENT_DEVELOPMENT_GUIDE.md

[FULL CONTENTS]

---

# SECTION 4: Whitelisted Patterns (Do Not Fix)
Source: retell/WHITELISTED_PATTERNS.md

[FULL CONTENTS]

---

# SECTION 5: Webhook API Reference
Source: n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md

[FULL CONTENTS]

---
END OF REFERENCE DOCUMENTATION
```

### Step 5: Download n8n workflows from API

**MUST fetch from n8n API - do not use local download folders.**

#### n8n API Configuration
```
N8N_URL: https://auto.yr.com.au
N8N_API_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4
```

#### List all workflows
```bash
curl -s "https://auto.yr.com.au/api/v1/workflows?limit=250" \
  -H "X-N8N-API-KEY: [API_KEY]"
```

#### Find workflows by WEBHOOK PATH (not by name)

For each webhook path, find the workflow that:
1. Is **ACTIVE** (not disabled)
2. Has a webhook trigger node with the **matching path**
3. Has the **HIGHEST version number** if multiple exist

| Webhook Path | Folder(s) to Save To |
|--------------|----------------------|
| `/webhook/reignite-retell/book-appointment-compound` | individual-booking-debug |
| `/webhook/reignite-retell/get-availability` | individual-booking-debug |
| `/webhook/reignite-retell/create-new-client` | individual-booking-debug |
| `/webhook/reignite-retell/enroll-class-single` | class-booking-debug |
| `/webhook/reignite-retell/get-class-schedule` | class-booking-debug |
| `/webhook/reignite-retell/lookup-caller-phone` | **BOTH** folders |
| `/webhook/reignite-retell/check-funding` | **BOTH** folders |

#### Download and save with ORIGINAL FILENAME

**IMPORTANT:** Save workflows with their ORIGINAL name from n8n. Do NOT rename files.

```bash
curl -s "https://auto.yr.com.au/api/v1/workflows/{WORKFLOW_ID}" \
  -H "X-N8N-API-KEY: [API_KEY]" \
  > "[folder]/{WORKFLOW_NAME}.json"
```

### Step 6: Run webhook health tests

Test against production endpoints using test patient only.

**USE ONLY:** Peter Ball / patient_id: `1805465202989210063` / phone: `0412111000`

#### Individual Booking Tests:
1. `lookup-caller-phone` - POST with phone_number
2. `check-funding` - POST with patient_id, funding_type
3. `get-availability` - POST with village, service_category, date (14+ days out)
4. `book-appointment-compound` - SKIP (destructive)
5. `create-new-client` - SKIP (would create duplicate)

#### Class Booking Tests:
1. `get-class-schedule` - POST with class_type, village
2. `enroll-class-single` - SKIP (destructive)

Record status, response time, and response snippet for each.

### Step 7: Query database state via SSH

```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"[QUERY];\""
```

**If SSH times out, document that and continue.**

#### Queries to run:
1. Recent webhook failures (last 24h)
2. Patient funding cache for test patient
3. Webhook logs for the specific call_id
4. Recent webhook log entries

### Step 8: Generate LIVE_DIAGNOSTICS.txt for each folder

Create `individual-booking-debug/LIVE_DIAGNOSTICS.txt`:
- Webhook test results for individual booking endpoints
- Database query results relevant to individual bookings
- Health summary

Create `class-booking-debug/LIVE_DIAGNOSTICS.txt`:
- Webhook test results for class booking endpoints
- Database query results relevant to class bookings
- Health summary

### Step 9: Generate DIAGNOSTIC_SUMMARY.md for each folder

Create `individual-booking-debug/DIAGNOSTIC_SUMMARY.md`:
- File manifest (list workflows in this folder)
- Reference to SHARED folder for agent/call/webhooks docs
- Webhook health table
- Issues found specific to individual booking
- Recommendations (DO NOT IMPLEMENT)

Create `class-booking-debug/DIAGNOSTIC_SUMMARY.md`:
- File manifest (list workflows in this folder)
- Reference to SHARED folder for agent/call/webhooks docs
- Webhook health table
- Issues found specific to class booking
- Recommendations (DO NOT IMPLEMENT)

### Step 10: Validate output

#### 10a: Verify agent file size
```bash
ls -la [output]/SHARED/agent_*.json
# Must be >200KB
```

#### 10b: Verify GEMINI folders exist
```bash
ls -d [output]/*/GEMINI
# Should show 3 GEMINI folders
```

#### 10c: Verify no duplicate agent/call/docs files
- Agent file ONLY in SHARED
- Call file ONLY in SHARED
- REFERENCE_DOCS.md ONLY in SHARED (contains all 5 essential docs)

#### 10d: Verify workflow distribution
- Individual-only workflows in individual-booking-debug
- Class-only workflows in class-booking-debug
- Shared workflows (lookup, check-funding) in BOTH folders

### Step 11: Final output (MANDATORY)

**Print ONLY this single text block - nothing else before or after:**

```
[FULL_PATH]/SHARED
[FULL_PATH]/SHARED/GEMINI
[FULL_PATH]/individual-booking-debug
[FULL_PATH]/individual-booking-debug/GEMINI
[FULL_PATH]/class-booking-debug
[FULL_PATH]/class-booking-debug/GEMINI
```

**Example (copy-paste ready):**
```
C:\Users\peter\Downloads\CC\retell\Testing\2025-12-06-combined-debug-143052\SHARED
C:\Users\peter\Downloads\CC\retell\Testing\2025-12-06-combined-debug-143052\SHARED\GEMINI
C:\Users\peter\Downloads\CC\retell\Testing\2025-12-06-combined-debug-143052\individual-booking-debug
C:\Users\peter\Downloads\CC\retell\Testing\2025-12-06-combined-debug-143052\individual-booking-debug\GEMINI
C:\Users\peter\Downloads\CC\retell\Testing\2025-12-06-combined-debug-143052\class-booking-debug
C:\Users\peter\Downloads\CC\retell\Testing\2025-12-06-combined-debug-143052\class-booking-debug\GEMINI
```

**IMPORTANT:** This must be the ONLY output at the end. No "DONE DONE DONE", no file lists, no extra text. Just the six folder paths.

---

## Quick Reference

### Production Info
- **Phone Numbers:** +61288800226, +61240620999
- **Server IP:** 52.13.124.171

### Test Patient (SAFE TO USE)
- **Name:** Peter Ball
- **Patient ID:** 1805465202989210063
- **Phone:** 0412111000

### Webhook Paths by Booking Type

| Individual Booking | Class Booking | Shared |
|--------------------|---------------|--------|
| book-appointment-compound | enroll-class-single | lookup-caller-phone |
| get-availability | get-class-schedule | check-funding |
| create-new-client | | |

---

*Last Updated: 2025-12-06*
