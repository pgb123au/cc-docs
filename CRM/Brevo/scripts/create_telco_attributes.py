"""
Create Telco Warehouse attributes in Brevo
"""
import sys
from brevo_api import BrevoClient

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = BrevoClient()

# New attributes for Telco Warehouse v6
TELCO_ATTRIBUTES = [
    # Total call counts
    ('TELCO_TOTAL_CALLS', 'float'),  # number
    ('TELCO_PROVIDER', 'text'),       # comma-separated list
    ('TELCO_CALL_SUMMARY', 'text'),   # AI-generated summary
    ('TELCO_SENTIMENT', 'text'),      # positive/negative/neutral

    # Provider-specific counts
    ('ZADARMA_CALL_COUNT', 'float'),  # number
    ('TELNYX_CALL_COUNT', 'float'),   # number
    ('RETELL_CALL_COUNT', 'float'),   # number (may already exist)

    # Retell-specific (may already exist)
    ('RETELL_CALL_ID', 'text'),
    ('RETELL_RECORDING_URL', 'text'),
    ('RETELL_PUBLIC_LOG_URL', 'text'),
    ('RETELL_TRANSCRIPT', 'text'),
    ('RETELL_CALL_DIRECTION', 'text'),
    ('RETELL_CALL_DURATION', 'text'),
    ('RETELL_CALL_STATUS', 'text'),
    ('RETELL_DISCONNECT_REASON', 'text'),
    ('RETELL_CALL_COST', 'float'),
    ('RETELL_LOG', 'text'),
]

def main():
    print("Creating Telco Warehouse attributes in Brevo...")
    print()

    created = 0
    existing = 0
    errors = 0

    for attr_name, attr_type in TELCO_ATTRIBUTES:
        result = client.create_attribute(attr_name, attr_type)

        if result.get('success'):
            print(f"  CREATED: {attr_name} ({attr_type})")
            created += 1
        else:
            error = result.get('error', '')
            if 'already exists' in str(error).lower() or 'duplicate' in str(error).lower():
                print(f"  EXISTS:  {attr_name}")
                existing += 1
            else:
                print(f"  ERROR:   {attr_name} - {error}")
                errors += 1

    print()
    print(f"Created: {created}")
    print(f"Already existed: {existing}")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()
