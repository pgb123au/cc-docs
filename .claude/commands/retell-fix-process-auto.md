---
description: Full autonomous RetellAI agent fix process with 110% certainty protocol (19 steps)
---

# RetellAI Agent Fix Process - AUTO (v3.0)

Full autonomous process to fix a RetellAI agent based on bug audit documents.
Includes 110% Certainty Protocol, False Positive Detection, and Rollback Safety.

---

## The 110% Mindset

> "Measure twice, cut once."

- **Rushing causes bugs** - Take the time to understand
- **Assumptions are dangerous** - Verify everything
- **Documentation prevents repeat mistakes** - Write it down
- **Testing catches surprises** - Test more than you think necessary
- **Confidence comes from thoroughness** - When you're 110% sure, you'll know

---

## First: Provide Bug Documents

Before I begin, please provide the bug/audit document paths:
- Local file paths (e.g., `C:\Users\peter\Downloads\bugs v11.XXX GPT.md`)
- Multiple documents (GPT audit, Gemini audit, Claude audit, manual notes)

**Please provide 1 or more bug document paths now.** I'll wait for your input.

Format:
```
Bug docs:
1. [path or paste content] (source: GPT/GEM/CLAUDE/MANUAL)
2. [path or paste content] (source: GPT/GEM/CLAUDE/MANUAL)
```

---

## Process Overview (19 Steps)

After you provide bug docs, I execute this process:

| Phase | Steps | Description |
|-------|-------|-------------|
| **PREPARE** | 1-2.5 | Combine audits, verify certainty |
| **INVESTIGATE** | 3-4.5 | Scope, investigate, verify webhooks |
| **PLAN** | 5-6 | Generate fixes, analyze conflicts |
| **EXECUTE** | 7-12 | Apply fixes, validate, deploy |
| **GO LIVE** | 13-14 | Activate, verify zero deferral |
| **VERIFY** | 15-16 | Test, generate report |
| **DOCUMENT** | 17-19 | Update docs, learnings, false positives |

---

## PHASE 1: PREPARE

### Step 1: COMBINE ALL AUDITS

- Read all bug documents you provided
- **Tag each issue with its SOURCE** (GPT, GEM, CLAUDE, MANUAL)
- Combine with my own audit findings (if I've already reviewed the agent)
- Deduplicate issues (keep source attribution)
- Categorize each as: `AGENT` / `WEBHOOK` / `DATABASE` / `COUPLED`
- Output: `COMBINED_ISSUES_v[version].md`

**>>> STOP FOR YOUR APPROVAL <<<**
You review the combined list and either approve or request changes.

---

### Step 2: 110% CERTAINTY GATE

Before ANY fix, I must answer YES to ALL:

| Question | Required |
|----------|----------|
| Do I understand the ROOT CAUSE? | YES |
| Have I VERIFIED assumptions with live data/code? | YES |
| Do I know EXACTLY what to change? | YES |
| Do I know what SIDE EFFECTS this could have? | YES |
| Have I checked if this affects OTHER components? | YES |
| Can I EXPLAIN the fix to a 5-year-old? | YES |

**If ANY answer is NO** → Go to Step 2.5

---

### Step 2.5: INVESTIGATION LOOP (if not 110% sure)

Repeat until 110% certain:

1. **Read the actual code/config** - not from memory
2. **Trace the data flow** - inputs → processing → outputs
3. **Check logs/errors** - what ACTUALLY happened vs assumed
4. **Test current behavior** - verify the problem exists as described
5. **Search for similar patterns** - how was this solved elsewhere?
6. **Verify against live systems** - webhooks, APIs, databases
7. **Document findings** - capture what I learned

**Loop back to Step 2** after each investigation round.

---

## PHASE 2: INVESTIGATE

### Step 3: CONFIRM SCOPE & CREATE TODO LIST

**Scope Confirmation:**
- [ ] Current agent version identified (from `retell/agents/` or `Testing/`)
- [ ] All affected nodes/edges listed
- [ ] All affected webhooks listed
- [ ] All affected database tables listed
- [ ] Coupled fixes identified (agent + webhook together)

**Create TodoWrite list with:**
- One item per fix (tagged AGENT/WEBHOOK/DATABASE/COUPLED)
- Dependencies noted (which fixes must happen first)
- Estimated complexity (simple/medium/complex)

---

### Step 4: DEEP INVESTIGATION

For each issue, investigate:

| Check | Action |
|-------|--------|
| **Locate** | Find exact file, node, line, webhook |
| **Validate** | Confirm the bug exists (don't trust audit blindly) |
| **Categorize** | AGENT / WEBHOOK / DATABASE / COUPLED |
| **Dependencies** | What else touches this code? |
| **Current behavior** | What happens NOW with this bug? |
| **Expected behavior** | What SHOULD happen after fix? |

Output: `VALIDATED_ISSUES_v[version].md` with verification status for each issue.

---

### Step 4.5: VERIFY WEBHOOK CLAIMS (MANDATORY)

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

3. **If audit claim is FALSE:**
- Mark issue as `INVALID - VERIFIED FALSE`
- Do NOT apply the "fix"
- Record in source-specific false positive list
- Document in VALIDATED_ISSUES

**Red flags to verify (never trust without testing):**
| Claim Type | Action |
|------------|--------|
| "Webhook returns X not Y" | CALL the webhook, verify actual fields |
| "Field mapping is wrong" | Compare current mapping to live response |
| "response_variables outdated" | Test if current agent works before "fixing" |
| "Tool schema doesn't match webhook" | Verify against live endpoint |
| "Edge condition isn't handled" | Test the actual flow first |
| "Variable is never set" | Trace the actual data flow |

**⚠️ NEVER change response_variables based on audit claims without live verification.**

**Real Example - v11.200 C4/C5 Disaster:**
GPT claimed `get-class-schedule` returns `slots` instead of `upcoming_sessions`. FALSE. The "fix" broke all class booking. Always verify.

---

## PHASE 3: PLAN

### Step 5: GENERATE FIND/REPLACE STRINGS

For EACH validated fix, document:

```markdown
### Fix [ID]: [Description]
**Source:** [GPT/GEM/CLAUDE/MANUAL]
**Category:** [AGENT/WEBHOOK/DATABASE/COUPLED]
**Root Cause:** [Why this bug exists]

**BEFORE:**
```json
[exact current code/config - copy from file]
```

**AFTER:**
```json
[exact new code/config]
```

**Side Effects Considered:**
- [List potential impacts]
- [How they were mitigated]

**Explanation (5-year-old version):**
[Simple explanation of what's changing and why]
```

Output: `fix_checklist.md` with all BEFORE/AFTER pairs.

---

### Step 6: CONFLICT & IMPACT ANALYSIS (6 Checks)

Run these 6 checks before applying ANY fix:

| # | Check | How to Verify | Pass? |
|---|-------|---------------|-------|
| 1 | **No duplicate node_ids** | Search agent for the new node_id | |
| 2 | **No broken edges** | All destination_node_id values exist | |
| 3 | **No orphan nodes** | All nodes reachable from start | |
| 4 | **Variable consistency** | Variables set before use | |
| 5 | **Tool schema matches webhook** | Compare tool params to webhook docs | |
| 6 | **No conflicting fixes** | Fixes don't overwrite each other | |

**If ANY check fails** → Revise the fix before proceeding.

---

## PHASE 4: EXECUTE

### Step 7: BACKUP & VERSION INCREMENT

**Before ANY changes:**

1. **Backup current agent:**
```bash
cp "retell/agents/[current_agent].json" "retell/Testing/[date]/[agent]_BACKUP.json"
```

2. **Increment version:**
- Filename: `Reignite_AI_Mega_Receptionist_vX.XX_CC.json` → increment XX
- Inside file: Update `agent_name` field to match

3. **Create working copy in Testing folder:**
```bash
cp "retell/agents/[current].json" "retell/Testing/[date]/[new_version].json"
```

---

### Step 8: GENERATE SCRIPTS

Create these Python scripts in `retell/Testing/[date]/`:

**preflight.py** - Validates before changes:
```python
# Checks:
# - Agent JSON is valid
# - All node_ids unique
# - All edges point to valid nodes
# - No circular references in logic_split
```

**apply_fixes.py** - Applies FIND/REPLACE:
```python
# For each fix:
# - Load agent JSON
# - Find old_string exactly
# - Replace with new_string
# - Save to new file (never overwrite source)
```

**verify_fixes.py** - Confirms changes applied:
```python
# For each fix:
# - Verify old_string no longer exists
# - Verify new_string exists
# - Run agent validator
```

---

### Step 9: EXECUTE SCRIPTS

Run in order:
```bash
cd /c/Users/peter/Downloads/CC/retell/Testing/[date]

# 1. Preflight check
python preflight.py [agent].json

# 2. Apply fixes (outputs agent_fixed.json)
python apply_fixes.py [agent].json

# 3. Verify fixes applied
python verify_fixes.py agent_fixed.json
```

**If ANY script fails** → Fix the issue before continuing.

---

### Step 10: AGENT VALIDATION

Run the official validator:
```bash
cd /c/Users/peter/Downloads/CC/retell/scripts
python retell_agent_validator.py "../Testing/[date]/agent_fixed.json" --fix
```

**Must pass with:**
- 0 CRITICAL errors
- 0 HIGH errors
- Warnings acceptable (review each)

**Then run audit:**
```bash
python retell_audit.py "../Testing/[date]/agent_fixed.json" -o audit_report.md
```

---

### Step 11: COMPLETE COUPLED FIXES

For fixes requiring BOTH agent AND webhook changes:

**Order matters:**
1. **Webhook FIRST** - Update n8n, test endpoint works
2. **Agent SECOND** - Update tool schema/response_variables to match

**For each coupled fix:**
```markdown
### COUPLED-1: [Description]

**Webhook changes:**
- Endpoint: [URL]
- Change: [What changed]
- Tested: [ ] curl returns expected response

**Agent changes:**
- Node: [node_id]
- Change: [What changed]
- Depends on webhook: [YES - must deploy webhook first]
```

**⚠️ NEVER say "DONE" with webhook changes still pending.**

---

### Step 12: DEPLOY AGENT (NOT LIVE YET)

Deploy to RetellAI WITHOUT connecting phone lines:

```bash
cd /c/Users/peter/Downloads/CC/retell/scripts
python deploy_agent.py "../Testing/[date]/agent_fixed.json"
```

**Verify deployment:**
- [ ] Agent appears in RetellAI dashboard
- [ ] Version number matches
- [ ] No phone lines connected yet

---

### Step 13: WEBHOOK & DATABASE FIXES

**For webhook-only fixes:**
1. Download current workflow from n8n
2. Apply changes
3. Upload via n8n API
4. Test endpoint with curl

```bash
# Download
cd /c/Users/peter/Downloads/CC/n8n/Python
python CC-Made-n8n_api_download_workflows.py --retell

# After editing, upload (filter to required fields only)
curl -X PUT "https://auto.yr.com.au/api/v1/workflows/[ID]" \
  -H "X-N8N-API-KEY: [key]" -H "Content-Type: application/json" \
  -d @filtered_workflow.json
```

**For database-only fixes:**
```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 \
  "docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod -c \"[SQL HERE];\""
```

---

## PHASE 5: GO LIVE

### Step 14: GO LIVE (Connect Phone Lines)

**Pre-activation checklist:**
- [ ] Agent deployed to RetellAI
- [ ] All webhook changes deployed
- [ ] All database changes applied
- [ ] Backup exists in Testing folder

**Connect phone lines:**
```bash
cd /c/Users/peter/Downloads/CC/Telcos
python telco.py
# Select option to connect agent to phone number
```

**Production phone numbers:**
- `+61288800226` - Main Sydney
- `+61240620999` - Secondary

**Git commit immediately after activation:**
```bash
cd /c/Users/peter/Downloads/CC/retell && git add . && git commit -m "Agent vX.XX - [description]" && git push
```

---

### Step 15: ZERO DEFERRAL CHECK

Verify NOTHING was deferred:

| Check | Status |
|-------|--------|
| All AGENT fixes applied? | [ ] |
| All WEBHOOK fixes deployed? | [ ] |
| All DATABASE fixes executed? | [ ] |
| All COUPLED fixes complete (both parts)? | [ ] |
| Any "TODO" or "LATER" items remaining? | [ ] Must be NO |

**If anything deferred** → Go back and complete it NOW.

---

## PHASE 6: VERIFY

### Step 16: POST-DEPLOYMENT TESTING

**All tests use Peter Ball:**
- Patient ID: `1805465202989210063`
- Phone: `0412111000`

| Test Type | Action | Pass? |
|-----------|--------|-------|
| **Smoke test** | Quick sanity - agent responds | [ ] |
| **Unit test** | Test specific fix in isolation | [ ] |
| **Integration test** | Test with connected webhooks | [ ] |
| **Regression test** | Verify nothing else broke | [ ] |
| **Edge cases** | Empty values, errors, unusual inputs | [ ] |
| **End-to-end test** | Full call flow start to finish | [ ] |
| **Monitoring** | Check n8n execution logs for errors | [ ] |
| **User perspective** | What would a real caller experience? | [ ] |

**If ANY test fails:**
1. Do NOT leave it broken
2. Either fix immediately OR rollback (see Rollback Procedure)

---

### Step 17: FINAL REPORT

Generate summary:

```markdown
# Fix Report - v[version]
Date: [Date]
Agent: [filename]

## Issues Fixed
| ID | Description | Category | Source | Status |
|----|-------------|----------|--------|--------|
| 1 | ... | AGENT | GPT | ✅ Fixed |
| 2 | ... | WEBHOOK | GEM | ✅ Fixed |

## Issues Rejected (False Positives)
| ID | Description | Source | Reason |
|----|-------------|--------|--------|
| 3 | ... | GPT | Verified webhook returns correct field |

## Tests Passed
- [x] Smoke test
- [x] Integration test
- [x] Regression test

## Files Modified
- `retell/Testing/[date]/[agent].json`
- `n8n workflow [ID]`
```

---

## PHASE 7: DOCUMENT

### Step 18: UPDATE DOCUMENTATION

Check and update as needed:

| Document | Update If... |
|----------|--------------|
| `CLAUDE.md` | New rules, gotchas discovered |
| `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` | Webhook params/responses changed |
| `retell/RETELLAI_REFERENCE.md` | New RetellAI patterns learned |
| `retell/RETELLAI_JSON_SCHEMAS.md` | JSON structure insights |
| `retell/AGENT_DEVELOPMENT_GUIDE.md` | New development rules |
| `retell/guides/BOOKING_FLOW_TROUBLESHOOTING.md` | Booking-related fixes |

**If n8n workflows changed, regenerate docs:**
```bash
cd /c/Users/peter/Downloads/CC/n8n/Python
python CC-Made-generate-workflow-docs.py
```

---

### Step 19: CAPTURE LEARNINGS

Create `LEARNINGS_v[version].md` in Testing folder:

```markdown
# Learnings from v[version] - [Date]

## What I Learned
1. [Insight 1]
2. [Insight 2]

## What Tripped Me Up
1. [Gotcha 1]
2. [Gotcha 2]

## Future Prevention
1. [How to avoid this next time]

## Patterns to Remember
1. [Reusable pattern discovered]
```

---

### Step 20: FALSE POSITIVE REPORTS BY SOURCE

**For EACH source that had false positives, generate a report:**

Only create reports for sources with false positives (skip if none).

**Template: `FALSE_POSITIVES_[SOURCE]_v[version].md`**

```markdown
# False Positives from [GPT/Gemini/Claude] Audit - v[version]
Date: [Date]
Audit File: [Original audit file path]

## Summary
- Total issues from [source]: [N]
- Valid issues: [N]
- False positives: [N]
- False positive rate: [X%]

## False Positive Details

### FP-[SRC]-1: [Issue Title]
- **Claimed:** [What audit said was wrong]
- **Verification:** [How we verified - curl, code inspection]
- **Actual Finding:** [What we actually found]
- **Why Wrong:** [Analysis - outdated info, hallucination, misread]
- **Evidence:** [Curl output, code snippet]

## Patterns in [Source] Errors
1. [Common mistake pattern]

## Recommendations for Future [Source] Audits
1. [What to always verify]
```

---

## ROLLBACK PROCEDURE

**If deployment breaks production:**

### Immediate Rollback (< 5 min)

1. **Disconnect phone lines:**
```bash
cd /c/Users/peter/Downloads/CC/Telcos
python telco.py
# Disconnect agent from phone numbers
```

2. **Redeploy backup agent:**
```bash
cd /c/Users/peter/Downloads/CC/retell/scripts
python deploy_agent.py "../Testing/[date]/[agent]_BACKUP.json"
```

3. **Reconnect phone lines to backup**

4. **Revert webhook changes** (if applicable):
- Re-upload previous workflow version from `n8n/JSON/archive/`

### Post-Rollback

- [ ] Document what went wrong
- [ ] Identify root cause
- [ ] Plan corrected fix
- [ ] Re-run process from Step 2

---

## CRITICAL RULES CHECKLIST

Before saying "DONE", verify:

- [ ] **110% CERTAINTY** - Passed certainty gate for ALL fixes
- [ ] **WEBHOOK VERIFICATION** - Called live endpoints for any response field claims
- [ ] **BEFORE/AFTER DOCUMENTED** - Every fix shows what changed
- [ ] **SOURCE ATTRIBUTION** - Every issue tagged with origin
- [ ] **ZERO DEFERRAL** - No "later" items remaining
- [ ] **SCHEMA VERIFIED** - Read existing JSON before writing new
- [ ] **COUPLED COMPLETE** - Both agent AND webhook done for coupled fixes
- [ ] **TESTS PASSED** - All test types executed
- [ ] **GIT COMMITTED** - Changes pushed to repo
- [ ] **DOCS UPDATED** - Relevant documentation refreshed

---

## FILES CREATED

| File | Step | Location |
|------|------|----------|
| COMBINED_ISSUES_v[ver].md | 1 | Testing/[date]/ |
| VALIDATED_ISSUES_v[ver].md | 4/4.5 | Testing/[date]/ |
| [agent]_BACKUP.json | 7 | Testing/[date]/ |
| preflight.py | 8 | Testing/[date]/ |
| apply_fixes.py | 8 | Testing/[date]/ |
| verify_fixes.py | 8 | Testing/[date]/ |
| agent_fixed.json | 9 | Testing/[date]/ |
| fix_checklist.md | 5 | Testing/[date]/ |
| FIX_REPORT_v[ver].md | 17 | Testing/[date]/ |
| LEARNINGS_v[ver].md | 19 | Testing/[date]/ |
| FALSE_POSITIVES_[SRC]_v[ver].md | 20 | Testing/[date]/ |

---

## VALIDATED_ISSUES FORMAT

For each issue, document:

```markdown
### Issue [ID]: [Title]
- **Source:** GPT/GEM/CLAUDE/MANUAL
- **Category:** AGENT/WEBHOOK/DATABASE/COUPLED
- **Audit Claim:** [What the audit said]
- **Verification:** [How verified - curl, code read, test]
- **Actual Finding:** [What we found]
- **Verdict:** VALID / INVALID - FALSE POSITIVE
- **Action:** [Fix description] / Do not fix
- **False Positive Report:** [If invalid, which report]
```

---

## FINAL OUTPUT FORMAT

End every session with:

```
110% COMPLETE

Changes Made:
- [Fix 1]: [BEFORE → AFTER summary]
- [Fix 2]: [BEFORE → AFTER summary]

Tests Passed:
- [x] Smoke, Unit, Integration, Regression, E2E

Docs Updated:
- [List updated documents]

False Positive Reports:
- FALSE_POSITIVES_GPT_v[ver].md: [N] issues
- FALSE_POSITIVES_GEM_v[ver].md: [N] issues

DONE DONE DONE

Files created/modified:
• `C:\Users\peter\Downloads\CC\retell\Testing\[date]\[file1]`
• `C:\Users\peter\Downloads\CC\retell\Testing\[date]\[file2]`
```

---

**Now: Please provide the bug document path(s) with their sources.**
