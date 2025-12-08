# Custom Slash Commands for RetellAI & n8n Development

Quick reference for all custom slash commands.

## Available Commands

### RetellAI Agent - Validation & Checking

| Command | Purpose |
|---------|---------|
| `/retell-validate-agent` | Comprehensive validation of agent JSON |
| `/retell-check-webhooks` | Verify tool_ids exist in n8n |
| `/retell-quick-test` | Fast validation suite with summary |

### RetellAI Agent - Management

| Command | Purpose |
|---------|---------|
| `/retell-increment-version` | Auto-increment version and sync fields |
| `/retell-new-agent` | Create new agent from latest template |
| `/retell-fix-agent` | Auto-fix common agent issues |
| `/retell-deploy-stable` | Copy tested agent to production folder |
| `/retell-agent-status` | Overview of all agents in Testing |
| `/retell-compare-agents` | Show differences between versions |

### RetellAI Agent - Debugging

| Command | Purpose |
|---------|---------|
| `/retell-debug-sim-calls` | Run simulation calls and analyze results |
| `/retell-debug-package` | Create external audit package |
| `/retell-debug-geminis-input` | Evaluate Gemini suggestions against plan |

### RetellAI Agent - Deployment

| Command | Purpose |
|---------|---------|
| `/retell-deploy-live-with-webhooks-test` | Full deployment: agent + n8n + phone lines + testing |
| `/retell-verify-n8n-database` | Verify webhooks and database after deployment |

### n8n Workflows

| Command | Purpose |
|---------|---------|
| `/n8n-deploy-workflow-fix` | **NEW** Deploy fixed workflow, test, verify SQL, update docs |
| `/n8n-doc-check` | Check which docs need updating after workflow changes |

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

Updated: 2025-12-09
Total commands: 17+
