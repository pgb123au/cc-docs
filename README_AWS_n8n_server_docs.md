# AWS / Docker / n8n Server — Documentation Index

This folder contains all of the markdown docs related to your **AWS EC2 + Docker + n8n + PostgreSQL + Metabase** stack.

Use this file as the entry point when you come back to this project in the future.

---

## Core Docs

### 1. Master Operations & Backup Runbook

**File:** `runbook_master.md`

Canonical, end-to-end runbook for the server, including:

- EC2 prerequisites and base OS packages
- Docker stack (n8n, Postgres, Metabase, Caddy, optional pgAdmin)
- Postgres administration
- Metabase connection and usage
- RetellAI data separation (`retellai_prod` DB)
- Automated backups to S3 + tiering (hourly/daily/weekly)
- Disk cleanup and maintenance
- CloudWatch agent + alarms
- Disaster recovery (restore from S3 onto a fresh EC2)

> When in doubt, start with this file.

---

### 2. Backup Optimisation & Debugging

**File:** `backup_optimization_notes.md`

Detailed case study of the hourly backup performance issue, covering:

- How you used a “flight recorder” script to diagnose the issue
- Why `tar + gzip` (default level 6) was saturating a CPU core
- The optimisations you applied:
  - `GZIP=-1` (fast gzip)
  - `nice -n 19`
  - `ionice -c3`
- Updated versions of the heavy `tar` commands
- How to verify on a new server and future improvement ideas

This is your reference for **“why did we choose these backup settings?”**.

---

### 3. Flight Recorder Monitoring Script

**File:** `flight_recorder_monitor.md`

Explains the **`monitor-1pm.sh`** script you used as a “flight recorder” when debugging:

- What metrics it collects (CPU, memory, load, top processes, docker stats, disk usage)
- How often it samples and where it logs
- How to run it again if you suspect resource contention

Use this when you want **deep, time-series insight** into what the server is doing around a specific event (e.g. during heavy backups or spikes).

---

## Additional Themed Docs (Created from Project Conversations)

The following markdown files summarise other useful knowledge and patterns that came up while working on this server.

### 4. EC2 Instance & IAM Notes

**File:** `aws_n8n_ec2_and_iam_notes.md`

Covers:

- Key identifiers (region, instance ID, IAM role, key pair, backup bucket)
- What the `n8n-ec2-s3-backup` role is for
- Why `aws ec2 monitor-instances` failed with `UnauthorizedOperation`
- How to think about IAM permissions for:
  - S3 backups
  - CloudWatch agent
  - CloudWatch alarms

Read this if you ever need to **change the instance role, move to a new instance, or debug AWS permissions**.

---

### 5. CloudWatch Monitoring & Alarms

**File:** `aws_n8n_cloudwatch_monitoring_and_alarms.md`

Summarises all CloudWatch-related pieces:

- Installing and configuring the CloudWatch agent on EC2
- What metrics you are collecting (CPU, memory, disk used%)
- CloudWatch alarms for:
  - High CPU
  - High memory
  - High disk usage
  - EC2 status check failures
- SNS + Gmail filters for alarms

Use this to **recreate or adjust your monitoring** on a new instance.

---

### 6. Postgres, Metabase & Data Layout

**File:** `aws_n8n_postgres_metabase_and_data_layout.md`

Gives you a mental “map” of the data layer:

- Postgres container and DBs: `n8n` and `retellai_prod`
- How to get/change Postgres credentials safely
- RetellAI data separation steps (migration, verification, optional cleanup)
- Key n8n tables (`workflow_entity`, `execution_entity`, `webhook_entity`, etc.)
- How Metabase connects to Postgres and common connectivity fixes

Use this whenever you need to **query data, debug Metabase, or move client data**.

---

### 7. Webhook Inventory & Python Export

**File:** `n8n_webhook_inventory_and_python_export.md`

Practical notes and example Python for:

- Listing all active n8n webhooks directly from Postgres
- Joining webhook info with workflow names and active flags
- Exporting to CSV for documentation or migration

Use this when you want a **single list of all webhooks** (for audits, migrations, or DNS/proxy changes).

---

### 8. Archived Workflows & Restore

**File:** `n8n_archived_workflows_and_restore.md`

Notes from when we looked at how n8n stores archived workflows:

- `workflow_entity` table and the `isArchived` flag
- SQL to list archived workflows
- SQL to unarchive a workflow safely
- Operational cautions (backups, UI refresh)

Use this when you need to **rescue or bulk-unarchive workflows** outside the n8n UI.

---

## How to Use This Folder

1. **Start with `runbook_master.md`** when you’re doing anything big:
   - New instance
   - Disaster recovery
   - Major upgrade

2. **Dip into the specific themed docs** when you’re working on a single topic:
   - Backups → `backup_optimization_notes.md`
   - Monitoring → `aws_n8n_cloudwatch_monitoring_and_alarms.md`
   - Data / Metabase → `aws_n8n_postgres_metabase_and_data_layout.md`
   - Webhooks → `n8n_webhook_inventory_and_python_export.md`
   - Archived workflows → `n8n_archived_workflows_and_restore.md`

3. Keep these files **in sync** with reality when you make major changes (new regions, new bucket, new IAM role, etc.).
