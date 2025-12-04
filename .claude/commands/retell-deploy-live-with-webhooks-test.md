---
description: Full live deployment: validate agent, deploy to RetellAI, connect phone lines, upload/activate n8n webhooks, test endpoints
---

# Full Live Deployment with Webhook Testing

Deploy the newest RetellAI agent to production with full webhook validation and testing.

## Pre-Flight Checks

1. **Skip validation if just done** - Check conversation history for recent `/retell-validate-agent` results
2. **If not validated recently**, run full validation:
   - Agent JSON structure
   - Version format and sync
   - tool_id references exist in n8n

## Deployment Steps

### Step 1: Find Newest Agent
- Look in `retell/Testing/` for the most recently modified `*.json` file
- Confirm filename matches pattern `Reignite_AI_Mega_Receptionist_vX.XX_CC.json`

### Step 2: Validate Agent (unless just done)
Run validation checks per `/retell-validate-agent`

### Step 3: Deploy Agent to RetellAI
```bash
cd C:\Users\peter\Downloads\CC\retell\scripts
python deploy_agent.py <agent_file>
```
- This uploads the conversation flow to the production agent
- Updates the agent name to match new version

### Step 4: Connect Both Phone Lines
Verify both inbound numbers are connected to the deployed agent:
- `+61288800226` (Main Sydney)
- `+61240620999` (Secondary)

Use the Retell API to confirm/update phone number assignments if needed.

### Step 5: Upload Changed n8n Webhooks
For any modified workflow JSON files in `n8n/JSON/active_workflows/`:
```bash
cd C:\Users\peter\Downloads\CC\n8n\Python
python CC-Made-n8n_api_upload_workflow.py <workflow.json> --activate
```

If replacing an old version:
1. Upload new workflow
2. Activate new workflow
3. Deactivate old workflow (if separate)

### Step 6: Test Webhook Endpoints
Run test curls against critical endpoints using Peter Ball test data:

```bash
# Test lookup-caller-phone
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/lookup-caller-phone" \
  -H "Content-Type: application/json" \
  -d '{"args": {"phone": "0412111000", "call_id": "test-deploy"}}'

# Test check-funding (requires patient_id)
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/check-funding" \
  -H "Content-Type: application/json" \
  -d '{"args": {"patient_id": "1805465202989210063", "funding_type": "PRIVATE", "call_id": "test-deploy"}}'

# Test get-availability
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/get-availability" \
  -H "Content-Type: application/json" \
  -d '{"args": {"village": "The Baytree", "call_id": "test-deploy"}}'
```

### Step 7: SQL Health Check
Run quick database verification:
```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@54.149.95.69 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"SELECT COUNT(*) as total_patients FROM patients; SELECT COUNT(*) as recent_calls FROM retell_calls WHERE created_at > NOW() - INTERVAL '24 hours';\""
```

### Step 8: Fix Issues
If any curl test fails:
1. Check n8n workflow is active
2. Check webhook path matches tool_id
3. Fix and re-upload workflow
4. Re-test until all pass

**Loop until all tests pass - do not stop on first error!**

## Final Report

After all steps complete, output:

```
=== DEPLOYMENT COMPLETE ===

Agent Deployed:
  Version: vX.XXX
  File: [full path to agent JSON]
  RetellAI Agent ID: [agent_id]

Phone Lines Connected:
  +61288800226 - [CONNECTED/FAILED]
  +61240620999 - [CONNECTED/FAILED]

n8n Workflows Updated:
  - [workflow name] - [ACTIVATED/FAILED]
  - [workflow name] - [ACTIVATED/FAILED]

Webhook Tests:
  lookup-caller-phone: [PASS/FAIL]
  check-funding: [PASS/FAIL]
  get-availability: [PASS/FAIL]

Database Health:
  Total patients: [count]
  Calls (24h): [count]

Files Changed:
  - [absolute path 1]
  - [absolute path 2]

Status: [ALL LIVE / PARTIAL / FAILED]

DONE DONE DONE
```

## Critical Rules

- Use ONLY Peter Ball test data (patient_id: 1805465202989210063, phone: 0412111000)
- Do NOT create real appointments during testing
- Fix ALL errors before declaring done
- Report exact file paths that were modified
