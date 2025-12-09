---
description: Deploy fixed n8n workflow to production, test endpoints, verify SQL, update docs
---

# Deploy n8n Workflow Fix

Deploy a fixed n8n workflow to production with full testing and documentation updates.

**Usage:** `/n8n-deploy-workflow-fix <workflow_json_path_or_workflow_id>`

---

## Step 1: Identify the Workflow

**If given a file path:**
1. Read the JSON file
2. Extract workflow name, nodes, connections, settings
3. Identify the webhook path from the Webhook node's `path` parameter
4. Determine the workflow ID to update (look for existing workflow with same webhook path)

**If given a workflow ID:**
1. Fetch the workflow from n8n API
2. Download to `n8n/JSON/active_workflows/` with timestamp
3. Identify the webhook path

**Extract webhook path using:**
```python
# Find webhook node and extract path
webhook_node = [n for n in nodes if n['type'] == 'n8n-nodes-base.webhook'][0]
webhook_path = webhook_node['parameters']['path']  # e.g., "reignite-retell/create-appointment"
```

---

## Step 2: Create Filtered PUT JSON

The n8n API only accepts these fields for PUT:
- `name`
- `nodes`
- `connections`
- `settings`

Create a filtered version:
```bash
cd "C:\Users\peter\Downloads\CC\n8n\JSON\active_workflows"
python -c "
import json
with open('INPUT_FILE.json', 'r') as f:
    data = json.load(f)
filtered = {
    'name': data['name'],
    'nodes': data['nodes'],
    'connections': data['connections'],
    'settings': data.get('settings', {'executionOrder': 'v1'})
}
with open('WORKFLOW_PUT.json', 'w') as f:
    json.dump(filtered, f, indent=2)
print(f'Created PUT JSON with {len(filtered[\"nodes\"])} nodes')
"
```

---

## Step 3: Upload to n8n

```bash
curl -s -X PUT "https://auto.yr.com.au/api/v1/workflows/WORKFLOW_ID" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4" \
  -H "Content-Type: application/json" \
  -d @WORKFLOW_PUT.json
```

**Verify response shows `"active": true`** - if not, activate it:
```bash
curl -s -X POST "https://auto.yr.com.au/api/v1/workflows/WORKFLOW_ID/activate" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4"
```

---

## Step 4: Test the Webhook Endpoint

**Use ONLY Peter Ball test data:**
- `patient_id`: `1805465202989210063`
- `phone`: `0412111000`
- `call_id`: `deploy-test-YYYYMMDD-HHMMSS`

**Test based on webhook path:**

### For lookup-caller-phone:
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/lookup-caller-phone" \
  -H "Content-Type: application/json" \
  -d '{"args": {"phone": "0412111000", "call_id": "deploy-test"}}'
```
**Expected:** `{"found": true, "patient_id": "1805465202989210063", ...}`

### For check-funding:
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/check-funding" \
  -H "Content-Type: application/json" \
  -d '{"args": {"patient_id": "1805465202989210063", "funding_type": "PRIVATE", "call_id": "deploy-test"}}'
```
**Expected:** `{"success": true, "eligible": true, ...}`

### For get-availability:
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/get-availability" \
  -H "Content-Type: application/json" \
  -d '{"args": {"village": "The Baytree", "call_id": "deploy-test"}}'
```
**Expected:** `{"success": true, "available_practitioners": [...], ...}`

### For create-appointment:
**Use a date 14+ days in future to avoid real booking concerns:**
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/create-appointment" \
  -H "Content-Type: application/json" \
  -d '{"body": {"args": {"patient_id": "1805465202989210063", "starts_at": "2025-12-24T10:00:00+11:00", "village": "Malabar Gardens", "funding_type": "PRIVATE", "appointment_type": "Standard Consultation", "call_id": "deploy-test"}}}'
```
**Expected:** `{"success": true, "appointment_created": true, "appointment_id": "...", ...}`
**NOTE:** This creates a REAL appointment - delete it after testing!

### For book-appointment-compound:
**Use far-future date to trigger validation without booking:**
```bash
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/book-appointment-compound" \
  -H "Content-Type: application/json" \
  -d '{"args": {"patient_id": "1805465202989210063", "starts_at": "2099-01-01T10:00:00.000Z", "village": "The Baytree", "funding_type": "PRIVATE", "appointment_type": "Standard", "duration_minutes": 30, "practitioner_id": "test", "call_id": "deploy-test"}}'
```
**Expected:** Error response (date too far) but confirms endpoint works

### For other webhooks:
Construct appropriate test based on `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md`

---

## Step 5: Verify with SQL Queries

```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"SELECT webhook_name, call_id, success, duration_ms, created_at FROM webhook_log WHERE call_id LIKE 'deploy-test%' ORDER BY created_at DESC LIMIT 5;\""
```

**For create-appointment, also check:**
```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"SELECT appointment_id, patient_id, datetime, village FROM appointment_log WHERE call_id LIKE 'deploy-test%' ORDER BY created_at DESC LIMIT 3;\""
```

---

## Step 6: Check for Errors

```bash
curl -s "https://auto.yr.com.au/api/v1/executions?limit=10&status=error" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4" \
  | python -c "import sys,json; r=json.load(sys.stdin); errors=[e for e in r.get('data',[]) if 'deploy-test' in str(e)]; print(f'Errors matching deploy-test: {len(errors)}')"
```

**If errors found, investigate:**
1. Get execution details
2. Check which node failed
3. Fix and re-deploy

---

## Step 7: Update Documentation

### 7a. Regenerate Auto-Generated Docs (ALWAYS)
```bash
cd C:\Users\peter\Downloads\CC\n8n\Python
python CC-Made-generate-workflow-docs.py
```

### 7b. Check if RETELLAI_WEBHOOKS_CURRENT.md Needs Updating

**Changes that REQUIRE doc updates:**
| Change Type | Update Required |
|-------------|-----------------|
| New/removed webhook parameter | YES - update Parameters table |
| Changed parameter name | YES - update Parameters table |
| New/removed response field | YES - update Response table |
| Changed response field name | YES - update Response table |
| Changed error codes | YES - update error handling notes |
| Internal code fix (no API change) | NO |
| Performance improvement | NO |
| Bug fix with same I/O | NO |

**To check:** Compare the workflow's input extraction and output format with the current docs.

Read `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` and search for the webhook section.

**If update needed:** Edit the relevant section in RETELLAI_WEBHOOKS_CURRENT.md

### 7c. Check if Retell Docs Need Updating

**Retell docs rarely need updating after n8n changes.** Only update if:

| Change Type | Retell Doc | Why |
|-------------|------------|-----|
| Response field name change | `RETELLAI_REFERENCE.md` | Agent variables reference these |
| New required parameter | `AGENT_DEVELOPMENT_GUIDE.md` | Agent tool schemas may need update |
| Changed booking validation | `guides/BOOKING_FLOW_TROUBLESHOOTING.md` | Troubleshooting steps may change |

**Usually NO retell doc updates needed** if you only fixed internal workflow logic.

---

## Step 8: Git Commit

```bash
cd C:\Users\peter\Downloads\CC\n8n && git add . && git commit -m "Workflow - [workflow name]: [brief description of fix]" && git push
```

---

## Step 9: Final Report

Output the following summary:

```
=== N8N WORKFLOW DEPLOYMENT COMPLETE ===

Workflow Deployed:
  Name: [workflow name]
  ID: [workflow ID]
  Webhook: [webhook path]

Test Results:
  Curl Test: [PASS/FAIL] - [response summary]
  SQL Verification: [PASS/FAIL] - [row count or error]
  Error Check: [PASS/FAIL] - [error count]

Documentation Updated:
  N8N_WORKFLOWS_AUTO_GENERATED.md: YES (always regenerated)
  RETELLAI_WEBHOOKS_CURRENT.md: [YES - what changed / NO - no API changes]
  Retell docs: [YES - which file / NO - not needed]

Files Created/Modified:
  • [absolute path to PUT JSON]
  • [absolute path to any docs changed]

Git Commit: [commit hash]

Status: [SUCCESS / PARTIAL / FAILED]

DONE DONE DONE
```

---

## Critical Rules

1. **ONLY use Peter Ball test data** (patient_id: 1805465202989210063, phone: 0412111000)
2. **Appointments 14+ days ahead** to avoid conflicts
3. **Delete test appointments** created during testing
4. **Fix ALL errors** before declaring success
5. **Always regenerate** auto-generated docs
6. **Only update RETELLAI_WEBHOOKS_CURRENT.md** if API contract changed
7. **Git commit** at the end

---

## Quick Reference: When to Update Which Doc

| What Changed | Auto-Gen | Webhooks Current | Retell Docs |
|--------------|----------|------------------|-------------|
| Workflow name/version | YES | NO | NO |
| Internal bug fix | YES | NO | NO |
| New parameter added | YES | YES | Maybe |
| Parameter renamed | YES | YES | YES |
| Response field added | YES | YES | Maybe |
| Response field renamed | YES | YES | YES |
| Error handling improved | YES | Maybe | Maybe |
| Performance fix | YES | NO | NO |
