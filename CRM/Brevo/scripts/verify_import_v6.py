"""
Verify v6 import - Check all fields populated in Brevo
"""
import sys
import json
from brevo_api import BrevoClient

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = BrevoClient()

CONTACTS = [
    "sara@reignitehealth.com.au",
    "bchalmers616@gmail.com",
    "Joe@jtwbuildinggroup.com.au",
    "info@lumierehomerenovations.com.au",
    "chris@clgelectrics.com.au"
]

def main():
    print("=" * 70)
    print("V6 IMPORT VERIFICATION")
    print("=" * 70)
    print()

    for email in CONTACTS:
        print(f"\n{'=' * 60}")
        print(f"CONTACT: {email}")
        print(f"{'=' * 60}")

        result = client.get_contact(email)
        if not result.get('success'):
            print(f"  ERROR: {result.get('error')}")
            continue

        data = result['data']
        attrs = data.get('attributes', {})

        # Count non-empty fields
        non_empty = {k: v for k, v in attrs.items() if v is not None and str(v).strip()}
        print(f"\nTotal populated fields: {len(non_empty)}")

        # Key fields to check
        key_fields = [
            # Identity
            ('FIRSTNAME', 'Identity'),
            ('LASTNAME', 'Identity'),
            ('COMPANY', 'Identity'),
            # Phone
            ('SMS', 'Phone'),
            ('PHONE_2', 'Phone'),
            ('COMPANY_PHONE', 'Phone'),
            # Appointment
            ('APPOINTMENT_DATE', 'Appointment'),
            ('APPOINTMENT_STATUS', 'Appointment'),
            ('DEAL_STAGE', 'Appointment'),
            # Telco Warehouse
            ('TELCO_TOTAL_CALLS', 'Telco'),
            ('TELCO_PROVIDER', 'Telco'),
            ('RETELL_LOG', 'Telco'),
            ('RETELL_CALL_COUNT', 'Retell'),
            ('ZADARMA_CALL_COUNT', 'Zadarma'),
            # HubSpot
            ('HUBSPOT_RAW_JSON', 'HubSpot'),
            ('INDUSTRY', 'HubSpot'),
            ('CITY', 'Location'),
            ('STATE_REGION', 'Location'),
        ]

        print("\nKey fields:")
        categories = {}
        for field, category in key_fields:
            value = attrs.get(field)
            status = "OK" if value else "MISSING"

            if category not in categories:
                categories[category] = {'present': 0, 'missing': 0}

            if value:
                categories[category]['present'] += 1
                # Truncate long values
                if isinstance(value, str) and len(value) > 60:
                    display = value[:57] + "..."
                else:
                    display = value
                print(f"  {status:7} {field}: {display}")
            else:
                categories[category]['missing'] += 1
                print(f"  {status:7} {field}")

        print("\nCategory summary:")
        for cat, counts in categories.items():
            total = counts['present'] + counts['missing']
            pct = counts['present'] / total * 100 if total > 0 else 0
            print(f"  {cat}: {counts['present']}/{total} ({pct:.0f}%)")

        # List all populated fields
        print("\nAll populated fields:")
        for k, v in sorted(non_empty.items()):
            if isinstance(v, str) and len(v) > 50:
                v = v[:47] + "..."
            print(f"  - {k}: {v}")

    print()
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
