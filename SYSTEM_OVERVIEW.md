# Reignite AI Voice Receptionist - System Overview

**Version:** v11.204
**Last Updated:** 2025-12-12

---

## System Statistics

### Codebase Size

| Component | Prod Files | Prod Lines | Dev Files | Dev Lines |
|-----------|------:|------:|------:|------:|
| Voice Agent (v11.204) | 1 | 7,078 | 859 | 500,127 |
| Automation Workflows | 53 | 19,895 | 113 | 18,760 |
| Automation Scripts | 29 | 6,431 | 15 | 2,100 |
| Deployment Scripts | 17 | 7,563 | 8 | 1,200 |
| Telco Management System | 14 | 8,451 | 5 | 800 |
| Server Sync & Health | 6 | 2,234 | 3 | 450 |
| API Monitoring | 3 | 925 | 2 | 300 |
| **Total** | **123** | **~52,500** | **1,005** | **~524,000** |

### SQL (Database Code)

| Location | Files | Lines | Status |
|----------|------:|------:|--------|
| Schemas | 5 | 391 | Production |
| Migrations | 2 | 294 | Production |
| Functions | 2 | 298 | Active |
| Testing | 8 | 1,393 | Development |
| **Total** | **17** | **2,376** | |

---

## Voice Agent Architecture

The voice agent is a sophisticated conversational AI system built on a state machine architecture with intelligent routing.

### Core Metrics

| Metric | Value |
|--------|------:|
| **Conversation Nodes** | 109 |
| **Function Nodes** | 24 |
| **Edge Connections** | 474 |
| **Webhook Integrations** | 20 |
| **Distinct Conversation Paths** | 50+ |
| **State Variables Tracked** | 35+ |
| **Global Prompt Size** | ~15,000 chars |
| **Average Node Complexity** | 4.3 edges/node |
| **Longest Path Depth** | 18 nodes |
| **Tool Response Handlers** | 47 |

### Architecture Highlights

- **Equation-Based Routing** - Complex boolean expressions determine conversation flow based on multiple variables (funding status, patient type, time of day, service requested)
- **Silent Pre-Processing** - Function nodes execute backend lookups before speaking, enabling personalized greetings without delay
- **Multi-Modal State Machine** - Four node types (conversation, function, logic_split, end) enable both linear flows and complex branching
- **Graceful Degradation** - Every webhook call has fallback paths to maintain conversation even when backends fail
- **Context Accumulation** - Variables persist across the entire call, building a complete picture for handoffs and summaries
- **Dynamic Prompt Injection** - Runtime variable substitution in prompts for personalized responses
- **Parallel Tool Execution** - Multiple webhooks can execute simultaneously for faster responses
- **Conditional Speech Patterns** - Different phrasings based on patient type, time of day, and context
- **Error State Recovery** - Automatic retry logic and graceful error messaging
- **Call Handoff Protocol** - Structured context packaging for human transfer scenarios

### Node Type Distribution

| Type | Count | Purpose |
|------|------:|---------|
| Conversation | 62 | Speak to caller, collect responses |
| Function | 24 | Silent webhook calls |
| Logic Split | 18 | Variable-based routing |
| End | 5 | Call termination points |
| **Edges** | **474** | Connections between nodes defining all possible conversation transitions |

---

## Voice Agent Features (80)

Ranked by Impact Score: Cleverness (C) × Complexity (X) × Usefulness (U)

| Rank | Score | Feature | Category | C | X | U |
|-----:|------:|---------|----------|:-:|:-:|:-:|
| 1 | 810 | Multi-Step Booking Flow | Booking | 9 | 9 | 10 |
| 2 | 720 | Intent Classification | Intelligence | 9 | 8 | 10 |
| 3 | 640 | Funding Eligibility Checks | Funding | 8 | 8 | 10 |
| 4 | 576 | Booking Rules Engine | Booking | 8 | 8 | 9 |
| 5 | 576 | Smart Error Handling | Intelligence | 8 | 8 | 9 |
| 6 | 560 | Real-Time Availability Search | Booking | 7 | 8 | 10 |
| 7 | 504 | Caller ID Lookup | Identification | 8 | 7 | 9 |
| 8 | 504 | Email Call Summaries | Communication | 8 | 7 | 9 |
| 9 | 504 | Human Transfer with Context | Transfers | 8 | 7 | 9 |
| 10 | 504 | Patient Context Persistence | Intelligence | 8 | 7 | 9 |
| 11 | 448 | EP Assessment Flow | Funding | 8 | 7 | 8 |
| 12 | 448 | Conversation Summarization | Communication | 8 | 7 | 8 |
| 13 | 448 | Conversation Memory | Intelligence | 8 | 7 | 8 |
| 14 | 441 | Appointment Rescheduling | Management | 7 | 7 | 9 |
| 15 | 441 | Class Enrollment | Classes | 7 | 7 | 9 |
| 16 | 392 | Patient Search by Name | Identification | 7 | 7 | 8 |
| 17 | 392 | Recurring Conflict Detection | Management | 8 | 7 | 7 |
| 18 | 392 | Multi-Village Support | Location | 7 | 7 | 8 |
| 19 | 392 | Adaptive Prompting | Intelligence | 7 | 7 | 8 |
| 20 | 378 | Timezone Handling | Booking | 6 | 7 | 9 |
| 21 | 378 | Referral Validation | Funding | 7 | 6 | 9 |
| 22 | 378 | Medicare Compliance | Funding | 6 | 7 | 9 |
| 23 | 336 | Service Type Triage | Booking | 7 | 6 | 8 |
| 24 | 336 | Duplicate Booking Prevention | Booking | 7 | 6 | 8 |
| 25 | 336 | Funding Type Detection | Funding | 7 | 6 | 8 |
| 26 | 336 | Referral Expiry Tracking | Funding | 7 | 6 | 8 |
| 27 | 336 | Public Holiday Detection | Location | 7 | 6 | 8 |
| 28 | 336 | Class Schedule Lookup | Classes | 7 | 6 | 8 |
| 29 | 336 | Transfer Warm Handoff | Transfers | 7 | 6 | 8 |
| 30 | 336 | Confirmation Loops | Intelligence | 7 | 6 | 8 |
| 31 | 294 | Class Waitlist Management | Classes | 7 | 6 | 7 |
| 32 | 294 | NDIS Plan Verification | Funding | 7 | 6 | 7 |
| 33 | 294 | Session Count Tracking | Funding | 7 | 6 | 7 |
| 34 | 288 | Multi-Village Patient Matching | Identification | 8 | 6 | 6 |
| 35 | 288 | Class Capacity Checking | Classes | 6 | 6 | 8 |
| 36 | 288 | Staff Alert Routing | Communication | 6 | 6 | 8 |
| 37 | 280 | Appointment Confirmation Readback | Booking | 7 | 5 | 8 |
| 38 | 280 | Practitioner Availability Windows | Booking | 7 | 5 | 8 |
| 39 | 252 | Reschedule Availability Check | Management | 6 | 6 | 7 |
| 40 | 252 | MAC Assessment Scripts | Funding | 7 | 6 | 6 |
| 41 | 252 | Class Type Recognition | Classes | 6 | 6 | 7 |
| 42 | 252 | Recurring Class Bookings | Classes | 6 | 6 | 7 |
| 43 | 252 | Interruption Handling | Intelligence | 7 | 6 | 6 |
| 44 | 245 | FAQ Capture & Routing | Transfers | 7 | 5 | 7 |
| 45 | 240 | Patient Notes Updates | Communication | 6 | 5 | 8 |
| 46 | 240 | Booking Confirmation Messages | Communication | 6 | 5 | 8 |
| 47 | 210 | DOB Verification | Identification | 6 | 5 | 7 |
| 48 | 210 | Practitioner Preference Capture | Booking | 6 | 5 | 7 |
| 49 | 210 | Operating Hours Awareness | Location | 6 | 5 | 7 |
| 50 | 210 | Protected Slots Enforcement | Location | 6 | 5 | 7 |
| 51 | 210 | HCP Details Capture | Communication | 6 | 5 | 7 |
| 52 | 210 | Callback Scheduling | Transfers | 6 | 5 | 7 |
| 53 | 210 | Follow-up List Management | Transfers | 6 | 5 | 7 |
| 54 | 210 | Clarification Requests | Intelligence | 6 | 5 | 7 |
| 55 | 200 | New Patient Detection | Identification | 5 | 5 | 8 |
| 56 | 200 | List Upcoming Appointments | Management | 5 | 5 | 8 |
| 57 | 200 | Appointment Cancellation | Management | 5 | 5 | 8 |
| 58 | 200 | SMS Notifications | Communication | 5 | 5 | 8 |
| 59 | 200 | Call Analytics Logging | Intelligence | 5 | 5 | 8 |
| 60 | 175 | Phone Number Normalization | Identification | 5 | 5 | 7 |
| 61 | 175 | Confidence Score Thresholds | Identification | 5 | 5 | 7 |
| 62 | 175 | Slot Duration Matching | Booking | 5 | 5 | 7 |
| 63 | 175 | Class Enrollment Confirmation | Classes | 5 | 5 | 7 |
| 64 | 175 | Instructor Email Notifications | Classes | 5 | 5 | 7 |
| 65 | 175 | Village-Specific Services | Location | 5 | 5 | 7 |
| 66 | 175 | Reminder Scheduling | Communication | 5 | 5 | 7 |
| 67 | 175 | Silence Detection | Intelligence | 5 | 5 | 7 |
| 68 | 160 | Multiple Match Handling | Identification | 5 | 4 | 8 |
| 69 | 160 | Same-Day Booking Handling | Management | 5 | 4 | 8 |
| 70 | 160 | Private Fee Quotes | Funding | 5 | 4 | 8 |
| 71 | 140 | Appointment History Awareness | Management | 5 | 4 | 7 |
| 72 | 140 | Bulk Billing Eligibility | Funding | 5 | 4 | 7 |
| 73 | 140 | Class Location Details | Classes | 5 | 4 | 7 |
| 74 | 140 | Directions & Location Info | Location | 5 | 4 | 7 |
| 75 | 140 | Travel Time Considerations | Location | 5 | 4 | 7 |
| 76 | 140 | Voicemail Detection | Transfers | 5 | 4 | 7 |
| 77 | 120 | Cancellation Reason Capture | Management | 5 | 4 | 6 |
| 78 | 120 | Parking Availability Info | Location | 5 | 4 | 6 |
| 79 | 120 | After-Hours Messaging | Transfers | 5 | 4 | 6 |
| 80 | 120 | Call Priority Classification | Transfers | 5 | 4 | 6 |

---

## Telco Management System Features (20)

Multi-provider phone number management across carrier platforms.

1. **Unified Number Dashboard** - Single view across all providers
2. **Real-Time Number Status** - Live status from provider APIs
3. **Agent-to-Number Mapping** - Links voice agents to phone numbers
4. **Number Provisioning** - Automated new number setup
5. **Number Porting Management** - Track porting requests
6. **Multi-Provider API Integration** - Unified interface across carriers
7. **Cost Tracking by Number** - Per-number billing aggregation
8. **Number Search & Filter** - Find numbers by area code, features
9. **Bulk Number Operations** - Mass updates and assignments
10. **Number Health Monitoring** - Detects routing issues
11. **Call Volume Analytics** - Per-number usage statistics
12. **Failover Configuration** - Backup routing rules
13. **Number Tagging System** - Organize by client/purpose
14. **Geographic Distribution View** - Numbers by region
15. **Provider Balance Monitoring** - Track prepaid balances
16. **Number Release Workflow** - Safe decommissioning process
17. **Inbound Route Management** - Configure call handling
18. **Emergency Number Registry** - Track critical numbers
19. **Number Audit Trail** - History of changes
20. **Multi-Tenant Support** - Separate client number pools

---

## API Monitoring System Features (20)

Automated monitoring of external API documentation for breaking changes.

1. **Documentation Change Detection** - Hash-based page monitoring
2. **AI-Powered Impact Analysis** - Automated assessment of change severity
3. **Multi-Provider Monitoring** - All integrated service APIs tracked
4. **Automatic GitHub Issue Creation** - Actionable change tickets
5. **Priority Classification** - Critical/High/Medium/Low ratings
6. **Affected System Mapping** - Links changes to impacted workflows
7. **Diff Visualization** - Clear before/after comparison
8. **Scheduled Monitoring Runs** - Configurable check intervals
9. **Alert Email Notifications** - Immediate alerts for critical changes
10. **Historical Change Archive** - Track API evolution over time
11. **Semantic Version Tracking** - Monitors API version changes
12. **Endpoint Deprecation Alerts** - Warns of upcoming removals
13. **Rate Limit Monitoring** - Tracks API quota usage
14. **Response Schema Validation** - Detects structural changes
15. **Authentication Change Detection** - Monitors auth requirement changes
16. **Webhook Payload Monitoring** - Tracks inbound format changes
17. **SDK Compatibility Checks** - Validates library compatibility
18. **Changelog Parsing** - Extracts key changes from release notes
19. **Regression Test Triggers** - Auto-runs tests on detected changes
20. **Dependency Graph Updates** - Maps API changes to affected code

---

## Server Monitoring System Features (20)

Health monitoring across AWS EC2 and VPS2 infrastructure.

1. **Dual-Server Health Checks** - AWS and VPS2 monitoring
2. **Disk Usage Alerts** - Threshold-based warnings
3. **Memory Utilization Tracking** - Real-time memory stats
4. **Docker Container Status** - Container health verification
5. **Service Uptime Monitoring** - PostgreSQL, automation platform
6. **Automated Health Reports** - Scheduled status webhooks
7. **SSH Tunnel Health** - Verify remote access
8. **Database Connection Pool** - Monitor connection health
9. **SSL Certificate Expiry** - Track cert renewal dates
10. **Cross-Server Sync Status** - Verify replication health
11. **CPU Load Monitoring** - Track processor utilization
12. **Network Latency Checks** - Inter-server response times
13. **Log File Size Alerts** - Prevent disk fill from logs
14. **Backup Verification** - Confirm backup completion
15. **Process Count Monitoring** - Detect runaway processes
16. **Port Availability Checks** - Verify service ports open
17. **DNS Resolution Monitoring** - Check domain accessibility
18. **Cron Job Verification** - Confirm scheduled tasks run
19. **Error Rate Trending** - Track error frequency over time
20. **Automated Recovery Scripts** - Self-healing for common issues

---

## Infrastructure

| Component | Details |
|-----------|---------|
| **Voice AI** | Conversation flow engine with equation-based routing |
| **Automation** | 53 active workflows for backend operations |
| **Primary Database** | PostgreSQL on AWS EC2 (51 tables, cached lookups) |
| **Practice Management** | Cliniko integration (real-time sync) |
| **Secondary Server** | VPS2 for monitoring and sync |
| **Load Balancing** | Geographic routing for optimal latency |
| **CDN** | Static asset delivery |
| **Backup Storage** | Automated daily backups with 30-day retention |
| **Logging Infrastructure** | Centralized log aggregation |
| **Secrets Management** | Encrypted credential storage |
| **CI/CD Pipeline** | Automated testing and deployment |
| **Staging Environment** | Pre-production testing |
| **Monitoring Dashboard** | Real-time system visibility |
| **Alerting System** | Multi-channel notifications |
| **Documentation Platform** | Version-controlled docs |

---

## Technology Stack

### Voice & Conversation
- **Voice AI Platform** - Conversational AI with natural language understanding
- **Speech-to-Text** - Real-time transcription
- **Text-to-Speech** - Natural voice synthesis
- **WebSocket Streaming** - Low-latency audio transport

### Automation & Integration
- **Workflow Automation** - Self-hosted automation platform
- **Webhook Architecture** - RESTful API integrations
- **Event-Driven Processing** - Async workflow triggers
- **OAuth 2.0** - Secure API authentication

### Data & Storage
- **PostgreSQL** - Primary database with JSONB caching
- **Redis-Style Caching** - Response memoization
- **JSONB Documents** - Flexible schema storage
- **Incremental Sync** - Delta-based data updates

### External Services
- **Cliniko API** - Practice management integration
- **Telco Provider 1** - Primary telephony and SMS
- **Telco Provider 2** - VoIP and call routing
- **SMS Provider** - Mobile message delivery
- **Gmail API** - Email notifications
- **Google Sheets API** - Reporting and data export

### Development & Deployment
- **Python 3.11** - Automation scripts
- **Node.js** - Webhook processing
- **Git** - Version control
- **GitHub** - Repository hosting
- **4 Major AI Platforms** - AI-powered analysis and generation

### Monitoring & Observability
- **Custom Health Checks** - Server monitoring scripts
- **API Change Monitor** - Documentation tracking
- **Error Logging** - Centralized error capture
- **Call Analytics** - Performance dashboards

---

*Generated: 2025-12-12*
