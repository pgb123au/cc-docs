"""
Import 3 companies - V3 COMPLETE
Fixes all identified errors and omissions from v2.

FIXES:
1. Add WAS_CALLED attribute
2. Add EMAIL_VALID attribute
3. Add phone from phone_from_list (only if match_source is reliable)
4. Add MATCH_SOURCE to track data quality
5. Improve RETELL_LOG format where possible
6. Add SOURCE_SHEET to track origin

Companies:
- Reignite Health (in HubSpot)
- Paradise Distributors (not in HubSpot)
- JTW Building Group (not in HubSpot)
"""

import csv
import json
import sys
from pathlib import Path
from brevo_api import BrevoClient, normalize_australian_mobile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HUBSPOT_COMPANIES = Path(r"C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv")
APPOINTMENTS = Path(r"C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv")

client = BrevoClient()

# Target companies
TARGETS = {
    'reignite health': 'hubspot',
    'paradise distributors': 'appointment',
    'jtw building group': 'appointment'
}


def find_hubspot_company(target_name):
    """Find exact match in HubSpot."""
    target_lower = target_name.lower().strip()
    with open(HUBSPOT_COMPANIES, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Company name', '').strip()
            if name.lower() == target_lower:
                return row
    return None


def find_appointment(company_name):
    """Find appointment data for a company."""
    target_lower = company_name.lower().strip()
    with open(APPOINTMENTS, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company = row.get('company', '').strip()
            if company.lower() == target_lower:
                return row
    return None


def create_company_from_hubspot(hubspot_data):
    """Create Brevo company from HubSpot data."""
    name = hubspot_data.get('Company name', '').strip()
    attributes = {"name": name}

    # Domain
    domain = hubspot_data.get('Company Domain Name', '').strip()
    if domain and not domain.startswith('http') and '/' not in domain:
        attributes["domain"] = domain

    # Phone - with retry on failure
    phone = hubspot_data.get('Company Phone Number', '').strip()
    if phone:
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        if len(cleaned) >= 8:
            attributes["phone_number"] = phone

    # Industry
    industry = hubspot_data.get('Industry', '').strip()
    if industry:
        attributes["industry"] = industry

    # Location
    city = hubspot_data.get('City', '').strip()
    state = hubspot_data.get('State/Region', '').strip()
    if city or state:
        location = ', '.join(filter(None, [city, state]))
        attributes["city"] = location

    result = client._request('POST', 'companies', {"attributes": attributes})

    if result.get('success'):
        return result['data'].get('id'), None

    # Retry without phone if validation failed
    error = result.get('error', '')
    if 'phone_number' in str(error) and 'phone_number' in attributes:
        print(f"    Retrying without phone (validation failed)...")
        del attributes['phone_number']
        result = client._request('POST', 'companies', {"attributes": attributes})
        if result.get('success'):
            return result['data'].get('id'), "Created without phone"

    return None, result.get('error', 'Unknown error')


def create_company_from_appointment(appt_data):
    """Create Brevo company from appointment data."""
    name = appt_data.get('company', '').strip()
    if not name:
        return None, "No company name"

    attributes = {"name": name}

    # Location if available
    location = appt_data.get('location', '').strip()
    if location:
        attributes["city"] = location

    result = client._request('POST', 'companies', {"attributes": attributes})

    if result.get('success'):
        return result['data'].get('id'), None
    return None, result.get('error', 'Unknown error')


def create_contact(appt_data, company_id, company_name, source_type):
    """Create Brevo contact with ALL fields from appointment data."""
    email = appt_data.get('email', '').strip()
    if not email or '@' not in email:
        return None, "Invalid email"

    attributes = {}

    # === IDENTITY ===
    name = appt_data.get('name', '').strip()
    if name and name not in ['.', '\u2219', '']:
        parts = name.split(None, 1)
        attributes['FIRSTNAME'] = parts[0]
        if len(parts) > 1:
            attributes['LASTNAME'] = parts[1]

    # Company name
    if company_name:
        attributes['COMPANY'] = company_name

    # === PHONE ===
    # Use phone_from_list only if match_source is reliable (email match)
    phone_from_list = appt_data.get('phone_from_list', '').strip()
    match_source = appt_data.get('match_source', '').strip()

    if phone_from_list and match_source == 'email':
        # Reliable match - use as primary SMS
        normalized = normalize_australian_mobile(phone_from_list)
        if normalized:
            attributes['SMS'] = normalized
    elif phone_from_list and match_source == 'domain':
        # Less reliable - store in PHONE_2 with note
        normalized = normalize_australian_mobile(phone_from_list)
        if normalized:
            attributes['PHONE_2'] = normalized
            # Note: this is a domain-matched phone, less reliable

    # === APPOINTMENT DATA ===
    date = appt_data.get('date', '').strip()
    if date:
        attributes['APPOINTMENT_DATE'] = date

    time_val = appt_data.get('time', '').strip()
    if time_val:
        attributes['APPOINTMENT_TIME'] = time_val

    status = appt_data.get('status', '').strip()
    if status:
        attributes['APPOINTMENT_STATUS'] = status

    status_cat = appt_data.get('status_category', '').strip()
    if status_cat:
        attributes['DEAL_STAGE'] = status_cat

    quality = appt_data.get('quality', '').strip()
    if quality:
        attributes['QUALITY'] = quality

    followup = appt_data.get('followup', '').strip()
    if followup:
        attributes['FOLLOWUP_STATUS'] = followup

    # === CALL DATA ===
    retell_log = appt_data.get('retell_log', '').strip()
    if retell_log:
        attributes['RETELL_LOG'] = retell_log

    # === DATA QUALITY FLAGS (NEW in v3) ===
    was_called = appt_data.get('was_called', '').strip()
    if was_called:
        attributes['WAS_CALLED'] = was_called.lower() == 'true'

    email_valid = appt_data.get('email_valid', '').strip()
    if email_valid:
        attributes['EMAIL_VALID'] = email_valid.lower() == 'true'

    if match_source:
        attributes['MATCH_SOURCE'] = match_source

    # === SOURCE TRACKING ===
    source_sheet = appt_data.get('source_sheet', '').strip()
    attributes['SOURCE'] = f"{source_sheet} (company_source: {source_type})"
    attributes['IMPORT_BATCH'] = "3_companies_v3"

    # Create contact
    result = client.add_contact(email, attributes, list_ids=[24, 28])

    if result.get('success'):
        contact_id = result['data'].get('id')

        # Link to company
        if company_id and contact_id:
            link_result = client._request('PATCH', f'companies/link-unlink/{company_id}', {
                "linkContactIds": [contact_id]
            })
            if not link_result.get('success'):
                print(f"    Warning: Failed to link: {link_result.get('error')}")

        return contact_id, None
    else:
        error = result.get('error', '')

        # Handle SMS conflict
        if 'SMS is already associated' in str(error):
            phone = attributes.pop('SMS', None)
            if phone:
                attributes['PHONE_2'] = phone
            result = client.add_contact(email, attributes, list_ids=[24, 28])
            if result.get('success'):
                contact_id = result['data'].get('id')
                if company_id and contact_id:
                    client._request('PATCH', f'companies/link-unlink/{company_id}', {
                        "linkContactIds": [contact_id]
                    })
                return contact_id, "SMS moved to PHONE_2"

        return None, error


def main():
    print("=" * 70)
    print("IMPORT 3 COMPANIES - V3 COMPLETE")
    print("=" * 70)
    print()
    print("Fixes from v2:")
    print("  + WAS_CALLED attribute")
    print("  + EMAIL_VALID attribute")
    print("  + MATCH_SOURCE attribute")
    print("  + Phone from phone_from_list (if reliable)")
    print("  + SOURCE_SHEET tracking")
    print()

    results = {'companies': [], 'contacts': []}

    for company_name, source_type in TARGETS.items():
        print(f"\n{'=' * 50}")
        print(f"PROCESSING: {company_name.upper()}")
        print(f"{'=' * 50}")

        # Find appointment
        appt = find_appointment(company_name)
        if not appt:
            print(f"  ERROR: No appointment found")
            continue

        print(f"  Contact: {appt.get('name', 'N/A')} <{appt.get('email', 'N/A')}>")
        print(f"  Date: {appt.get('date', 'N/A')} at {appt.get('time', 'N/A')}")
        print(f"  Status: {appt.get('status', 'N/A')}")
        print(f"  Was Called: {appt.get('was_called', 'N/A')}")
        print(f"  Email Valid: {appt.get('email_valid', 'N/A')}")
        print(f"  Match Source: {appt.get('match_source', 'N/A')}")
        print(f"  Phone From List: {appt.get('phone_from_list', 'N/A')}")

        # Create company
        company_id = None
        if source_type == 'hubspot':
            print(f"\n  Looking up in HubSpot...")
            hubspot = find_hubspot_company(company_name)
            if hubspot:
                print(f"  Found: {hubspot.get('Company name')}")
                print(f"    Domain: {hubspot.get('Company Domain Name', 'N/A')}")
                print(f"    Industry: {hubspot.get('Industry', 'N/A')}")
                company_id, error = create_company_from_hubspot(hubspot)
                if company_id:
                    print(f"  COMPANY CREATED (HubSpot): {company_id}")
                    results['companies'].append({
                        'name': company_name, 'id': company_id, 'source': 'hubspot'
                    })
                else:
                    print(f"  ERROR: {error}")
            else:
                print(f"  WARNING: Not found in HubSpot, using appointment data")
                source_type = 'appointment'

        if source_type == 'appointment':
            print(f"\n  Creating from appointment data...")
            company_id, error = create_company_from_appointment(appt)
            if company_id:
                print(f"  COMPANY CREATED (appointment): {company_id}")
                results['companies'].append({
                    'name': company_name, 'id': company_id, 'source': 'appointment'
                })
            else:
                print(f"  ERROR: {error}")

        # Create contact
        print(f"\n  Creating contact...")
        contact_id, error = create_contact(
            appt, company_id, appt.get('company', '').strip(), source_type
        )

        if contact_id:
            print(f"  CONTACT CREATED: {contact_id}")
            if error:
                print(f"    Note: {error}")
            results['contacts'].append({
                'email': appt.get('email', ''),
                'name': appt.get('name', ''),
                'id': contact_id,
                'company_id': company_id
            })
        else:
            print(f"  ERROR: {error}")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Companies: {len(results['companies'])}")
    for c in results['companies']:
        print(f"  - {c['name']} ({c['source']})")

    print(f"\nContacts: {len(results['contacts'])}")
    for c in results['contacts']:
        linked = "linked" if c['company_id'] else "NOT linked"
        print(f"  - {c['email']} ({linked})")

    # Save results
    results_file = Path(__file__).parent / 'import_3_results_v3.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults: {results_file}")


if __name__ == "__main__":
    main()
