#!/usr/bin/env python3
"""
Investigate missing phone numbers in telco_warehouse database.
Check calls, contacts, and phone normalization for 5 specific numbers.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database connection
DB_CONFIG = {
    'host': '96.47.238.189',
    'port': 5432,
    'database': 'telco_warehouse',
    'user': 'telco_sync',
    'password': 'TelcoSync2024!'
}

# Numbers to investigate
MISSING_NUMBERS = [
    {'contact': 'Sara Lehmann', 'company': 'Reignite Health', 'phone': '+61437160997'},
    {'contact': 'Bob Chalmers', 'company': 'Paradise Distributors', 'phone': '+61408687109'},
    {'contact': 'Joe Van Stripe', 'company': 'JTW Building Group', 'phone': '+61424023677'},
    {'contact': 'Chantelle', 'company': 'Lumiere Home Renovations', 'phone': '+61423238679'},
    {'contact': 'Chris', 'company': 'CLG Electrics', 'phone': '+61402140955'}
]

def connect_db():
    """Connect to the database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None

def test_normalize_function(cursor, phone):
    """Test the telco.normalize_phone() function."""
    try:
        cursor.execute("SELECT telco.normalize_phone(%s) as normalized", (phone,))
        result = cursor.fetchone()
        return result['normalized'] if result else None
    except Exception as e:
        print(f"  [WARNING] normalize_phone error: {e}")
        return None

def search_calls_table(cursor, phone):
    """Search telco.calls for this number in from_number and to_number."""
    patterns = [
        phone,                          # +61437160997
        phone[1:],                      # 61437160997
        phone[-9:],                     # 437160997
        f"%{phone[-9:]}",               # %437160997
        f"%{phone}%",                   # %+61437160997%
        f"%{phone[1:]}%",               # %61437160997%
    ]

    results = {}

    for pattern in patterns:
        try:
            # Search from_number
            if '%' in pattern:
                cursor.execute("""
                    SELECT id, from_number, to_number, provider_id, started_at
                    FROM telco.calls
                    WHERE from_number LIKE %s
                    ORDER BY started_at DESC LIMIT 5
                """, (pattern,))
            else:
                cursor.execute("""
                    SELECT id, from_number, to_number, provider_id, started_at
                    FROM telco.calls
                    WHERE from_number = %s
                    ORDER BY started_at DESC LIMIT 5
                """, (pattern,))

            from_results = cursor.fetchall()

            # Search to_number
            if '%' in pattern:
                cursor.execute("""
                    SELECT id, from_number, to_number, provider_id, started_at
                    FROM telco.calls
                    WHERE to_number LIKE %s
                    ORDER BY started_at DESC LIMIT 5
                """, (pattern,))
            else:
                cursor.execute("""
                    SELECT id, from_number, to_number, provider_id, started_at
                    FROM telco.calls
                    WHERE to_number = %s
                    ORDER BY started_at DESC LIMIT 5
                """, (pattern,))

            to_results = cursor.fetchall()

            if from_results or to_results:
                results[pattern] = {
                    'from_number_matches': len(from_results),
                    'to_number_matches': len(to_results),
                    'sample_from': from_results[:2] if from_results else [],
                    'sample_to': to_results[:2] if to_results else []
                }
        except Exception as e:
            print(f"  [WARNING] Error searching pattern '{pattern}': {e}")

    return results

def search_contacts_table(cursor, phone):
    """Search telco.contacts for this phone number."""
    patterns = [
        phone,                          # +61437160997
        phone[1:],                      # 61437160997
        phone[-9:],                     # 437160997
        f"%{phone[-9:]}",               # %437160997
        f"%{phone}%",                   # %+61437160997%
        f"%{phone[1:]}%",               # %61437160997%
    ]

    results = {}

    for pattern in patterns:
        try:
            if '%' in pattern:
                cursor.execute("""
                    SELECT contact_id, phone_normalized, phone_display, contact_type,
                           total_calls, retell_calls, zadarma_calls
                    FROM telco.contacts
                    WHERE phone_normalized LIKE %s
                    LIMIT 10
                """, (pattern,))
            else:
                cursor.execute("""
                    SELECT contact_id, phone_normalized, phone_display, contact_type,
                           total_calls, retell_calls, zadarma_calls
                    FROM telco.contacts
                    WHERE phone_normalized = %s
                    LIMIT 10
                """, (pattern,))

            matches = cursor.fetchall()

            if matches:
                results[pattern] = {
                    'count': len(matches),
                    'samples': matches[:3]
                }
        except Exception as e:
            print(f"  [WARNING] Error searching contacts pattern '{pattern}': {e}")

    return results

def search_retell_calls_only(cursor, phone):
    """Search specifically for Retell calls (provider_id = 3)."""
    patterns = [phone, phone[1:], phone[-9:], f"%{phone[-9:]}%"]

    results = {}

    for pattern in patterns:
        try:
            if '%' in pattern:
                cursor.execute("""
                    SELECT id, from_number, to_number, started_at, duration_seconds
                    FROM telco.calls
                    WHERE provider_id = 3
                    AND (from_number LIKE %s OR to_number LIKE %s)
                    ORDER BY started_at DESC LIMIT 5
                """, (pattern, pattern))
            else:
                cursor.execute("""
                    SELECT id, from_number, to_number, started_at, duration_seconds
                    FROM telco.calls
                    WHERE provider_id = 3
                    AND (from_number = %s OR to_number = %s)
                    ORDER BY started_at DESC LIMIT 5
                """, (pattern, pattern))

            matches = cursor.fetchall()

            if matches:
                results[pattern] = {
                    'count': len(matches),
                    'samples': matches[:3]
                }
        except Exception as e:
            print(f"  [WARNING] Error searching Retell calls pattern '{pattern}': {e}")

    return results

def check_all_retell_numbers(cursor):
    """Get a sample of all Retell phone numbers to see formatting."""
    try:
        cursor.execute("""
            SELECT DISTINCT from_number
            FROM telco.calls
            WHERE provider_id = 3
            AND from_number IS NOT NULL
            ORDER BY from_number
            LIMIT 20
        """)
        from_numbers = [row['from_number'] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT DISTINCT to_number
            FROM telco.calls
            WHERE provider_id = 3
            AND to_number IS NOT NULL
            ORDER BY to_number
            LIMIT 20
        """)
        to_numbers = [row['to_number'] for row in cursor.fetchall()]

        return {
            'sample_from_numbers': from_numbers,
            'sample_to_numbers': to_numbers
        }
    except Exception as e:
        print(f"  [WARNING] Error getting Retell number samples: {e}")
        return {}

def main():
    """Main investigation function."""
    print("=" * 80)
    print("INVESTIGATING MISSING PHONE NUMBERS IN TELCO_WAREHOUSE")
    print("=" * 80)
    print()

    conn = connect_db()
    if not conn:
        return

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # First, check sample of Retell numbers
        print("[STEP 1] SAMPLE OF RETELL NUMBERS IN DATABASE")
        print("-" * 80)
        retell_samples = check_all_retell_numbers(cursor)
        if retell_samples:
            print("Sample from_numbers:")
            for num in retell_samples.get('sample_from_numbers', [])[:10]:
                print(f"  {num}")
            print("\nSample to_numbers:")
            for num in retell_samples.get('sample_to_numbers', [])[:10]:
                print(f"  {num}")
        print()

        # Now investigate each missing number
        for idx, record in enumerate(MISSING_NUMBERS, 1):
            contact = record['contact']
            company = record['company']
            phone = record['phone']

            print("=" * 80)
            print(f"[PHONE {idx}/5] - {contact} ({company})")
            print(f"Phone: {phone}")
            print("=" * 80)

            # Test normalize function
            print("\n[CHECK 1] NORMALIZE FUNCTION TEST")
            print("-" * 80)
            normalized = test_normalize_function(cursor, phone)
            print(f"Input:      {phone}")
            print(f"Normalized: {normalized}")

            # Search calls table
            print("\n[CHECK 2] SEARCHING telco.calls TABLE")
            print("-" * 80)
            calls_results = search_calls_table(cursor, phone)
            if calls_results:
                for pattern, data in calls_results.items():
                    print(f"\nPattern: {pattern}")
                    print(f"  from_number matches: {data['from_number_matches']}")
                    print(f"  to_number matches: {data['to_number_matches']}")
                    if data['sample_from']:
                        print(f"  Sample from_number hits:")
                        for row in data['sample_from']:
                            print(f"    {row['id']} | {row['from_number']} -> {row['to_number']} | Provider: {row['provider_id']} | {row['started_at']}")
                    if data['sample_to']:
                        print(f"  Sample to_number hits:")
                        for row in data['sample_to']:
                            print(f"    {row['id']} | {row['from_number']} -> {row['to_number']} | Provider: {row['provider_id']} | {row['started_at']}")
            else:
                print("  [NO MATCHES] Not found in calls table")

            # Search contacts table
            print("\n[CHECK 3] SEARCHING telco.contacts TABLE")
            print("-" * 80)
            contacts_results = search_contacts_table(cursor, phone)
            if contacts_results:
                for pattern, data in contacts_results.items():
                    print(f"\nPattern: {pattern}")
                    print(f"  Matches: {data['count']}")
                    for row in data['samples']:
                        print(f"    ID: {row['contact_id']} | Phone: {row['phone_normalized']} | Display: {row['phone_display']} | Type: {row['contact_type']} | Calls: {row['total_calls']} (Retell: {row['retell_calls']}, Zadarma: {row['zadarma_calls']})")
            else:
                print("  [NO MATCHES] Not found in contacts table")

            # Search Retell calls specifically
            print("\n[CHECK 4] SEARCHING RETELL CALLS ONLY (provider_id = 3)")
            print("-" * 80)
            retell_results = search_retell_calls_only(cursor, phone)
            if retell_results:
                for pattern, data in retell_results.items():
                    print(f"\nPattern: {pattern}")
                    print(f"  Matches: {data['count']}")
                    for row in data['samples']:
                        print(f"    {row['id']} | {row['from_number']} -> {row['to_number']} | {row['started_at']} | {row['duration_seconds']}s")
            else:
                print("  [NO MATCHES] Not found in Retell calls")

            print("\n")

        # Summary
        print("=" * 80)
        print("INVESTIGATION COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"[ERROR] Error during investigation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
