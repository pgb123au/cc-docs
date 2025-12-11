---
description: Full autonomous n8n webhook/database fix process - includes agent changes if needed (12 steps)
---

# n8n Webhook Fix Process - AUTO

Full autonomous process to fix n8n webhooks and database issues. **If a fix requires agent changes too (COUPLED), this process handles both.**

**Prerequisites:** You should have already identified the bugs in this conversation (from testing, call analysis, or discussion). If not, describe the issues first.

---

## Step 1: CONFIRM BUGS

I'll list all bugs/issues we've identified in this conversation:

| ID | Type | Location | Bug | Solution |
|----|------|----------|-----|----------|

Types:
- **WEBHOOK** - n8n workflow change only
- **DATABASE** - Table/data change needed
- **SQL_FUNCTION** - PostgreSQL function change needed
- **COUPLED** - Webhook change AND agent change needed together

**>>> STOP FOR YOUR APPROVAL <<<**
You review the list and either approve or request changes.

---

## After Approval: Autonomous Execution (Steps 2-12)

| Step | Description |
|------|-------------|
| 2 | Fetch current workflows (backup first) |
| 3 | Implement webhook fixes |
| 4 | Deploy webhooks to n8n |
| 5 | Test webhooks with curl |
| 6 | Database/SQL function fixes |
| 7 | **COUPLED fixes - agent changes** (if any) |
| 8 | Deploy agent (if changed) |
| 9 | Update documentation |
| 10 | Git commit |
| 11 | Zero deferral check |
| 12 | Final report |

---

## Critical Rules

1. **DO NOT RUSH** - Complete each fix thoroughly
2. **TEST EVERY CHANGE** - Curl test before marking complete
3. **ZERO DEFERRAL** - Complete ALL fixes, no "later" allowed
4. **BACKUP FIRST** - Always backup workflows before modifying
5. **OUTPUT FULL PATHS** - Show Windows paths for all files
6. **COUPLED = BOTH** - If webhook needs agent change, do BOTH

---

## Step 7: COUPLED Fixes (Agent Changes)

**If ANY fix is marked COUPLED, or discovered during implementation to need agent changes:**

### 7A: Identify Agent Changes Needed
For each COUPLED fix, determine what agent changes are required:
- New response_variables to capture webhook fields?
- New edge conditions to route on error_codes?
- New nodes to handle new scenarios?
- Instruction text changes?

### 7B: Get Current Agent
```bash
# Find latest agent
cd C:\Users\peter\Downloads\CC\retell
ls -la agents/
ls -la Testing/*/Reignite_AI_Mega_Receptionist_v*.json
```

### 7C: Schema Verification (MANDATORY)
Before writing ANY new node/edge JSON, read existing elements first:
```bash
python3 -c "import json; d=json.load(open('agent.json')); print(json.dumps(d['conversation_flow']['nodes'][0], indent=2)[:800])"
```

| Wrong | Correct |
|-------|---------|
| `target` | `destination_node_id` |
| `condition` | `transition_condition` |
| `id` (nodes) | `node_id` |
| `id` (tools) | `tool_id` |

**NEVER write JSON from memory.**

### 7D: Implement Agent Changes
1. Create FIND/REPLACE strings for each change
2. Verify FIND is unique and in correct location
3. Apply changes
4. Validate JSON: `python retell_agent_validator.py agent_fixed.json --fix`

### 7E: Test Integration
1. Curl the webhook with test data that triggers the condition
2. Verify agent JSON correctly routes based on new response fields
3. Trace: webhook response → response_variables → edge condition → destination node

---

## Step 8: Deploy Agent (if changed)

Only if Step 7 made agent changes:

```bash
cd C:\Users\peter\Downloads\CC\retell\scripts
python deploy_agent.py agent_fixed.json
```

Then connect to phone lines:
- +61288800226 (Main Sydney)
- +61240620999 (Secondary)

---

## n8n Rules

- `alwaysOutputData: true` on ALL PostgreSQL nodes
- `RETURNING *;` on ALL INSERT/UPDATE/DELETE statements
- NEVER use `JSON.parse()` on JSONB columns (already parsed)

## Test Data

All tests use Peter Ball:
- Patient ID: `1805465202989210063`
- Phone: `0412111000`
- Appointment dates: minimum 14 days from today

## Key Commands

```bash
# Fetch workflows
cd C:\Users\peter\Downloads\CC\n8n\Python
python CC-Made-n8n_api_download_workflows.py --retell

# SSH to database
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171
docker exec -it n8n-postgres-1 psql -U n8n -d retellai_prod

# One-liner SQL
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"SQL;\""
```

## API for Workflow Deployment

```bash
# Filter to allowed fields only: name, nodes, connections, settings
# API REJECTS: active, id, updatedAt, createdAt, shared, tags, versionId

curl -X PUT "https://auto.yr.com.au/api/v1/workflows/WORKFLOW_ID" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4" \
  -H "Content-Type: application/json" \
  -d @filtered_workflow.json
```

---

## Zero Deferral Check (Step 11)

Before final report, verify ALL fixes are done:

| Type | Verification |
|------|--------------|
| WEBHOOK | Deployed + curl tested |
| DATABASE | SQL executed + verified |
| SQL_FUNCTION | Created/replaced + tested |
| COUPLED | Webhook deployed + agent deployed + integration tested |

**If ANY fix not complete: GO BACK AND FIX IT.**

You are NOT allowed to output "Deferred" or "Later" or "Not in Scope".

---

**Now: Let me list the bugs we've identified in this conversation.**
