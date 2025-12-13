---
description: Full autonomous n8n webhook/database fix process - includes agent changes if needed (16 steps)
---

# RetellAI Agent Fix Process - AUTO (v2.0)

Full autonomous process to fix a RetellAI agent based on bug audit documents.
**Now with 110% Certainty Protocol and False Positive Reporting by Source.**

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

Before I begin, please provide the bug/audit document paths. These can be:
- Local file paths (e.g., `C:\Users\peter\Downloads\bugs v11.XXX GPT.md`)
- Multiple documents (GPT audit, Gemini audit, Claude audit, manual notes, etc.)

**Please provide 1 or more bug document paths now.** I'll wait for your input.

Format:
```
Bug docs:
1. [path or paste content] (source: GPT/GEM/CLAUDE/MANUAL)
2. [path or paste content] (source: GPT/GEM/CLAUDE/MANUAL)
...
```

---

## After You Provide Bug Docs

I will execute this enhanced process with 110% certainty gates:

### PART 1: Combine & Approve (Step 1)

**Step 1: COMBINE ALL AUDITS**
- Read all bug documents you provided
- **Tag each issue with its SOURCE** (GPT, GEM, CLAUDE, MANUAL)
- Combine with my own audit findings (if I've already reviewed the agent)
- Deduplicate issues (keep source attribution)
- Categorize each as: AGENT / WEBHOOK / DATABASE / COUPLED
- Output `COMBINED_ISSUES_v[version].md`

**>>> STOP FOR YOUR APPROVAL <<<**
You review the combined list and either approve or request changes.

---

### PART 2: 110% Certainty Gate (Step 2)

Before ANY fix, I must answer YES to ALL of these:

| Question | Required Answer |
|----------|-----------------|
| Do I understand the ROOT CAUSE? | YES |
| Have I VERIFIED my assumptions with live data/code? | YES |
| Do I know EXACTLY what to change? | YES |
| Do I know what SIDE EFFECTS this could have? | YES |
| Have I checked if this affects OTHER components? | YES |
| Can I EXPLAIN the fix to a 5-year-old? | YES |

**If ANY answer is NO** → Go to Investigation Loop (Step 2.5)

---

### Step 2.5: Investigation Loop (if not 110% sure)

Repeat until 110% certain:

1. **Read the actual code/config** - not from memory
2. **Trace the data flow** - inputs → processing → outputs
3. **Check logs/errors** - what ACTUALLY happened vs what I assume
4. **Test current behavior** - verify the problem exists as described
5. **Search for similar patterns** - how was this solved elsewhere?
6. **Verify against live systems** - webhooks, APIs, databases
7. **Document findings** - capture what I learned

**Loop back to 110% Certainty Gate** after each investigation round.

---

### PART 3: Autonomous Execution (Steps 3-19)

After passing the 110% Certainty Gate, I execute ALL remaining steps:

| Step | Description |
|------|-------------|
| 3 | Confirm scope, create todo list |
| 4 | Deep investigation (locate, validate, categorize) |
| **4.5** | **VERIFY webhook claims against LIVE endpoints** |
| 5 | Generate FIND/REPLACE strings (show BEFORE and AFTER) |
| 6 | Conflict & impact analysis (6 checks) |
| 7 | Generate scripts (preflight, apply, verify) |
| 8 | Execute scripts |
| 9 | Agent validation |
| 10 | Complete COUPLED fixes (webhook first, then agent) |
| 11 | Deploy agent (NOT live yet) |
| 12 | Webhook-only & database-only fixes |
| 13 | Go live (connect phone lines, commit) |
| 14 | Zero deferral check |
| 15 | Post-deployment testing |
| 16 | Final report |
| 17 | Update documentation |
| 18 | Capture learnings |
| **19** | **Generate False Positive Reports by Source** |

---

## Step 4.5: VERIFY WEBHOOK CLAIMS (MANDATORY)

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
   - **Record in source-specific false positive list** (GPT/GEM/CLAUDE)
   - Document in VALIDATED_ISSUES as false positive

**NEVER change response_variables based on audit claims without live verification.**

---

## Step 5: BEFORE and AFTER Documentation

For EACH fix, document:

```markdown
### Fix [ID]: [Description]

**Root Cause:** [Why this bug exists]

**BEFORE:**
```json
[exact current code/config]
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

---

## Step 15: Post-Deployment Testing

After live deployment, perform ALL of these:

| Test Type | Action | Pass? |
|-----------|--------|-------|
| **Smoke test** | Quick sanity check that basics work | |
| **Unit test** | Test the specific fix in isolation | |
| **Integration test** | Test with connected systems | |
| **Regression test** | Verify nothing else broke | |
| **Edge cases** | Test unusual inputs, empty values, errors | |
| **End-to-end test** | Full flow from start to finish | |
| **Monitoring** | Check for errors in logs | |
| **User perspective** | What would a real caller experience? | |

**All tests must use Peter Ball test data:**
- Patient ID: `1805465202989210063`
- Phone: `0412111000`

---

## Step 17: Update Documentation

Check and update as needed:

| Document | Update If... |
|----------|--------------|
| `CLAUDE.md` | New rules, gotchas, or patterns discovered |
| `RETELLAI_WEBHOOKS_CURRENT.md` | Webhook params/responses changed |
| `RETELLAI_REFERENCE.md` | New RetellAI patterns learned |
| `RETELLAI_JSON_SCHEMAS.md` | JSON structure insights |
| `AGENT_DEVELOPMENT_GUIDE.md` | New agent development rules |
| `BOOKING_FLOW_TROUBLESHOOTING.md` | Booking-related fixes |
| Agent README/changelog | Version changes |

Run doc generator if n8n changed:
```bash
cd /c/Users/peter/Downloads/CC/n8n/Python
python CC-Made-generate-workflow-docs.py
```

---

## Step 18: Capture Learnings

Create `LEARNINGS_v[version].md`:

```markdown
## New Learnings from [Date] - v[version]

### What I Learned
1. [Insight 1]
2. [Insight 2]
...

### What Tripped Me Up
1. [Gotcha 1]
2. [Gotcha 2]
...

### Future Prevention
1. [How to avoid this issue next time]
...

### Patterns to Remember
1. [Reusable pattern discovered]
...
```

---

## Step 19: False Positive Reports by Source (NEW)

**For EACH source that had false positives, generate a separate report:**

### FALSE_POSITIVES_GPT_v[version].md
```markdown
# False Positives from GPT Audit - v[version]
Date: [Date]
Audit File: [Original GPT audit file path]

## Summary
- Total issues from GPT: [N]
- Valid issues: [N]
- False positives: [N]
- False positive rate: [X%]

## False Positive Details

### FP-GPT-1: [Issue Title]
- **GPT Claimed:** [What GPT said was wrong]
- **Verification Method:** [How we verified - curl, code inspection, etc.]
- **Actual Finding:** [What we actually found]
- **Why GPT Was Wrong:** [Analysis of the error - outdated info, hallucination, misread, etc.]
- **Evidence:** [Curl output, code snippet, etc.]

### FP-GPT-2: [Issue Title]
...

## Patterns in GPT Errors
1. [Common mistake pattern 1]
2. [Common mistake pattern 2]
...

## Recommendations for Future GPT Audits
1. [What to watch for]
2. [What to always verify]
...
```

### FALSE_POSITIVES_GEM_v[version].md
```markdown
# False Positives from Gemini Audit - v[version]
Date: [Date]
Audit File: [Original Gemini audit file path]

## Summary
- Total issues from Gemini: [N]
- Valid issues: [N]
- False positives: [N]
- False positive rate: [X%]

## False Positive Details

### FP-GEM-1: [Issue Title]
- **Gemini Claimed:** [What Gemini said was wrong]
- **Verification Method:** [How we verified]
- **Actual Finding:** [What we actually found]
- **Why Gemini Was Wrong:** [Analysis]
- **Evidence:** [Proof]

...

## Patterns in Gemini Errors
...

## Recommendations for Future Gemini Audits
...
```

### FALSE_POSITIVES_CLAUDE_v[version].md
```markdown
# False Positives from Claude Audit - v[version]
Date: [Date]
Audit File: [Original Claude audit file path]

## Summary
- Total issues from Claude: [N]
- Valid issues: [N]
- False positives: [N]
- False positive rate: [X%]

## False Positive Details

### FP-CLAUDE-1: [Issue Title]
- **Claude Claimed:** [What Claude said was wrong]
- **Verification Method:** [How we verified]
- **Actual Finding:** [What we actually found]
- **Why Claude Was Wrong:** [Analysis]
- **Evidence:** [Proof]

...

## Patterns in Claude Errors
...

## Recommendations for Future Claude Audits
...
```

**Only generate reports for sources that had false positives.**

---

## False Positive Detection

Audits (GPT, Gemini, Claude, manual) can make incorrect claims. Watch for:

| Red Flag | Action |
|----------|--------|
| "Webhook returns X not Y" | CALL the webhook, verify actual fields |
| "Field mapping is wrong" | Compare current mapping to live response |
| "response_variables outdated" | Test if current agent works before "fixing" |
| "Tool schema doesn't match webhook" | Verify against live endpoint |
| "This edge condition isn't handled" | Test the actual flow first |
| "Variable is never set" | Trace the actual data flow |

**If the current agent WORKS for that flow, investigate thoroughly before changing.**

### Real Example: v11.200 C4/C5 Disaster

GPT audit claimed `get-class-schedule` webhook returns `slots` instead of `upcoming_sessions`. This was FALSE. The "fix" broke all class booking. Always verify.

---

## Critical Rules

1. **110% CERTAINTY** - Pass the certainty gate before ANY fix
2. **DO NOT RUSH** - Complete each step thoroughly
3. **DO NOT SKIP VALIDATION** - Loop until each gate passes
4. **ZERO DEFERRAL** - Complete ALL fixes, no "later" allowed
5. **SCHEMA VERIFICATION** - Before writing JSON, read existing elements first
6. **OUTPUT FULL PATHS** - Show Windows paths for all created files
7. **WEBHOOK VERIFICATION** - Any audit claim about webhook response fields MUST be verified by calling the live endpoint
8. **DOCUMENT BEFORE/AFTER** - Every fix must show what's changing
9. **SOURCE ATTRIBUTION** - Track which audit each issue came from
10. **FALSE POSITIVE REPORTING** - Generate per-source reports at end

---

## JSON Schema Rules

Before writing ANY new node/edge JSON:
| Wrong | Correct |
|-------|---------|
| `target` | `destination_node_id` |
| `condition` | `transition_condition` |
| `id` (nodes) | `node_id` |
| `id` (tools) | `tool_id` |

**NEVER write JSON from memory - always verify against actual agent file first.**

---

## Test Data

All tests use Peter Ball:
- Patient ID: `1805465202989210063`
- Phone: `0412111000`

---

## Files Created

| File | Step |
|------|------|
| COMBINED_ISSUES_v[ver].md | 1 |
| VALIDATED_ISSUES_v[ver].md | 4/4.5 |
| fix_checklist.md | 5/6 |
| preflight.py, apply_fixes.py, verify_fixes.py | 7 |
| agent_fixed.json | 8 |
| LEARNINGS_v[ver].md | 18 |
| FALSE_POSITIVES_GPT_v[ver].md | 19 (if applicable) |
| FALSE_POSITIVES_GEM_v[ver].md | 19 (if applicable) |
| FALSE_POSITIVES_CLAUDE_v[ver].md | 19 (if applicable) |

---

## VALIDATED_ISSUES Format

For each issue, document verification status:

```markdown
### Issue C4: get-class-schedule Response Mapping
- **Source:** GPT
- **Audit Claim:** Webhook returns `slots` not `upcoming_sessions`
- **Verification:** Called live endpoint with test data
- **Actual Response:** `{"success":true,"upcoming_sessions":[...],...}`
- **Verdict:** INVALID - FALSE POSITIVE
- **Action:** Do not fix - current agent is correct
- **Added to:** FALSE_POSITIVES_GPT_v[ver].md
```

---

## Final Output

End with:

```
110% COMPLETE

Changes Made:
- [List each change with BEFORE/AFTER summary]

Tests Passed:
- [List each test type and result]

Live URLs:
- [If applicable]

New Learnings:
- [Key insights]

Docs Updated:
- [List updated docs]

False Positive Reports Generated:
- FALSE_POSITIVES_GPT_v[ver].md: [N] false positives
- FALSE_POSITIVES_GEM_v[ver].md: [N] false positives
- FALSE_POSITIVES_CLAUDE_v[ver].md: [N] false positives

DONE DONE DONE

Files created/modified:
• [Full absolute paths]
```

---

**Now: Please provide the bug document path(s) with their sources.**
