# Brevo CRM Import Procedure

**Last Updated:** 2025-12-13
**Purpose:** Complete procedure for importing contacts with full data enrichment

---

## OVERVIEW

This procedure ensures ALL available data is captured for each contact:
- Contact details (name, email, phone)
- Company information
- Appointment data
- Call recordings with URLs
- Source tracking
- List assignments

---

## PHASE 1: Data Source Search

### 1.1 Primary Sources (MUST check all)

| Source | Location | What to Look For |
|--------|----------|------------------|
| Master Contacts CSV | `CRM/Master_Contacts_With_Flags.csv` | Email, phone, company, DNC status |
| Appointments Enriched | `CRM/Appointments_Enriched.csv` | Full appointment + call details |
| Appointments Won | `CRM/Appointments_won.csv` | Won clients |
| Appointments Followup | `CRM/Appointments_followup.csv` | Follow-up needed |
| Call Logs Sheet 1 | `CRM/call_log_sheet_export.json` | 15,156 calls (Aug-Oct 2025) |
| Call Logs Sheet 2 | `CRM/call_log_sheet2_export.json` | 6,844 calls (Jun-Jul 2025) |

### 1.2 Secondary Sources (check for enrichment)

| Source | Location | What to Look For |
|--------|----------|------------------|
| HubSpot Companies | `CRM/All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` | Phone, social, description |
| HubSpot Contacts | `CRM/All_Contacts_2025_07_07_Cleaned.csv` | Additional contacts |
| Client Folders | `CLIENTS/[company-name]/` | Audit reports, emails, logos |
| DNC List | `CRM/DO_NOT_CALL_Master.csv` | Blocklist status |

### 1.3 Name Enrichment (REQUIRED when name is empty)

**CRITICAL:** If the primary source (appointments) has an empty name field, you MUST:

1. **Search by email** in secondary sources:
   - `CRM/All_Contacts_2025_07_07_Cleaned.csv` - look for exact email match
   - `CRM/Master_Contacts_With_Flags.csv` - may have name from original list

2. **Search by email domain** in company sources:
   - `CRM/All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` - check `Company Domain Name` column
   - Extract domain from email (e.g., `amrs@amariners.com.au` → search for `amariners.com.au`)

3. **Search by company name** if available:
   - HubSpot contacts/companies with matching company

4. **Manual lookup** if not found:
   - Check original Google Sheet for any additional columns
   - Look up company website for contact names
   - Flag for manual review if name cannot be found

**Example Code:**
```python
def enrich_name(email, company_name=None):
    """Search secondary sources for contact name when primary source is empty."""
    domain = email.split('@')[1] if '@' in email else None

    # 1. Search HubSpot Contacts by email
    with open('CRM/All_Contacts_2025_07_07_Cleaned.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('email', '').lower() == email.lower():
                first = row.get('first_name', '') or row.get('First Name', '')
                last = row.get('last_name', '') or row.get('Last Name', '')
                if first or last:
                    return first, last

    # 2. Search Master Contacts by email
    with open('CRM/Master_Contacts_With_Flags.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('email', '').lower() == email.lower():
                name = row.get('name', '') or row.get('contact_name', '')
                if name:
                    parts = name.split()
                    return parts[0], ' '.join(parts[1:]) if len(parts) > 1 else ''

    # 3. Search HubSpot Companies by domain for primary contact
    if domain:
        with open('CRM/All_Companies_2025-07-07_Cleaned_For_HubSpot.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if domain.lower() in str(row.get('Company Domain Name', '')).lower():
                    # Found company - check for primary contact
                    print(f"Found company: {row.get('Company name')} - check for contacts")

    return None, None  # Name not found - flag for manual review
```

**Root Cause of Missing Names:**
- Appointment spreadsheets may only capture email (no name column filled)
- Telemarketer notes may use email as identifier
- Original lead source may not have had name

**If name cannot be found:** Add to NOTES: `"Name not available - manual lookup required"`

---

## PHASE 2: Call Recording Search

### 2.1 Search Strategy

Search call logs using these methods (in order of reliability):

1. **Phone number match** - Match `to_number` or `from_number` in call logs
2. **Timestamp from retell_log** - Use date/time hint from appointment data (e.g., `25/08/2025, 16:4`)

**NOTE:** Do NOT use transcript searching - it causes false positives (e.g., "completely" matches "etel").

### 2.2 Search Code Template

```python
import json
import re

def clean_phone(phone):
    """Normalize phone number - last 9 digits only."""
    if not phone:
        return ""
    return re.sub(r'[^\d]', '', str(phone))[-9:]

def find_call_recording(phone_numbers, timestamp_hint):
    """
    Search call logs for a specific contact.

    Args:
        phone_numbers: List of possible phone numbers
        timestamp_hint: Date/time from retell_log (DD/MM/YYYY, HH:MM)
    """
    matches = []
    seen_ids = set()

    for sheet in ['call_log_sheet_export.json', 'call_log_sheet2_export.json']:
        with open(f'C:/Users/peter/Downloads/CC/CRM/{sheet}', 'r') as f:
            data = json.load(f)

        for record in data:
            call_id = record.get('call_id', '')
            if call_id in seen_ids:
                continue

            matched = False

            # Method 1: Phone number match (PREFERRED)
            to_num = clean_phone(record.get('to_number', ''))
            from_num = clean_phone(record.get('from_number', ''))
            for phone in phone_numbers:
                clean_p = clean_phone(phone)
                if clean_p and len(clean_p) >= 8:
                    if clean_p in to_num or clean_p in from_num:
                        matched = True
                        break

            # Method 2: Timestamp match (if no phone match)
            if not matched and timestamp_hint:
                start_time = record.get('start_time', '')
                # Convert timestamp hint to match format
                if timestamp_hint[:10] in start_time:
                    matched = True

            if matched:
                seen_ids.add(call_id)
                matches.append(record)

    return matches
```

### 2.3 Key Fields in Call Logs

| Field | Description |
|-------|-------------|
| `call_id` | Unique identifier (e.g., `call_7c9e9fe93366b7d6887f9439e2b`) |
| `start_time` | Format: `DD/MM/YYYY, HH:MM:SS` |
| `to_number` | Called number (THIS is the real phone!) |
| `from_number` | Caller ID |
| `recording_url` | CloudFront URL to WAV file |
| `plain_transcript` | Text transcript (may have errors) |
| `human_duration` | e.g., `3m 58s` |

---

## PHASE 3: Brevo Update

### 3.1 Contact Attributes to Update

| Attribute | Source | Notes |
|-----------|--------|-------|
| FIRSTNAME | Appointments/Master CSV | |
| LASTNAME | Appointments/Master CSV | |
| COMPANY | Appointments (preferred) | Real company name |
| SMS | Call logs `to_number` | Use ACTUAL called number, not CSV |
| APPOINTMENT_DATE | Appointments | Format: YYYY-MM-DD |
| APPOINTMENT_TIME | Appointments | e.g., `11:00am` |
| APPOINTMENT_STATUS | Appointments | e.g., `Seen - Client` |
| DEAL_STAGE | Derived from status | Won/Lost/Negotiation/etc |
| QUALITY | Appointments | Good/OK/Poor |
| FOLLOWUP_STATUS | Appointments | Client/Follow-up/etc |
| FOLLOWUP_DATE | Appointments | Date type - for sorting follow-ups |
| RETELL_LOG | Call logs | Format: `DATE DIRECTION (DURATION) - Recording: URL` |
| SOURCE | Master CSV / derived | e.g., `Telemarketer Campaign` |
| NOTES | Combined from all sources | Include follow-up history |

### 3.2 Deal Stage Mapping

| Status Contains | Deal Stage |
|-----------------|------------|
| won, client | Won |
| followup, negotiation | Negotiation |
| booked, qualified | Qualified Lead |
| contacted, new | New Lead |
| no_show, dead, lost | Lost |

### 3.3 List Assignments

| List ID | Name | Assign When |
|---------|------|-------------|
| 24 | All Telemarketer Contacts | Always |
| 25 | Safe to Contact | NOT on DNC |
| 27 | DO NOT CALL | On DNC list |
| 28 | Had Appointments | Has appointment data |
| 29 | Previously Called | Called but no appointment |

### 3.4 Update Code Template

```python
from brevo_api import BrevoClient

client = BrevoClient()

def update_contact_complete(email, data):
    """Update contact with all available data."""

    attrs = {
        'FIRSTNAME': data.get('first_name'),
        'LASTNAME': data.get('last_name'),
        'COMPANY': data.get('company'),
        'SMS': data.get('phone'),  # From call logs to_number!
        'APPOINTMENT_DATE': data.get('appt_date'),
        'APPOINTMENT_TIME': data.get('appt_time'),
        'APPOINTMENT_STATUS': data.get('appt_status'),
        'DEAL_STAGE': data.get('deal_stage'),
        'QUALITY': data.get('quality'),
        'FOLLOWUP_STATUS': data.get('followup'),
        'SOURCE': data.get('source', 'Telemarketer Campaign'),
        'NOTES': data.get('notes'),
    }

    # Build RETELL_LOG with all recordings
    if data.get('calls'):
        log_entries = []
        for call in data['calls']:
            entry = f"{call['date']} {call['direction']} ({call['duration']}) - Recording: {call['recording_url']}"
            log_entries.append(entry)
        attrs['RETELL_LOG'] = '\n'.join(log_entries)

    # Remove None values
    attrs = {k: v for k, v in attrs.items() if v}

    result = client.update_contact(email, attrs)

    # Handle SMS conflict
    if not result.get('success') and 'SMS is already associated' in str(result.get('error', '')):
        del attrs['SMS']
        attrs['NOTES'] = (attrs.get('NOTES', '') + f" Phone: {data.get('phone')} (shared with another contact)")
        result = client.update_contact(email, attrs)

    return result
```

---

## PHASE 4: Company Linking

### 4.1 Create/Update Company

```python
def ensure_company(client, company_name, domain, contact_ids):
    """Create company if needed and link contacts."""

    # Search existing
    companies = client._request('GET', 'companies', params={'limit': 100})
    company_id = None

    for co in companies.get('data', {}).get('items', []):
        if company_name.lower() in co.get('attributes', {}).get('name', '').lower():
            company_id = co.get('id')
            break

    # Create if not exists
    if not company_id:
        result = client._request('POST', 'companies', {
            'name': company_name,
            'attributes': {'domain': domain} if domain else {}
        })
        if result.get('success'):
            company_id = result['data']['id']

    # Link contacts
    if company_id and contact_ids:
        client._request('PATCH', f'companies/link-unlink/{company_id}', {
            'linkContactIds': contact_ids
        })

    return company_id
```

---

## PHASE 5: Verification

### 5.1 Checklist After Each Import

- [ ] Contact has all attributes populated
- [ ] RETELL_LOG contains recording URL(s)
- [ ] SMS field has correct phone (from call logs)
- [ ] Contact linked to company
- [ ] Contact in correct lists
- [ ] Notes include follow-up history

### 5.2 Verification Code

```python
def verify_contact(client, email):
    """Verify contact has complete data."""
    result = client.get_contact(email)
    if not result.get('success'):
        return {'complete': False, 'error': 'Contact not found'}

    data = result['data']
    attrs = data.get('attributes', {})

    required = ['FIRSTNAME', 'LASTNAME', 'COMPANY', 'SOURCE']
    appointment_fields = ['APPOINTMENT_DATE', 'APPOINTMENT_STATUS', 'DEAL_STAGE']

    missing = [f for f in required if not attrs.get(f)]

    has_recording = 'recording' in attrs.get('RETELL_LOG', '').lower()
    has_lists = len(data.get('listIds', [])) > 0

    return {
        'complete': len(missing) == 0 and has_recording and has_lists,
        'missing_fields': missing,
        'has_recording': has_recording,
        'has_lists': has_lists,
        'list_ids': data.get('listIds', [])
    }
```

---

## LESSONS LEARNED

### From Reignite Health
1. Multiple contacts per company (Sara, Liam, hello@)
2. Check CLIENTS folder for audit reports
3. HubSpot exports have additional phone/social data
4. Alt domains exist (reignitehealth.co vs .com.au)

### From Paradise Distributors
1. **Phone number in CSV may be WRONG** - use call logs `to_number`
2. **Timestamp matching** - use retell_log date to find calls
3. Appointment notes have full call details including correct phone
4. **Personal email domains cause bad company records** - gmail.com as company domain

### From Bulk Import Review
1. **NEVER use personal email domains as company domain**
2. **NEVER use URLs as company names** - extract proper name
3. **48 companies had URL-like names** from original telemarketer import
4. **NEVER search transcripts** - causes massive false positives (e.g., "completely" matches "etel")

### General
1. Search call logs by phone number and timestamp ONLY
2. The actual called phone is in `to_number`, not CSV
3. SMS field conflicts mean phone is shared - add to NOTES instead
4. Use appointment data for company names (most accurate)

---

## DATA QUALITY RULES

### Personal Email Domains (NEVER use as company domain)

```python
PERSONAL_DOMAINS = [
    'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
    'bigpond.com', 'live.com', 'icloud.com', 'aol.com',
    'msn.com', 'optusnet.com.au', 'hotmail.com.au',
    'yahoo.com.au', 'mail.com'
]

def get_company_domain(email, company_name=None):
    """Extract domain only if it's a business domain."""
    if not email or '@' not in email:
        return None

    domain = email.split('@')[1].lower()

    # Never use personal email domains
    if domain in PERSONAL_DOMAINS:
        return None

    return domain
```

### Company Name Cleaning

```python
def clean_company_name(name):
    """Extract proper company name from URL-like strings."""
    if not name:
        return None

    # Remove URL prefixes
    name = name.replace('https://', '').replace('http://', '').replace('www.', '')

    # If it looks like a domain, try to extract company name
    if '.com' in name or '.au' in name or '.net' in name:
        # Remove TLD and path
        name = name.split('/')[0]  # Remove path
        name = name.replace('.com.au', '').replace('.net.au', '')
        name = name.replace('.com', '').replace('.au', '').replace('.net', '')

        # Convert to title case
        name = name.replace('-', ' ').replace('_', ' ').title()

    return name.strip() if name else None
```

### Company Creation Rules

1. **Source priority for company name:**
   - Appointments data (most accurate - real names)
   - HubSpot exports (verified business names)
   - Master CSV (may have domains only)

2. **Domain handling:**
   - Only set domain if from business email
   - Never use gmail.com, hotmail.com, etc.
   - If contact uses personal email, leave domain blank

3. **Name validation:**
   - Reject names that are URLs
   - Reject names with http/www
   - Clean domain-style names to proper names

---

## QUICK REFERENCE

### Files
- Scripts: `C:\Users\peter\Downloads\CC\MARKETING\scripts\`
- Data: `C:\Users\peter\Downloads\CC\CRM\`
- Call logs: `call_log_sheet_export.json`, `call_log_sheet2_export.json`

### Commands
```bash
# Verify contact
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python -c "from brevo_api import BrevoClient; c=BrevoClient(); print(c.get_contact('email@example.com'))"

# Search call logs
python -c "import json; [print(r) for r in json.load(open('../CRM/call_log_sheet_export.json')) if 'searchterm' in json.dumps(r).lower()][:5]"
```
