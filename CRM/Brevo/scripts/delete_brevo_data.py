"""Delete all test data from Brevo."""
from brevo_api import BrevoClient
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = BrevoClient()

print("=" * 50)
print("DELETING ALL BREVO TEST DATA")
print("=" * 50)

# Delete contacts first
print("\nDeleting contacts...")
result = client.get_contacts(limit=100)
if result.get('success'):
    contacts = result['data'].get('contacts', [])
    for c in contacts:
        email = c.get('email', '')
        delete_result = client.delete_contact(email)
        if delete_result.get('success'):
            print(f"  Deleted contact: {email}")
        else:
            print(f"  Failed to delete {email}: {delete_result.get('error')}")

# Delete companies
print("\nDeleting companies...")
result = client._request('GET', 'companies', params={'limit': 100})
if result.get('success'):
    companies = result['data'].get('items', [])
    for co in companies:
        co_id = co.get('id')
        name = co.get('attributes', {}).get('name', 'Unknown')
        delete_result = client._request('DELETE', f'companies/{co_id}')
        if delete_result.get('success'):
            print(f"  Deleted company: {name}")
        else:
            print(f"  Failed to delete {name}: {delete_result.get('error')}")

print("\nDone!")
