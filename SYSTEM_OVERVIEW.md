# Reignite AI Voice Receptionist - System Overview

**Version:** v11.204
**Last Updated:** 2025-12-12

---

## System Statistics

### Codebase Size (Production)

| Component | Files | Lines |
|-----------|------:|------:|
| Voice Agent (v11.204) | 1 | 7,078 |
| Automation Workflows | 53 | 19,895 |
| Automation Scripts | 29 | 6,431 |
| Deployment Scripts | 17 | 7,563 |
| Telco Management System | 14 | 8,451 |
| Server Sync & Health | 6 | 2,234 |
| API Monitoring | 3 | 925 |
| **Production Total** | **123** | **~52,500** |

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
| **Webhook Integrations** | 20 |
| **Distinct Conversation Paths** | 50+ |
| **State Variables Tracked** | 35+ |

### Architecture Highlights

- **Equation-Based Routing** - Complex boolean expressions determine conversation flow based on multiple variables (funding status, patient type, time of day, service requested)
- **Silent Pre-Processing** - Function nodes execute backend lookups before speaking, enabling personalized greetings without delay
- **Multi-Modal State Machine** - Four node types (conversation, function, logic_split, end) enable both linear flows and complex branching
- **Graceful Degradation** - Every webhook call has fallback paths to maintain conversation even when backends fail
- **Context Accumulation** - Variables persist across the entire call, building a complete picture for handoffs and summaries

### Node Type Distribution

| Type | Count | Purpose |
|------|------:|---------|
| Conversation | 62 | Speak to caller, collect responses |
| Function | 24 | Silent webhook calls |
| Logic Split | 18 | Variable-based routing |
| End | 5 | Call termination points |

---

## Voice Agent Features (80)

### Patient Identification & Verification
1. **Caller ID Lookup** - Silent pre-greeting phone lookup for personalized experience
2. **Patient Search by Name** - Fuzzy matching with confidence scoring
3. **DOB Verification** - Secondary verification for uncertain matches
4. **Multi-Village Patient Matching** - Disambiguates same-name patients across locations
5. **New Patient Detection** - Routes first-time callers to registration
6. **Phone Number Normalization** - Handles Australian mobile/landline formats
7. **Confidence Score Thresholds** - Configurable match certainty requirements
8. **Multiple Match Handling** - Presents options when several patients match

### Appointment Booking
9. **Multi-Step Booking Flow** - Funding → availability → slot → confirmation
10. **Practitioner Preference Capture** - Records and respects preferred provider
11. **Service Type Triage** - Routes to appropriate service category
12. **Real-Time Availability Search** - Live calendar queries with slot aggregation
13. **Appointment Confirmation Readback** - Verbal confirmation before finalizing
14. **Duplicate Booking Prevention** - Checks existing appointments first
15. **Booking Rules Engine** - Enforces lead times, practitioner requirements
16. **Timezone Handling** - Sydney/Melbourne conversion with DST awareness
17. **Practitioner Availability Windows** - Respects individual schedules
18. **Slot Duration Matching** - Ensures service fits available time

### Appointment Management
19. **List Upcoming Appointments** - Retrieves and reads scheduled visits
20. **Appointment Rescheduling** - Atomic cancel + rebook flow
21. **Reschedule Availability Check** - Context-aware slot queries
22. **Appointment Cancellation** - With reason tracking and confirmation
23. **Cancellation Reason Capture** - Analytics on why patients cancel
24. **Recurring Conflict Detection** - Prevents double-booking recurring slots
25. **Appointment History Awareness** - References past visits in conversation
26. **Same-Day Booking Handling** - Special flow for urgent requests

### Funding & Eligibility
27. **Funding Eligibility Checks** - Validates HCP/NDIS/Private status
28. **Funding Type Detection** - Auto-determines from patient records
29. **Referral Validation** - Checks Medicare referral existence
30. **Referral Expiry Tracking** - Monitors validity and remaining sessions
31. **EP Assessment Flow** - Tracks exercise physiology requirements
32. **Medicare Compliance** - Ensures bookings meet funding rules
33. **NDIS Plan Verification** - Validates NDIS funding status
34. **Private Fee Quotes** - Provides pricing for self-funded patients
35. **Bulk Billing Eligibility** - Checks concession card status
36. **Session Count Tracking** - Monitors remaining funded sessions

### Exercise Classes
37. **Class Schedule Lookup** - Retrieves classes by type and location
38. **Class Enrollment** - Books into group sessions with capacity check
39. **Class Capacity Checking** - Validates spots before enrollment
40. **Class Waitlist Management** - Queues patients for full classes
41. **Class Enrollment Confirmation** - Details and notification sending
42. **Instructor Email Notifications** - Alerts instructors of enrollments
43. **Class Type Recognition** - Understands Pilates, Strength, Yoga, etc.
44. **Recurring Class Bookings** - Weekly/fortnightly enrollment options
45. **Class Location Details** - Venue-specific instructions

### Location & Scheduling
46. **Multi-Village Support** - Routes to correct clinic location
47. **Directions & Location Info** - Addresses and parking details
48. **Operating Hours Awareness** - Business hours validation
49. **Public Holiday Detection** - Australian holiday calendar
50. **Protected Slots Enforcement** - Respects blocked time for meetings
51. **Village-Specific Services** - Different offerings per location
52. **Travel Time Considerations** - Accounts for patient travel
53. **Parking Availability Info** - Location-specific parking guidance

### Patient Communication
54. **SMS Notifications** - Appointment confirmations via SMS
55. **Email Call Summaries** - End-of-call reports to staff
56. **Conversation Summarization** - Auto-generated call summaries
57. **Patient Notes Updates** - Appends notes to records
58. **HCP Details Capture** - Records referral information
59. **MAC Assessment Scripts** - Medical Assessment Certification handling
60. **Booking Confirmation Messages** - Multi-channel confirmations
61. **Reminder Scheduling** - Triggers for future reminders
62. **Staff Alert Routing** - Urgent matters to specific staff

### Call Handling & Transfers
63. **Human Transfer with Context** - Seamless escalation to receptionist
64. **FAQ Capture & Routing** - Logs unanswered questions
65. **Callback Scheduling** - Captures callback requests
66. **Follow-up List Management** - Tracks patients needing intervention
67. **After-Hours Messaging** - Custom flows outside business hours
68. **Voicemail Detection** - Handles answering machine scenarios
69. **Call Priority Classification** - Urgent vs routine handling
70. **Transfer Warm Handoff** - Context passed to human agent

### System Intelligence
71. **Intent Classification** - NLU-driven intent detection
72. **Smart Error Handling** - Graceful backend failure recovery
73. **Patient Context Persistence** - State across tool calls
74. **Conversation Memory** - References earlier in same call
75. **Adaptive Prompting** - Adjusts based on patient responses
76. **Silence Detection** - Handles pauses appropriately
77. **Interruption Handling** - Manages caller interruptions
78. **Clarification Requests** - Asks for unclear input
79. **Confirmation Loops** - Verifies critical information
80. **Call Analytics Logging** - Tracks outcomes for reporting

---

## Telco Management System Features (20)

Multi-provider phone number management across Telnyx, Zadarma, and voice platform.

1. **Unified Number Dashboard** - Single view across all carriers
2. **Real-Time Number Status** - Live status from carrier APIs
3. **Agent-to-Number Mapping** - Links voice agents to phone numbers
4. **Number Provisioning** - Automated new number setup
5. **Number Porting Management** - Track porting requests
6. **Carrier API Integration** - Telnyx, Zadarma unified interface
7. **Cost Tracking by Number** - Per-number billing aggregation
8. **Number Search & Filter** - Find numbers by area code, features
9. **Bulk Number Operations** - Mass updates and assignments
10. **Number Health Monitoring** - Detects routing issues
11. **Call Volume Analytics** - Per-number usage statistics
12. **Failover Configuration** - Backup routing rules
13. **Number Tagging System** - Organize by client/purpose
14. **Geographic Distribution View** - Numbers by region
15. **Carrier Balance Monitoring** - Track prepaid balances
16. **Number Release Workflow** - Safe decommissioning process
17. **Inbound Route Management** - Configure call handling
18. **Emergency Number Registry** - Track critical numbers
19. **Number Audit Trail** - History of changes
20. **Multi-Tenant Support** - Separate client number pools

---

## API Monitoring System Features (10)

Automated monitoring of external API documentation for breaking changes.

1. **Documentation Change Detection** - Hash-based page monitoring
2. **Claude-Powered Impact Analysis** - AI assessment of change severity
3. **Multi-Provider Monitoring** - Cliniko, Telnyx, Zadarma, voice platform
4. **Automatic GitHub Issue Creation** - Actionable change tickets
5. **Priority Classification** - Critical/High/Medium/Low ratings
6. **Affected System Mapping** - Links changes to impacted workflows
7. **Diff Visualization** - Clear before/after comparison
8. **Scheduled Monitoring Runs** - Configurable check intervals
9. **Alert Email Notifications** - Immediate alerts for critical changes
10. **Historical Change Archive** - Track API evolution over time

---

## Server Monitoring System Features (10)

Health monitoring across AWS EC2 and RackNerd infrastructure.

1. **Dual-Server Health Checks** - AWS and RackNerd monitoring
2. **Disk Usage Alerts** - Threshold-based warnings
3. **Memory Utilization Tracking** - Real-time memory stats
4. **Docker Container Status** - Container health verification
5. **Service Uptime Monitoring** - PostgreSQL, automation platform
6. **Automated Health Reports** - Scheduled status webhooks
7. **SSH Tunnel Health** - Verify remote access
8. **Database Connection Pool** - Monitor connection health
9. **SSL Certificate Expiry** - Track cert renewal dates
10. **Cross-Server Sync Status** - Verify replication health

---

## Infrastructure

| Component | Details |
|-----------|---------|
| **Voice AI** | Conversation flow engine with equation-based routing |
| **Automation** | 53 active workflows for backend operations |
| **Database** | PostgreSQL on AWS EC2 (51 tables, cached lookups) |
| **Practice Management** | Cliniko integration (real-time sync) |
| **Secondary Server** | RackNerd VPS for monitoring and sync |

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
- **Telnyx API** - Telephony and SMS
- **Zadarma API** - VoIP and call routing
- **Gmail API** - Email notifications
- **Google Sheets API** - Reporting and data export

### Infrastructure
- **AWS EC2** - Primary cloud compute
- **RackNerd VPS** - Secondary monitoring server
- **Docker** - Container orchestration
- **Ubuntu Server** - Operating system
- **SSH Tunnels** - Secure remote access
- **Nginx** - Reverse proxy

### Development & Deployment
- **Python 3.11** - Automation scripts
- **Node.js** - Webhook processing
- **Git** - Version control
- **GitHub** - Repository hosting
- **Claude API** - AI-powered analysis tools

### Monitoring & Observability
- **Custom Health Checks** - Server monitoring scripts
- **API Change Monitor** - Documentation tracking
- **Error Logging** - Centralized error capture
- **Call Analytics** - Performance dashboards

---

*Generated: 2025-12-12*
