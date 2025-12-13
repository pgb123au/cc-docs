# SYSTEM_OVERVIEW.md - Document Specification

This document defines all formatting rules, naming conventions, and content structure used to generate `SYSTEM_OVERVIEW.md`. Given raw system data, follow these rules to recreate the document.

---

## 1. Naming Conventions (Anonymization)

| Raw Name | Display As |
|----------|------------|
| n8n | "Automation Workflows" or "Workflow Automation" |
| RetellAI / Retell | "Voice Agent" or "Voice AI" |
| Telnyx | "Telco Provider 1" |
| Zadarma | "Telco Provider 2" |
| RackNerd | "VPS2" |
| Claude / Claude API | "4 Major AI Platforms" or "AI-powered" |
| Cliniko | Keep as-is (practice management) |

**Rule:** Never mention specific AI model names, telco provider names, or secondary hosting providers directly.

---

## 2. Document Structure

### Header
```markdown
# AI Voice Receptionist / Booking System Overview

---
```
**No version line.** No "Last Updated" in header.

---

## 3. Codebase Statistics Table

### Format
```markdown
| Component | Prod Files | Prod Lines | Dev Files | Dev Lines |
|-----------|------:|------:|------:|------:|
```

### Components to Include
1. Voice Agent (v{VERSION}) - single JSON file
2. Automation Workflows - `n8n/JSON/active_workflows/*.json`
3. Automation Scripts - `n8n/Python/*.py` (exclude archive, downloads)
4. Deployment Scripts - `retell/scripts/*.py`
5. Telco Management System - `Telcos/*.py` (all Python files)
6. Server Sync & Health - `Telcos/sync/*.py`
7. API Monitoring - `Telcos/api_monitor/*.py`
8. Custom Slash Commands - `.claude/commands/*.md`

### How to Count
- **Prod Files:** Count files in production directories only
- **Prod Lines:** `wc -l` on those files
- **Dev Files:** Count ALL files including Testing/, archive/, tools/
- **Dev Lines:** `wc -l` on all files

---

## 4. SQL Statistics Table

### Format
```markdown
| Location | Files | Lines | Status |
|----------|------:|------:|--------|
```

### Categories
| Location | Path Pattern | Status |
|----------|--------------|--------|
| Schemas | `n8n/SQL/schemas/*.sql` | Production |
| Migrations | `n8n/SQL/migrations/*.sql` | Production |
| Functions | `n8n/SQL/functions/*.sql` | Active |
| Testing | `n8n/SQL/testing/*.sql` | Development |

---

## 5. Voice Agent Architecture Section

### Core Metrics Table
Include these metrics (extract from agent JSON):
- Conversation Nodes (count nodes where type="conversation")
- Function Nodes (count nodes where type="function")
- Edge Connections (count all "destination_node_id" occurrences)
- Webhook Integrations (count unique tool names)
- Distinct Conversation Paths (estimate: 50+)
- State Variables Tracked (estimate: 35+)
- Global Prompt Size (~15,000 chars)
- Average Node Complexity (edges/nodes ratio)
- Longest Path Depth (estimate: 18 nodes)
- Tool Response Handlers (count edges with tool responses)

### Architecture Highlights (20 items)
Present as bullet list with **Bold Title** - Description format:
1. Equation-Based Routing
2. Silent Pre-Processing
3. Multi-Modal State Machine
4. Graceful Degradation
5. Context Accumulation
6. Dynamic Prompt Injection
7. Parallel Tool Execution
8. Conditional Speech Patterns
9. Error State Recovery
10. Call Handoff Protocol
11. Barge-In Detection
12. Confidence-Based Branching
13. Slot Filling Logic
14. Disambiguation Flows
15. Time-Aware Greetings
16. Caller History Integration
17. Multi-Turn Confirmation
18. Natural Number Handling
19. Sentiment-Aware Responses
20. Fallback Escalation Ladder

### Node Type Distribution Table
```markdown
| Type | Count | Purpose |
|------|------:|---------|
| Conversation | {count} | Speak to caller, collect responses |
| Function | {count} | Silent webhook calls |
| Logic Split | {count} | Variable-based routing |
| End | {count} | Call termination points |
| **Edges** | **{count}** | Connections between nodes defining all possible conversation transitions |
```

---

## 6. Voice Agent Features (80 total)

### Table Format
```markdown
| Feature | Category |
|---------|----------|
```
**Two columns only.** No ranking, no scores.

### Categories
- Booking
- Intelligence
- Funding
- Management
- Classes
- Location
- Communication
- Transfers
- Identification

### Feature Naming Convention
**Feature Name** - Brief description (5-15 words)

Example: `Multi-Step Booking Flow - Funding check → availability → slot selection → confirmation`

---

## 7. Telco Management System Features (20)

Numbered list format:
```markdown
1. **Feature Name** - Description
```

Features to include:
1. Unified Number Dashboard
2. Real-Time Number Status
3. Agent-to-Number Mapping
4. Number Provisioning
5. Number Porting Management
6. Multi-Provider API Integration
7. Cost Tracking by Number
8. Number Search & Filter
9. Bulk Number Operations
10. Number Health Monitoring
11. Call Volume Analytics
12. Failover Configuration
13. Number Tagging System
14. Geographic Distribution View
15. Provider Balance Monitoring
16. Number Release Workflow
17. Inbound Route Management
18. Emergency Number Registry
19. Number Audit Trail
20. Multi-Tenant Support

---

## 8. API Monitoring System Features (20)

Numbered list format. Features:
1. Documentation Change Detection
2. AI-Powered Impact Analysis
3. Multi-Provider Monitoring
4. Automatic GitHub Issue Creation
5. Priority Classification
6. Affected System Mapping
7. Diff Visualization
8. Scheduled Monitoring Runs
9. Alert Email Notifications
10. Historical Change Archive
11. Semantic Version Tracking
12. Endpoint Deprecation Alerts
13. Rate Limit Monitoring
14. Response Schema Validation
15. Authentication Change Detection
16. Webhook Payload Monitoring
17. SDK Compatibility Checks
18. Changelog Parsing
19. Regression Test Triggers
20. Dependency Graph Updates

---

## 9. Server Monitoring System Features (20)

Numbered list format. Features:
1. Dual-Server Health Checks
2. Disk Usage Alerts
3. Memory Utilization Tracking
4. Docker Container Status
5. Service Uptime Monitoring
6. Automated Health Reports
7. SSH Tunnel Health
8. Database Connection Pool
9. SSL Certificate Expiry
10. Cross-Server Sync Status
11. CPU Load Monitoring
12. Network Latency Checks
13. Log File Size Alerts
14. Backup Verification
15. Process Count Monitoring
16. Port Availability Checks
17. DNS Resolution Monitoring
18. Cron Job Verification
19. Error Rate Trending
20. Automated Recovery Scripts

---

## 10. Infrastructure Table

### Format
```markdown
| Component | Details |
|-----------|---------|
```

### Required Rows (21)
1. Voice AI - Conversation flow engine with equation-based routing
2. Automation - {count} active workflows for backend operations
3. Primary Database - PostgreSQL on AWS EC2 ({table_count} tables, cached lookups)
4. Practice Management - Cliniko integration (real-time sync)
5. Secondary Server - VPS2 for monitoring and sync
6. Load Balancing - Geographic routing for optimal latency
7. CDN - Static asset delivery
8. Backup Storage - Automated daily backups with retention policy
9. Server Snapshots - Point-in-time EC2 instance recovery
10. Backup Monitoring - Automated verification of backup completion
11. CloudWatch Metrics - CPU, memory, disk, network monitoring
12. CloudWatch Alarms - Threshold-based alerting for resource usage
13. CloudWatch Logs - Centralized application log aggregation
14. CloudWatch Events - Scheduled tasks and event-driven automation
15. Logging Infrastructure - Centralized log aggregation
16. Secrets Management - Encrypted credential storage
17. CI/CD Pipeline - Automated testing and deployment
18. Staging Environment - Pre-production testing
19. Monitoring Dashboard - Real-time system visibility
20. Alerting System - Multi-channel notifications
21. Documentation Platform - Version-controlled docs

---

## 11. Technology Stack

### Organize by Category

**Voice & Conversation**
- Voice AI Platform - Conversational AI with natural language understanding
- Speech-to-Text - Real-time transcription
- Text-to-Speech - Natural voice synthesis
- WebSocket Streaming - Low-latency audio transport

**Automation & Integration**
- Workflow Automation - Self-hosted automation platform
- Webhook Architecture - RESTful API integrations
- Event-Driven Processing - Async workflow triggers
- OAuth 2.0 - Secure API authentication

**Data & Storage**
- PostgreSQL - Primary database with JSONB caching
- Redis-Style Caching - Response memoization
- JSONB Documents - Flexible schema storage
- Incremental Sync - Delta-based data updates

**External Services**
- Cliniko API - Practice management integration
- Telco Provider 1 - Primary telephony and SMS
- Telco Provider 2 - VoIP and call routing
- SMS Provider - Mobile message delivery
- Gmail API - Email notifications
- Google Sheets API - Reporting and data export

**Development & Deployment**
- Python 3.11 - Automation scripts
- Node.js - Webhook processing
- Git - Version control
- GitHub - Repository hosting
- 4 Major AI Platforms - AI-powered analysis and generation

**Monitoring & Observability**
- Custom Health Checks - Server monitoring scripts
- API Change Monitor - Documentation tracking
- Error Logging - Centralized error capture
- Call Analytics - Performance dashboards

---

## 12. Formatting Rules

1. **Tables:** Right-align numeric columns using `------:|`
2. **No emojis** unless explicitly requested
3. **Horizontal rules:** Use `---` between major sections
4. **Bold:** Use for feature names in lists, table headers
5. **No version numbers** in document header
6. **Footer:** None required

---

## 13. Data Extraction Commands

```bash
# Voice agent stats
cd /c/Users/peter/Downloads/CC/retell/agents
cat *.json | grep -c '"type".*conversation"'  # Conversation nodes
cat *.json | grep -c '"destination_node_id"'   # Edge count

# Production file counts
find n8n/JSON/active_workflows -name "*.json" | wc -l
find n8n/Python -maxdepth 1 -name "*.py" | wc -l
find retell/scripts -name "*.py" | wc -l

# Line counts
wc -l n8n/JSON/active_workflows/*.json
wc -l n8n/Python/*.py
wc -l retell/scripts/*.py
```

---

*This specification enables exact recreation of SYSTEM_OVERVIEW.md from raw system data.*
