---
description: Verify n8n webhooks and database changes after deploying a RetellAI agent
---

# Verify n8n & Database Changes for Deployed Agent

After deploying a RetellAI agent, verify all n8n webhooks and database components are working correctly.

## Step 1: Identify Agent's Tool IDs

Read the most recently deployed agent JSON from `retell/Testing/` and extract ALL `tool_id` values.

Create a list of all webhooks the agent uses.

## Step 2: Verify All Webhooks Are Active

For each tool_id, verify the corresponding n8n workflow is active:

```bash
# Get all active workflows and check for retell webhooks
curl -s "https://auto.yr.com.au/api/v1/workflows?limit=200" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4" \
  | python -c "import sys,json; wfs=json.load(sys.stdin)['data']; [print(f'{w[\"name\"]} - {\"ACTIVE\" if w[\"active\"] else \"INACTIVE\"}') for w in wfs if 'retell' in w['name'].lower() or 'reignite' in w['name'].lower()]"
```

## Step 3: Test Critical Webhooks

Test each webhook category using Peter Ball test data (patient_id: 1805465202989210063, phone: 0412111000).

### Caller Identification

```bash
# lookup-caller-phone
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/lookup-caller-phone" \
  -H "Content-Type: application/json" \
  -d '{"args": {"phone": "0412111000", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'lookup-caller-phone: {\"PASS\" if r.get(\"found\") else \"FAIL\"} - patient_id={r.get(\"patient_id\")}')"

# lookup-caller-name-village
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/lookup-caller-name-village" \
  -H "Content-Type: application/json" \
  -d '{"args": {"first_name": "Peter", "last_name": "Ball", "village": "The Baytree", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'lookup-caller-name-village: {\"PASS\" if r.get(\"found\") else \"FAIL\"}')"
```

### Funding & Eligibility

```bash
# check-funding
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/check-funding" \
  -H "Content-Type: application/json" \
  -d '{"args": {"patient_id": "1805465202989210063", "funding_type": "PRIVATE", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'check-funding: {\"PASS\" if r.get(\"success\") else \"FAIL\"} - eligible={r.get(\"eligible\")}')"

# check-ep-assessment
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/check-ep-assessment" \
  -H "Content-Type: application/json" \
  -d '{"args": {"patient_id": "1805465202989210063", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'check-ep-assessment: {\"PASS\" if \"assessment_required\" in r else \"FAIL\"}')"
```

### Availability & Scheduling

```bash
# get-availability
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/get-availability" \
  -H "Content-Type: application/json" \
  -d '{"args": {"village": "The Baytree", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'get-availability: {\"PASS\" if r.get(\"success\") else \"FAIL\"} - slots={len(r.get(\"available_practitioners\",[]))}')"

# list-appointments
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/list-appointments" \
  -H "Content-Type: application/json" \
  -d '{"args": {"patient_id": "1805465202989210063", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'list-appointments: {\"PASS\" if r.get(\"success\") else \"FAIL\"} - count={r.get(\"count\",0)}')"
```

### Class Management

```bash
# get-class-schedule
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/get-class-schedule" \
  -H "Content-Type: application/json" \
  -d '{"args": {"village": "The Baytree", "class_type": "Pilates", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'get-class-schedule: {\"PASS\" if r.get(\"success\") else \"FAIL\"} - class_id={r.get(\"next_class_id\")}')"

# check-class-capacity
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/check-class-capacity" \
  -H "Content-Type: application/json" \
  -d '{"args": {"class_name": "Pilates", "village": "The Baytree", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'check-class-capacity: {\"PASS\" if r.get(\"success\") else \"FAIL\"} - spots={r.get(\"available_spots\")}')"
```

### Directions & Info

```bash
# get-directions
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/get-directions" \
  -H "Content-Type: application/json" \
  -d '{"args": {"village": "The Baytree", "class_type": "Pilates", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'get-directions: {\"PASS\" if r.get(\"success\") else \"FAIL\"}')"

# get-operating-hours
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/get-operating-hours" \
  -H "Content-Type: application/json" \
  -d '{"args": {"village": "The Baytree", "call_id": "verify-test"}}' | python -c "import sys,json; r=json.load(sys.stdin); print(f'get-operating-hours: {\"PASS\" if r.get(\"hours\") else \"FAIL\"}')"
```

## Step 4: Verify Database Tables

Check critical database tables have expected structure and data:

```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 << 'ENDSSH'
docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod << 'ENDSQL'

-- Table existence and row counts
SELECT 'patients' as table_name, COUNT(*) as row_count FROM patients
UNION ALL
SELECT 'webhook_cache', COUNT(*) FROM webhook_cache
UNION ALL
SELECT 'retell_calls', COUNT(*) FROM retell_calls
UNION ALL
SELECT 'safety_holidays', COUNT(*) FROM safety_holidays
UNION ALL
SELECT 'safety_protected_slots', COUNT(*) FROM safety_protected_slots
ORDER BY table_name;

-- Verify Peter Ball test patient exists
SELECT 'Test Patient Check' as check_name,
  CASE WHEN COUNT(*) > 0 THEN 'PASS' ELSE 'FAIL' END as status
FROM patients WHERE cliniko_id = '1805465202989210063';

-- Check recent sync metadata
SELECT sync_type, last_sync_at, records_updated
FROM sync_metadata
ORDER BY last_sync_at DESC LIMIT 5;

-- Check cache health (entries in last 24h)
SELECT 'Cache entries (24h)' as metric, COUNT(*) as value
FROM webhook_cache
WHERE created_at > NOW() - INTERVAL '24 hours';

-- Check for upcoming holidays
SELECT 'Upcoming holidays' as metric, COUNT(*) as value
FROM safety_holidays
WHERE holiday_date >= CURRENT_DATE;

-- Check protected slots
SELECT 'Active protected slots' as metric, COUNT(*) as value
FROM safety_protected_slots
WHERE end_date IS NULL OR end_date >= CURRENT_DATE;

ENDSQL
ENDSSH
```

## Step 5: Verify Safety Checks (v1.3+)

If the agent uses book-appointment-compound v1.3+, verify safety tables:

```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 << 'ENDSSH'
docker exec -i n8n-postgres-1 psql -U n8n -d retellai_prod << 'ENDSQL'

-- View configured holidays
SELECT holiday_date, description, created_at
FROM safety_holidays
WHERE holiday_date >= CURRENT_DATE
ORDER BY holiday_date LIMIT 10;

-- View protected time slots
SELECT village, day_of_week, start_time, end_time, reason, start_date, end_date
FROM safety_protected_slots
WHERE end_date IS NULL OR end_date >= CURRENT_DATE
ORDER BY village, day_of_week;

ENDSQL
ENDSSH
```

## Step 6: Test Booking Safety (Read-Only)

Test the pre-booking validation without actually creating an appointment:

```bash
# This will trigger pre-checks but use a far-future date to avoid actual booking
curl -s -X POST "https://auto.yr.com.au/webhook/reignite-retell/book-appointment-compound" \
  -H "Content-Type: application/json" \
  -d '{
    "args": {
      "patient_id": "1805465202989210063",
      "starts_at": "2099-01-01T10:00:00.000Z",
      "village": "The Baytree",
      "funding_type": "PRIVATE",
      "appointment_type": "Standard",
      "duration_minutes": 30,
      "practitioner_id": "test-practitioner",
      "call_id": "verify-test"
    }
  }' | python -c "import sys,json; r=json.load(sys.stdin); print(f'book-appointment-compound: Endpoint responds - error_code={r.get(\"error_code\",\"none\")}')"
```

## Step 7: Check Recent n8n Executions

Verify no errors in recent workflow executions:

```bash
curl -s "https://auto.yr.com.au/api/v1/executions?limit=20&status=error" \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4" \
  | python -c "import sys,json; r=json.load(sys.stdin); errors=r.get('data',[]); print(f'Recent errors: {len(errors)}'); [print(f'  - {e[\"workflowData\"][\"name\"]}: {e[\"stoppedAt\"]}') for e in errors[:5]]"
```

## Step 8: Fix Any Issues

If any test fails:

1. **Workflow not active:** Activate via n8n API or UI
2. **Webhook returns error:** Check n8n workflow nodes for misconfiguration
3. **Database table missing:** Run migration scripts from `n8n/Python/migrations/`
4. **Test patient not found:** Run patient sync workflow

**For cache-related issues**, read:
- `n8n/Webhooks Docs/N8N_CACHE_ISSUES_COMPLETE_FIX_GUIDE.md`

**Loop until all tests pass!**

## Final Report

After all steps complete, output:

```
=== N8N & DATABASE VERIFICATION COMPLETE ===

Agent Verified: vX.XX
Tool IDs Found: [count]

Webhook Tests:
  lookup-caller-phone:      [PASS/FAIL]
  lookup-caller-name-village: [PASS/FAIL]
  check-funding:            [PASS/FAIL]
  check-ep-assessment:      [PASS/FAIL]
  get-availability:         [PASS/FAIL]
  list-appointments:        [PASS/FAIL]
  get-class-schedule:       [PASS/FAIL]
  check-class-capacity:     [PASS/FAIL]
  get-directions:           [PASS/FAIL]
  get-operating-hours:      [PASS/FAIL]
  book-appointment-compound: [PASS/FAIL]

Database Health:
  patients:              [count] rows
  webhook_cache:         [count] rows
  retell_calls:          [count] rows
  safety_holidays:       [count] rows
  safety_protected_slots: [count] rows
  Test patient (Peter Ball): [FOUND/MISSING]

n8n Workflow Status:
  Active retell workflows: [count]
  Recent errors (24h):     [count]

Status: [ALL PASS / ISSUES FOUND]

DONE DONE DONE
```

## Critical Rules

- Use ONLY Peter Ball test data (patient_id: 1805465202989210063, phone: 0412111000)
- Do NOT create real appointments during testing
- Fix ALL errors before declaring done
- This command verifies existing infrastructure - it does NOT deploy new workflows
