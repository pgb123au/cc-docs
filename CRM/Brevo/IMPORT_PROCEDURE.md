# Brevo CRM Import Procedure

**Last Updated:** 2025-12-13
**Purpose:** Complete procedure for importing contacts with full data enrichment
**Status:** CLEAN SLATE - All data deleted, ready for fresh import

---

## PRE-REQUISITES

Before running import:
1. All data files are up to date
2. Custom attributes exist in Brevo (created automatically on first import)
3. Scripts have been verified (see SCRIPTS CHECKLIST at end)

---

## DATA SOURCES - COMPLETE FILE INVENTORY

### HubSpot CRM Exports (Original Source)

| File | Path | Records | Key Fields |
|------|------|---------|------------|
| **HubSpot Companies** | `C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` | 363,516 | Company name, Domain, Email, Phone (1-3), Address, City, Postal Code, State, Country, Google reviews, GBP rating, Business type, Industry, Year Founded, Website URL, Business Description, Social links (FB, Twitter, LinkedIn, Instagram, YouTube) |
| **HubSpot Contacts** | `C:\Users\peter\Documents\HS\All_Contacts_2025_07_07_Cleaned.csv` | 207,277 | First Name, Last Name, Email, Phone Number 1, Mobile Phone Number, Company Name, Website URL, Job Title, City, Postal Code, State/Region, Street Address, Country, Email Domain, NeverBounce Validation Result |

### Telemarketer Dialer Original Files

| File | Original Path | Derived Path | Records | Key Fields |
|------|---------------|--------------|---------|------------|
| **Massive List - Main** | `C:\Users\peter\retell-dialer\massive_list.csv` | (source for Master_Contacts) | 47,086 | First Name, Last Name, Mobile Phone Number, Email, Company Name, Website URL, Industry, Email Domain, City, Associated Company |
| **Massive List - Victoria** | `C:\Users\peter\retell-dialer\massive_list_vic.csv` | (source for Master_Contacts) | 19,238 | Same as above |
| **Pakenham Companies** | `C:\Users\peter\retell-dialer\companies_pakenham.csv` | (source for Master_Contacts) | 196 | Same as above |
| **Called Log (Text)** | `C:\Users\peter\retell-dialer\called_log.txt` | (source for was_called flag) | 27,786 | Phone numbers called |
| **Called Numbers (JSON)** | `C:\Users\peter\retell-dialer\called_numbers.json` | (source for call counts) | 27,799 | Phone numbers with timestamps |

### Derived/Processed Files

| File | Path | Records | Created From |
|------|------|---------|--------------|
| **Master Contacts With Flags** | `C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv` | 54,086 | massive_list + massive_list_vic + companies_pakenham + called_log |
| **Fresh Leads Never Called** | `C:\Users\peter\Downloads\CC\CRM\Fresh_Leads_Never_Called.csv` | 24,335 | Master minus called contacts |
| **Safe To Contact** | `C:\Users\peter\Downloads\CC\CRM\Safe_To_Contact.csv` | 21,693 | Called contacts ready for re-engagement |
| **Brevo Import Filtered** | `C:\Users\peter\Downloads\CC\CRM\Brevo_Import_Filtered.csv` | 755 | All_Contacts + All_Companies with quality filters |

### Appointments - 4 Source Tabs

The appointments data comes from a Google Sheet with **4 tabs**:

| Tab Name | Type | Description |
|----------|------|-------------|
| **Appts** | Appointments | Original appointments (older entries) |
| **Appts New** | Appointments | Newer appointment entries |
| **Call Backs** | Follow-ups | Original follow-up/callback entries |
| **Call Backs New** | Follow-ups | Newer follow-up entries |

### Appointment Files (Combined & By Status)

| File | Path | Records | Source |
|------|------|---------|--------|
| **All Appointments (Combined)** | `C:\Users\peter\Downloads\CC\CRM\All_Appointments_Extracted.csv` | 87 | All 4 tabs combined |
| **Appointments Enriched** | `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv` | 87 | Above + cross-reference with massive_lists |

**By Status Category:**

| File | Path | Records |
|------|------|---------|
| Won | `C:\Users\peter\Downloads\CC\CRM\Appointments_won.csv` | 6 |
| Follow-up | `C:\Users\peter\Downloads\CC\CRM\Appointments_followup.csv` | 15 |
| Booked | `C:\Users\peter\Downloads\CC\CRM\Appointments_booked.csv` | 4 |
| Contacted | `C:\Users\peter\Downloads\CC\CRM\Appointments_contacted.csv` | 10 |
| Seen | `C:\Users\peter\Downloads\CC\CRM\Appointments_seen.csv` | 2 |
| No Show | `C:\Users\peter\Downloads\CC\CRM\Appointments_no_show.csv` | 13 |
| Reschedule | `C:\Users\peter\Downloads\CC\CRM\Appointments_reschedule.csv` | 5 |
| Bad Prospect | `C:\Users\peter\Downloads\CC\CRM\Appointments_bad_prospect.csv` | 16 |
| Dead | `C:\Users\peter\Downloads\CC\CRM\Appointments_dead.csv` | 1 |

### Retell API Call Logs

| File | Path | Records | Date Range |
|------|------|---------|------------|
| **Call Log Export 1** | `C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json` | 15,156 | Aug-Oct 2025 |
| **Call Log Export 2** | `C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json` | 6,844 | Jun-Jul 2025 |
| **Total** | | **22,000** | Jun-Oct 2025 |

**Note:** These exports may have gaps. For complete data, query Retell API directly.

---

## IMPORT ORDER (CRITICAL)

**Must follow this exact order:**

1. **Create Brevo Lists** (if not exist)
2. **Import Appointment Contacts** (highest priority - best data) - TEST FIRST
3. **Verify Appointment Import** (100% quality before bulk)
4. **Import Bulk Contacts** (in batches of 100)
5. **Create Companies** (from multiple sources)
6. **Link Contacts to Companies**
7. **Final Verification**

---

## PHASE 1: Create Brevo Lists

### Lists to Create

| List ID | Name | Purpose |
|---------|------|---------|
| 24 | All Telemarketer Contacts | Everyone imported |
| 25 | Safe to Contact | Available for campaigns |
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
- Third option: Match via phone in Master Contacts
- Format: +61XXXXXXXXX

**Date Fields:**
- APPOINTMENT_DATE: YYYY-MM-DD format
- FOLLOWUP_DATE: YYYY-MM-DD format (for sorting)

### 2.2 Name Enrichment (when name is empty)

**Search order for names:**

1. **By Email Match:**
   - `C:\Users\peter\Documents\HS\All_Contacts_2025_07_07_Cleaned.csv` - exact email match (First Name, Last Name columns)
   - `C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv` - email match (first_name, last_name columns)

2. **By Phone Match:**
   - Same files as above, match by last 9 digits of phone number
   - This is important because sometimes email is known but name is in a different record matched by phone

3. **By Domain Match (for company name):**
   - `C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` - domain match (Company name column)

4. **Search Large Datasets:**
   - Before flagging for manual review, search ALL columns of the 363K companies and 207K contacts files
   - These contain rich data that may have names/details not in smaller files

**If not found after all steps:** Flag for manual review in NOTES field.

### 2.3 Call Recording Search

**ONLY use these methods (in order):**
1. **Phone number match** - Match last 9 digits of `to_number` or `from_number`
2. **Timestamp match** - Use `retell_log` date hint from appointments CSV

**NEVER search transcripts** - causes massive false positives! (e.g., "etel" matches "completely")

**Call Log Files (from Retell export):**
- `C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json` (15,156 records, Aug-Oct 2025)
- `C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json` (6,844 records, Jun-Jul 2025)

**IMPORTANT:** These exports may have gaps. For complete data, query Retell API directly:
```bash
cd /c/Users/peter/Downloads/CC/retell/scripts
python get_calls.py --limit 100 --phone 0412345678
```

### 2.4 Import Command
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python bulk_import_appointments.py
```

### 2.5 Verify Appointment Import

**Before proceeding to bulk import, verify 100% quality:**

```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python -c "
from brevo_api import BrevoClient
client = BrevoClient()

result = client._request('GET', 'contacts/lists/28/contacts', params={'limit': 100})
contacts = result['data'].get('contacts', [])

print('=== APPOINTMENT CONTACTS QUALITY CHECK ===')
missing_name = 0
missing_company = 0
has_recording = 0

for c in contacts:
    attrs = c.get('attributes', {})
    email = c.get('email')
    name = f\"{attrs.get('FIRSTNAME', '')} {attrs.get('LASTNAME', '')}\".strip()
    company = attrs.get('COMPANY', '')
    has_retell = bool(attrs.get('RETELL_LOG'))

    if not name:
        missing_name += 1
        print(f'MISSING NAME: {email}')
    if not company:
        missing_company += 1
        print(f'MISSING COMPANY: {email}')
    if has_retell:
        has_recording += 1

print(f'')
print(f'Total: {len(contacts)}')
print(f'With Name: {len(contacts) - missing_name}')
print(f'With Company: {len(contacts) - missing_company}')
print(f'With Recordings: {has_recording}')
"
```

**Target:** 100% of appointment contacts should have names and companies.

---

## PHASE 3: Import Bulk Contacts (Batched)

### 3.1 Source File
`C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv` (54,086 records)

### 3.2 Fields to Import

From Master_Contacts_With_Flags.csv:
- `phone` - Phone number (primary key for matching)
- `first_name` -> FIRSTNAME
- `last_name` -> LASTNAME
- `email` -> email (required)
- `company` -> COMPANY
- `website` -> (for company enrichment)
- `city`, `state` -> Location info
- `source_list` -> SOURCE
- `was_called` -> determines list assignment
- `call_count` -> NOTES (call history)

**Additional fields to enrich from HubSpot files:**
From All_Contacts_2025_07_07_Cleaned.csv:
- Job Title
- Street Address
- Postal Code
- NeverBounce Validation Result

From All_Companies_2025-07-07_Cleaned_For_HubSpot.csv:
- Google reviews, GBP rating
- Industry, Business type
- Business Description
- Social media links

### 3.3 List Assignment Logic

```python
if was_called:
    lists = [24, 25, 29]  # All + Safe + Previously Called
else:
    lists = [24, 25]  # All + Safe (Fresh leads)
```

### 3.4 Batch Import Command

Import in batches of 100 to monitor quality:

```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python bulk_import_contacts.py --batch-size 100 --offset 0
```

After each batch, verify quality before continuing.

---

## PHASE 4: Create Companies

### 4.1 Data Sources for Companies (Multiple)

**Create companies from ALL these sources:**

1. **Appointment Data** (highest quality - verified real names)
   - `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv` (87 records)
   - Use `company` field directly

2. **HubSpot Companies Export** (verified business data)
   - `C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` (363,516 records)
   - Use `Company name` field
   - Rich data: phone, address, Google reviews, industry

3. **HubSpot Contacts Export** (if company name present)
   - `C:\Users\peter\Documents\HS\All_Contacts_2025_07_07_Cleaned.csv` (207,277 records)
   - Use `Company Name` field

**NEVER create companies from:**
- Personal email domains (gmail.com, hotmail.com, etc.)
- URL-like strings without proper company names
- Domain-only names without additional context (too unreliable)

### 4.2 Personal Domains Blacklist
```python
PERSONAL_DOMAINS = [
    'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
    'bigpond.com', 'bigpond.net.au', 'live.com', 'icloud.com',
    'aol.com', 'msn.com', 'optusnet.com.au', 'hotmail.com.au',
    'yahoo.com.au', 'mail.com'
]
```

### 4.3 Company Name Cleaning
```python
def clean_company_name(name):
    if not name:
        return None

    # Reject URL-like names
    if name.startswith('http') or name.startswith('www.'):
        return None

    # Reject if it's clearly just a domain
    if name.count('.') >= 2 and ' ' not in name:
        return None

    # Clean domain-style names (but only if they look like real names)
    if '.com' in name or '.au' in name:
        name = name.split('/')[0]
        name = name.replace('.com.au', '').replace('.net.au', '')
        name = name.replace('.com', '').replace('.au', '')
        name = name.replace('-', ' ').replace('_', ' ').title()

    return name.strip() if name and len(name) > 2 else None
```

### 4.4 Company Creation Command
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python create_companies_from_appointments.py
```

---

## PHASE 5: Link Contacts to Companies

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

## PHASE 6: Final Verification

### 6.1 Check Counts
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python -c "
from brevo_api import BrevoClient
client = BrevoClient()

# Total contacts
result = client.get_contacts(limit=1)
print(f'Total contacts: {result[\"data\"][\"count\"]}')

# List counts
lists = [(24, 'All'), (25, 'Safe'), (28, 'Appointments'), (29, 'Called')]
for lid, name in lists:
    result = client._request('GET', f'contacts/lists/{lid}')
    count = result['data'].get('totalSubscribers', 0) if result.get('success') else 0
    print(f'{name}: {count}')

# Companies
result = client._request('GET', 'companies', params={'limit': 1})
print(f'Companies: {len(result.get(\"data\", {}).get(\"items\", []))}')
"
```

### 6.2 Expected Results

| Metric | Expected |
|--------|----------|
| Total contacts | ~54,000 |
| Appointment contacts (list 28) | 87 |
| Companies | ~50-100 (from appointments + HubSpot) |
| Contacts with names | 100% of appointments, ~10% of bulk |
| Contacts with recordings | 70%+ of appointments |

---

## SCRIPTS REFERENCE

| Script | Full Path | Purpose |
|--------|-----------|---------|
| `brevo_api.py` | `C:\Users\peter\Downloads\CC\MARKETING\scripts\brevo_api.py` | API wrapper |
| `bulk_import_appointments.py` | `C:\Users\peter\Downloads\CC\MARKETING\scripts\bulk_import_appointments.py` | Import appointments |
| `bulk_import_contacts.py` | `C:\Users\peter\Downloads\CC\MARKETING\scripts\bulk_import_contacts.py` | Import bulk contacts |
| `create_companies_from_appointments.py` | `C:\Users\peter\Downloads\CC\MARKETING\scripts\create_companies_from_appointments.py` | Create companies |
| `delete_all_brevo_data.py` | `C:\Users\peter\Downloads\CC\MARKETING\scripts\delete_all_brevo_data.py` | Wipe all data (emergency only) |

---

## SCRIPTS CHECKLIST

**Before running any import, verify these scripts are correct:**

- [ ] `bulk_import_appointments.py` - Does NOT use transcript search
- [ ] `bulk_import_appointments.py` - Uses phone matching for name enrichment
- [ ] `bulk_import_appointments.py` - Searches large HubSpot files for missing data
- [ ] `bulk_import_contacts.py` - Supports batch-size parameter
- [ ] `create_companies_from_appointments.py` - Uses all data sources (not just appointments)
- [ ] `create_companies_from_appointments.py` - Properly rejects URL-like names

---

## LESSONS LEARNED

### Data Quality Issues (from previous import)

1. **93% of bulk contacts had no name** - This is expected (raw email lists)
2. **48/87 companies had URL-like names** - From using domain as name
3. **Transcript search caused false positives** - "etel" matched "completely"
4. **Name enrichment was incomplete** - Didn't search large HubSpot files

### Rules to Prevent Issues

1. **Names:** Only expect names on appointment contacts; bulk is email-only
2. **Companies:** Use multiple sources, but require real business names
3. **Domains:** Never use personal email domains (gmail, hotmail, etc.)
4. **Call search:** Phone + timestamp ONLY, never transcript
5. **Enrichment:** Search ALL large datasets before flagging for manual review

---

## TROUBLESHOOTING

### Contact shows email as name in Brevo UI
- **Cause:** FIRSTNAME and LASTNAME are empty
- **Fix:** Search large HubSpot files by email AND phone for name

### SMS field conflict error
- **Cause:** Phone number already assigned to another contact
- **Fix:** Add phone to NOTES field instead: "Phone: +61... (shared)"

### Company has gmail.com domain
- **Cause:** Contact uses personal email
- **Fix:** Don't create company for personal emails

### Recordings not found
- **Cause:** Phone number mismatch or call not in export date range
- **Fix:** Query Retell API directly for the specific phone number

---

## QUICK COMMANDS

```bash
# Navigate to scripts
cd /c/Users/peter/Downloads/CC/MARKETING/scripts

# Check Brevo connection
python brevo_api.py

# Get contact details
python -c "from brevo_api import BrevoClient; print(BrevoClient().get_contact('email@example.com'))"

# Delete all data (emergency only - requires confirmation)
python delete_all_brevo_data.py

# Search call logs by phone
python -c "
import json
phone = '412345678'  # Last 9 digits
for f in ['C:/Users/peter/Downloads/CC/CRM/call_log_sheet_export.json', 'C:/Users/peter/Downloads/CC/CRM/call_log_sheet2_export.json']:
    data = json.load(open(f))
    for r in data:
        if phone in r.get('to_number', '') or phone in r.get('from_number', ''):
            print(r.get('start_time'), r.get('recording_url', 'No recording'))
"

# Query Retell API directly for calls
cd /c/Users/peter/Downloads/CC/retell/scripts
python get_calls.py --limit 10 --phone 0412345678
```
