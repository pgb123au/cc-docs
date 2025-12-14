#!/usr/bin/env python3
"""Show full details of the specific call."""

import psycopg2

DB_CONFIG = {
    'host': '96.47.238.189',
    'port': 5432,
    'database': 'telco_warehouse',
    'user': 'telco_sync',
    'password': 'TelcoSync2024!'
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get the full call record
    cur.execute('''
        SELECT
            id,
            external_call_id,
            from_number,
            to_number,
            started_at,
            duration_seconds,
            transcript,
            raw_data
        FROM telco.calls
        WHERE id = 1567999
    ''')
    row = cur.fetchone()

    print('=== RETELL CALL (ID 1567999) ===')
    print(f'external_call_id: {row[1]}')
    print(f'from_number: {row[2]}')
    print(f'to_number: {row[3]}')
    print(f'started_at: {row[4]}')
    print(f'duration: {row[5]}s')
    print()
    print('=== TRANSCRIPT ===')
    transcript = row[6] or ''
    # Handle unicode issues on Windows
    print(transcript.encode('ascii', 'replace').decode('ascii'))
    print()

    # Check raw_data for phone numbers
    raw = row[7]
    if raw:
        print('=== RAW_DATA phone fields ===')
        print(f"from_number in raw_data: {raw.get('from_number')}")
        print(f"to_number in raw_data: {raw.get('to_number')}")
        print(f"toNumber in raw_data: {raw.get('toNumber')}")
        print(f"fromNumber in raw_data: {raw.get('fromNumber')}")

    # Get the matching Zadarma call
    print()
    print('=== ZADARMA CALL (same phone) ===')
    cur.execute('''
        SELECT id, from_number, to_number, started_at, duration_seconds, raw_data
        FROM telco.calls
        WHERE id = 1603113
    ''')
    row = cur.fetchone()
    print(f'ID: {row[0]}')
    print(f'from: {row[1]} -> to: {row[2]}')
    print(f'started: {row[3]} | dur: {row[4]}s')

    raw = row[5]
    if raw:
        print('Raw data sample keys:', list(raw.keys())[:10])

    conn.close()

if __name__ == "__main__":
    main()
