"""
Test Import: 200 Contacts + 200 Companies
Includes all 82 appointment contacts + 118 from Master
All flagged with IMPORT_BATCH for later full import
"""
import csv
import json
import time
import re
import sys
from datetime import datetime
from brevo_api import BrevoClient

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

IMPORT_BATCH = "test_2025-12-13"

# Personal email domains - never use as company domain
PERSONAL_DOMAINS = [
    'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
    'bigpond.com', 'live.com', 'icloud.com', 'aol.com',
    'msn.com', 'optusnet.com.au', 'hotmail.com.au',
    'yahoo.com.au', 'mail.com', 'bigpond.net.au'
]

def clean_phone(phone):
    """Normalize phone number for matching - last 9 digits."""
    if not phone:
        return ""
    return re.sub(r'[^\d]', '', str(phone))[-9:]

def format_phone(phone):
    """Format phone to +61 format."""
    if not phone:
        return None
    digits = re.sub(r'[^\d]', '', str(phone))
    if len(digits) == 9 and digits.startswith('4'):
        return f"+61{digits}"
    if len(digits) == 10 and digits.startswith('0'):
        return f"+61{digits[1:]}"
    if len(digits) == 11 and digits.startswith('61'):
        return f"+{digits}"
    if digits.startswith('614') and len(digits) == 11:
        return f"+{digits}"
    return None

def get_company_domain(email):
    """Extract domain only if it's a business domain."""
    if not email or '@' not in email:
        return None
    domain = email.split('@')[1].lower()
    if domain in PERSONAL_DOMAINS:
        return None
    return domain

def map_deal_stage(status_category, status):
    """Map status to deal stage."""
    status_lower = str(status).lower() if status else ""
    cat_lower = str(status_category).lower() if status_category else ""

    if 'won' in cat_lower or 'client' in status_lower:
        return 'Won'
    if 'followup' in cat_lower or 'fu' in status_lower or 'negotiation' in status_lower:
        return 'Negotiation'
    if 'booked' in cat_lower or 'qualified' in cat_lower:
        return 'Qualified Lead'
    if 'contacted' in cat_lower or 'new' in cat_lower:
        return 'New Lead'
    if 'no_show' in cat_lower or 'dead' in cat_lower or 'bad_prospect' in cat_lower:
        return 'Lost'
    return 'New Lead'

# Load HubSpot contacts for enrichment (indexed by email)
print("Loading HubSpot contacts for enrichment...")
hubspot_by_email = {}
hubspot_by_phone = {}
try:
    with open('C:/Users/peter/Documents/HS/All_Contacts_2025_07_07_Cleaned.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            email = row.get('Email', '').strip().lower()
            if email and '@' in email:
                hubspot_by_email[email] = row
            # Index by phone too
            for phone_field in ['Phone Number 1', 'Mobile Phone Number', 'Mobile Phone 2']:
                phone = clean_phone(row.get(phone_field, ''))
                if phone and len(phone) >= 8:
                    hubspot_by_phone[phone] = row
            count += 1
            if count % 50000 == 0:
                print(f"  Loaded {count} HubSpot contacts...")
    print(f"  Loaded {len(hubspot_by_email)} by email, {len(hubspot_by_phone)} by phone")
except Exception as e:
    print(f"  Warning: Could not load HubSpot contacts: {e}")

# Load HubSpot companies for enrichment (indexed by domain)
print("\nLoading HubSpot companies for enrichment...")
hubspot_companies = {}
try:
    with open('C:/Users/peter/Documents/HS/All_Companies_2025-07-07_Cleaned_For_HubSpot.csv', 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            domain = row.get('Domain', '').strip().lower()
            if domain:
                hubspot_companies[domain] = row
            # Also index by company name
            name = row.get('Company name', '').strip().lower()
            if name:
                hubspot_companies[f"name:{name}"] = row
            count += 1
            if count % 100000 == 0:
                print(f"  Loaded {count} HubSpot companies...")
    print(f"  Loaded {len(hubspot_companies)} companies")
except Exception as e:
    print(f"  Warning: Could not load HubSpot companies: {e}")

# Load call logs
print("\nLoading call logs...")
all_calls = []
try:
    with open('C:/Users/peter/Downloads/CC/CRM/call_log_sheet_export.json', 'r', encoding='utf-8') as f:
        all_calls.extend(json.load(f))
    with open('C:/Users/peter/Downloads/CC/CRM/call_log_sheet2_export.json', 'r', encoding='utf-8') as f:
        all_calls.extend(json.load(f))
    print(f"  Loaded {len(all_calls)} calls")
except Exception as e:
    print(f"  Warning: Could not load call logs: {e}")

# Index calls by phone
calls_by_phone = {}
for call in all_calls:
    to_num = clean_phone(call.get('to_number', ''))
    from_num = clean_phone(call.get('from_number', ''))
    if to_num:
        if to_num not in calls_by_phone:
            calls_by_phone[to_num] = []
        calls_by_phone[to_num].append(call)
    if from_num and from_num != to_num:
        if from_num not in calls_by_phone:
            calls_by_phone[from_num] = []
        calls_by_phone[from_num].append(call)
print(f"  Indexed {len(calls_by_phone)} unique phone numbers")

def build_retell_log(phone):
    """Build RETELL_LOG string from calls for a phone number."""
    phone_clean = clean_phone(phone)
    if not phone_clean or phone_clean not in calls_by_phone:
        return ""

    calls = calls_by_phone[phone_clean]
    entries = []
    seen_ids = set()

    for call in sorted(calls, key=lambda x: x.get('start_time', ''), reverse=True)[:10]:  # Last 10 calls
        call_id = call.get('call_id', '')
        if call_id in seen_ids:
            continue
        seen_ids.add(call_id)

        from_num = str(call.get('from_number', ''))
        if '+612' in from_num or '+613' in from_num:
            direction = 'OUTBOUND'
        else:
            direction = 'INBOUND'

        start_time = call.get('start_time', '')
        date_part = start_time.split(',')[0] if ',' in start_time else start_time[:10]
        time_part = start_time.split(',')[1].strip()[:5] if ',' in start_time else ''
        duration = call.get('human_duration', 'unknown')
        recording_url = call.get('recording_url', '')

        if recording_url:
            entry = f"{date_part} {time_part} {direction} ({duration}) - Recording: {recording_url}"
        else:
            entry = f"{date_part} {time_part} {direction} ({duration}) - No recording"
        entries.append(entry)

    return '\n'.join(entries)

def enrich_from_hubspot(email, phone):
    """Get enrichment data from HubSpot."""
    email_lower = email.strip().lower() if email else ''
    phone_clean = clean_phone(phone) if phone else ''

    hs_contact = None
    if email_lower in hubspot_by_email:
        hs_contact = hubspot_by_email[email_lower]
    elif phone_clean in hubspot_by_phone:
        hs_contact = hubspot_by_phone[phone_clean]

    if not hs_contact:
        return {}

    enrichment = {}

    # Names
    if hs_contact.get('First Name'):
        enrichment['FIRSTNAME'] = hs_contact['First Name'].strip()
    if hs_contact.get('Last Name'):
        enrichment['LASTNAME'] = hs_contact['Last Name'].strip()

    # Company
    if hs_contact.get('Company Name'):
        enrichment['COMPANY'] = hs_contact['Company Name'].strip()

    # Phones
    if hs_contact.get('Mobile Phone Number'):
        enrichment['PHONE_2'] = format_phone(hs_contact['Mobile Phone Number'])
    if hs_contact.get('Mobile Phone 2'):
        enrichment['PHONE_3'] = format_phone(hs_contact['Mobile Phone 2'])

    # Location
    if hs_contact.get('Street Address'):
        enrichment['STREET_ADDRESS'] = hs_contact['Street Address'].strip()
    if hs_contact.get('City'):
        enrichment['CITY'] = hs_contact['City'].strip()
    if hs_contact.get('State/Region'):
        enrichment['STATE_REGION'] = hs_contact['State/Region'].strip()
    if hs_contact.get('Postal Code'):
        enrichment['POSTAL_CODE'] = hs_contact['Postal Code'].strip()
    if hs_contact.get('Country'):
        enrichment['COUNTRY'] = hs_contact['Country'].strip()

    # Professional
    if hs_contact.get('Job Title'):
        enrichment['JOB_TITLE'] = hs_contact['Job Title'].strip()
    if hs_contact.get('Website URL'):
        enrichment['WEBSITE'] = hs_contact['Website URL'].strip()

    # Email quality
    if hs_contact.get('Email Validation'):
        enrichment['EMAIL_VALIDATION'] = hs_contact['Email Validation'].strip()
    if hs_contact.get('NeverBounce Validation Result'):
        enrichment['NEVERBOUNCE_RESULT'] = hs_contact['NeverBounce Validation Result'].strip()

    # Lead info
    if hs_contact.get('Biz- Lead Source'):
        enrichment['LEAD_SOURCE'] = hs_contact['Biz- Lead Source'].strip()
    if hs_contact.get('Biz- lead Status'):
        enrichment['LEAD_STATUS'] = hs_contact['Biz- lead Status'].strip()
    if hs_contact.get('Biz- Lead Type'):
        enrichment['LEAD_TYPE'] = hs_contact['Biz- Lead Type'].strip()
    if hs_contact.get('Biz- Tag'):
        enrichment['TAGS'] = hs_contact['Biz- Tag'].strip()

    # Social
    if hs_contact.get('Twitter Profile'):
        enrichment['TWITTER'] = hs_contact['Twitter Profile'].strip()

    # Build JSON metadata blob
    meta = {}
    for field in ['Legacy  Record ID', 'Biz - Associated Company IDs', 'Biz- Contact owner',
                  'Biz- Create Date-Time', 'Biz- Original Source', 'Biz- Original Source Drill-Down 1']:
        if hs_contact.get(field):
            meta[field] = hs_contact[field]
    if meta:
        enrichment['HUBSPOT_CONTACT_META'] = json.dumps(meta)

    return enrichment

def enrich_company_from_hubspot(company_name, domain):
    """Get company enrichment from HubSpot companies."""
    company_key = f"name:{company_name.lower()}" if company_name else None

    hs_company = None
    if domain and domain in hubspot_companies:
        hs_company = hubspot_companies[domain]
    elif company_key and company_key in hubspot_companies:
        hs_company = hubspot_companies[company_key]

    if not hs_company:
        return {}

    enrichment = {}

    # Basic info
    if hs_company.get('Phone Number'):
        enrichment['phone_number'] = hs_company['Phone Number']
    if hs_company.get('Industry'):
        enrichment['industry'] = hs_company['Industry']
    if hs_company.get('Number of Employees'):
        enrichment['number_of_employees'] = hs_company['Number of Employees']
    if hs_company.get('Annual Revenue'):
        enrichment['revenue'] = hs_company['Annual Revenue']
    if hs_company.get('Description'):
        enrichment['description'] = hs_company['Description'][:500]  # Limit length

    return enrichment

# Initialize Brevo client
client = BrevoClient()

# ============================================================
# PHASE 1: Load and process appointments
# ============================================================
print("\n" + "=" * 60)
print("PHASE 1: LOADING APPOINTMENTS")
print("=" * 60)

appointments = []
with open('C:/Users/peter/Downloads/CC/CRM/Appointments_Enriched.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        if email and '@' in email and ';' not in email:
            appointments.append(row)

print(f"Loaded {len(appointments)} valid appointment contacts")

# ============================================================
# PHASE 2: Load Master contacts (for remaining 118)
# ============================================================
print("\n" + "=" * 60)
print("PHASE 2: LOADING MASTER CONTACTS")
print("=" * 60)

# Get appointment emails to exclude
appointment_emails = {a['email'].strip().lower() for a in appointments}

master_contacts = []
with open('C:/Users/peter/Downloads/CC/CRM/Master_Contacts_With_Flags.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip().lower()
        if email and '@' in email and email not in appointment_emails:
            master_contacts.append(row)
            if len(master_contacts) >= 118:  # Need 118 to reach 200 total
                break

print(f"Loaded {len(master_contacts)} additional Master contacts")

# ============================================================
# PHASE 3: Import contacts to Brevo
# ============================================================
print("\n" + "=" * 60)
print("PHASE 3: IMPORTING CONTACTS TO BREVO")
print("=" * 60)

results = {
    'appointment_success': 0,
    'appointment_failed': 0,
    'master_success': 0,
    'master_failed': 0,
    'errors': []
}

# 3A: Import appointment contacts
print("\n--- Importing Appointment Contacts ---")
for i, appt in enumerate(appointments):
    email = appt.get('email', '').strip().lower()
    company = appt.get('company', '').strip()
    name = appt.get('name', '').strip()
    phone = appt.get('phone', '') or appt.get('phone_from_list', '')

    # Parse name
    first_name = ''
    last_name = ''
    if name and name not in ['.', '∙', '-']:
        parts = name.split()
        first_name = parts[0] if parts else ''
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

    # Build attributes
    attrs = {
        'IMPORT_BATCH': IMPORT_BATCH,
        'SOURCE': 'Appointment - ' + appt.get('source_sheet', 'Unknown'),
    }

    if first_name:
        attrs['FIRSTNAME'] = first_name
    if last_name:
        attrs['LASTNAME'] = last_name
    if company:
        attrs['COMPANY'] = company
    if phone:
        formatted = format_phone(phone)
        if formatted:
            attrs['SMS'] = formatted

    # Appointment-specific fields
    if appt.get('date'):
        attrs['APPOINTMENT_DATE'] = appt['date']
    if appt.get('time'):
        attrs['APPOINTMENT_TIME'] = appt['time']
    if appt.get('status'):
        attrs['APPOINTMENT_STATUS'] = appt['status']
    if appt.get('status_category'):
        attrs['DEAL_STAGE'] = map_deal_stage(appt.get('status_category'), appt.get('status'))
    if appt.get('quality'):
        attrs['QUALITY'] = appt['quality']
    if appt.get('followup'):
        attrs['FOLLOWUP_STATUS'] = appt['followup']

    # Was called flag
    attrs['WAS_CALLED'] = True if appt.get('was_called', '').lower() == 'true' else False

    # Enrich from HubSpot
    hs_enrichment = enrich_from_hubspot(email, phone)
    for key, value in hs_enrichment.items():
        if value and key not in attrs:  # Don't overwrite appointment data
            attrs[key] = value

    # Add call log
    retell_log = build_retell_log(phone)
    if retell_log:
        attrs['RETELL_LOG'] = retell_log
        attrs['WAS_CALLED'] = True

    # Company domain
    domain = get_company_domain(email)
    if domain:
        attrs['COMPANY_DOMAIN'] = domain

    # Import to Brevo
    try:
        result = client.add_contact(email, attrs, list_ids=[24, 25, 28])  # All + Safe + Appointments
        if result.get('success'):
            results['appointment_success'] += 1
            print(f"  [{i+1}/{len(appointments)}] OK: {email}")
        else:
            results['appointment_failed'] += 1
            results['errors'].append({'email': email, 'error': result.get('error')})
            print(f"  [{i+1}/{len(appointments)}] FAIL: {email} - {result.get('error')}")
    except Exception as e:
        results['appointment_failed'] += 1
        results['errors'].append({'email': email, 'error': str(e)})
        print(f"  [{i+1}/{len(appointments)}] ERROR: {email} - {e}")

    time.sleep(0.1)

# 3B: Import Master contacts
print("\n--- Importing Master Contacts ---")
for i, contact in enumerate(master_contacts):
    email = contact.get('email', '').strip().lower()

    attrs = {
        'IMPORT_BATCH': IMPORT_BATCH,
        'SOURCE': 'Master - ' + contact.get('source_list', 'Unknown'),
    }

    if contact.get('first_name'):
        attrs['FIRSTNAME'] = contact['first_name'].strip()
    if contact.get('last_name'):
        attrs['LASTNAME'] = contact['last_name'].strip()
    if contact.get('company'):
        attrs['COMPANY'] = contact['company'].strip()
    if contact.get('website'):
        attrs['WEBSITE'] = contact['website'].strip()
    if contact.get('city'):
        attrs['CITY'] = contact['city'].strip()
    if contact.get('state'):
        attrs['STATE_REGION'] = contact['state'].strip()
    if contact.get('source_list'):
        attrs['SOURCE_LIST'] = contact['source_list'].strip()

    phone = contact.get('phone', '')
    if phone:
        formatted = format_phone(phone)
        if formatted:
            attrs['SMS'] = formatted

    # Was called and call count
    attrs['WAS_CALLED'] = contact.get('was_called', '').lower() == 'true'
    if contact.get('call_count'):
        try:
            attrs['CALL_COUNT'] = int(contact['call_count'])
        except:
            pass

    # Enrich from HubSpot
    hs_enrichment = enrich_from_hubspot(email, phone)
    for key, value in hs_enrichment.items():
        if value and key not in attrs:
            attrs[key] = value

    # Add call log
    retell_log = build_retell_log(phone)
    if retell_log:
        attrs['RETELL_LOG'] = retell_log
        attrs['WAS_CALLED'] = True

    # Company domain
    domain = get_company_domain(email)
    if domain:
        attrs['COMPANY_DOMAIN'] = domain

    # Determine lists
    list_ids = [24, 25]  # All + Safe
    if attrs.get('WAS_CALLED'):
        list_ids.append(29)  # Previously Called

    # Import to Brevo
    try:
        result = client.add_contact(email, attrs, list_ids=list_ids)
        if result.get('success'):
            results['master_success'] += 1
            print(f"  [{i+1}/{len(master_contacts)}] OK: {email}")
        else:
            results['master_failed'] += 1
            results['errors'].append({'email': email, 'error': result.get('error')})
            print(f"  [{i+1}/{len(master_contacts)}] FAIL: {email} - {result.get('error')}")
    except Exception as e:
        results['master_failed'] += 1
        results['errors'].append({'email': email, 'error': str(e)})
        print(f"  [{i+1}/{len(master_contacts)}] ERROR: {email} - {e}")

    time.sleep(0.1)

# ============================================================
# PHASE 4: Create Companies
# ============================================================
print("\n" + "=" * 60)
print("PHASE 4: CREATING COMPANIES")
print("=" * 60)

# Collect unique companies from appointments + master
companies_to_create = {}

# From appointments (priority)
for appt in appointments:
    company = appt.get('company', '').strip()
    email = appt.get('email', '').strip().lower()
    if company and len(company) > 2:
        domain = get_company_domain(email)
        key = company.lower()
        if key not in companies_to_create:
            companies_to_create[key] = {
                'name': company,
                'domain': domain,
                'source': 'appointment',
                'emails': [email]
            }
        else:
            companies_to_create[key]['emails'].append(email)

# From master contacts (fill up to 200)
for contact in master_contacts:
    if len(companies_to_create) >= 200:
        break
    company = contact.get('company', '').strip()
    email = contact.get('email', '').strip().lower()
    if company and len(company) > 2:
        domain = get_company_domain(email)
        key = company.lower()
        if key not in companies_to_create:
            companies_to_create[key] = {
                'name': company,
                'domain': domain,
                'source': 'master',
                'emails': [email]
            }
        else:
            companies_to_create[key]['emails'].append(email)

print(f"Found {len(companies_to_create)} unique companies")

# Create companies in Brevo
company_results = {'success': 0, 'failed': 0}
company_id_map = {}  # name -> id

for i, (key, company_data) in enumerate(list(companies_to_create.items())[:200]):
    name = company_data['name']
    domain = company_data['domain']

    # Build company attributes
    company_attrs = {
        'name': name,
    }
    if domain:
        company_attrs['domain'] = domain

    # Enrich from HubSpot
    hs_enrichment = enrich_company_from_hubspot(name, domain)
    company_attrs.update(hs_enrichment)

    # Create via API
    try:
        result = client._request('POST', 'companies', {'name': name, 'attributes': company_attrs})
        if result.get('success'):
            company_results['success'] += 1
            company_id = result['data'].get('id')
            company_id_map[key] = company_id
            print(f"  [{i+1}] OK: {name} (ID: {company_id})")
        else:
            company_results['failed'] += 1
            print(f"  [{i+1}] FAIL: {name} - {result.get('error')}")
    except Exception as e:
        company_results['failed'] += 1
        print(f"  [{i+1}] ERROR: {name} - {e}")

    time.sleep(0.1)

# ============================================================
# PHASE 5: Link Contacts to Companies
# ============================================================
print("\n" + "=" * 60)
print("PHASE 5: LINKING CONTACTS TO COMPANIES")
print("=" * 60)

link_results = {'success': 0, 'failed': 0}

for key, company_data in companies_to_create.items():
    if key not in company_id_map:
        continue

    company_id = company_id_map[key]
    emails = company_data['emails'][:10]  # Limit to first 10

    # Get contact IDs
    contact_ids = []
    for email in emails:
        result = client.get_contact(email)
        if result.get('success'):
            contact_ids.append(result['data']['id'])

    if contact_ids:
        try:
            result = client._request('PATCH', f'companies/link-unlink/{company_id}', {
                'linkContactIds': contact_ids
            })
            if result.get('success'):
                link_results['success'] += 1
                print(f"  Linked {len(contact_ids)} contacts to {company_data['name']}")
            else:
                link_results['failed'] += 1
        except Exception as e:
            link_results['failed'] += 1

    time.sleep(0.05)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("IMPORT SUMMARY")
print("=" * 60)

print(f"\nContacts:")
print(f"  Appointments: {results['appointment_success']} success, {results['appointment_failed']} failed")
print(f"  Master: {results['master_success']} success, {results['master_failed']} failed")
print(f"  TOTAL: {results['appointment_success'] + results['master_success']} contacts imported")

print(f"\nCompanies:")
print(f"  Created: {company_results['success']}")
print(f"  Failed: {company_results['failed']}")

print(f"\nLinks:")
print(f"  Successful company-contact links: {link_results['success']}")

print(f"\nAll records flagged with IMPORT_BATCH = '{IMPORT_BATCH}'")

# Verify in Brevo
print("\n" + "=" * 60)
print("BREVO VERIFICATION")
print("=" * 60)

result = client.get_contacts(limit=1)
print(f"Total contacts in Brevo: {result['data'].get('count', 0) if result.get('success') else 'Error'}")

for lid, name in [(24, 'All Telemarketer'), (25, 'Safe to Contact'), (28, 'Had Appointments'), (29, 'Previously Called')]:
    result = client._request('GET', f'contacts/lists/{lid}')
    count = result['data'].get('totalSubscribers', 0) if result.get('success') else 0
    print(f"  List {lid} ({name}): {count}")

result = client._request('GET', 'companies', params={'limit': 1})
if result.get('success'):
    # The companies endpoint returns items directly
    print(f"Total companies in Brevo: Check in UI (API doesn't return count)")

# Save results
with open('C:/Users/peter/Downloads/CC/MARKETING/scripts/test_import_results.json', 'w') as f:
    json.dump({
        'import_batch': IMPORT_BATCH,
        'contacts': {
            'appointments': results['appointment_success'],
            'master': results['master_success'],
            'total': results['appointment_success'] + results['master_success']
        },
        'companies': company_results['success'],
        'errors': results['errors'][:20]  # First 20 errors
    }, f, indent=2)

print(f"\nResults saved to test_import_results.json")
