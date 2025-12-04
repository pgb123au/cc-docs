# Debug Individual Appointment Booking Issues

Create a focused debug package for diagnosing individual appointment booking problems (Physio/EP, not classes).

## Output Folder

**IMPORTANT:** Create a NEW unique folder each time this command runs:
`retell/Testing/[YYYY-MM-DD]-booking-debug-[HHMMSS]/`

Example: `retell/Testing/2025-12-04-booking-debug-143052/`

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
| 8 | `wf_get_availability.json` | n8n API | Slot lookup workflow |
| 9 | `WEBHOOKS_REFERENCE.md` | Copy from n8n/Webhooks Docs/ | API contracts |
| 10 | `DIAGNOSTIC_REPORT.md` | Generated | Analysis and fix recommendations |

## Execution Steps

### Step 1: Create UNIQUE output folder
```bash
mkdir -p retell/Testing/[YYYY-MM-DD]-booking-debug-[HHMMSS]
```

### Step 2: Download call data (1 file)
Use RetellAI SDK or API:
- Get most recent call for the production agent (or specific call_id if provided)
- Save `call_[id]_full.json` with complete call data including `transcript_with_tool_calls`

### Step 3: Download live agent (1 file - FULL agent with conversation flow)
**CRITICAL:** The agent file MUST include the conversation flow nodes and tools.

1. Get production agent ID from phone number
2. Get agent details via `client.agent.retrieve()`
3. Get conversation flow via `client.conversation_flow.retrieve()`
4. Combine into single file with `conversationFlow` containing nodes, tools, etc.
5. **Verify file size is >200KB** (small files = missing conversation flow)

Save as: `Reignite_AI_Mega_Receptionist_vX.XX_CC_[timestamp].json`

### Step 4: Generate Live Diagnostics (1 file)

Create `LIVE_DIAGNOSTICS.txt` with results from database queries and webhook health checks.

#### 4a. Database Queries (via SSH to n8n Postgres)

Connect and run against `retellai_prod` database:
```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@54.149.95.69 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"[QUERY];\""
```

**Query 1: Recent webhook failures (last 24h)**
```sql
SELECT created_at, endpoint, status, error_message
FROM webhook_cache
WHERE status != 'success' AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC LIMIT 20;
```

**Query 2: Recent individual bookings (appointments, not classes)**
```sql
SELECT call_id, patient_id, created_at, booking_status, practitioner_name, appointment_time
FROM retell_calls
WHERE booking_type = 'individual' OR booking_type IS NULL
ORDER BY created_at DESC LIMIT 15;
```

**Query 3: This call's DB records** (use call_id from Step 2)
```sql
SELECT * FROM retell_calls
WHERE call_id = '[CALL_ID]';
```

**Query 4: Recent Cliniko sync errors**
```sql
SELECT * FROM sync_metadata
WHERE status = 'error'
ORDER BY updated_at DESC LIMIT 10;
```

**Query 5: Funding check failures (last 24h)**
```sql
SELECT created_at, endpoint, request_body, response_body, error_message
FROM webhook_cache
WHERE endpoint LIKE '%check-funding%' AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC LIMIT 10;
```

#### 4b. Webhook Health Checks (test patient ONLY)

**USE ONLY:** Peter Ball / patient_id: `1805465202989210063` / phone: `0412111000`

**Test 1: Lookup caller by phone**
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/lookup-caller-phone" \
  -H "Content-Type: application/json" \
  -d '{"args": {"phone_number": "+61412111000", "call_id": "debug-[timestamp]"}}'
```

**Test 2: Get availability** (use village from failing call, date 14+ days out)
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/get-availability" \
  -H "Content-Type: application/json" \
  -d '{"args": {"village": "[FROM_CALL]", "service_category": "physio", "date": "[YYYY-MM-DD]", "appointment_type": "Standard Consultation", "patient_id": "1805465202989210063", "call_id": "debug-[timestamp]"}}'
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

[Query 2: Recent Individual Bookings]
[results]

[Query 3: This Call's DB Records]
[results or "No records found"]

[Query 4: Sync Errors]
[results or "No errors"]

[Query 5: Funding Check Failures]
[results or "No failures"]

--- WEBHOOK HEALTH CHECKS ---

[1. Lookup Caller by Phone]
Endpoint: lookup-caller-phone
Request: {"phone_number": "+61412111000", ...}
Response: [JSON]
Status: OK / FAIL

[2. Get Availability]
Endpoint: get-availability
Request: {"village": "...", "service_category": "physio", ...}
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
Funding failures: X
Sync errors: X
Likely issue area: [webhooks/database/agent logic/funding/practitioner_id/unknown]
```

### Step 5: Download n8n workflows (2 files)
Use `n8n/Python/CC-Made-n8n_api_download_workflows.py --retell` or n8n API directly:
- Book Appointment Compound -> `wf_book_appointment_compound.json`
- Get Availability -> `wf_get_availability.json`

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
- **Duration:** [X seconds]
- **Outcome:** [what happened - booking success/fail/abandoned]
- **Disconnection Reason:** [reason]

## Booking Flow Analysis
- **Patient identified:** Yes/No (patient_id: [id])
- **Service type:** Physio/EP
- **Village:** [village name]
- **Practitioner requested:** [name or "none"]
- **Funding type:** [HCP/DVA/PRIVATE/etc.]
- **Slot selected:** [datetime or "none"]

## Tool Calls Made
| # | Tool | Request | Response | Success |
|---|------|---------|----------|---------|
| 1 | lookup-caller-phone | {...} | {...} | OK/FAIL |
| 2 | get-availability | {...} | {...} | OK/FAIL |
| 3 | check-funding | {...} | {...} | OK/FAIL |
| 4 | book-appointment-compound | {...} | {...} | OK/FAIL |

## Critical Variables at Failure Point
```json
{
  "patient_id": "[value]",
  "village": "[value]",
  "practitioner_id": "[value or MISSING]",
  "starts_at": "[value or MISSING]",
  "funding_type": "[value or MISSING]",
  "appointment_type": "[value]"
}
```

## Live System Health
- Webhooks: [X/3 responding]
- DB errors last 24h: [count]
- Funding failures: [count]
- Sync status: [OK/errors]

## Issues Found
1. **[Issue Name]**: [Description with evidence from call/DB]
2. ...

## Common Individual Booking Failure Patterns

Check these first:
- [ ] `practitioner_id` missing or null in book-appointment-compound call
- [ ] `starts_at` timestamp malformed or doesn't match available slot
- [ ] `funding_type` not extracted from conversation
- [ ] `appointment_type` mismatch between get-availability and book-appointment
- [ ] Edge loop: agent cycling between get-slots and present-slots
- [ ] Double funding check latency (now fixed in v11.139)

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
├── Reignite_AI_Mega_Receptionist_v11.139_CC_20251204.json  # Live agent (>200KB)
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
C:\Users\peter\Downloads\CC\retell\Testing\2025-12-04-booking-debug-143052
DONE DONE DONE
```

**This MUST be the last thing printed.** No additional text after "DONE DONE DONE".
