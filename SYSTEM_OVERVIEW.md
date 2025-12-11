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

## Features (50)

### Patient Identification & Verification (5)

1. **Caller ID Lookup** - Automatic patient identification from incoming phone number (silent lookup before greeting)

2. **Patient Search by Name** - Name-based search with fuzzy matching and confidence scoring

3. **DOB Verification** - Secondary verification using date of birth when name match is uncertain

4. **Multi-Village Patient Matching** - Disambiguates patients with same name across different clinic locations

5. **New Patient Detection** - Identifies first-time callers and routes to registration flow

### Appointment Booking (8)

6. **Appointment Booking Flow** - Multi-step flow: check funding eligibility → get availability → select practitioner/slot → create appointment

7. **Practitioner Preference Capture** - Records and respects patient's preferred provider for bookings

8. **Service Type Triage** - Determines appropriate service category (EP, physio, group class, etc.)

9. **Availability Search** - Queries real-time practitioner calendars for open slots

10. **Appointment Confirmation Readback** - Reads back booking details for verbal confirmation before finalizing

11. **Duplicate Booking Prevention** - Checks for existing appointments before creating new ones

12. **Booking Rules Engine** - Enforces service-specific constraints (lead times, practitioner requirements, funding rules)

13. **Timezone Handling** - Converts all times to Sydney/Melbourne timezone for consistency

### Appointment Management (6)

14. **List Upcoming Appointments** - Retrieves and reads patient's scheduled appointments

15. **Appointment Rescheduling** - Finds alternative slots and moves existing bookings

16. **Reschedule Availability Check** - Queries available slots specifically for rescheduling context

17. **Appointment Cancellation** - Cancels bookings with reason tracking and confirmation

18. **Cancellation Reason Capture** - Records why appointments are cancelled for analytics

19. **Recurring Conflict Detection** - Identifies when new bookings would conflict with existing recurring appointments

### Funding & Eligibility (6)

20. **Funding Eligibility Checks** - Validates HCP/NDIS/Private funding status before booking

21. **Funding Type Detection** - Automatically determines HCP/NDIS/Private from patient records

22. **Referral Validation** - Checks if valid referral exists for Medicare-funded services

23. **Referral Expiry Tracking** - Monitors HCP referral validity and remaining sessions

24. **EP Assessment Flow** - Tracks exercise physiology assessment requirements and completion status

25. **Medicare Compliance** - Ensures bookings comply with Medicare funding requirements

### Exercise Classes (6)

26. **Class Schedule Lookup** - Retrieves available group exercise classes by type and location

27. **Class Enrollment** - Books patients into group sessions with capacity checking

28. **Class Capacity Checking** - Validates spots available before enrolling in group sessions

29. **Class Waitlist Management** - Adds patients to waitlist when classes are full

30. **Class Enrollment Confirmation** - Confirms class details and sends enrollment notification

31. **Instructor Email Notifications** - Notifies class instructors when new enrollments occur

### Location & Scheduling (5)

32. **Multi-Village Support** - Routes to correct clinic location (Yarra Junction, Warburton, etc.)

33. **Directions & Location Info** - Provides clinic addresses, parking info, and class-specific locations

34. **Operating Hours Awareness** - Validates business hours, adjusts messaging for after-hours calls

35. **Public Holiday Detection** - Checks Australian public holidays, prevents bookings on closed days

36. **Protected Slots Enforcement** - Respects blocked/reserved time slots for staff meetings, breaks

### Patient Communication (6)

37. **SMS Notifications** - Sends appointment confirmations and reminders via SMS

38. **Email Call Summaries** - Automated end-of-call reports emailed to clinic staff

39. **Conversation Summarization** - Auto-generates call summary for email reports

40. **Patient Notes Updates** - Appends call notes and booking details to patient records

41. **HCP Details Capture** - Records Health Care Provider referral information for Medicare claims

42. **MAC Assessment Scripts** - Medical Assessment Certification eligibility scripts and outcome handling

### Call Handling & Transfers (5)

43. **Human Transfer (Sara)** - Seamless escalation to human receptionist with context handoff

44. **FAQ Capture & Routing** - Logs unanswered questions for staff follow-up

45. **Callback Scheduling** - Captures callback requests and routes to follow-up queue

46. **Follow-up List Management** - Tracks patients needing callbacks or manual intervention

47. **After-Hours Messaging** - Custom flows for calls outside business hours

### System Intelligence (3)

48. **Intent Classification** - Detects caller intent (book, cancel, reschedule, enquiry, transfer)

49. **Smart Error Handling** - Graceful recovery when backend services fail or return unexpected data

50. **Patient Context Persistence** - Maintains conversation state across tool calls and transfers

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
