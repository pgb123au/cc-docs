"""
Comprehensive Brevo data audit - V4
Checks ALL fields including HubSpot enrichment.
"""
from brevo_api import BrevoClient
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = BrevoClient()

print('=' * 80)
print('COMPREHENSIVE BREVO DATA AUDIT - V4')
print('=' * 80)

# Expected data for our 3 test companies
expected_companies = {
    'reignite health': {
        'contact_email': 'sara@reignitehealth.com.au',
        'contact_name': 'Sara Lehmann',
        'date': '2025-09-17',
        'time': '10:00am',
        'status': 'Seen  - Client',
        'status_category': 'won',
        'quality': 'Good',
        'followup': 'Client',
        'source_sheet': 'Appts New',
        'hubspot_domain': 'reignitehealth.co',
        'hubspot_industry': 'Health, Wellness and Fitness',
        'was_called': False,
        'email_valid': True,
        'match_source': '',
        'phone_from_list': '',
        'has_hubspot_enrichment': True
    },
    'paradise distributors': {
        'contact_email': 'bchalmers616@gmail.com',
        'contact_name': 'Bob Chalmers',
        'date': '2025-09-24',
        'time': '11:00am',
        'status': 'Seen  - Client',
        'status_category': 'won',
        'quality': 'OK',
        'followup': 'Client',
        'source_sheet': 'Appts New',
        'was_called': True,
        'email_valid': True,
        'match_source': 'domain',
        'phone_from_list': '61402213582',
        'has_hubspot_enrichment': False
    },
    'jtw building group': {
        'contact_email': 'Joe@jtwbuildinggroup.com.au',
        'contact_name': 'Joe Van Stripe',
        'date': '2025-07-29',
        'time': '12:30pm',
        'status': 'Seen - FU',
        'status_category': 'followup',
        'quality': 'Good',
        'followup': '2026-02-01',
        'source_sheet': 'Appts New',
        'was_called': False,
        'email_valid': True,
        'match_source': '',
        'phone_from_list': '',
        'has_hubspot_enrichment': False
    }
}

errors = []
warnings = []

# ============ COMPANIES ============
print('\n' + '=' * 40)
print('COMPANIES')
print('=' * 40)

result = client._request('GET', 'companies', params={'limit': 50})
company_ids = {}  # name -> id for checking links

if result.get('success'):
    companies = result['data'].get('items', [])
    print(f'Total: {len(companies)}')

    for co in companies:
        co_id = co.get('id')
        attrs = co.get('attributes', {})
        name = attrs.get('name', '')
        domain = attrs.get('domain', '')
        industry = attrs.get('industry', '')
        phone = attrs.get('phone_number', '')
        city = attrs.get('city', '')
        linked = co.get('linkedContactsIds', [])

        company_ids[name.lower()] = co_id

        print(f'\n  [{name}]')
        print(f'    ID: {co_id}')
        print(f'    Domain: {domain or "(missing)"}')
        print(f'    Industry: {industry or "(missing)"}')
        print(f'    Phone: {phone or "(missing)"}')
        print(f'    City: {city or "(missing)"}')
        print(f'    Linked contacts: {len(linked)}')
        print(f'    All attributes: {list(attrs.keys())}')

        name_lower = name.lower()

        # Is name a domain?
        if '.' in name and ' ' not in name and len(name) < 50:
            errors.append(f'Company "{name}" - name looks like a domain')

        # Check expected enrichment for Reignite Health
        if 'reignite' in name_lower:
            if not domain:
                errors.append(f'{name}: MISSING domain (expected: reignitehealth.co)')
            elif domain != 'reignitehealth.co':
                warnings.append(f'{name}: Wrong domain "{domain}" (expected: reignitehealth.co)')
            if not industry:
                errors.append(f'{name}: MISSING industry (expected: Health, Wellness and Fitness)')
            elif industry != 'Health, Wellness and Fitness':
                warnings.append(f'{name}: Wrong industry "{industry}"')

# ============ CONTACTS ============
print('\n' + '=' * 40)
print('CONTACTS')
print('=' * 40)

result = client.get_contacts(limit=50)
if result.get('success'):
    contacts = result['data'].get('contacts', [])
    print(f'Total: {len(contacts)}')

    for c in contacts:
        email = c.get('email', '')
        email_lower = email.lower()
        attrs = c.get('attributes', {})

        # Core attributes
        firstname = attrs.get('FIRSTNAME', '')
        lastname = attrs.get('LASTNAME', '')
        company = attrs.get('COMPANY', '')
        sms = attrs.get('SMS', '')
        phone2 = attrs.get('PHONE_2', '')

        # Appointment
        appt_date = attrs.get('APPOINTMENT_DATE', '')
        appt_time = attrs.get('APPOINTMENT_TIME', '')
        appt_status = attrs.get('APPOINTMENT_STATUS', '')
        deal_stage = attrs.get('DEAL_STAGE', '')
        quality = attrs.get('QUALITY', '')
        followup = attrs.get('FOLLOWUP_STATUS', '')
        retell_log = attrs.get('RETELL_LOG', '')

        # v4 fixes
        was_called = attrs.get('WAS_CALLED', '')
        email_valid = attrs.get('EMAIL_VALIDATION', '')  # Fixed name!
        match_source = attrs.get('MATCH_SOURCE', '')
        call_count = attrs.get('CALL_COUNT', '')

        # HubSpot enrichment
        company_domain = attrs.get('COMPANY_DOMAIN', '')
        industry = attrs.get('INDUSTRY', '')
        business_type = attrs.get('BUSINESS_TYPE', '')
        city = attrs.get('CITY', '')
        state = attrs.get('STATE_REGION', '')

        # Source tracking
        source = attrs.get('SOURCE', '')
        import_batch = attrs.get('IMPORT_BATCH', '')

        print(f'\n  [{email}]')
        print(f'    --- Identity ---')
        print(f'    FIRSTNAME: "{firstname}"')
        print(f'    LASTNAME: "{lastname}"')
        print(f'    COMPANY: "{company}"')
        print(f'    --- Phone ---')
        print(f'    SMS: {sms or "(none)"}')
        print(f'    PHONE_2: {phone2 or "(none)"}')
        print(f'    --- Appointment ---')
        print(f'    APPOINTMENT_DATE: "{appt_date}"')
        print(f'    APPOINTMENT_TIME: "{appt_time}"')
        print(f'    APPOINTMENT_STATUS: "{appt_status}"')
        print(f'    DEAL_STAGE: "{deal_stage}"')
        print(f'    QUALITY: "{quality}"')
        print(f'    FOLLOWUP_STATUS: "{followup}"')
        print(f'    --- Call Data ---')
        log_preview = retell_log[:80] + '...' if retell_log and len(retell_log) > 80 else retell_log
        print(f'    RETELL_LOG: {log_preview or "(none)"}')
        print(f'    WAS_CALLED: {was_called}')
        print(f'    CALL_COUNT: {call_count or "(none)"}')
        print(f'    --- Data Quality (V4 fixes) ---')
        print(f'    EMAIL_VALIDATION: "{email_valid}"')
        print(f'    MATCH_SOURCE: "{match_source}"')
        print(f'    --- HubSpot Enrichment ---')
        print(f'    COMPANY_DOMAIN: "{company_domain}"')
        print(f'    INDUSTRY: "{industry}"')
        print(f'    BUSINESS_TYPE: "{business_type}"')
        print(f'    CITY: "{city}"')
        print(f'    STATE_REGION: "{state}"')
        print(f'    --- Source ---')
        print(f'    SOURCE: "{source}"')
        print(f'    IMPORT_BATCH: "{import_batch}"')
        print(f'    --- All Attributes ---')
        print(f'    {list(attrs.keys())}')

        # Find expected data
        expected = None
        for co_name, data in expected_companies.items():
            if data['contact_email'].lower() == email_lower:
                expected = data.copy()
                expected['company'] = co_name
                break

        if expected:
            # Check all expected fields
            if not appt_date:
                errors.append(f'{email}: MISSING APPOINTMENT_DATE (expected: {expected["date"]})')
            elif appt_date != expected['date']:
                errors.append(f'{email}: Wrong APPOINTMENT_DATE: "{appt_date}" vs "{expected["date"]}"')

            if not appt_time:
                errors.append(f'{email}: MISSING APPOINTMENT_TIME (expected: {expected["time"]})')
            elif appt_time != expected['time']:
                errors.append(f'{email}: Wrong APPOINTMENT_TIME: "{appt_time}" vs "{expected["time"]}"')

            if not appt_status:
                errors.append(f'{email}: MISSING APPOINTMENT_STATUS (expected: {expected["status"]})')

            if not deal_stage:
                errors.append(f'{email}: MISSING DEAL_STAGE (expected: {expected["status_category"]})')
            elif deal_stage != expected['status_category']:
                errors.append(f'{email}: Wrong DEAL_STAGE: "{deal_stage}" vs "{expected["status_category"]}"')

            if not quality:
                errors.append(f'{email}: MISSING QUALITY (expected: {expected["quality"]})')
            elif quality != expected['quality']:
                errors.append(f'{email}: Wrong QUALITY: "{quality}" vs "{expected["quality"]}"')

            # Followup status
            if expected.get('followup') and not followup:
                errors.append(f'{email}: MISSING FOLLOWUP_STATUS (expected: {expected["followup"]})')

            # Company name
            if not company:
                errors.append(f'{email}: MISSING COMPANY attribute')

            # Name check
            expected_name = expected['contact_name']
            expected_parts = expected_name.split(None, 1)
            expected_first = expected_parts[0] if expected_parts else ''
            expected_last = expected_parts[1] if len(expected_parts) > 1 else ''

            if not firstname:
                errors.append(f'{email}: MISSING FIRSTNAME (expected: {expected_first})')
            elif firstname != expected_first:
                errors.append(f'{email}: Wrong FIRSTNAME: "{firstname}" vs "{expected_first}"')

            if expected_last and not lastname:
                errors.append(f'{email}: MISSING LASTNAME (expected: {expected_last})')

            # V4 checks - EMAIL_VALIDATION
            if expected.get('email_valid') and not email_valid:
                errors.append(f'{email}: MISSING EMAIL_VALIDATION (expected: valid)')

            # V4 checks - MATCH_SOURCE
            if expected.get('match_source') and not match_source:
                errors.append(f'{email}: MISSING MATCH_SOURCE (expected: {expected["match_source"]})')
            elif expected.get('match_source') and match_source != expected['match_source']:
                warnings.append(f'{email}: MATCH_SOURCE mismatch: "{match_source}" vs "{expected["match_source"]}"')

            # V4 checks - HubSpot enrichment
            if expected.get('has_hubspot_enrichment'):
                if not company_domain:
                    errors.append(f'{email}: MISSING COMPANY_DOMAIN (has_hubspot_enrichment=True)')
                if not industry:
                    errors.append(f'{email}: MISSING INDUSTRY (has_hubspot_enrichment=True)')

            # V4 checks - Phone
            if expected.get('phone_from_list') and expected.get('match_source') == 'domain':
                if not phone2:
                    errors.append(f'{email}: MISSING PHONE_2 (match_source=domain)')

# ============ SUMMARY ============
print('\n' + '=' * 80)
print('ERRORS AND OMISSIONS FOUND')
print('=' * 80)

if errors:
    print(f'\nERRORS ({len(errors)}):')
    for e in errors:
        print(f'  X {e}')
else:
    print('\nNo errors found.')

if warnings:
    print(f'\nWARNINGS ({len(warnings)}):')
    for w in warnings:
        print(f'  ! {w}')
else:
    print('\nNo warnings.')

print('\n' + '=' * 80)
if not errors and not warnings:
    print('STATUS: ALL DATA PERFECT!')
else:
    print(f'STATUS: {len(errors)} errors, {len(warnings)} warnings to fix')
print('=' * 80)
