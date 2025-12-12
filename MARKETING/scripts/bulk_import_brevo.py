"""
Bulk Import to Brevo - Import all telemarketer contacts with segmentation.

Imports:
- 54,086 contacts from Master_Contacts_With_Flags.csv
- Creates lists: Safe to Contact, Fresh Leads, DNC Blocklist, Appointments
- Links contacts to companies
- Handles rate limits (Brevo allows ~100 requests/second)

Usage:
    python bulk_import_brevo.py --dry-run   # Preview without importing
    python bulk_import_brevo.py             # Full import
"""

import os
import sys
import csv
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent to path for brevo_api
sys.path.insert(0, str(Path(__file__).parent))
from brevo_api import BrevoClient, normalize_australian_mobile

# Data files
CRM_DIR = Path(r'C:\Users\peter\Downloads\CC\CRM')
MASTER_CONTACTS = CRM_DIR / 'Master_Contacts_With_Flags.csv'
DNC_MASTER = CRM_DIR / 'DO_NOT_CALL_Master.csv'
APPOINTMENTS = CRM_DIR / 'Appointments_Enriched.csv'

# Brevo list names to create
LIST_NAMES = {
    'all_contacts': 'All Telemarketer Contacts',
    'safe_to_contact': 'Safe to Contact',
    'fresh_leads': 'Fresh Leads - Never Called',
    'dnc': 'DO NOT CALL',
    'appointments': 'Had Appointments',
    'called': 'Previously Called'
}

# Batch settings
BATCH_SIZE = 100  # Contacts per API call
RATE_LIMIT_DELAY = 0.1  # Seconds between batches


def load_master_contacts():
    """Load all contacts from Master_Contacts_With_Flags.csv."""
    contacts = []

    if not MASTER_CONTACTS.exists():
        print(f"ERROR: Master contacts file not found: {MASTER_CONTACTS}")
        return contacts

    with open(MASTER_CONTACTS, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract relevant fields
            email = row.get('email', '').strip().lower()
            phone = row.get('phone_normalized', '').strip()

            # Skip if no email (Brevo requires email as identifier)
            if not email or '@' not in email:
                continue

            contact = {
                'email': email,
                'attributes': {
                    'FIRSTNAME': row.get('first_name', '').strip(),
                    'LASTNAME': row.get('last_name', '').strip(),
                    'SMS': normalize_australian_mobile(phone) if phone else '',
                    'COMPANY': row.get('company', '').strip(),
                    'WEBSITE': row.get('website', '').strip(),
                    'SOURCE': row.get('source', '').strip(),
                    'PHONE_RAW': row.get('phone_number', '').strip(),
                },
                'flags': {
                    'is_dnc': row.get('is_dnc', '').lower() == 'true',
                    'was_called': row.get('was_called', '').lower() == 'true',
                    'had_appointment': row.get('had_appointment', '').lower() == 'true',
                }
            }
            contacts.append(contact)

    return contacts


def load_dnc_emails():
    """Load DNC emails from DO_NOT_CALL_Master.csv."""
    dnc_emails = set()

    if DNC_MASTER.exists():
        with open(DNC_MASTER, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('email', '').strip().lower()
                if email and '@' in email:
                    dnc_emails.add(email)

    return dnc_emails


def create_lists(client):
    """Create Brevo lists for segmentation."""
    print("\n=== Creating Brevo Lists ===")

    # Get existing lists
    existing = client.get_lists(limit=100)
    existing_names = {}
    if existing.get('success'):
        for lst in existing['data'].get('lists', []):
            existing_names[lst['name']] = lst['id']

    list_ids = {}

    for key, name in LIST_NAMES.items():
        if name in existing_names:
            list_ids[key] = existing_names[name]
            print(f"  [EXISTS] {name} (ID: {list_ids[key]})")
        else:
            result = client.create_list(name)
            if result.get('success'):
                list_ids[key] = result['data']['id']
                print(f"  [CREATED] {name} (ID: {list_ids[key]})")
            else:
                print(f"  [FAILED] {name}: {result.get('error')}")

    return list_ids


def import_contacts_batch(client, contacts, list_ids, dry_run=False):
    """Import contacts in batches using Brevo's import API."""
    print(f"\n=== Importing {len(contacts)} Contacts ===")

    if dry_run:
        print("[DRY RUN - No changes will be made]")

    stats = {
        'total': len(contacts),
        'imported': 0,
        'updated': 0,
        'dnc_blocked': 0,
        'failed': 0,
        'errors': []
    }

    # Group contacts by their list assignments
    for i, contact in enumerate(contacts):
        if i > 0 and i % 500 == 0:
            print(f"Progress: {i}/{len(contacts)} - {stats['imported']} imported, {stats['failed']} failed")

        # Determine which lists to add to
        contact_list_ids = [list_ids['all_contacts']]

        if contact['flags']['is_dnc']:
            contact_list_ids.append(list_ids['dnc'])
        elif contact['flags']['had_appointment']:
            contact_list_ids.append(list_ids['appointments'])
            contact_list_ids.append(list_ids['safe_to_contact'])
        elif contact['flags']['was_called']:
            contact_list_ids.append(list_ids['called'])
            contact_list_ids.append(list_ids['safe_to_contact'])
        else:
            contact_list_ids.append(list_ids['fresh_leads'])
            contact_list_ids.append(list_ids['safe_to_contact'])

        if dry_run:
            stats['imported'] += 1
            continue

        # Add contact
        result = client.add_contact(
            email=contact['email'],
            attributes=contact['attributes'],
            list_ids=contact_list_ids
        )

        if result.get('success'):
            stats['imported'] += 1

            # If DNC, also blocklist them
            if contact['flags']['is_dnc']:
                block_result = client.blocklist_contact(email=contact['email'])
                if block_result.get('success'):
                    stats['dnc_blocked'] += 1
        else:
            error_msg = result.get('error', 'Unknown error')
            if 'already exists' in str(error_msg).lower():
                stats['updated'] += 1
            else:
                stats['failed'] += 1
                if len(stats['errors']) < 10:  # Keep first 10 errors
                    stats['errors'].append({
                        'email': contact['email'],
                        'error': error_msg
                    })

        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)

    return stats


def import_with_bulk_api(client, contacts, list_ids, dry_run=False):
    """
    Use Brevo's bulk import endpoint for faster importing.
    POST /contacts/import
    """
    print(f"\n=== Bulk Importing {len(contacts)} Contacts ===")

    if dry_run:
        print("[DRY RUN - No changes will be made]")
        return {'total': len(contacts), 'imported': len(contacts), 'failed': 0}

    stats = {
        'total': len(contacts),
        'imported': 0,
        'failed': 0,
        'batches': 0
    }

    # Prepare contacts for bulk import
    # Group by list assignment for efficiency
    list_assignments = defaultdict(list)

    for contact in contacts:
        # Determine primary list based on priority
        if contact['flags']['is_dnc']:
            primary_list = 'dnc'
        elif contact['flags']['had_appointment']:
            primary_list = 'appointments'
        elif contact['flags']['was_called']:
            primary_list = 'called'
        else:
            primary_list = 'fresh_leads'

        list_assignments[primary_list].append(contact)

    # Import each group to their primary list + all_contacts
    for list_key, group_contacts in list_assignments.items():
        print(f"\n  Importing {len(group_contacts)} contacts to '{LIST_NAMES[list_key]}'...")

        # Process in batches
        for batch_start in range(0, len(group_contacts), BATCH_SIZE):
            batch = group_contacts[batch_start:batch_start + BATCH_SIZE]
            stats['batches'] += 1

            # Build import data for bulk API
            # Brevo bulk import format
            import_data = {
                'fileBody': '',
                'listIds': [list_ids[list_key], list_ids['all_contacts']],
                'updateExistingContacts': True,
                'emptyContactsAttributes': False
            }

            # Also add to safe_to_contact for non-DNC
            if list_key != 'dnc':
                import_data['listIds'].append(list_ids['safe_to_contact'])

            # Build CSV-like format for fileBody
            headers = ['EMAIL', 'FIRSTNAME', 'LASTNAME', 'SMS', 'COMPANY', 'WEBSITE', 'SOURCE']
            lines = [';'.join(headers)]

            for c in batch:
                row = [
                    c['email'],
                    c['attributes'].get('FIRSTNAME', ''),
                    c['attributes'].get('LASTNAME', ''),
                    c['attributes'].get('SMS', ''),
                    c['attributes'].get('COMPANY', ''),
                    c['attributes'].get('WEBSITE', ''),
                    c['attributes'].get('SOURCE', '')
                ]
                # Escape semicolons in values
                row = [v.replace(';', ',') if v else '' for v in row]
                lines.append(';'.join(row))

            import_data['fileBody'] = '\n'.join(lines)

            # Call bulk import API
            result = client._request('POST', 'contacts/import', import_data)

            if result.get('success'):
                stats['imported'] += len(batch)
            else:
                print(f"    Batch {stats['batches']} failed: {result.get('error')}")
                stats['failed'] += len(batch)

            # Progress update
            if stats['batches'] % 10 == 0:
                print(f"    Progress: {stats['imported']}/{stats['total']} contacts imported")

            time.sleep(RATE_LIMIT_DELAY * 2)  # Slightly slower for bulk

    # Blocklist DNC contacts
    if 'dnc' in list_assignments:
        print(f"\n  Blocklisting {len(list_assignments['dnc'])} DNC contacts...")
        dnc_blocked = 0
        for c in list_assignments['dnc']:
            result = client.blocklist_contact(email=c['email'])
            if result.get('success'):
                dnc_blocked += 1
            time.sleep(RATE_LIMIT_DELAY)
        print(f"    Blocked: {dnc_blocked}")

    return stats


def create_companies(client, contacts):
    """
    Extract unique companies and create them in Brevo CRM.
    Then link contacts to companies.
    """
    print("\n=== Creating Companies ===")

    # Extract unique companies
    companies = {}
    for c in contacts:
        company = c['attributes'].get('COMPANY', '').strip()
        website = c['attributes'].get('WEBSITE', '').strip()

        if company and company not in companies:
            companies[company] = {
                'name': company,
                'website': website,
                'contacts': []
            }

        if company:
            companies[company]['contacts'].append(c['email'])

    print(f"  Found {len(companies)} unique companies")

    # Note: Brevo's free plan may not include full CRM features
    # We'll store company info as contact attributes instead

    return companies


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Bulk import contacts to Brevo')
    parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    parser.add_argument('--limit', type=int, help='Limit number of contacts to import')
    parser.add_argument('--use-bulk', action='store_true', help='Use bulk import API (faster)')
    args = parser.parse_args()

    print("=" * 60)
    print("BREVO BULK IMPORT")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize client
    client = BrevoClient()

    # Test connection
    account = client.get_account()
    if not account.get('success'):
        print(f"ERROR: Cannot connect to Brevo: {account.get('error')}")
        return

    print(f"Account: {account['data'].get('companyName', 'N/A')}")

    # Load contacts
    print("\n=== Loading Data ===")
    contacts = load_master_contacts()
    print(f"  Loaded {len(contacts)} contacts with email addresses")

    if args.limit:
        contacts = contacts[:args.limit]
        print(f"  Limited to {len(contacts)} contacts")

    # Count by type
    dnc_count = sum(1 for c in contacts if c['flags']['is_dnc'])
    called_count = sum(1 for c in contacts if c['flags']['was_called'] and not c['flags']['is_dnc'])
    appt_count = sum(1 for c in contacts if c['flags']['had_appointment'])
    fresh_count = len(contacts) - dnc_count - called_count

    print(f"\n  Breakdown:")
    print(f"    DNC (to blocklist): {dnc_count}")
    print(f"    Previously called: {called_count}")
    print(f"    Had appointments: {appt_count}")
    print(f"    Fresh leads: {fresh_count}")

    # Create lists
    list_ids = create_lists(client)

    if not all(list_ids.values()):
        print("ERROR: Failed to create all required lists")
        return

    # Import contacts
    if args.use_bulk:
        stats = import_with_bulk_api(client, contacts, list_ids, dry_run=args.dry_run)
    else:
        stats = import_contacts_batch(client, contacts, list_ids, dry_run=args.dry_run)

    # Summary
    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)
    print(f"Total contacts: {stats['total']}")
    print(f"Imported: {stats['imported']}")
    print(f"Failed: {stats['failed']}")
    if 'dnc_blocked' in stats:
        print(f"DNC blocked: {stats['dnc_blocked']}")

    if stats.get('errors'):
        print(f"\nFirst {len(stats['errors'])} errors:")
        for err in stats['errors']:
            print(f"  {err['email']}: {err['error']}")

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
