"""
Import exactly 3 companies: Paradise Distributors, Reignite Health, JTW Building Group

Strategy:
- Reignite Health: In HubSpot - use HubSpot data for company
- Paradise Distributors: NOT in HubSpot - create from appointment (real company name, not domain)
- JTW Building Group: NOT in HubSpot - create from appointment (real company name, not domain)

Key rules:
- Company names must be proper names, never domains
- Create company entities AND link contacts to them
- Include all appointment data
- Handle SMS conflicts with PHONE_2
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

# The 3 target companies
TARGETS = {
    'reignite health': 'hubspot',  # In HubSpot
    'paradise distributors': 'appointment',  # Not in HubSpot
    'jtw building group': 'appointment'  # Not in HubSpot
}


def find_hubspot_company(target_name):
    """Find exact match in HubSpot companies file."""
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

    # Domain - only if not URL-like
    domain = hubspot_data.get('Company Domain Name', '').strip()
    if domain and not domain.startswith('http') and '/' not in domain:
        attributes["domain"] = domain

    # Phone - validate and normalize
    phone = hubspot_data.get('Company Phone Number', '').strip()
    if phone:
        # Clean and validate
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        if len(cleaned) >= 8:
            attributes["phone_number"] = phone

    # Other fields
    industry = hubspot_data.get('Industry', '').strip()
    if industry:
        attributes["industry"] = industry

    city = hubspot_data.get('City', '').strip()
    state = hubspot_data.get('State/Region', '').strip()
    if city or state:
        attributes["city"] = f"{city}, {state}".strip(', ')

    result = client._request('POST', 'companies', {"attributes": attributes})

    if result.get('success'):
        return result['data'].get('id'), None

    # If phone validation failed, retry without phone
    error = result.get('error', '')
    if 'phone_number' in str(error) and 'phone_number' in attributes:
        print(f"    Retrying without phone (validation failed)...")
        del attributes['phone_number']
        result = client._request('POST', 'companies', {"attributes": attributes})
        if result.get('success'):
            return result['data'].get('id'), "Created without phone (validation failed)"

    return None, result.get('error', 'Unknown error')


def create_company_from_appointment(appt_data):
    """Create Brevo company from appointment data only."""
    name = appt_data.get('company', '').strip()

    if not name:
        return None, "No company name"

    # Only use proper company name - never domain
    attributes = {"name": name}

    # Add location if available
    location = appt_data.get('location', '').strip()
    if location:
        attributes["city"] = location

    # Add website if it's a proper URL (not just domain)
    website = appt_data.get('website_from_list', '').strip()
    if website and website.startswith('http'):
        attributes["website"] = website

    result = client._request('POST', 'companies', {"attributes": attributes})

    if result.get('success'):
        return result['data'].get('id'), None
    return None, result.get('error', 'Unknown error')


def create_contact(appt_data, company_id, company_name, source_type):
    """Create Brevo contact from appointment data and link to company."""
    email = appt_data.get('email', '').strip()

    if not email or '@' not in email:
        return None, "Invalid email"

    # Build attributes
    attributes = {}

    # Name - keep "?" as per user request
    name = appt_data.get('name', '').strip()
    if name and name not in ['.', '∙', '']:
        parts = name.split(None, 1)
        attributes['FIRSTNAME'] = parts[0]
        if len(parts) > 1:
            attributes['LASTNAME'] = parts[1]

    # Company name (as text attribute)
    if company_name:
        attributes['COMPANY'] = company_name

    # Phone
    phone = appt_data.get('phone', '').strip()
    if phone:
        normalized = normalize_australian_mobile(phone)
        if normalized:
            attributes['SMS'] = normalized

    # Appointment data
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

    # Retell log if available
    retell_log = appt_data.get('retell_log', '').strip()
    if retell_log:
        attributes['RETELL_LOG'] = retell_log

    # Source tracking
    attributes['SOURCE'] = f"Appts New (company_source: {source_type})"
    attributes['IMPORT_BATCH'] = "3_companies_v2"

    # Create contact with list assignment
    # List 24 = All Telemarketer, List 28 = Had Appointments
    result = client.add_contact(email, attributes, list_ids=[24, 28])

    if result.get('success'):
        contact_id = result['data'].get('id')

        # Link contact to company
        if company_id and contact_id:
            link_result = client._request('PATCH', f'companies/link-unlink/{company_id}', {
                "linkContactIds": [contact_id]
            })
            if not link_result.get('success'):
                print(f"    Warning: Failed to link contact to company: {link_result.get('error')}")

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
    print("IMPORT 3 COMPANIES: Paradise Distributors, Reignite Health, JTW Building Group")
    print("=" * 70)
    print()

    results = {
        'companies': [],
        'contacts': []
    }

    for company_name, source_type in TARGETS.items():
        print(f"\n{'=' * 50}")
        print(f"PROCESSING: {company_name.upper()}")
        print(f"{'=' * 50}")

        # 1. Find appointment data
        appt = find_appointment(company_name)
        if not appt:
            print(f"  ERROR: No appointment found for {company_name}")
            continue

        print(f"  Contact: {appt.get('name', 'N/A')} <{appt.get('email', 'N/A')}>")
        print(f"  Date: {appt.get('date', 'N/A')} at {appt.get('time', 'N/A')}")
        print(f"  Status: {appt.get('status', 'N/A')} ({appt.get('status_category', 'N/A')})")

        # 2. Create company
        company_id = None
        if source_type == 'hubspot':
            print(f"\n  Looking up in HubSpot...")
            hubspot = find_hubspot_company(company_name)
            if hubspot:
                print(f"  Found HubSpot data:")
                print(f"    Domain: {hubspot.get('Company Domain Name', 'N/A')}")
                print(f"    Phone: {hubspot.get('Company Phone Number', 'N/A')}")
                print(f"    Industry: {hubspot.get('Industry', 'N/A')}")

                company_id, error = create_company_from_hubspot(hubspot)
                if company_id:
                    print(f"  COMPANY CREATED (from HubSpot): ID {company_id}")
                    results['companies'].append({
                        'name': company_name,
                        'id': company_id,
                        'source': 'hubspot'
                    })
                else:
                    print(f"  ERROR creating company: {error}")
            else:
                print(f"  WARNING: HubSpot lookup failed, creating from appointment")
                source_type = 'appointment'  # Fall back

        if source_type == 'appointment':
            print(f"\n  Creating company from appointment data...")
            company_id, error = create_company_from_appointment(appt)
            if company_id:
                print(f"  COMPANY CREATED (from appointment): ID {company_id}")
                results['companies'].append({
                    'name': company_name,
                    'id': company_id,
                    'source': 'appointment'
                })
            else:
                print(f"  ERROR creating company: {error}")

        # 3. Create contact and link to company
        print(f"\n  Creating contact...")
        contact_id, error = create_contact(
            appt,
            company_id,
            appt.get('company', '').strip(),
            source_type
        )

        if contact_id:
            print(f"  CONTACT CREATED: ID {contact_id}")
            if error:
                print(f"    Note: {error}")
            results['contacts'].append({
                'email': appt.get('email', ''),
                'name': appt.get('name', ''),
                'id': contact_id,
                'company_id': company_id
            })
        else:
            print(f"  ERROR creating contact: {error}")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Companies created: {len(results['companies'])}")
    for c in results['companies']:
        print(f"  - {c['name']} (ID: {c['id']}, source: {c['source']})")

    print(f"\nContacts created: {len(results['contacts'])}")
    for c in results['contacts']:
        linked = "linked" if c['company_id'] else "NOT linked"
        print(f"  - {c['name']} <{c['email']}> ({linked})")

    # Save results
    results_file = Path(__file__).parent / 'import_3_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()
