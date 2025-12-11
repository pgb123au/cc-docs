---
description: Full autonomous agent fix process - combines audits, fixes agent, deploys (17 steps)
---

# RetellAI Agent Fix Process - AUTO

Full autonomous process to fix a RetellAI agent based on bug audit documents.

## First: Provide Bug Documents

Before I begin, please provide the bug/audit document paths. These can be:
- Local file paths (e.g., `C:\Users\peter\Downloads\bugs v11.XXX GPT.md`)
- Multiple documents (GPT audit, Gemini audit, manual notes, etc.)

**Please provide 1 or more bug document paths now.** I'll wait for your input.

Format:
```
Bug docs:
1. [path or paste content]
2. [path or paste content]
...
```

---

## After You Provide Bug Docs

I will execute this 17-step process:

### PART 1: Combine & Approve (Step 1)

**Step 1: COMBINE ALL AUDITS**
- Read all bug documents you provided
- Combine with my own audit findings (if I've already reviewed the agent)
- Deduplicate issues
- Categorize each as: AGENT / WEBHOOK / DATABASE / COUPLED
- Output `COMBINED_ISSUES_v[version].md`

**>>> STOP FOR YOUR APPROVAL <<<**
You review the combined list and either approve or request changes.

---

### PART 2: Autonomous Execution (Steps 2-17)

After your approval, I execute ALL remaining steps automatically:

| Step | Description |
|------|-------------|
| 2 | Confirm scope, create todo list |
| 3 | Deep investigation (locate, validate, categorize) |
| **3.5** | **VERIFY webhook claims against LIVE endpoints** |
| 4 | Generate FIND/REPLACE strings |
| 5 | Conflict & impact analysis (6 checks) |
| 6 | Generate scripts (preflight, apply, verify) |
| 7 | Execute scripts |
| 8 | Agent validation |
| 9 | Complete COUPLED fixes (webhook first, then agent) |
| 10 | Deploy agent (NOT live yet) |
| 11 | Webhook-only & database-only fixes |
| 12 | Go live (connect phone lines, commit) |
| 13 | Zero deferral check |
| 14 | Final report |
| 15 | Update webhook docs (if changed) |
| 16 | Capture learnings |
| 17 | Archive false positives for future reference |

---

## Step 3.5: VERIFY WEBHOOK CLAIMS (MANDATORY)

**For ANY audit issue claiming webhook response fields are wrong:**

1. **CALL THE LIVE WEBHOOK** with test data:
   ```bash
   curl -X POST "https://auto.yr.com.au/webhook/retell/[endpoint]" \
     -H "Content-Type: application/json" \
     -d '{"call_id":"verify_test","patient_id":"1805465202989210063",...}'
   ```

2. **COMPARE actual response** to audit claims:
   | Audit Claims | Actual Response | Match? |
   |--------------|-----------------|--------|
   | Field X exists | ... | YES/NO |
   | Field Y is named Z | ... | YES/NO |

3. **If audit claim is FALSE:**
   - Mark issue as `INVALID - VERIFIED FALSE`
   - Do NOT apply the "fix"
   - Document in VALIDATED_ISSUES as false positive

**NEVER change response_variables based on audit claims without live verification.**

---

## False Positive Detection

Audits (GPT, Gemini, manual) can make incorrect claims. Watch for:

| Red Flag | Action |
|----------|--------|
| "Webhook returns X not Y" | CALL the webhook, verify actual fields |
| "Field mapping is wrong" | Compare current mapping to live response |
| "response_variables outdated" | Test if current agent works before "fixing" |
| "Tool schema doesn't match webhook" | Verify against live endpoint |

**If the current agent WORKS for that flow, investigate thoroughly before changing.**

### Real Example: v11.200 C4/C5 Disaster

GPT audit claimed `get-class-schedule` webhook returns `slots` instead of `upcoming_sessions`. This was FALSE. The "fix" broke all class booking. Always verify.

---

## Critical Rules

1. **DO NOT RUSH** - Complete each step thoroughly
2. **DO NOT SKIP VALIDATION** - Loop until each gate passes
3. **ZERO DEFERRAL** - Complete ALL fixes, no "later" allowed
4. **SCHEMA VERIFICATION** - Before writing JSON, read existing elements first
5. **OUTPUT FULL PATHS** - Show Windows paths for all created files
6. **WEBHOOK VERIFICATION** - Any audit claim about webhook response fields MUST be verified by calling the live endpoint. Audits can be wrong.

## JSON Schema Rules

Before writing ANY new node/edge JSON:
| Wrong | Correct |
|-------|---------|
| `target` | `destination_node_id` |
| `condition` | `transition_condition` |
| `id` (nodes) | `node_id` |
| `id` (tools) | `tool_id` |

**NEVER write JSON from memory - always verify against actual agent file first.**

## Test Data

All tests use Peter Ball:
- Patient ID: `1805465202989210063`
- Phone: `0412111000`

## Files Created

| File | Step |
|------|------|
| COMBINED_ISSUES_v[ver].md | 1 |
| VALIDATED_ISSUES_v[ver].md | 3/3.5 |
| fix_checklist.md | 4/5 |
| preflight.py, apply_fixes.py, verify_fixes.py | 6 |
| agent_fixed.json | 7 |
| LEARNINGS_v[ver].md | 16 |

## VALIDATED_ISSUES Format

For each issue, document verification status:

```markdown
### Issue C4: get-class-schedule Response Mapping
- **Audit Claim:** Webhook returns `slots` not `upcoming_sessions`
- **Verification:** Called live endpoint with test data
- **Actual Response:** `{"success":true,"upcoming_sessions":[...],...}`
- **Verdict:** INVALID - FALSE POSITIVE
- **Action:** Do not fix - current agent is correct
```

---

**Now: Please provide the bug document path(s).**
