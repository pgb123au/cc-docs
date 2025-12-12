"""
Create Companies in Brevo and Link Contacts.

Extracts unique companies from contacts and:
1. Creates Company records in Brevo CRM
2. Links contacts to their companies

Usage:
    python create_companies.py --limit 100  # Test with 100 companies
    python create_companies.py              # All companies
"""

import sys
import csv
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from brevo_api import BrevoClient

MASTER_CSV = Path(r'C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv')


def load_companies_and_contacts():
    """Load companies with their associated contacts from CSV."""
    companies = defaultdict(lambda: {'contacts': [], 'website': '', 'first_contact': None})

    with open(MASTER_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip().lower()
            company_name = row.get('company', '').strip()
            website = row.get('website', '').strip()

            if not email or '@' not in email or not company_name:
                continue

            # Normalize company name (title case, clean up)
            company_key = company_name.lower().strip()

            companies[company_key]['name'] = company_name
            companies[company_key]['contacts'].append(email)
            if website and not companies[company_key]['website']:
                companies[company_key]['website'] = website
            if not companies[company_key]['first_contact']:
                companies[company_key]['first_contact'] = email

    return companies


def get_contact_id(client, email):
    """Get Brevo contact ID from email."""
    result = client.get_contact(email)
    if result.get('success'):
        return result['data'].get('id')
    return None


def create_and_link_companies(client, companies, limit=None):
    """Create companies and link contacts."""
    print(f"\n=== Creating {len(companies) if not limit else min(limit, len(companies))} companies ===")

    stats = {
        'companies_created': 0,
        'contacts_linked': 0,
        'failed': 0
    }

    count = 0
    for company_key, data in companies.items():
        if limit and count >= limit:
            break

        company_name = data['name']
        website = data['website']
        contacts = data['contacts']

        # Create company
        company_data = {
            'name': company_name,
        }
        if website:
            company_data['attributes'] = {'domain': website}

        result = client._request('POST', 'companies', company_data)

        if result.get('success'):
            company_id = result['data']['id']
            stats['companies_created'] += 1

            # Link contacts (get IDs first)
            contact_ids = []
            for email in contacts[:10]:  # Limit to 10 contacts per company
                cid = get_contact_id(client, email)
                if cid:
                    contact_ids.append(cid)

            if contact_ids:
                link_result = client._request('PATCH', f'companies/link-unlink/{company_id}', {
                    'linkContactIds': contact_ids
                })
                if link_result.get('success'):
                    stats['contacts_linked'] += len(contact_ids)
        else:
            error = result.get('error', '')
            if 'already exists' not in str(error).lower():
                stats['failed'] += 1

        count += 1
        if count % 50 == 0:
            print(f"  Progress: {count} companies, {stats['contacts_linked']} contacts linked")

        time.sleep(0.1)  # Rate limiting

    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, help='Limit companies to create')
    args = parser.parse_args()

    print("=" * 60)
    print("CREATE COMPANIES AND LINK CONTACTS")
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
    print("\nLoading companies from CSV...")
    companies = load_companies_and_contacts()
    print(f"Found {len(companies)} unique companies")

    # Stats
    total_contacts = sum(len(c['contacts']) for c in companies.values())
    with_website = sum(1 for c in companies.values() if c['website'])
    print(f"Total contacts with companies: {total_contacts}")
    print(f"Companies with website: {with_website}")

    # Create companies
    stats = create_and_link_companies(client, companies, limit=args.limit)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Companies created: {stats['companies_created']}")
    print(f"Contacts linked: {stats['contacts_linked']}")
    print(f"Failed: {stats['failed']}")
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
