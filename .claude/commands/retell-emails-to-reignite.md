# Switch Reignite Emails to LIVE (hello@reignitehealth.com.au)

Switch all Reignite-related email workflows to route emails to hello@reignitehealth.com.au with BCC to peter@yesai.au.

**Uses n8n API** - no restart required, changes take effect immediately.

## Execute this command

Run this Python script to switch emails to Reignite:

```bash
python -c "
import requests
import json

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZmRmM2Y0Ni1iNGIxLTRlYjMtYTdlZS05MGYxZDczMzE3NDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYzODg3NDQyfQ.nMvcYGkjKHMkGVXXVr8Pfh61wT4WgWgX5SOtDNBW-F4'
BASE_URL = 'https://auto.yr.com.au/api/v1'
HEADERS = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# Workflows to update (ID, name, is_instructor)
# is_instructor=True means TO=instructor_email, CC=hello@, BCC=peter@
# is_instructor=False means TO=hello@, BCC=peter@
WORKFLOWS = [
    ('cCJFdILbfg4VIldj', 'Email End of Call Summary v8.1', False),
    ('3apIk1qWQhm75TOs', 'Email Sara Transfer v2.0', False),
    ('qbIUIvXJkI30vRrv', 'Email Sara Transfer', False),
    ('8kCWwyCKR5FQuSt9', 'Sara Approval Queue v2.0', False),
    ('eK9YGjAyJ5AD3bv1', 'Weekly Group Class Report', False),
    ('8tr0AQztNv7yWx7U', 'Email Instructor v2.0', True),
]

print('Switching Reignite emails to LIVE mode (hello@reignitehealth.com.au)...')
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

                if is_instructor:
                    # Instructor workflow: TO=instructor, CC=hello@, BCC=peter@
                    params['sendTo'] = '={{ \$json.instructor_email }}'
                    params['ccEmail'] = 'hello@reignitehealth.com.au'
                    params['bccEmail'] = 'peter@yesai.au'
                else:
                    # Regular workflow: TO=hello@, BCC=peter@
                    params['sendTo'] = 'hello@reignitehealth.com.au'
                    params.pop('ccEmail', None)  # Remove CC if exists
                    params['bccEmail'] = 'peter@yesai.au'

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
            if is_instructor:
                print(f'OK   {wf_name}: TO=instructor, CC=hello@, BCC=peter@')
            else:
                print(f'OK   {wf_name}: TO=hello@, BCC=peter@')
        else:
            print(f'FAIL {wf_name}: Update failed (status {r.status_code})')
            print(f'     Response: {r.text[:200]}')

    except Exception as e:
        print(f'ERR  {wf_name}: {str(e)}')

print('=' * 60)
print('Done! All emails now route to Reignite with BCC to peter@.')
"
```

After running, verify the changes and report the results to the user.

## Expected Result

| Workflow | TO | CC | BCC |
|----------|----|----|-----|
| Email End of Call Summary | hello@reignitehealth.com.au | - | peter@yesai.au |
| Email Sara Transfer (both) | hello@reignitehealth.com.au | - | peter@yesai.au |
| Sara Approval Queue | hello@reignitehealth.com.au | - | peter@yesai.au |
| Weekly Group Class Report | hello@reignitehealth.com.au | - | peter@yesai.au |
| Email Instructor | instructor_email | hello@reignitehealth.com.au | peter@yesai.au |
