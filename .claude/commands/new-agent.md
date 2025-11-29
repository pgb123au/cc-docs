---
description: Create a new RetellAI agent from the latest template
---

Create a new RetellAI agent JSON file using the most recent version in /retell/Testing/ as a template.

Steps:
1. **Find the latest agent** in `retell/Testing/` (highest version number)
2. **Determine new version** by incrementing the latest by 0.01
3. **Create new agent file** with:
   - New version number
   - Proper _CC suffix
   - Updated agent_name field
   - Updated version field
   - Clean structure (remove any testing artifacts)
4. **Save to:** `C:\Users\peter\Downloads\CC\retell\Testing\Reignite_AI_Mega_Receptionist_v{new_version}_CC.json`

Ask me before creating:
- What changes should I make to the template? (e.g., prompt updates, tool changes)
- Should I use a specific version as the template instead of the latest?
- Any specific configuration to modify?

After creation:
- Validate the new agent using /validate-agent
- Show summary of what was created
- Confirm it's ready for testing/import

Output format:
```
New Agent Created
=================
Template used: v5.102_CC
New version: v5.103_CC
File location: C:\Users\peter\Downloads\CC\retell\Testing\Reignite_AI_Mega_Receptionist_v5.103_CC.json

Changes made:
- [list any modifications]

✅ Validation passed
Ready for: [Testing | Import | Further modifications]
```
