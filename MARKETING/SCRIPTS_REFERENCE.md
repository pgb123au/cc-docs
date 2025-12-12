# Marketing Scripts Reference

**Location:** `C:\Users\peter\Downloads\CC\MARKETING\scripts\`

---

## brevo_api.py - Core API Wrapper

### Usage
```python
from brevo_api import BrevoClient
client = BrevoClient()

# Contacts
client.add_contact(email, attributes={}, list_ids=[])
client.get_contact(email)
client.update_contact(email, attributes={})
client.get_contacts(limit=50, offset=0)

# Lists
client.create_list(name, folder_id=1)
client.get_lists(limit=50)
client.add_contacts_to_list(list_id, [emails])

# Companies (via _request)
client._request('POST', 'companies', {'name': 'Company Name'})
client._request('GET', 'companies', params={'limit': 100})
client._request('PATCH', f'companies/link-unlink/{company_id}', {'linkContactIds': [contact_id]})

# Email
client.send_email(to_email, to_name, subject, html_content, sender_name, sender_email)

# Blocklist
client.blocklist_contact(email=email)
```

### Important Notes
- Sender email MUST be `yesrightau@gmail.com` (verified)
- Contact IDs are integers (e.g., 778), not email addresses
- Company IDs are strings (e.g., '693c813d58677e43aa29b493')

---

## bulk_import_brevo.py - Mass Contact Import

### Usage
```bash
python bulk_import_brevo.py --dry-run          # Preview
python bulk_import_brevo.py --limit 1000       # Test batch
python bulk_import_brevo.py --use-bulk         # Full import with bulk API
python bulk_import_brevo.py                    # Full import (slower)
```

### What it does
1. Loads contacts from `Master_Contacts_With_Flags.csv`
2. Creates lists if they don't exist
3. Imports contacts with list assignments
4. Blocklists DNC contacts

### Data source
`C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv`

---

## update_contact_attributes.py - Update COMPANY/SOURCE

### Usage
```bash
python update_contact_attributes.py --limit 100   # Test
python update_contact_attributes.py               # All contacts
```

### What it does
- Reads `Master_Contacts_With_Flags.csv`
- Updates existing Brevo contacts with COMPANY, SOURCE, FIRSTNAME, LASTNAME
- Rate limited at 0.05s per contact
- ~30 minutes for full run

### Prerequisites
- Custom attributes must exist in Brevo (already created)
- Contacts must already be imported

---

## create_companies.py - Create Company Records

### Usage
```bash
python create_companies.py --limit 50    # Test
python create_companies.py               # All companies
```

### What it does
1. Extracts unique companies from CSV
2. Creates Company record in Brevo CRM
3. Gets contact ID for each email
4. Links contacts to companies

### Note
- Uses domain names from CSV as company names (not ideal)
- Better: Use `import_appointments.py` for real company names

---

## import_appointments.py - Import Appointments with Full Data

### Usage
```bash
python import_appointments.py --dry-run   # Preview
python import_appointments.py             # Import all
```

### What it does
1. Loads from multiple appointment CSVs (won, followup, booked, etc.)
2. Updates contact with:
   - FIRSTNAME, LASTNAME
   - COMPANY
   - APPOINTMENT_DATE
   - APPOINTMENT_STATUS
   - DEAL_STAGE (mapped from status)
3. Adds to "Had Appointments" list (ID: 28)

### Deal Stage Mapping
| Status Category | Deal Stage |
|-----------------|------------|
| won | Closed Won |
| followup | Negotiation |
| booked | Qualified Lead |
| contacted | New Lead |
| no_show, dead | Lost |

### Data sources
```
C:\Users\peter\Downloads\CC\CRM\Appointments_won.csv
C:\Users\peter\Downloads\CC\CRM\Appointments_followup.csv
C:\Users\peter\Downloads\CC\CRM\Appointments_booked.csv
C:\Users\peter\Downloads\CC\CRM\Appointments_contacted.csv
```

---

## mobilemessage.py - SMS Integration

### Usage
```python
from mobilemessage import MobileMessageClient
client = MobileMessageClient()
result = client.send_sms('0412345678', 'Hello from Yes AI!')
```

### CLI Test
```bash
python mobilemessage.py 0412111000 "Test message"
```

### Credentials (hardcoded)
- Username: `03KnC9`
- Password: `TthH29CLiQ7S8Jd22jMq4UWr16YgtuJBPgjMNX23faP`
- Endpoint: `https://api.mobilemessage.com.au/simple/send-sms`

---

## assign_contacts_to_lists.py - List Assignment Utility

### Usage
```bash
python assign_contacts_to_lists.py
```

### What it does
1. Fetches all contacts from Brevo
2. Categorizes based on attributes/source
3. Assigns to appropriate lists
4. Useful if list assignments got out of sync

---

## call_log_linker.py - Retell/Zadarma Recording Linker

### Location
`C:\Users\peter\Downloads\CC\CRM\call_log_linker.py`

### Usage
```bash
python call_log_linker.py --stats              # Show statistics
python call_log_linker.py --lookup 0412345678  # Look up number
python call_log_linker.py --retell             # Link Retell recordings
python call_log_linker.py --zadarma export.csv # Link Zadarma CDR
```

### Retell API
- Uses main API key from `C:\Users\peter\Downloads\Retell_API_Key.txt`
- POST to `https://api.retellai.com/v2/list-calls`

---

## QUICK REFERENCE

### Check Brevo State
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python -c "
from brevo_api import BrevoClient
client = BrevoClient()
c = client.get_contacts(limit=1)
print(f'Total contacts: {c[\"data\"][\"count\"]}')
lists = client.get_lists()
for l in lists['data']['lists']:
    if l['id'] >= 24:
        print(f'{l[\"name\"]}: {l[\"totalSubscribers\"]} (ID: {l[\"id\"]})')
"
```

### Check Specific Contact
```bash
python -c "
from brevo_api import BrevoClient
client = BrevoClient()
c = client.get_contact('sara@reignitehealth.com.au')
print(c['data'])
"
```

### Send Test Email
```bash
python -c "
from brevo_api import BrevoClient
client = BrevoClient()
r = client.send_email(
    'Peter@Ball.com.au', 'Peter Ball',
    'Test Subject', '<h1>Test</h1>',
    'Yes AI', 'yesrightau@gmail.com'
)
print(r)
"
```
