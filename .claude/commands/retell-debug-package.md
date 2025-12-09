---
description: Create external audit/debug package with cutting edge agent + reference docs
---

# Create Debug Package for External Audit

Gather the cutting edge (latest deployed) RetellAI agent plus all reference documentation into a dated folder for external review or debugging.

## What Gets Packaged

1. **Cutting Edge Agent** - Latest version from `retell/Testing/` or `retell/agents/`
2. **Last Call Log** - Most recent `CALL*.json` from `retell/Testing/` subfolders (single file only by default)
3. **Whitelist Patterns** - `retell/WHITELISTED_PATTERNS.md`
4. **RetellAI Reference Docs:**
   - `retell/RETELLAI_REFERENCE.md`
   - `retell/RETELLAI_JSON_SCHEMAS.md`
   - `retell/AGENT_DEVELOPMENT_GUIDE.md`
5. **Webhook Documentation:**
   - `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md`
6. **Test Cases** - Latest from `retell/Testing/*/TEST_RESULTS/test-cases*.json` (if exists)

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

### Step 3: Find Last Call Log
- Search `retell/Testing/` subfolders for `CALL*.json` files
- Sort by modification time and get the MOST RECENT ONE ONLY
- Copy single file to the debug package folder

### Step 4: Copy Reference Documentation
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

### Step 5: Copy Latest Test Cases (if available)
- Find the most recent `test-cases*.json` file in Testing subfolders
- Copy to the debug package folder

### Step 6: Create README
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
  - CALL_DATA.json (Last call log)
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
- **Only the LAST call log is included by default** - request additional calls explicitly if needed
- Update package by re-running this command (creates new dated folder)
