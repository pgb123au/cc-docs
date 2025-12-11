# Reignite AI Voice Receptionist - System Overview

**Version:** v11.204
**Last Updated:** 2025-12-12

---

## System Statistics

### Codebase Size (Production)

| Component | Files | Lines |
|-----------|------:|------:|
| RetellAI Agent (v11.204) | 1 | 7,078 |
| n8n Workflows | 53 | 19,895 |
| n8n Python Scripts | 29 | 6,431 |
| Retell Scripts | 17 | 7,563 |
| Telco Scripts | 1 | 3,475 |
| **Production Total** | **101** | **~44,500** |

### SQL (Database Code)

| Location | Files | Lines | Status |
|----------|------:|------:|--------|
| n8n/SQL/ | 5 | 391 | Production schemas |
| n8n/migrations/ | 2 | 294 | Production migrations |
| n8n/JSON/active_workflows/ | 2 | 298 | Active functions |
| retell/Testing/ | 8 | 1,393 | Dev/testing |
| retell/archive/ | 2 | 246 | Archived |
| **Total** | **19** | **2,622** | |

**Production SQL: ~983 lines** (9 files)

### Database Tables (retellai_prod)

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
| retell_calls | - | Call records (304 calls) |

### Agent Architecture

- **109 conversation nodes** (conversation, function, logic_split, end)
- **24 function nodes** (webhook calls)
- **20 webhook tools** integrated
- **Equation-based routing** for complex decision trees

---

## Features

### Core Features (10)

1. **Caller ID Lookup** - Automatic patient identification from incoming phone number (silent lookup before greeting)

2. **Patient Search & Verification** - Name-based search with confidence scoring + DOB fallback for verification

3. **Appointment Booking** - Multi-step flow: check funding eligibility → get availability → select practitioner/slot → create appointment

4. **Appointment Management** - List upcoming appointments, reschedule, cancel with reason tracking

5. **Funding & Eligibility Checks** - Validates HCP/NDIS/Private funding, referral requirements, service eligibility

6. **Exercise Classes** - Class schedule lookup, enrollment, waitlist management for group sessions

7. **Multi-Village Support** - Routes to correct clinic location (Yarra Junction, Warburton, etc.)

8. **EP Assessment Flow** - Tracks exercise physiology assessment requirements and completion status

9. **Smart Error Handling** - Detects holiday closures, protected slots, recurring conflicts, missing practitioner IDs

10. **n8n + Cliniko Integration** - 20 webhook tools connecting to practice management system for real-time data operations

### Additional Features (20)

11. **SMS Notifications** - Sends appointment confirmations and reminders via SMS to patient mobile

12. **Email Call Summaries** - Automated end-of-call reports emailed to clinic staff with full conversation details

13. **Human Transfer (Sara)** - Seamless escalation to human receptionist with context handoff

14. **New Patient Registration** - Creates new patients in Cliniko with phone, name, and booking details

15. **FAQ Capture & Routing** - Logs unanswered questions for staff follow-up, prevents repeat issues

16. **MAC Assessment Scripts** - Medical Assessment Certification eligibility scripts and outcome handling

17. **Callback Scheduling** - Captures callback requests and routes to follow-up queue

18. **Follow-up List Management** - Tracks patients needing callbacks, EP assessments, or manual intervention

19. **Waitlist Management** - Adds patients to class or practitioner waitlists when no availability

20. **Patient Notes Updates** - Appends call notes and booking details to Cliniko patient records

21. **HCP Details Capture** - Records Health Care Provider referral information for Medicare claims

22. **Operating Hours Awareness** - Validates business hours, adjusts messaging for after-hours calls

23. **Directions & Location Info** - Provides clinic addresses, parking info, and class-specific locations

24. **Instructor Email Notifications** - Notifies class instructors when new enrollments occur

25. **Call Event Logging** - Tracks call start/end times, durations, outcomes for analytics

26. **Practitioner Preference Capture** - Records and respects patient's preferred provider for bookings

27. **Public Holiday Detection** - Checks Australian public holidays, prevents bookings on closed days

28. **Recurring Conflict Detection** - Identifies when new bookings would conflict with existing recurring appointments

29. **Protected Slots Enforcement** - Respects blocked/reserved time slots for staff meetings, breaks

30. **Booking Rules Engine** - Enforces service-specific constraints (lead times, practitioner requirements, funding rules)

---

## Infrastructure

| Component | Details |
|-----------|---------|
| **Voice AI** | RetellAI conversation flow engine with equation-based routing |
| **Automation** | n8n workflow platform (53 active workflows) |
| **Database** | PostgreSQL on AWS EC2 (51 tables, cached lookups) |
| **Practice Management** | Cliniko integration (real-time sync) |
| **Phone Numbers** | +61 2 8880 0226 (Sydney), +61 2 4062 0999 (Secondary) |
| **Email** | Gmail OAuth for call summaries and notifications |
| **SMS** | Mobile message integration for confirmations |

---

## Technology Stack

- **RetellAI** - Conversational AI platform
- **n8n** - Workflow automation (self-hosted on AWS EC2)
- **PostgreSQL** - Database with JSONB caching
- **Cliniko API** - Practice management integration
- **Docker** - Container orchestration
- **Python** - Automation scripts, deployment tools
- **AWS EC2** - Cloud infrastructure

---

*Generated: 2025-12-12*
