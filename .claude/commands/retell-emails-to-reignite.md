# Switch Reignite Emails - Sara Holiday Routing

Switch all Reignite-related email workflows to route emails to Aspire Admin Services (Sara's holiday cover).

**Uses n8n API** - no restart required, changes take effect immediately.

## Current Configuration (Sara on Holiday)

| Field | Value |
|-------|-------|
| **TO** | `clients@aspireadminservices.com.au` |
| **CC** | `Hello@reignitehealth.com.au` |
| **BCC** | `support@yesai.au` |

## Execute this command

Run this Python script to apply the Sara holiday email routing:

```bash
python -c "
import requests
import json

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4'
BASE_URL = 'https://auto.yr.com.au/api/v1'
HEADERS = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# Sara Holiday routing
NEW_TO = 'clients@aspireadminservices.com.au'
NEW_CC = 'Hello@reignitehealth.com.au'
NEW_BCC = 'support@yesai.au'

# Workflows to update
WORKFLOWS = [
    ('cCJFdILbfg4VIldj', 'Email End of Call Summary'),
    ('3apIk1qWQhm75TOs', 'Email Sara Transfer v2.0'),
    ('qbIUIvXJkI30vRrv', 'Email Sara Transfer'),
    ('8kCWwyCKR5FQuSt9', 'Sara Approval Queue v2.0'),
]

print('Switching emails for Sara holiday routing...')
print('TO:', NEW_TO)
print('CC:', NEW_CC)
print('BCC:', NEW_BCC)
print('=' * 60)

for wf_id, wf_name in WORKFLOWS:
    try:
        r = requests.get(f'{BASE_URL}/workflows/{wf_id}', headers=HEADERS)
        if r.status_code != 200:
            print(f'SKIP {wf_name}: Could not fetch (status {r.status_code})')
            continue

        wf = r.json()
        modified = False

        for node in wf.get('nodes', []):
            if node.get('type') == 'n8n-nodes-base.gmail':
                params = node.get('parameters', {})
                old_to = params.get('sendTo', '(none)')

                # Set TO address
                params['sendTo'] = NEW_TO

                # Remove broken top-level CC/BCC params (these don't work!)
                params.pop('ccEmail', None)
                params.pop('bccEmail', None)

                # Set CC and BCC inside options (correct location for Gmail node v2.x)
                if 'options' not in params:
                    params['options'] = {}
                params['options']['ccList'] = NEW_CC
                params['options']['bccList'] = NEW_BCC

                node['parameters'] = params
                modified = True
                print(f'  {wf_name}')
                print(f'    Node: {node.get(\"name\", \"Gmail\")}')
                print(f'    TO: {old_to} -> {NEW_TO}')

        if not modified:
            print(f'SKIP {wf_name}: No Gmail node found')
            continue

        update_data = {
            'name': wf['name'],
            'nodes': wf['nodes'],
            'connections': wf['connections'],
            'settings': wf.get('settings', {})
        }

        r = requests.put(f'{BASE_URL}/workflows/{wf_id}', headers=HEADERS, json=update_data)
        if r.status_code == 200:
            print(f'    -> OK')
        else:
            print(f'    -> FAIL: {r.status_code} - {r.text[:200]}')
        print()

    except Exception as e:
        print(f'ERR  {wf_name}: {str(e)}')

print('=' * 60)
print('Done! Emails now route to Aspire Admin with Reignite CC and Yes AI BCC.')
"
```

## Expected Result

| Workflow | TO | CC | BCC |
|----------|----|----|-----|
| Email End of Call Summary | clients@aspireadminservices.com.au | Hello@reignitehealth.com.au | support@yesai.au |
| Email Sara Transfer (both) | clients@aspireadminservices.com.au | Hello@reignitehealth.com.au | support@yesai.au |
| Sara Approval Queue | clients@aspireadminservices.com.au | Hello@reignitehealth.com.au | support@yesai.au |

## Technical Note

**IMPORTANT:** n8n Gmail node v2.x requires CC/BCC to be set inside `options`:
```python
params['options']['ccList'] = 'email@example.com'   # CORRECT
params['options']['bccList'] = 'email@example.com'  # CORRECT
params['ccEmail'] = 'email@example.com'             # WRONG - ignored!
```

## To Restore Original Routing (When Sara Returns)

Use `/retell-emails-to-peter` to route all emails to peter@yesai.au, or modify this script:
```python
NEW_TO = 'hello@reignitehealth.com.au'
NEW_CC = ''
NEW_BCC = 'peter@yesai.au'
```

---
**Last Updated:** 2025-12-12
**Status:** Updated with correct options.ccList/bccList format
