---
description: Increment a RetellAI agent version and sync all fields
---

Take the RetellAI agent JSON file at the path I provide (or the most recent one in /retell/Testing/ if I don't specify) and:

1. **Read the current version** from the `version` field
2. **Increment by 0.01** (e.g., v5.102 → v5.103, or v5.199 → v5.200)
3. **Update the `version` field** with the new version
4. **Update the `agent_name` field** to match format: `Reignite_AI_Mega_Receptionist_{new_version}_CC`
5. **Save to a new file** with filename: `Reignite_AI_Mega_Receptionist_{new_version}_CC.json`
6. **Save location:** Always save to `C:\Users\peter\Downloads\CC\retell\Testing\`

Before saving:
- Validate that agent_name matches the new filename
- Confirm version field is updated
- Ensure _CC suffix is present
- Verify JSON is still valid

Show me:
- Old version → New version
- Old filename → New filename
- Full path where the new file was saved
- Confirmation that all fields are synchronized

Ask me if I want to keep the old version file or move it to `retell/Testing/Old Agents/`
