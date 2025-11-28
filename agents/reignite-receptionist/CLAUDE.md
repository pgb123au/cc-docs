# Reignite AI Mega Receptionist

## Project Overview
AI voice agent system for patient booking and class enrollment using RetellAI technology.
Currently on version 3.50 with ongoing optimization.

## Critical Guidelines
- **DO NOT MODIFY WEBHOOK CODE** - Backend systems are thoroughly tested and stable
- Focus on agent configuration and prompting optimization
- Maintain node budget constraints during development

## Current Version
v3.50 - Enhanced prompting, token reduction, improved tool persistence

## Key Directories
- webhooks/ - Backend integration (STABLE - do not modify)
- configs/ - RetellAI agent configuration files
- tests/ - Test cases for booking flows, cancellations, class enrollment
- archive/ - Previous versions for reference

## Testing Requirements
All changes must be tested against:
1. New patient booking flow
2. Existing patient cancellation
3. Class enrollment

## Optimization Focus
- Dramatic token reduction
- Prevent premature responses
- Fix incomplete booking flows
- Eliminate infinite loops
- Improve tool persistence
