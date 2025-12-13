"""
Delete ALL data from Brevo CRM - Non-interactive version
"""
import sys
import time
import concurrent.futures
from brevo_api import BrevoClient

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = BrevoClient()

def delete_contact(email):
    """Delete a single contact."""
    result = client.delete_contact(email)
    return email, result.get('success', False)

def main():
    print("=" * 60)
    print("BREVO DATA DELETION - ALL CONTACTS AND COMPANIES")
    print("=" * 60)
    print()

    # Get counts
    result = client.get_contacts(limit=1)
    total_contacts = result['data']['count'] if result.get('success') else 0
    print(f"Total contacts to delete: {total_contacts:,}")

    result = client._request('GET', 'companies', params={'limit': 100})
    companies = result['data'].get('items', []) if result.get('success') else []
    print(f"Companies found: {len(companies)}")
    print()

    if total_contacts == 0 and len(companies) == 0:
        print("Nothing to delete!")
        return

    print("Starting deletion...")
    print()

    # Delete contacts
    deleted_contacts = 0
    errors = 0
    batch_size = 100
    start_time = time.time()

    while True:
        result = client.get_contacts(limit=batch_size, offset=0)
        if not result.get('success'):
            print(f"Error getting contacts: {result.get('error')}")
            break

        contacts = result['data'].get('contacts', [])
        if not contacts:
            break

        emails = [c.get('email') for c in contacts if c.get('email')]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(delete_contact, email): email for email in emails}
            for future in concurrent.futures.as_completed(futures):
                email, success = future.result()
                if success:
                    deleted_contacts += 1
                else:
                    errors += 1

        print(f"  Deleted: {deleted_contacts} contacts")

    print(f"\nContacts deleted: {deleted_contacts}")

    # Delete companies
    print("\nDeleting companies...")
    deleted_companies = 0

    while True:
        result = client._request('GET', 'companies', params={'limit': 100})
        if not result.get('success'):
            break

        companies = result['data'].get('items', [])
        if not companies:
            break

        for co in companies:
            co_id = co.get('id')
            if co_id:
                del_result = client._request('DELETE', f'companies/{co_id}')
                if del_result.get('success'):
                    deleted_companies += 1
                    print(f"  Deleted: {co.get('attributes', {}).get('name', co_id)}")

    print()
    print("=" * 60)
    print("DELETION COMPLETE")
    print("=" * 60)
    print(f"Contacts deleted: {deleted_contacts}")
    print(f"Companies deleted: {deleted_companies}")

if __name__ == "__main__":
    main()
