# AI Voice Agent & Automation Knowledge Base

## MANDATORY COMPLETION FORMAT

**After EVERY completed task**, end your response with:
```
DONE DONE DONE

Files created/modified:
• [Full absolute path]
```

---

## CRITICAL SAFETY RULES

### Test Patient (ONLY USE THIS)
| Field | Value |
|-------|-------|
| **Name** | `Peter Ball` |
| **Patient ID** | `1805465202989210063` |
| **Phone** | `0412111000` |

**⚠️ ALL tests, simulations, and webhook calls MUST use Peter Ball's data. Never use real patient data.**

### RetellAI Simulation Tests
Tests with `"tool_mocks": []` execute REAL webhooks and modify REAL Cliniko data.

| Rule | Allowed Values Only |
|------|---------------------|
| Patient Names | `Peter Ball` or `Test Test` |
| Phone Number | `0412111000` |
| Appointment Dates | Minimum 14 days from test creation |

**If ANY rule is violated → DO NOT RUN THE TEST**

### n8n PostgreSQL (3 Rules)
1. `alwaysOutputData: true` on ALL PostgreSQL nodes
2. `RETURNING *;` on ALL INSERT/UPDATE/DELETE statements
3. NEVER use `JSON.parse()` on JSONB columns (already parsed)

---

## GIT AUTO-COMMIT (REQUIRED)

**Commit and push immediately after creating/modifying files. Do not ask.**

```bash
# Root docs
cd /c/Users/peter/Downloads/CC && git add . && git commit -m "Update - [desc]" && git push

# RetellAI agents
cd /c/Users/peter/Downloads/CC/retell && git add . && git commit -m "Agent vX.XX - [desc]" && git push

# n8n workflows
cd /c/Users/peter/Downloads/CC/n8n && git add . && git commit -m "Workflow - [desc]" && git push
```

### After Modifying n8n Workflows

**If you changed webhook parameters, responses, or endpoints:**
- [ ] Update `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md`

**To regenerate workflow docs automatically:**
```bash
cd C:\Users\peter\Downloads\CC\n8n\Python
python CC-Made-generate-workflow-docs.py
```

**Quick doc check:** Run `/n8n-doc-check` slash command to be prompted about documentation updates.

---

## QUICK REFERENCE

### Production Phone Numbers
- `+61288800226` - Main Sydney number
- `+61240620999` - Secondary number

### API Keys & Credentials

| Service | Location | Notes |
|---------|----------|-------|
| **Retell API** | `C:\Users\peter\Downloads\Retell_API_Key.txt` | Used by deploy scripts automatically |
| **n8n API** | Hardcoded in approved commands | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4` |
| **SSH Key** | `C:\Users\peter\.ssh\metabase-aws` | For n8n server access |
| **n8n Server** | `ubuntu@52.13.124.171` | ⚠️ NOT 54.149.95.69 |

### Key Commands
```bash
# Deploy agent to production
cd C:\Users\peter\Downloads\CC\retell\scripts
python deploy_agent.py agent.json

# Validate agent (pre-import)
python retell_agent_validator.py agent.json --fix

# Audit agent
python retell_audit.py agent.json -o report.md

# View phone numbers
cd C:\Users\peter\Downloads\CC\Telcos && python telco.py

# n8n webhook tools
cd C:\Users\peter\Downloads\CC\n8n\Python
python CC-Made-n8n_api_download_workflows.py --retell

# Upload/update n8n workflow (filter to required fields only)
# API rejects: active (read-only), id, updatedAt, createdAt, shared, tags, etc.
# Keep only: name, nodes, connections, settings
curl -X PUT "https://auto.yr.com.au/api/v1/workflows/WORKFLOW_ID" \
  -H "X-N8N-API-KEY: <key>" -H "Content-Type: application/json" \
  -d @filtered_workflow.json

# Execute SQL on n8n Postgres (via SSH)
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"SELECT * FROM patients LIMIT 5;\""
```

### Direct Database Access

**SSH + Docker exec** to run SQL on n8n's Postgres:
```bash
# Interactive psql session
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171
docker exec -it n8n-postgres-1 psql -U n8n -d retellai_prod

# One-liner SQL query
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"YOUR SQL HERE;\""
```

| Database | Contains |
|----------|----------|
| `n8n` | Workflow definitions, credentials, execution logs |
| `retellai_prod` | patients, webhook_cache, retell_calls, sync_metadata |

**Reference:** `n8n/Guides Docs/N8N_SETUP_CREDENTIAL_FOR_N8N_DATABASE.md`

---

## MANDATORY READS

**Read BEFORE working on RetellAI agents:**

| Priority | File | Why |
|----------|------|-----|
| 1 | `retell/RETELLAI_REFERENCE.md` | API, Events, Variables |
| 2 | `retell/RETELLAI_JSON_SCHEMAS.md` | Valid JSON, node types, validation rules |
| 3 | `retell/AGENT_DEVELOPMENT_GUIDE.md` | **v2.2:** 6 critical rules, equation transitions, IPA pronunciation, `does not exists` syntax |
| 4 | `retell/guides/BOOKING_FLOW_TROUBLESHOOTING.md` | Booking failures, edge loops, practitioner_id |

**Read BEFORE working on n8n:**

| File | Why |
|------|-----|
| `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` | **ONLY source of truth** for endpoints, params, responses |
| `n8n/Webhooks Docs/N8N_WEBHOOK_TROUBLESHOOTING.md` | Debugging, common errors, fixes |
| `n8n/Webhooks Docs/SYSTEM_EMAILS_REFERENCE.md` | Email workflows |

**⚠️ NEVER use docs from `n8n/Webhooks Docs/archive/` - they're outdated and WILL cause bugs.**

---

## FILE LOCATIONS

| What | Where |
|------|-------|
| **Active dev** | `retell/Testing/[current-date]/` (e.g., `25-12-03a/`) |
| **Production agent** | `retell/agents/` (only latest stable) |
| **n8n workflows** | `n8n/JSON/active_workflows/` |
| **Webhook specs** | `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` |

**Agent Naming:** `Reignite_AI_Mega_Receptionist_vX.XX_CC.json`

---

## WORKFLOW: New Agent Version

1. Copy from `retell/agents/` (latest) or current Testing folder
2. Increment version in filename AND `agent_name` field
3. Save to `retell/Testing/[current-date]/`
4. Run: `python retell_agent_validator.py <file> --fix`
5. Run: `python retell_audit.py <file>` - fix CRITICAL issues
6. Deploy: `python deploy_agent.py <file>`
7. When stable → copy to `retell/agents/`
8. Git commit both locations

---

## BEFORE BUILDING NEW SCRIPTS

**Check the `run.py` launcher system first!** Many scripts already exist.

```bash
# Launch the script menu to see all available scripts
cd C:\Users\peter\Downloads\CC
python run.py
```

**Script locations to check:**
| Category | Location |
|----------|----------|
| n8n Core | `n8n/Python/` |
| n8n Diagnostics | `n8n/Python/Diagnose-n8n-Errors/` |
| RetellAI Scripts | `retell/scripts/` |
| Telco Manager | `Telcos/telco.py` |

**Don't reinvent the wheel** - search existing scripts before creating new ones.

---

## ALWAYS DO

- **Check existing scripts** in `run.py` before building new tools
- Read reference docs before agent/workflow work
- Run independent tool calls in parallel
- Read files before editing
- Commit and push after file changes
- Save dev work to Testing/, stable to agents/

## NEVER DO

- Save agents directly to agents/ without testing
- Keep multiple versions in agents/ (only latest stable)
- Overwrite source files (input ≠ output)
- Use `tool-log-error` (doesn't exist - use `tool-add-to-followup`)

---

## PROJECT OVERVIEW

**System:** AI receptionist using RetellAI + n8n automation
**Stack:** RetellAI, n8n, AWS EC2, Docker, PostgreSQL, Cliniko
**Version:** Reignite AI Mega Receptionist v11.154

---

**Last Updated:** 2025-12-06
