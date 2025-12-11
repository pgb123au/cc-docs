# Switch Reignite Emails to Peter Only

Switch all Reignite-related email workflows to route emails directly to peter@yesai.au only (for testing or when you need all emails to yourself).

**Uses n8n API** - no restart required, changes take effect immediately.

## Target Configuration

| Field | Value |
|-------|-------|
| **TO** | `peter@yesai.au` |
| **CC** | *(none)* |
| **BCC** | *(none)* |

## Execute this command

Run this Python script to switch all emails to Peter:

```bash
python -c "
import requests
import json

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4'
BASE_URL = 'https://auto.yr.com.au/api/v1'
HEADERS = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# Peter only routing
NEW_TO = 'peter@yesai.au'

# Workflows to update
WORKFLOWS = [
    ('cCJFdILbfg4VIldj', 'Email End of Call Summary'),
    ('3apIk1qWQhm75TOs', 'Email Sara Transfer v2.0'),
    ('qbIUIvXJkI30vRrv', 'Email Sara Transfer'),
    ('8kCWwyCKR5FQuSt9', 'Sara Approval Queue v2.0'),
]

print('Switching emails to Peter only...')
print('TO:', NEW_TO)
print('CC: (none)')
print('BCC: (none)')
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

                params['sendTo'] = NEW_TO
                params.pop('ccEmail', None)   # Remove CC
                params.pop('bccEmail', None)  # Remove BCC

                node['parameters'] = params
                modified = True
                print(f'  Node: {node.get(\"name\", \"Gmail\")} - TO changed from {old_to}')

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
            print(f'OK   {wf_name}')
        else:
            print(f'FAIL {wf_name}: {r.status_code} - {r.text[:200]}')

    except Exception as e:
        print(f'ERR  {wf_name}: {str(e)}')

print('=' * 60)
print('Done! All emails now route to peter@yesai.au only.')
"
```

## Expected Result

| Workflow | TO | CC | BCC |
|----------|----|----|-----|
| Email End of Call Summary | peter@yesai.au | - | - |
| Email Sara Transfer (both) | peter@yesai.au | - | - |
| Sara Approval Queue | peter@yesai.au | - | - |

---
**Last Updated:** 2025-12-11
