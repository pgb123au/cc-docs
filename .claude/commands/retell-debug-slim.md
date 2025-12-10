---
description: Create slim debug package (max 10 files) with live agent, call, docs, and essential webhooks
---

# Create Slim Debug Package

Create a streamlined debug package for external audit with maximum 10 files in a single folder.

**Key differences from `/retell-debug-package`:**
- Single flat folder (no subfolders)
- Maximum 10 files
- Combined reference docs (5 docs → 1 file)
- Only 4 essential webhooks (2 individual + 2 class)
- Single diagnostic report

---

## What Gets Packaged (9 files max)

| # | File | Source |
|---|------|--------|
| 1 | `agent_LIVE.json` | RetellAI API (live) |
| 2 | `call_latest.json` | RetellAI API (most recent) |
| 3 | `REFERENCE_DOCS.md` | 5 docs combined |
| 4 | `RetellAI_-_Lookup_Caller_by_Phone_*.json` | n8n API (shared webhook) |
| 5 | `RetellAI_-_Book_Appointment_Compound_*.json` | n8n API (individual booking) |
| 6 | `RetellAI_-_Get_Class_Schedule_*.json` | n8n API (class booking) |
| 7 | `RetellAI_-_Enroll_Class_Single_*.json` | n8n API (class enrollment) |
| 8 | `DIAGNOSTIC_REPORT.md` | Generated |
| 9 | `README.md` | Generated |

---

## Execution Steps

### Step 1: Create Folder

```bash
mkdir -p "C:/Users/peter/Downloads/CC/retell/Testing/$(date +%Y-%m-%d)-slim-debug"
```

### Step 2: Fetch Live Agent from RetellAI API

**MUST fetch from API - do not use local files.**

```python
from retell import Retell
import json

# Load API key from C:\Users\peter\Downloads\Retell_API_Key.txt
client = Retell(api_key=api_key)

# Get production agent from phone numbers
numbers = client.phone_number.list()
for n in numbers:
    if hasattr(n, 'inbound_agent_id') and n.inbound_agent_id:
        agent_id = n.inbound_agent_id
        break

# Get agent + conversation flow
agent = client.agent.retrieve(agent_id=agent_id)
cf_id = agent.response_engine.conversation_flow_id
flow = client.conversation_flow.retrieve(cf_id)

# Combine and save
export = {'agent': agent.model_dump(), 'conversation_flow': flow.model_dump()}
# Save as agent_LIVE.json
```

**VERIFY file size is >200KB** (small files = missing conversation flow)

### Step 3: Fetch Latest Call

```python
calls = client.call.list(limit=1)
call = calls[0].model_dump()
# Save as call_latest.json
```

### Step 4: Create REFERENCE_DOCS.md

Combine these 5 docs into a SINGLE file with section headers:

1. `retell/RETELLAI_REFERENCE.md`
2. `retell/RETELLAI_JSON_SCHEMAS.md`
3. `retell/AGENT_DEVELOPMENT_GUIDE.md`
4. `retell/WHITELISTED_PATTERNS.md`
5. `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md`

Structure:
```markdown
# Reference Documentation (5 Essential Docs)
Generated: [date]
Agent Version: [version]

---
## TABLE OF CONTENTS
1. RetellAI Platform Reference
2. RetellAI JSON Schemas
3. Agent Development Guide
4. Whitelisted Patterns (Do Not Fix)
5. Webhook API Reference

---
# SECTION 1: RetellAI Platform Reference
[FULL CONTENTS]

# SECTION 2: RetellAI JSON Schemas
[FULL CONTENTS]

... etc
```

### Step 5: Download 4 Essential Webhooks from n8n API

```bash
N8N_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4"
```

Find and download these 4 webhooks (use original filenames):

| Webhook | Flow Type |
|---------|-----------|
| `Lookup Caller by Phone` | Shared (both flows) |
| `Book Appointment Compound` | Individual booking |
| `Get Class Schedule` | Class booking |
| `Enroll Class Single` | Class booking |

**Finding workflows:**
1. List all workflows: `GET /api/v1/workflows?limit=250`
2. Filter for active workflows matching the names above
3. Download each: `GET /api/v1/workflows/{id}`
4. Save with original n8n name (e.g., `RetellAI_-_Lookup_Caller_by_Phone_v2.8_SUPER_LOOKUP.json`)

### Step 6: Create DIAGNOSTIC_REPORT.md

Include:
- Agent summary (name, nodes, tools, file size)
- Last call summary (call_id, status, duration, disconnection)
- Webhooks included table
- File manifest with sizes
- Audit guidelines
- Test patient info

### Step 7: Create README.md

Include:
- Package contents table
- Quick start guide
- Webhooks by flow type
- Safe to share note

---

## Output Format

```
=== SLIM DEBUG PACKAGE CREATED ===

Folder: C:\Users\peter\Downloads\CC\retell\Testing\YYYY-MM-DD-slim-debug

Contents:
  1. agent_LIVE.json (XXX KB)
  2. call_latest.json (XXX KB)
  3. REFERENCE_DOCS.md (XX KB - 5 docs combined)
  4. RetellAI_-_Lookup_Caller_by_Phone_*.json
  5. RetellAI_-_Book_Appointment_Compound_*.json
  6. RetellAI_-_Get_Class_Schedule_*.json
  7. RetellAI_-_Enroll_Class_Single_*.json
  8. DIAGNOSTIC_REPORT.md
  9. README.md

Agent Version: vX.XXX
Total Files: 9 (under 10 limit)

Ready for external review.

DONE DONE DONE
```

---

## Notes

- **Single folder** - No subfolders like GEMINI or SHARED
- **Max 10 files** - Currently 9, room for 1 more if needed
- **Live data only** - Agent and call fetched from APIs, not local files
- **Original webhook names** - Keep n8n filenames unchanged
- **Safe to share** - Contains NO credentials or API keys
- **Combined docs** - 5 reference docs → 1 REFERENCE_DOCS.md file

---

## Test Patient (Safe to Use)

| Field | Value |
|-------|-------|
| Name | Peter Ball |
| Patient ID | 1805465202989210063 |
| Phone | 0412111000 |

---

*Last Updated: 2025-12-11*
