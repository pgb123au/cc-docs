"""
Import 5 companies - V8 RETELL TRANSCRIPTS

V8 IMPROVEMENTS:
- Queries telco.calls directly for Retell transcript data
- Adds RETELL_CALL_ID, RETELL_CALL_SUMMARY, RETELL_TRANSCRIPT
- Adds TELCO_SENTIMENT, RETELL_CALL_DURATION, RETELL_CALL_DIRECTION
- Still uses telco.contacts for aggregated stats
- Uses telco.normalize_phone() for proper phone matching

Reference: C:/Users/peter/Downloads/CC/Telcos/TELCO_WAREHOUSE_CRM_HANDOFF.md
"""

import csv
import json
import re
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

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
    'password': 'TelcoSync2024!',
    'connect_timeout': 15
}

OUR_NUMBERS = ['61399997398', '61288800208', '61288800226', '61240620999',
               '399997398', '288800208', '288800226', '240620999']

client = BrevoClient()

TARGETS = [
    'Reignite Health',
    'Paradise Distributors',
    'JTW building group',
    'Lumiere Home Renovations',
    'CLG Electrics'
]


# === TELCO WAREHOUSE QUERIES (V8 - Including Retell transcripts) ===

def get_telco_connection():
    """Get PostgreSQL connection to Telco Warehouse with retry."""
    if not HAS_PSYCOPG2:
        return None

    for attempt in range(3):
        try:
            conn = psycopg2.connect(**TELCO_DB)
            return conn
        except Exception as e:
            print(f"  Connection attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(3)
    return None


def lookup_telco_contact(phone, conn):
    """
    Look up a phone number in telco.contacts table using normalize_phone().
    Returns pre-aggregated stats from the contacts table.
    """
    if not conn or not phone:
        return None

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT
                phone_normalized,
                phone_display,
                contact_type,
                first_seen,
                last_seen,
                total_calls,
                inbound_calls,
                outbound_calls,
                answered_calls,
                missed_calls,
                total_duration_sec,
                retell_calls,
                zadarma_calls,
                telnyx_calls,
                total_sms,
                last_transcript,
                last_disposition,
                is_dnc,
                dnc_reason,
                contact_status,
                lead_score,
                hostile_interactions,
                notes,
                tags
            FROM telco.contacts
            WHERE phone_normalized = telco.normalize_phone(%s)
        """, (phone,))

        row = cursor.fetchone()
        cursor.close()

        if row:
            return dict(row)
        return None

    except Exception as e:
        print(f"  ERROR querying telco.contacts: {e}")
        return None


def lookup_retell_calls(phone, conn, limit=5):
    """
    V8: Query telco.calls directly for Retell data with transcripts.
    Returns detailed call data including transcript and analysis.
    """
    if not conn or not phone:
        return []

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT
                c.id,
                c.external_call_id,
                c.from_number,
                c.to_number,
                c.direction,
                c.started_at,
                c.duration_seconds,
                c.transcript,
                c.raw_data->>'disconnection_reason' as disconnection_reason,
                c.raw_data->'call_analysis'->>'call_summary' as call_summary,
                c.raw_data->'call_analysis'->>'user_sentiment' as sentiment,
                c.raw_data->'call_analysis'->>'call_successful' as successful,
                c.raw_data->'call_analysis'->>'in_voicemail' as voicemail
            FROM telco.calls c
            WHERE (telco.normalize_phone(c.from_number) = telco.normalize_phone(%s)
                OR telco.normalize_phone(c.to_number) = telco.normalize_phone(%s))
              AND c.provider_id = 3
              AND c.transcript IS NOT NULL
            ORDER BY c.started_at DESC
            LIMIT %s
        """, (phone, phone, limit))

        rows = cursor.fetchall()
        cursor.close()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"  ERROR querying Retell calls: {e}")
        return []


def get_call_log_entries(phone, conn, limit=20):
    """
    Get individual call log entries for building RETELL_LOG.
    Uses telco.normalize_phone() for matching.
    """
    if not conn or not phone:
        return []

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT
                c.started_at,
                c.direction,
                c.duration_seconds,
                p.name as provider_name,
                c.disposition,
                c.transcript
            FROM telco.calls c
            JOIN telco.providers p ON c.provider_id = p.provider_id
            WHERE telco.normalize_phone(c.from_number) = telco.normalize_phone(%s)
               OR telco.normalize_phone(c.to_number) = telco.normalize_phone(%s)
            ORDER BY c.started_at DESC
            LIMIT %s
        """, (phone, phone, limit))

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


def build_telco_attributes_v8(contact_data, call_entries, retell_calls):
    """
    V8: Build Brevo attributes from telco.contacts data, call entries, AND Retell transcripts.
    """
    attrs = {}

    if contact_data:
        # Pre-aggregated stats from telco.contacts
        if contact_data.get('total_calls'):
            attrs['TELCO_TOTAL_CALLS'] = contact_data['total_calls']

        if contact_data.get('retell_calls'):
            attrs['RETELL_CALL_COUNT'] = contact_data['retell_calls']
        if contact_data.get('zadarma_calls'):
            attrs['ZADARMA_CALL_COUNT'] = contact_data['zadarma_calls']
        if contact_data.get('telnyx_calls'):
            attrs['TELNYX_CALL_COUNT'] = contact_data['telnyx_calls']

        # Build provider list
        providers = []
        if contact_data.get('retell_calls'):
            providers.append('retell')
        if contact_data.get('zadarma_calls'):
            providers.append('zadarma')
        if contact_data.get('telnyx_calls'):
            providers.append('telnyx')
        if providers:
            attrs['TELCO_PROVIDER'] = ', '.join(providers)

        # DNC and status from contact analysis
        if contact_data.get('is_dnc'):
            attrs['TELCO_IS_DNC'] = True
            if contact_data.get('dnc_reason'):
                attrs['TELCO_DNC_REASON'] = contact_data['dnc_reason']

        if contact_data.get('contact_status') and contact_data['contact_status'] != 'active':
            attrs['TELCO_CONTACT_STATUS'] = contact_data['contact_status']

        if contact_data.get('lead_score'):
            attrs['TELCO_LEAD_SCORE'] = contact_data['lead_score']

        if contact_data.get('hostile_interactions'):
            attrs['TELCO_HOSTILE_COUNT'] = contact_data['hostile_interactions']

        # Timestamps
        if contact_data.get('first_seen'):
            attrs['TELCO_FIRST_SEEN'] = contact_data['first_seen'].strftime('%Y-%m-%d %H:%M')
        if contact_data.get('last_seen'):
            attrs['TELCO_LAST_SEEN'] = contact_data['last_seen'].strftime('%Y-%m-%d %H:%M')

    # V8: Add Retell-specific data from direct call query
    if retell_calls:
        # Get the most recent Retell call with transcript
        latest_retell = retell_calls[0]

        # External Call ID
        if latest_retell.get('external_call_id'):
            attrs['RETELL_CALL_ID'] = latest_retell['external_call_id']

        # Call Summary (from Retell analysis)
        if latest_retell.get('call_summary'):
            summary = latest_retell['call_summary']
            if len(summary) > 5000:
                summary = summary[:4990] + '...[truncated]'
            attrs['RETELL_CALL_SUMMARY'] = summary

        # Full Transcript
        if latest_retell.get('transcript'):
            transcript = latest_retell['transcript']
            if len(transcript) > 10000:
                transcript = transcript[:9990] + '...[truncated]'
            attrs['RETELL_TRANSCRIPT'] = transcript

        # Sentiment
        if latest_retell.get('sentiment'):
            attrs['TELCO_SENTIMENT'] = latest_retell['sentiment']

        # Call outcome flags
        if latest_retell.get('successful'):
            attrs['RETELL_SUCCESSFUL'] = latest_retell['successful'].lower() == 'true'
        if latest_retell.get('voicemail'):
            attrs['RETELL_VOICEMAIL'] = latest_retell['voicemail'].lower() == 'true'

        # Disconnection reason
        if latest_retell.get('disconnection_reason'):
            attrs['RETELL_DISCONNECT_REASON'] = latest_retell['disconnection_reason']

        # Call duration
        if latest_retell.get('duration_seconds'):
            attrs['RETELL_CALL_DURATION'] = latest_retell['duration_seconds']

        # Call direction
        if latest_retell.get('direction'):
            attrs['RETELL_CALL_DIRECTION'] = latest_retell['direction']

        # Call time
        if latest_retell.get('started_at'):
            started = latest_retell['started_at']
            if hasattr(started, 'strftime'):
                attrs['RETELL_CALL_TIME'] = started.strftime('%Y-%m-%d %H:%M:%S')
            else:
                attrs['RETELL_CALL_TIME'] = str(started)[:19]

    # Build call log from individual entries
    if call_entries:
        log_lines = []
        for call in call_entries[:20]:
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

    excel_path = None
    for path in EXCEL_PATHS:
        if path.exists():
            try:
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

    phone_data = {}

    for col in range(1, len(df.columns)):
        company = df.iloc[2, col] if len(df) > 2 and pd.notna(df.iloc[2, col]) else None
        email = df.iloc[6, col] if len(df) > 6 and pd.notna(df.iloc[6, col]) else None

        if not company:
            continue

        company = str(company).strip()
        email = str(email).strip().lower() if email else ''

        phone_found = None
        for row in range(8, min(20, len(df))):
            cell = df.iloc[row, col]
            if pd.notna(cell):
                cell_str = str(cell)
                match = re.search(r'Phone Call\s*:\s*\+?(\d+)\s*->\s*\+?(\d+)', cell_str)
                if match:
                    num1, num2 = match.groups()
                    if any(our in num2 for our in OUR_NUMBERS):
                        phone_found = '+' + num1
                    else:
                        phone_found = '+' + num2
                    break

        if phone_found:
            phone_data[company.lower()] = phone_found
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
    sms_set = False

    if excel_phone:
        normalized = normalize_australian_mobile(excel_phone)
        if normalized:
            attributes['SMS'] = normalized
            sms_set = True
            print(f"    SMS from Excel: {normalized}")

    if hubspot_contact_data and not sms_set:
        mobile = hubspot_contact_data.get('Mobile Phone Number', '').strip()
        if mobile:
            normalized = normalize_australian_mobile(mobile)
            if normalized:
                attributes['SMS'] = normalized
                sms_set = True
                print(f"    SMS from HubSpot Contact: {normalized}")

    phone_from_list = appt_data.get('phone_from_list', '').strip()
    match_source = appt_data.get('match_source', '').strip()

    if phone_from_list and not sms_set and match_source == 'email':
        normalized = normalize_australian_mobile(phone_from_list)
        if normalized:
            attributes['SMS'] = normalized
            sms_set = True
            print(f"    SMS from Appointment: {normalized}")

    if phone_from_list and sms_set:
        normalized = normalize_australian_mobile(phone_from_list)
        if normalized and normalized != attributes.get('SMS'):
            attributes['PHONE_2'] = normalized

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

    # === TELCO WAREHOUSE CALL DATA (v8) ===
    if telco_attrs:
        attributes.update(telco_attrs)
        print(f"    Added {len(telco_attrs)} Telco attributes")

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
        domain = hubspot_data.get('Company Domain Name', '').strip()
        if domain:
            attributes['COMPANY_DOMAIN'] = domain

        industry = hubspot_data.get('Industry', '').strip()
        if industry:
            attributes['INDUSTRY'] = industry

        biz_type = hubspot_data.get('Business type', '').strip()
        if biz_type:
            attributes['BUSINESS_TYPE'] = biz_type

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

        co_email = hubspot_data.get('Company Email', '').strip()
        if co_email:
            attributes['COMPANY_EMAIL'] = co_email

        twitter = hubspot_data.get('Twitter Handle', '').strip()
        if twitter:
            attributes['TWITTER'] = twitter
        facebook = hubspot_data.get('Facebook Company Page', '').strip()
        if facebook:
            attributes['FACEBOOK'] = facebook
        linkedin = hubspot_data.get('LinkedIn Company Page', '').strip()
        if linkedin:
            attributes['LINKEDIN'] = linkedin

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

        employees = hubspot_data.get('Number of Employees', '').strip()
        if employees and employees.isdigit():
            attributes['NUMBER_OF_EMPLOYEES'] = int(employees)
        founded = hubspot_data.get('Year Founded', '').strip()
        if founded and founded.isdigit():
            attributes['YEAR_FOUNDED'] = int(founded)

        desc = hubspot_data.get('Business Description', '').strip()
        if desc:
            attributes['BUSINESS_DESCRIPTION'] = desc[:500]

        legacy_id = hubspot_data.get('Legacy Record ID', '').strip()
        contact_ids = hubspot_data.get('Biz - Associated Contact IDs', '').strip()
        if legacy_id or contact_ids:
            meta = {'legacy_id': legacy_id, 'contact_ids': contact_ids}
            attributes['HUBSPOT_COMPANY_META'] = json.dumps(meta)

        record_source = hubspot_data.get('Biz - Record source', '').strip()
        if record_source:
            attributes['HUBSPOT_RECORD_SOURCE'] = record_source

        create_date = hubspot_data.get('Biz - First Contact Create Date', '').strip()
        if create_date:
            attributes['HUBSPOT_CREATE_DATE'] = create_date
        mod_date = hubspot_data.get('Biz - Last Modified Date', '').strip()
        if mod_date:
            attributes['HUBSPOT_MODIFIED_DATE'] = mod_date

        hubspot_json = {k: v for k, v in hubspot_data.items() if v and str(v).strip()}
        if hubspot_json:
            attributes['HUBSPOT_RAW_JSON'] = json.dumps(hubspot_json)

    # === HUBSPOT CONTACT ENRICHMENT ===
    if hubspot_contact_data:
        job_title = hubspot_contact_data.get('Job Title', '').strip()
        if job_title:
            attributes['JOBTITLE'] = job_title

        lead_source = hubspot_contact_data.get('Biz- Lead Source', '').strip()
        if lead_source:
            attributes['LEAD_SOURCE'] = lead_source
        lead_status = hubspot_contact_data.get('Biz- lead Status', '').strip()
        if lead_status:
            attributes['LEAD_STATUS'] = lead_status

        city = hubspot_contact_data.get('City', '').strip()
        if city and 'CITY' not in attributes:
            attributes['CITY'] = city

        contact_source = hubspot_contact_data.get('Biz - Contact record source', '').strip()
        if contact_source:
            attributes['CONTACT_RECORD_SOURCE'] = contact_source

    # === LOCATION FROM APPOINTMENT (fallback) ===
    location = appt_data.get('location', '').strip()
    if location and 'CITY' not in attributes and 'STATE_REGION' not in attributes:
        if ',' in location:
            parts = location.split(',')
            attributes['CITY'] = parts[0].strip()
            if len(parts) > 1:
                attributes['STATE_REGION'] = parts[1].strip()
        elif ' ' in location:
            parts = location.rsplit(' ', 1)
            if len(parts[1]) <= 3:
                attributes['CITY'] = parts[0].strip()
                attributes['STATE_REGION'] = parts[1].strip()

    # === SOURCE TRACKING ===
    source_sheet = appt_data.get('source_sheet', '').strip()
    attributes['SOURCE'] = f"{source_sheet} (company_source: {source_type})"
    attributes['IMPORT_BATCH'] = "v8_retell_transcripts"

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

        if company_id and contact_id:
            link_result = client._request('PATCH', f'companies/link-unlink/{company_id}', {
                "linkContactIds": [contact_id]
            })
            if not link_result.get('success'):
                print(f"    Warning: Failed to link: {link_result.get('error')}")

        return contact_id, None
    else:
        error = result.get('error', '')

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
    print("IMPORT 5 COMPANIES - V8 (RETELL TRANSCRIPTS)")
    print("=" * 70)
    print()
    print("V8 Improvements:")
    print("  + Queries telco.calls for Retell transcript data")
    print("  + Adds RETELL_CALL_ID, RETELL_CALL_SUMMARY, RETELL_TRANSCRIPT")
    print("  + Adds TELCO_SENTIMENT, RETELL_CALL_DURATION, RETELL_CALL_DIRECTION")
    print("  + Still uses telco.contacts for aggregated stats")
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
            company_phone = hubspot_data.get('Company Phone Number', 'N/A')
            print(f"    Company Phone: {company_phone}")
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

        # V8: Get call data from telco.contacts AND telco.calls (for Retell transcripts)
        telco_attrs = {}

        # Collect all phone numbers to try
        phones_to_try = []

        # 1. Excel phone (most reliable)
        if excel_phone:
            phones_to_try.append(('Excel', excel_phone))

        # 2. Appointment phone
        appt_phone = appt.get('phone_from_list', '').strip()
        if appt_phone:
            phones_to_try.append(('Appointment', appt_phone))

        # 3. Company phone from HubSpot
        if hubspot_data:
            company_phone = hubspot_data.get('Company Phone Number', '').strip()
            if company_phone:
                phones_to_try.append(('Company', company_phone))

        print(f"\n  Looking up calls for {len(phones_to_try)} phone numbers...")

        telco_contact = None
        call_entries = []
        retell_calls = []
        matched_phone = None

        if telco_conn and phones_to_try:
            for source, phone in phones_to_try:
                print(f"    Trying {source}: {phone}")

                # Look up aggregated stats
                contact = lookup_telco_contact(phone, telco_conn)
                if contact and contact.get('total_calls', 0) > 0:
                    print(f"      FOUND! {contact['total_calls']} calls")
                    telco_contact = contact
                    matched_phone = phone
                    call_entries = get_call_log_entries(phone, telco_conn)

                    # V8: Also look up Retell-specific calls with transcripts
                    retell_calls = lookup_retell_calls(phone, telco_conn)
                    if retell_calls:
                        print(f"      Retell calls with transcripts: {len(retell_calls)}")
                    break
                else:
                    # Still try to find Retell calls even if no contact stats
                    retell_temp = lookup_retell_calls(phone, telco_conn)
                    if retell_temp:
                        print(f"      No contact stats, but found {len(retell_temp)} Retell calls!")
                        retell_calls = retell_temp
                        matched_phone = phone
                        break
                    print(f"      No calls found")

            if telco_contact or retell_calls:
                telco_attrs = build_telco_attributes_v8(telco_contact, call_entries, retell_calls)
                print(f"  Telco data from {matched_phone}:")
                if telco_contact:
                    print(f"    Total: {telco_contact.get('total_calls', 0)} calls")
                    print(f"    Retell: {telco_contact.get('retell_calls', 0)}")
                    print(f"    Zadarma: {telco_contact.get('zadarma_calls', 0)}")
                if retell_calls:
                    print(f"    Retell Transcripts: {len(retell_calls)}")
                    if retell_calls[0].get('sentiment'):
                        print(f"    Latest Sentiment: {retell_calls[0]['sentiment']}")
            else:
                print(f"  No calls found for any phone number")
        elif not telco_conn:
            print(f"  Skipping call lookup (no DB connection)")

        # Create contact
        print(f"\n  Creating contact...")
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
                'retell_transcripts': len(retell_calls) if retell_calls else 0,
                'matched_phone': matched_phone,
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
        if c.get('matched_phone'):
            extras.append(f"Phone: {c['matched_phone']}")
        if c.get('telco_calls'):
            extras.append(f"Calls: {c['telco_calls']}")
        if c.get('retell_transcripts'):
            extras.append(f"Transcripts: {c['retell_transcripts']}")
        if c.get('hubspot_company_enriched'):
            extras.append("HS-Co")
        if c.get('hubspot_contact_enriched'):
            extras.append("HS-Contact")
        extra_str = f" [{', '.join(extras)}]" if extras else ""
        print(f"  - {c['email']} ({linked}){extra_str}")

    # Save results
    results_file = Path(__file__).parent / 'import_v8_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults: {results_file}")


if __name__ == "__main__":
    main()
