# Custom Slash Commands for RetellAI Agent Development

Quick reference for all custom slash commands.

## Available Commands (10 total)

### Validation & Checking

| Command | Purpose |
|---------|---------|
| `/validate-agent` | Comprehensive validation of agent JSON |
| `/check-webhooks` | Verify tool_ids exist in n8n |
| `/quick-test` | Fast validation suite with summary |

### Agent Management

| Command | Purpose |
|---------|---------|
| `/increment-version` | Auto-increment version and sync fields |
| `/new-agent` | Create new agent from latest template |
| `/fix-agent` | Auto-fix common agent issues |
| `/deploy-stable` | Copy tested agent to production folder |

### Analysis & Session

| Command | Purpose |
|---------|---------|
| `/compare-agents` | Show differences between versions |
| `/agent-status` | Overview of all agents in Testing |
| `/session-start` | Initialize new dev session with context |

---

## Quick Workflows

### Start of Day
```
/session-start           # Get context, check uncommitted changes
```

### Create New Version
```
/agent-status            # See current versions
/increment-version       # Create next version
/validate-agent          # Confirm valid
```

### Pre-Import Checklist
```
/validate-agent          # Check structure
/check-webhooks          # Verify tool_ids
/quick-test              # Final validation
# If all pass: ✅ Ready to import
```

### Deploy to Production
```
/quick-test              # Final validation
/deploy-stable           # Copy to agents/ folder
```

### Fix Import Errors
```
/validate-agent          # Identify issues
/fix-agent               # Auto-fix problems
/validate-agent          # Verify fixes
```

---

## File Locations

| What | Where |
|------|-------|
| Slash commands | `.claude/commands/` |
| Active development | `retell/Testing/[date]/` |
| Production agents | `retell/agents/` |
| Webhook reference | `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` |

---

## Tips

- **Most commands work without arguments** - defaults to latest agent
- **Always validate before import** - catches issues early
- **Backups are automatic** - `/fix-agent` creates backups
- **Use `/session-start`** - establishes context at day start

---

Updated: 2025-11-29
Total commands: 10
