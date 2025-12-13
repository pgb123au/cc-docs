"""
Import Appointments to Brevo as CRM Deals.

Maps appointment status to Brevo deal stages:
- won -> Closed Won
- followup -> Negotiation
- booked -> Qualified Lead
- contacted -> New Lead
- no_show, dead -> Lost

Usage:
    python import_appointments.py
"""

import sys
import csv
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from brevo_api import BrevoClient

CRM_DIR = Path(r'C:\Users\peter\Downloads\CC\CRM')

# Appointment files by status category
APPOINTMENT_FILES = {
    'won': CRM_DIR / 'Appointments_won.csv',
    'followup': CRM_DIR / 'Appointments_followup.csv',
    'booked': CRM_DIR / 'Appointments_booked.csv',
    'contacted': CRM_DIR / 'Appointments_contacted.csv',
    'seen': CRM_DIR / 'Appointments_seen.csv',
    'no_show': CRM_DIR / 'Appointments_no_show.csv',
    'reschedule': CRM_DIR / 'Appointments_reschedule.csv',
    'dead': CRM_DIR / 'Appointments_dead.csv',
    'bad_prospect': CRM_DIR / 'Appointments_bad_prospect.csv',
}

# Map status categories to deal stages
STAGE_MAPPING = {
    'won': 'Closed Won',
    'followup': 'Negotiation',
    'booked': 'Qualified Lead',
    'contacted': 'New Lead',
    'seen': 'Demo Scheduled',
    'no_show': 'Lost',
    'reschedule': 'Qualified Lead',
    'dead': 'Lost',
    'bad_prospect': 'Lost',
}

# List ID for appointments
APPOINTMENTS_LIST_ID = 28


def load_all_appointments():
    """Load appointments from all status files."""
    all_appointments = []

    for status, filepath in APPOINTMENT_FILES.items():
        if not filepath.exists():
            continue

        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['deal_stage'] = STAGE_MAPPING.get(status, 'New Lead')
                row['status_category'] = status
                all_appointments.append(row)

    return all_appointments


def create_deal_name(appt):
    """Create a meaningful deal name."""
    company = appt.get('company', '').strip()
    name = appt.get('name', '').strip()
    date = appt.get('date', '').strip()

    if company:
        return f"{company} - {date}" if date else company
    elif name:
        return f"{name} - {date}" if date else name
    else:
        email = appt.get('email', '').strip()
        return f"Lead: {email}"


def import_appointments(client, appointments, dry_run=False):
    """Import appointments as Brevo deals."""
    print(f"\n=== Importing {len(appointments)} appointments ===")

    if dry_run:
        print("[DRY RUN - No changes will be made]")

    stats = {'created': 0, 'failed': 0, 'errors': []}

    # Also track emails to add to appointments list
    appointment_emails = []

    for i, appt in enumerate(appointments):
        email = appt.get('email', '').strip().lower()
        company = appt.get('company', '').strip()
        name = appt.get('name', '').strip()

        if not email or '@' not in email:
            continue

        appointment_emails.append(email)

        # Create deal
        deal_name = create_deal_name(appt)
        deal_stage = appt.get('deal_stage', 'New Lead')

        if dry_run:
            print(f"  Would create: {deal_name} [{deal_stage}]")
            stats['created'] += 1
            continue

        # Brevo deal attributes
        deal_attributes = {
            'deal_stage': deal_stage,
            'deal_name': deal_name,
        }

        # Add contact to appointments list first
        result = client.add_contact(
            email=email,
            attributes={
                'FIRSTNAME': name.split()[0] if name else '',
                'LASTNAME': ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                'COMPANY': company,
                'APPOINTMENT_DATE': appt.get('date', ''),
                'APPOINTMENT_STATUS': appt.get('status', ''),
                'DEAL_STAGE': deal_stage,
            },
            list_ids=[APPOINTMENTS_LIST_ID]
        )

        if result.get('success'):
            stats['created'] += 1
        else:
            stats['failed'] += 1
            if len(stats['errors']) < 5:
                stats['errors'].append({'email': email, 'error': result.get('error')})

        # Progress update
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{len(appointments)}")

    # Summary
    print(f"\n  Created/updated: {stats['created']}")
    print(f"  Failed: {stats['failed']}")

    if stats['errors']:
        print(f"  Sample errors: {stats['errors']}")

    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Import appointments to Brevo')
    parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    args = parser.parse_args()

    print("=" * 60)
    print("IMPORT APPOINTMENTS TO BREVO")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    client = BrevoClient()

    # Verify connection
    account = client.get_account()
    if not account.get('success'):
        print(f"ERROR: Cannot connect to Brevo")
        return

    print(f"Account: {account['data'].get('companyName')}")

    # Load appointments
    print("\n=== Loading Appointments ===")
    appointments = load_all_appointments()
    print(f"Total appointments: {len(appointments)}")

    # Count by status
    status_counts = {}
    for appt in appointments:
        status = appt.get('status_category', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    print("By status:")
    for status, count in sorted(status_counts.items()):
        stage = STAGE_MAPPING.get(status, 'N/A')
        print(f"  {status}: {count} -> {stage}")

    # Import
    import_appointments(client, appointments, dry_run=args.dry_run)

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
