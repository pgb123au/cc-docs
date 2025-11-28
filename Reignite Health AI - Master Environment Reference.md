# **Reignite Health AI \- Master Environment Reference**

**Comprehensive configuration, tools, and workflows for Peter.** *Combines system setup, database patterns, and error analysis tools.*

**Last Updated:** November 27, 2025

**Project:** Reignite Health AI Integration

**Status:** Production Environment

**Server:** AWS EC2 (54.149.95.69)

**n8n Version:** 1.116.2 (updated 2025-11-27)

## **📋 Quick Command Cheat Sheet**

### **🚀 Top 3 Most Used Commands**

\# 1\. Run Error Analyzer (Windows PowerShell)  
cd C:\\Users\\peter\\Downloads; python n8n\_error\_analyzer.py

\# 2\. Connect to Server (Windows PowerShell)  
ssh \-i "C:\\Users\\peter\\.ssh\\metabase-aws" ubuntu@54.149.95.69

\# 3\. Check App Database (EC2)  
docker exec \-it n8n-postgres-1 psql \-U n8n \-d retellai\_prod

## **📁 Table of Contents**

1. [Environment Overview](https://www.google.com/search?q=%231-environment-overview)  
2. [Connectivity (SSH & SCP)](https://www.google.com/search?q=%232-connectivity-ssh--scp)  
3. [Tools: n8n Error Analyzer](https://www.google.com/search?q=%233-tools-n8n-error-analyzer)  
4. [Database Architecture](https://www.google.com/search?q=%234-database-architecture)  
5. [Testing & Validation](https://www.google.com/search?q=%235-testing--validation)  
6. [n8n & RetellAI Configuration](https://www.google.com/search?q=%236-n8n--retellai-configuration)  
7. [Troubleshooting](https://www.google.com/search?q=%237-troubleshooting)

## **1\. Environment Overview**

### **Windows PC (Local)**

* **User:** peter  
* **Home:** C:\\Users\\peter\\  
* **Working Dir:** C:\\Users\\peter\\Downloads\\  
* **SSH Key:** C:\\Users\\peter\\.ssh\\metabase-aws

### **AWS EC2 (Server)**

* **Public IP:** 54.149.95.69  
* **Internal IP:** 172.31.0.243  
* **User:** ubuntu  
* **Host Prompt:** ubuntu@ip-172-31-0-243:\~$  
* **Docker Container:** n8n-postgres-1

### **Service URLs**

* **n8n Web UI:** https://auto.yr.com.au  
* **Cliniko API:** https://api.au2.cliniko.com/v1/

## **2\. Connectivity (SSH & SCP)**

### **Connecting to EC2**

**From Windows PowerShell:**

ssh \-i "C:\\Users\\peter\\.ssh\\metabase-aws" ubuntu@54.149.95.69

### **File Transfer (SCP)**

**Upload (Windows → EC2):**

scp \-i "C:\\Users\\peter\\.ssh\\metabase-aws" \`  
    "C:\\Users\\peter\\Downloads\\script.py" \`  
    ubuntu@54.149.95.69:\~/script.py

**Download (EC2 → Windows):**

\# Single File  
scp \-i "C:\\Users\\peter\\.ssh\\metabase-aws" \`  
    ubuntu@54.149.95.69:\~/error\_analysis.csv \`  
    "C:\\Users\\peter\\Downloads\\error\_analysis.csv"

\# Entire Folder  
scp \-i "C:\\Users\\peter\\.ssh\\metabase-aws" \-r \`  
    ubuntu@54.149.95.69:/tmp/folder \`  
    "C:\\Users\\peter\\Downloads\\folder"

## **3\. Tools: n8n Error Analyzer & Daily Error Report**

### **3.1 n8n Error Analyzer** (Manual Analysis)

The n8n\_error\_analyzer.py is the primary tool for diagnosing RetellAI missing data issues.

**Mode A: API Mode (Recommended for Windows)**

*Runs from your PC, connects via n8n API.*

1. **API Key Location:** Stored in `.env` file at:
   `C:\\Users\\peter\\Downloads\\CC\\n8n\\Python\\Diagnose-n8n-Errors\\.env`

2. **Run:**
   cd C:\\Users\\peter\\Downloads\\CC\\n8n\\Python\\Diagnose-n8n-Errors
   python n8n\_error\_analyzer.py

3. **Configuration:** API key automatically loaded from `.env` file.

### **3.2 Daily Error Report Emailer** (Automated Monitoring)

**NEW:** Automated script that runs twice daily and emails error reports.

* **Location:** `C:\\Users\\peter\\Downloads\\CC\\n8n\\Python\\CC-Made-daily_error_report_emailer.py`
* **Features:**
  \- Uses n8n API (from `.env` file)
  \- Monitors ACTIVE workflows only
  \- Categorizes errors: RetellAI vs n8n vs Other
  \- Generates formatted HTML email reports
  \- Shows successful workflows in neat tables

**Run Manually:**

cd C:\\Users\\peter\\Downloads\\CC\\n8n\\Python
python CC-Made-daily\_error\_report\_emailer.py

**Scheduled:** Set up Windows Task Scheduler to run at 7am & 7pm (see guide in n8n/Guides Docs folder).

### **Mode B: Database Mode (Recommended for EC2)**

*Runs on the server, queries Postgres directly. Faster, no API key needed.*

1. **SSH into EC2:** (See Connectivity section).  
2. **Run:**  
   python3 n8n\_error\_analyzer.py \--database

### **Weekly Monitoring Workflow**

Run this once a week to track improvements.

\# Windows PowerShell  
python n8n\_error\_analyzer.py \--export-csv  
Rename-Item error\_analysis.csv "errors\_$(Get-Date \-Format 'yyyy-MM-dd').csv"

### **Interpreting Results**

If the analyzer reports **RETELLAI MISSING DATA**:

1. Check the **"Missing fields breakdown"** (e.g., caller\_name: 6 times).  
2. Open the corresponding **RetellAI JSON** file.  
3. Verify the conversation node collects the data.  
4. Verify the Tool parameters include the field.

## **4\. Database Architecture**

**Container Name:** n8n-postgres-1

### **🚨 Critical Distinction**

There are two distinct databases inside the Postgres container. **Do not mix them up.**

| Database Name | Purpose | Access Command |
| :---- | :---- | :---- |
| **retellai\_prod** | **Application Data** (Patients, Appts, Webhook Logs) | docker exec \-it n8n-postgres-1 psql \-U n8n \-d retellai\_prod |
| **n8n** | **Internal System** (Workflow execution logs, errors) | docker exec \-it n8n-postgres-1 psql \-U n8n \-d n8n |

### **Common SQL Operations (retellai\_prod)**

**Check Webhook Logs:**

SELECT \* FROM webhook\_log   
ORDER BY created\_at DESC   
LIMIT 10;

Running SQL Files:  
Never run from /mnt/. Always copy to /tmp/ first.  
\# 1\. Copy to container  
docker cp script.sql n8n-postgres-1:/tmp/

\# 2\. Execute  
docker exec \-it n8n-postgres-1 psql \-U n8n \-d retellai\_prod \-f /tmp/script.sql

## **5\. Testing & Validation**

### **🧪 Designated Test Patient**

**CRITICAL:** Only use this profile for testing. Never use real patient data.

* **Name:** Peter Ball  
* **Phone:** 61412111000  
* **Patient ID:** 1805465202989210063  
* **Cliniko URL:** [View in Cliniko](https://reignitehealth.au2.cliniko.com/patients/1805465202989210063)

### **Testing Webhooks (curl)**

curl \-X POST \[https://auto.yr.com.au/webhook/reignite-retell/check-funding\](https://auto.yr.com.au/webhook/reignite-retell/check-funding) \\  
  \-H "Content-Type: application/json" \\  
  \-d '{  
    "args": {"patient\_id": "1805465202989210063"},  
    "call": {"call\_id": "test\_manual\_001"}  
  }' | jq

## **6\. n8n & RetellAI Configuration**

### **Credential IDs (Production)**

| System | ID | Name | Notes |
| :---- | :---- | :---- | :---- |
| **Postgres** | 7IKr1k5yuchz7uQL | n8n Postgres DB | Must point to retellai\_prod |
| **Cliniko** | jjBjG1tO5syL0Ip9 | Reignite-Cliniko | HTTP Basic Auth |

### **Common Workflow Fixes**

* **Postgres Nodes:** Always ensure alwaysOutputData: true is set in the node options, or the workflow will stop if no rows are returned.  
* **SQL Inserts:** Always use RETURNING \* at the end of INSERT statements so n8n receives the ID of the created row.

## **7\. Troubleshooting**

### **Connection Issues**

* **"Identity file not accessible":** You are likely trying to run the ssh command *while already inside* the EC2 server. Check your prompt.  
  * PS C:\\Users\\peter\> \= Windows (Safe to SSH)  
  * ubuntu@ip-172-31...\> \= EC2 (Do not SSH)  
* **"Permission denied (publickey)":** Verify the key path C:\\Users\\peter\\.ssh\\metabase-aws exists.

### **Database Issues**

* **"No such file or directory" (SQL):** You tried to run a file from a path Docker cannot see (like /mnt/). Move the file to /tmp/ inside the container.  
* **"Relation does not exist":** You are likely in the wrong database. Check if you are in n8n instead of retellai\_prod.

### **Error Analyzer Issues**

* **"401 Unauthorized":** Your n8n API key is expired or incorrect. Generate a new one.  
* **"Docker command not found":** You are running the database-mode command on Windows. Use API mode on Windows, or SSH to EC2 first.

---

## **8. n8n Workflow Statistics & Maintenance**

### **Current Workflow Counts (as of 2025-11-27)**

| Category | Count | Notes |
| :---- | :---- | :---- |
| **Active Workflows** | 52 | Production webhooks + scheduled jobs |
| **Active Webhooks** | 45 | RetellAI integration endpoints |
| **Scheduled/Internal** | 7 | Cliniko syncs, error reports, health checks |
| **Inactive (Rollback)** | 60 | Kept for rollback - newest inactive version of each |

### **n8n Update Procedure**

**From Windows (Claude Code can run this):**

```bash
# SSH command format for n8n operations
ssh -i "C:/Users/peter/.ssh/metabase-aws" ubuntu@54.149.95.69 "COMMAND"
```

**Update n8n:**

```bash
# 1. Manual backup first
ssh -i "C:/Users/peter/.ssh/metabase-aws" ubuntu@54.149.95.69 "sudo /usr/local/bin/backup-full.sh"

# 2. Pull latest image
ssh -i "C:/Users/peter/.ssh/metabase-aws" ubuntu@54.149.95.69 "docker pull n8nio/n8n:latest"

# 3. Restart containers
ssh -i "C:/Users/peter/.ssh/metabase-aws" ubuntu@54.149.95.69 "cd /opt/n8n && docker compose down && docker compose up -d"

# 4. Verify
ssh -i "C:/Users/peter/.ssh/metabase-aws" ubuntu@54.149.95.69 "docker ps && docker logs n8n-n8n-1 --tail 20"
```

### **Workflow Cleanup Procedure**

When cleaning up old workflow versions, keep the **newest inactive version** of each workflow type for rollback.

**Delete old versions (keeping newest inactive):**

```sql
-- Run via: docker exec n8n-postgres-1 psql -U n8n -d n8n -c "SQL"

-- Group by base name, keep only newest inactive
WITH base_names AS (
    SELECT
        id, name, "updatedAt",
        REGEXP_REPLACE(
            REGEXP_REPLACE(name, ' v[0-9]+\.[0-9]+.*$', ''),
            ' \(.*\)$', ''
        ) as base_name
    FROM workflow_entity
    WHERE active = false
    AND (name LIKE 'RetellAI%' OR name LIKE 'Reignite%' OR name LIKE 'get-village%'
        OR name LIKE 'log-%' OR name LIKE 'SMS%' OR name LIKE 'Cliniko%')
),
ranked AS (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY base_name ORDER BY "updatedAt" DESC) as rn
    FROM base_names
)
DELETE FROM workflow_entity WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
```

### **Workflows with Zero Usage (Review List)**

These webhooks are active but had 0 executions in 30 days (as of 2025-11-27). May not be wired into the agent:

| Workflow | Notes |
| :---- | :---- |
| `log-faq-query v1.9 PRODUCTION FINAL` | FAQ logging - check if agent uses it |
| `Reignite - Check Protected Slots` | Protected slot checking |
| `Reignite Vapi - Transfer Router` | Vapi system - only if using Vapi |
| `RetellAI - Check Holiday` | Holiday checking - seasonal? |
| `RetellAI - Check Recurring Conflict v1.0` | Conflict checking |
| `RetellAI - Get Class Capacity Rules v1.8 IF NODE` | Capacity rules lookup |
| `RetellAI - Update Client Notes v1.3` | Notes update |

### **High-Usage Workflows (Core System)**

| Workflow | 30-Day Executions | Purpose |
| :---- | :---- | :---- |
| `Cliniko Incremental Sync v2` | 338 | Core patient sync |
| `Cliniko Group Appointments Sync` | 338 | Class/group sync |
| `RetellAI - Lookup Caller by Phone` | 215 | Main caller ID |
| `RetellAI - Lookup Caller by Name & Village` | 88 | Secondary lookup |
| `RetellAI - Create or Get Patient` | 62 | Patient creation |
| `RetellAI - Email End of Call Summary` | 54 | Call logging |

### **Docker Compose Environment Variables**

Located at `/opt/n8n/.env` on EC2:

```
# Deprecation fixes (added 2025-11-27)
N8N_RUNNERS_ENABLED=true
N8N_BLOCK_ENV_ACCESS_IN_NODE=false
N8N_GIT_NODE_DISABLE_BARE_REPOS=true
```

### **Export Manifest Location**

Current webhook manifest: `n8n/JSON/EXPORT_MANIFEST_2025_11_27.json`

---

## **9. SSH Key Path for Windows**

**Important:** When running SSH commands from Windows via Claude Code, use forward slashes:

```bash
# Correct (works from Windows)
ssh -i "C:/Users/peter/.ssh/metabase-aws" ubuntu@54.149.95.69

# Incorrect (path parsing issues)
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@54.149.95.69
```

This applies to all SSH and SCP commands run programmatically.