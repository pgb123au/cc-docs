---
description: Verify all tool_ids in an agent exist in n8n webhooks
---

Check the RetellAI agent JSON file at the path I provide (or the most recent one in /retell/Testing/ if I don't specify).

Extract all `tool_id` values from the agent configuration and verify each one exists in the n8n webhook system.

Check against these sources:
1. `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_SHORT_REFERENCE_2025_11_22.md`
2. `n8n/JSON/EXPORT_MANIFEST.json`
3. `n8n/JSON/active_webhooks_list.csv`

For each tool_id found in the agent:
- ✅ Show valid tools (exist in webhook system)
- ❌ Show invalid tools (don't exist)
- ⚠️ Warn about deprecated tools (if mentioned in docs)

For invalid tool_ids, suggest:
- The correct tool_id if it's a common typo
- Alternative tools that might serve the same purpose
- Whether the node should be removed entirely

Summary output:
```
Tool ID Analysis for {agent_name}
================================
Total tools referenced: X
Valid tools: X
Invalid tools: X
Deprecated tools: X

✅ Valid Tools:
   - tool-add-to-followup
   - tool-create-appointment
   ...

❌ Invalid Tools:
   - tool-log-error (doesn't exist - use tool-add-to-followup instead)
   ...

Status: [SAFE TO IMPORT | NEEDS FIXES]
```
