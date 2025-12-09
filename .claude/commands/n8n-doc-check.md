---
description: Check if n8n documentation needs updating after workflow changes
---

After making changes to n8n workflows, check if documentation needs updating.

Ask the user which of these apply to their recent changes:

**1. Did you change webhook parameters, responses, or endpoints?**
   - If yes: Update `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md`

**2. Did you add, remove, or significantly modify workflows?**
   - If yes: Run the auto-generation script:
   ```bash
   cd C:\Users\peter\Downloads\CC\n8n\Python
   python CC-Made-generate-workflow-docs.py
   ```
   This will regenerate `n8n/Webhooks Docs/N8N_WORKFLOWS_AUTO_GENERATED.md`

**3. Did you discover new debugging patterns or fixes?**
   - If yes: Update `n8n/Webhooks Docs/N8N_WEBHOOK_TROUBLESHOOTING.md`

**4. Did you change email templates or email workflows?**
   - If yes: Update `n8n/Webhooks Docs/SYSTEM_EMAILS_REFERENCE.md`

**Quick Reference - The 5 MAINTAINED docs:**
| Document | Update when... |
|----------|----------------|
| `RETELLAI_WEBHOOKS_CURRENT.md` | Webhook params/responses change |
| `N8N_WORKFLOWS_MASTER_REFERENCE.md` | Workflows added/removed/changed |
| `N8N_WEBHOOK_TROUBLESHOOTING.md` | New debugging patterns found |
| `SYSTEM_EMAILS_REFERENCE.md` | Email templates change |
| `N8N_WORKFLOWS_AUTO_GENERATED.md` | Run script to regenerate |

Offer to help the user update the relevant documentation if they need it.
