#!/usr/bin/env python3
"""Check Zadarma call durations for appointment phones."""

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

    phone = '61404610402'

    print(f'=== ALL CALLS FOR {phone} ===')
    cur.execute('''
        SELECT
            c.id,
            p.name as provider,
            c.from_number,
            c.to_number,
            c.started_at,
            c.duration_seconds,
            c.disposition
        FROM telco.calls c
        JOIN telco.providers p ON p.provider_id = c.provider_id
        WHERE c.from_number LIKE %s
           OR c.to_number LIKE %s
        ORDER BY c.started_at
    ''', ('%' + phone + '%', '%' + phone + '%'))

    for row in cur.fetchall():
        print(f'{row[0]}: {row[1]} | {row[2]} -> {row[3]} | {row[4]} | {row[5]}s | {row[6]}')

    # Check the specific call at 19:20 that we know exists
    print()
    print('=== ZADARMA CALL 1603113 ===')
    cur.execute('SELECT * FROM telco.calls WHERE id = 1603113')
    row = cur.fetchone()
    print(f'Duration: {row}')

    conn.close()

if __name__ == "__main__":
    main()
