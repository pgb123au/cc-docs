# Debug Individual Appointment Booking Issues

Create a focused debug package for diagnosing individual appointment booking problems (Physio/EP, not classes).

## IMPORTANT: Diagnosis Only

**This command is for DIAGNOSIS ONLY. DO NOT fix anything.**

Your job is to:
- Gather all evidence
- Run diagnostics
- Analyze the problem
- Document findings

Your job is NOT to:
- Edit any agent files
- Modify any workflows
- Apply any fixes
- Change any code

Produce the evidence package and let the user decide what to do with it.

## Output Folder

**IMPORTANT:** Create a NEW unique folder each time this command runs:
`retell/Testing/[YYYY-MM-DD]-booking-debug-[HHMMSS]/`

Example: `retell/Testing/2025-12-05-booking-debug-143052/`

## File Budget (10 files maximum)

| # | Filename | Purpose |
|---|----------|---------|
| 1 | `call_[id]_full.json` | The problem call - transcript, tool calls, variables, what actually happened |
| 2 | `AGENT_[version].json` | Live production agent - conversation flow nodes, tools, prompts, logic |
| 3 | `LIVE_DIAGNOSTICS.txt` | Real-time system health - DB queries + webhook endpoint tests |
| 4 | `REFERENCE_DOCS.md` | All 5 essential docs: platform ref + JSON schemas + dev guide + whitelist + webhooks |
| 5 | `RetellAI_-_Book_Appointment_Compound_*.json` | n8n booking workflow (original name) |
| 6 | `RetellAI_-_Get_Practitioner_Availability_*.json` | n8n availability workflow (original name) |
| 7 | `RetellAI_-_Check_Funding_Eligibility_*.json` | n8n funding workflow (original name) |
| 8 | `RetellAI_-_Lookup_Caller_by_Phone_*.json` | n8n caller lookup workflow (original name) |
| 9 | `N8N_WORKFLOW_MANIFEST.md` | List of all active n8n workflows with IDs and webhook paths |
| 10 | `DIAGNOSTIC_REPORT.md` | Analysis: root cause, evidence, fix recommendations |

## Execution Steps

### Step 1: Create UNIQUE output folder
```bash
mkdir -p retell/Testing/[YYYY-MM-DD]-booking-debug-[HHMMSS]
```

### Step 2: Download LIVE AGENT from RetellAI API

**CRITICAL:** Always fetch the LIVE agent from the API - never use local files.

```python
from retell import Retell
from pathlib import Path
import json

# Load API key
with open(Path.home() / 'Downloads' / 'Retell_API_Key.txt') as f:
    api_key = f.read().strip()

client = Retell(api_key=api_key)

# Get production agent ID from phone numbers
phones = client.phone_number.list()
agent_id = None
for phone in phones:
    if hasattr(phone, 'inbound_agent_id') and phone.inbound_agent_id:
        agent_id = phone.inbound_agent_id
        break

# Get agent details
agent = client.agent.retrieve(agent_id=agent_id)

# Get conversation flow
cf_id = agent.response_engine.conversation_flow_id
cf = client.conversation_flow.retrieve(cf_id)

# Extract version from agent name
agent_name = agent.agent_name
# Store for later use in manifest

# Combine into exportable format
agent_export = {
    'agent_id': agent.agent_id,
    'agent_name': agent.agent_name,
    'conversationFlow': {
        'conversation_flow_id': cf_id,
        'nodes': [n.__dict__ for n in cf.nodes],
        'tools': [t.__dict__ for t in cf.tools],
        'global_prompt': cf.global_prompt,
        'start_node_id': cf.start_node_id,
        'default_dynamic_variables': cf.default_dynamic_variables
    }
}
```

**Verify file size is >200KB** (small files = missing conversation flow)

Save as: `AGENT_[version].json` (extract version from agent_name)

**STORE THE AGENT VERSION** - you need it for the manifest.

### Step 3: Download call data (1 file)

Use RetellAI SDK:
```python
# Get most recent call (or specific call_id if provided by user)
calls = client.call.list(limit=5)
call_id = calls[0].call_id  # or use provided call_id

# Retrieve full call details
call = client.call.retrieve(call_id)

# Extract key data
call_data = {
    'call_id': call.call_id,
    'agent_id': call.agent_id,
    'agent_name': call.agent_name,
    'call_status': call.call_status,
    'disconnection_reason': call.disconnection_reason,
    'duration_ms': call.duration_ms,
    'start_timestamp': call.start_timestamp,
    'end_timestamp': call.end_timestamp,
    'collected_dynamic_variables': call.collected_dynamic_variables,
    'call_analysis': {
        'call_successful': call.call_analysis.call_successful,
        'call_summary': call.call_analysis.call_summary,
        'user_sentiment': call.call_analysis.user_sentiment
    } if call.call_analysis else None,
    'transcript': call.transcript,
    'transcript_with_tool_calls': [str(t) for t in call.transcript_with_tool_calls] if call.transcript_with_tool_calls else None,
    'tool_calls': call.model_extra.get('tool_calls', []) if hasattr(call, 'model_extra') else [],
    'from_number': call.model_extra.get('from_number') if hasattr(call, 'model_extra') else None,
    'to_number': call.model_extra.get('to_number') if hasattr(call, 'model_extra') else None,
    'public_log_url': call.public_log_url,
    'recording_url': call.recording_url
}
```

Save `call_[id]_full.json` with complete call data.

### Step 4: Download n8n workflows LIVE from API (4 files)

**CRITICAL:** Always fetch workflows from the LIVE n8n API - never use local files.

```python
import requests

N8N_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4'
N8N_URL = 'https://auto.yr.com.au'

headers = {'X-N8N-API-KEY': N8N_API_KEY}

# List ALL workflows
resp = requests.get(f'{N8N_URL}/api/v1/workflows?limit=250', headers=headers)
all_workflows = resp.json().get('data', [])

# Find ACTIVE workflows for each webhook path
# Webhook paths to match (these are the endpoints the agent calls)
required_webhooks = [
    'book-appointment-compound',
    'get-availability',
    'check-funding',
    'lookup-caller-phone'
]

for wf in all_workflows:
    if not wf.get('active'):
        continue
    wf_name = wf.get('name', '')
    wf_id = wf.get('id')

    # Match by webhook path in workflow name
    for webhook_key in required_webhooks:
        if webhook_key.replace('-', '') in wf_name.lower().replace('-', '').replace('_', '').replace(' ', ''):
            # Download full workflow
            detail = requests.get(f'{N8N_URL}/api/v1/workflows/{wf_id}', headers=headers)
            # Save with ORIGINAL name from n8n (do NOT rename)
            # Example: "RetellAI_-_Book_Appointment_Compound_v1.4_MERGE_FIX.json"
            # Record: workflow_id, name, version for manifest
```

**For each workflow, record:**
- Workflow ID
- Full name (includes version)
- Node count
- Whether it has the expected webhook path

### Step 5: Generate N8N_WORKFLOW_MANIFEST.md (1 file)

Create a manifest listing ALL active RetellAI workflows **fetched live from the API**:

```markdown
# n8n Workflow Manifest
Generated: [timestamp]
Agent Version: [from Step 2]

## Active Booking Workflows (Downloaded)

| Workflow ID | Name | Node Count | Webhook Path |
|-------------|------|------------|--------------|
| [id] | [full name with version] | [count] | /webhook/reignite-retell/book-appointment-compound |
| [id] | [full name with version] | [count] | /webhook/reignite-retell/get-availability |
| [id] | [full name with version] | [count] | /webhook/reignite-retell/check-funding |
| [id] | [full name with version] | [count] | /webhook/reignite-retell/lookup-caller-phone |

## All Active RetellAI Workflows

| Workflow ID | Name | Active | Updated At |
|-------------|------|--------|------------|
[List ALL workflows containing "RetellAI" or "reignite-retell" - from API]

## Workflow Health Checks

For each downloaded workflow, verify:
- [ ] Has webhook trigger node with correct path
- [ ] Has response node (respondToWebhook)
- [ ] PostgreSQL nodes have `alwaysOutputData: true`
- [ ] No obvious missing connections

## Version Summary
- Agent: [version from agent_name]
- book-appointment: [version from workflow name]
- get-availability: [version from workflow name]
- check-funding: [version from workflow name]
- lookup-caller: [version from workflow name]
```

### Step 6: Generate Live Diagnostics (1 file)

Create `LIVE_DIAGNOSTICS.txt` with results from database queries and webhook health checks.

#### 6a. Database Queries (via SSH to n8n Postgres)

**Get server IP dynamically or use current:** `52.13.124.171`

```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"[QUERY];\""
```

**Query 1: Recent webhook failures (last 24h)**
```sql
SELECT created_at, webhook_name, success, error_code, duration_ms
FROM webhook_log
WHERE success = false AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC LIMIT 20;
```

**Query 2: Recent call log entries**
```sql
SELECT call_id, from_number, agent_name, intent, outcome, patient_id,
       call_started_at, duration_seconds
FROM call_log
ORDER BY created_at DESC LIMIT 15;
```

**Query 3: Recent individual bookings from appointment_log**
```sql
SELECT appointment_id, patient_id, practitioner_id, appointment_type,
       funding_type, village, call_id, flagged_for_review, created_at
FROM appointment_log
ORDER BY created_at DESC LIMIT 15;
```

**Query 4: This call's webhook logs** (use call_id from Step 3)
```sql
SELECT webhook_name, success, error_code, duration_ms,
       request_body::text, response_body::text, created_at
FROM webhook_log
WHERE call_id = '[CALL_ID]'
ORDER BY created_at ASC;
```

**Query 5: Available slots cache state**
```sql
SELECT village, service_category, COUNT(*) as slot_count,
       MIN(starts_at) as earliest, MAX(starts_at) as latest
FROM individual_slots_cache
WHERE is_available = true AND starts_at > NOW()
GROUP BY village, service_category
ORDER BY village;
```

**Query 6: Safety tables state** (holidays, protected slots)
```sql
SELECT 'holidays' as table_name, COUNT(*) as count FROM safety_holidays
UNION ALL
SELECT 'protected_slots', COUNT(*) FROM safety_protected_slots WHERE is_active = true;
```

#### 6b. Webhook Health Checks (test patient ONLY)

**USE ONLY:** Peter Ball / patient_id: `1805465202989210063` / phone: `0412111000`

Use Python requests (not curl) for reliable Windows execution:

```python
import requests
from datetime import datetime, timedelta

base_url = 'https://auto.yr.com.au/webhook/reignite-retell'
test_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

# Test 1: Lookup caller by phone
resp1 = requests.post(f'{base_url}/lookup-caller-phone',
    json={'args': {'phone': '0412111000', 'call_id': 'debug-test'}})

# Test 2: Get availability WITHOUT date (baseline)
resp2a = requests.post(f'{base_url}/get-availability',
    json={'args': {'village': 'The Baytree', 'service_category': 'physio',
                   'call_id': 'debug-test-no-date'}})

# Test 3: Get availability WITH date (verify date filtering works)
resp2b = requests.post(f'{base_url}/get-availability',
    json={'args': {'village': 'The Baytree', 'service_category': 'physio',
                   'date': test_date, 'call_id': 'debug-test-with-date'}})

# Test 4: Check funding
resp3 = requests.post(f'{base_url}/check-funding',
    json={'args': {'patient_id': '1805465202989210063', 'funding_type': 'HCP',
                   'call_id': 'debug-test'}})

# Record response times, status codes, and key response fields
```

**For get-availability tests, specifically check:**
- Does response include `requested_date` field? (date filtering working)
- Do returned slots respect the date if provided?
- Response time (latency reduction working if <800ms)

#### 6c. Format LIVE_DIAGNOSTICS.txt
```
=== LIVE DIAGNOSTICS ===
Generated: [timestamp]
Call ID: [from step 3]
Agent Version: [from step 2]

--- DATABASE QUERIES ---

[Query 1: Webhook Failures - Last 24h]
[results or "No failures found"]

[Query 2: Recent Call Log Entries]
[results]

[Query 3: Recent Appointment Bookings]
[results or "No bookings found"]

[Query 4: This Call's Webhook Logs]
[results or "No webhook logs for this call"]

[Query 5: Slots Cache Summary]
[results - shows slot availability by village]

[Query 6: Safety Tables State]
[results - holidays and protected slots counts]

--- WEBHOOK HEALTH CHECKS ---

[1. Lookup Caller by Phone]
Endpoint: lookup-caller-phone
Response Time: [X]ms
Status: OK / FAIL
Response: [key fields]

[2a. Get Availability (no date)]
Endpoint: get-availability
Response Time: [X]ms
Status: OK / FAIL
Slots returned: [count]
Has requested_date field: [Yes/No]

[2b. Get Availability (with date)]
Endpoint: get-availability
Date requested: [YYYY-MM-DD]
Response Time: [X]ms
Status: OK / FAIL
Slots returned: [count]
requested_date in response: [value or MISSING]
First slot date: [date] - [PASS if >= requested date, FAIL otherwise]

[3. Check Funding]
Endpoint: check-funding
Response Time: [X]ms
Status: OK / FAIL
Response: [key fields]

[4. Book Appointment Compound]
Status: SKIPPED (destructive test)

--- HEALTH SUMMARY ---
Webhooks responding: X/3
Average response time: [X]ms
Date filtering working: [Yes/No]
DB errors in last 24h: [count]
Webhook failures in last 24h: [count]
Individual slots available: [total count]
Likely issue area: [webhooks/database/agent logic/funding/practitioner_id/slot_unavailable/date_filtering/unknown]
```

### Step 7: Concatenate Reference Docs (1 file)

**IMPORTANT:** Combine ALL 5 ESSENTIAL reference documents into a SINGLE file called `REFERENCE_DOCS.md`.

Read these files IN ORDER and concatenate with section headers:

1. `retell/RETELLAI_REFERENCE.md` - Platform reference (API, events, variables)
2. `retell/RETELLAI_JSON_SCHEMAS.md` - JSON validation rules
3. `retell/AGENT_DEVELOPMENT_GUIDE.md` - Development rules & patterns
4. `retell/WHITELISTED_PATTERNS.md` - Intentional patterns (DO NOT "fix")
5. `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` - Webhook endpoints

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

### Step 8: Generate and SAVE diagnostic report (1 file)

Create `DIAGNOSTIC_REPORT.md` in the output folder:

```markdown
# Diagnostic Report: [Call ID]
Generated: [timestamp]

## File Manifest

| # | File | What It Contains | When To Use It |
|---|------|------------------|----------------|
| 1 | `call_[id]_full.json` | Complete call data | Start here - what happened |
| 2 | `AGENT_[version].json` | Live agent with flow | Check agent logic |
| 3 | `LIVE_DIAGNOSTICS.txt` | DB + webhook tests | System health |
| 4 | `REFERENCE_DOCS.md` | Combined docs | Look up patterns |
| 5 | `RetellAI_-_Book_Appointment_Compound_*.json` | Booking workflow (original name) | Debug booking failures |
| 6 | `RetellAI_-_Get_Practitioner_Availability_*.json` | Availability workflow (original name) | Debug slot issues |
| 7 | `RetellAI_-_Check_Funding_Eligibility_*.json` | Funding workflow (original name) | Debug funding issues |
| 8 | `RetellAI_-_Lookup_Caller_by_Phone_*.json` | Caller lookup (original name) | Debug identification |
| 9 | `N8N_WORKFLOW_MANIFEST.md` | Workflow inventory | Version alignment |
| 10 | `DIAGNOSTIC_REPORT.md` | This file | Summary |

---

## Call Summary
- **Call ID:** [id]
- **Agent Version:** [from live API]
- **Duration:** [X seconds]
- **Outcome:** [call_analysis.call_summary]
- **Disconnection Reason:** [reason]

## Collected Variables (at call end)
```json
[collected_dynamic_variables]
```

## Tool Calls Made
| # | Tool | Latency (ms) | Success | Key Data |
|---|------|--------------|---------|----------|
[Extract from transcript_with_tool_calls]

## Critical Variables at Failure Point
```json
{
  "patient_id": "[value]",
  "village": "[value]",
  "practitioner_id": "[value or MISSING]",
  "starts_at": "[value or MISSING]",
  "funding_type": "[value or MISSING]",
  "error_code": "[value if present]"
}
```

## Live System Health
- Webhooks: [X/3 responding]
- Date filtering: [Working/Not working]
- Avg response time: [X]ms
- DB errors 24h: [count]

## Version Alignment (from live APIs)
- **Agent:** [version from RetellAI API]
- **book-appointment:** [version from n8n API]
- **get-availability:** [version from n8n API]
- **check-funding:** [version from n8n API]
- **lookup-caller:** [version from n8n API]

## Workflow Structure Check
| Workflow | Node Count | Has Webhook | Has Response | Issues |
|----------|------------|-------------|--------------|--------|
| book-appointment | [X] | Yes/No | Yes/No | [any issues] |
| get-availability | [X] | Yes/No | Yes/No | [any issues] |

## Issues Found
1. **[Issue Name]**: [Description with evidence]
2. ...

## Common Failure Patterns Checklist
- [ ] `practitioner_id` missing in book-appointment-compound
- [ ] `starts_at` malformed or doesn't match available slot
- [ ] `SLOT_UNAVAILABLE` error (race condition)
- [ ] `funding_type` not extracted from conversation
- [ ] Date not being respected (deaf agent loop)
- [ ] Webhook timeout or 5xx error
- [ ] Edge loop between nodes

## Root Cause
[Specific analysis based on evidence]

## Fix Recommendations
1. **[Location]**: [What to change]
2. ...
```

### Step 9: Final Validation (MANDATORY)

#### 9a: Verify agent file size (>200KB)
```bash
ls -la [output]/AGENT_v*.json
```
**If <200KB:** DELETE and re-download with conversation flow.

#### 9b: Verify exactly 10 files
```bash
ls -1 [output] | wc -l
```

#### 9c: Final checklist
- [ ] Exactly 10 files
- [ ] Agent file >200KB
- [ ] All workflows downloaded from LIVE n8n API
- [ ] `LIVE_DIAGNOSTICS.txt` has both date-filtered and non-date-filtered availability tests
- [ ] `N8N_WORKFLOW_MANIFEST.md` shows versions from live API
- [ ] No Python scripts in folder
- [ ] No subfolders

### Step 10: Final Output (MANDATORY)

```
[FULL_ABSOLUTE_PATH_TO_OUTPUT_FOLDER]
DONE DONE DONE
```

---

## Quick Reference

### API Endpoints
- **RetellAI:** Use SDK with key from `~/Downloads/Retell_API_Key.txt`
- **n8n API:** `https://auto.yr.com.au/api/v1/workflows`
- **n8n Webhooks:** `https://auto.yr.com.au/webhook/reignite-retell/[endpoint]`
- **PostgreSQL:** SSH to `52.13.124.171` → docker exec n8n-postgres-1

### Test Patient (SAFE TO USE)
- **Name:** Peter Ball
- **Patient ID:** 1805465202989210063
- **Phone:** 0412111000

### Key Webhook Endpoints
| Endpoint | Tool ID |
|----------|---------|
| lookup-caller-phone | tool-lookup-caller-phone |
| get-availability | tool-get-availability |
| check-funding | tool-check-funding |
| book-appointment-compound | tool-book-appointment-compound |

### Key Database Tables
| Table | Purpose |
|-------|---------|
| `webhook_log` | All webhook calls with request/response |
| `individual_slots_cache` | Available appointment slots |
| `safety_holidays` | Blocked dates |
| `safety_protected_slots` | Protected time ranges |

---

*This command always fetches live data from RetellAI and n8n APIs to ensure version accuracy.*
