#!/usr/bin/env python3
"""
Check the schema of telco.calls and telco.contacts tables.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': '96.47.238.189',
    'port': 5432,
    'database': 'telco_warehouse',
    'user': 'telco_sync',
    'password': 'TelcoSync2024!'
}

def check_schema():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Check calls table schema
    print("=" * 80)
    print("TELCO.CALLS TABLE SCHEMA")
    print("=" * 80)
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'telco' AND table_name = 'calls'
        ORDER BY ordinal_position;
    """)
    for row in cursor.fetchall():
        print(f"{row['column_name']:<30} {row['data_type']:<20} nullable={row['is_nullable']}")

    print("\n" + "=" * 80)
    print("TELCO.CONTACTS TABLE SCHEMA")
    print("=" * 80)
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'telco' AND table_name = 'contacts'
        ORDER BY ordinal_position;
    """)
    for row in cursor.fetchall():
        print(f"{row['column_name']:<30} {row['data_type']:<20} nullable={row['is_nullable']}")

    # Sample some calls
    print("\n" + "=" * 80)
    print("SAMPLE CALLS DATA")
    print("=" * 80)
    cursor.execute("""
        SELECT * FROM telco.calls
        WHERE provider_id = 3
        ORDER BY call_start_time DESC
        LIMIT 3;
    """)
    for row in cursor.fetchall():
        print(dict(row))
        print()

    # Sample some contacts
    print("\n" + "=" * 80)
    print("SAMPLE CONTACTS DATA")
    print("=" * 80)
    cursor.execute("""
        SELECT * FROM telco.contacts
        WHERE phone_normalized LIKE '%437%' OR phone_normalized LIKE '%408%'
        LIMIT 5;
    """)
    contacts = cursor.fetchall()
    if contacts:
        for row in contacts:
            print(dict(row))
            print()
    else:
        print("No contacts found with those patterns")

    # Also check if name/company fields exist
    print("\n" + "=" * 80)
    print("CHECKING FOR NAME/COMPANY FIELDS IN CONTACTS")
    print("=" * 80)
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'telco' AND table_name = 'contacts'
        AND column_name IN ('name', 'company', 'first_name', 'last_name', 'company_name')
    """)
    name_fields = cursor.fetchall()
    if name_fields:
        print("Found name/company fields:")
        for f in name_fields:
            print(f"  - {f['column_name']}")
    else:
        print("No name or company fields found in contacts table")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_schema()
