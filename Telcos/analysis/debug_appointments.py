#!/usr/bin/env python3
"""Debug why appointment phone numbers have no transcripts."""

import psycopg2
import requests
from datetime import datetime

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

    phones = ['418127174', '402213582', '421189252']

    for phone in phones:
        print(f"\n{'='*60}")
        print(f"=== PHONE: {phone} ===")
        print(f"{'='*60}")

        # Get all calls for this phone
        cur.execute('''
            SELECT
                c.id,
                c.external_call_id,
                c.from_number,
                c.to_number,
                c.started_at,
                c.duration_seconds,
                c.disposition,
                p.name as provider,
                CASE WHEN c.transcript IS NOT NULL AND LENGTH(c.transcript) > 10 THEN 'YES' ELSE 'NO' END as has_transcript
            FROM telco.calls c
            JOIN telco.providers p ON p.provider_id = c.provider_id
            WHERE c.from_number LIKE %s
               OR c.to_number LIKE %s
            ORDER BY c.started_at DESC
        ''', ('%' + phone + '%', '%' + phone + '%'))

        rows = cur.fetchall()
        print(f"\nTotal calls in DB: {len(rows)}")

        for row in rows[:5]:
            print(f"\nID: {row[0]}")
            print(f"  External ID: {row[1]}")
            print(f"  From: {row[2]} -> To: {row[3]}")
            print(f"  Date: {row[4]} | Duration: {row[5]}s")
            print(f"  Disposition: {row[6]} | Provider: {row[7]}")
            print(f"  Has Transcript: {row[8]}")

        # If there are Retell calls, check Retell API directly
        retell_rows = [r for r in rows if r[7] == 'retell']
        if retell_rows:
            print(f"\n--- Checking Retell API for external_call_id ---")
            API_KEY = open('C:/Users/peter/Downloads/Retell_API_Key.txt').read().strip()
            headers = {'Authorization': f'Bearer {API_KEY}'}

            for row in retell_rows[:2]:
                ext_id = row[1]
                if ext_id:
                    response = requests.get(
                        f'https://api.retellai.com/v2/get-call/{ext_id}',
                        headers=headers
                    )
                    if response.status_code == 200:
                        call = response.json()
                        print(f"\nRetell API for {ext_id}:")
                        print(f"  Status: {call.get('call_status')}")
                        print(f"  Duration: {call.get('duration_ms', 0)//1000}s")
                        print(f"  From: {call.get('from_number')} -> To: {call.get('to_number')}")
                        has_trans = bool(call.get('transcript'))
                        print(f"  Has transcript in API: {has_trans}")
                        if has_trans:
                            print(f"  Transcript preview: {call.get('transcript', '')[:200]}...")

                        # Check call_analysis
                        print(f"  call_successful: {call.get('call_analysis', {}).get('call_successful')}")
                        print(f"  user_sentiment: {call.get('call_analysis', {}).get('user_sentiment')}")
                        summary = call.get('call_analysis', {}).get('call_summary', '')
                        if summary:
                            print(f"  Summary: {summary[:150]}...")
                    else:
                        print(f"  API Error for {ext_id}: {response.status_code}")

    conn.close()

if __name__ == "__main__":
    main()
