# Switch Reignite Emails to TESTING (peter@yesai.au)

Switch all Reignite-related email workflows to route emails directly to peter@yesai.au only (for testing without bothering the client).

**Uses n8n API** - no restart required, changes take effect immediately.

## Execute this command

Run this Python script to switch emails to Peter only:

```bash
python -c "
import requests
import json

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4'
BASE_URL = 'https://auto.yr.com.au/api/v1'
HEADERS = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# Workflows to update (ID, name, is_instructor)
WORKFLOWS = [
    ('cCJFdILbfg4VIldj', 'Email End of Call Summary v8.1', False),
    ('3apIk1qWQhm75TOs', 'Email Sara Transfer v2.0', False),
    ('qbIUIvXJkI30vRrv', 'Email Sara Transfer', False),
    ('8kCWwyCKR5FQuSt9', 'Sara Approval Queue v2.0', False),
    ('eK9YGjAyJ5AD3bv1', 'Weekly Group Class Report', False),
    ('8tr0AQztNv7yWx7U', 'Email Instructor v2.0', True),
]

print('Switching Reignite emails to TESTING mode (peter@yesai.au only)...')
print('=' * 60)

for wf_id, wf_name, is_instructor in WORKFLOWS:
    try:
        # GET workflow
        r = requests.get(f'{BASE_URL}/workflows/{wf_id}', headers=HEADERS)
        if r.status_code != 200:
            print(f'SKIP {wf_name}: Could not fetch (status {r.status_code})')
            continue

        wf = r.json()
        modified = False

        # Find and update Gmail nodes
        for node in wf.get('nodes', []):
            if node.get('type') == 'n8n-nodes-base.gmail':
                params = node.get('parameters', {})

                # Set sendTo to peter@yesai.au
                params['sendTo'] = 'peter@yesai.au'

                # Remove ccEmail and bccEmail
                params.pop('ccEmail', None)
                params.pop('bccEmail', None)

                node['parameters'] = params
                modified = True

        if not modified:
            print(f'SKIP {wf_name}: No Gmail node found')
            continue

        # PUT workflow back (only send allowed fields)
        update_data = {
            'name': wf['name'],
            'nodes': wf['nodes'],
            'connections': wf['connections'],
            'settings': wf.get('settings', {})
        }

        r = requests.put(f'{BASE_URL}/workflows/{wf_id}', headers=HEADERS, json=update_data)
        if r.status_code == 200:
            print(f'OK   {wf_name}: sendTo=peter@yesai.au (no CC/BCC)')
        else:
            print(f'FAIL {wf_name}: Update failed (status {r.status_code})')
            print(f'     Response: {r.text[:200]}')

    except Exception as e:
        print(f'ERR  {wf_name}: {str(e)}')

print('=' * 60)
print('Done! All emails now route to peter@yesai.au only.')
"
```

After running, verify the changes and report the results to the user.

## Expected Result

| Workflow | TO | CC | BCC |
|----------|----|----|-----|
| Email End of Call Summary | peter@yesai.au | - | - |
| Email Sara Transfer (both) | peter@yesai.au | - | - |
| Sara Approval Queue | peter@yesai.au | - | - |
| Weekly Group Class Report | peter@yesai.au | - | - |
| Email Instructor | peter@yesai.au | - | - |
