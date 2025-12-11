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
| Telco Scripts | 1 | 3,475 |
| **Production Total** | **101** | **~44,500** |

### SQL (Database Code)

| Location | Files | Lines | Status |
|----------|------:|------:|--------|
| Schemas | 5 | 391 | Production |
| Migrations | 2 | 294 | Production |
| Functions | 2 | 298 | Active |
| Testing | 8 | 1,393 | Development |
| Archive | 2 | 246 | Historical |
| **Total** | **19** | **2,622** | |

**Production SQL: ~983 lines** (9 files)

### Database Tables

**Total: 51 tables**

| Table | Size | Purpose |
|-------|-----:|---------|
| group_appointments | 8.5 MB | Class schedule cache |
| individual_slots_cache | 912 KB | Individual booking slots |
| webhook_log | 904 KB | API call logging |
| patients | 824 KB | Patient records (877 patients) |
| webhook_cache | 176 KB | Response caching |
| appointment_log | 144 KB | Booking history |
| patient_funding_cache | 128 KB | Funding eligibility cache |
| error_log | 128 KB | Error tracking |
| call_log | 120 KB | Call events |
| calls | - | Call records (304 calls) |

### Voice Agent Architecture

- **109 conversation nodes** (conversation, function, logic_split, end)
- **24 function nodes** (webhook calls)
- **20 webhook tools** integrated
- **Equation-based routing** for complex decision trees

---

## Features Ranked by Impact (50)

**Scoring:** Cleverness (1-10) × Complexity (1-10) × Usefulness (1-10)

| Rank | Score | Feature | C | X | U |
|-----:|------:|---------|:-:|:-:|:-:|
| 1 | 810 | **Appointment Booking Flow** - Multi-step orchestration: funding check → availability → slot selection → create appointment | 9 | 9 | 10 |
| 2 | 720 | **Intent Classification** - NLU-driven detection of caller intent (book, cancel, reschedule, enquiry, transfer) | 9 | 8 | 10 |
| 3 | 640 | **Funding Eligibility Checks** - Validates HCP/NDIS/Private funding with Australian healthcare rules | 8 | 8 | 10 |
| 4 | 576 | **Booking Rules Engine** - Enforces service-specific constraints (lead times, practitioner requirements, funding) | 8 | 8 | 9 |
| 5 | 576 | **Smart Error Handling** - Graceful degradation when backends fail, prevents call abandonment | 8 | 8 | 9 |
| 6 | 560 | **Availability Search** - Real-time practitioner calendar queries with slot aggregation | 7 | 8 | 10 |
| 7 | 504 | **Caller ID Lookup** - Silent pre-greeting phone lookup enables personalized experience | 8 | 7 | 9 |
| 8 | 504 | **Email Call Summaries** - Auto-generated end-of-call reports with full conversation context | 8 | 7 | 9 |
| 9 | 504 | **Human Transfer (Sara)** - Seamless escalation with context handoff to human receptionist | 8 | 7 | 9 |
| 10 | 504 | **Patient Context Persistence** - Maintains state across tool calls and conversation branches | 8 | 7 | 9 |
| 11 | 448 | **EP Assessment Flow** - Domain-specific workflow tracking exercise physiology requirements | 8 | 7 | 8 |
| 12 | 448 | **Conversation Summarization** - Auto-generates natural language call summaries | 8 | 7 | 8 |
| 13 | 441 | **Appointment Rescheduling** - Atomic cancel + rebook with availability checking | 7 | 7 | 9 |
| 14 | 441 | **Class Enrollment** - Books patients into group sessions with capacity validation | 7 | 7 | 9 |
| 15 | 392 | **Patient Search by Name** - Fuzzy matching with confidence scoring and multi-result handling | 7 | 7 | 8 |
| 16 | 392 | **Recurring Conflict Detection** - Identifies clashes with existing recurring appointments | 8 | 7 | 7 |
| 17 | 392 | **Multi-Village Support** - Routes to correct clinic location with location-aware logic | 7 | 7 | 8 |
| 18 | 378 | **Timezone Handling** - Sydney/Melbourne timezone conversion with DST awareness | 6 | 7 | 9 |
| 19 | 378 | **Referral Validation** - Checks Medicare referral existence for funded services | 7 | 6 | 9 |
| 20 | 378 | **Medicare Compliance** - Ensures bookings meet Medicare funding requirements | 6 | 7 | 9 |
| 21 | 336 | **Service Type Triage** - Maps caller intent to appropriate service category | 7 | 6 | 8 |
| 22 | 336 | **Duplicate Booking Prevention** - Checks existing appointments before creating new ones | 7 | 6 | 8 |
| 23 | 336 | **Funding Type Detection** - Auto-determines HCP/NDIS/Private from patient records | 7 | 6 | 8 |
| 24 | 336 | **Referral Expiry Tracking** - Monitors HCP validity and remaining sessions | 7 | 6 | 8 |
| 25 | 336 | **Public Holiday Detection** - Australian holiday calendar integration | 7 | 6 | 8 |
| 26 | 294 | **Class Waitlist Management** - Queues patients when classes reach capacity | 7 | 6 | 7 |
| 27 | 288 | **Multi-Village Patient Matching** - Disambiguates same-name patients across locations | 8 | 6 | 6 |
| 28 | 288 | **Class Schedule Lookup** - Retrieves group classes by type, location, and date | 6 | 6 | 8 |
| 29 | 288 | **Class Capacity Checking** - Validates available spots before enrollment | 6 | 6 | 8 |
| 30 | 280 | **Appointment Confirmation Readback** - Natural language confirmation before finalizing | 7 | 5 | 8 |
| 31 | 252 | **Reschedule Availability Check** - Context-aware slot queries for rescheduling | 6 | 6 | 7 |
| 32 | 252 | **MAC Assessment Scripts** - Medical Assessment Certification eligibility handling | 7 | 6 | 6 |
| 33 | 245 | **FAQ Capture & Routing** - Logs unanswered questions for staff follow-up | 7 | 5 | 7 |
| 34 | 240 | **Patient Notes Updates** - Appends call notes to patient records | 6 | 5 | 8 |
| 35 | 210 | **DOB Verification** - Secondary verification when name match is uncertain | 6 | 5 | 7 |
| 36 | 210 | **Practitioner Preference Capture** - Records and respects preferred provider | 6 | 5 | 7 |
| 37 | 210 | **Operating Hours Awareness** - Business hours validation and after-hours messaging | 6 | 5 | 7 |
| 38 | 210 | **Protected Slots Enforcement** - Respects blocked time for meetings/breaks | 6 | 5 | 7 |
| 39 | 210 | **HCP Details Capture** - Records Health Care Provider referral information | 6 | 5 | 7 |
| 40 | 210 | **Callback Scheduling** - Captures callback requests for follow-up queue | 6 | 5 | 7 |
| 41 | 210 | **Follow-up List Management** - Tracks patients needing manual intervention | 6 | 5 | 7 |
| 42 | 200 | **List Upcoming Appointments** - Retrieves and reads scheduled appointments | 5 | 5 | 8 |
| 43 | 200 | **Appointment Cancellation** - Cancels with reason tracking and confirmation | 5 | 5 | 8 |
| 44 | 200 | **SMS Notifications** - Appointment confirmations and reminders via SMS | 5 | 5 | 8 |
| 45 | 175 | **Class Enrollment Confirmation** - Confirms details and sends notification | 5 | 5 | 7 |
| 46 | 175 | **Instructor Email Notifications** - Notifies instructors of new enrollments | 5 | 5 | 7 |
| 47 | 160 | **New Patient Detection** - Identifies first-time callers for registration | 5 | 4 | 8 |
| 48 | 140 | **Directions & Location Info** - Provides addresses and parking info | 5 | 4 | 7 |
| 49 | 120 | **Cancellation Reason Capture** - Records cancellation reasons for analytics | 5 | 4 | 6 |
| 50 | 120 | **After-Hours Messaging** - Custom flows outside business hours | 5 | 4 | 6 |

**Legend:** C = Cleverness, X = Complexity, U = Usefulness

---

## Top 10 Features by Category

### Highest Cleverness (Innovation)
1. Appointment Booking Flow (9)
2. Intent Classification (9)
3. Funding Eligibility Checks (8)
4. Booking Rules Engine (8)
5. Smart Error Handling (8)

### Highest Complexity (Engineering Effort)
1. Appointment Booking Flow (9)
2. Intent Classification (8)
3. Funding Eligibility Checks (8)
4. Booking Rules Engine (8)
5. Smart Error Handling (8)

### Highest Usefulness (Business Value)
1. Appointment Booking Flow (10)
2. Intent Classification (10)
3. Funding Eligibility Checks (10)
4. Availability Search (10)
5. Booking Rules Engine (9)

---

## Infrastructure

| Component | Details |
|-----------|---------|
| **Voice AI** | Conversation flow engine with equation-based routing |
| **Automation** | 53 active workflows for backend operations |
| **Database** | PostgreSQL on AWS EC2 (51 tables, cached lookups) |
| **Practice Management** | Cliniko integration (real-time sync) |
| **Phone Numbers** | +61 2 8880 0226 (Sydney), +61 2 4062 0999 (Secondary) |
| **Email** | Gmail OAuth for call summaries and notifications |
| **SMS** | Mobile message integration for confirmations |

---

## Technology Stack

- **Voice AI Platform** - Conversational AI with natural language understanding
- **Workflow Automation** - Self-hosted automation platform on AWS EC2
- **PostgreSQL** - Database with JSONB caching
- **Cliniko API** - Practice management integration
- **Docker** - Container orchestration
- **Python** - Automation scripts, deployment tools
- **AWS EC2** - Cloud infrastructure

---

*Generated: 2025-12-12*
