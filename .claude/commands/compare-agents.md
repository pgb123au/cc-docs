---
description: Compare two RetellAI agent versions and show differences
---

Compare two RetellAI agent JSON files. I'll provide two file paths, or you can compare the two most recent versions in /retell/Testing/.

Show differences in these key areas:

**1. Metadata Changes:**
- agent_name
- version
- llm_websocket_url
- voice_id
- response_temperature
- ambient_sound

**2. General Prompt Changes:**
- Show diff of begin_message
- Show diff of general_prompt
- Highlight any significant instruction changes

**3. Node Changes:**
- Added nodes (show node id, type, and description)
- Removed nodes (show node id, type, and description)
- Modified nodes (show what changed)

**4. Tool/Webhook Changes:**
- Added tool_ids
- Removed tool_ids
- Changed tool configurations

**5. Edge/Flow Changes:**
- New conversation paths added
- Removed conversation paths
- Modified transitions

**6. States/Variables:**
- New states added
- Removed states
- Changed state configurations

**Format output like:**
```
Comparing Agent Versions
========================
Old: Reignite_AI_Mega_Receptionist_v5.102_CC
New: Reignite_AI_Mega_Receptionist_v5.103_CC

METADATA CHANGES:
  version: v5.102 → v5.103

PROMPT CHANGES:
  + Added: "When checking appointments..."
  - Removed: "Old instruction about..."

NODE CHANGES:
  + Added node-xyz: "Check patient eligibility"
  - Removed node-abc: "Old validation step"

TOOL CHANGES:
  + Added: tool-check-funding

EDGE CHANGES:
  Modified flow from booking to confirmation

Summary: X changes across Y categories
```
