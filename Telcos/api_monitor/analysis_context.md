# System Context for API Change Analysis

This document provides context about the current system capabilities to help analyze whether API changes are relevant.

**IMPORTANT: Analyze for BOTH beneficial AND breaking/harmful changes!**

## Overview

We operate an AI voice receptionist system using:
- **RetellAI** - AI voice agent platform (handles calls, agent logic, LLM integration)
- **n8n** - Workflow automation (webhooks, database, Cliniko integration)
- **Cliniko** - Practice management system (patients, appointments, practitioners)
- **Telnyx** - SIP trunking provider (Australian phone numbers)
- **Zadarma** - Secondary phone provider (Australian numbers)
- **PostgreSQL** - Data warehouse for call records, analytics

## Current Cliniko Usage (CRITICAL)

### Integration Points
- **Patient lookup** - Search by phone number, name, DOB
- **Appointment booking** - Create individual appointments
- **Availability checking** - Query practitioner availability slots
- **Practitioner listing** - Get active practitioners for booking
- **Patient creation** - Register new patients during calls

### API Endpoints We Use
- `GET /patients` - Search patients
- `POST /patients` - Create new patients
- `GET /individual_appointments` - List appointments
- `POST /individual_appointments` - Book appointments
- `GET /practitioners` - List practitioners
- `GET /available_times` - Check availability
- `GET /appointment_types` - Get service types

### Current Rate Limit
- 200 requests per minute per user
- We implement request throttling in n8n

### Things We Would Benefit From
- Batch patient lookup
- Webhook notifications for appointment changes
- Better availability query options
- Patient merge/deduplication API
- Appointment rescheduling in single call

### Breaking Changes We MUST Know About
- Rate limit changes (we're near limits during peak)
- Authentication changes
- Response format changes
- Required field additions
- Endpoint deprecations
- Date/time format changes (affects booking logic)

## Current RetellAI Usage

### Agent Capabilities
- Custom LLM-powered voice agents
- Tool/function calling for:
  - Patient lookup
  - Appointment booking
  - Availability checking
  - Practitioner information
  - SMS notifications
- Post-call webhooks for data persistence
- Call transcription and sentiment analysis
- Multi-language support (primarily English AU)

### Current Webhooks (n8n endpoints)
The system uses these n8n webhook endpoints:
- `get-patient-by-phone` - Patient lookup
- `create-patient` - New patient registration
- `get-availability` - Appointment slot availability
- `create-appointment` - Book appointments
- `get-practitioners` - List practitioners
- `send-sms` - SMS notifications
- `tool-add-to-followup` - Flag for human follow-up
- `post-call-summary` - End-of-call data persistence

### Things We Would Benefit From
- Better real-time transcription streaming
- Improved sentiment analysis
- Call recording enhancements
- New webhook event types
- Better error handling in function calls
- Agent analytics/metrics endpoints
- Batch operations for calls/agents

### Breaking Changes We MUST Know About
- Webhook payload format changes
- Tool call response format changes
- Agent configuration changes
- LLM provider changes
- Pricing/billing changes

## Current Telnyx Usage

### SIP Configuration
- FQDN connection to RetellAI (`sip.retellai.com`)
- Codecs: OPUS (primary), G722, G729
- TCP transport
- Australian region (Sydney media servers)

### Current Features Used
- Inbound/outbound voice
- Phone number management
- Call detail records (CDRs)
- SIP credential authentication

### Things We Would Benefit From
- Call recording API improvements
- Real-time call events/webhooks
- Better CDR query capabilities
- Transcription services
- Number porting automation
- Emergency calling compliance features

### Breaking Changes We MUST Know About
- SIP protocol changes
- Codec deprecations
- Authentication changes
- Regional routing changes

## Current Zadarma Usage

### Features Used
- Virtual phone numbers (Sydney, Melbourne, Brisbane)
- SIP routing to LiveKit/RetellAI
- Call statistics and CDRs
- Balance monitoring

### Things We Would Benefit From
- Webhook/callback improvements
- Recording API enhancements
- Real-time call status
- SMS API capabilities
- Better Australian number availability

## n8n Webhook Architecture

All RetellAI tool calls route through n8n webhooks on `auto.yr.com.au`:
- Webhooks receive JSON from RetellAI
- Process via n8n workflow nodes
- Query/update PostgreSQL database
- Integrate with Cliniko (practice management)
- Return structured responses to agent

### Database Tables
- `patients` - Patient records
- `appointments` - Booking data
- `retell_calls` - Call history
- `webhook_cache` - Response caching
- `sync_metadata` - Sync tracking

## Analysis Guidelines

**CRITICAL: Look for BOTH opportunities AND risks!**

### BENEFICIAL Changes (Opportunities)
1. **New Features** - Does this enable something we couldn't do before?
2. **Performance** - Could this reduce latency or improve quality?
3. **Reliability** - Could this improve uptime or error handling?
4. **Cost Savings** - Could this reduce API costs?
5. **New Endpoints** - New capabilities we could leverage

### BREAKING/HARMFUL Changes (Risks)
1. **Deprecations** - Features being removed we currently use
2. **Breaking Changes** - Changes that will break our integration
3. **Rate Limits** - Reduced quotas that could throttle us
4. **Auth Changes** - New authentication requirements
5. **Response Changes** - Modified field names, types, or structure
6. **Required Fields** - New mandatory parameters
7. **Sunset Dates** - End-of-life announcements
8. **Pricing** - Cost increases or billing changes
9. **Security** - New TLS or security requirements

### Priority Levels

- **CRITICAL** - Breaking change or deprecation affecting current functionality - IMMEDIATE ACTION REQUIRED
- **HIGH** - Either a major new feature OR a change with migration deadline
- **MEDIUM** - Useful enhancement OR minor change requiring future attention
- **LOW** - Nice to have, not urgent

### Known Pain Points (prioritize changes affecting these)

1. Cliniko rate limits during peak booking times
2. Occasional webhook timeouts on complex operations
3. Call recording retrieval latency
4. Sentiment analysis accuracy
5. Multi-turn conversation context handling
6. Australian phone number format handling
7. SIP connection reliability during peak hours
8. Patient duplicate detection
