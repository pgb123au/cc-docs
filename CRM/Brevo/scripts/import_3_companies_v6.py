"""
Import 5 companies - V6 TELCO WAREHOUSE (PostgreSQL)

Imports from ALL sources:
- HubSpot Companies CSV (363K companies)
- HubSpot Contacts CSV (207K contacts)
- Appointments Enriched CSV
- Excel Appointments (phone numbers from "Phone Call" rows)
- Telco Warehouse PostgreSQL (74K calls - Retell + Zadarma + Telnyx)

V6 IMPROVEMENTS:
- Uses Telco Warehouse PostgreSQL instead of JSON files
- Captures ALL providers: Retell (37K), Zadarma (35K), Telnyx (700)
- Full transcripts, sentiment, call_analysis from database
- Real-time queryable data

Reference: C:/Users/peter/Downloads/CC/Telcos/TELCO_WAREHOUSE_CRM_HANDOFF.md

Companies:
- Reignite Health (HubSpot Company + Appointment)
- Paradise Distributors (HubSpot Company + Appointment + Excel Phone + Telco DB)
- JTW Building Group (Appointment + Excel Phone + Telco DB)
- Lumiere Home Renovations (HubSpot Company + Contact + Appointment + Excel Phone + Telco DB)
- CLG Electrics (HubSpot Contact + Appointment + Excel Phone + Telco DB)
"""

import csv
import json
import re
import sys
from pathlib import Path
from datetime import datetime

# Try pandas for Excel, fall back to openpyxl
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# PostgreSQL driver
try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    print("WARNING: psycopg2 not installed. Run: pip install psycopg2-binary")

from brevo_api import BrevoClient, normalize_australian_mobile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# === FILE PATHS ===
HUBSPOT_COMPANIES = Path(r"C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv")
HUBSPOT_CONTACTS = Path(r"C:\Users\peter\Documents\HS\All_Contacts_2025_07_07_Cleaned.csv")
APPOINTMENTS = Path(r"C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv")

# Excel file - try multiple locations (main file might be locked)
EXCEL_PATHS = [
    Path(r"C:\Users\peter\Downloads\CC\CRM\temp_appointments.xlsx"),
    Path(r"C:\Users\peter\OneDrive\Documents\Yes Right Pty Ltd\AI Appointments Set 2025-copy2025-12-12.xlsx"),
    Path(r"C:\Users\peter\OneDrive\Documents\Yes Right Pty Ltd\AI Appointments Set 2025-backup.xlsx"),
    Path(r"C:\Users\peter\OneDrive\Documents\Yes Right Pty Ltd\AI Appointments Set 2025.xlsx"),
]

# === TELCO WAREHOUSE CONNECTION ===
TELCO_DB = {
    'host': '96.47.238.189',
    'port': 5432,
    'database': 'telco_warehouse',
    'user': 'telco_sync',
    'password': 'TelcoSync2024!'
}

# Our phone numbers (to determine call direction)
OUR_NUMBERS = ['61399997398', '61288800208', '61288800226', '61240620999',
               '399997398', '288800208', '288800226', '240620999']

client = BrevoClient()

# Target companies
TARGETS = [
    'Reignite Health',
    'Paradise Distributors',
    'JTW building group',
    'Lumiere Home Renovations',
    'CLG Electrics'
]


# === TELCO WAREHOUSE QUERIES ===

def get_telco_connection():
    """Get PostgreSQL connection to Telco Warehouse."""
    if not HAS_PSYCOPG2:
        return None
    try:
        conn = psycopg2.connect(**TELCO_DB)
        return conn
    except Exception as e:
        print(f"  ERROR connecting to Telco Warehouse: {e}")
        return None


def normalize_phone_for_db(phone):
    """Normalize phone to format used in telco warehouse (without + prefix)."""
    if not phone:
        return ''
    # Remove all non-digits
    digits = ''.join(c for c in str(phone) if c.isdigit())
    # Ensure it starts with 61 for Australian numbers
    if digits.startswith('0') and len(digits) == 10:
        digits = '61' + digits[1:]
    return digits


def find_calls_for_phone_db(phone, conn):
    """Find all calls matching a phone number from Telco Warehouse."""
    if not conn or not phone:
        return []

    phone_normalized = normalize_phone_for_db(phone)
    if len(phone_normalized) < 9:
        return []

    # Use last 9 digits for matching
    phone_suffix = phone_normalized[-9:]

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Query calls from all providers where this phone appears
        query = """
            SELECT
                c.id,
                c.provider_id,
                p.name as provider_name,
                c.external_call_id,
                c.from_number,
                c.to_number,
                c.direction,
                c.started_at,
                c.ended_at,
                c.duration_seconds,
                c.status,
                c.disposition,
                c.hangup_cause,
                c.cost,
                c.currency,
                c.retell_agent_id,
                c.retell_agent_name,
                c.transcript,
                c.full_transcript,
                c.sentiment,
                c.has_recording,
                c.recording_url,
                c.raw_data
            FROM telco.calls c
            JOIN telco.providers p ON c.provider_id = p.provider_id
            WHERE c.from_number LIKE %s OR c.to_number LIKE %s
            ORDER BY c.started_at DESC
        """

        like_pattern = f'%{phone_suffix}'
        cursor.execute(query, (like_pattern, like_pattern))
        rows = cursor.fetchall()
        cursor.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"  ERROR querying calls: {e}")
        return []


def format_duration(seconds):
    """Format seconds into human-readable duration."""
    if not seconds:
        return 'N/A'
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    if secs:
        return f"{minutes}m {secs}s"
    return f"{minutes}m"


def build_telco_attributes(calls, phone):
    """Build Brevo attributes from Telco Warehouse call data."""
    if not calls:
        return {}

    attrs = {}

    # Separate calls by provider
    retell_calls = [c for c in calls if c.get('provider_name') == 'retell']
    zadarma_calls = [c for c in calls if c.get('provider_name') == 'zadarma']
    telnyx_calls = [c for c in calls if c.get('provider_name') == 'telnyx']

    # Total calls across all providers
    attrs['TELCO_TOTAL_CALLS'] = len(calls)

    # Provider breakdown
    if retell_calls:
        attrs['RETELL_CALL_COUNT'] = len(retell_calls)
    if zadarma_calls:
        attrs['ZADARMA_CALL_COUNT'] = len(zadarma_calls)
    if telnyx_calls:
        attrs['TELNYX_CALL_COUNT'] = len(telnyx_calls)

    # Providers used
    providers = []
    if retell_calls:
        providers.append('retell')
    if zadarma_calls:
        providers.append('zadarma')
    if telnyx_calls:
        providers.append('telnyx')
    if providers:
        attrs['TELCO_PROVIDER'] = ', '.join(providers)

    # Use most recent Retell call for detailed attributes (richest data)
    if retell_calls:
        last_retell = retell_calls[0]

        # Call ID and URLs
        call_id = last_retell.get('external_call_id', '')
        if call_id:
            attrs['RETELL_CALL_ID'] = call_id

        recording_url = last_retell.get('recording_url', '')
        if recording_url and recording_url not in ['N/A', 'None', '']:
            attrs['RETELL_RECORDING_URL'] = recording_url

        # Transcript
        transcript = last_retell.get('full_transcript') or last_retell.get('transcript', '')
        if transcript:
            # Brevo has attribute length limits
            if len(transcript) > 10000:
                transcript = transcript[:9990] + '...[truncated]'
            attrs['RETELL_TRANSCRIPT'] = transcript

        # Short transcript / summary
        short_transcript = last_retell.get('transcript', '')
        if short_transcript and short_transcript != transcript:
            attrs['TELCO_CALL_SUMMARY'] = short_transcript[:500]

        # Sentiment
        sentiment = last_retell.get('sentiment', '')
        if sentiment:
            attrs['TELCO_SENTIMENT'] = sentiment

        # Call metadata
        direction = last_retell.get('direction', '')
        if direction:
            attrs['RETELL_CALL_DIRECTION'] = direction.upper()

        duration = last_retell.get('duration_seconds')
        if duration:
            attrs['RETELL_CALL_DURATION'] = format_duration(duration)

        status = last_retell.get('status', '')
        if status:
            attrs['RETELL_CALL_STATUS'] = status

        hangup = last_retell.get('hangup_cause', '')
        if hangup:
            attrs['RETELL_DISCONNECT_REASON'] = hangup

        cost = last_retell.get('cost')
        if cost:
            attrs['RETELL_CALL_COST'] = float(cost)

        # Call analysis from raw_data JSONB
        raw_data = last_retell.get('raw_data', {})
        if raw_data and isinstance(raw_data, dict):
            call_analysis = raw_data.get('call_analysis', {})
            if call_analysis and isinstance(call_analysis, dict):
                summary = call_analysis.get('call_summary', '')
                if summary and 'TELCO_CALL_SUMMARY' not in attrs:
                    attrs['TELCO_CALL_SUMMARY'] = summary[:500]
                user_sentiment = call_analysis.get('user_sentiment', '')
                if user_sentiment and 'TELCO_SENTIMENT' not in attrs:
                    attrs['TELCO_SENTIMENT'] = user_sentiment

    # Build combined log from ALL calls
    log_lines = []
    for call in calls[:20]:  # Limit to 20 most recent
        started = call.get('started_at')
        if started:
            if hasattr(started, 'strftime'):
                date_str = started.strftime('%d/%m/%Y %H:%M')
            else:
                date_str = str(started)[:16]
        else:
            date_str = 'N/A'

        duration = format_duration(call.get('duration_seconds'))
        direction = (call.get('direction') or 'unknown').upper()
        provider = call.get('provider_name', 'unknown')
        disposition = call.get('disposition', '')

        log_line = f"{date_str} {direction} ({duration}) [{provider}]"
        if disposition and disposition not in ['answered', 'completed']:
            log_line += f" - {disposition}"
        log_lines.append(log_line)

    if log_lines:
        attrs['RETELL_LOG'] = '\n'.join(log_lines)

    return attrs


# === EXCEL PHONE EXTRACTION ===

def load_excel_phone_data():
    """Load phone numbers from Excel 'Phone Call' rows."""
    if not HAS_PANDAS:
        print("  WARNING: pandas not installed, skipping Excel phone data")
        return {}

    # Find accessible Excel file
    excel_path = None
    for path in EXCEL_PATHS:
        if path.exists():
            try:
                # Try to open it
                with open(path, 'rb') as f:
                    f.read(1)
                excel_path = path
                break
            except PermissionError:
                continue

    if not excel_path:
        print("  WARNING: No accessible Excel file found")
        return {}

    print(f"  Loading Excel from: {excel_path.name}")

    try:
        df = pd.read_excel(excel_path, header=None)
    except Exception as e:
        print(f"  ERROR reading Excel: {e}")
        return {}

    # Extract phone data by company/email
    phone_data = {}

    for col in range(1, len(df.columns)):
        company = df.iloc[2, col] if len(df) > 2 and pd.notna(df.iloc[2, col]) else None
        email = df.iloc[6, col] if len(df) > 6 and pd.notna(df.iloc[6, col]) else None

        if not company:
            continue

        company = str(company).strip()
        email = str(email).strip().lower() if email else ''

        # Look for phone in Retell Log rows (8-20)
        phone_found = None
        for row in range(8, min(20, len(df))):
            cell = df.iloc[row, col]
            if pd.notna(cell):
                cell_str = str(cell)
                match = re.search(r'Phone Call\s*:\s*\+?(\d+)\s*->\s*\+?(\d+)', cell_str)
                if match:
                    num1, num2 = match.groups()
                    # Determine which is theirs (not ours)
                    if any(our in num2 for our in OUR_NUMBERS):
                        phone_found = '+' + num1
                    else:
                        phone_found = '+' + num2
                    break

        if phone_found:
            # Store by company name (lowercase for matching)
            phone_data[company.lower()] = phone_found
            # Also store by email if available
            if email and '@' in email:
                phone_data[email] = phone_found

    print(f"  Extracted {len(phone_data)} phone numbers from Excel")
    return phone_data


# === HUBSPOT LOOKUPS ===

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
    """Find contact by email in HubSpot Contacts CSV."""
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


# === PHONE FORMAT HELPERS ===

def try_phone_formats(phone):
    """Generate different phone formats to try with Brevo."""
    if not phone:
        return []

    digits = ''.join(c for c in phone if c.isdigit())
    formats = []

    if digits.startswith('61') and len(digits) >= 11:
        formats.append('+' + digits)
        formats.append(digits)
        if len(digits) == 11:
            formats.append(f'+{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}')
    elif digits.startswith('0') and len(digits) == 10:
        formats.append('+61' + digits[1:])
        formats.append('61' + digits[1:])
    else:
        formats.append(phone)
        formats.append(digits)

    return formats


def extract_domain_from_email(email):
    """Extract business domain from email."""
    if not email or '@' not in email:
        return None
    domain = email.split('@')[1].lower()
    personal_domains = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
                       'icloud.com', 'live.com', 'msn.com', 'bigpond.com',
                       'optusnet.com.au', 'mail.com', 'aol.com']
    if domain in personal_domains:
        return None
    return domain


# === COMPANY CREATION ===

def create_company_from_hubspot(hubspot_data):
    """Create Brevo company from HubSpot data."""
    name = hubspot_data.get('Company name', '').strip()
    attributes = {"name": name}

    domain = hubspot_data.get('Company Domain Name', '').strip()
    if domain and not domain.startswith('http') and '/' not in domain:
        attributes["domain"] = domain

    industry = hubspot_data.get('Industry', '').strip()
    if industry:
        attributes["industry"] = industry

    phone = hubspot_data.get('Company Phone Number', '').strip()
    phone_formats = try_phone_formats(phone) if phone else []

    for phone_fmt in phone_formats:
        attributes["phone_number"] = phone_fmt
        result = client._request('POST', 'companies', {"attributes": attributes})
        if result.get('success'):
            return result['data'].get('id'), hubspot_data, None

    if 'phone_number' in attributes:
        del attributes['phone_number']

    result = client._request('POST', 'companies', {"attributes": attributes})
    if result.get('success'):
        return result['data'].get('id'), hubspot_data, f"Created without phone"

    return None, hubspot_data, result.get('error', 'Unknown error')


def create_company_from_appointment(appt_data):
    """Create Brevo company from appointment data."""
    name = appt_data.get('company', '').strip()
    if not name:
        return None, None, "No company name"

    attributes = {"name": name}

    email = appt_data.get('email', '').strip()
    domain = extract_domain_from_email(email)
    if domain:
        attributes["domain"] = domain

    website = appt_data.get('website_from_list', '').strip()
    if website and 'domain' not in attributes:
        match = re.search(r'https?://(?:www\.)?([^/]+)', website)
        if match:
            attributes["domain"] = match.group(1)

    phone_from_list = appt_data.get('phone_from_list', '').strip()
    phone_formats = try_phone_formats(phone_from_list) if phone_from_list else []

    for phone_fmt in phone_formats:
        attributes["phone_number"] = phone_fmt
        result = client._request('POST', 'companies', {"attributes": attributes})
        if result.get('success'):
            return result['data'].get('id'), None, None

    if 'phone_number' in attributes:
        del attributes['phone_number']

    result = client._request('POST', 'companies', {"attributes": attributes})
    if result.get('success'):
        return result['data'].get('id'), None, None

    return None, None, result.get('error', 'Unknown error')


# === CONTACT CREATION ===

def create_contact(appt_data, company_id, company_name, source_type,
                   hubspot_data=None, hubspot_contact_data=None,
                   excel_phone=None, telco_attrs=None):
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

    if company_name:
        attributes['COMPANY'] = company_name

    # === PHONE (from multiple sources) ===
    # Priority: 1) Excel phone, 2) HubSpot Contact phone, 3) Appointment phone_from_list

    sms_set = False

    # 1. Excel phone (most reliable - from actual call records)
    if excel_phone:
        normalized = normalize_australian_mobile(excel_phone)
        if normalized:
            attributes['SMS'] = normalized
            sms_set = True
            print(f"    SMS from Excel: {normalized}")

    # 2. HubSpot Contact mobile
    if hubspot_contact_data and not sms_set:
        mobile = hubspot_contact_data.get('Mobile Phone Number', '').strip()
        if mobile:
            normalized = normalize_australian_mobile(mobile)
            if normalized:
                attributes['SMS'] = normalized
                sms_set = True
                print(f"    SMS from HubSpot Contact: {normalized}")

    # 3. Appointment phone_from_list
    phone_from_list = appt_data.get('phone_from_list', '').strip()
    match_source = appt_data.get('match_source', '').strip()

    if phone_from_list and not sms_set and match_source == 'email':
        normalized = normalize_australian_mobile(phone_from_list)
        if normalized:
            attributes['SMS'] = normalized
            sms_set = True
            print(f"    SMS from Appointment: {normalized}")

    # Store additional phones in PHONE_2, PHONE_3
    if phone_from_list and sms_set:
        normalized = normalize_australian_mobile(phone_from_list)
        if normalized and normalized != attributes.get('SMS'):
            attributes['PHONE_2'] = normalized

    # Company phone
    if hubspot_data:
        co_phone = hubspot_data.get('Company Phone Number', '').strip()
        if co_phone:
            attributes['COMPANY_PHONE'] = co_phone

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

    # === TELCO WAREHOUSE CALL DATA (v6) ===
    if telco_attrs:
        attributes.update(telco_attrs)
        print(f"    Added {len(telco_attrs)} Telco call attributes")

    # === DATA QUALITY FLAGS ===
    was_called = appt_data.get('was_called', '').strip()
    if was_called:
        attributes['WAS_CALLED'] = was_called.lower() == 'true'

    email_valid = appt_data.get('email_valid', '').strip()
    if email_valid:
        attributes['EMAIL_VALIDATION'] = 'valid' if email_valid.lower() == 'true' else 'invalid'

    if match_source:
        attributes['MATCH_SOURCE'] = match_source

    # === HUBSPOT COMPANY ENRICHMENT ===
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

        # Social links
        twitter = hubspot_data.get('Twitter Handle', '').strip()
        if twitter:
            attributes['TWITTER'] = twitter
        facebook = hubspot_data.get('Facebook Company Page', '').strip()
        if facebook:
            attributes['FACEBOOK'] = facebook
        linkedin = hubspot_data.get('LinkedIn Company Page', '').strip()
        if linkedin:
            attributes['LINKEDIN'] = linkedin

        # Reviews
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
        employees = hubspot_data.get('Number of Employees', '').strip()
        if employees and employees.isdigit():
            attributes['NUMBER_OF_EMPLOYEES'] = int(employees)
        founded = hubspot_data.get('Year Founded', '').strip()
        if founded and founded.isdigit():
            attributes['YEAR_FOUNDED'] = int(founded)

        # Description
        desc = hubspot_data.get('Business Description', '').strip()
        if desc:
            attributes['BUSINESS_DESCRIPTION'] = desc[:500]

        # HubSpot metadata
        legacy_id = hubspot_data.get('Legacy Record ID', '').strip()
        contact_ids = hubspot_data.get('Biz - Associated Contact IDs', '').strip()
        if legacy_id or contact_ids:
            meta = {'legacy_id': legacy_id, 'contact_ids': contact_ids}
            attributes['HUBSPOT_COMPANY_META'] = json.dumps(meta)

        # Record source tracking
        record_source = hubspot_data.get('Biz - Record source', '').strip()
        if record_source:
            attributes['HUBSPOT_RECORD_SOURCE'] = record_source

        # Create/Modified dates
        create_date = hubspot_data.get('Biz - First Contact Create Date', '').strip()
        if create_date:
            attributes['HUBSPOT_CREATE_DATE'] = create_date
        mod_date = hubspot_data.get('Biz - Last Modified Date', '').strip()
        if mod_date:
            attributes['HUBSPOT_MODIFIED_DATE'] = mod_date

        # Store RAW JSON of all HubSpot fields
        hubspot_json = {k: v for k, v in hubspot_data.items() if v and str(v).strip()}
        if hubspot_json:
            attributes['HUBSPOT_RAW_JSON'] = json.dumps(hubspot_json)

    # === HUBSPOT CONTACT ENRICHMENT ===
    if hubspot_contact_data:
        # Job Title
        job_title = hubspot_contact_data.get('Job Title', '').strip()
        if job_title:
            attributes['JOBTITLE'] = job_title

        # Lead info
        lead_source = hubspot_contact_data.get('Biz- Lead Source', '').strip()
        if lead_source:
            attributes['LEAD_SOURCE'] = lead_source
        lead_status = hubspot_contact_data.get('Biz- lead Status', '').strip()
        if lead_status:
            attributes['LEAD_STATUS'] = lead_status

        # City from contact
        city = hubspot_contact_data.get('City', '').strip()
        if city and 'CITY' not in attributes:
            attributes['CITY'] = city

        # Contact record source
        contact_source = hubspot_contact_data.get('Biz - Contact record source', '').strip()
        if contact_source:
            attributes['CONTACT_RECORD_SOURCE'] = contact_source

    # === LOCATION FROM APPOINTMENT (fallback) ===
    location = appt_data.get('location', '').strip()
    if location and 'CITY' not in attributes and 'STATE_REGION' not in attributes:
        # Try to parse location like "Sydney, NSW" or "Melbourne VIC"
        if ',' in location:
            parts = location.split(',')
            attributes['CITY'] = parts[0].strip()
            if len(parts) > 1:
                attributes['STATE_REGION'] = parts[1].strip()
        elif ' ' in location:
            parts = location.rsplit(' ', 1)
            if len(parts[1]) <= 3:  # Likely state abbreviation
                attributes['CITY'] = parts[0].strip()
                attributes['STATE_REGION'] = parts[1].strip()

    # === SOURCE TRACKING ===
    source_sheet = appt_data.get('source_sheet', '').strip()
    attributes['SOURCE'] = f"{source_sheet} (company_source: {source_type})"
    attributes['IMPORT_BATCH'] = "v6_telco_warehouse"

    # === CREATE CONTACT ===
    result = client.add_contact(email, attributes, list_ids=[24, 28])

    if result.get('success'):
        contact_id = None
        if result.get('data'):
            contact_id = result['data'].get('id')

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


# === MAIN ===

def main():
    print("=" * 70)
    print("IMPORT 5 COMPANIES - V6 (TELCO WAREHOUSE PostgreSQL)")
    print("=" * 70)
    print()
    print("Data sources:")
    print("  + HubSpot Companies CSV (363K companies)")
    print("  + HubSpot Contacts CSV (207K contacts)")
    print("  + Appointments Enriched CSV")
    print("  + Excel Appointments (phone from 'Phone Call' rows)")
    print("  + TELCO WAREHOUSE PostgreSQL (74K calls - Retell + Zadarma + Telnyx)")
    print()

    # Connect to Telco Warehouse
    print("Connecting to Telco Warehouse...")
    telco_conn = get_telco_connection()
    if telco_conn:
        print("  Connected successfully!")
    else:
        print("  WARNING: Failed to connect - will import without call data")

    # Load Excel phone data
    print("\nLoading Excel phone data...")
    excel_phones = load_excel_phone_data()

    results = {'companies': [], 'contacts': []}

    for company_name in TARGETS:
        print(f"\n{'=' * 60}")
        print(f"PROCESSING: {company_name.upper()}")
        print(f"{'=' * 60}")

        # Find appointment
        appt = find_appointment(company_name)
        if not appt:
            print(f"  ERROR: No appointment found")
            continue

        contact_email = appt.get('email', '').strip()
        print(f"  Contact: {appt.get('name', 'N/A')} <{contact_email}>")
        print(f"  Date: {appt.get('date', 'N/A')} at {appt.get('time', 'N/A')}")

        # Get Excel phone
        excel_phone = excel_phones.get(company_name.lower()) or excel_phones.get(contact_email.lower())
        if excel_phone:
            print(f"  Excel Phone: {excel_phone}")
        else:
            print(f"  Excel Phone: NOT FOUND")

        # Create company
        company_id = None
        hubspot_data = None
        source_type = 'appointment'

        print(f"\n  Looking up in HubSpot...")
        hubspot_data = find_hubspot_company(company_name)
        if hubspot_data:
            source_type = 'hubspot'
            print(f"  FOUND in HubSpot: {hubspot_data.get('Company name')}")
            print(f"    Phone: {hubspot_data.get('Company Phone Number', 'N/A')}")
            company_id, hubspot_data, error = create_company_from_hubspot(hubspot_data)
            if company_id:
                print(f"  COMPANY CREATED (HubSpot): {company_id}")
                results['companies'].append({
                    'name': company_name, 'id': company_id, 'source': 'hubspot'
                })
            else:
                print(f"  ERROR: {error}")
        else:
            print(f"  NOT in HubSpot, using appointment data...")
            company_id, _, error = create_company_from_appointment(appt)
            if company_id:
                print(f"  COMPANY CREATED (appointment): {company_id}")
                results['companies'].append({
                    'name': company_name, 'id': company_id, 'source': 'appointment'
                })

        # Look up HubSpot Contact
        hubspot_contact_data = find_hubspot_contact(contact_email)
        if hubspot_contact_data:
            print(f"\n  FOUND in HubSpot Contacts CSV!")
        else:
            print(f"\n  NOT in HubSpot Contacts CSV")

        # Get call data from Telco Warehouse
        telco_attrs = {}
        phone_for_calls = excel_phone or appt.get('phone_from_list', '').strip()

        if phone_for_calls and telco_conn:
            calls = find_calls_for_phone_db(phone_for_calls, telco_conn)
            if calls:
                # Count by provider
                retell_count = len([c for c in calls if c.get('provider_name') == 'retell'])
                zadarma_count = len([c for c in calls if c.get('provider_name') == 'zadarma'])
                telnyx_count = len([c for c in calls if c.get('provider_name') == 'telnyx'])

                print(f"  Found {len(calls)} calls in Telco Warehouse:")
                if retell_count:
                    print(f"    - Retell: {retell_count}")
                if zadarma_count:
                    print(f"    - Zadarma: {zadarma_count}")
                if telnyx_count:
                    print(f"    - Telnyx: {telnyx_count}")

                telco_attrs = build_telco_attributes(calls, phone_for_calls)
            else:
                print(f"  No calls found in Telco Warehouse for {phone_for_calls}")
        elif not telco_conn:
            print(f"  Skipping call lookup (no DB connection)")

        # Create contact
        print(f"  Creating contact...")
        contact_id, error = create_contact(
            appt, company_id, appt.get('company', '').strip(),
            source_type, hubspot_data, hubspot_contact_data,
            excel_phone, telco_attrs
        )

        if contact_id:
            print(f"  CONTACT CREATED: {contact_id}")
            if error:
                print(f"    Note: {error}")
            results['contacts'].append({
                'email': contact_email,
                'name': appt.get('name', ''),
                'id': contact_id,
                'company_id': company_id,
                'excel_phone': excel_phone,
                'telco_calls': telco_attrs.get('TELCO_TOTAL_CALLS', 0),
                'hubspot_company_enriched': hubspot_data is not None,
                'hubspot_contact_enriched': hubspot_contact_data is not None
            })
        else:
            print(f"  ERROR: {error}")

    # Close DB connection
    if telco_conn:
        telco_conn.close()

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
        linked = "linked" if c.get('company_id') else "NOT linked"
        extras = []
        if c.get('excel_phone'):
            extras.append(f"Phone: {c['excel_phone']}")
        if c.get('telco_calls'):
            extras.append(f"Telco: {c['telco_calls']} calls")
        if c.get('hubspot_company_enriched'):
            extras.append("HS-Co")
        if c.get('hubspot_contact_enriched'):
            extras.append("HS-Contact")
        extra_str = f" [{', '.join(extras)}]" if extras else ""
        print(f"  - {c['email']} ({linked}){extra_str}")

    # Save results
    results_file = Path(__file__).parent / 'import_v6_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults: {results_file}")


if __name__ == "__main__":
    main()
