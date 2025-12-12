"""
Enrich and cross-reference appointment data with telemarketer lists.

This script:
1. Loads appointments from All_Appointments_Extracted.csv
2. Cross-references with massive_list.csv and massive_list_vic.csv
3. Matches against called_numbers.json to see which were actually called
4. Normalizes status values into categories
5. Creates enriched output with all original columns preserved
"""

import csv
import json
import re
from pathlib import Path
from collections import Counter

# File paths
APPOINTMENTS_CSV = Path(r'C:\Users\peter\Downloads\CC\CRM\All_Appointments_Extracted.csv')
MASSIVE_LIST = Path(r'C:\Users\peter\retell-dialer\massive_list.csv')
VIC_LIST = Path(r'C:\Users\peter\retell-dialer\massive_list_vic.csv')
CALLED_LOG = Path(r'C:\Users\peter\retell-dialer\called_log.txt')
CALLED_JSON = Path(r'C:\Users\peter\retell-dialer\called_numbers.json')
OUTPUT_DIR = Path(r'C:\Users\peter\Downloads\CC\CRM')


def normalize_phone(phone):
    """Normalize phone to 61XXXXXXXXX format."""
    if not phone:
        return None
    phone = str(phone).strip()
    clean = ''.join(c for c in phone if c.isdigit() or c == '+')
    clean = clean.replace('+', '')
    if clean.startswith('0') and len(clean) == 10:
        clean = '61' + clean[1:]
    elif clean.startswith('4') and len(clean) == 9:
        clean = '61' + clean
    if clean.startswith('61') and len(clean) == 11:
        return clean
    return None


def extract_email_domain(email):
    """Extract domain from email address."""
    if not email or '@' not in email:
        return None
    # Handle multiple emails
    email = email.split(';')[0].strip()
    try:
        domain = email.split('@')[1].lower().strip()
        return domain
    except:
        return None


def load_called_numbers():
    """Load all numbers that were actually called."""
    called = set()

    if CALLED_LOG.exists():
        with open(CALLED_LOG, 'r') as f:
            for line in f:
                num = normalize_phone(line.strip())
                if num:
                    called.add(num)

    if CALLED_JSON.exists():
        with open(CALLED_JSON, 'r') as f:
            data = json.load(f)
            for num in data:
                normalized = normalize_phone(num)
                if normalized:
                    called.add(normalized)

    return called


def load_telemarketer_contacts():
    """Load contact details from massive lists, indexed by email domain and company."""
    contacts_by_domain = {}
    contacts_by_email = {}
    contacts_by_company = {}

    for filepath in [MASSIVE_LIST, VIC_LIST]:
        if not filepath.exists():
            print(f"  Warning: {filepath} not found")
            continue

        print(f"  Loading {filepath.name}...")
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get phone number
                phone = None
                for col in ['phone_number', 'Phone Number 1', 'Phone Number 2', 'Mobile Phone Number']:
                    if col in row and row[col]:
                        phone = normalize_phone(row[col])
                        if phone:
                            break

                # Get email
                email = row.get('Email', '').strip().lower()
                domain = extract_email_domain(email)

                # Get company
                company = row.get('Company Name', '').strip().lower()

                # Get other details
                contact = {
                    'phone': phone,
                    'first_name': row.get('First Name', '').strip(),
                    'last_name': row.get('Last Name', '').strip(),
                    'email': email,
                    'company': row.get('Company Name', '').strip(),
                    'website': row.get('Website URL', '').strip(),
                    'city': row.get('City', '').strip(),
                    'state': row.get('State/Region', '').strip(),
                }

                # Index by domain
                if domain and domain not in contacts_by_domain:
                    contacts_by_domain[domain] = contact

                # Index by email
                if email:
                    contacts_by_email[email] = contact

                # Index by company name (normalized)
                if company and len(company) > 2:
                    contacts_by_company[company] = contact

    return contacts_by_domain, contacts_by_email, contacts_by_company


def normalize_status(status):
    """Normalize status to a category."""
    if not status:
        return 'unknown', status

    status_lower = status.lower().strip()

    # Client/Won
    if any(x in status_lower for x in ['client', 'paid', 'excellent']):
        return 'won', status

    # Follow up needed
    if any(x in status_lower for x in ['fu', 'follow', 'cb ', 'call back', 'callback']):
        return 'followup', status

    # No show
    if 'no show' in status_lower or 'noshow' in status_lower:
        return 'no_show', status

    # Cancelled/Rescheduled
    if any(x in status_lower for x in ['cancel', 'reschedule']):
        return 'reschedule', status

    # Bad prospect - too small
    if 'too small' in status_lower or 'to small' in status_lower:
        return 'bad_prospect_small', status

    # Bad prospect - demographic
    if any(x in status_lower for x in ['indian', 'asian']):
        return 'bad_prospect_demo', status

    # Bad prospect - competitor
    if 'competitor' in status_lower:
        return 'competitor', status

    # Seen but not converted (BP = bad prospect)
    if 'bp' in status_lower:
        return 'bad_prospect', status

    # Seen - general
    if 'seen' in status_lower:
        return 'seen', status

    # Booked
    if 'booked' in status_lower or 'book' in status_lower:
        return 'booked', status

    # Dead
    if 'dead' in status_lower:
        return 'dead', status

    # Sent info
    if any(x in status_lower for x in ['sent info', 'sent sms', 'sent email', 'left vm']):
        return 'contacted', status

    # Wanted to book
    if 'wanted' in status_lower:
        return 'hot_lead', status

    return 'other', status


def is_valid_email(email):
    """Check if email looks valid."""
    if not email:
        return False
    if '@' not in email:
        return False
    # Check for notes in email field
    invalid_patterns = ['no email', 'sms', 'indian', 'accountant', '!!', '??']
    for pattern in invalid_patterns:
        if pattern in email.lower():
            return False
    return True


def main():
    print("=" * 70)
    print("APPOINTMENT DATA ENRICHMENT & CROSS-REFERENCE")
    print("=" * 70)

    # Load called numbers
    print("\n1. Loading called numbers...")
    called_numbers = load_called_numbers()
    print(f"   Total unique numbers called: {len(called_numbers):,}")

    # Load telemarketer contacts
    print("\n2. Loading telemarketer contact lists...")
    contacts_by_domain, contacts_by_email, contacts_by_company = load_telemarketer_contacts()
    print(f"   Contacts indexed by domain: {len(contacts_by_domain):,}")
    print(f"   Contacts indexed by email: {len(contacts_by_email):,}")
    print(f"   Contacts indexed by company: {len(contacts_by_company):,}")

    # Load appointments
    print("\n3. Loading appointments...")
    appointments = []
    with open(APPOINTMENTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            appointments.append(row)
    print(f"   Total appointments: {len(appointments)}")

    # Enrich appointments
    print("\n4. Cross-referencing and enriching...")
    enriched = []
    stats = {
        'matched_by_email': 0,
        'matched_by_domain': 0,
        'matched_by_company': 0,
        'phone_found': 0,
        'was_called': 0,
        'valid_email': 0,
        'has_date': 0,
    }

    status_categories = Counter()
    status_raw = Counter()

    for appt in appointments:
        # Start with original data
        enriched_appt = dict(appt)

        # Add enrichment fields
        enriched_appt['match_source'] = None
        enriched_appt['phone_from_list'] = None
        enriched_appt['was_called'] = False
        enriched_appt['email_valid'] = False
        enriched_appt['status_category'] = None
        enriched_appt['company_from_list'] = None
        enriched_appt['website_from_list'] = None
        enriched_appt['location'] = None

        # Normalize and categorize status
        status_cat, status_orig = normalize_status(appt.get('status', ''))
        enriched_appt['status_category'] = status_cat
        status_categories[status_cat] += 1
        if status_orig:
            status_raw[status_orig] += 1

        # Check email validity
        email = appt.get('email', '').strip().lower()
        if is_valid_email(email):
            enriched_appt['email_valid'] = True
            stats['valid_email'] += 1

        # Check if has date
        if appt.get('date'):
            stats['has_date'] += 1

        # Try to match to telemarketer lists
        contact = None
        match_source = None

        # 1. Try exact email match
        if email in contacts_by_email:
            contact = contacts_by_email[email]
            match_source = 'email'
            stats['matched_by_email'] += 1

        # 2. Try domain match
        elif email:
            domain = extract_email_domain(email)
            if domain and domain in contacts_by_domain:
                contact = contacts_by_domain[domain]
                match_source = 'domain'
                stats['matched_by_domain'] += 1

        # 3. Try company name match
        if not contact:
            company = appt.get('company', '').strip().lower()
            if company and len(company) > 2 and company in contacts_by_company:
                contact = contacts_by_company[company]
                match_source = 'company'
                stats['matched_by_company'] += 1

        # Apply enrichment from contact
        if contact:
            enriched_appt['match_source'] = match_source
            enriched_appt['phone_from_list'] = contact.get('phone')
            enriched_appt['company_from_list'] = contact.get('company')
            enriched_appt['website_from_list'] = contact.get('website')
            if contact.get('city') or contact.get('state'):
                enriched_appt['location'] = f"{contact.get('city', '')}, {contact.get('state', '')}".strip(', ')

            if contact.get('phone'):
                stats['phone_found'] += 1

                # Check if this phone was called
                if contact['phone'] in called_numbers:
                    enriched_appt['was_called'] = True
                    stats['was_called'] += 1

        enriched.append(enriched_appt)

    # Print results
    print("\n" + "=" * 70)
    print("ENRICHMENT RESULTS")
    print("=" * 70)

    print(f"\nMatch statistics:")
    print(f"  Matched by exact email:  {stats['matched_by_email']}")
    print(f"  Matched by domain:       {stats['matched_by_domain']}")
    print(f"  Matched by company:      {stats['matched_by_company']}")
    print(f"  Total with phone found:  {stats['phone_found']}")
    print(f"  Confirmed as called:     {stats['was_called']}")

    print(f"\nData quality:")
    print(f"  Valid emails:            {stats['valid_email']}")
    print(f"  Has appointment date:    {stats['has_date']}")

    print(f"\n{'=' * 70}")
    print("STATUS CATEGORIES (normalized)")
    print("=" * 70)
    for cat, count in status_categories.most_common():
        print(f"  {cat:25} {count:3}")

    print(f"\n{'=' * 70}")
    print("RAW STATUS VALUES (top 20)")
    print("=" * 70)
    for status, count in status_raw.most_common(20):
        print(f"  {status[:45]:45} {count:3}")

    # Save enriched data
    output_file = OUTPUT_DIR / 'Appointments_Enriched.csv'
    fieldnames = [
        # Original fields
        'source_sheet', 'company', 'name', 'email', 'phone', 'date', 'time',
        'status', 'quality', 'followup', 'retell_log',
        # Enrichment fields
        'status_category', 'email_valid', 'match_source', 'phone_from_list',
        'was_called', 'company_from_list', 'website_from_list', 'location'
    ]

    print(f"\n{'=' * 70}")
    print(f"SAVING OUTPUT")
    print("=" * 70)

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(enriched)
    print(f"  Enriched data:  {output_file}")

    # Create segmented files
    segments = {
        'won': [],
        'hot_lead': [],
        'followup': [],
        'booked': [],
        'seen': [],
        'contacted': [],
        'reschedule': [],
        'no_show': [],
        'bad_prospect': [],
        'dead': [],
    }

    for appt in enriched:
        cat = appt.get('status_category', 'other')
        # Consolidate bad prospect categories
        if cat in ['bad_prospect_small', 'bad_prospect_demo', 'competitor']:
            cat = 'bad_prospect'
        if cat in segments:
            segments[cat].append(appt)

    print(f"\n  Segmented files:")
    for segment_name, segment_data in segments.items():
        if segment_data:
            seg_file = OUTPUT_DIR / f'Appointments_{segment_name}.csv'
            with open(seg_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(segment_data)
            print(f"    {segment_name:20} {len(segment_data):3} records -> {seg_file.name}")

    # Summary of actionable leads
    print(f"\n{'=' * 70}")
    print("ACTIONABLE LEADS SUMMARY")
    print("=" * 70)

    actionable = [a for a in enriched if a['status_category'] in ['won', 'hot_lead', 'followup', 'booked', 'seen', 'contacted', 'reschedule']]
    with_email = [a for a in actionable if a['email_valid']]
    with_phone = [a for a in actionable if a['phone_from_list']]

    print(f"  Total actionable:     {len(actionable)}")
    print(f"  With valid email:     {len(with_email)}")
    print(f"  With phone number:    {len(with_phone)}")

    # Show won clients
    won = [a for a in enriched if a['status_category'] == 'won']
    if won:
        print(f"\n  WON CLIENTS ({len(won)}):")
        for w in won:
            print(f"    - {w.get('company') or w.get('name') or 'N/A'}: {w.get('email', 'N/A')}")

    # Show hot leads
    hot = [a for a in enriched if a['status_category'] == 'hot_lead']
    if hot:
        print(f"\n  HOT LEADS ({len(hot)}):")
        for h in hot:
            print(f"    - {h.get('name', 'N/A')}: {h.get('email', 'N/A')}")

    print(f"\nDone!")


if __name__ == "__main__":
    main()
