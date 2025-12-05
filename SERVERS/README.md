# SERVERS - Cross-Cutting Infrastructure

## What This Folder Is For

General server management that spans multiple systems or doesn't belong to a specific project.

## What Does NOT Go Here

| Don't Put Here | Put It In | Why |
|----------------|-----------|-----|
| n8n configs, workflows, backups | `n8n/` | n8n-specific |
| n8n AWS EC2 docs | `n8n/AWS Docs/` | n8n server docs |
| Telco sync scripts | `Telcos/sync/` | Telco-specific |
| RackNerd telco server setup | `Telcos/` | Telco infrastructure |
| RetellAI anything | `retell/` | RetellAI-specific |

## What DOES Go Here

- Server inventory (below)
- SSH configurations that span multiple servers
- Scripts that operate on multiple servers at once
- General monitoring/alerting configs
- Future servers that aren't n8n or Telco related

---

## Server Inventory

| Name | IP | Purpose | SSH | Detailed Docs |
|------|-----|---------|-----|---------------|
| **AWS EC2** | `52.13.124.171` | n8n, Metabase, PostgreSQL | `ssh -i ~/.ssh/metabase-aws ubuntu@52.13.124.171` | `n8n/AWS Docs/` |
| **RackNerd** | `96.47.238.189` | Telco data sync | `ssh root@96.47.238.189` | `Telcos/SERVER_SYNC_SETUP.md` |

---

## Quick SSH Commands

```bash
# AWS (n8n server)
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171

# RackNerd (telco sync)
ssh root@96.47.238.189
```

---

## Folder Structure

```
SERVERS/
├── README.md          # This file - inventory & guidelines
├── ssh/               # SSH configs (if needed)
└── scripts/           # Cross-server scripts (when needed)
```
