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

| # | Filename | Source | Why Essential |
|---|----------|--------|---------------|
| 1 | `call_[id]_full.json` | RetellAI API | THE problem - what actually happened |
| 2 | `Reignite_*_vX.XX_*.json` | RetellAI API | THE code - flow logic, tools, nodes |
| 3 | `LIVE_DIAGNOSTICS.txt` | Generated | Live DB queries + webhook health checks |
| 4 | `RETELLAI_JSON_SCHEMAS.md` | Copy from retell/ | Validation rules, correct patterns |
| 5 | `AGENT_DEVELOPMENT_GUIDE.md` | Copy from retell/ | 5 critical rules, variable binding |
| 6 | `BOOKING_FLOW_TROUBLESHOOTING.md` | Copy from retell/guides/ | Booking failures, edge loops, practitioner_id |
| 7 | `wf_book_appointment_compound.json` | n8n API | Core booking workflow |
| 8 | `wf_get_availability.json` | n8n API | Availability lookup workflow |
| 9 | `WEBHOOKS_REFERENCE.md` | Copy from n8n/Webhooks Docs/ | API contracts |
| 10 | `DIAGNOSTIC_REPORT.md` | Generated | Analysis and fix recommendations |

## Execution Steps

### Step 1: Create UNIQUE output folder
```bash
mkdir -p retell/Testing/[YYYY-MM-DD]-booking-debug-[HHMMSS]
```

### Step 2: Download call data (1 file)
Use RetellAI SDK:
```python
from retell import Retell
import json

client = Retell(api_key='key_8388afacb9ed29ccf0328d10e376')

# Get most recent call (or specific call_id if provided)
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

### Step 3: Download live agent (1 file - FULL agent with conversation flow)
**CRITICAL:** The agent file MUST include the conversation flow nodes and tools.

```python
# Get production agent ID from phone number
agent_id = 'agent_4ed4bfb82acde1bc924c69d406'

# Get agent details
agent = client.agent.retrieve(agent_id=agent_id)

# Get conversation flow
cf_id = agent.response_engine.conversation_flow_id
cf = client.conversation_flow.retrieve(cf_id)

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

Save as: `Reignite_AI_Mega_Receptionist_vX.XX_CC_[timestamp].json`

### Step 4: Generate Live Diagnostics (1 file)

Create `LIVE_DIAGNOSTICS.txt` with results from database queries and webhook health checks.

#### 4a. Database Queries (via SSH to n8n Postgres)

Connect and run against `retellai_prod` database:
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

**Query 4: This call's webhook logs** (use call_id from Step 2)
```sql
SELECT webhook_name, success, error_code, duration_ms,
       request_body::text, response_body::text, created_at
FROM webhook_log
WHERE call_id = '[CALL_ID]'
ORDER BY created_at ASC;
```

**Query 5: Error log entries (last 24h)**
```sql
SELECT call_id, error_type, error_message, severity, context, created_at
FROM error_log
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC LIMIT 10;
```

**Query 6: Funding cache for test patient**
```sql
SELECT patient_id, funding_type, is_eligible, remaining_appointments,
       needs_referral, gap_fee_amount, cached_at
FROM patient_funding_cache
WHERE patient_id = '1805465202989210063';
```

**Query 7: Available slots for test village**
```sql
SELECT practitioner_name, village, service_category, starts_at, is_available
FROM individual_slots_cache
WHERE village = 'The Baytree' AND is_available = true
  AND starts_at > NOW()
ORDER BY starts_at
LIMIT 10;
```

#### 4b. Webhook Health Checks (test patient ONLY)

**USE ONLY:** Peter Ball / patient_id: `1805465202989210063` / phone: `0412111000`

**Test 1: Lookup caller by phone**
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/lookup-caller-phone" \
  -H "Content-Type: application/json" \
  -d '{"args": {"phone_number": "+61412111000", "call_id": "debug-[timestamp]"}}'
```

**Test 2: Get availability** (date 14+ days out)
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/get-availability" \
  -H "Content-Type: application/json" \
  -d '{"args": {"village": "The Baytree", "service_category": "physio", "date": "[YYYY-MM-DD]", "appointment_type": "Standard Consultation", "patient_id": "1805465202989210063", "call_id": "debug-[timestamp]"}}'
```

**Test 3: Check funding**
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/check-funding" \
  -H "Content-Type: application/json" \
  -d '{"args": {"patient_id": "1805465202989210063", "funding_type": "HCP", "call_id": "debug-[timestamp]"}}'
```

**Test 4: Book appointment compound** (DO NOT RUN unless explicitly testing - uses real data)
```bash
# SKIPPED by default - only run with explicit instruction
# curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/book-appointment-compound" \
#   -H "Content-Type: application/json" \
#   -d '{"args": {"patient_id": "1805465202989210063", ...}}'
```

#### 4c. Format LIVE_DIAGNOSTICS.txt
```
=== LIVE DIAGNOSTICS ===
Generated: [timestamp]
Call ID: [from step 2]
Agent Version: [from step 3]

--- DATABASE QUERIES ---

[Query 1: Webhook Failures - Last 24h]
[results or "No failures found"]

[Query 2: Recent Call Log Entries]
[results]

[Query 3: Recent Appointment Bookings]
[results or "No bookings found"]

[Query 4: This Call's Webhook Logs]
[results or "No webhook logs for this call"]

[Query 5: Error Log Entries]
[results or "No errors"]

[Query 6: Funding Cache for Test Patient]
[results]

[Query 7: Available Slots]
[results]

--- WEBHOOK HEALTH CHECKS ---

[1. Lookup Caller by Phone]
Endpoint: lookup-caller-phone
Request: {"phone_number": "+61412111000", ...}
Response: [JSON]
Status: OK / FAIL

[2. Get Availability]
Endpoint: get-availability
Request: {"village": "The Baytree", "service_category": "physio", ...}
Response: [JSON]
Status: OK / FAIL

[3. Check Funding]
Endpoint: check-funding
Request: {"patient_id": "...", "funding_type": "...", ...}
Response: [JSON]
Status: OK / FAIL

[4. Book Appointment Compound]
Status: SKIPPED (destructive test)

--- HEALTH SUMMARY ---
Webhooks responding: X/3
DB errors in last 24h: X
Webhook failures in last 24h: X
Individual slots available: X
Likely issue area: [webhooks/database/agent logic/funding/practitioner_id/slot_unavailable/unknown]
```

### Step 5: Download n8n workflows (2 files)

Get workflow IDs from n8n API, then download:
```bash
# List workflows to find IDs
curl -s "https://auto.yr.com.au/api/v1/workflows?limit=50" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4"

# Look for:
# - "RetellAI - Create Appointment v2.5 PETER EMAIL FIXED" (book-appointment-compound)
# - "RetellAI - Get Practitioner Availability v2.0 DATABASE_FIRST" (get-availability)
```

Save as:
- `wf_book_appointment_compound.json`
- `wf_get_availability.json`

### Step 6: Copy reference docs (4 files)
```bash
cp "retell/RETELLAI_JSON_SCHEMAS.md" "[output]/RETELLAI_JSON_SCHEMAS.md"
cp "retell/AGENT_DEVELOPMENT_GUIDE.md" "[output]/AGENT_DEVELOPMENT_GUIDE.md"
cp "retell/guides/BOOKING_FLOW_TROUBLESHOOTING.md" "[output]/BOOKING_FLOW_TROUBLESHOOTING.md"
cp "n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md" "[output]/WEBHOOKS_REFERENCE.md"
```

### Step 7: Generate and SAVE diagnostic report (1 file)

Create `DIAGNOSTIC_REPORT.md` in the output folder containing:

```markdown
# Diagnostic Report: [Call ID]
Generated: [timestamp]

## Call Summary
- **Call ID:** [id]
- **Agent Version:** [agent_name]
- **Duration:** [X seconds]
- **Outcome:** [call_analysis.call_summary]
- **Disconnection Reason:** [reason]
- **User Sentiment:** [sentiment]

## Collected Variables (at call end)
```json
[collected_dynamic_variables from call data]
```

## Booking Flow Analysis
- **Patient identified:** Yes/No (patient_id: [id])
- **Service type:** Physio/EP
- **Village:** [village from variables]
- **Practitioner requested:** [from variables or "none"]
- **Funding type:** [funding_type from variables]
- **Slot offered:** [from spoken_text or slots variable]
- **Error received:** [error_code and error_message if present]

## Tool Calls Made
| # | Tool | Latency (ms) | Success | Key Request Data | Key Response Data |
|---|------|--------------|---------|------------------|-------------------|
| 1 | lookup_caller_by_phone | X | OK/FAIL | phone_number | patient_id, village |
| 2 | get_availability | X | OK/FAIL | village, date | practitioner_id, slots |
| 3 | check_funding | X | OK/FAIL | patient_id, funding_type | eligible |
| 4 | book_appointment_compound | X | OK/FAIL | all params | error_code/success |

## Critical Variables at Failure Point
```json
{
  "patient_id": "[value]",
  "village": "[value]",
  "practitioner_id": "[value or MISSING]",
  "starts_at": "[value or MISSING]",
  "funding_type": "[value or MISSING]",
  "appointment_type": "[value]",
  "error_code": "[value if present]",
  "error_message": "[value if present]"
}
```

## Live System Health
- Webhooks: [X/3 responding]
- DB errors last 24h: [count]
- Webhook failures last 24h: [count]
- Available slots in system: [count]

## Issues Found
1. **[Issue Name]**: [Description with evidence from call/DB]
2. ...

## Common Individual Booking Failure Patterns

Check these first:
- [ ] `practitioner_id` missing or null in book-appointment-compound call
- [ ] `starts_at` timestamp malformed or doesn't match available slot
- [ ] `SLOT_UNAVAILABLE` error (slot was booked between availability check and booking)
- [ ] `funding_type` not extracted from conversation
- [ ] `appointment_type` mismatch between get-availability and book-appointment
- [ ] Edge loop: agent cycling between get-slots and present-slots
- [ ] Webhook timeout or failure

## Root Cause
[Why the booking failed - be specific. Reference the tool call that failed and why.]

## Fix Recommendations
1. **[File to change]**: [What to change and why]
2. ...
```

**IMPORTANT:** Write the diagnostic report to the output folder, not just display it.

## Step 8: Final Validation (MANDATORY)

### 8a: Verify agent file size (>200KB)
```bash
ls -la [output]/Reignite_AI_Mega_Receptionist_v*.json
```

**If agent file is <200KB:** DELETE and re-download with conversation flow.

### 8b: Enforce exactly 10 files
Count files. If more than 10, delete in this order (least important first):
1. Any `.py` scripts -> DELETE
2. Any `download_summary.json` or manifest files -> DELETE
3. Any temp/helper files -> DELETE
4. `wf_get_availability.json` if still over 10
5. `WEBHOOKS_REFERENCE.md` if still over 10

```bash
ls -1 [output] | wc -l
# Must be exactly 10
```

### 8c: Final checklist
- [ ] Exactly 10 files
- [ ] Agent file >200KB
- [ ] `LIVE_DIAGNOSTICS.txt` exists with DB + curl results
- [ ] `DIAGNOSTIC_REPORT.md` saved to folder
- [ ] No Python scripts in folder
- [ ] No subfolders

**If any check fails, fix it before completing.**

## Final Folder Structure

```
[YYYY-MM-DD]-booking-debug-[HHMMSS]/
├── call_abc123_full.json              # The problem call
├── Reignite_AI_Mega_Receptionist_v11.142_CC_20251205.json  # Live agent (>200KB)
├── LIVE_DIAGNOSTICS.txt               # DB queries + webhook tests
├── RETELLAI_JSON_SCHEMAS.md           # Validation rules
├── AGENT_DEVELOPMENT_GUIDE.md         # 5 critical rules
├── BOOKING_FLOW_TROUBLESHOOTING.md    # Individual booking failures
├── wf_book_appointment_compound.json  # Booking workflow
├── wf_get_availability.json           # Availability lookup workflow
├── WEBHOOKS_REFERENCE.md              # API contracts
└── DIAGNOSTIC_REPORT.md               # Analysis + fixes
```

**Total: 10 files, no scripts, no subfolders**

## Step 9: Final Output (MANDATORY)

After all steps complete successfully, print EXACTLY this to the screen:

```
[FULL_ABSOLUTE_PATH_TO_OUTPUT_FOLDER]
DONE DONE DONE
```

Example:
```
C:\Users\peter\Downloads\CC\retell\Testing\2025-12-05-booking-debug-143052
DONE DONE DONE
```

**This MUST be the last thing printed.** No additional text after "DONE DONE DONE".

---

## Quick Reference

### Production Info
- **Phone Numbers:** +61288800226, +61240620999
- **Agent ID:** agent_4ed4bfb82acde1bc924c69d406
- **Current Version:** v11.142 (85 nodes, 19 tools)
- **Server IP:** 52.13.124.171

### Test Patient (SAFE TO USE)
- **Name:** Peter Ball
- **Patient ID:** 1805465202989210063
- **Phone:** 0412111000

### Key Tables
| Table | Purpose |
|-------|---------|
| `webhook_log` | All webhook calls with request/response |
| `call_log` | Call metadata (intent, outcome) |
| `appointment_log` | Created appointments |
| `error_log` | System errors |
| `patient_funding_cache` | Funding eligibility |
| `individual_slots_cache` | Available appointment slots |

### Key Tools in Agent
| Tool ID | Purpose |
|---------|---------|
| `tool-lookup-caller-phone` | Identify caller |
| `tool-get-availability` | Find available slots |
| `tool-check-funding` | Verify funding eligibility |
| `tool-book-appointment-compound` | Create appointment |

---

*Last Updated: 2025-12-05 | Based on agent v11.142 and current database schema*
