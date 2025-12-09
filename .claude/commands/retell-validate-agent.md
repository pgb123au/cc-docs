---
description: Validate a RetellAI agent JSON file for common errors
---

Validate the RetellAI agent JSON file at the path I provide (or the most recent one in /retell/Testing/ if I don't specify).

Check for these critical issues:

1. **agent_name matches filename** - The `agent_name` field must exactly match the base filename (without .json)
2. **_CC suffix present** - Filename and agent_name must end with `_CC` (before .json)
3. **Version format valid** - Must be `vX.XXX` format (e.g., v5.102)
4. **Version sync** - The `version` field and version in `agent_name` must match
5. **No duplicate node IDs** - All node `id` fields must be unique (NOTE: Multiple nodes sharing the same `tool_id` is VALID and expected - this is how you reuse webhooks across different conversation contexts)
6. **Valid tool_ids** - All `tool_id` references must exist in the n8n webhook system (check against n8n/Webhooks Docs/RETELLAI_WEBHOOKS_SHORT_REFERENCE_2025_11_22.md)
7. **No orphaned edges** - All `destination_node_id` values in edges must point to existing node `id` values (not `tool_id` values)
8. **Valid JSON** - File must parse correctly

For each issue found:
- Show the exact location (line number if possible)
- Explain the problem
- Suggest the fix

If all checks pass, confirm: "✅ Agent validation passed - ready for import to RetellAI"

Provide a summary at the end with:
- Total issues found
- Critical vs. warning issues
- Whether it's safe to import
