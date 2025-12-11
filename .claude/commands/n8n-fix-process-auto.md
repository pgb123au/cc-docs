---
description: Full autonomous n8n webhook/database fix process (10 steps)
---

# n8n Webhook Fix Process - AUTO

Full autonomous process to fix n8n webhooks and database issues.

**Prerequisites:** You should have already identified the bugs in this conversation (from testing, call analysis, or discussion). If not, describe the issues first.

---

## Step 1: CONFIRM BUGS

I'll list all bugs/issues we've identified in this conversation:

| ID | Type | Location | Bug | Solution |
|----|------|----------|-----|----------|

Types:
- **WEBHOOK** - n8n workflow change needed
- **DATABASE** - Table/data change needed
- **SQL_FUNCTION** - PostgreSQL function change needed

**>>> STOP FOR YOUR APPROVAL <<<**
You review the list and either approve or request changes.

---

## After Approval: Autonomous Execution (Steps 2-10)

| Step | Description |
|------|-------------|
| 2 | Fetch current workflows (backup first) |
| 3 | Implement webhook fixes |
| 4 | Deploy webhooks to n8n |
| 5 | Test webhooks with curl |
| 6 | Database/SQL function fixes |
| 7 | Update documentation |
| 8 | Git commit |
| 9 | Zero deferral check |
| 10 | Final report |

---

## Critical Rules

1. **DO NOT RUSH** - Complete each fix thoroughly
2. **TEST EVERY CHANGE** - Curl test before marking complete
3. **ZERO DEFERRAL** - Complete ALL fixes, no "later" allowed
4. **BACKUP FIRST** - Always backup workflows before modifying
5. **OUTPUT FULL PATHS** - Show Windows paths for all files

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

**Now: Let me list the bugs we've identified in this conversation.**
