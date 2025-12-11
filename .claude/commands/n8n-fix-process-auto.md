---
description: Full autonomous n8n webhook/database fix process - includes agent changes if needed (15 steps)
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

## After Approval: Autonomous Execution (Steps 2-15)

| Step | Description |
|------|-------------|
| 2 | Create todo list, confirm scope |
| 3 | Fetch current workflows (backup first) |
| 4 | **Deep investigation - find root causes** |
| 5 | **Impact analysis - what else is affected?** |
| 6 | Implement webhook fixes |
| 7 | Deploy webhooks to n8n |
| 8 | Test webhooks with curl |
| 9 | Database/SQL function fixes |
| 10 | COUPLED fixes - agent changes (if any) |
| 11 | Deploy agent (if changed) |
| 12 | Update documentation |
| 13 | Git commit |
| 14 | Zero deferral check |
| 15 | Final report + capture learnings |

---

## Critical Rules

1. **DO NOT RUSH** - Complete each fix thoroughly
2. **TEST EVERY CHANGE** - Curl test before marking complete
3. **ZERO DEFERRAL** - Complete ALL fixes, no "later" allowed
4. **BACKUP FIRST** - Always backup workflows before modifying
5. **OUTPUT FULL PATHS** - Show Windows paths for all files
6. **COUPLED = BOTH** - If webhook needs agent change, do BOTH
7. **FIX ROOT CAUSE** - Don't just fix symptoms, find why it's broken

---

## Step 2: Create Todo List & Confirm Scope

Create a todo list tracking ALL approved issues:
- Each issue gets its own todo item
- Mark as in_progress when working on it
- Mark as completed only when fully tested

Confirm:
- Which workflows are affected?
- Which database tables/functions?
- Any agent files involved?

VALIDATION GATE: Todo list created with all issues tracked.

---

## Step 3: Fetch Current Workflows (Backup First)

```bash
cd C:\Users\peter\Downloads\CC\n8n\Python
python CC-Made-n8n_api_download_workflows.py --retell
```

Or fetch specific workflow by ID:
```bash
curl -s "https://auto.yr.com.au/api/v1/workflows/WORKFLOW_ID" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4" \
  | python -m json.tool > workflow_backup.json
```

Save backups to: `C:\Users\peter\Downloads\CC\n8n\JSON\archive\`
Output: "Backup saved: [FULL PATH]"

VALIDATION GATE: All relevant workflows fetched and backed up.

---

## Step 4: Deep Investigation - Find Root Causes

**For EACH bug, answer these questions BEFORE implementing any fix:**

### 4A: Locate Exactly
- Which workflow? Which node(s)?
- What line/field has the problem?
- Show the actual current code/config

### 4B: Understand Root Cause
- WHY is this broken? (not just WHAT is broken)
- Is this a typo, logic error, missing field, wrong assumption?
- When did it break? Was it ever working?

### 4C: Check for Related Issues
- Is this same pattern broken elsewhere in the workflow?
- Are other workflows using similar logic that might be broken too?
- Is this a symptom of a deeper problem?

### 4D: Define Complete Fix
- What EXACTLY needs to change?
- Are there multiple places that need the same fix?
- What's the test to prove it's fixed?

Output for each bug:
```
BUG: [ID]
ROOT CAUSE: [why it's broken]
LOCATIONS: [all places needing fix]
COMPLETE FIX: [what to change]
TEST: [how to verify]
```

VALIDATION GATE: Every bug has root cause identified and complete fix defined.
DO NOT proceed to implementing until root causes are understood.

---

## Step 5: Impact Analysis - What Else Is Affected?

**Before changing anything, analyze ripple effects:**

### 5A: Data Flow Tracing
- If changing a response field: what uses that field downstream?
- If changing SQL: what workflows call this query?
- If changing error handling: what conditions trigger it?

### 5B: Cross-Workflow Check
- Does this fix need to be applied to multiple workflows?
- Are there other webhooks with the same pattern?

### 5C: Agent Impact
- Will the agent need to handle new/changed response fields?
- Does this change any error_codes the agent routes on?
- If YES → mark as COUPLED, add agent changes to scope

### 5D: Fix Dependencies
- Do fixes need to be applied in a specific order?
- Does Fix B depend on Fix A being done first?

Output:
```
IMPACT ANALYSIS:
- Downstream effects: [list]
- Other workflows affected: [list or NONE]
- Agent changes needed: [YES/NO - if YES, now COUPLED]
- Fix order: [sequence if dependencies exist]
```

VALIDATION GATE: Impact analysis complete. All COUPLED fixes identified.

---

## Step 6: Implement Webhook Fixes

For EACH webhook fix:

1. LOCATE the exact node in the workflow JSON
2. UNDERSTAND what the node currently does
3. IMPLEMENT the fix:
   - For response changes: modify the "Respond to Webhook" node
   - For logic changes: modify the relevant code/function nodes
   - For new error_codes: add to response object
   - Remember: `alwaysOutputData: true` on ALL PostgreSQL nodes
   - Remember: `RETURNING *;` on ALL INSERT/UPDATE/DELETE

4. VALIDATE JSON syntax before deploying

Output for each fix:
- Node modified: [node name]
- Change made: [description]
- JSON valid: YES/NO

VALIDATION GATE: All webhook fixes implemented. JSON valid.

---

## Step 7: Deploy Webhooks

Deploy each modified workflow:

```bash
# Filter to allowed fields only: name, nodes, connections, settings
# API REJECTS: active, id, updatedAt, createdAt, shared, tags, versionId

curl -X PUT "https://auto.yr.com.au/api/v1/workflows/WORKFLOW_ID" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4" \
  -H "Content-Type: application/json" \
  -d @filtered_workflow.json
```

VALIDATION GATE: Each workflow deployment returns success (HTTP 200).
If any fail: check error, fix, retry.

---

## Step 8: Test Webhooks with Curl

For EACH deployed webhook, test with curl:

```bash
curl -X POST "https://auto.yr.com.au/webhook/ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "1805465202989210063",
    "phone": "0412111000"
  }'
```

For each test, verify:
- HTTP 200 response
- Expected fields present
- New error_codes work (if applicable)
- Root cause is actually fixed (not just symptom)

Output:
| Endpoint | Status | Response Valid | Root Cause Fixed? |
|----------|--------|----------------|-------------------|

VALIDATION GATE: ALL curl tests pass AND root causes verified fixed.
If ANY fail: diagnose, fix workflow, redeploy, retest. LOOP until pass.

---

## Step 9: Database/SQL Function Fixes

For each DATABASE or SQL_FUNCTION fix:

1. SSH to server:
```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171
```

2. Connect to database:
```bash
docker exec -it n8n-postgres-1 psql -U n8n -d retellai_prod
```

3. For SQL function changes:
   - First SELECT to see current behavior
   - CREATE OR REPLACE FUNCTION with fix
   - Test with sample query
   - Verify expected output

4. For table changes:
   - First SELECT to verify current state
   - Run ALTER/UPDATE/INSERT
   - Verify with follow-up SELECT

One-liner format:
```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"YOUR SQL HERE;\""
```

Output for each fix:
- SQL executed: [command]
- Result: [output summary]
- Verified: YES/NO

VALIDATION GATE: All database fixes applied and verified.

---

## Step 10: COUPLED Fixes (Agent Changes)

**If ANY fix is marked COUPLED, or discovered during implementation to need agent changes:**

### 10A: Identify Agent Changes Needed
For each COUPLED fix, determine what agent changes are required:
- New response_variables to capture webhook fields?
- New edge conditions to route on error_codes?
- New nodes to handle new scenarios?
- Instruction text changes?

### 10B: Get Current Agent
```bash
cd C:\Users\peter\Downloads\CC\retell
ls -la agents/
ls -la Testing/*/Reignite_AI_Mega_Receptionist_v*.json
```

### 10C: Schema Verification (MANDATORY)
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

### 10D: Implement Agent Changes
1. Create FIND/REPLACE strings for each change
2. Verify FIND is unique and in correct location
3. Apply changes
4. Validate JSON: `python retell_agent_validator.py agent_fixed.json --fix`

### 10E: Test Integration
1. Curl the webhook with test data that triggers the condition
2. Verify agent JSON correctly routes based on new response fields
3. Trace: webhook response → response_variables → edge condition → destination node

VALIDATION GATE: Agent changes applied, validated, integration tested.

---

## Step 11: Deploy Agent (if changed)

Only if Step 10 made agent changes:

```bash
cd C:\Users\peter\Downloads\CC\retell\scripts
python deploy_agent.py agent_fixed.json
```

Then connect to phone lines:
- +61288800226 (Main Sydney)
- +61240620999 (Secondary)

VALIDATION GATE: Agent deployed and connected to phone lines.

---

## Step 12: Update Documentation

If ANY webhook parameters, responses, or error_codes changed:

1. Read: `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md`
2. Update:
   - Endpoint parameters (if changed)
   - Response fields (especially new error_codes)
   - Example responses
3. Add changelog entry at top:
   ```
   ## Changelog
   - [DATE] v[X.X]: [description of changes]
   ```
4. Save and commit

Output: "Docs updated: [PATH]" or "No doc changes needed"

---

## Step 13: Git Commit

```bash
cd C:\Users\peter\Downloads\CC\n8n
git add .
git commit -m "Webhook fixes - [summary]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push
```

If agent changed:
```bash
cd C:\Users\peter\Downloads\CC\retell
git add .
git commit -m "Agent v[X.XX] - [summary]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push
```

Output commit hash(es).

---

## Step 14: Zero Deferral Check

Before final report, verify ALL fixes are done:

| Type | Verification |
|------|--------------|
| WEBHOOK | Deployed + curl tested + root cause fixed |
| DATABASE | SQL executed + verified |
| SQL_FUNCTION | Created/replaced + tested |
| COUPLED | Webhook deployed + agent deployed + integration tested |

**If ANY fix not complete: GO BACK AND FIX IT.**

You are NOT allowed to output "Deferred" or "Later" or "Not in Scope".

VALIDATION GATE: Unresolved count = 0

---

## Step 15: Final Report + Capture Learnings

### Final Report

ALL BUGS STATUS:
| ID | Type | Root Cause | Status | Verification |
|----|------|------------|--------|--------------|
(List EVERY bug - ALL must show FIXED)

FILES CREATED/MODIFIED:
- [Full Windows path]: [description]

FIXES APPLIED:
- Webhook: [count]
- Database: [count]
- SQL function: [count]
- Coupled: [count]

TEST RESULTS:
- Webhook curls: [X/X] PASS
- SQL verifications: [X/X] PASS
- Integration tests: [X/X] PASS (if COUPLED)

GIT:
- n8n commit: [hash]
- retell commit: [hash] (if agent changed)
- Docs updated: YES/NO

### Capture Learnings

Save to working folder: `LEARNINGS_[date].md` (max 20 lines)

```
# Learnings from [date]

## Root Causes Found
- [pattern]: [why it was broken]

## Mistakes Made (don't repeat)
- [mistake]: [fix]

## Time Wasters
- [what]: [faster approach]

## Process Improvements
- [suggestion]
```

If CRITICAL learning: `>>> SUGGEST ADDING TO CLAUDE.md: [one-liner] <<<`

Output: "Created: [FULL WINDOWS PATH]"

---

## Test Data

All tests use Peter Ball:
- Patient ID: `1805465202989210063`
- Phone: `0412111000`
- Appointment dates: minimum 14 days from today

## n8n Rules

- `alwaysOutputData: true` on ALL PostgreSQL nodes
- `RETURNING *;` on ALL INSERT/UPDATE/DELETE statements
- NEVER use `JSON.parse()` on JSONB columns (already parsed)

---

**Now: Let me list the bugs we've identified in this conversation.**
