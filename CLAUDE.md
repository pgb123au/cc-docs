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

---

## QUICK REFERENCE

### Test Patient
- **Name:** Peter Ball | **ID:** `1805465202989210063` | **Phone:** `0412111000`

### Production Phone Numbers
- `+61288800226` - Main Sydney number
- `+61240620999` - Secondary number

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
```

---

## MANDATORY READS

**Read BEFORE working on RetellAI agents:**

| Priority | File | Why |
|----------|------|-----|
| 1 | `retell/RETELLAI_REFERENCE.md` | API, Events, Variables |
| 2 | `retell/RETELLAI_JSON_SCHEMAS.md` | Valid JSON, node types, validation rules |
| 3 | `retell/AGENT_DEVELOPMENT_GUIDE.md` | 5 critical rules, variable binding, anti-patterns |
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

## ALWAYS DO

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
**Version:** Reignite AI Mega Receptionist v11.109

---

**Last Updated:** 2025-12-03
