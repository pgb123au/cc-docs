"""
Assign existing Brevo contacts to appropriate lists based on their attributes.

This script reads all contacts from Brevo and assigns them to lists based on:
- DNC flag (emailBlacklisted) -> DO NOT CALL list
- SOURCE attribute -> Previously Called / Fresh Leads
- Has COMPANY -> Safe to Contact

Usage:
    python assign_contacts_to_lists.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from brevo_api import BrevoClient

# List IDs (update these if they change)
LIST_IDS = {
    'all_contacts': 24,
    'safe_to_contact': 25,
    'fresh_leads': 26,
    'dnc': 27,
    'appointments': 28,
    'called': 29
}


def get_all_contacts(client, batch_size=1000):
    """Retrieve all contacts from Brevo in batches."""
    all_contacts = []
    offset = 0

    while True:
        result = client.get_contacts(limit=batch_size, offset=offset)
        if not result.get('success'):
            print(f"Error fetching contacts: {result.get('error')}")
            break

        contacts = result['data'].get('contacts', [])
        if not contacts:
            break

        all_contacts.extend(contacts)
        offset += len(contacts)

        print(f"  Fetched {offset} contacts...")

        if len(contacts) < batch_size:
            break

    return all_contacts


def categorize_contact(contact):
    """Determine which lists a contact should belong to."""
    lists = [LIST_IDS['all_contacts']]  # Everyone goes to All Contacts

    email = contact.get('email', '')
    attributes = contact.get('attributes', {})
    is_blacklisted = contact.get('emailBlacklisted', False)

    # DNC check
    if is_blacklisted:
        lists.append(LIST_IDS['dnc'])
        return lists  # DNC contacts don't go to other marketing lists

    # Source-based categorization
    source = attributes.get('SOURCE', '').lower()

    if 'called' in source or 'called_log' in source:
        lists.append(LIST_IDS['called'])
        lists.append(LIST_IDS['safe_to_contact'])
    elif 'massive_list' in source or 'fresh' in source:
        lists.append(LIST_IDS['fresh_leads'])
        lists.append(LIST_IDS['safe_to_contact'])
    else:
        # Default to safe to contact if has email
        lists.append(LIST_IDS['safe_to_contact'])

    # Appointment check (based on attributes)
    # We'll mark this separately when we import appointments

    return lists


def assign_contacts_to_lists(client, contacts):
    """Assign contacts to appropriate lists."""
    print(f"\n=== Assigning {len(contacts)} contacts to lists ===")

    # Group contacts by list assignment
    list_assignments = {list_id: [] for list_id in LIST_IDS.values()}

    for contact in contacts:
        email = contact.get('email')
        if not email:
            continue

        assigned_lists = categorize_contact(contact)
        for list_id in assigned_lists:
            list_assignments[list_id].append(email)

    # Print summary
    print("\nAssignment summary:")
    for name, list_id in LIST_IDS.items():
        print(f"  {name}: {len(list_assignments[list_id]):,} contacts")

    # Add contacts to lists in batches
    for name, list_id in LIST_IDS.items():
        emails = list_assignments[list_id]
        if not emails:
            continue

        print(f"\nAdding {len(emails):,} contacts to '{name}'...")

        # Brevo allows up to 150 emails per batch
        batch_size = 150
        success = 0
        failed = 0

        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]

            result = client.add_contacts_to_list(list_id, batch)
            if result.get('success'):
                success += len(batch)
            else:
                failed += len(batch)
                if failed <= 3:  # Only show first few errors
                    print(f"    Error: {result.get('error')}")

            time.sleep(0.1)  # Rate limiting

            if (i // batch_size) % 10 == 0:
                print(f"    Progress: {i + len(batch)}/{len(emails)}")

        print(f"    Done: {success} added, {failed} failed")


def main():
    print("=" * 60)
    print("ASSIGN CONTACTS TO LISTS")
    print("=" * 60)

    client = BrevoClient()

    # Verify connection
    account = client.get_account()
    if not account.get('success'):
        print(f"ERROR: Cannot connect to Brevo")
        return

    print(f"Account: {account['data'].get('companyName')}")

    # Get all contacts
    print("\n=== Fetching all contacts ===")
    contacts = get_all_contacts(client)
    print(f"Total contacts: {len(contacts):,}")

    if not contacts:
        print("No contacts found!")
        return

    # Assign to lists
    assign_contacts_to_lists(client, contacts)

    # Verify
    print("\n=== Verification ===")
    lists = client.get_lists(limit=50)
    if lists.get('success'):
        for lst in lists['data'].get('lists', []):
            if lst['id'] >= 24:
                print(f"  {lst['name']}: {lst.get('totalSubscribers', 0):,} contacts")

    print("\nDone!")


if __name__ == "__main__":
    main()
