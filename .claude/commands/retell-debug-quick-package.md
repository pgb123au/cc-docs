---
description: Create a quick debug package with whitelist patterns and latest test cases
---

# Create Quick Debug Package

Package the whitelisted patterns documentation and latest simulation test cases for external review or debugging.

**Usage:** `/retell-debug-quick-package`

## What Gets Packaged

1. **Whitelist Patterns** - `retell/WHITELISTED_PATTERNS.md` (known intentional design choices to ignore)
2. **Latest Test Cases** - Most recent file from `retell/Testing/Simulation-Test-Cases/`

## Steps

### Step 1: Create Dated Folder

```bash
# Create folder with today's date and suffix
FOLDER="C:/Users/peter/Downloads/CC/retell/Testing/$(date +%Y-%m-%d)-quick-debug"
mkdir -p "$FOLDER"
```

### Step 2: Copy Whitelist Patterns

```bash
cp "C:/Users/peter/Downloads/CC/retell/WHITELISTED_PATTERNS.md" "$FOLDER/"
```

### Step 3: Find and Copy Latest Test Cases

Find the most recently modified test case file in `retell/Testing/Simulation-Test-Cases/`:

```bash
# Find latest test-cases file by modification time
LATEST_TEST=$(ls -t "C:/Users/peter/Downloads/CC/retell/Testing/Simulation-Test-Cases/"*.json | head -1)
cp "$LATEST_TEST" "$FOLDER/"
```

### Step 4: Create README

Generate a `README.md` in the folder:

```markdown
# Quick Debug Package

**Created:** YYYY-MM-DD
**Purpose:** External audit reference - whitelisted patterns and test cases

## Contents

| File | Description |
|------|-------------|
| WHITELISTED_PATTERNS.md | Intentional design choices that auditors should ignore |
| test-cases-vX.XXX.json | Simulation test cases for agent validation |

## WHITELISTED_PATTERNS.md

This document lists patterns that are **intentional design choices**, not bugs:
- Silent caller ID lookup at start (1-2s delay for personalization)
- No emergency escalation (we're not an emergency service)
- No SMS confirmation (handled by Cliniko)
- Optimistic SMS sending (no mobile check)
- Single appointments only (no recurring series via agent)
- Custom voice ID (account-specific)

**Audit Rule:** If an issue matches a whitelisted pattern, ignore it.

## Test Cases

The test cases file contains simulation scenarios that exercise:
- Caller identification flows
- Booking journeys (private pay, funded)
- Proxy caller handling
- Reschedule/cancel flows
- Knowledge base queries
- Error recovery paths

Each test case includes:
- `name`: Test scenario name
- `description`: What the test validates
- `dynamic_variables`: Patient data for simulation
- `metrics`: Expected outcomes to verify
- `user_prompt`: Full instructions for the simulated caller
- `tool_mocks`: Empty (uses real webhooks) or mock data

## Usage

1. Review WHITELISTED_PATTERNS.md to understand intentional design choices
2. Use test cases to validate agent behavior
3. Ignore findings that match whitelisted patterns
```

### Step 5: Commit Changes

```bash
cd /c/Users/peter/Downloads/CC
git add .
git commit -m "Debug - Quick package with whitelist and test cases"
git push
```

## Output Format

```
=== QUICK DEBUG PACKAGE CREATED ===

Folder: C:\Users\peter\Downloads\CC\retell\Testing\YYYY-MM-DD-quick-debug

Contents:
  - WHITELISTED_PATTERNS.md (14 whitelisted patterns)
  - test-cases-vX.XXX_comprehensive.json (N test cases)
  - README.md

Test Cases Version: vX.XXX
Whitelisted Patterns: 14 items

Ready for external review.

DONE DONE DONE
```

## Notes

- This is a lightweight package for quick reference
- For full debug package with agent + all docs, use `/retell-debug-package`
- Contains NO credentials or API keys - safe to share externally
- Whitelist patterns prevent false-positive audit findings
