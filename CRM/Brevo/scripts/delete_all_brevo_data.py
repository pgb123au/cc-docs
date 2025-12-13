"""
Delete ALL data from Brevo CRM - Contacts and Companies
Run this before a fresh import.

WARNING: This is destructive and cannot be undone!
"""
import sys
import time
import concurrent.futures
from brevo_api import BrevoClient

# Encoding fix for Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = BrevoClient()

def delete_contact(email):
    """Delete a single contact."""
    result = client.delete_contact(email)
    return email, result.get('success', False)

def delete_company(company_id):
    """Delete a single company."""
    result = client._request('DELETE', f'companies/{company_id}')
    return company_id, result.get('success', False)

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

    # Confirm
    confirm = input("Type 'DELETE' to confirm deletion: ")
    if confirm != "DELETE":
        print("Aborted.")
        return

    print()
    print("Starting deletion...")
    print()

    # Delete contacts with threading for speed
    deleted_contacts = 0
    errors = 0
    batch_size = 100

    start_time = time.time()

    while True:
        # Get batch
        result = client.get_contacts(limit=batch_size, offset=0)
        if not result.get('success'):
            print(f"Error getting contacts: {result.get('error')}")
            break

        contacts = result['data'].get('contacts', [])
        if not contacts:
            break

        emails = [c.get('email') for c in contacts if c.get('email')]

        # Delete concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(delete_contact, email): email for email in emails}
            for future in concurrent.futures.as_completed(futures):
                email, success = future.result()
                if success:
                    deleted_contacts += 1
                else:
                    errors += 1

        elapsed = time.time() - start_time
        rate = deleted_contacts / elapsed if elapsed > 0 else 0
        remaining = (total_contacts - deleted_contacts) / rate if rate > 0 else 0

        print(f"  Deleted: {deleted_contacts:,} / {total_contacts:,} | "
              f"Errors: {errors} | "
              f"Rate: {rate:.1f}/sec | "
              f"ETA: {remaining/60:.1f} min")

    print()
    print(f"Contacts deleted: {deleted_contacts:,}")
    print(f"Errors: {errors}")
    print()

    # Delete companies
    print("Deleting companies...")
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
                    print(f"  Deleted company: {co.get('attributes', {}).get('name', co_id)}")

    print()
    print(f"Companies deleted: {deleted_companies}")
    print()
    print("=" * 60)
    print("DELETION COMPLETE")
    print("=" * 60)
    print(f"Total contacts deleted: {deleted_contacts:,}")
    print(f"Total companies deleted: {deleted_companies}")
    print(f"Time taken: {time.time() - start_time:.1f} seconds")

if __name__ == "__main__":
    main()
