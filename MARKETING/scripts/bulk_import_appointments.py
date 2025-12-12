"""
Bulk Import All Appointments to Brevo with Call Recording Search
Following the complete IMPORT_PROCEDURE.md
"""
import csv
import json
import time
import re
import sys
from collections import defaultdict
from brevo_api import BrevoClient

# Encoding fix for Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Personal email domains - NEVER use as company domain
PERSONAL_DOMAINS = [
    'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
    'bigpond.com', 'live.com', 'icloud.com', 'aol.com',
    'msn.com', 'optusnet.com.au', 'hotmail.com.au',
    'yahoo.com.au', 'mail.com', 'bigpond.net.au'
]

def get_company_domain(email):
    """Extract domain only if it's a business domain."""
    if not email or '@' not in email:
        return None
    domain = email.split('@')[1].lower()
    if domain in PERSONAL_DOMAINS:
        return None
    return domain

# Load call logs
print("Loading call logs...")
with open('C:/Users/peter/Downloads/CC/CRM/call_log_sheet_export.json', 'r', encoding='utf-8') as f:
    call_logs_1 = json.load(f)
print(f"  Sheet 1: {len(call_logs_1)} calls (Aug-Oct 2025)")

with open('C:/Users/peter/Downloads/CC/CRM/call_log_sheet2_export.json', 'r', encoding='utf-8') as f:
    call_logs_2 = json.load(f)
print(f"  Sheet 2: {len(call_logs_2)} calls (Jun-Jul 2025)")

all_calls = call_logs_1 + call_logs_2
print(f"  Total: {len(all_calls)} calls")

def clean_phone(phone):
    """Normalize phone number for matching"""
    if not phone:
        return ""
    return re.sub(r'[^\d]', '', str(phone))[-9:]  # Last 9 digits

def find_calls_for_contact(company_name, phone_numbers, timestamp_hint, email=None):
    """
    Search call logs using multiple methods (from IMPORT_PROCEDURE.md)
    Returns list of matching calls
    """
    matches = []
    seen_call_ids = set()

    # Normalize inputs
    company_lower = company_name.lower() if company_name else ""
    clean_phones = [clean_phone(p) for p in phone_numbers if p]

    # Extract date from timestamp hint (format: MM/DD/YYYY or DD/MM/YYYY)
    timestamp_date = ""
    if timestamp_hint:
        # Try to extract date portion
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', str(timestamp_hint))
        if date_match:
            timestamp_date = date_match.group(1)

    for record in all_calls:
        call_id = record.get('call_id', '')
        if call_id in seen_call_ids:
            continue

        matched = False
        match_method = None

        # Method 1: Phone number match
        to_num = clean_phone(record.get('to_number', ''))
        from_num = clean_phone(record.get('from_number', ''))
        for phone in clean_phones:
            if phone and len(phone) >= 8:
                if phone in to_num or phone in from_num:
                    matched = True
                    match_method = 'phone'
                    break

        # Method 2: Company name in transcript (fuzzy - first 4 chars)
        if not matched and company_lower and len(company_lower) >= 4:
            transcript = str(record.get('plain_transcript', '')).lower()
            # Check first 4 chars or full name
            if company_lower[:4] in transcript or company_lower in transcript:
                matched = True
                match_method = 'transcript'

        # Method 3: Timestamp match
        if not matched and timestamp_date:
            start_time = str(record.get('start_time', ''))
            if timestamp_date in start_time:
                matched = True
                match_method = 'timestamp'

        # Method 4: Email domain in transcript (for edge cases)
        if not matched and email and '@' in email:
            domain = email.split('@')[1].split('.')[0].lower()
            if len(domain) >= 4:
                transcript = str(record.get('plain_transcript', '')).lower()
                if domain in transcript:
                    matched = True
                    match_method = 'email_domain'

        if matched and call_id:
            seen_call_ids.add(call_id)
            matches.append({
                'call_id': call_id,
                'start_time': record.get('start_time', ''),
                'to_number': record.get('to_number', ''),
                'from_number': record.get('from_number', ''),
                'recording_url': record.get('recording_url', ''),
                'duration': record.get('human_duration', ''),
                'transcript_preview': str(record.get('plain_transcript', ''))[:100],
                'match_method': match_method
            })

    return matches

def map_deal_stage(status_category, status):
    """Map status to deal stage"""
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

def build_retell_log(calls):
    """Build RETELL_LOG string from calls"""
    if not calls:
        return ""

    entries = []
    for call in calls:
        # Determine direction
        from_num = str(call.get('from_number', ''))
        if '+612' in from_num or '+613' in from_num:  # Our numbers
            direction = 'OUTBOUND'
        else:
            direction = 'INBOUND'

        # Parse timestamp
        start_time = call.get('start_time', '')
        # Format: DD/MM/YYYY, HH:MM:SS
        date_part = start_time.split(',')[0] if ',' in start_time else start_time[:10]
        time_part = start_time.split(',')[1].strip()[:5] if ',' in start_time else ''

        duration = call.get('duration', 'unknown')
        recording_url = call.get('recording_url', '')

        if recording_url:
            entry = f"{date_part} {time_part} {direction} ({duration}) - Recording: {recording_url}"
        else:
            entry = f"{date_part} {time_part} {direction} ({duration}) - No recording"
        entries.append(entry)

    return '\n'.join(entries)

# Initialize Brevo client
client = BrevoClient()

# Load appointments
print("\nLoading appointments...")
appointments = []
with open('C:/Users/peter/Downloads/CC/CRM/Appointments_Enriched.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        # Skip invalid emails
        if not email or '@' not in email or email == 'Davesremovals' or ';' in email:
            continue
        appointments.append(row)

print(f"Found {len(appointments)} valid appointments with emails")

# Process each appointment
results = {
    'updated': [],
    'failed': [],
    'skipped': []
}
recording_counts = {}  # email -> count

print("\nProcessing appointments...")
print("=" * 60)

for i, appt in enumerate(appointments):
    email = appt.get('email', '').strip().lower()
    company = appt.get('company', '').strip()
    name = appt.get('name', '').strip()
    phone = appt.get('phone', '') or appt.get('phone_from_list', '')
    date = appt.get('date', '')
    time_str = appt.get('time', '')
    status = appt.get('status', '')
    status_category = appt.get('status_category', '')
    quality = appt.get('quality', '')
    followup = appt.get('followup', '')
    retell_log_hint = appt.get('retell_log', '')

    # Parse name
    first_name = ''
    last_name = ''
    if name:
        parts = name.split()
        first_name = parts[0] if parts else ''
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

    print(f"\n[{i+1}/{len(appointments)}] {email}")
    print(f"  Company: {company or 'Unknown'}")

    # Search for calls
    phone_numbers = [phone] if phone else []
    calls = find_calls_for_contact(company, phone_numbers, retell_log_hint, email)
    recording_count = len([c for c in calls if c.get('recording_url')])
    recording_counts[email] = recording_count

    print(f"  Calls found: {len(calls)} ({recording_count} with recordings)")

    # Build attributes
    attrs = {
        'SOURCE': 'Telemarketer Campaign'
    }

    if first_name:
        attrs['FIRSTNAME'] = first_name
    if last_name:
        attrs['LASTNAME'] = last_name
    if company:
        attrs['COMPANY'] = company
    if date:
        # Convert date format if needed
        if '/' in date:
            parts = date.split('/')
            if len(parts) == 3:
                date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        attrs['APPOINTMENT_DATE'] = date
    if time_str:
        attrs['APPOINTMENT_TIME'] = time_str
    if status:
        attrs['APPOINTMENT_STATUS'] = status

    attrs['DEAL_STAGE'] = map_deal_stage(status_category, status)

    if quality:
        attrs['QUALITY'] = quality
    if followup:
        attrs['FOLLOWUP_STATUS'] = followup

    # Build RETELL_LOG
    if calls:
        retell_log = build_retell_log(calls)
        if retell_log:
            attrs['RETELL_LOG'] = retell_log

    # Update contact in Brevo
    try:
        result = client.update_contact(email, attrs)
        if result.get('success'):
            print(f"  Updated successfully")
            results['updated'].append({
                'email': email,
                'company': company,
                'recordings': recording_count
            })

            # Add to lists
            client.add_contacts_to_list(24, [email])  # All Telemarketer
            client.add_contacts_to_list(25, [email])  # Safe to Contact
            if date:
                client.add_contacts_to_list(28, [email])  # Had Appointments
        else:
            error = result.get('error', 'Unknown error')
            print(f"  Failed: {error}")
            results['failed'].append({'email': email, 'error': str(error)})
    except Exception as e:
        print(f"  Error: {e}")
        results['failed'].append({'email': email, 'error': str(e)})

    # Rate limit
    time.sleep(0.1)

# Summary
print("\n" + "=" * 60)
print("IMPORT COMPLETE")
print("=" * 60)
print(f"Updated: {len(results['updated'])}")
print(f"Failed: {len(results['failed'])}")

# Find contact with most recordings
print("\n" + "=" * 60)
print("RECORDING COUNTS")
print("=" * 60)

sorted_by_recordings = sorted(recording_counts.items(), key=lambda x: x[1], reverse=True)
print("\nTop 10 contacts by recording count:")
for email, count in sorted_by_recordings[:10]:
    if count > 0:
        # Find company name
        company = next((a['company'] for a in results['updated'] if a['email'] == email), 'Unknown')
        print(f"  {count} recordings: {email} ({company})")

# Winner
if sorted_by_recordings:
    winner_email, winner_count = sorted_by_recordings[0]
    winner_company = next((a['company'] for a in results['updated'] if a['email'] == winner_email), 'Unknown')
    print(f"\nMOST RECORDINGS: {winner_email}")
    print(f"  Company: {winner_company}")
    print(f"  Recording count: {winner_count}")

# Save results
with open('C:/Users/peter/Downloads/CC/MARKETING/scripts/import_results.json', 'w') as f:
    json.dump({
        'updated': results['updated'],
        'failed': results['failed'],
        'recording_counts': dict(sorted_by_recordings)
    }, f, indent=2)

print("\nResults saved to import_results.json")
