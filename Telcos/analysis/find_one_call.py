#!/usr/bin/env python3
"""Find the specific call: call_9c79e4d26fdee6c5119...0c2, phone +61404610402"""

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

    print('=== SEARCHING FOR SPECIFIC CALL ===')
    print('Target: call_9c79e4d26fdee6c5119...0c2')
    print('Phone: +61404610402')
    print('Date: 2025-05-27')
    print()

    # Search 1: By partial call ID
    print('--- Search by call_id pattern ---')
    cur.execute('''
        SELECT
            id,
            external_call_id,
            from_number,
            to_number,
            started_at,
            duration_seconds,
            disposition,
            CASE WHEN transcript IS NOT NULL THEN LENGTH(transcript) ELSE 0 END as transcript_len,
            provider_id
        FROM telco.calls
        WHERE external_call_id LIKE 'call_9c79e4d26fdee6c5119%'
        LIMIT 5
    ''')
    rows = cur.fetchall()
    print(f'Found by call_id: {len(rows)}')
    for row in rows:
        print(f'  ID: {row[0]}')
        print(f'  external_call_id: {row[1]}')
        print(f'  from: {row[2]} -> to: {row[3]}')
        print(f'  started: {row[4]} | dur: {row[5]}s | disp: {row[6]}')
        print(f'  transcript_len: {row[7]} | provider_id: {row[8]}')
        print()

    # Search 2: By phone number (multiple formats)
    print('--- Search by phone 404610402 ---')
    cur.execute('''
        SELECT
            id,
            external_call_id,
            from_number,
            to_number,
            started_at,
            duration_seconds,
            CASE WHEN transcript IS NOT NULL THEN LENGTH(transcript) ELSE 0 END as transcript_len
        FROM telco.calls
        WHERE from_number LIKE '%404610402%'
           OR to_number LIKE '%404610402%'
        ORDER BY started_at DESC
        LIMIT 10
    ''')
    rows = cur.fetchall()
    print(f'Found by phone: {len(rows)}')
    for row in rows:
        print(f'  {row[0]}: {row[2]} -> {row[3]} | {row[4]} | {row[5]}s | trans:{row[6]}')

    # Search 3: Check if call exists with NULL phones on that date
    print()
    print('--- Calls on 2025-05-27 with NULL phones that have transcripts ---')
    cur.execute('''
        SELECT
            id,
            external_call_id,
            started_at,
            duration_seconds,
            CASE WHEN transcript IS NOT NULL THEN LENGTH(transcript) ELSE 0 END as transcript_len,
            LEFT(transcript, 100) as transcript_preview
        FROM telco.calls
        WHERE from_number IS NULL
          AND to_number IS NULL
          AND transcript IS NOT NULL
          AND started_at::date = '2025-05-27'
          AND duration_seconds > 60
        ORDER BY started_at
        LIMIT 20
    ''')
    rows = cur.fetchall()
    print(f'Found {len(rows)} calls with NULL phones but transcripts on 2025-05-27')
    for row in rows:
        print(f'  {row[0]}: {row[1][:40]}... | {row[2]} | {row[3]}s | trans_len:{row[4]}')

    # Search 4: Look for the specific call ID with wildcard
    print()
    print('--- Search for any call_9c79e4d% ---')
    cur.execute('''
        SELECT external_call_id, from_number, to_number, started_at, duration_seconds
        FROM telco.calls
        WHERE external_call_id LIKE 'call_9c79e4d%'
        LIMIT 5
    ''')
    rows = cur.fetchall()
    print(f'Found: {len(rows)}')
    for row in rows:
        print(f'  {row[0]} | {row[1]} -> {row[2]} | {row[3]} | {row[4]}s')

    # Search 5: Check call_analysis table for this call
    print()
    print('--- Search call_analysis for call_9c79e4d% ---')
    cur.execute('''
        SELECT call_id, user_sentiment, call_successful, LEFT(call_summary, 200)
        FROM telco.call_analysis
        WHERE call_id LIKE 'call_9c79e4d%'
        LIMIT 5
    ''')
    rows = cur.fetchall()
    print(f'Found in call_analysis: {len(rows)}')
    for row in rows:
        print(f'  {row[0]}')
        print(f'  sentiment: {row[1]} | successful: {row[2]}')
        print(f'  summary: {row[3]}')

    conn.close()

if __name__ == "__main__":
    main()
