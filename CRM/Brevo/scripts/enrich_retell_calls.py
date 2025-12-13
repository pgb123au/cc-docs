"""
Enrich Brevo contacts with full Retell call data.

Reads phone numbers from the original Excel appointments file,
looks up full call details from Retell Call Logs JSON,
and updates Brevo contacts with:
- RETELL_CALL_ID
- RETELL_RECORDING_URL
- RETELL_PUBLIC_LOG_URL
- RETELL_TRANSCRIPT
- RETELL_CALL_DIRECTION
- RETELL_CALL_DURATION
- RETELL_CALL_STATUS
- RETELL_DISCONNECT_REASON
- RETELL_CALL_COST
- RETELL_LOG (enhanced with all call history)

Usage:
    python enrich_retell_calls.py           # Dry run (show what would be updated)
    python enrich_retell_calls.py --update  # Actually update Brevo
"""

import pandas as pd
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Import Brevo client
from brevo_api import BrevoClient

# File paths
EXCEL_FILE = Path(r"C:\Users\peter\Downloads\CC\CRM\temp_appointments.xlsx")
CALL_LOG_1 = Path(r"C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json")
CALL_LOG_2 = Path(r"C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json")

# Our phone numbers (to determine call direction)
OUR_NUMBERS = ['61399997398', '61288800208', '399997398', '288800208']


def load_call_logs():
    """Load all Retell call logs from JSON files."""
    calls = []
    for path in [CALL_LOG_1, CALL_LOG_2]:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                calls.extend(json.load(f))
    print(f"Loaded {len(calls)} calls from logs")
    return calls


def normalize_phone(phone):
    """Normalize phone to last 9 digits for matching."""
    if not phone:
        return ''
    return ''.join(c for c in str(phone) if c.isdigit())[-9:]


def find_calls_for_phone(phone, all_calls):
    """Find all calls matching a phone number (inbound and outbound)."""
    phone_normalized = normalize_phone(phone)
    if len(phone_normalized) < 8:
        return []

    matching_calls = []
    for call in all_calls:
        from_num = normalize_phone(call.get('from_number', ''))
        to_num = normalize_phone(call.get('to_number', ''))

        if phone_normalized in [from_num, to_num]:
            matching_calls.append(call)

    # Sort by start_time (newest first for "last call" logic)
    return sorted(matching_calls, key=lambda x: x.get('start_time', ''), reverse=True)


def extract_contacts_from_excel():
    """
    Extract contacts with phone numbers from the Excel appointments file.
    The Excel has rows as fields (Company, Email, Retell Log1-9, etc.)
    """
    if not EXCEL_FILE.exists():
        print(f"ERROR: Excel file not found: {EXCEL_FILE}")
        print("Please copy the original file first:")
        print('  cp "C:/Users/peter/OneDrive/Documents/Yes Right Pty Ltd/AI Appointments Set 2025.xlsx" temp_appointments.xlsx')
        return []

    df = pd.read_excel(EXCEL_FILE, header=None)

    contacts = []

    for col in range(1, len(df.columns)):
        # Extract basic info (row indices based on Excel structure)
        company = df.iloc[2, col] if pd.notna(df.iloc[2, col]) else None
        email = df.iloc[6, col] if pd.notna(df.iloc[6, col]) else None
        name = df.iloc[19, col] if pd.notna(df.iloc[19, col]) else None

        if not company or str(company).strip() == '':
            continue

        # Look for phone numbers in Retell Log rows (rows 8-18 typically)
        phones_found = []
        for row in range(8, 26):
            cell = df.iloc[row, col] if row < len(df) else None
            if pd.notna(cell):
                cell_str = str(cell)
                # Pattern: 'Phone Call : +61xxx -> +61yyy'
                match = re.search(r'Phone Call\s*:\s*\+?(\d+)\s*->\s*\+?(\d+)', cell_str)
                if match:
                    num1, num2 = match.groups()

                    # Determine direction based on which number is ours
                    num1_norm = normalize_phone(num1)
                    num2_norm = normalize_phone(num2)

                    if any(our in num2_norm for our in OUR_NUMBERS):
                        # num2 is ours, so num1 is theirs (INBOUND call)
                        contact_phone = '+' + num1
                        direction = 'inbound'
                    else:
                        # num1 is ours, so num2 is theirs (OUTBOUND call)
                        contact_phone = '+' + num2
                        direction = 'outbound'

                    if contact_phone not in [p[0] for p in phones_found]:
                        phones_found.append((contact_phone, direction))

        if email and phones_found:
            contacts.append({
                'company': str(company).strip(),
                'email': str(email).strip(),
                'name': str(name).strip() if name else '',
                'phones': phones_found
            })

    print(f"Extracted {len(contacts)} contacts with phone numbers from Excel")
    return contacts


def format_enhanced_retell_log(calls):
    """Format a detailed RETELL_LOG from all calls."""
    if not calls:
        return ''

    log_lines = []
    for call in calls:
        start = call.get('start_time', '')
        duration = call.get('human_duration', 'N/A')
        direction = call.get('direction', 'unknown').upper()
        status = call.get('status', '')
        disconnect = call.get('disconnection_reason', '')

        # Parse date/time
        if ',' in start:
            date_part = start.split(',')[0].strip()
            time_full = start.split(',')[1].strip()
            time_short = ':'.join(time_full.split(':')[:2])
        else:
            date_part = start
            time_short = ''

        log_line = f"{date_part} {time_short} {direction} ({duration})"

        if disconnect and disconnect not in ['user_hangup', 'agent_hangup']:
            log_line += f" [{disconnect}]"

        log_lines.append(log_line)

    return '\n'.join(log_lines)


def build_call_attributes(calls):
    """Build Brevo attributes from call data."""
    if not calls:
        return {}

    # Use the most recent call for "last call" fields
    last_call = calls[0]

    attrs = {}

    # Call ID and URLs
    call_id = last_call.get('call_id', '')
    if call_id:
        attrs['RETELL_CALL_ID'] = call_id

    recording_url = last_call.get('recording_url', '')
    if recording_url and recording_url not in ['N/A', 'None', '']:
        attrs['RETELL_RECORDING_URL'] = recording_url

    public_log_url = last_call.get('public_log_url', '')
    if public_log_url and public_log_url not in ['N/A', 'None', '']:
        attrs['RETELL_PUBLIC_LOG_URL'] = public_log_url

    # Transcript
    transcript = last_call.get('plain_transcript', '')
    if transcript:
        # Brevo has attribute length limits, truncate if needed
        if len(transcript) > 10000:
            transcript = transcript[:9990] + '...[truncated]'
        attrs['RETELL_TRANSCRIPT'] = transcript

    # Call metadata
    direction = last_call.get('direction', '')
    if direction:
        attrs['RETELL_CALL_DIRECTION'] = direction.upper()

    duration = last_call.get('human_duration', '')
    if duration:
        attrs['RETELL_CALL_DURATION'] = duration

    status = last_call.get('status', '')
    if status:
        attrs['RETELL_CALL_STATUS'] = status

    disconnect = last_call.get('disconnection_reason', '')
    if disconnect:
        attrs['RETELL_DISCONNECT_REASON'] = disconnect

    cost = last_call.get('total_cost', 0)
    if cost:
        attrs['RETELL_CALL_COST'] = float(cost)

    # Enhanced log with all calls
    enhanced_log = format_enhanced_retell_log(calls)
    if enhanced_log:
        attrs['RETELL_LOG'] = enhanced_log

    # Was called flag
    attrs['WAS_CALLED'] = True

    # Total call count
    attrs['RETELL_CALL_COUNT'] = len(calls)

    return attrs


def main():
    parser = argparse.ArgumentParser(description='Enrich Brevo contacts with Retell call data')
    parser.add_argument('--update', action='store_true', help='Actually update Brevo (default is dry run)')
    parser.add_argument('--email', type=str, help='Only process a specific email')
    args = parser.parse_args()

    print("=" * 60)
    print("Brevo Retell Call Enrichment")
    print("=" * 60)

    if not args.update:
        print("\n*** DRY RUN MODE - No changes will be made ***")
        print("Use --update to actually update Brevo\n")

    # Load call logs
    all_calls = load_call_logs()

    # Extract contacts from Excel
    contacts = extract_contacts_from_excel()

    if args.email:
        contacts = [c for c in contacts if c['email'].lower() == args.email.lower()]
        if not contacts:
            print(f"No contact found with email: {args.email}")
            return

    # Initialize Brevo client
    client = BrevoClient()

    # Process each contact
    updated = 0
    skipped = 0
    errors = 0

    print(f"\nProcessing {len(contacts)} contacts...")
    print("-" * 60)

    for contact in contacts:
        email = contact['email']
        company = contact['company']
        phones = contact['phones']

        # Find all calls for this contact's phone numbers
        all_contact_calls = []
        for phone, _ in phones:
            calls = find_calls_for_phone(phone, all_calls)
            all_contact_calls.extend(calls)

        # Deduplicate by call_id
        seen_ids = set()
        unique_calls = []
        for call in all_contact_calls:
            cid = call.get('call_id', '')
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                unique_calls.append(call)

        # Sort by time (newest first)
        unique_calls = sorted(unique_calls, key=lambda x: x.get('start_time', ''), reverse=True)

        if not unique_calls:
            print(f"  {company}: No calls found for phones {[p[0] for p in phones]}")
            skipped += 1
            continue

        # Build attributes
        attrs = build_call_attributes(unique_calls)

        print(f"\n{company} ({email}):")
        print(f"  Phones: {[p[0] for p in phones]}")
        print(f"  Calls found: {len(unique_calls)}")
        print(f"  Last call: {unique_calls[0].get('call_id', 'N/A')}")
        print(f"  Recording: {attrs.get('RETELL_RECORDING_URL', 'N/A')[:60]}...")
        print(f"  Direction: {attrs.get('RETELL_CALL_DIRECTION', 'N/A')}")
        print(f"  Duration: {attrs.get('RETELL_CALL_DURATION', 'N/A')}")

        if args.update:
            # Check if contact exists in Brevo
            result = client.get_contact(email)
            if not result.get('success'):
                print(f"  WARNING: Contact not in Brevo, skipping")
                skipped += 1
                continue

            # Update contact
            result = client.update_contact(email, attrs)
            if result.get('success'):
                print(f"  UPDATED in Brevo with {len(attrs)} attributes")
                updated += 1
            else:
                print(f"  ERROR: {result.get('error', 'Unknown error')}")
                errors += 1
        else:
            print(f"  [DRY RUN] Would update with {len(attrs)} attributes")
            updated += 1

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total contacts processed: {len(contacts)}")
    print(f"Updated: {updated}")
    print(f"Skipped (no calls): {skipped}")
    print(f"Errors: {errors}")

    if not args.update:
        print("\n*** This was a DRY RUN - no changes were made ***")
        print("Run with --update to actually update Brevo")


if __name__ == "__main__":
    main()
