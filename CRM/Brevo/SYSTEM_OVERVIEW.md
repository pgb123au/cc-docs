# AI Voice Receptionist / Booking System Overview

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
| Custom Slash Commands | 29 | 5,720 | 5 | 400 |
| **Total** | **152** | **~58,300** | **1,010** | **~524,000** |

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
- **Barge-In Detection** - Allows callers to interrupt and redirect conversation mid-speech
- **Confidence-Based Branching** - Routes differently based on speech recognition confidence scores
- **Slot Filling Logic** - Progressively collects required information across multiple turns
- **Disambiguation Flows** - Handles ambiguous responses with targeted clarification questions
- **Time-Aware Greetings** - Adjusts salutations based on time of day (morning/afternoon/evening)
- **Caller History Integration** - References previous calls and appointments in conversation
- **Multi-Turn Confirmation** - Complex bookings require staged confirmation checkpoints
- **Natural Number Handling** - Understands spoken dates, times, and phone numbers in various formats
- **Sentiment-Aware Responses** - Adjusts tone based on detected caller frustration or urgency
- **Fallback Escalation Ladder** - Progressive escalation from retry to clarify to transfer

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

| Feature | Category |
|---------|----------|
| Multi-Step Booking Flow | Booking |
| Intent Classification | Intelligence |
| Funding Eligibility Checks | Funding |
| Booking Rules Engine | Booking |
| Smart Error Handling | Intelligence |
| Real-Time Availability Search | Booking |
| Caller ID Lookup | Identification |
| Email Call Summaries | Communication |
| Human Transfer with Context | Transfers |
| Patient Context Persistence | Intelligence |
| EP Assessment Flow | Funding |
| Conversation Summarization | Communication |
| Conversation Memory | Intelligence |
| Appointment Rescheduling | Management |
| Class Enrollment | Classes |
| Patient Search by Name | Identification |
| Recurring Conflict Detection | Management |
| Multi-Village Support | Location |
| Adaptive Prompting | Intelligence |
| Timezone Handling | Booking |
| Referral Validation | Funding |
| Medicare Compliance | Funding |
| Service Type Triage | Booking |
| Duplicate Booking Prevention | Booking |
| Funding Type Detection | Funding |
| Referral Expiry Tracking | Funding |
| Public Holiday Detection | Location |
| Class Schedule Lookup | Classes |
| Transfer Warm Handoff | Transfers |
| Confirmation Loops | Intelligence |
| Class Waitlist Management | Classes |
| NDIS Plan Verification | Funding |
| Session Count Tracking | Funding |
| Multi-Village Patient Matching | Identification |
| Class Capacity Checking | Classes |
| Staff Alert Routing | Communication |
| Appointment Confirmation Readback | Booking |
| Practitioner Availability Windows | Booking |
| Reschedule Availability Check | Management |
| MAC Assessment Scripts | Funding |
| Class Type Recognition | Classes |
| Recurring Class Bookings | Classes |
| Interruption Handling | Intelligence |
| FAQ Capture & Routing | Transfers |
| Patient Notes Updates | Communication |
| Booking Confirmation Messages | Communication |
| DOB Verification | Identification |
| Practitioner Preference Capture | Booking |
| Operating Hours Awareness | Location |
| Protected Slots Enforcement | Location |
| HCP Details Capture | Communication |
| Callback Scheduling | Transfers |
| Follow-up List Management | Transfers |
| Clarification Requests | Intelligence |
| New Patient Detection | Identification |
| List Upcoming Appointments | Management |
| Appointment Cancellation | Management |
| SMS Notifications | Communication |
| Call Analytics Logging | Intelligence |
| Phone Number Normalization | Identification |
| Confidence Score Thresholds | Identification |
| Slot Duration Matching | Booking |
| Class Enrollment Confirmation | Classes |
| Instructor Email Notifications | Classes |
| Village-Specific Services | Location |
| Reminder Scheduling | Communication |
| Silence Detection | Intelligence |
| Multiple Match Handling | Identification |
| Same-Day Booking Handling | Management |
| Private Fee Quotes | Funding |
| Appointment History Awareness | Management |
| Bulk Billing Eligibility | Funding |
| Class Location Details | Classes |
| Directions & Location Info | Location |
| Travel Time Considerations | Location |
| Voicemail Detection | Transfers |
| Cancellation Reason Capture | Management |
| Parking Availability Info | Location |
| After-Hours Messaging | Transfers |
| Call Priority Classification | Transfers |

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
| **Backup Storage** | Automated daily backups with retention policy |
| **Server Snapshots** | Point-in-time EC2 instance recovery |
| **Backup Monitoring** | Automated verification of backup completion |
| **CloudWatch Metrics** | CPU, memory, disk, network monitoring |
| **CloudWatch Alarms** | Threshold-based alerting for resource usage |
| **CloudWatch Logs** | Centralized application log aggregation |
| **CloudWatch Events** | Scheduled tasks and event-driven automation |
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
