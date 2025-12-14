#!/usr/bin/env python3
"""Backfill phone numbers for Retell calls that have NULL phones."""

import psycopg2
import requests
import time

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

    API_KEY = open('C:/Users/peter/Downloads/Retell_API_Key.txt').read().strip()
    headers = {'Authorization': f'Bearer {API_KEY}'}

    print('=== BACKFILLING PHONE NUMBERS FROM RETELL API ===')

    # Get calls with NULL phones
    cur.execute('''
        SELECT external_call_id, started_at, duration_seconds
        FROM telco.calls
        WHERE provider_id = 3
          AND from_number IS NULL
          AND to_number IS NULL
          AND transcript IS NOT NULL
          AND duration_seconds > 60
        ORDER BY started_at DESC
        LIMIT 10
    ''')
    calls = cur.fetchall()
    print(f'Found {len(calls)} calls to check')

    updated = 0
    not_found = 0

    for ext_id, started_at, duration in calls:
        print(f'\nCall: {ext_id} | {started_at} | {duration}s')

        response = requests.get(
            f'https://api.retellai.com/v2/get-call/{ext_id}',
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            from_num = data.get('from_number')
            to_num = data.get('to_number')
            print(f'  API says: {from_num} -> {to_num}')

            if from_num or to_num:
                cur.execute('''
                    UPDATE telco.calls
                    SET from_number = COALESCE(%s, from_number),
                        to_number = COALESCE(%s, to_number)
                    WHERE external_call_id = %s
                ''', (from_num, to_num, ext_id))
                updated += 1
                print(f'  UPDATED!')
        elif response.status_code == 404:
            print(f'  NOT FOUND (call expired in Retell)')
            not_found += 1
        else:
            print(f'  API error: {response.status_code}')

        time.sleep(0.1)  # Rate limit

    conn.commit()
    conn.close()

    print(f'\n=== SUMMARY ===')
    print(f'Checked: {len(calls)}')
    print(f'Updated: {updated}')
    print(f'Not found (expired): {not_found}')

if __name__ == "__main__":
    main()
