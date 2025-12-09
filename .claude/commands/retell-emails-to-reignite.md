# Switch Reignite Emails to LIVE (hello@reignitehealth.com.au)

Switch all Reignite-related email workflows to route emails to hello@reignitehealth.com.au with BCC to peter@yesai.au.

## Execute this command

Run this Python script via SSH to switch emails to Reignite:

```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 "docker exec -i n8n-postgres-1 psql -U n8n -d n8n" << 'SQLEOF'
-- Switch all Reignite emails to LIVE (hello@)
-- Workflows: End of Call, Sara Transfer, Sara Approval, Weekly Report
-- Handles both JSON patterns: with space ("sendTo": ) and without ("sendTo":)

UPDATE workflow_entity
SET nodes = REPLACE(
    REPLACE(nodes::text,
        '"sendTo": "peter@yesai.au"',
        '"sendTo": "hello@reignitehealth.com.au", "bccEmail": "peter@yesai.au"'
    ),
    '"sendTo":"peter@yesai.au"',
    '"sendTo":"hello@reignitehealth.com.au","bccEmail":"peter@yesai.au"'
)::json,
"updatedAt" = NOW()
WHERE name IN (
    'RetellAI - Email End of Call Summary + Sheets v8.1 UNIFIED',
    'RetellAI - Email Sara Transfer',
    'RetellAI - Email Sara Transfer v2.0 UNIFIED',
    'Reignite - Add to Sara Approval Queue v2.0 UNIFIED',
    'Weekly Group Class Performance Report'
)
AND (nodes::text LIKE '%"sendTo": "peter@yesai.au"%' OR nodes::text LIKE '%"sendTo":"peter@yesai.au"%')
RETURNING name, 'switched to hello@' as status;

-- Instructor emails: Add CC=hello@ and BCC=peter@ to existing instructor_email pattern
-- These workflows keep TO=instructor_email, just need CC/BCC added
UPDATE workflow_entity
SET nodes = REPLACE(nodes::text,
    '"sendTo": "={{ $json.instructor_email }}"',
    '"sendTo": "={{ $json.instructor_email }}", "ccEmail": "hello@reignitehealth.com.au", "bccEmail": "peter@yesai.au"'
)::json,
"updatedAt" = NOW()
WHERE name IN (
    'RetellAI - Email Instructor (Production Final) v2.0 UNIFIED',
    'RetellAI - Email Instructor v2.0 UNIFIED'
)
AND nodes::text LIKE '%"sendTo": "={{ $json.instructor_email }}"%'
AND nodes::text NOT LIKE '%"ccEmail":%'
RETURNING name, 'added CC+BCC' as status;
SQLEOF
```

After running, verify the changes and report the results to the user.

## Expected Result

| Workflow | TO | CC | BCC |
|----------|----|----|-----|
| Email End of Call Summary | hello@reignitehealth.com.au | - | peter@yesai.au |
| Email Sara Transfer (both) | hello@reignitehealth.com.au | - | peter@yesai.au |
| Sara Approval Queue | hello@reignitehealth.com.au | - | peter@yesai.au |
| Weekly Group Class Report | hello@reignitehealth.com.au | - | peter@yesai.au |
| Email Instructor (both) | instructor_email | hello@reignitehealth.com.au | peter@yesai.au |
