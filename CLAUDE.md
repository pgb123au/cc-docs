# AI Voice Agent & Automation Knowledge Base

## ⚠️ MANDATORY COMPLETION FORMAT - ALWAYS DO THIS LAST

**After EVERY completed task**, end your response with:
```
DONE DONE DONE

Files created/modified:
• [Full absolute path as clickable link, e.g., C:\Users\peter\Downloads\CC\filename.ext]
```

This is NON-NEGOTIABLE. Every task must end with "DONE DONE DONE" and full file paths.

---

## CRITICAL SAFETY RULES

### RetellAI Simulation Tests - MANDATORY
Tests with `"tool_mocks": []` execute REAL webhooks and modify REAL Cliniko data.

| Rule | Allowed Values Only |
|------|---------------------|
| Patient Names | `Peter Ball` or `Test Test` |
| Phone Number | `0412111000` |
| Appointment Dates | Minimum 14 days from test creation |

**If ANY rule is violated → DO NOT RUN THE TEST**

### n8n PostgreSQL Cache - ALWAYS DO
- `alwaysOutputData: true` on ALL PostgreSQL nodes
- `RETURNING *;` on ALL INSERT/UPDATE statements
- NEVER use `JSON.parse()` on JSONB columns (already parsed)
- Response node BEFORE logging node

---

## MANDATORY WORKFLOWS

### GitHub Auto-Commit (REQUIRED for all file changes)

**IMPORTANT:** After creating or modifying any agent, workflow, or documentation file, **commit and push immediately without asking**. Do not ask "Would you like me to commit?" - just do it.

**Repositories:**
| Repo | Local Path | GitHub |
|------|------------|--------|
| retell-agents | `C:\Users\peter\Downloads\CC\retell` | https://github.com/pgb123au/retell-agents |
| n8n-workflows | `C:\Users\peter\Downloads\CC\n8n` | https://github.com/pgb123au/n8n-workflows |
| cc-docs | `C:\Users\peter\Downloads\CC` | https://github.com/pgb123au/cc-docs |

**After modifying CLAUDE.md or root docs:**
```bash
cd /c/Users/peter/Downloads/CC
git add CLAUDE.md && git commit -m "Update CLAUDE.md - [description]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>" && git push
```

**After creating/modifying ANY RetellAI agent:**
```bash
cd /c/Users/peter/Downloads/CC/retell
git add . && git commit -m "Add agent vX.XX_CC - [description]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>" && git push
```

**After creating/modifying ANY n8n workflow:**
```bash
cd /c/Users/peter/Downloads/CC/n8n
git add . && git commit -m "Update workflow: [name] - [description]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>" && git push
```

### RetellAI Agent Changelog (REQUIRED)

When creating a new agent version, create/update `CHANGELOG.md` in the **same folder as the new agent**:

```markdown
## vX.XX_CC - YYYY-MM-DD
**Changes:**
- [List each change made]
```

### Webhook Reference Updates (REQUIRED)

When creating a new webhook reference:
1. Save dated version: `RETELLAI_WEBHOOKS_AGENT_REFERENCE_YYYY_MM_DD.md`
2. Copy to: `RETELLAI_WEBHOOKS_CURRENT.md` (overwrites old)
3. Git commit and push both files to n8n-workflows repo

---

## QUICK REFERENCE

### Test Patient Data
- **Name:** Peter Ball
- **Patient ID:** `1805465202989210063`
- **Phone:** `0412111000`

### RetellAI Agent Naming
- **Filename:** `Reignite_AI_Mega_Receptionist_vX.XX_CC.json`
- **agent_name field:** `Reignite_AI_Mega_Receptionist_vX.XX_CC`
- **version field:** `vX.XX`
- **Location:** `C:\Users\peter\Downloads\CC\retell\Testing\`

### n8n API Scripts
```bash
cd C:\Users\peter\Downloads\CC\n8n\Python
python CC-Made-n8n_api_download_workflows.py --retell   # Download RetellAI webhooks
python CC-Made-n8n_api_download_workflows.py --all      # Download all workflows
python CC-Made-n8n_api_upload_workflow.py file.json     # Upload workflow
python CC-Made-n8n_api_check_webhooks.py                # Check for issues
```

### Valid Tool IDs
Check `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` for valid webhooks.
Common: `add-to-followup`, `book-appointment-compound`, `list-appointments`, `send-sms`

---

## CLAUDE CODE BEHAVIOR

### Before Working on RetellAI Agents
**MANDATORY:** Read these files FIRST before creating or modifying any agent JSON file:
1. `retell/RETELL_ARCHITECTURAL_PATTERNS.md` - ⚠️ **START HERE** - 5 critical rules
2. `retell/RETELL_VARIABLE_BINDING_RULES.md` - Variable binding details
3. `retell/AGENT_DEVELOPMENT_GUIDE.md` - Naming, versioning, file safety
4. `retell/Medical_Center_Receptionist_OFFICIAL_TEMPLATE.json` - Reference implementation

**THE 5 CRITICAL RETELL RULES:**
| Rule | Requirement |
|------|-------------|
| 1. Entry Node | Must be `type: "conversation"` (not function) - no silent starts |
| 2. Variable Binding | Only bind `call_id`/`patient_id` - LLM extracts conversation values |
| 3. Farewell Flow | Use `skip_response_edge` - don't wait for user response |
| 4. Call Termination | Use `type: "end"` nodes - proper SIP termination |
| 5. Global Prompt | Keep under 1000 chars - move specifics to node instructions |

### Before Working on n8n Workflows
**MANDATORY:** Read `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` for current webhook reference.

### Always Do
1. **Parallel execution** - Run independent tool calls in single message
2. **Read before edit** - Never modify files without reading first
3. **Read guides before agent/workflow work** - See mandatory reads above
4. **Test webhooks** - After n8n changes, run curl test against endpoint
5. **Show completion summary** with full file paths:
```
════════════════════════════════════════════════════════════════
✅ DONE
════════════════════════════════════════════════════════════════
Files created/modified:
• C:\Users\peter\Downloads\CC\path\to\file.json

Summary: [description]
════════════════════════════════════════════════════════════════
```

### Never Do
- Overwrite source files (input ≠ output)
- Use `tool-log-error` (doesn't exist)
- Commit files with `_temp` or `_backup` in name
- Skip GitHub commit after creating files

---

## PROJECT OVERVIEW

Production AI receptionist system using RetellAI voice agents + n8n automation workflows.

**Tech Stack:** RetellAI, n8n, AWS EC2, Docker, PostgreSQL, Cliniko

**Current Version:** Reignite AI Mega Receptionist v10+

---

## DIRECTORY INDEX

### RetellAI Agents (`/retell/`)
| Document | Purpose |
|----------|---------|
| `RETELL_ARCHITECTURAL_PATTERNS.md` | ⚠️ **START HERE** - 5 critical rules from official template |
| `RETELL_VARIABLE_BINDING_RULES.md` | When to bind vs not bind parameters |
| `Medical_Center_Receptionist_OFFICIAL_TEMPLATE.json` | Official Retell reference implementation |
| `AGENT_DEVELOPMENT_GUIDE.md` | Naming, versioning, file safety rules |
| `RETELLAI_MASTER_GUIDE_FOR_CLAUDE.md` | Complete agent building guide |
| `RETELLAI_DEBUGGING_AND_VALIDATION_GUIDE.md` | Troubleshooting |
| `Testing/` | Active agent development folder |

### n8n Workflows (`/n8n/`)
| Document | Purpose |
|----------|---------|
| `Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` | **Current webhook reference** (always up-to-date) |
| `Webhooks Docs/N8N_CACHE_ISSUES_COMPLETE_FIX_GUIDE.md` | Cache debugging |
| `Python/N8N_API_WORKFLOW_MANAGEMENT_GUIDE.md` | API script docs |
| `JSON/` | Workflow exports |

### Infrastructure
| Document | Purpose |
|----------|---------|
| `README_AWS_n8n_server_docs.md` | AWS/Docker/n8n server docs index |
| `Reignite Health AI - Master Environment Reference.md` | SSH, versions, stats |

### Project-Specific
| Document | Purpose |
|----------|---------|
| `agents/reignite-receptionist/CLAUDE.md` | Reignite project rules |
| `shared/CLAUDE.md` | Global development principles |

---

## GETTING STARTED

1. Read this file for critical rules
2. Read `Reignite Health AI - Master Environment Reference.md` for environment details
3. For RetellAI agents: `retell/AGENT_DEVELOPMENT_GUIDE.md`
4. For n8n webhooks: `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md`

---

**Last Updated:** 2025-11-29
