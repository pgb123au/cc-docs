---
description: Automatically fix common RetellAI agent issues
---

Take the RetellAI agent JSON file at the path I provide (or the most recent one in /retell/Testing/ if I don't specify) and automatically fix these common issues:

**Auto-fixes:**
1. **Sync agent_name with filename** - Update agent_name to match the base filename
2. **Add _CC suffix** - If missing, add to both filename and agent_name
3. **Sync version fields** - Ensure version field matches version in agent_name
4. **Remove duplicate node IDs** - Rename duplicate `id` field values with unique suffixes (NOTE: Multiple nodes sharing the same `tool_id` is VALID and expected - do NOT flag this as an issue)
5. **Remove orphaned edges** - Delete edges pointing to non-existent node `id` values
6. **Fix invalid tool_ids** - Replace with valid alternatives where possible (check against n8n webhook reference)

**Before making changes:**
- Create a backup of the original file in `/retell/Testing/Old Agents/`
- Show me all issues found
- Show me what fixes will be applied
- Ask for confirmation before proceeding

**After fixes:**
- Save the corrected file
- Run /validate-agent to confirm all issues are resolved
- Show summary of changes made

Output format:
```
Agent Auto-Fix Report
=====================
File: Reignite_AI_Mega_Receptionist_v5.102_CC.json

Issues Found:
  ❌ agent_name doesn't match filename
  ❌ 2 duplicate node IDs
  ❌ 1 orphaned edge

Fixes Applied:
  ✅ Updated agent_name: "...v5_87..." → "...v5.102_CC"
  ✅ Renamed duplicate nodes: node-123 → node-123-1
  ✅ Removed edge pointing to deleted node-xyz

Backup saved to: /retell/Testing/Old Agents/...

✅ Validation passed - agent is now ready for import
```
