# Debug Class Booking Issues

Create a comprehensive debug package for diagnosing class booking problems in the RetellAI agent system.

## Task

1. **Download Latest Call Log (1 call only)**
   - Download the single most recent call from RetellAI API
   - Include: `_full.json`, `_transcript_with_tools.json`, `_public_log.json`

2. **Download Current Live Agent**
   - Get the active agent configuration from RetellAI
   - Save with original name + timestamp: `Reignite_AI_Mega_Receptionist_vX.XX_CC_YYYYMMDD_HHMMSS.json`
   - Include the conversation flow JSON

3. **Collect Class Booking n8n Workflows**
   - Lookup Caller by Phone (current active version)
   - Lookup Caller by Name/Village (current active version)
   - Get Class Schedule workflow
   - Enroll Class workflow

4. **Collect Documentation (max 10 files total including above)**
   Priority order:
   - `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` (required)
   - `retell/guides/BOOKING_FLOW_TROUBLESHOOTING.md`
   - `retell/RETELLAI_REFERENCE.md`

5. **Write Diagnostic Report**
   Create `CLASS_BOOKING_DIAGNOSTIC_REPORT.md` analyzing:
   - What the call log shows happened
   - Expected vs actual behavior
   - Root cause analysis with specific evidence (line numbers, JSON snippets)
   - Recommended fixes with code examples
   - Steps to verify the fix

## Output

Save to: `retell/Testing/[YYYY-MM-DD]-class-booking-debug/`

```
[date]-class-booking-debug/
  call_[id]_full.json
  call_[id]_transcript_with_tools.json
  call_[id]_public_log.json
  Reignite_AI_Mega_Receptionist_vX.XX_CC_YYYYMMDD_HHMMSS.json
  conversation_flow_LIVE.json
  [workflow files].json
  docs/
    RETELLAI_WEBHOOKS_CURRENT.md
    BOOKING_FLOW_TROUBLESHOOTING.md
    RETELLAI_REFERENCE.md
  CLASS_BOOKING_DIAGNOSTIC_REPORT.md
```

## Constraints

- **Max 10 files** in docs/ folder
- Only 1 call log (most recent)
- Only ACTIVE workflows
- Agent filename must include original version + timestamp
- Focus on `collected_dynamic_variables` and variable mapping issues
