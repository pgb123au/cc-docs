# Deploy Agent to Stable

Copy the current working agent to the `agents/` folder as the new stable production version.

## Instructions

1. First, identify the latest agent in the current Testing folder (e.g., `Testing/25-11-29a/`)
2. Validate it using `/validate-agent`
3. If valid, copy it to `retell/agents/` folder
4. Remove any older versions from `agents/` (keep only the new one)
5. Update the version in agents/README.md if needed
6. Git commit both the Testing folder and agents/ folder changes

## Safety Checks Before Deploy

- Confirm the agent has been tested
- Verify webhook tool_ids match n8n webhooks
- Check that version number is incremented from current stable

## After Deploy

Report:
- Previous stable version
- New stable version
- File copied from → to
- Git commit status
