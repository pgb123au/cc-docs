"""
Call Log Linker - Cross-reference phone numbers with Zadarma/Retell recordings.

This tool helps link your called numbers from the telemarketer campaigns
to call recordings in Zadarma CDR exports or Retell API.

Usage:
    python call_log_linker.py --zadarma <zadarma_cdr.csv>
    python call_log_linker.py --retell
    python call_log_linker.py --lookup +61412345678
"""

import os
import sys
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime

# Data files
CALLED_LOG = Path(r'C:\Users\peter\retell-dialer\called_log.txt')
CALLED_JSON = Path(r'C:\Users\peter\retell-dialer\called_numbers.json')
MASSIVE_LIST = Path(r'C:\Users\peter\retell-dialer\massive_list.csv')
VIC_LIST = Path(r'C:\Users\peter\retell-dialer\massive_list_vic.csv')
OUTPUT_DIR = Path(r'C:\Users\peter\Downloads\CC\CRM')


def normalize_phone(phone):
    """Normalize phone to 61XXXXXXXXX format."""
    if not phone:
        return None

    phone = str(phone).strip()
    # Remove all non-digits except leading +
    clean = ''.join(c for c in phone if c.isdigit() or c == '+')
    clean = clean.replace('+', '')

    # Handle Australian formats
    if clean.startswith('0') and len(clean) == 10:
        clean = '61' + clean[1:]
    elif clean.startswith('4') and len(clean) == 9:
        clean = '61' + clean

    if clean.startswith('61') and len(clean) == 11:
        return clean

    return None


def load_called_numbers():
    """Load all called numbers from both log files."""
    called = set()

    # Text log
    if CALLED_LOG.exists():
        with open(CALLED_LOG, 'r') as f:
            for line in f:
                num = normalize_phone(line.strip())
                if num:
                    called.add(num)

    # JSON log
    if CALLED_JSON.exists():
        with open(CALLED_JSON, 'r') as f:
            data = json.load(f)
            for num in data:
                normalized = normalize_phone(num)
                if normalized:
                    called.add(normalized)

    return called


def load_contact_details():
    """Load contact details from massive_list for enrichment."""
    contacts = {}

    for filepath in [MASSIVE_LIST, VIC_LIST]:
        if not filepath.exists():
            continue

        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                phone_raw = row.get('phone_number', '').strip()
                phone = normalize_phone(phone_raw)
                if phone and phone not in contacts:
                    contacts[phone] = {
                        'first_name': row.get('First Name', '').strip(),
                        'last_name': row.get('Last Name', '').strip(),
                        'email': row.get('Email', '').strip(),
                        'company': row.get('Company Name', '').strip(),
                        'website': row.get('Website URL', '').strip(),
                    }

    return contacts


def lookup_number(phone):
    """Look up a single phone number."""
    phone = normalize_phone(phone)
    if not phone:
        print(f"Invalid phone number format")
        return

    called = load_called_numbers()
    contacts = load_contact_details()

    print(f"\n{'='*60}")
    print(f"LOOKUP: {phone} (+{phone})")
    print(f"{'='*60}")

    was_called = phone in called
    print(f"Was called: {'YES' if was_called else 'NO'}")

    if phone in contacts:
        c = contacts[phone]
        print(f"\nContact details:")
        print(f"  Name:    {c['first_name']} {c['last_name']}")
        print(f"  Email:   {c['email']}")
        print(f"  Company: {c['company']}")
        print(f"  Website: {c['website']}")
    else:
        print(f"\nNo contact details found in telemarketer lists")


def link_zadarma_cdr(cdr_file):
    """
    Cross-reference Zadarma CDR export with called numbers.

    Zadarma CDR typically has columns like:
    - Date, Caller ID, Destination, Duration, Recording URL, etc.
    """
    if not Path(cdr_file).exists():
        print(f"File not found: {cdr_file}")
        return

    called = load_called_numbers()
    contacts = load_contact_details()

    print(f"\n{'='*60}")
    print(f"ZADARMA CDR CROSS-REFERENCE")
    print(f"{'='*60}")

    matched = []
    unmatched = []

    with open(cdr_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Try common column names for destination number
            dest = None
            for col in ['Destination', 'destination', 'Called Number', 'called_number', 'To', 'to']:
                if col in row:
                    dest = normalize_phone(row[col])
                    break

            if dest:
                record = {
                    'phone': dest,
                    'raw_row': row,
                    'was_in_our_list': dest in called,
                    'contact': contacts.get(dest, {})
                }

                if record['was_in_our_list']:
                    matched.append(record)
                else:
                    unmatched.append(record)

    print(f"\nTotal CDR records processed: {len(matched) + len(unmatched)}")
    print(f"Matched to our called list: {len(matched)}")
    print(f"Not in our list: {len(unmatched)}")

    # Save matched records with enrichment
    if matched:
        output_file = OUTPUT_DIR / f"zadarma_matched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['phone', 'first_name', 'last_name', 'email', 'company', 'recording_url']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()

            for r in matched:
                row = {
                    'phone': r['phone'],
                    'first_name': r['contact'].get('first_name', ''),
                    'last_name': r['contact'].get('last_name', ''),
                    'email': r['contact'].get('email', ''),
                    'company': r['contact'].get('company', ''),
                    'recording_url': r['raw_row'].get('Recording', r['raw_row'].get('recording_url', '')),
                }
                writer.writerow(row)

        print(f"\nMatched records saved to: {output_file}")


def link_retell_calls():
    """
    Cross-reference Retell call data with called numbers.

    Uses Retell API to get recent calls and match against our called list.
    """
    # Try to use existing Retell scripts
    retell_scripts = Path(r'C:\Users\peter\Downloads\CC\retell\scripts')
    sys.path.insert(0, str(retell_scripts))

    called = load_called_numbers()
    contacts = load_contact_details()

    print(f"\n{'='*60}")
    print(f"RETELL CALL CROSS-REFERENCE")
    print(f"{'='*60}")

    try:
        # Try to get Retell API key
        api_key_file = Path(r'C:\Users\peter\Downloads\Retell_API_Key.txt')
        if not api_key_file.exists():
            print("Retell API key not found")
            return

        import requests

        api_key = api_key_file.read_text().strip()
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Get recent calls
        response = requests.get(
            'https://api.retellai.com/v2/list-calls',
            headers=headers,
            params={'limit': 100}
        )

        if response.status_code != 200:
            print(f"Retell API error: {response.status_code}")
            return

        calls = response.json()
        print(f"Retrieved {len(calls)} recent calls from Retell")

        matched = []
        for call in calls:
            # Extract phone number from call
            to_number = call.get('to_number', '')
            from_number = call.get('from_number', '')

            # Check if either number is in our list
            to_norm = normalize_phone(to_number)
            from_norm = normalize_phone(from_number)

            phone = None
            if to_norm in called:
                phone = to_norm
            elif from_norm in called:
                phone = from_norm

            if phone:
                matched.append({
                    'call_id': call.get('call_id'),
                    'phone': phone,
                    'direction': 'outbound' if to_norm == phone else 'inbound',
                    'duration': call.get('end_timestamp', 0) - call.get('start_timestamp', 0) if call.get('end_timestamp') else 0,
                    'contact': contacts.get(phone, {}),
                    'recording_url': call.get('recording_url'),
                    'transcript': call.get('transcript'),
                })

        print(f"Matched to our telemarketer list: {len(matched)}")

        # Save matched
        if matched:
            output_file = OUTPUT_DIR / f"retell_matched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(matched, f, indent=2)
            print(f"Saved to: {output_file}")

            # Print sample
            print(f"\nSample matches:")
            for m in matched[:5]:
                print(f"  {m['phone']} - {m['contact'].get('company', 'N/A')} - {m['direction']}")

    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description='Cross-reference call logs with recordings')
    parser.add_argument('--zadarma', help='Path to Zadarma CDR export CSV')
    parser.add_argument('--retell', action='store_true', help='Cross-reference with Retell API')
    parser.add_argument('--lookup', help='Look up a specific phone number')
    parser.add_argument('--stats', action='store_true', help='Show statistics')

    args = parser.parse_args()

    if args.lookup:
        lookup_number(args.lookup)
    elif args.zadarma:
        link_zadarma_cdr(args.zadarma)
    elif args.retell:
        link_retell_calls()
    elif args.stats:
        called = load_called_numbers()
        contacts = load_contact_details()

        print(f"\n{'='*60}")
        print(f"CALL LOG STATISTICS")
        print(f"{'='*60}")
        print(f"Total numbers called: {len(called):,}")
        print(f"Contacts with details: {len(contacts):,}")

        # How many called have details
        called_with_details = sum(1 for c in called if c in contacts)
        print(f"Called numbers with contact info: {called_with_details:,}")
    else:
        parser.print_help()
        print("\n\nExamples:")
        print("  python call_log_linker.py --stats")
        print("  python call_log_linker.py --lookup 0412345678")
        print("  python call_log_linker.py --zadarma zadarma_export.csv")
        print("  python call_log_linker.py --retell")


if __name__ == "__main__":
    main()
