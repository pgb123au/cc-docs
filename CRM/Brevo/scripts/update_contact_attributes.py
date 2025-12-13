"""
Update Brevo contacts with missing attributes from Master CSV.

The bulk import added contacts to lists but didn't preserve attributes.
This script updates existing contacts with their full details.

Usage:
    python update_contact_attributes.py --limit 100  # Test with 100
    python update_contact_attributes.py              # Update all
"""

import sys
import csv
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from brevo_api import BrevoClient, normalize_australian_mobile

MASTER_CSV = Path(r'C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv')


def load_contact_data():
    """Load contact attributes from master CSV."""
    contacts = {}

    with open(MASTER_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip().lower()
            if not email or '@' not in email:
                continue

            phone = row.get('phone_normalized', '').strip()

            contacts[email] = {
                'FIRSTNAME': row.get('first_name', '').strip(),
                'LASTNAME': row.get('last_name', '').strip(),
                'SMS': normalize_australian_mobile(phone) if phone else '',
                'COMPANY': row.get('company', '').strip(),
                'WEBSITE': row.get('website', '').strip(),
                'SOURCE': row.get('source', '').strip(),
            }

    return contacts


def update_contacts(client, contact_data, limit=None):
    """Update contacts with their attributes."""
    print(f"\n=== Updating {len(contact_data) if not limit else limit} contacts ===")

    stats = {'updated': 0, 'failed': 0, 'skipped': 0}

    count = 0
    for email, attrs in contact_data.items():
        if limit and count >= limit:
            break

        # Skip if no meaningful data
        if not any(attrs.values()):
            stats['skipped'] += 1
            continue

        # Filter out empty attributes
        attrs_to_update = {k: v for k, v in attrs.items() if v}

        if not attrs_to_update:
            stats['skipped'] += 1
            continue

        result = client.update_contact(email, attrs_to_update)

        if result.get('success'):
            stats['updated'] += 1
        else:
            error = result.get('error', '')
            if 'not found' in str(error).lower():
                stats['skipped'] += 1  # Contact not in Brevo
            else:
                stats['failed'] += 1

        count += 1

        if count % 500 == 0:
            print(f"  Progress: {count} processed - {stats['updated']} updated")

        time.sleep(0.05)  # Rate limiting

    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, help='Limit contacts to update')
    args = parser.parse_args()

    print("=" * 60)
    print("UPDATE CONTACT ATTRIBUTES")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    client = BrevoClient()

    # Verify connection
    account = client.get_account()
    if not account.get('success'):
        print("ERROR: Cannot connect to Brevo")
        return

    print(f"Account: {account['data'].get('companyName')}")

    # Load data
    print("\nLoading contact data from CSV...")
    contact_data = load_contact_data()
    print(f"Loaded {len(contact_data):,} contacts with attributes")

    # Count contacts with actual data
    with_company = sum(1 for c in contact_data.values() if c.get('COMPANY'))
    with_name = sum(1 for c in contact_data.values() if c.get('FIRSTNAME'))
    with_phone = sum(1 for c in contact_data.values() if c.get('SMS'))

    print(f"  With company: {with_company:,}")
    print(f"  With name: {with_name:,}")
    print(f"  With phone: {with_phone:,}")

    # Update
    stats = update_contacts(client, contact_data, limit=args.limit)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Updated: {stats['updated']:,}")
    print(f"Skipped: {stats['skipped']:,}")
    print(f"Failed: {stats['failed']:,}")
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
