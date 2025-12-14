#!/usr/bin/env python3
"""Debug NULL phone numbers in Retell calls."""

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

    print('=== RETELL CALLS BY PHONE NUMBER STATUS ===')
    cur.execute('''
        SELECT
            CASE
                WHEN from_number IS NULL AND to_number IS NULL THEN 'Both NULL'
                WHEN from_number IS NULL THEN 'From NULL only'
                WHEN to_number IS NULL THEN 'To NULL only'
                ELSE 'Both populated'
            END as phone_status,
            COUNT(*) as cnt,
            COUNT(CASE WHEN transcript IS NOT NULL AND LENGTH(transcript) > 50 THEN 1 END) as with_transcript,
            AVG(duration_seconds) as avg_duration
        FROM telco.calls
        WHERE provider_id = 3
        GROUP BY 1
        ORDER BY cnt DESC
    ''')
    for row in cur.fetchall():
        avg = f'{row[3]:.1f}s' if row[3] else 'N/A'
        print(f'{row[0]}: {row[1]} calls, {row[2]} with transcripts, avg {avg}')

    print()
    print('=== SAMPLE CALLS WITH BOTH NULL PHONES BUT TRANSCRIPTS ===')
    cur.execute('''
        SELECT
            id,
            external_call_id,
            started_at,
            duration_seconds,
            raw_data->>'from_number' as raw_from,
            raw_data->>'to_number' as raw_to,
            LEFT(transcript, 150) as transcript_preview
        FROM telco.calls
        WHERE provider_id = 3
          AND from_number IS NULL
          AND to_number IS NULL
          AND transcript IS NOT NULL
          AND duration_seconds > 60
        ORDER BY duration_seconds DESC
        LIMIT 3
    ''')
    for row in cur.fetchall():
        print(f'ID: {row[0]} | {row[2]} | {row[3]}s')
        print(f'  External ID: {row[1]}')
        print(f'  Raw from: {row[4]}')
        print(f'  Raw to: {row[5]}')
        print(f'  Transcript: {row[6]}...')
        print()

    # Check if raw_data has phone numbers
    print('=== CHECK RAW_DATA FOR PHONE NUMBERS ===')
    cur.execute('''
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN raw_data->>'from_number' IS NOT NULL THEN 1 END) as has_raw_from,
            COUNT(CASE WHEN raw_data->>'to_number' IS NOT NULL THEN 1 END) as has_raw_to,
            COUNT(CASE WHEN raw_data->>'toNumber' IS NOT NULL THEN 1 END) as has_raw_toNumber
        FROM telco.calls
        WHERE provider_id = 3
          AND from_number IS NULL
          AND to_number IS NULL
    ''')
    row = cur.fetchone()
    print(f'Calls with NULL phone cols: {row[0]}')
    print(f'  Has raw_data.from_number: {row[1]}')
    print(f'  Has raw_data.to_number: {row[2]}')
    print(f'  Has raw_data.toNumber: {row[3]}')

    # Sample raw_data structure
    print()
    print('=== SAMPLE RAW_DATA KEYS ===')
    cur.execute('''
        SELECT raw_data
        FROM telco.calls
        WHERE provider_id = 3
          AND from_number IS NULL
          AND transcript IS NOT NULL
        LIMIT 1
    ''')
    row = cur.fetchone()
    if row and row[0]:
        print(f'Keys: {list(row[0].keys())[:20]}')

    conn.close()

if __name__ == "__main__":
    main()
