"""
Import 3 companies - V4 COMPLETE
Fixes ALL field mapping issues identified in the mapping report.

FIXES FROM V3:
1. EMAIL_VALIDATION (was EMAIL_VALID - wrong name)
2. MATCH_SOURCE now exists and stores
3. HubSpot enrichment flows to contacts (COMPANY_DOMAIN, INDUSTRY, etc.)
4. Enhanced RETELL_LOG with call duration, direction, recording
5. All available HubSpot fields mapped

Companies:
- Reignite Health (in HubSpot - full enrichment)
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
CALL_LOG_1 = Path(r"C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json")
CALL_LOG_2 = Path(r"C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json")

client = BrevoClient()

# Target companies
TARGETS = {
    'reignite health': 'hubspot',
    'paradise distributors': 'appointment',
    'jtw building group': 'appointment'
}


def load_call_logs():
    """Load all call logs for enhanced RETELL_LOG."""
    calls = []
    for path in [CALL_LOG_1, CALL_LOG_2]:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                calls.extend(json.load(f))
    return calls


def find_calls_for_phone(phone, calls):
    """Find calls matching a phone number (last 9 digits)."""
    if not phone:
        return []
    # Normalize to last 9 digits
    phone_normalized = ''.join(c for c in str(phone) if c.isdigit())[-9:]
    if len(phone_normalized) < 8:
        return []

    matching_calls = []
    for call in calls:
        to_num = str(call.get('to_number', ''))
        to_normalized = ''.join(c for c in to_num if c.isdigit())[-9:]
        if to_normalized == phone_normalized:
            matching_calls.append(call)

    return sorted(matching_calls, key=lambda x: x.get('start_time', ''))


def format_enhanced_retell_log(calls, basic_log=''):
    """Format enhanced RETELL_LOG with full call details."""
    if not calls:
        return basic_log

    log_lines = []
    for call in calls:
        start = call.get('start_time', '')
        duration = call.get('human_duration', 'N/A')
        direction = call.get('direction', 'outbound').upper()
        recording = call.get('recording_url', '')
        status = call.get('status', '')

        if start:
            # Parse "25/08/2025, 16:45:30" format
            if ',' in start:
                date_part = start.split(',')[0].strip()
                time_full = start.split(',')[1].strip()
                time_short = ':'.join(time_full.split(':')[:2])  # Remove seconds
            else:
                date_part = start
                time_short = ''

            log_line = f'{date_part} {time_short} {direction} ({duration})'
            if status and status != 'ended':
                log_line += f' [{status}]'
            if recording and str(recording) not in ['N/A', 'None', '']:
                log_line += f' Recording: {recording}'
            log_lines.append(log_line)

    return '\n'.join(log_lines) if log_lines else basic_log


def find_hubspot_company(target_name):
    """Find exact match in HubSpot and return ALL available fields."""
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


def try_phone_formats(phone):
    """Generate different phone formats to try with Brevo."""
    if not phone:
        return []

    # Clean to digits only
    digits = ''.join(c for c in phone if c.isdigit())

    formats = []

    # If starts with 61 (Australia)
    if digits.startswith('61') and len(digits) >= 11:
        # +61XXXXXXXXX
        formats.append('+' + digits)
        # Without plus
        formats.append(digits)
        # With spaces: +61 4XX XXX XXX
        if len(digits) == 11:
            formats.append(f'+{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}')
    elif digits.startswith('0') and len(digits) == 10:
        # Australian format starting with 0
        formats.append('+61' + digits[1:])
        formats.append('61' + digits[1:])
    else:
        # Just use what we have
        formats.append(phone)
        formats.append(digits)

    return formats


def create_company_from_hubspot(hubspot_data):
    """Create Brevo company from HubSpot data with ALL available fields."""
    name = hubspot_data.get('Company name', '').strip()
    attributes = {"name": name}

    # Domain
    domain = hubspot_data.get('Company Domain Name', '').strip()
    if domain and not domain.startswith('http') and '/' not in domain:
        attributes["domain"] = domain

    # Industry
    industry = hubspot_data.get('Industry', '').strip()
    if industry:
        attributes["industry"] = industry

    # Location - combine city and state
    city = hubspot_data.get('City', '').strip()
    state = hubspot_data.get('State/Region', '').strip()
    if city or state:
        location = ', '.join(filter(None, [city, state]))
        attributes["city"] = location

    # Phone - try multiple formats
    phone = hubspot_data.get('Company Phone Number', '').strip()
    phone_formats = try_phone_formats(phone) if phone else []

    for phone_fmt in phone_formats:
        attributes["phone_number"] = phone_fmt
        result = client._request('POST', 'companies', {"attributes": attributes})
        if result.get('success'):
            print(f"    Phone accepted in format: {phone_fmt}")
            return result['data'].get('id'), hubspot_data, None
        error = result.get('error', '')
        print(f"    Phone format {phone_fmt} failed: {error}")

    # Try without phone if all formats failed
    if 'phone_number' in attributes:
        del attributes['phone_number']

    result = client._request('POST', 'companies', {"attributes": attributes})
    if result.get('success'):
        return result['data'].get('id'), hubspot_data, f"Created without phone (tried: {phone})"

    return None, None, result.get('error', 'Unknown error')


def extract_domain_from_email(email):
    """Extract business domain from email (skip personal email providers)."""
    if not email or '@' not in email:
        return None
    domain = email.split('@')[1].lower()
    # Skip personal email providers
    personal_domains = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
                       'icloud.com', 'live.com', 'msn.com', 'bigpond.com',
                       'optusnet.com.au', 'mail.com', 'aol.com']
    if domain in personal_domains:
        return None
    return domain


def create_company_from_appointment(appt_data):
    """Create Brevo company from appointment data with ALL available fields."""
    name = appt_data.get('company', '').strip()
    if not name:
        return None, None, "No company name"

    attributes = {"name": name}

    # Domain - extract from email if business email
    email = appt_data.get('email', '').strip()
    domain = extract_domain_from_email(email)
    if domain:
        attributes["domain"] = domain

    # Website from website_from_list
    website = appt_data.get('website_from_list', '').strip()
    if website:
        # Clean up website to get domain if needed
        if website.startswith('http'):
            # Extract domain from URL for company domain if we don't have one
            if 'domain' not in attributes:
                import re
                match = re.search(r'https?://(?:www\.)?([^/]+)', website)
                if match:
                    attributes["domain"] = match.group(1)

    # Location if available
    location = appt_data.get('location', '').strip()
    if location:
        attributes["city"] = location

    # Company from list might be different/better
    company_from_list = appt_data.get('company_from_list', '').strip()
    if company_from_list and company_from_list.lower() != name.lower():
        # Store as additional info - might be alternate name
        pass  # Could add as note if Brevo supports

    print(f"    Company attributes (before phone): {attributes}")

    # Phone - try multiple formats
    phone_from_list = appt_data.get('phone_from_list', '').strip()
    phone_formats = try_phone_formats(phone_from_list) if phone_from_list else []

    for phone_fmt in phone_formats:
        attributes["phone_number"] = phone_fmt
        result = client._request('POST', 'companies', {"attributes": attributes})
        if result.get('success'):
            print(f"    Phone accepted in format: {phone_fmt}")
            return result['data'].get('id'), None, None
        error = result.get('error', '')
        print(f"    Phone format {phone_fmt} failed: {error}")

    # Try without phone if all formats failed or no phone
    if 'phone_number' in attributes:
        del attributes['phone_number']

    result = client._request('POST', 'companies', {"attributes": attributes})
    if result.get('success'):
        warning = f"Created without phone (tried: {phone_from_list})" if phone_from_list else None
        return result['data'].get('id'), None, warning

    return None, None, result.get('error', 'Unknown error')


def create_contact(appt_data, company_id, company_name, source_type, hubspot_data=None, all_calls=None):
    """Create Brevo contact with ALL fields from all sources."""
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
    phone_from_list = appt_data.get('phone_from_list', '').strip()
    match_source = appt_data.get('match_source', '').strip()

    if phone_from_list and match_source == 'email':
        # Reliable match - use as primary SMS
        normalized = normalize_australian_mobile(phone_from_list)
        if normalized:
            attributes['SMS'] = normalized
    elif phone_from_list and match_source == 'domain':
        # Less reliable - store in PHONE_2
        normalized = normalize_australian_mobile(phone_from_list)
        if normalized:
            attributes['PHONE_2'] = normalized

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

    # === ENHANCED RETELL LOG ===
    basic_log = appt_data.get('retell_log', '').strip()
    if phone_from_list and all_calls:
        matching_calls = find_calls_for_phone(phone_from_list, all_calls)
        if matching_calls:
            attributes['RETELL_LOG'] = format_enhanced_retell_log(matching_calls, basic_log)
            attributes['CALL_COUNT'] = len(matching_calls)
        elif basic_log:
            attributes['RETELL_LOG'] = basic_log
    elif basic_log:
        attributes['RETELL_LOG'] = basic_log

    # === DATA QUALITY FLAGS (FIXED in v4) ===
    was_called = appt_data.get('was_called', '').strip()
    if was_called:
        attributes['WAS_CALLED'] = was_called.lower() == 'true'

    # FIX: Use EMAIL_VALIDATION (not EMAIL_VALID)
    email_valid = appt_data.get('email_valid', '').strip()
    if email_valid:
        attributes['EMAIL_VALIDATION'] = 'valid' if email_valid.lower() == 'true' else 'invalid'

    # FIX: MATCH_SOURCE now exists
    if match_source:
        attributes['MATCH_SOURCE'] = match_source

    # === HUBSPOT ENRICHMENT (NEW in v4) ===
    if hubspot_data:
        # Domain
        domain = hubspot_data.get('Company Domain Name', '').strip()
        if domain:
            attributes['COMPANY_DOMAIN'] = domain

        # Industry
        industry = hubspot_data.get('Industry', '').strip()
        if industry:
            attributes['INDUSTRY'] = industry

        # Business type
        biz_type = hubspot_data.get('Business type', '').strip()
        if biz_type:
            attributes['BUSINESS_TYPE'] = biz_type

        # Vertical
        vertical = hubspot_data.get('Vertical', '').strip()
        if vertical:
            attributes['VERTICAL'] = vertical

        # Location
        city = hubspot_data.get('City', '').strip()
        if city:
            attributes['CITY'] = city
        state = hubspot_data.get('State/Region', '').strip()
        if state:
            attributes['STATE_REGION'] = state
        suburb = hubspot_data.get('Suburb', '').strip()
        if suburb:
            attributes['SUBURB'] = suburb
        postal = hubspot_data.get('Postal Code', '').strip()
        if postal:
            attributes['POSTAL_CODE'] = postal
        country = hubspot_data.get('Country/Region', '').strip()
        if country:
            attributes['COUNTRY'] = country
        street1 = hubspot_data.get('Street Address 1', '').strip()
        street2 = hubspot_data.get('Street Address 2', '').strip()
        if street1 or street2:
            attributes['STREET_ADDRESS'] = ', '.join(filter(None, [street1, street2]))

        # Company contact info
        co_email = hubspot_data.get('Company Email', '').strip()
        if co_email:
            attributes['COMPANY_EMAIL'] = co_email
        co_phone = hubspot_data.get('Company Phone Number', '').strip()
        if co_phone:
            attributes['COMPANY_PHONE'] = co_phone

        # Social links
        google = hubspot_data.get('Google profile link', '').strip()
        if google:
            attributes['GOOGLE_PROFILE'] = google
        twitter = hubspot_data.get('Twitter Handle', '').strip()
        if twitter:
            attributes['TWITTER'] = twitter
        facebook = hubspot_data.get('Facebook Company Page', '').strip()
        if facebook:
            attributes['FACEBOOK'] = facebook
        linkedin = hubspot_data.get('LinkedIn Company Page', '').strip()
        if linkedin:
            attributes['LINKEDIN'] = linkedin
        instagram = hubspot_data.get('instagram page', '').strip()
        if instagram:
            attributes['INSTAGRAM'] = instagram
        youtube = hubspot_data.get('Youtube  handle', '').strip()
        if youtube:
            attributes['YOUTUBE'] = youtube

        # Reviews
        reviews = hubspot_data.get('Total Google reviews', '').strip()
        if reviews and reviews.isdigit():
            attributes['GOOGLE_REVIEWS_COUNT'] = int(reviews)
        rating = hubspot_data.get('GBP rating', '').strip()
        if rating:
            try:
                attributes['GBP_RATING'] = float(rating)
            except:
                pass

        # Business info
        revenue = hubspot_data.get('Annual Revenue', '').strip()
        if revenue:
            try:
                attributes['ANNUAL_REVENUE'] = float(revenue.replace(',', '').replace('$', ''))
            except:
                pass
        employees = hubspot_data.get('Number of Employees', '').strip()
        if employees and employees.isdigit():
            attributes['NUMBER_OF_EMPLOYEES'] = int(employees)
        founded = hubspot_data.get('Year Founded', '').strip()
        if founded and founded.isdigit():
            attributes['YEAR_FOUNDED'] = int(founded)

        # Description
        desc = hubspot_data.get('Business Description', '').strip()
        if desc:
            attributes['BUSINESS_DESCRIPTION'] = desc[:500]  # Limit length

        # Marketing
        supplier = hubspot_data.get('Current Online Marketing Supplier', '').strip()
        if supplier:
            attributes['CURRENT_MARKETING_SUPPLIER'] = supplier

        # HubSpot metadata for linking
        legacy_id = hubspot_data.get('Legacy Record ID', '').strip()
        contact_ids = hubspot_data.get('Biz - Associated Contact IDs', '').strip()
        if legacy_id or contact_ids:
            meta = {'legacy_id': legacy_id, 'contact_ids': contact_ids}
            attributes['HUBSPOT_COMPANY_META'] = json.dumps(meta)

    # === APPOINTMENT EXTRA FIELDS ===
    website = appt_data.get('website_from_list', '').strip()
    if website:
        attributes['WEBSITE'] = website

    # Location from appointments (if no HubSpot enrichment)
    if 'CITY' not in attributes:
        location = appt_data.get('location', '').strip()
        if location:
            # Parse "Suburb, State" format
            if ',' in location:
                parts = [p.strip() for p in location.split(',')]
                if parts[0]:
                    attributes['SUBURB'] = parts[0]
                if len(parts) > 1 and parts[1]:
                    # Could be "VIC" or "Victoria"
                    attributes['STATE_REGION'] = parts[1]
            else:
                attributes['CITY'] = location

    # Domain from email (if no HubSpot enrichment)
    if 'COMPANY_DOMAIN' not in attributes:
        email = appt_data.get('email', '').strip()
        domain = extract_domain_from_email(email)
        if domain:
            attributes['COMPANY_DOMAIN'] = domain

    # === SOURCE TRACKING ===
    source_sheet = appt_data.get('source_sheet', '').strip()
    attributes['SOURCE'] = f"{source_sheet} (company_source: {source_type})"
    attributes['IMPORT_BATCH'] = "3_companies_v4"

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
    print("IMPORT 3 COMPANIES - V4 COMPLETE")
    print("=" * 70)
    print()
    print("Fixes from v3:")
    print("  + EMAIL_VALIDATION (was wrong attribute name)")
    print("  + MATCH_SOURCE (now exists)")
    print("  + HubSpot enrichment flows to contacts")
    print("  + Enhanced RETELL_LOG with call details")
    print("  + All HubSpot fields mapped")
    print()

    # Load call logs for enhanced RETELL_LOG
    print("Loading call logs...")
    all_calls = load_call_logs()
    print(f"  Loaded {len(all_calls)} calls")

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
        hubspot_data = None

        if source_type == 'hubspot':
            print(f"\n  Looking up in HubSpot...")
            hubspot_data = find_hubspot_company(company_name)
            if hubspot_data:
                print(f"  Found: {hubspot_data.get('Company name')}")
                print(f"    Domain: {hubspot_data.get('Company Domain Name', 'N/A')}")
                print(f"    Industry: {hubspot_data.get('Industry', 'N/A')}")
                print(f"    City: {hubspot_data.get('City', 'N/A')}")
                company_id, hubspot_data, error = create_company_from_hubspot(hubspot_data)
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
            company_id, _, error = create_company_from_appointment(appt)
            if company_id:
                print(f"  COMPANY CREATED (appointment): {company_id}")
                results['companies'].append({
                    'name': company_name, 'id': company_id, 'source': 'appointment'
                })
            else:
                print(f"  ERROR: {error}")

        # Create contact with HubSpot enrichment
        print(f"\n  Creating contact...")
        contact_id, error = create_contact(
            appt, company_id, appt.get('company', '').strip(),
            source_type, hubspot_data, all_calls
        )

        if contact_id:
            print(f"  CONTACT CREATED: {contact_id}")
            if error:
                print(f"    Note: {error}")
            results['contacts'].append({
                'email': appt.get('email', ''),
                'name': appt.get('name', ''),
                'id': contact_id,
                'company_id': company_id,
                'hubspot_enriched': hubspot_data is not None
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
        enriched = "+ HubSpot enriched" if c.get('hubspot_enriched') else ""
        print(f"  - {c['email']} ({linked}) {enriched}")

    # Save results
    results_file = Path(__file__).parent / 'import_3_results_v4.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults: {results_file}")


if __name__ == "__main__":
    main()
