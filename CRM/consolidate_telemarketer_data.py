"""
Consolidate all telemarketer data files and create master contact list.

This script:
1. Loads all contact lists (massive_list, massive_list_vic, companies_pakenham)
2. Loads call logs (current + backup) and identifies duplicates
3. Extracts and dedupes DO NOT CALL list (filtering test numbers)
4. Flags invalid numbers
5. Creates consolidated master list with DNC flags
"""

import csv
import json
from pathlib import Path
from collections import Counter
from datetime import datetime

# File paths
RETELL_DIALER = Path(r'C:\Users\peter\retell-dialer')
OUTPUT_DIR = Path(r'C:\Users\peter\Downloads\CC\CRM')

# Test numbers to exclude from DNC (your own numbers)
TEST_NUMBERS = {
    '61412111000',  # Peter's test number
    '61399997398',  # Yes AI office number
}


def normalize_phone(phone):
    """Normalize phone to 61XXXXXXXXX format."""
    if not phone:
        return None
    phone = str(phone).strip()

    # Handle scientific notation
    if 'E' in phone.upper():
        try:
            phone = str(int(float(phone)))
        except:
            return None

    clean = ''.join(c for c in phone if c.isdigit() or c == '+')
    clean = clean.replace('+', '')

    if clean.startswith('0') and len(clean) == 10:
        clean = '61' + clean[1:]
    elif clean.startswith('4') and len(clean) == 9:
        clean = '61' + clean

    if clean.startswith('61') and len(clean) == 11:
        return clean

    return None


def load_do_not_call():
    """Load and dedupe DO NOT CALL list, filtering test numbers."""
    dnc_file = RETELL_DIALER / 'do_not_call.txt'

    dnc_numbers = set()
    raw_count = 0
    test_count = 0
    invalid_count = 0

    if dnc_file.exists():
        with open(dnc_file, 'r') as f:
            for line in f:
                raw_count += 1
                num = normalize_phone(line.strip())
                if num:
                    if num in TEST_NUMBERS:
                        test_count += 1
                    else:
                        dnc_numbers.add(num)
                else:
                    invalid_count += 1

    print(f"  DO NOT CALL list:")
    print(f"    Raw entries:      {raw_count}")
    print(f"    Test numbers:     {test_count} (filtered out)")
    print(f"    Invalid numbers:  {invalid_count}")
    print(f"    Unique DNC:       {len(dnc_numbers)}")

    return dnc_numbers


def load_invalid_numbers():
    """Load invalid numbers list."""
    invalid_file = RETELL_DIALER / 'invalid_numbers.txt'

    invalid = set()

    if invalid_file.exists():
        with open(invalid_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Extract number from lines like "SCIENTIFIC_NOTATION: 6.14102E+11"
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        num_part = parts[1].strip()
                        num = normalize_phone(num_part)
                        if num:
                            invalid.add(num)
                else:
                    num = normalize_phone(line)
                    if num:
                        invalid.add(num)

    return invalid


def load_called_numbers():
    """Load called numbers from current and backup files."""
    files = {
        'current_log': RETELL_DIALER / 'called_log.txt',
        'backup_log': RETELL_DIALER / 'called_log_backup.txt',
        'current_json': RETELL_DIALER / 'called_numbers.json',
        'backup_json': RETELL_DIALER / 'called_numbers - Copy.json',
    }

    called = {}  # phone -> {sources: [], first_seen: date}

    for source_name, filepath in files.items():
        if not filepath.exists():
            continue

        count = 0
        if filepath.suffix == '.txt':
            with open(filepath, 'r') as f:
                for line in f:
                    num = normalize_phone(line.strip())
                    if num:
                        if num not in called:
                            called[num] = {'sources': [], 'count': 0}
                        called[num]['sources'].append(source_name)
                        called[num]['count'] += 1
                        count += 1
        elif filepath.suffix == '.json':
            with open(filepath, 'r') as f:
                data = json.load(f)
                for num in data:
                    normalized = normalize_phone(num)
                    if normalized:
                        if normalized not in called:
                            called[normalized] = {'sources': [], 'count': 0}
                        called[normalized]['sources'].append(source_name)
                        called[normalized]['count'] += 1
                        count += 1

        print(f"    {source_name}: {count:,} entries")

    return called


def load_contact_lists():
    """Load all contact lists and dedupe."""
    files = {
        'massive_list': RETELL_DIALER / 'massive_list.csv',
        'massive_list_vic': RETELL_DIALER / 'massive_list_vic.csv',
        'companies_pakenham': RETELL_DIALER / 'companies_pakenham.csv',
    }

    contacts = {}  # phone -> contact details

    for source_name, filepath in files.items():
        if not filepath.exists():
            print(f"    {source_name}: NOT FOUND")
            continue

        count = 0
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Try different phone column names
                phone = None
                for col in ['phone_number', 'Phone Number 1', 'Mobile Number', 'Mobile Phone Number']:
                    if col in row and row[col]:
                        phone = normalize_phone(row[col])
                        if phone:
                            break

                if not phone:
                    continue

                # Only add if not already present (keep first occurrence)
                if phone not in contacts:
                    contacts[phone] = {
                        'phone': phone,
                        'first_name': row.get('First Name', row.get('Contact Name', '')).strip(),
                        'last_name': row.get('Last Name', '').strip(),
                        'email': row.get('Email', '').strip().lower(),
                        'company': row.get('Company Name', '').strip(),
                        'website': row.get('Website URL', row.get('Website', '')).strip(),
                        'city': row.get('City', row.get('Suburb', '')).strip(),
                        'state': row.get('State/Region', '').strip(),
                        'source_list': source_name,
                    }
                    count += 1

        print(f"    {source_name}: {count:,} unique contacts loaded")

    return contacts


def main():
    print("=" * 70)
    print("TELEMARKETER DATA CONSOLIDATION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Load DO NOT CALL list
    print("\n1. Loading DO NOT CALL list...")
    dnc_numbers = load_do_not_call()

    # 2. Load invalid numbers
    print("\n2. Loading invalid numbers...")
    invalid_numbers = load_invalid_numbers()
    print(f"    Invalid numbers: {len(invalid_numbers):,}")

    # 3. Load called numbers
    print("\n3. Loading called numbers (current + backups)...")
    called_data = load_called_numbers()
    print(f"    Total unique called: {len(called_data):,}")

    # Check overlap between current and backup
    current_only = set()
    backup_only = set()
    in_both = set()

    for phone, data in called_data.items():
        sources = set(data['sources'])
        has_current = any('current' in s for s in sources)
        has_backup = any('backup' in s for s in sources)

        if has_current and has_backup:
            in_both.add(phone)
        elif has_current:
            current_only.add(phone)
        else:
            backup_only.add(phone)

    print(f"\n    Overlap analysis:")
    print(f"      In current only:  {len(current_only):,}")
    print(f"      In backup only:   {len(backup_only):,}")
    print(f"      In both:          {len(in_both):,}")

    # 4. Load contact lists
    print("\n4. Loading contact lists...")
    contacts = load_contact_lists()
    print(f"    Total unique contacts: {len(contacts):,}")

    # 5. Cross-reference and flag
    print("\n5. Cross-referencing and flagging...")

    stats = {
        'dnc_in_contacts': 0,
        'called_in_contacts': 0,
        'invalid_in_contacts': 0,
    }

    for phone, contact in contacts.items():
        contact['is_dnc'] = phone in dnc_numbers
        contact['was_called'] = phone in called_data
        contact['is_invalid'] = phone in invalid_numbers
        contact['call_count'] = called_data.get(phone, {}).get('count', 0)

        if contact['is_dnc']:
            stats['dnc_in_contacts'] += 1
        if contact['was_called']:
            stats['called_in_contacts'] += 1
        if contact['is_invalid']:
            stats['invalid_in_contacts'] += 1

    print(f"    Contacts flagged as DNC:     {stats['dnc_in_contacts']}")
    print(f"    Contacts that were called:   {stats['called_in_contacts']}")
    print(f"    Contacts with invalid #:     {stats['invalid_in_contacts']}")

    # 6. Also check DNC numbers not in contacts (people who complained but aren't in our lists)
    dnc_not_in_contacts = dnc_numbers - set(contacts.keys())
    print(f"    DNC numbers NOT in contacts: {len(dnc_not_in_contacts)}")

    # 7. Save outputs
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)

    # Save master contact list
    master_file = OUTPUT_DIR / 'Master_Contacts_With_Flags.csv'
    fieldnames = [
        'phone', 'first_name', 'last_name', 'email', 'company', 'website',
        'city', 'state', 'source_list', 'is_dnc', 'was_called', 'is_invalid', 'call_count'
    ]

    with open(master_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for contact in contacts.values():
            writer.writerow(contact)
    print(f"  Master contacts: {master_file}")
    print(f"    Total: {len(contacts):,} contacts")

    # Save DNC list (clean, deduplicated)
    dnc_file = OUTPUT_DIR / 'DO_NOT_CALL_Master.csv'
    with open(dnc_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['phone', 'in_contacts', 'company', 'email'])
        for phone in sorted(dnc_numbers):
            contact = contacts.get(phone, {})
            writer.writerow([
                phone,
                'Yes' if phone in contacts else 'No',
                contact.get('company', ''),
                contact.get('email', '')
            ])
    print(f"  DO NOT CALL master: {dnc_file}")
    print(f"    Total: {len(dnc_numbers)} numbers")

    # Save safe-to-contact list (called contacts minus DNC)
    safe_contacts = [c for c in contacts.values() if c['was_called'] and not c['is_dnc'] and not c['is_invalid']]
    safe_file = OUTPUT_DIR / 'Safe_To_Contact.csv'
    with open(safe_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(safe_contacts)
    print(f"  Safe to contact: {safe_file}")
    print(f"    Total: {len(safe_contacts):,} contacts")

    # Save never-called contacts (fresh leads)
    fresh_contacts = [c for c in contacts.values() if not c['was_called'] and not c['is_dnc'] and not c['is_invalid']]
    fresh_file = OUTPUT_DIR / 'Fresh_Leads_Never_Called.csv'
    with open(fresh_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(fresh_contacts)
    print(f"  Fresh leads: {fresh_file}")
    print(f"    Total: {len(fresh_contacts):,} contacts")

    # Save DNC contacts with details
    dnc_contacts = [c for c in contacts.values() if c['is_dnc']]
    dnc_details_file = OUTPUT_DIR / 'DNC_Contacts_With_Details.csv'
    with open(dnc_details_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dnc_contacts)
    print(f"  DNC with details: {dnc_details_file}")
    print(f"    Total: {len(dnc_contacts)} contacts")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total contacts in system:     {len(contacts):,}")
    print(f"  DO NOT CALL (complaints):     {len(dnc_numbers)}")
    print(f"  Previously called:            {len(called_data):,}")
    print(f"  Safe to re-contact:           {len(safe_contacts):,}")
    print(f"  Fresh leads (never called):   {len(fresh_contacts):,}")
    print(f"  Invalid phone numbers:        {len(invalid_numbers):,}")

    # Show sample DNC contacts
    if dnc_contacts:
        print(f"\n  Sample DNC contacts (first 10):")
        for c in dnc_contacts[:10]:
            print(f"    {c['phone']} - {c['company'] or c['email'] or 'N/A'}")

    print("\nDone!")


if __name__ == "__main__":
    main()
