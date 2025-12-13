# Brevo CRM Import Procedure

**Last Updated:** 2025-12-13
**Purpose:** Complete procedure for importing contacts with full data enrichment
**Status:** CLEAN SLATE - All data deleted, ready for fresh import

---

## PRE-REQUISITES

Before running import:
1. Brevo account is empty (run `delete_all_brevo_data.py` if needed)
2. All data files are up to date
3. Custom attributes exist in Brevo (created automatically on first import)

---

## DATA SOURCES - FULL PATHS

### Primary Sources (MUST process all)

| Source | Full Path | Records | What to Extract |
|--------|-----------|---------|-----------------|
| **Appointments** | `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv` | 87 | Name, email, company, dates, status, quality |
| **Call Logs 1** | `C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json` | 15,156 | Recording URLs, phone numbers, timestamps |
| **Call Logs 2** | `C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json` | 6,844 | Recording URLs, phone numbers, timestamps |
| **Master Contacts** | `C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv` | 54,086 | Email, phone, company, DNC flags |
| **DNC List** | `C:\Users\peter\Downloads\CC\CRM\DO_NOT_CALL_Master.csv` | 852 | Blocklist emails |

### Secondary Sources (for enrichment)

| Source | Full Path | What to Extract |
|--------|-----------|-----------------|
| **HubSpot Companies** | `C:\Users\peter\Downloads\CC\CRM\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` | Phone, social, verified names |
| **HubSpot Contacts** | `C:\Users\peter\Downloads\CC\CRM\All_Contacts_2025_07_07_Cleaned.csv` | Additional contact details |
| **Client Folders** | `C:\Users\peter\Downloads\CC\CLIENTS\[company-name]\` | Audit reports, emails |

### Appointment Sub-files

| File | Full Path | Purpose |
|------|-----------|---------|
| Won | `C:\Users\peter\Downloads\CC\CRM\Appointments_won.csv` | Won clients |
| Followup | `C:\Users\peter\Downloads\CC\CRM\Appointments_followup.csv` | Follow-up needed |
| Booked | `C:\Users\peter\Downloads\CC\CRM\Appointments_booked.csv` | Upcoming appointments |
| No Show | `C:\Users\peter\Downloads\CC\CRM\Appointments_no_show.csv` | Missed appointments |

---

## IMPORT ORDER (CRITICAL)

**Must follow this exact order:**

1. **Create Brevo Lists** (if not exist)
2. **Import Appointment Contacts** (highest priority - best data)
3. **Import Bulk Contacts** (from Master CSV)
4. **Apply DNC Blocklist**
5. **Create Companies** (from appointment data only)
6. **Link Contacts to Companies**
7. **Verify Import**

---

## PHASE 1: Create Brevo Lists

### Lists to Create

| List ID | Name | Purpose |
|---------|------|---------|
| 24 | All Telemarketer Contacts | Everyone imported |
| 25 | Safe to Contact | NOT on DNC |
| 27 | DO NOT CALL | DNC - blocklisted |
| 28 | Had Appointments | Has appointment data |
| 29 | Previously Called | Called but no appointment |

### Command
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python -c "
from brevo_api import BrevoClient
client = BrevoClient()

lists = [
    ('All Telemarketer Contacts', 24),
    ('Safe to Contact', 25),
    ('DO NOT CALL', 27),
    ('Had Appointments', 28),
    ('Previously Called', 29),
]

for name, expected_id in lists:
    result = client.create_list(name)
    if result.get('success'):
        print(f'Created: {name} (ID: {result[\"data\"].get(\"id\")})')
    else:
        print(f'Already exists or error: {name} - {result.get(\"error\", \"\")}')
"
```

---

## PHASE 2: Import Appointment Contacts

### 2.1 Data Processing Rules

**Name Extraction:**
- Split `name` field into FIRSTNAME and LASTNAME
- If name is empty, search secondary sources (see Section 2.2)
- If still empty, add to NOTES: "Name not available"

**Company Handling:**
- Use `company` field from appointments (most accurate)
- NEVER use URL-like names (clean them first)
- NEVER use personal email domains as company domain

**Phone Number:**
- Primary: `to_number` from call logs (the ACTUAL called number)
- Fallback: `phone` from appointments CSV
- Format: +61XXXXXXXXX

**Date Fields:**
- APPOINTMENT_DATE: YYYY-MM-DD format
- FOLLOWUP_DATE: YYYY-MM-DD format (for sorting)

### 2.2 Name Enrichment (when name is empty)

**Search order:**
1. `C:\Users\peter\Downloads\CC\CRM\All_Contacts_2025_07_07_Cleaned.csv` - exact email match
2. `C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv` - email match
3. `C:\Users\peter\Downloads\CC\CRM\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` - domain match

**If not found:** Flag for manual review in NOTES field.

### 2.3 Call Recording Search

**ONLY use these methods (in order):**
1. **Phone number match** - Match last 9 digits of `to_number` or `from_number`
2. **Timestamp match** - Use `retell_log` date hint

**NEVER search transcripts** - causes massive false positives!

**Call Log Files:**
- `C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json` (Aug-Oct 2025)
- `C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json` (Jun-Jul 2025)

### 2.4 Import Command
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python bulk_import_appointments.py
```

---

## PHASE 3: Import Bulk Contacts

### 3.1 Source File
`C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv`

### 3.2 Fields to Import
- email (required)
- name → FIRSTNAME, LASTNAME
- company → COMPANY
- phone → SMS (if valid)
- source → SOURCE
- is_dnc → determines list assignment
- was_called → determines list assignment

### 3.3 List Assignment Logic
```python
if is_dnc:
    lists = [24, 27]  # All + DNC
elif was_called:
    lists = [24, 25, 29]  # All + Safe + Previously Called
else:
    lists = [24, 25]  # All + Safe (Fresh leads)
```

### 3.4 Import Command
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python bulk_import_contacts.py
```

---

## PHASE 4: Apply DNC Blocklist

### 4.1 Source File
`C:\Users\peter\Downloads\CC\CRM\DO_NOT_CALL_Master.csv`

### 4.2 Process
1. Read all emails from DNC list
2. For each email:
   - Set `emailBlacklisted: true`
   - Add to list 27 (DO NOT CALL)
   - Remove from list 25 (Safe to Contact)

### 4.3 Command
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python -c "
from brevo_api import BrevoClient
import csv

client = BrevoClient()

dnc_file = 'C:/Users/peter/Downloads/CC/CRM/DO_NOT_CALL_Master.csv'
blocked = 0
errors = 0

with open(dnc_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip().lower()
        if email and '@' in email:
            result = client.blocklist_contact(email=email)
            if result.get('success'):
                blocked += 1
            else:
                errors += 1

print(f'Blocklisted: {blocked}')
print(f'Errors: {errors}')
"
```

---

## PHASE 5: Create Companies

### 5.1 Rules

**ONLY create companies from:**
- Appointment data (verified real names)
- HubSpot exports (verified business names)

**NEVER create companies from:**
- Personal email domains (gmail.com, hotmail.com, etc.)
- URL-like strings
- Domain-only names without context

### 5.2 Personal Domains Blacklist
```python
PERSONAL_DOMAINS = [
    'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
    'bigpond.com', 'bigpond.net.au', 'live.com', 'icloud.com',
    'aol.com', 'msn.com', 'optusnet.com.au', 'hotmail.com.au',
    'yahoo.com.au', 'mail.com'
]
```

### 5.3 Company Name Cleaning
```python
def clean_company_name(name):
    if not name:
        return None

    # Reject URL-like names
    if name.startswith('http') or name.startswith('www.'):
        return None

    # Clean domain-style names
    if '.com' in name or '.au' in name:
        name = name.split('/')[0]
        name = name.replace('.com.au', '').replace('.net.au', '')
        name = name.replace('.com', '').replace('.au', '')
        name = name.replace('-', ' ').replace('_', ' ').title()

    return name.strip() if name else None
```

### 5.4 Company Creation Command
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python create_companies_from_appointments.py
```

---

## PHASE 6: Link Contacts to Companies

After companies are created, link related contacts:

```python
def link_contacts_to_company(client, company_id, emails):
    """Link multiple contacts to a company."""
    contact_ids = []
    for email in emails:
        result = client.get_contact(email)
        if result.get('success'):
            contact_ids.append(result['data']['id'])

    if contact_ids:
        client._request('PATCH', f'companies/link-unlink/{company_id}', {
            'linkContactIds': contact_ids
        })
```

---

## PHASE 7: Verification

### 7.1 Check Counts
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python -c "
from brevo_api import BrevoClient
client = BrevoClient()

# Total contacts
result = client.get_contacts(limit=1)
print(f'Total contacts: {result[\"data\"][\"count\"]}')

# List counts
lists = [(24, 'All'), (25, 'Safe'), (27, 'DNC'), (28, 'Appointments'), (29, 'Called')]
for lid, name in lists:
    result = client._request('GET', f'contacts/lists/{lid}')
    count = result['data'].get('totalSubscribers', 0) if result.get('success') else 0
    print(f'{name}: {count}')

# Companies
result = client._request('GET', 'companies', params={'limit': 1})
print(f'Companies: {len(result.get(\"data\", {}).get(\"items\", []))}')
"
```

### 7.2 Data Quality Check
```bash
python -c "
from brevo_api import BrevoClient
client = BrevoClient()

# Sample appointment contacts
result = client._request('GET', 'contacts/lists/28/contacts', params={'limit': 20})
contacts = result['data'].get('contacts', [])

print('=== APPOINTMENT CONTACTS QUALITY ===')
for c in contacts[:5]:
    attrs = c.get('attributes', {})
    email = c.get('email')
    name = f\"{attrs.get('FIRSTNAME', '')} {attrs.get('LASTNAME', '')}\".strip()
    company = attrs.get('COMPANY', '')
    has_retell = 'Yes' if attrs.get('RETELL_LOG') else 'No'
    print(f'{email}: Name={name or \"MISSING\"}, Company={company or \"MISSING\"}, Recording={has_retell}')
"
```

### 7.3 Expected Results

| Metric | Expected |
|--------|----------|
| Total contacts | ~35,000 |
| Appointment contacts (list 28) | ~87 |
| DNC contacts (list 27) | ~658 |
| Companies | ~40-50 (from appointments only) |
| Contacts with names | 100% of appointments, ~10% of bulk |
| Contacts with recordings | 70%+ of appointments |

---

## SCRIPTS REFERENCE

| Script | Full Path | Purpose |
|--------|-----------|---------|
| `brevo_api.py` | `C:\Users\peter\Downloads\CC\MARKETING\scripts\brevo_api.py` | API wrapper |
| `bulk_import_appointments.py` | `C:\Users\peter\Downloads\CC\MARKETING\scripts\bulk_import_appointments.py` | Import appointments |
| `delete_all_brevo_data.py` | `C:\Users\peter\Downloads\CC\MARKETING\scripts\delete_all_brevo_data.py` | Wipe all data |

---

## LESSONS LEARNED

### Data Quality Issues (from previous import)

1. **93% of bulk contacts had no name** - This is expected (raw email lists)
2. **DNC blocklisting failed** - 0/658 were blocklisted
3. **48/87 companies had URL-like names** - From using domain as name
4. **Transcript search caused false positives** - "etel" matched "completely"

### Rules to Prevent Issues

1. **Names:** Only expect names on appointment contacts; bulk is email-only
2. **Companies:** Only create from appointment data with real business names
3. **Domains:** Never use personal email domains (gmail, hotmail, etc.)
4. **Call search:** Phone + timestamp ONLY, never transcript
5. **DNC:** Must explicitly set `emailBlacklisted: true` on each contact

---

## TROUBLESHOOTING

### Contact shows email as name in Brevo UI
- **Cause:** FIRSTNAME and LASTNAME are empty
- **Fix:** Enrich from secondary sources or flag for manual lookup

### SMS field conflict error
- **Cause:** Phone number already assigned to another contact
- **Fix:** Add phone to NOTES field instead: "Phone: +61... (shared)"

### Company has gmail.com domain
- **Cause:** Contact uses personal email
- **Fix:** Leave domain blank, or don't create company for personal emails

### Recordings not found
- **Cause:** Phone number mismatch or call not in export date range
- **Fix:** Search by timestamp if available, or accept no recording

---

## QUICK COMMANDS

```bash
# Navigate to scripts
cd /c/Users/peter/Downloads/CC/MARKETING/scripts

# Check Brevo connection
python brevo_api.py

# Get contact details
python -c "from brevo_api import BrevoClient; print(BrevoClient().get_contact('email@example.com'))"

# Delete all data (requires confirmation)
python delete_all_brevo_data.py

# Search call logs by phone
python -c "
import json
phone = '412345678'  # Last 9 digits
for f in ['../CRM/call_log_sheet_export.json', '../CRM/call_log_sheet2_export.json']:
    data = json.load(open(f.replace('../', 'C:/Users/peter/Downloads/CC/')))
    for r in data:
        if phone in r.get('to_number', '') or phone in r.get('from_number', ''):
            print(r.get('start_time'), r.get('recording_url', 'No recording'))
"
```
