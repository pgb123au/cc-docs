# AI Voice Agent & Automation Knowledge Base

## MANDATORY COMPLETION FORMAT

**After EVERY completed task**, end your response with:
```
DONE DONE DONE

Files created/modified:
• [Full absolute path, e.g., C:\Users\peter\Downloads\CC\filename.ext]
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

### n8n PostgreSQL Cache
- `alwaysOutputData: true` on ALL PostgreSQL nodes
- `RETURNING *;` on ALL INSERT/UPDATE statements
- NEVER use `JSON.parse()` on JSONB columns (already parsed)
- Response node BEFORE logging node

---

## GIT AUTO-COMMIT (REQUIRED)

**Commit and push immediately after creating/modifying files. Do not ask.**

| Repo | Local Path | GitHub |
|------|------------|--------|
| retell-agents | `C:\Users\peter\Downloads\CC\retell` | github.com/pgb123au/retell-agents |
| n8n-workflows | `C:\Users\peter\Downloads\CC\n8n` | github.com/pgb123au/n8n-workflows |
| cc-docs | `C:\Users\peter\Downloads\CC` | github.com/pgb123au/cc-docs |

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

### Agent Naming
- **File:** `Reignite_AI_Mega_Receptionist_vX.XX_CC.json`
- **Location:** `retell/Testing/`

### n8n API Scripts
```bash
cd C:\Users\peter\Downloads\CC\n8n\Python
python CC-Made-n8n_api_download_workflows.py --retell   # Download webhooks
python CC-Made-n8n_api_upload_workflow.py file.json     # Upload workflow
python CC-Made-n8n_api_check_webhooks.py                # Check issues
```

---

## MANDATORY READS

### Before RetellAI Work
| Priority | File | Content |
|----------|------|---------|
| 1 | `retell/RETELLAI_REFERENCE.md` | API, Events, Variables, Models |
| 2 | `retell/RETELLAI_JSON_SCHEMAS.md` | Valid JSON structures |
| 3 | `retell/RETELL_ARCHITECTURAL_PATTERNS.md` | 5 critical rules |
| 4 | `retell/AGENT_DEVELOPMENT_GUIDE.md` | Naming, versioning |

### Before n8n Work
| File | Content |
|------|---------|
| `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` | Current webhook reference |

---

## THE 5 CRITICAL RETELL RULES

| # | Rule | Requirement |
|---|------|-------------|
| 1 | Entry Node | Must be `type: "conversation"` (not function) |
| 2 | Variable Binding | Only bind `call_id`/`patient_id` - LLM extracts rest |
| 3 | Farewell Flow | Use `skip_response_edge` - don't wait for response |
| 4 | Call Termination | Use `type: "end"` nodes for proper SIP termination |
| 5 | Global Prompt | Keep under 1000 chars |

## JSON VALIDATION RULES

| Rule | Requirement |
|------|-------------|
| Tool Parameters | MUST have `"type": "object"` at top level |
| Dynamic Variables | ALL values MUST be strings |
| Response Engine | Use `response_engine` NOT `llm_websocket_url` |
| start_speaker | REQUIRED - "agent" or "user" |
| Node/Edge IDs | Must be unique |

---

## DIRECTORY STRUCTURE

```
CC/
├── CLAUDE.md                 ← This file (master config)
├── Reignite Health AI - Master Environment Reference.md
│
├── retell/                   ← RetellAI agents repo
│   ├── RETELLAI_REFERENCE.md       ← CRITICAL: API reference
│   ├── RETELLAI_JSON_SCHEMAS.md    ← CRITICAL: JSON validation
│   ├── AGENT_DEVELOPMENT_GUIDE.md
│   ├── RETELL_ARCHITECTURAL_PATTERNS.md
│   ├── RETELL_VARIABLE_BINDING_RULES.md
│   ├── guides/               ← Learning docs & guides
│   ├── templates/            ← Official RetellAI templates
│   ├── Testing/              ← Active development
│   └── archive/              ← Old versions
│
├── n8n/                      ← n8n workflows repo
│   ├── Webhooks Docs/
│   │   ├── RETELLAI_WEBHOOKS_CURRENT.md  ← PRIMARY reference
│   │   └── archive/          ← Old webhook docs
│   ├── Guides Docs/          ← Operational guides
│   ├── AWS Docs/             ← Infrastructure docs
│   ├── JSON/                 ← Workflow exports
│   │   ├── active_workflows/ ← Current production
│   │   └── archive/          ← Old backups
│   └── Python/               ← API scripts
│
├── agents/reignite-receptionist/  ← Project-specific rules
└── shared/                        ← Global principles
```

---

## ALWAYS DO

1. Read guides before agent/workflow work
2. Run independent tool calls in parallel
3. Read files before editing
4. Commit and push after file changes
5. Create CHANGELOG.md with new agent versions

## NEVER DO

- Overwrite source files (input ≠ output)
- Use `tool-log-error` (doesn't exist)
- Commit files with `_temp` or `_backup`
- Skip git commit after creating files

---

## PROJECT OVERVIEW

**System:** AI receptionist using RetellAI + n8n automation
**Stack:** RetellAI, n8n, AWS EC2, Docker, PostgreSQL, Cliniko
**Version:** Reignite AI Mega Receptionist v10+

---

**Last Updated:** 2025-11-29
