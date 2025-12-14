#!/usr/bin/env python3
"""Fetch full Retell data for appointment phone numbers and update database."""

import psycopg2
import requests
import json
from datetime import datetime

DB_CONFIG = {
    'host': '96.47.238.189',
    'port': 5432,
    'database': 'telco_warehouse',
    'user': 'telco_sync',
    'password': 'TelcoSync2024!'
}

# Appointment phone numbers from APPOINTMENTS_MOBILE_NUMBERS.md
APPOINTMENT_PHONES = [
    '+61402140955',
    '+61402213582',
    '+61404610402',
    '+61418127174',
    '+61421189252',
    '+61425757530',
    '+61431413530',
    '+61431587938',
]

def get_retell_calls(api_key, to_number):
    """Fetch all calls to a specific number from Retell API."""
    headers = {'Authorization': f'Bearer {api_key}'}

    all_calls = []

    # Use filter_criteria to find calls to this number
    payload = {
        'filter_criteria': {
            'to_number': [to_number]
        },
        'limit': 1000,
        'sort_order': 'descending'
    }

    response = requests.post(
        'https://api.retellai.com/v2/list-calls',
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        all_calls.extend(data)
        print(f"  Found {len(data)} calls to {to_number}")
    else:
        print(f"  API error for {to_number}: {response.status_code} - {response.text[:200]}")

    return all_calls

def main():
    # Load API key - Telco DB Sync workspace (has the May 2025 campaign data)
    api_key = 'key_b8d6bd5512827f71f1f1202e06a4'

    print('=== FETCHING RETELL DATA FOR APPOINTMENT PHONES ===')
    print(f'Phones to query: {len(APPOINTMENT_PHONES)}')
    print()

    all_calls = []

    for phone in APPOINTMENT_PHONES:
        print(f'Querying: {phone}')
        calls = get_retell_calls(api_key, phone)
        all_calls.extend(calls)

    print(f'\nTotal calls found: {len(all_calls)}')

    if not all_calls:
        print('No calls found!')
        return

    # Show sample of data available
    print('\n=== SAMPLE CALL DATA ===')
    if all_calls:
        sample = all_calls[0]
        print(f'Available fields: {list(sample.keys())}')
        print(f'\nSample call:')
        print(f'  call_id: {sample.get("call_id")}')
        print(f'  from_number: {sample.get("from_number")}')
        print(f'  to_number: {sample.get("to_number")}')
        print(f'  start_timestamp: {sample.get("start_timestamp")}')
        print(f'  end_timestamp: {sample.get("end_timestamp")}')
        print(f'  duration_ms: {sample.get("duration_ms")}')
        print(f'  call_status: {sample.get("call_status")}')
        print(f'  disconnection_reason: {sample.get("disconnection_reason")}')
        transcript = sample.get('transcript', '')
        if transcript:
            print(f'  transcript (preview): {str(transcript)[:200]}...')
        print(f'  call_analysis: {sample.get("call_analysis", {})}')

    # Connect to database and update
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    updated = 0
    inserted = 0

    for call in all_calls:
        call_id = call.get('call_id')
        from_num = call.get('from_number')
        to_num = call.get('to_number')

        # Get transcript - could be string or list of objects
        transcript_raw = call.get('transcript', '')
        if isinstance(transcript_raw, list):
            # Format as conversation
            lines = []
            for turn in transcript_raw:
                role = turn.get('role', 'unknown').capitalize()
                content = turn.get('content', '')
                lines.append(f'{role}: {content}')
            transcript = '\n'.join(lines)
        else:
            transcript = str(transcript_raw) if transcript_raw else ''

        # Check if call exists
        cur.execute('''
            SELECT id, from_number, to_number, transcript
            FROM telco.calls
            WHERE external_call_id = %s
        ''', (call_id,))
        existing = cur.fetchone()

        if existing:
            db_id, db_from, db_to, db_trans = existing
            # Update if phone numbers or transcript missing
            if db_from is None or db_to is None or not db_trans:
                cur.execute('''
                    UPDATE telco.calls
                    SET from_number = COALESCE(%s, from_number),
                        to_number = COALESCE(%s, to_number),
                        transcript = COALESCE(NULLIF(%s, ''), transcript),
                        raw_data = %s
                    WHERE external_call_id = %s
                ''', (from_num, to_num, transcript, json.dumps(call), call_id))
                updated += 1
                print(f'  Updated: {call_id} ({from_num} -> {to_num})')
        else:
            # Insert new call
            start_ts = call.get('start_timestamp')
            end_ts = call.get('end_timestamp')
            duration_ms = call.get('duration_ms', 0)
            duration_s = duration_ms // 1000 if duration_ms else 0

            # Convert timestamp (milliseconds) to datetime
            started_at = None
            ended_at = None
            if start_ts:
                started_at = datetime.fromtimestamp(start_ts / 1000)
            if end_ts:
                ended_at = datetime.fromtimestamp(end_ts / 1000)

            cur.execute('''
                INSERT INTO telco.calls (
                    provider_id, external_call_id, from_number, to_number,
                    direction, started_at, ended_at, duration_seconds,
                    disposition, transcript, raw_data
                ) VALUES (
                    3, %s, %s, %s, 'outbound', %s, %s, %s, %s, %s, %s
                )
            ''', (
                call_id, from_num, to_num, started_at, ended_at, duration_s,
                call.get('disconnection_reason'), transcript, json.dumps(call)
            ))
            inserted += 1
            print(f'  Inserted: {call_id} ({from_num} -> {to_num})')

    conn.commit()
    conn.close()

    print(f'\n=== SUMMARY ===')
    print(f'Total calls from API: {len(all_calls)}')
    print(f'Updated in DB: {updated}')
    print(f'Inserted to DB: {inserted}')

if __name__ == "__main__":
    main()
