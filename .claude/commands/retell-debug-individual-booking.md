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
| 4 | `REFERENCE_DOCS.md` | Concatenated reference: JSON schemas + dev guide + troubleshooting + webhooks |
| 5 | `wf_book_appointment.json` | n8n booking workflow - creates appointments in Cliniko |
| 6 | `wf_get_availability.json` | n8n availability workflow - finds open slots |
| 7 | `wf_check_funding.json` | n8n funding workflow - verifies patient eligibility |
| 8 | `wf_lookup_caller.json` | n8n caller lookup workflow - identifies patient from phone |
| 9 | `N8N_WORKFLOW_MANIFEST.md` | List of all active n8n workflows with IDs and webhook paths |
| 10 | `DIAGNOSTIC_REPORT.md` | Analysis: root cause, evidence, fix recommendations |

## Execution Steps

### Step 1: Create UNIQUE output folder
```bash
mkdir -p retell/Testing/[YYYY-MM-DD]-booking-debug-[HHMMSS]
```

### Step 2: Download LIVE AGENT FIRST (determines versions for everything else)

**CRITICAL:** Fetch the agent FIRST. The agent version determines which workflow versions to fetch.

```python
from retell import Retell
import json

client = Retell(api_key='key_8388afacb9ed29ccf0328d10e376')

# Get production agent ID from phone number
agent_id = 'agent_4ed4bfb82acde1bc924c69d406'

# Get agent details
agent = client.agent.retrieve(agent_id=agent_id)

# Get conversation flow
cf_id = agent.response_engine.conversation_flow_id
cf = client.conversation_flow.retrieve(cf_id)

# Extract agent version from name (e.g., "v11.142")
agent_name = agent.agent_name
agent_version = agent_name  # Store this for workflow matching

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

Save as: `AGENT_[version].json` (e.g., `AGENT_v11.142.json`)

**STORE THE AGENT VERSION** - you need it for Step 4.

### Step 3: Download call data (1 file)

Use RetellAI SDK:
```python
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

### Step 4: Download n8n workflows (4 files) - LATEST ACTIVE VERSIONS

**IMPORTANT:** Get the LATEST ACTIVE versions of each workflow from n8n. These must match what the agent is currently calling.

```bash
# List ALL workflows to find the currently active versions
curl -s "https://auto.yr.com.au/api/v1/workflows?limit=100" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4"
```

**Find and download ONLY the ACTIVE workflows that handle these webhooks:**

| Webhook Path | Save As |
|--------------|---------|
| `/webhook/reignite-retell/book-appointment-compound` | `wf_book_appointment.json` |
| `/webhook/reignite-retell/get-availability` | `wf_get_availability.json` |
| `/webhook/reignite-retell/check-funding` | `wf_check_funding.json` |
| `/webhook/reignite-retell/lookup-caller-phone` | `wf_lookup_caller.json` |

**To identify the correct workflow:**
1. List all workflows
2. For each webhook path above, find the workflow that:
   - Is ACTIVE (not disabled)
   - Has the matching webhook trigger node
   - Has the HIGHEST version number if multiple exist

Download each workflow by ID:
```bash
curl -s "https://auto.yr.com.au/api/v1/workflows/[WORKFLOW_ID]" \
  -H "X-N8N-API-KEY: [API_KEY]"
```

### Step 5: Generate N8N_WORKFLOW_MANIFEST.md (1 file)

Create a manifest listing ALL active RetellAI workflows:

```markdown
# n8n Workflow Manifest
Generated: [timestamp]
Agent Version: [from Step 2]

## Active Workflows for This Agent

| Workflow ID | Name | Webhook Path | Status |
|-------------|------|--------------|--------|
| [id] | [name] | /webhook/reignite-retell/book-appointment-compound | Active |
| [id] | [name] | /webhook/reignite-retell/get-availability | Active |
| [id] | [name] | /webhook/reignite-retell/check-funding | Active |
| [id] | [name] | /webhook/reignite-retell/lookup-caller-phone | Active |

## All RetellAI Workflows (for reference)

| Workflow ID | Name | Active | Last Updated |
|-------------|------|--------|--------------|
[List all workflows containing "RetellAI" or "reignite-retell"]

## Version Alignment Check
- Agent Version: [version from Step 2]
- Workflows downloaded: [list IDs]
- Any version mismatches: [yes/no + details]
```

### Step 6: Generate Live Diagnostics (1 file)

Create `LIVE_DIAGNOSTICS.txt` with results from database queries and webhook health checks.

#### 6a. Database Queries (via SSH to n8n Postgres)

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

**Query 4: This call's webhook logs** (use call_id from Step 3)
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

#### 6b. Webhook Health Checks (test patient ONLY)

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

### Step 7: Concatenate Reference Docs (1 file)

**IMPORTANT:** Combine all reference documentation into a SINGLE file called `REFERENCE_DOCS.md`.

```bash
# Create concatenated reference file with clear section headers
```

The file should have this structure:

```markdown
# Reference Documentation
Generated: [timestamp]
Agent Version: [from Step 2]

This file contains all reference documentation needed for debugging booking issues.

---

## TABLE OF CONTENTS
1. [RetellAI JSON Schemas](#retellai-json-schemas)
2. [Agent Development Guide](#agent-development-guide)
3. [Booking Flow Troubleshooting](#booking-flow-troubleshooting)
4. [Webhook API Reference](#webhook-api-reference)

---

# SECTION 1: RetellAI JSON Schemas
Source: retell/RETELLAI_JSON_SCHEMAS.md

[FULL CONTENTS OF RETELLAI_JSON_SCHEMAS.md]

---

# SECTION 2: Agent Development Guide
Source: retell/AGENT_DEVELOPMENT_GUIDE.md

[FULL CONTENTS OF AGENT_DEVELOPMENT_GUIDE.md]

---

# SECTION 3: Booking Flow Troubleshooting
Source: retell/guides/BOOKING_FLOW_TROUBLESHOOTING.md

[FULL CONTENTS OF BOOKING_FLOW_TROUBLESHOOTING.md]

---

# SECTION 4: Webhook API Reference
Source: n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md

[FULL CONTENTS OF RETELLAI_WEBHOOKS_CURRENT.md]

---
END OF REFERENCE DOCUMENTATION
```

### Step 8: Generate and SAVE diagnostic report (1 file)

Create `DIAGNOSTIC_REPORT.md` in the output folder containing:

```markdown
# Diagnostic Report: [Call ID]
Generated: [timestamp]

## File Manifest

This debug package contains 10 files. Here's what each one is for:

| # | File | What It Contains | When To Use It |
|---|------|------------------|----------------|
| 1 | `call_[id]_full.json` | Complete call data: transcript, tool calls, timestamps, collected variables | Start here - shows exactly what happened |
| 2 | `AGENT_[version].json` | Live agent: all nodes, tools, prompts, conversation flow logic | Check agent logic, node transitions, variable bindings |
| 3 | `LIVE_DIAGNOSTICS.txt` | Database query results + webhook health check responses | Verify system health, find DB errors, check endpoints |
| 4 | `REFERENCE_DOCS.md` | Combined docs: JSON schemas, dev guide, troubleshooting, webhook specs | Look up correct patterns, validation rules, API contracts |
| 5 | `wf_book_appointment.json` | n8n workflow that creates appointments in Cliniko | Debug booking failures, check parameter handling |
| 6 | `wf_get_availability.json` | n8n workflow that finds available slots | Debug slot lookup issues, practitioner_id problems |
| 7 | `wf_check_funding.json` | n8n workflow that verifies patient eligibility | Debug funding check failures |
| 8 | `wf_lookup_caller.json` | n8n workflow that identifies patient from phone | Debug patient identification issues |
| 9 | `N8N_WORKFLOW_MANIFEST.md` | List of all active workflows with IDs and webhook paths | Verify correct workflows are active, check version alignment |
| 10 | `DIAGNOSTIC_REPORT.md` | This file - analysis, root cause, recommendations | Summary and action items |

---

## Call Summary
- **Call ID:** [id]
- **Agent Version:** [agent_name from Step 2]
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

## Version Alignment
- **Agent version:** [from Step 2]
- **Workflows match agent:** [Yes/No]
- **Any stale workflows:** [list or "None"]

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

## Step 9: Final Validation (MANDATORY)

### 9a: Verify agent file size (>200KB)
```bash
ls -la [output]/AGENT_v*.json
```

**If agent file is <200KB:** DELETE and re-download with conversation flow.

### 9b: Verify exactly 10 files
```bash
ls -1 [output] | wc -l
# Must be exactly 10
```

Expected files:
1. `call_[id]_full.json`
2. `AGENT_[version].json`
3. `LIVE_DIAGNOSTICS.txt`
4. `REFERENCE_DOCS.md`
5. `wf_book_appointment.json`
6. `wf_get_availability.json`
7. `wf_check_funding.json`
8. `wf_lookup_caller.json`
9. `N8N_WORKFLOW_MANIFEST.md`
10. `DIAGNOSTIC_REPORT.md`

### 9c: Final checklist
- [ ] Exactly 10 files
- [ ] Agent file >200KB
- [ ] `LIVE_DIAGNOSTICS.txt` exists with DB + curl results
- [ ] `REFERENCE_DOCS.md` contains all 4 concatenated docs
- [ ] `DIAGNOSTIC_REPORT.md` saved to folder with file manifest
- [ ] `N8N_WORKFLOW_MANIFEST.md` lists active workflows
- [ ] No Python scripts in folder
- [ ] No subfolders

**If any check fails, fix it before completing.**

## Final Folder Structure

```
[YYYY-MM-DD]-booking-debug-[HHMMSS]/
├── call_abc123_full.json         # 1. The problem call - what happened
├── AGENT_v11.142.json            # 2. Live agent (>200KB) - the logic
├── LIVE_DIAGNOSTICS.txt          # 3. System health - DB + webhooks
├── REFERENCE_DOCS.md             # 4. Combined docs - schemas, guides, APIs
├── wf_book_appointment.json      # 5. Booking workflow
├── wf_get_availability.json      # 6. Availability workflow
├── wf_check_funding.json         # 7. Funding workflow
├── wf_lookup_caller.json         # 8. Caller lookup workflow
├── N8N_WORKFLOW_MANIFEST.md      # 9. Workflow inventory
└── DIAGNOSTIC_REPORT.md          # 10. Analysis + file manifest + fixes
```

**Total: 10 files, no scripts, no subfolders**

## Step 10: Final Output (MANDATORY)

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

*Last Updated: 2025-12-05*
