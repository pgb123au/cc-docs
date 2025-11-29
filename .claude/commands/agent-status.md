---
description: Show quick overview of all agents in Testing folder
---

Scan `/retell/Testing/` directory and provide a status overview of all RetellAI agent JSON files.

For each agent file, show:
- ✅ or ❌ indicating validation status
- Version number
- File size
- Last modified date
- Quick issue count (if any)

Sort by version number (newest first).

Highlight:
- 🟢 Latest version (highest number)
- 🔴 Files with validation errors
- ⚠️ Files without _CC suffix

Output format:
```
Agent Status Overview
=====================
Location: C:\Users\peter\Downloads\CC\retell\Testing\

🟢 v5.103_CC  ✅  (245 KB)  Modified: 2025-11-23 14:30
   Latest version - Ready for import

   v5.102_CC  ✅  (243 KB)  Modified: 2025-11-22 10:15
   No issues found

   v5.101_CC  ❌  (241 KB)  Modified: 2025-11-21 16:45
   Issues: agent_name mismatch, 2 invalid tool_ids

🔴 v5.100     ⚠️  (240 KB)  Modified: 2025-11-20 09:20
   Missing _CC suffix

Total agents: 4
Ready for import: 2
Need fixes: 2

Recommendation: Use v5.103_CC for production
```

Optionally, ask me if I want to:
- Validate all agents
- Fix all agents with issues
- Move old versions to Old Agents folder
