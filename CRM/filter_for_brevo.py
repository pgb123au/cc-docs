"""
Filter contacts for Brevo import.
Criteria:
- Linked to a company
- Has first name AND last name
- Has mobile number
- Company has business type
- Company has website (domain)
"""
import csv
import re
from collections import defaultdict

CONTACTS_FILE = r'C:\Users\peter\Downloads\CC\CRM\All_Contacts_2025_07_07_Cleaned.csv'
COMPANIES_FILE = r'C:\Users\peter\Downloads\CC\CRM\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv'
OUTPUT_FILE = r'C:\Users\peter\Downloads\CC\CRM\Brevo_Import_Filtered.csv'

def normalize_phone(phone):
    """Normalize Australian mobile to +61 format."""
    if not phone:
        return None

    # Remove spaces, dashes, parentheses
    phone = re.sub(r'[^\d+]', '', phone)

    # Must be mobile (starts with 04 or +614)
    if phone.startswith('+614') and len(phone) == 12:
        return phone
    elif phone.startswith('614') and len(phone) == 11:
        return '+' + phone
    elif phone.startswith('04') and len(phone) == 10:
        return '+61' + phone[1:]
    elif phone.startswith('4') and len(phone) == 9:
        return '+61' + phone

    return None  # Not a valid AU mobile


def main():
    print("Loading companies...")

    # Build company lookup: Legacy Record ID -> company data
    # Also index by Company ID as fallback
    companies_by_legacy = {}
    companies_by_id = {}

    with open(COMPANIES_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            legacy_id = row.get('Legacy Record ID', '').strip()
            company_id = row.get('Company ID', '').strip()

            company_data = {
                'name': row.get('Company name', '').strip(),
                'domain': row.get('Company Domain Name', '').strip(),
                'email': row.get('Company Email', '').strip(),
                'phone': row.get('Company Phone Number', '').strip(),
                'business_type': row.get('Business type', '').strip(),
                'industry': row.get('Industry', '').strip(),
                'state': row.get('State/Region', '').strip(),
                'suburb': row.get('Suburb', '').strip(),
                'postcode': row.get('Postal Code', '').strip(),
            }

            if legacy_id:
                companies_by_legacy[legacy_id] = company_data
            if company_id:
                companies_by_id[company_id] = company_data

    print(f"Loaded {len(companies_by_legacy):,} companies (by Legacy ID)")
    print(f"Loaded {len(companies_by_id):,} companies (by Company ID)")

    # Process contacts
    print("\nProcessing contacts...")

    stats = {
        'total': 0,
        'no_company_id': 0,
        'company_not_found': 0,
        'no_first_name': 0,
        'no_last_name': 0,
        'no_mobile': 0,
        'no_business_type': 0,
        'no_website': 0,
        'passed': 0,
    }

    filtered_contacts = []

    with open(CONTACTS_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            stats['total'] += 1

            # Check company association
            company_ids = row.get('Biz - Associated Company IDs', '').strip()
            if not company_ids:
                stats['no_company_id'] += 1
                continue

            # Get first company ID (may have multiple semicolon-separated)
            first_company_id = company_ids.split(';')[0].strip()

            # Try to find company by Legacy ID first, then by Company ID
            company = companies_by_legacy.get(first_company_id) or companies_by_id.get(first_company_id)
            if not company:
                stats['company_not_found'] += 1
                continue

            # Check first name
            first_name = row.get('First Name', '').strip()
            if not first_name:
                stats['no_first_name'] += 1
                continue

            # Check last name
            last_name = row.get('Last Name', '').strip()
            if not last_name:
                stats['no_last_name'] += 1
                continue

            # Check mobile - try all mobile fields
            mobile = None
            for field in ['Mobile Phone Number', 'Mobile Phone 2', 'Mobile Phone 3']:
                normalized = normalize_phone(row.get(field, ''))
                if normalized:
                    mobile = normalized
                    break

            if not mobile:
                stats['no_mobile'] += 1
                continue

            # Check company has business type
            if not company['business_type']:
                stats['no_business_type'] += 1
                continue

            # Check company has website
            if not company['domain']:
                stats['no_website'] += 1
                continue

            # PASSED ALL CRITERIA
            stats['passed'] += 1

            filtered_contacts.append({
                # Contact fields
                'email': row.get('Email', '').strip().lower(),
                'first_name': first_name.title(),
                'last_name': last_name.title(),
                'mobile': mobile,
                'job_title': row.get('Job Title', '').strip(),
                'contact_state': row.get('State/Region', '').strip(),
                'contact_city': row.get('City', '').strip(),
                'contact_postcode': row.get('Postal Code', '').strip(),

                # Company fields
                'company_id': first_company_id,
                'company_name': company['name'],
                'company_domain': company['domain'],
                'company_email': company['email'],
                'company_phone': company['phone'],
                'business_type': company['business_type'],
                'industry': company['industry'],
                'company_state': company['state'],
                'company_suburb': company['suburb'],
                'company_postcode': company['postcode'],
            })

    # Print stats
    print(f"\n{'='*60}")
    print("FILTER RESULTS")
    print(f"{'='*60}")
    print(f"Total contacts:        {stats['total']:,}")
    print(f"")
    print(f"Filtered out:")
    print(f"  No company ID:       {stats['no_company_id']:,}")
    print(f"  Company not found:   {stats['company_not_found']:,}")
    print(f"  No first name:       {stats['no_first_name']:,}")
    print(f"  No last name:        {stats['no_last_name']:,}")
    print(f"  No mobile:           {stats['no_mobile']:,}")
    print(f"  No business type:    {stats['no_business_type']:,}")
    print(f"  No website:          {stats['no_website']:,}")
    print(f"")
    print(f"PASSED ALL CRITERIA:   {stats['passed']:,}")

    # Analyze passed records
    if filtered_contacts:
        states = defaultdict(int)
        industries = defaultdict(int)
        business_types = defaultdict(int)

        for c in filtered_contacts:
            state = (c['company_state'] or c['contact_state'] or 'Unknown').upper()
            # Normalize state names
            if state in ['VICTORIA']:
                state = 'VIC'
            elif state in ['NEW SOUTH WALES']:
                state = 'NSW'
            elif state in ['QUEENSLAND']:
                state = 'QLD'
            elif state in ['WESTERN AUSTRALIA']:
                state = 'WA'
            elif state in ['SOUTH AUSTRALIA']:
                state = 'SA'
            states[state] += 1

            if c['industry']:
                industries[c['industry']] += 1
            if c['business_type']:
                business_types[c['business_type']] += 1

        print(f"\n{'='*60}")
        print("BREAKDOWN OF QUALIFIED CONTACTS")
        print(f"{'='*60}")

        print(f"\nBy State:")
        for state, count in sorted(states.items(), key=lambda x: -x[1])[:10]:
            print(f"  {state:20} {count:,}")

        print(f"\nTop Industries:")
        for ind, count in sorted(industries.items(), key=lambda x: -x[1])[:10]:
            print(f"  {ind:40} {count:,}")

        print(f"\nTop Business Types:")
        for bt, count in sorted(business_types.items(), key=lambda x: -x[1])[:10]:
            print(f"  {bt:40} {count:,}")

    # Write output
    if filtered_contacts:
        print(f"\nWriting {len(filtered_contacts):,} contacts to {OUTPUT_FILE}...")

        fieldnames = [
            'email', 'first_name', 'last_name', 'mobile', 'job_title',
            'contact_state', 'contact_city', 'contact_postcode',
            'company_id', 'company_name', 'company_domain', 'company_email',
            'company_phone', 'business_type', 'industry',
            'company_state', 'company_suburb', 'company_postcode'
        ]

        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_contacts)

        print("Done!")

    return stats, filtered_contacts


if __name__ == "__main__":
    stats, contacts = main()
