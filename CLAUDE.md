# AI Voice Agent & Automation Knowledge Base

## ⛔ NO AUTONOMOUS FIXES

**Claude MUST NOT fix, modify, or change ANY code/files without EXPRESS USER APPROVAL.**

- **INVESTIGATE ONLY** - Research, analyze, and report findings
- **PROPOSE solutions** - Explain what you would change and why
- **WAIT for approval** - Only proceed after user says "yes", "do it", "go ahead", etc.
- **ASK if unclear** - When in doubt, ask before touching anything

**This applies to:** Bug fixes, code improvements, "obvious" fixes, cleanup, refactoring, and ANY file modifications.

---

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

### RetellAI JSON Schema (MEMORIZE THIS)

**MANDATORY: Before writing ANY agent JSON, READ an existing node first to verify schema.**

```bash
# Quick schema check - run this BEFORE writing new nodes/edges
python3 -c "import json; d=json.load(open('agent.json')); print(json.dumps(d['conversation_flow']['nodes'][0], indent=2)[:800])"
```

| Wrong (Common Mistakes) | Correct (RetellAI) |
|-------------------------|-------------------|
| `target` | `destination_node_id` |
| `target_node_id` | `destination_node_id` |
| `condition` | `transition_condition` |
| `condition_prompt` | `transition_condition.prompt` |
| `prompt` (for node content) | `instruction` |
| `text` (in instruction) | `instruction.text` with `type: "prompt"` |

**Node types and their purpose:**
| Type | Purpose | User Interaction? |
|------|---------|-------------------|
| `conversation` | Speaks to user, can ask questions | YES |
| `function` | Calls webhooks silently | NO |
| `logic_split` | Silent instant routing on variables | NO - NEVER converts to/from conversation |
| `end` | Terminates call | NO |

**RULE: Before proposing node type changes, READ the node's instruction to understand what it does.**

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

### RetellAI Call Data Rule
**When user requests "last call" or "recent calls", ALWAYS fetch fresh from RetellAI API.**

- Use `retell/scripts/` tools or direct API calls to get current data
- NEVER use cached files like `last_call.json`, `call_*.json` from previous sessions
- Delete temp call files after use (don't leave in root folders)

```bash
# Get calls from API
cd C:\Users\peter\Downloads\CC\retell\scripts
python get_calls.py --limit 5
```

### Fix Location Rule (Agent vs n8n)
**When a fix can be done in EITHER the RetellAI agent OR n8n webhook, prefer n8n:**

| Fix in n8n (preferred) | Fix in Agent |
|------------------------|--------------|
| Type coercion (empty string → boolean/default) | Edge routing logic |
| Adding `error_code` fields for cleaner matching | Node parameter bindings |
| Input validation & defaults | Tool schema `required` arrays |
| Response formatting | Prompt/instruction text |

**Rationale:** n8n fixes are centralized, apply to all agents, and don't require agent redeployment.

### ⚠️ COUPLED FIXES - Agent + n8n Together
**When a fix requires BOTH agent AND n8n changes, you MUST complete BOTH.**

This is a recurring issue - DO NOT:
- Fix the agent and forget the webhook
- Say "we also need to update n8n" but never do it
- Deploy agent changes without the corresponding n8n changes

**MANDATORY PROCESS for coupled fixes:**
1. **Immediately create TodoWrite entries for BOTH parts** when you identify a coupled fix
2. Mark agent fix as `in_progress`, n8n fix as `pending`
3. Complete agent fix, mark as `completed`
4. **Immediately** start n8n fix - do NOT end the task
5. Only report "DONE DONE DONE" when BOTH are deployed

**Example todo list for coupled fix:**
```
[in_progress] Fix agent tool schema for get-availability
[pending] Update n8n get-availability webhook response format
[pending] Test end-to-end after both deployed
```

**If you find yourself about to say "DONE" with n8n changes still pending - STOP and complete them first.**

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

### Bash Path Format (CRITICAL)

**Windows paths DON'T work in bash.** Always use Unix-style `/c/` format:

| WRONG (will fail) | CORRECT |
|-------------------|---------|
| `cd C:\Users\peter\Downloads\CC` | `cd /c/Users/peter/Downloads/CC` |
| `cd C:\Users\peter\Downloads\CC\n8n\Python` | `cd /c/Users/peter/Downloads/CC/n8n/Python` |

**Exception:** Python scripts and SSH commands can use Windows paths with quotes:
```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@...  # OK
python "C:\Users\peter\...\script.py"                  # OK
```

### Key Commands
```bash
# Deploy agent to production
cd /c/Users/peter/Downloads/CC/retell/scripts
python deploy_agent.py agent.json

# Validate agent (pre-import)
python retell_agent_validator.py agent.json --fix

# Audit agent
python retell_audit.py agent.json -o report.md

# View phone numbers
cd /c/Users/peter/Downloads/CC/Telcos && python telco.py

# n8n webhook tools
cd /c/Users/peter/Downloads/CC/n8n/Python
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

### n8n Workflow Updates: API vs Direct SQL

**⚠️ ALWAYS prefer n8n REST API over direct SQL for workflow changes:**

| Method | When to Use |
|--------|-------------|
| **n8n REST API** | Updating workflow nodes, email addresses, parameters - PREFERRED |
| **Direct SQL** | Read-only queries, simple text searches, data inspection |

**Why API is better:**
1. No SQL escaping nightmares (quotes, special chars break SSH+psql chains)
2. JSON parsing handled properly
3. Automatic validation
4. No risk of corrupting workflow JSON

**n8n database has corrupted Unicode** in some workflows that breaks `json_array_elements()`. Use text extraction instead:
```sql
-- FAILS on some workflows:
SELECT n.value->>'sendTo' FROM workflow_entity w
CROSS JOIN LATERAL json_array_elements(w.nodes) AS n(value);

-- WORKS - text-based extraction:
SELECT substring(nodes::text from 'sendTo":"([^"]+)') FROM workflow_entity;
```

**API pattern for workflow updates:**
```python
import requests
API_KEY = '...'
BASE_URL = 'https://auto.yr.com.au/api/v1'
HEADERS = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# GET, modify, PUT back
wf = requests.get(f'{BASE_URL}/workflows/{wf_id}', headers=HEADERS).json()
# ... modify wf['nodes'] ...
requests.put(f'{BASE_URL}/workflows/{wf_id}', headers=HEADERS,
    json={'name': wf['name'], 'nodes': wf['nodes'],
          'connections': wf['connections'], 'settings': wf.get('settings', {})})
```

---

## Yes AI Branding (for Audit Reports)

**Always use these assets when generating website audit reports/PDFs:**

| Asset | Location |
|-------|----------|
| **Logo (PNG)** | `C:\Users\peter\Downloads\CC\Yes AI Assets\YesAI_colors_punched_transparent6.png` |
| **Logo colors** | Red "Yes", Blue "AI", Blue swoosh |

**Contact details to include:**
- Phone: `(03) 9999 7398`
- Email: `hello@yesai.au`
- Website: `www.yesai.au`

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
cd /c/Users/peter/Downloads/CC
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
- **Complete BOTH agent AND n8n changes** when fixes are coupled (see COUPLED FIXES rule)
- **Use TodoWrite** to track multi-part fixes - don't rely on memory

## NEVER DO

- Save agents directly to agents/ without testing
- Keep multiple versions in agents/ (only latest stable)
- Overwrite source files (input ≠ output)
- Use `tool-log-error` (doesn't exist - use `tool-add-to-followup`)
- **Deploy agent fix without completing the paired n8n fix**
- **Say "DONE" when pending n8n/webhook changes remain**

---

## FILE ORGANIZATION RULES

**⚠️ NEVER save files to these root folders:**
- `CC/` (project root)
- `CC/retell/`
- `CC/n8n/`
- `CC/n8n/JSON/`

### Where Files MUST Go

| File Type | Correct Location | Example |
|-----------|------------------|---------|
| **Temp/debug JSON** | `retell/Testing/[date]/` | `temp_agent.json` → `Testing/2025-12-09/` |
| **Agent dev files** | `retell/Testing/[date]/` | New agent versions during development |
| **Stable agents** | `retell/agents/` | Only final tested version |
| **n8n workflow exports** | `n8n/JSON/active_workflows/` | Production workflows |
| **Old/archived workflows** | `n8n/JSON/archive/` | Superseded versions |
| **Debug workflow files** | `n8n/JSON/archive/` | One-off fixes, debug exports |
| **Python scripts (n8n)** | `n8n/Python/` | NOT in `n8n/JSON/` |
| **Planning docs** | Relevant subfolder or delete after | NOT in root folders |
| **Client audit reports** | `CLIENTS/[client-name]/` | NOT in `CC/` root |
| **Call logs/debug data** | `retell/Testing/[date]/` or delete | NOT in `CC/` root |

### Cleanup Rules

1. **Temp files** (`temp_*.json`, `debug_*.json`) → Delete after use or save to `Testing/`
2. **One-off scripts** → Archive to `n8n/archive/old_scripts/` or delete
3. **Old workflow versions** → Keep only latest 1-2 in `active_workflows/`, archive rest
4. **Download directories** → Clean `n8n/Python/downloads/` regularly (keep newest 2-3)
5. **Planning/changelog docs** → Move to `archive/` when complete

### Before Creating ANY File

Ask yourself:
1. Does this file already exist somewhere? → Edit existing
2. Is this temporary? → Use `Testing/[date]/` or don't save
3. Will this be needed long-term? → Put in correct permanent location
4. Is this a one-off script? → Consider not saving, or archive immediately

**If you find yourself saving to a root folder, STOP and find the correct subfolder.**

---

## PROJECT OVERVIEW

**System:** AI receptionist using RetellAI + n8n automation
**Stack:** RetellAI, n8n, AWS EC2, Docker, PostgreSQL, Cliniko
**Version:** Reignite AI Mega Receptionist v11.154

---

**Last Updated:** 2025-12-11
