"""Quick analysis of CRM data files."""
import csv
from collections import Counter

def analyze_contacts():
    print("=" * 60)
    print("CONTACTS ANALYSIS")
    print("=" * 60)

    stats = {
        'total': 0,
        'has_email': 0,
        'has_mobile': 0,
        'has_any_phone': 0,
        'has_first_name': 0,
        'has_company': 0,
        'states': Counter(),
        'countries': Counter(),
        'email_domains': Counter(),
    }

    with open(r'C:\Users\peter\Downloads\CC\CRM\All_Contacts_2025_07_07_Cleaned.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            stats['total'] += 1

            # Email
            email = row.get('Email', '').strip()
            if email and '@' in email:
                stats['has_email'] += 1
                domain = email.split('@')[-1].lower()
                stats['email_domains'][domain] += 1

            # Mobile phones
            mobile1 = row.get('Mobile Phone Number', '').strip()
            mobile2 = row.get('Mobile Phone 2', '').strip()
            mobile3 = row.get('Mobile Phone 3', '').strip()
            phone1 = row.get('Phone Number 1', '').strip()

            if mobile1 or mobile2 or mobile3:
                stats['has_mobile'] += 1
            if mobile1 or mobile2 or mobile3 or phone1:
                stats['has_any_phone'] += 1

            # Name
            if row.get('First Name', '').strip():
                stats['has_first_name'] += 1

            # Company
            if row.get('Company Name', '').strip():
                stats['has_company'] += 1

            # State
            state = row.get('State/Region', '').strip().upper()
            if state:
                stats['states'][state] += 1

            # Country
            country = row.get('Country', '').strip()
            if country:
                stats['countries'][country] += 1

    # Print results
    print(f"\nTotal Records: {stats['total']:,}")
    print(f"\n--- COVERAGE ---")
    print(f"Has Email:      {stats['has_email']:,} ({stats['has_email']/stats['total']*100:.1f}%)")
    print(f"Has Mobile:     {stats['has_mobile']:,} ({stats['has_mobile']/stats['total']*100:.1f}%)")
    print(f"Has Any Phone:  {stats['has_any_phone']:,} ({stats['has_any_phone']/stats['total']*100:.1f}%)")
    print(f"Has First Name: {stats['has_first_name']:,} ({stats['has_first_name']/stats['total']*100:.1f}%)")
    print(f"Has Company:    {stats['has_company']:,} ({stats['has_company']/stats['total']*100:.1f}%)")

    print(f"\n--- TOP STATES ---")
    for state, count in stats['states'].most_common(15):
        print(f"  {state:20} {count:,}")

    print(f"\n--- TOP COUNTRIES ---")
    for country, count in stats['countries'].most_common(10):
        print(f"  {country:20} {count:,}")

    print(f"\n--- TOP EMAIL DOMAINS ---")
    for domain, count in stats['email_domains'].most_common(15):
        print(f"  {domain:30} {count:,}")

    return stats


def analyze_companies():
    print("\n" + "=" * 60)
    print("COMPANIES ANALYSIS")
    print("=" * 60)

    stats = {
        'total': 0,
        'has_email': 0,
        'has_phone': 0,
        'has_any_phone': 0,
        'has_website': 0,
        'states': Counter(),
        'industries': Counter(),
        'business_types': Counter(),
    }

    with open(r'C:\Users\peter\Downloads\CC\CRM\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            stats['total'] += 1

            # Email
            email = row.get('Company Email', '').strip()
            if email and '@' in email:
                stats['has_email'] += 1

            # Phones
            phone1 = row.get('Company Phone Number', '').strip()
            phone2 = row.get('Company Phone 2', '').strip()
            phone3 = row.get('Company Phone 3', '').strip()

            if phone1:
                stats['has_phone'] += 1
            if phone1 or phone2 or phone3:
                stats['has_any_phone'] += 1

            # Website
            domain = row.get('Company Domain Name', '').strip()
            if domain:
                stats['has_website'] += 1

            # State
            state = row.get('State/Region', '').strip().upper()
            if state:
                stats['states'][state] += 1

            # Industry
            industry = row.get('Industry', '').strip()
            if industry:
                stats['industries'][industry] += 1

            # Business type
            biz_type = row.get('Business type', '').strip()
            if biz_type:
                stats['business_types'][biz_type] += 1

    # Print results
    print(f"\nTotal Records: {stats['total']:,}")
    print(f"\n--- COVERAGE ---")
    print(f"Has Email:      {stats['has_email']:,} ({stats['has_email']/stats['total']*100:.1f}%)")
    print(f"Has Phone:      {stats['has_phone']:,} ({stats['has_phone']/stats['total']*100:.1f}%)")
    print(f"Has Any Phone:  {stats['has_any_phone']:,} ({stats['has_any_phone']/stats['total']*100:.1f}%)")
    print(f"Has Website:    {stats['has_website']:,} ({stats['has_website']/stats['total']*100:.1f}%)")

    print(f"\n--- TOP STATES ---")
    for state, count in stats['states'].most_common(15):
        print(f"  {state:20} {count:,}")

    print(f"\n--- TOP INDUSTRIES ---")
    for industry, count in stats['industries'].most_common(20):
        print(f"  {industry:40} {count:,}")

    print(f"\n--- TOP BUSINESS TYPES ---")
    for biz_type, count in stats['business_types'].most_common(15):
        print(f"  {biz_type:30} {count:,}")

    return stats


if __name__ == "__main__":
    contacts = analyze_contacts()
    companies = analyze_companies()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Contacts: {contacts['total']:,} records")
    print(f"Companies: {companies['total']:,} records")
    print(f"\nVIC Contacts: {contacts['states'].get('VIC', 0) + contacts['states'].get('VICTORIA', 0):,}")
    print(f"VIC Companies: {companies['states'].get('VIC', 0) + companies['states'].get('VICTORIA', 0):,}")
