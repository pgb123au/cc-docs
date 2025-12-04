---
description: Evaluate Gemini's suggestions against your plan - adopt or argue with evidence
---

# Debug Gemini's Input

Gemini (or another AI) has provided suggestions. Evaluate them against your current plan.

## Instructions

### Step 1: Understand Gemini's Input
The user will paste or describe what Gemini suggested. Parse and summarize the key points.

### Step 2: Compare Against Your Plan
For each suggestion Gemini made:
- Does it align with your current approach?
- Does it contradict your plan?
- Is it a new idea you hadn't considered?

### Step 3: Evaluate Each Point

For each suggestion, decide:
- **AGREE** - Gemini's point is valid, adopt it
- **PARTIAL** - Some merit, needs modification
- **DISAGREE** - You have strong evidence against it

### Step 4: Handle Disagreements

If you **DISAGREE** with any point, you MUST:

1. **State your case clearly** with solid backing
2. **Cite references** from these authoritative sources:
   - RetellAI official docs: https://docs.retellai.com/
   - RetellAI API reference: https://docs.retellai.com/api-references/
   - n8n docs: https://docs.n8n.io/
   - Agent template file: `retell/agents/` (latest stable)
   - `retell/RETELLAI_REFERENCE.md`
   - `retell/RETELLAI_JSON_SCHEMAS.md`
   - `retell/AGENT_DEVELOPMENT_GUIDE.md`
   - `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md`
   - Credible third-party sources (official docs, RFCs, well-known engineering blogs)

3. **Create an arguments file** in the same working folder:
   - Find the current Testing folder (e.g., `retell/Testing/25-12-04a/`)
   - Create: `GEMINI_DEBATE_[topic]_[timestamp].md`
   - Include:
     ```markdown
     # Disagreement with Gemini: [Topic]

     **Date:** [YYYY-MM-DD HH:MM]
     **Context:** [Brief description of the task]

     ## Gemini's Suggestion
     [Quote what Gemini said]

     ## My Position
     [Your counter-argument]

     ## Evidence

     ### Source 1: [Name]
     - Reference: [URL or file path]
     - Quote: "[Exact quote supporting your position]"
     - Relevance: [Why this supports your argument]

     ### Source 2: [Name]
     ...

     ## Conclusion
     [Summary of why your approach is correct]
     ```

4. **Git commit** the arguments file

### Step 5: Handle Agreements

If you **AGREE** with Gemini's suggestions:
1. **Do NOT create a new file** - no arguments file needed
2. **Amend your plan** to incorporate the suggestions
3. **Present the updated plan on screen** with:
   - What changed from your original plan
   - Which Gemini suggestions were adopted
   - The complete revised plan

### Step 6: Output Format

```
=== GEMINI INPUT EVALUATION ===

Gemini's Key Points:
1. [Point 1]
2. [Point 2]
...

Evaluation:
| # | Gemini's Point | Verdict | Reason |
|---|----------------|---------|--------|
| 1 | [summary] | AGREE/PARTIAL/DISAGREE | [brief reason] |
| 2 | [summary] | AGREE/PARTIAL/DISAGREE | [brief reason] |

[If any DISAGREE:]
Arguments documented in: [full path to .md file]

[If all AGREE or PARTIAL:]
=== REVISED PLAN ===
[Present updated plan here]

DONE DONE DONE
```

## Critical Rules

- Never dismiss Gemini without evidence - if you disagree, PROVE IT
- Use primary sources (official docs) over secondary sources
- Quote exact text from references, don't paraphrase
- Be intellectually honest - if Gemini is right, admit it and adapt
- Arguments file is ONLY created when you disagree, not for agreements
