# System Context for API Change Analysis

This document provides context about the current system capabilities to help analyze whether API changes are relevant.

## Overview

We operate an AI voice receptionist system using:
- **RetellAI** - AI voice agent platform (handles calls, agent logic, LLM integration)
- **n8n** - Workflow automation (webhooks, database, Cliniko integration)
- **Telnyx** - SIP trunking provider (Australian phone numbers)
- **Zadarma** - Secondary phone provider (Australian numbers)
- **PostgreSQL** - Data warehouse for call records, analytics

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

When analyzing API changes, consider:

1. **Direct Impact** - Does this change something we currently use?
2. **New Capability** - Does this enable something we couldn't do before?
3. **Reliability** - Could this improve system reliability or error handling?
4. **Performance** - Could this reduce latency or improve call quality?
5. **Cost** - Could this reduce API costs or improve efficiency?
6. **Compliance** - Does this affect Australian telecom compliance?

### Priority Levels

- **CRITICAL** - Breaking change or deprecation affecting current functionality
- **HIGH** - New feature that solves a known pain point
- **MEDIUM** - Useful enhancement worth investigating
- **LOW** - Nice to have, not urgent

### Known Pain Points (prioritize fixes for these)

1. Occasional webhook timeouts on complex operations
2. Call recording retrieval latency
3. Sentiment analysis accuracy
4. Multi-turn conversation context handling
5. Australian phone number format handling
6. SIP connection reliability during peak hours
