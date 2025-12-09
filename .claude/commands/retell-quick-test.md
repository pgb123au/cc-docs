# Quick Test Agent

Run a quick validation suite on the specified agent.

## Usage
/quick-test [path-to-agent.json]

If no path provided, use the latest agent in the current Testing folder.

## Tests to Run

1. **JSON Validity** - Parse without errors
2. **Required Fields** - agent_name, nodes, edges, tools exist
3. **Version Format** - Matches vX.XX pattern
4. **Entry Node** - First node is type "conversation"
5. **Tool IDs** - All tool_ids match known n8n webhooks
6. **No Orphan Nodes** - All nodes reachable from entry
7. **End Nodes Exist** - At least one type:"end" node
8. **No Self-Loops** - No edges where source = destination

## Output Format

```
QUICK TEST: [filename]
═══════════════════════════════════════════
✅ JSON Valid
✅ Required fields present
✅ Version: v10.96
✅ Entry node is conversation type
⚠️  2 tool_ids not in webhook reference
✅ No orphan nodes
✅ 3 end nodes found
✅ No self-loops
═══════════════════════════════════════════
Result: PASS (1 warning)
```

Report any failures with specific details.
