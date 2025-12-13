"""
Import 10 companies from Appts New - CORRECTED APPROACH

Key corrections from v1:
1. Companies MUST come from HubSpot Companies file (not appointment data)
2. Never use domain names as company names
3. Match appointments to existing companies, flag non-matches
4. Keep "?" in names (don't strip)
5. Handle SMS conflicts with PHONE_2

Process:
1. Read first 10 companies from Appts New tab
2. Search HubSpot Companies file for matches
3. Create companies ONLY from HubSpot data
4. Import contacts with COMPANY_MATCH_STATUS flag
"""

import csv
import json
import sys
import time
from pathlib import Path
from brevo_api import BrevoClient, normalize_australian_mobile

# Encoding fix
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Files
HUBSPOT_COMPANIES = Path(r"C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv")
APPOINTMENTS = Path(r"C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv")

client = BrevoClient()

def load_hubspot_companies():
    """Load HubSpot companies into memory with indexes for fast lookup."""
    print("Loading HubSpot Companies (363K records)...")

    companies_by_name = {}  # lowercase name -> company data
    companies_by_domain = {}  # domain -> company data

    with open(HUBSPOT_COMPANIES, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            name = row.get('Company name', '').strip()
            domain = row.get('Company Domain Name', '').strip().lower()

            if name:
                # Store by lowercase name for fuzzy matching
                name_lower = name.lower()
                if name_lower not in companies_by_name:
                    companies_by_name[name_lower] = row

            if domain:
                if domain not in companies_by_domain:
                    companies_by_domain[domain] = row

            count += 1
            if count % 50000 == 0:
                print(f"  Loaded {count:,} companies...")

    print(f"  Total loaded: {count:,}")
    print(f"  Unique names: {len(companies_by_name):,}")
    print(f"  Unique domains: {len(companies_by_domain):,}")

    return companies_by_name, companies_by_domain


def extract_domain_from_email(email):
    """Extract domain from email address."""
    if '@' in email:
        return email.split('@')[1].lower()
    return None


def find_company_in_hubspot(company_name, email, companies_by_name, companies_by_domain):
    """
    Try to find a matching company in HubSpot data.

    Returns: (hubspot_company_data, match_type) or (None, "Not Found")
    """
    # Try exact name match first
    if company_name:
        name_lower = company_name.lower().strip()
        if name_lower in companies_by_name:
            return companies_by_name[name_lower], "exact_name"

        # Try partial name match with stricter rules:
        # - Both names must be at least 5 chars
        # - The shorter name must be at least 60% of the longer name
        best_match = None
        best_score = 0

        for hs_name, hs_data in companies_by_name.items():
            # Skip very short names (single letters, etc.)
            if len(hs_name) < 5 or len(name_lower) < 5:
                continue

            # Check if one contains the other
            if name_lower in hs_name or hs_name in name_lower:
                # Calculate overlap quality
                shorter = min(len(name_lower), len(hs_name))
                longer = max(len(name_lower), len(hs_name))
                ratio = shorter / longer

                # Only accept if good overlap (60%+)
                if ratio >= 0.6 and ratio > best_score:
                    best_match = hs_data
                    best_score = ratio

        if best_match:
            return best_match, "partial_name"

    # Try email domain match
    if email:
        domain = extract_domain_from_email(email)
        if domain and domain in companies_by_domain:
            return companies_by_domain[domain], "email_domain"

    return None, "Not Found"


def is_valid_phone(phone):
    """Check if phone looks like a valid phone number."""
    if not phone:
        return False
    # Remove common separators
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    # Should have at least 8 digits and start with + or digit
    return len(cleaned) >= 8 and (cleaned.startswith('+') or cleaned[0].isdigit())


def create_brevo_company(hubspot_data, match_type):
    """Create a company in Brevo from HubSpot data."""
    name = hubspot_data.get('Company name', '').strip()

    if not name:
        return None, "No company name"

    # Build company attributes from HubSpot data
    attributes = {
        "name": name,
    }

    # Add domain if available (not a URL, just domain)
    domain = hubspot_data.get('Company Domain Name', '').strip()
    if domain and not domain.startswith('http'):
        attributes["domain"] = domain

    # Add optional fields - validate phone before adding
    phone = hubspot_data.get('Company Phone Number', '').strip()
    if phone and is_valid_phone(phone):
        # Normalize to international format if Australian
        normalized = normalize_australian_mobile(phone)
        if normalized:
            attributes["phone_number"] = normalized

    industry = hubspot_data.get('Industry', '').strip()
    if industry:
        attributes["industry"] = industry

    employees = hubspot_data.get('Number of Employees', '').strip()
    if employees:
        try:
            attributes["number_of_employees"] = int(float(employees))
        except:
            pass

    revenue = hubspot_data.get('Annual Revenue', '').strip()
    if revenue:
        try:
            attributes["revenue"] = int(float(revenue))
        except:
            pass

    # Create in Brevo
    result = client._request('POST', 'companies', {"attributes": attributes})

    if result.get('success'):
        return result['data'].get('id'), None
    else:
        return None, result.get('error', 'Unknown error')


def create_brevo_contact(appt_row, company_id, company_match_status, company_name_used):
    """Create a contact in Brevo from appointment data."""
    email = appt_row.get('email', '').strip()
    if not email or '@' not in email:
        return None, "Invalid email"

    # Build attributes - keep "?" in names per user correction
    attributes = {}

    name = appt_row.get('name', '').strip()
    if name and name != '.' and name != '∙':
        # Split name into first/last if space present
        parts = name.split(None, 1)
        attributes['FIRSTNAME'] = parts[0]
        if len(parts) > 1:
            attributes['LASTNAME'] = parts[1]

    # Phone - try SMS first, fall back to PHONE_2 on conflict
    phone = appt_row.get('phone', '').strip()
    if phone:
        normalized = normalize_australian_mobile(phone)
        if normalized:
            attributes['SMS'] = normalized

    # Company info
    if company_name_used:
        attributes['COMPANY'] = company_name_used

    # Appointment data
    date = appt_row.get('date', '').strip()
    if date:
        attributes['APPOINTMENT_DATE'] = date

    time_val = appt_row.get('time', '').strip()
    if time_val:
        attributes['APPOINTMENT_TIME'] = time_val

    status = appt_row.get('status', '').strip()
    if status:
        attributes['APPOINTMENT_STATUS'] = status

    status_cat = appt_row.get('status_category', '').strip()
    if status_cat:
        attributes['DEAL_STAGE'] = status_cat

    quality = appt_row.get('quality', '').strip()
    if quality:
        attributes['QUALITY'] = quality

    # Track company match status (new attribute)
    attributes['SOURCE'] = f"Appts New (company_match: {company_match_status})"
    attributes['IMPORT_BATCH'] = "test_10_companies_v2"

    # Create contact
    result = client.add_contact(email, attributes, list_ids=[24, 28])  # All + Appointments

    if result.get('success'):
        contact_id = result['data'].get('id')

        # Link to company if we have one
        if company_id and contact_id:
            link_result = client._request('PATCH', f'companies/link-unlink/{company_id}', {
                "linkContactIds": [contact_id]
            })

        return contact_id, None
    else:
        error = result.get('error', '')

        # Handle SMS conflict by moving to PHONE_2
        if 'SMS is already associated' in str(error):
            # Remove SMS and retry with PHONE_2
            phone = attributes.pop('SMS', None)
            if phone:
                attributes['PHONE_2'] = phone

            result = client.add_contact(email, attributes, list_ids=[24, 28])
            if result.get('success'):
                return result['data'].get('id'), "SMS moved to PHONE_2"

        return None, error


def main():
    print("=" * 70)
    print("CORRECTED IMPORT: 10 Companies from Appts New")
    print("=" * 70)
    print()
    print("Corrections applied:")
    print("  1. Companies from HubSpot file ONLY (never use domains as names)")
    print("  2. Keep '?' in names")
    print("  3. Flag non-matching companies")
    print("  4. SMS conflicts -> PHONE_2")
    print()

    # Load HubSpot companies
    companies_by_name, companies_by_domain = load_hubspot_companies()
    print()

    # Read Appts New appointments (first 10 with company names)
    print("Reading Appts New appointments...")
    appts_new = []

    with open(APPOINTMENTS, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('source_sheet') == 'Appts New':
                company = row.get('company', '').strip()
                email = row.get('email', '').strip()

                # Only include rows with valid emails
                if email and '@' in email:
                    appts_new.append(row)

    print(f"  Found {len(appts_new)} Appts New contacts with valid emails")

    # Get first 10 that have company names
    appts_with_companies = [a for a in appts_new if a.get('company', '').strip()]
    print(f"  Of these, {len(appts_with_companies)} have company names")

    # Take first 10
    to_import = appts_with_companies[:10]
    print(f"  Will import: {len(to_import)} companies")
    print()

    # Process each appointment
    results = {
        'companies_created': 0,
        'companies_not_found': 0,
        'contacts_created': 0,
        'contacts_failed': 0,
        'details': []
    }

    for i, appt in enumerate(to_import, 1):
        company_name = appt.get('company', '').strip()
        email = appt.get('email', '').strip()
        name = appt.get('name', '').strip()

        print(f"\n[{i}/10] {company_name}")
        print(f"        Contact: {name or 'N/A'} <{email}>")

        # Find company in HubSpot
        hubspot_match, match_type = find_company_in_hubspot(
            company_name, email, companies_by_name, companies_by_domain
        )

        company_id = None
        company_name_used = None

        if hubspot_match:
            print(f"        HubSpot match: {match_type}")
            company_name_used = hubspot_match.get('Company name', '').strip()
            print(f"        Using name: {company_name_used}")

            # Create company in Brevo
            company_id, error = create_brevo_company(hubspot_match, match_type)

            if company_id:
                print(f"        Company created: ID {company_id}")
                results['companies_created'] += 1
            else:
                print(f"        Company error: {error}")
        else:
            print(f"        NO MATCH in HubSpot - flagging as 'Not Found'")
            results['companies_not_found'] += 1
            company_name_used = company_name  # Use original name, but don't create company

        # Create contact
        contact_id, error = create_brevo_contact(
            appt, company_id, match_type, company_name_used
        )

        if contact_id:
            print(f"        Contact created: ID {contact_id}")
            if error:
                print(f"        Note: {error}")
            results['contacts_created'] += 1
        else:
            print(f"        Contact FAILED: {error}")
            results['contacts_failed'] += 1

        results['details'].append({
            'appointment_company': company_name,
            'email': email,
            'hubspot_match': match_type,
            'company_id': company_id,
            'contact_id': contact_id
        })

        time.sleep(0.2)  # Rate limit

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Companies created (from HubSpot): {results['companies_created']}")
    print(f"Companies NOT found in HubSpot: {results['companies_not_found']}")
    print(f"Contacts created: {results['contacts_created']}")
    print(f"Contacts failed: {results['contacts_failed']}")
    print()

    # Show non-matches
    not_found = [d for d in results['details'] if d['hubspot_match'] == 'Not Found']
    if not_found:
        print("Companies NOT found in HubSpot (flagged):")
        for d in not_found:
            print(f"  - {d['appointment_company']} ({d['email']})")

    # Save results
    results_file = Path(__file__).parent / 'import_10_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()
