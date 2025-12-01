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

## FILE LOCATIONS (WHERE TO SAVE)

### RetellAI Agents
| Purpose | Location | Notes |
|---------|----------|-------|
| **Active Development** | `retell/Testing/[current-date]/` | e.g., `25-11-29a/` |
| **Production/Stable** | `retell/agents/` | Only latest stable version |
| **Official Templates** | `retell/templates/` | Reference templates |
| **Old Versions** | `retell/archive/agent-history/` | Auto-ignored by git |

**Naming:** `Reignite_AI_Mega_Receptionist_vX.XX_CC.json`

### n8n Workflows
| Purpose | Location |
|---------|----------|
| **Current Production** | `n8n/JSON/active_workflows/` |
| **Old Backups** | `n8n/JSON/archive/` |

### Documentation
| Purpose | Location |
|---------|----------|
| **Webhook Reference** | `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` |
| **Dated Webhook Refs** | `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_AGENT_REFERENCE_YYYY_MM_DD.md` |
| **Old Webhook Docs** | `n8n/Webhooks Docs/archive/` |

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

### RetellAI Python Tools
```bash
cd C:\Users\peter\Downloads\CC\retell\scripts

# Basic auditor (fast, catches common issues)
python retell_audit.py agent.json              # Audit specific file
python retell_audit.py                         # Audit most recent agent
python retell_audit.py agent.json -o report.md # Generate markdown report

# Deep auditor (comprehensive, catches ALL bug patterns from v11.40-v11.64)
python retell_deep_audit.py agent.json         # Full deep audit
python retell_deep_audit.py agent.json -o report.md  # Detailed report

# Agent utilities (for fix scripts)
from agent_utils import AgentEditor
editor = AgentEditor("agent_v11.64.json")
editor.set_version("11.65")
editor.change_edge_destination("edge-id", "new-node")
editor.save("agent_v11.65.json")
```

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
| 3 | `retell/AGENT_DEVELOPMENT_GUIDE.md` | 5 critical rules, variable binding, naming, versioning |
| 4 | `retell/WHITELISTED_PATTERNS.md` | **Intentional design choices - DO NOT "fix" these** |

### Before n8n Work
| File | Content |
|------|---------|
| `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` | Webhook specs + Agent variable mappings (Single Source of Truth) |

---

## THE 5 CRITICAL RETELL RULES

| # | Rule | Requirement |
|---|------|-------------|
| 1 | Entry Node | Must be `type: "conversation"` (not function) |
| 2 | Variable Binding | Only bind `call_id`/`patient_id` - LLM extracts rest |
| 3 | Farewell Flow | Use `skip_response_edge` - don't wait for response |
| 4 | Call Termination | Use `type: "end"` nodes for proper SIP termination |
| 5 | Global Prompt | Keep under 1000 chars |

## ANTI-PATTERNS (NEVER DO)

| # | Anti-Pattern | Fix |
|---|--------------|-----|
| 1 | Mixed edge types (`skip_response_edge` + `edges`) | Use only one; set `edges: []` if using skip |
| 2 | Function node without `response_variables` | Always add with at least `"success": "success"` |
| 3 | Entry node without timeout edge | Add edge: `"No response for 15 seconds"` |
| 4 | Function node without error edge | Add edge to `node-human-transfer-prep` |
| 5 | Variable collision (`village` = `class_village`) | Use distinct names: `class_village` |
| 6 | Instructions over 1000 chars | Split node or move to tool description |
| 7 | Duplicate nodes diverging | Update BOTH when changing one |

## PARAMETER BINDING RULES

| Source | How to Bind | Example |
|--------|-------------|---------|
| System-provided | `"{{var}}"` | `"call_id": "{{call_id}}"` |
| Tool response | `"{{var}}"` | `"patient_id": "{{patient_id}}"` |
| User spoke it | `""` (empty) | `"first_name": ""` |
| Not needed | Omit key | Don't include it |

## JSON VALIDATION RULES

| Rule | Requirement |
|------|-------------|
| Tool Parameters | MUST have `"type": "object"` at top level |
| Dynamic Variables | ALL values MUST be strings |
| Response Engine | Use `response_engine` NOT `llm_websocket_url` |
| start_speaker | REQUIRED - "agent" or "user" |
| Node/Edge IDs | Must be unique |
| Function nodes | MUST have `response_variables` block |
| Entry node | MUST have timeout edge |
| End node | MUST have `type: "end"` with NO edges |

---

## DIRECTORY STRUCTURE

```
CC/
├── CLAUDE.md                 ← This file (master config)
├── Reignite Health AI - Master Environment Reference.md
│
├── retell/                   ← RetellAI agents repo
│   ├── agents/               ← PRODUCTION: Latest stable only
│   ├── Testing/              ← DEVELOPMENT: Current work
│   │   └── [date-folder]/    ← Active session (e.g., 25-11-29a/)
│   ├── templates/            ← Official RetellAI templates
│   ├── guides/               ← Learning docs & guides
│   ├── scripts/              ← Reusable Python tools
│   │   ├── agent_utils.py    ← AgentEditor class for modifications
│   │   ├── retell_audit.py   ← Basic auditor (fast)
│   │   ├── retell_deep_audit.py ← Deep auditor (catches all bug patterns)
│   │   └── validate_agent_edges.py ← Edge-specific validator
│   ├── archive/              ← Old versions (git-ignored)
│   │   └── agent-history/    ← All historical versions
│   ├── RETELLAI_REFERENCE.md     ← API reference
│   ├── RETELLAI_JSON_SCHEMAS.md  ← JSON structures
│   └── AGENT_DEVELOPMENT_GUIDE.md ← Development guide (includes patterns)
│
├── n8n/                      ← n8n workflows repo
│   ├── Webhooks Docs/
│   │   ├── RETELLAI_WEBHOOKS_CURRENT.md  ← PRIMARY reference
│   │   └── archive/
│   ├── Guides Docs/
│   ├── AWS Docs/
│   ├── JSON/
│   │   ├── active_workflows/ ← Current production
│   │   └── archive/
│   └── Python/               ← API scripts
│
├── agents/reignite-receptionist/
└── shared/
```

---

## WORKFLOW: Creating New Agent Version

1. **Read mandatory docs** (RETELLAI_REFERENCE.md, JSON_SCHEMAS.md)
2. **Copy from** `retell/agents/` (latest stable) or current Testing folder
3. **Increment version** in filename AND `agent_name` field
4. **Save to** `retell/Testing/[current-date]/`
5. **Audit** with `python retell/scripts/retell_audit.py <file>` - fix any CRITICAL issues
6. **Validate** with `/validate-agent` command
7. **When stable** → Copy to `retell/agents/` (replaces old)
8. **Git commit** both locations

## WORKFLOW: Fixing Agent Issues

1. **Audit** with `python retell/scripts/retell_audit.py agent.json -o report.md`
2. **Review** the markdown report - prioritize CRITICAL, then WARNING
3. **Write fix script** using `AgentEditor` class from `agent_utils.py`:
   ```python
   from agent_utils import AgentEditor
   editor = AgentEditor("v11.64.json")
   editor.change_edge_destination("edge-id", "correct-node")
   editor.remove_node_parameter("node-id", "bad_param")
   editor.increment_version()
   editor.save("v11.65.json")
   ```
4. **Re-audit** the fixed version to verify all CRITICAL issues resolved
5. **Git commit** both the fix script and new agent version

---

## ALWAYS DO

1. Read guides before agent/workflow work
2. Run independent tool calls in parallel
3. Read files before editing
4. Commit and push after file changes
5. Create CHANGELOG.md with new agent versions
6. Save development work to Testing/, stable to agents/

## NEVER DO

- Save agents directly to agents/ without testing
- Keep multiple versions in agents/ (only latest stable)
- Commit call transcripts or audit files
- Overwrite source files (input ≠ output)
- Use `tool-log-error` (doesn't exist)

---

## PROJECT OVERVIEW

**System:** AI receptionist using RetellAI + n8n automation
**Stack:** RetellAI, n8n, AWS EC2, Docker, PostgreSQL, Cliniko
**Version:** Reignite AI Mega Receptionist v11.59+

---

**Last Updated:** 2025-12-01
