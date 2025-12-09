---
description: Create external audit/debug package with cutting edge agent + reference docs
---

# Create Debug Package for External Audit

Gather the cutting edge (latest deployed) RetellAI agent plus all reference documentation into a dated folder for external review or debugging.

## What Gets Packaged

1. **Cutting Edge Agent** - Latest version from `retell/Testing/` or `retell/agents/`
2. **Whitelist Patterns** - `retell/WHITELISTED_PATTERNS.md`
3. **RetellAI Reference Docs:**
   - `retell/RETELLAI_REFERENCE.md`
   - `retell/RETELLAI_JSON_SCHEMAS.md`
   - `retell/AGENT_DEVELOPMENT_GUIDE.md`
4. **Webhook Documentation:**
   - `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md`
5. **Test Cases** - Latest from `retell/Testing/*/TEST_RESULTS/test-cases*.json` (if exists)

## Steps

### Step 1: Create Dated Folder
```bash
# Create folder with today's date
mkdir -p "C:/Users/peter/Downloads/CC/retell/Testing/$(date +%Y-%m-%d)-debug-package"
```

### Step 2: Find Cutting Edge Agent
- Search `retell/Testing/` subfolders for the newest `Reignite_AI_Mega_Receptionist_v*.json`
- If none found, use latest from `retell/agents/`
- Copy to the new folder

### Step 3: Copy Reference Documentation
```bash
DEST="C:/Users/peter/Downloads/CC/retell/Testing/YYYY-MM-DD-debug-package"

# Core agent docs
cp "C:/Users/peter/Downloads/CC/retell/WHITELISTED_PATTERNS.md" "$DEST/"
cp "C:/Users/peter/Downloads/CC/retell/RETELLAI_REFERENCE.md" "$DEST/"
cp "C:/Users/peter/Downloads/CC/retell/RETELLAI_JSON_SCHEMAS.md" "$DEST/"
cp "C:/Users/peter/Downloads/CC/retell/AGENT_DEVELOPMENT_GUIDE.md" "$DEST/"

# Webhook docs
cp "C:/Users/peter/Downloads/CC/n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md" "$DEST/"
```

### Step 4: Copy Latest Test Cases (if available)
- Find the most recent `test-cases*.json` file in Testing subfolders
- Copy to the debug package folder

### Step 5: Create README
Generate a README.md in the folder with:
- Date created
- Agent version included
- List of all files with descriptions
- Purpose: External audit/debug package

## Output Format

```
=== DEBUG PACKAGE CREATED ===

Folder: C:\Users\peter\Downloads\CC\retell\Testing\YYYY-MM-DD-debug-package

Contents:
  - Reignite_AI_Mega_Receptionist_vX.XXX_CC.json (Agent)
  - WHITELISTED_PATTERNS.md
  - RETELLAI_REFERENCE.md
  - RETELLAI_JSON_SCHEMAS.md
  - AGENT_DEVELOPMENT_GUIDE.md
  - RETELLAI_WEBHOOKS_CURRENT.md
  - test-cases-vX.XXX.json (if found)
  - README.md

Agent Version: vX.XXX
Total Files: N

Ready for external review.

DONE DONE DONE
```

## Notes

- This package is READ-ONLY reference material
- Safe to share externally for code review/audit
- Contains NO credentials or API keys
- Update package by re-running this command (creates new dated folder)
