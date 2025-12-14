#!/usr/bin/env python3
"""Link Retell calls (with transcripts) to Zadarma calls (with phone numbers)."""

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

    # The appointment phone numbers
    phones = ['61404610402', '61418127174', '61402213582', '61421189252']

    print('=== LINKING RETELL TRANSCRIPTS TO ZADARMA PHONE NUMBERS ===')
    print()

    for phone in phones:
        print(f'--- Phone: {phone} ---')

        # Find Zadarma calls with this phone
        cur.execute('''
            SELECT id, from_number, to_number, started_at, duration_seconds
            FROM telco.calls
            WHERE provider_id = 1  -- Zadarma
              AND (to_number LIKE %s OR from_number LIKE %s)
              AND duration_seconds > 30
            ORDER BY started_at DESC
            LIMIT 5
        ''', ('%' + phone + '%', '%' + phone + '%'))

        zadarma_calls = cur.fetchall()

        for zid, zfrom, zto, zstart, zdur in zadarma_calls:
            print(f'\nZadarma: {zid} | {zfrom} -> {zto} | {zstart} | {zdur}s')

            # Find matching Retell call within 30 seconds and similar duration
            cur.execute('''
                SELECT
                    id,
                    external_call_id,
                    started_at,
                    duration_seconds,
                    LEFT(transcript, 200) as trans_preview
                FROM telco.calls
                WHERE provider_id = 3  -- Retell
                  AND from_number IS NULL
                  AND transcript IS NOT NULL
                  AND ABS(EXTRACT(EPOCH FROM (started_at - %s))) < 30
                  AND ABS(duration_seconds - %s) < 15
                ORDER BY ABS(EXTRACT(EPOCH FROM (started_at - %s)))
                LIMIT 1
            ''', (zstart, zdur, zstart))

            retell = cur.fetchone()
            if retell:
                print(f'  -> MATCHED Retell: {retell[0]} | {retell[1][:30]}...')
                print(f'     Started: {retell[2]} | Dur: {retell[3]}s')
                preview = retell[4] or ''
                print(f'     Transcript: {preview[:100].encode("ascii", "replace").decode("ascii")}...')
            else:
                print('  -> No matching Retell call found')

        print()

    conn.close()

if __name__ == "__main__":
    main()
