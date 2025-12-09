# Switch Reignite Emails to TESTING (peter@yesai.au)

Switch all Reignite-related email workflows to route emails directly to peter@yesai.au only (for testing without bothering the client).

## Execute this command

Run this Python script via SSH to switch emails to Peter only:

```bash
ssh -i "C:\Users\peter\.ssh\metabase-aws" ubuntu@52.13.124.171 "docker exec -i n8n-postgres-1 psql -U n8n -d n8n" << 'SQLEOF'
-- Switch all Reignite emails to TESTING (peter@ only)
-- Remove CC and BCC, send directly to peter@yesai.au

-- Regular workflows: just change TO to peter@
UPDATE workflow_entity
SET nodes = REPLACE(
    REPLACE(
        REPLACE(
            REPLACE(nodes::text,
                '"sendTo": "hello@reignitehealth.com.au", "bccEmail": "peter@yesai.au"',
                '"sendTo": "peter@yesai.au"'
            ),
            '"sendTo":"hello@reignitehealth.com.au","bccEmail":"peter@yesai.au"',
            '"sendTo":"peter@yesai.au"'
        ),
        '"sendTo": "hello@reignitehealth.com.au"',
        '"sendTo": "peter@yesai.au"'
    ),
    ', "bccEmail": "peter@yesai.au"', ''
)::json,
"updatedAt" = NOW()
WHERE name IN (
    'RetellAI - Email End of Call Summary + Sheets v8.1 UNIFIED',
    'RetellAI - Email Sara Transfer',
    'RetellAI - Email Sara Transfer v2.0 UNIFIED',
    'Reignite - Add to Sara Approval Queue v2.0 UNIFIED',
    'Weekly Group Class Performance Report'
)
AND nodes::text LIKE '%hello@reignitehealth.com.au%'
RETURNING name, 'switched to peter@' as status;

-- Instructor emails: change TO to peter@, remove CC and BCC
UPDATE workflow_entity
SET nodes = REPLACE(
    REPLACE(
        REPLACE(
            REPLACE(nodes::text,
                '"sendTo": "={{ $json.instructor_email }}", "ccEmail": "hello@reignitehealth.com.au", "bccEmail": "peter@yesai.au"',
                '"sendTo": "peter@yesai.au"'
            ),
            '"sendTo":"={{ $json.instructor_email }}","ccEmail":"hello@reignitehealth.com.au","bccEmail":"peter@yesai.au"',
            '"sendTo":"peter@yesai.au"'
        ),
        '"ccEmail": "hello@reignitehealth.com.au", ', ''
    ),
    ', "bccEmail": "peter@yesai.au"', ''
)::json,
"updatedAt" = NOW()
WHERE name IN (
    'RetellAI - Email Instructor (Production Final) v2.0 UNIFIED',
    'RetellAI - Email Instructor v2.0 UNIFIED'
)
AND (nodes::text LIKE '%instructor_email%' OR nodes::text LIKE '%hello@reignitehealth.com.au%')
RETURNING name, 'switched to peter@' as status;
SQLEOF
```

After running, verify the changes and report the results to the user.

## Expected Result

| Workflow | TO | CC | BCC |
|----------|----|----|-----|
| Email End of Call Summary | peter@yesai.au | - | - |
| Email Sara Transfer (both) | peter@yesai.au | - | - |
| Sara Approval Queue | peter@yesai.au | - | - |
| Weekly Group Class Report | peter@yesai.au | - | - |
| Email Instructor (both) | peter@yesai.au | - | - |
