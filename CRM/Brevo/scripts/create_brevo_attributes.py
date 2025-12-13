"""
Create all Brevo attributes needed for comprehensive import.
Includes IMPORT_BATCH for tracking which batch contacts were imported in.
"""
from brevo_api import BrevoClient
import time

client = BrevoClient()

# All attributes to create with their types
# Format: (name, type, category)
# Types: text, date, float (number), boolean
ATTRIBUTES_TO_CREATE = [
    # Tracking (for batch imports)
    ("IMPORT_BATCH", "text", "normal"),

    # Identity
    ("PHONE_2", "text", "normal"),
    ("PHONE_3", "text", "normal"),
    ("WORK_EMAIL", "text", "normal"),

    # Location
    ("STREET_ADDRESS", "text", "normal"),
    ("CITY", "text", "normal"),
    ("SUBURB", "text", "normal"),
    ("STATE_REGION", "text", "normal"),
    ("POSTAL_CODE", "text", "normal"),
    ("COUNTRY", "text", "normal"),

    # Company
    ("COMPANY_DOMAIN", "text", "normal"),
    ("COMPANY_EMAIL", "text", "normal"),
    ("COMPANY_PHONE", "text", "normal"),

    # Professional
    ("SENIORITY", "text", "normal"),
    ("INDUSTRY", "text", "normal"),
    ("BUSINESS_TYPE", "text", "normal"),
    ("VERTICAL", "text", "normal"),

    # Social
    ("TWITTER", "text", "normal"),
    ("FACEBOOK", "text", "normal"),
    ("INSTAGRAM", "text", "normal"),
    ("YOUTUBE", "text", "normal"),
    ("GOOGLE_PROFILE", "text", "normal"),

    # Business Intelligence
    ("ANNUAL_REVENUE", "float", "normal"),
    ("NUMBER_OF_EMPLOYEES", "float", "normal"),
    ("YEAR_FOUNDED", "float", "normal"),
    ("TOTAL_MONEY_RAISED", "text", "normal"),
    ("IS_PUBLIC", "boolean", "normal"),

    # Google Reviews
    ("GOOGLE_REVIEWS_COUNT", "float", "normal"),
    ("GBP_RATING", "float", "normal"),
    ("GOOGLE_5_STARS", "float", "normal"),

    # Lead/Marketing
    ("LEAD_SOURCE", "text", "normal"),
    ("LEAD_STATUS", "text", "normal"),
    ("LEAD_TYPE", "text", "normal"),
    ("LEAD_SCORE", "float", "normal"),
    ("ORIGINAL_SOURCE", "text", "normal"),
    ("TAGS", "text", "normal"),
    ("LAST_ACTIVITY_DATE", "date", "normal"),

    # Email Quality
    ("EMAIL_VALIDATION", "text", "normal"),
    ("NEVERBOUNCE_RESULT", "text", "normal"),
    ("HARD_BOUNCE_REASON", "text", "normal"),
    ("EMAIL_QUARANTINED", "boolean", "normal"),

    # System
    ("CURRENT_MARKETING_SUPPLIER", "text", "normal"),
    ("BUSINESS_DESCRIPTION", "text", "normal"),
    ("WAS_CALLED", "boolean", "normal"),
    ("CALL_COUNT", "float", "normal"),
    ("SOURCE_LIST", "text", "normal"),

    # JSON Metadata Blobs
    ("HUBSPOT_CONTACT_META", "text", "normal"),
    ("HUBSPOT_COMPANY_META", "text", "normal"),
    ("SOCIAL_LINKS_JSON", "text", "normal"),
    ("LOCATION_JSON", "text", "normal"),
]

def get_existing_attributes():
    """Get list of existing attribute names."""
    result = client._request('GET', 'contacts/attributes')
    if result.get('success'):
        return [a['name'] for a in result['data'].get('attributes', [])]
    return []

def create_attribute(name, attr_type, category="normal"):
    """Create a single attribute."""
    # Brevo API uses different type names
    type_map = {
        "text": "text",
        "date": "date",
        "float": "float",
        "boolean": "boolean"
    }

    data = {
        "type": type_map.get(attr_type, "text")
    }

    result = client._request('POST', f'contacts/attributes/{category}/{name}', data)
    return result

def main():
    print("=" * 60)
    print("CREATING BREVO ATTRIBUTES")
    print("=" * 60)

    # Get existing attributes
    existing = get_existing_attributes()
    print(f"\nExisting attributes: {len(existing)}")

    # Create missing attributes
    created = 0
    skipped = 0
    errors = []

    for name, attr_type, category in ATTRIBUTES_TO_CREATE:
        if name in existing:
            print(f"  SKIP: {name} (already exists)")
            skipped += 1
            continue

        result = create_attribute(name, attr_type, category)
        if result.get('success'):
            print(f"  CREATE: {name} ({attr_type})")
            created += 1
        else:
            error = result.get('error', 'Unknown error')
            if 'already exist' in str(error).lower():
                print(f"  SKIP: {name} (already exists)")
                skipped += 1
            else:
                print(f"  ERROR: {name} - {error}")
                errors.append((name, error))

        time.sleep(0.1)  # Rate limit

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Created: {created}")
    print(f"Skipped (existing): {skipped}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for name, error in errors:
            print(f"  {name}: {error}")

    # Verify final count
    final_attrs = get_existing_attributes()
    print(f"\nTotal attributes now: {len(final_attrs)}")

if __name__ == "__main__":
    main()
