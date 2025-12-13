"""
Import 5 companies - V4.2 COMPLETE
Imports from ALL sources: HubSpot Companies + HubSpot Contacts + Appointments + Call Logs

V4.2 ADDS:
- HubSpot Contacts CSV lookup (207K contacts, 46 fields)
- 26 new contact-level attributes
- 5 test companies (was 3)

Companies:
- Reignite Health (HubSpot Company + Appointment)
- Paradise Distributors (HubSpot Company + Appointment)
- JTW Building Group (Appointment only)
- Lumiere Home Renovations (HubSpot Company + HubSpot Contact + Appointment) - FULL ENRICHMENT
- CLG Electrics (HubSpot Contact + Appointment)
"""

import csv
import json
import sys
from pathlib import Path
from brevo_api import BrevoClient, normalize_australian_mobile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HUBSPOT_COMPANIES = Path(r"C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv")
HUBSPOT_CONTACTS = Path(r"C:\Users\peter\Documents\HS\All_Contacts_2025_07_07_Cleaned.csv")
APPOINTMENTS = Path(r"C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv")
CALL_LOG_1 = Path(r"C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json")
CALL_LOG_2 = Path(r"C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json")

client = BrevoClient()

# Target companies - ALWAYS check HubSpot first for ALL companies
# Only use 'appointment' as fallback if not found in HubSpot
TARGETS = [
    'Reignite Health',
    'Paradise Distributors',
    'JTW building group',
    'Lumiere Home Renovations',  # v4.2: Has HubSpot Company + Contact + Appointment
    'CLG Electrics'              # v4.2: Has HubSpot Contact + Appointment (no company)
]


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


def find_hubspot_contact(email):
    """Find contact by email in HubSpot Contacts CSV and return ALL available fields."""
    if not email:
        return None
    target_email = email.lower().strip()
    with open(HUBSPOT_CONTACTS, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_email = row.get('Email', '').strip().lower()
            if row_email == target_email:
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

    # Note: Brevo companies don't have built-in city/location fields
    # Location data will be stored on the contact instead
    # We could create custom company attributes but for now skip on company

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

    # Return hubspot_data even on failure so contact can still be enriched
    return None, hubspot_data, result.get('error', 'Unknown error')


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

    # Note: Brevo companies don't have built-in city/location fields
    # Location data will be stored on the contact instead

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


def create_contact(appt_data, company_id, company_name, source_type, hubspot_data=None, hubspot_contact_data=None, all_calls=None):
    """Create Brevo contact with ALL fields from all sources (Company + Contact CSVs)."""
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

        # Reviews (check both columns - HubSpot has "Total Google reviews" and "Total Google reviews 2")
        reviews = hubspot_data.get('Total Google reviews', '').strip()
        if not reviews:
            reviews = hubspot_data.get('Total Google reviews 2', '').strip()
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

        # === ALL REMAINING HUBSPOT FIELDS (v4.1 - import EVERYTHING) ===

        # Time Zone
        timezone = hubspot_data.get('Time Zone', '').strip()
        if timezone:
            attributes['TIMEZONE'] = timezone

        # HubSpot dates
        create_date = hubspot_data.get('Create Date-Time', '').strip()
        if create_date:
            attributes['HUBSPOT_CREATE_DATE'] = create_date

        modified_date = hubspot_data.get('Biz - Last Modified Date', '').strip()
        if modified_date:
            attributes['HUBSPOT_MODIFIED_DATE'] = modified_date

        # LinkedIn Bio (separate from LinkedIn Company Page)
        linkedin_bio = hubspot_data.get('LinkedIn Bio', '').strip()
        if linkedin_bio:
            attributes['LINKEDIN_BIO'] = linkedin_bio[:500]  # Limit length

        # Is Public company
        is_public = hubspot_data.get('Is Public', '').strip()
        if is_public:
            attributes['IS_PUBLIC_COMPANY'] = is_public.lower() == 'true'

        # Traffic source / attribution fields
        latest_traffic = hubspot_data.get('Biz - Latest Traffic Source', '').strip()
        if latest_traffic:
            attributes['LATEST_TRAFFIC_SOURCE'] = latest_traffic

        latest_traffic_1 = hubspot_data.get('Biz - Latest Traffic Source Data 1', '').strip()
        if latest_traffic_1:
            attributes['LATEST_TRAFFIC_SOURCE_1'] = latest_traffic_1

        latest_traffic_2 = hubspot_data.get('Biz - Latest Traffic Source Data 2', '').strip()
        if latest_traffic_2:
            attributes['LATEST_TRAFFIC_SOURCE_2'] = latest_traffic_2

        # Original source fields
        orig_source_1 = hubspot_data.get('Biz - Original Source Data 1', '').strip()
        if orig_source_1:
            attributes['ORIGINAL_SOURCE_1'] = orig_source_1

        orig_source_2 = hubspot_data.get('Biz - Original Source Data 2', '').strip()
        if orig_source_2:
            attributes['ORIGINAL_SOURCE_2'] = orig_source_2

        orig_source_type = hubspot_data.get('Biz - Original Source Type', '').strip()
        if orig_source_type:
            attributes['ORIGINAL_SOURCE_TYPE'] = orig_source_type

        # HubSpot internal tracking
        record_source = hubspot_data.get('Biz - Record source', '').strip()
        if record_source:
            attributes['HUBSPOT_RECORD_SOURCE'] = record_source

        updated_by = hubspot_data.get('Biz - Updated by user ID', '').strip()
        if updated_by:
            attributes['HUBSPOT_UPDATED_BY'] = updated_by

        # Raw JSON blob (store everything)
        raw_json = hubspot_data.get('HubSpot_LongText_JSON', '').strip()
        if raw_json:
            attributes['HUBSPOT_RAW_JSON'] = raw_json[:2000]  # Brevo text limit

    # === HUBSPOT CONTACT ENRICHMENT (v4.2 - ALL 46 contact fields) ===
    if hubspot_contact_data:
        # Identity (only if not already set from appointment)
        if 'FIRSTNAME' not in attributes:
            fname = hubspot_contact_data.get('First Name', '').strip()
            if fname:
                attributes['FIRSTNAME'] = fname
        if 'LASTNAME' not in attributes:
            lname = hubspot_contact_data.get('Last Name', '').strip()
            if lname:
                attributes['LASTNAME'] = lname
        if 'COMPANY' not in attributes:
            co_name = hubspot_contact_data.get('Company Name', '').strip()
            if co_name:
                attributes['COMPANY'] = co_name

        # HubSpot Contact ID
        hs_contact_id = hubspot_contact_data.get('Legacy  Record ID', '').strip()
        if hs_contact_id:
            attributes['HUBSPOT_CONTACT_ID'] = hs_contact_id

        # Phone numbers from HubSpot Contacts (fill in gaps)
        if 'SMS' not in attributes:
            mobile = hubspot_contact_data.get('Mobile Phone Number', '').strip()
            if mobile:
                normalized = normalize_australian_mobile(mobile)
                if normalized:
                    attributes['SMS'] = normalized

        phone1 = hubspot_contact_data.get('Phone Number 1', '').strip()
        if phone1:
            normalized = normalize_australian_mobile(phone1)
            if normalized and normalized != attributes.get('SMS'):
                attributes['PHONE_1'] = normalized

        if 'PHONE_2' not in attributes:
            mobile2 = hubspot_contact_data.get('Mobile Phone 2', '').strip()
            if mobile2:
                normalized = normalize_australian_mobile(mobile2)
                if normalized:
                    attributes['PHONE_2'] = normalized

        if 'PHONE_3' not in attributes:
            mobile3 = hubspot_contact_data.get('Mobile Phone 3', '').strip()
            if mobile3:
                normalized = normalize_australian_mobile(mobile3)
                if normalized:
                    attributes['PHONE_3'] = normalized

        # Email validation from HubSpot
        hs_email_valid = hubspot_contact_data.get('Email Validation', '').strip()
        if hs_email_valid and 'EMAIL_VALIDATION' not in attributes:
            attributes['EMAIL_VALIDATION'] = hs_email_valid

        neverbounce = hubspot_contact_data.get('NeverBounce Validation Result', '').strip()
        if neverbounce:
            attributes['NEVERBOUNCE_RESULT'] = neverbounce

        # Location (fill gaps if not from company)
        if 'CITY' not in attributes:
            city = hubspot_contact_data.get('City', '').strip()
            if city:
                attributes['CITY'] = city
        if 'STATE_REGION' not in attributes:
            state = hubspot_contact_data.get('State/Region', '').strip()
            if state:
                attributes['STATE_REGION'] = state
        if 'POSTAL_CODE' not in attributes:
            postal = hubspot_contact_data.get('Postal Code', '').strip()
            if postal:
                attributes['POSTAL_CODE'] = postal
        if 'STREET_ADDRESS' not in attributes:
            street = hubspot_contact_data.get('Street Address', '').strip()
            if street:
                attributes['STREET_ADDRESS'] = street
        if 'COUNTRY' not in attributes:
            country = hubspot_contact_data.get('Country', '').strip()
            if country:
                attributes['COUNTRY'] = country

        # Work info
        job_title = hubspot_contact_data.get('Job Title', '').strip()
        if job_title:
            attributes['JOBTITLE'] = job_title  # Note: JOB_TITLE is reserved by Brevo

        work_email = hubspot_contact_data.get('Work email', '').strip()
        if work_email:
            attributes['WORK_EMAIL'] = work_email

        website = hubspot_contact_data.get('Website URL', '').strip()
        if website and 'WEBSITE' not in attributes:
            attributes['WEBSITE'] = website

        # Contact owner / team
        owner = hubspot_contact_data.get('Biz- Contact owner', '').strip()
        if owner:
            attributes['CONTACT_OWNER'] = owner

        team = hubspot_contact_data.get('Biz- Team', '').strip()
        if team:
            attributes['HUBSPOT_TEAM'] = team

        # Lead info
        lead_source = hubspot_contact_data.get('Biz- Lead Source', '').strip()
        if lead_source:
            attributes['LEAD_SOURCE'] = lead_source

        lead_status = hubspot_contact_data.get('Biz- lead Status', '').strip()
        if lead_status:
            attributes['LEAD_STATUS'] = lead_status

        lead_type = hubspot_contact_data.get('Biz- Lead Type', '').strip()
        if lead_type:
            attributes['LEAD_TYPE'] = lead_type

        # Original source (contact-level)
        contact_orig = hubspot_contact_data.get('Biz- Original Source', '').strip()
        if contact_orig:
            attributes['CONTACT_ORIGINAL_SOURCE'] = contact_orig

        contact_orig_1 = hubspot_contact_data.get('Biz- Original Source Drill-Down 1', '').strip()
        if contact_orig_1:
            attributes['CONTACT_ORIGINAL_SOURCE_1'] = contact_orig_1

        contact_orig_2 = hubspot_contact_data.get('Biz- Original Source Drill-Down 2', '').strip()
        if contact_orig_2:
            attributes['CONTACT_ORIGINAL_SOURCE_2'] = contact_orig_2

        # Record source (contact-level)
        contact_rec_src = hubspot_contact_data.get('Biz- Record source', '').strip()
        if contact_rec_src:
            attributes['CONTACT_RECORD_SOURCE'] = contact_rec_src

        contact_rec_detail = hubspot_contact_data.get('Biz- Record source detail 1', '').strip()
        if contact_rec_detail:
            attributes['CONTACT_RECORD_SOURCE_DETAIL'] = contact_rec_detail

        # Dates
        contact_create = hubspot_contact_data.get('Biz- Create Date-Time', '').strip()
        if contact_create:
            attributes['HUBSPOT_CONTACT_CREATE_DATE'] = contact_create

        last_activity = hubspot_contact_data.get('Biz- Last Activity Date-Time', '').strip()
        if last_activity:
            attributes['LAST_ACTIVITY_DATE'] = last_activity

        created_by = hubspot_contact_data.get('Biz- Created by user ID', '').strip()
        if created_by:
            attributes['HUBSPOT_CONTACT_CREATED_BY'] = created_by

        # Social / online
        twitter = hubspot_contact_data.get('Twitter Profile', '').strip()
        if twitter:
            attributes['TWITTER_PROFILE'] = twitter

        google_page = hubspot_contact_data.get('Biz- Google Page URL', '').strip()
        if google_page:
            attributes['GOOGLE_PAGE_URL'] = google_page

        # Additional fields
        email_domain = hubspot_contact_data.get('Email Domain', '').strip()
        if email_domain:
            attributes['EMAIL_DOMAIN'] = email_domain

        bounce_reason = hubspot_contact_data.get('Biz- Email hard bounce reason', '').strip()
        if bounce_reason:
            attributes['EMAIL_BOUNCE_REASON'] = bounce_reason

        score_active = hubspot_contact_data.get('Biz- Score ACTIVE', '').strip()
        if score_active:
            attributes['HUBSPOT_SCORE_ACTIVE'] = score_active

        ip_country = hubspot_contact_data.get('IP Country Code', '').strip()
        if ip_country:
            attributes['IP_COUNTRY_CODE'] = ip_country

        country_origin = hubspot_contact_data.get('Country of Origin', '').strip()
        if country_origin:
            attributes['COUNTRY_OF_ORIGIN'] = country_origin

        tag = hubspot_contact_data.get('Biz- Tag', '').strip()
        if tag:
            attributes['HUBSPOT_TAG'] = tag

        # HubSpot association IDs
        hs_company_ids = hubspot_contact_data.get('Biz - Associated Company IDs', '').strip()
        if hs_company_ids:
            attributes['HUBSPOT_COMPANY_IDS'] = hs_company_ids

        hs_primary_company = hubspot_contact_data.get('Biz- Associated Company IDs (Primary)', '').strip()
        if hs_primary_company:
            attributes['HUBSPOT_PRIMARY_COMPANY_ID'] = hs_primary_company

        hs_sequence_ids = hubspot_contact_data.get('Biz- Associated Sequence enrollment IDs', '').strip()
        if hs_sequence_ids:
            attributes['HUBSPOT_SEQUENCE_IDS'] = hs_sequence_ids

        hs_task_ids = hubspot_contact_data.get('Biz- Associated Task IDs', '').strip()
        if hs_task_ids:
            attributes['HUBSPOT_TASK_IDS'] = hs_task_ids

        hs_email_ids = hubspot_contact_data.get('Biz- Associated Email IDs', '').strip()
        if hs_email_ids:
            attributes['HUBSPOT_EMAIL_IDS'] = hs_email_ids

        # Legacy import info
        legacy_import = hubspot_contact_data.get('Legacy Import (concatenated)', '').strip()
        if legacy_import:
            attributes['HUBSPOT_LEGACY_IMPORT'] = legacy_import[:2000]

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
        # Get contact ID - might be in response or need to look up if contact was updated
        contact_id = None
        if result.get('data'):
            contact_id = result['data'].get('id')

        # If no ID returned (update case), look up the contact
        if not contact_id:
            lookup = client.get_contact(email)
            if lookup.get('success') and lookup.get('data'):
                contact_id = lookup['data'].get('id')

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
                contact_id = None
                if result.get('data'):
                    contact_id = result['data'].get('id')
                if not contact_id:
                    lookup = client.get_contact(email)
                    if lookup.get('success') and lookup.get('data'):
                        contact_id = lookup['data'].get('id')
                if company_id and contact_id:
                    client._request('PATCH', f'companies/link-unlink/{company_id}', {
                        "linkContactIds": [contact_id]
                    })
                return contact_id, "SMS moved to PHONE_2"

        return None, error


def main():
    print("=" * 70)
    print("IMPORT 5 COMPANIES - V4.2 (ALL HUBSPOT DATA)")
    print("=" * 70)
    print()
    print("v4.2 sources:")
    print("  + HubSpot Companies CSV (363K companies)")
    print("  + HubSpot Contacts CSV (207K contacts)")
    print("  + Appointments Enriched")
    print("  + Call Logs (22K calls)")
    print()

    # Load call logs for enhanced RETELL_LOG
    print("Loading call logs...")
    all_calls = load_call_logs()
    print(f"  Loaded {len(all_calls)} calls")

    results = {'companies': [], 'contacts': []}

    for company_name in TARGETS:
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

        # Create company - ALWAYS check HubSpot first
        company_id = None
        hubspot_data = None
        source_type = 'appointment'  # Default fallback

        print(f"\n  Looking up in HubSpot...")
        hubspot_data = find_hubspot_company(company_name)
        if hubspot_data:
            source_type = 'hubspot'
            print(f"  FOUND in HubSpot: {hubspot_data.get('Company name')}")
            print(f"    Domain: {hubspot_data.get('Company Domain Name', 'N/A')}")
            print(f"    Phone: {hubspot_data.get('Company Phone Number', 'N/A')}")
            print(f"    Email: {hubspot_data.get('Company Email', 'N/A')}")
            print(f"    Industry: {hubspot_data.get('Industry', 'N/A')}")
            print(f"    Business Type: {hubspot_data.get('Business type', 'N/A')}")
            print(f"    City: {hubspot_data.get('City', 'N/A')}")
            print(f"    State: {hubspot_data.get('State/Region', 'N/A')}")
            print(f"    Address: {hubspot_data.get('Street Address 1', 'N/A')}")
            print(f"    Rating: {hubspot_data.get('GBP rating', 'N/A')}")
            company_id, hubspot_data, error = create_company_from_hubspot(hubspot_data)
            if company_id:
                print(f"  COMPANY CREATED (HubSpot): {company_id}")
                results['companies'].append({
                    'name': company_name, 'id': company_id, 'source': 'hubspot'
                })
            else:
                print(f"  ERROR creating from HubSpot: {error}")
        else:
            print(f"  NOT found in HubSpot, using appointment data...")
            company_id, _, error = create_company_from_appointment(appt)
            if company_id:
                print(f"  COMPANY CREATED (appointment): {company_id}")
                results['companies'].append({
                    'name': company_name, 'id': company_id, 'source': 'appointment'
                })
            else:
                print(f"  ERROR: {error}")

        # Look up contact in HubSpot Contacts CSV
        contact_email = appt.get('email', '').strip()
        hubspot_contact_data = find_hubspot_contact(contact_email)
        if hubspot_contact_data:
            print(f"\n  FOUND in HubSpot Contacts CSV!")
            print(f"    Job Title: {hubspot_contact_data.get('Job Title', 'N/A')}")
            print(f"    Lead Source: {hubspot_contact_data.get('Biz- Lead Source', 'N/A')}")
            print(f"    Lead Status: {hubspot_contact_data.get('Biz- lead Status', 'N/A')}")
        else:
            print(f"\n  NOT in HubSpot Contacts CSV")

        # Create contact with HubSpot enrichment (Company + Contact data)
        print(f"  Creating contact...")
        contact_id, error = create_contact(
            appt, company_id, appt.get('company', '').strip(),
            source_type, hubspot_data, hubspot_contact_data, all_calls
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
                'hubspot_company_enriched': hubspot_data is not None,
                'hubspot_contact_enriched': hubspot_contact_data is not None
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
        enrichments = []
        if c.get('hubspot_company_enriched'):
            enrichments.append("Company")
        if c.get('hubspot_contact_enriched'):
            enrichments.append("Contact")
        enriched = f"+ HubSpot: {', '.join(enrichments)}" if enrichments else ""
        print(f"  - {c['email']} ({linked}) {enriched}")

    # Save results
    results_file = Path(__file__).parent / 'import_3_results_v4.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults: {results_file}")


if __name__ == "__main__":
    main()
