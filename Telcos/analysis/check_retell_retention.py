#!/usr/bin/env python3
"""Check what date range of calls exists in Retell API."""

import requests
from datetime import datetime

def main():
    api_key = open('C:/Users/peter/Downloads/Retell_API_Key.txt').read().strip()
    headers = {'Authorization': f'Bearer {api_key}'}

    print('=== CHECKING RETELL API CALL RETENTION ===')

    # Get oldest calls (ascending)
    payload = {
        'limit': 5,
        'sort_order': 'ascending'
    }
    response = requests.post(
        'https://api.retellai.com/v2/list-calls',
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        calls = response.json()
        print(f'\nOLDEST {len(calls)} calls in API:')
        for c in calls:
            start_ts = c.get('start_timestamp', 0)
            dt = datetime.fromtimestamp(start_ts / 1000) if start_ts else None
            print(f"  {c.get('call_id', 'N/A')[:30]}... | {dt} | {c.get('to_number')}")
    else:
        print(f'Error: {response.status_code} - {response.text[:200]}')

    # Get newest calls (descending)
    payload = {
        'limit': 5,
        'sort_order': 'descending'
    }
    response = requests.post(
        'https://api.retellai.com/v2/list-calls',
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        calls = response.json()
        print(f'\nNEWEST {len(calls)} calls in API:')
        for c in calls:
            start_ts = c.get('start_timestamp', 0)
            dt = datetime.fromtimestamp(start_ts / 1000) if start_ts else None
            print(f"  {c.get('call_id', 'N/A')[:30]}... | {dt} | {c.get('to_number')}")

    # Try to get a specific call we know exists
    print('\n=== TRYING SPECIFIC CALL ID ===')
    call_id = 'call_9c79e4d26fdee6c5119edabd0c2'
    response = requests.get(
        f'https://api.retellai.com/v2/get-call/{call_id}',
        headers=headers
    )
    print(f'call_9c79e4d... status: {response.status_code}')
    if response.status_code == 404:
        print('  EXPIRED - call no longer in Retell')
    elif response.status_code == 200:
        c = response.json()
        print(f'  Found! from: {c.get("from_number")} to: {c.get("to_number")}')

    # Check total count
    print('\n=== GETTING TOTAL COUNT ===')
    payload = {'limit': 1}
    response = requests.post(
        'https://api.retellai.com/v2/list-calls',
        headers=headers,
        json=payload
    )
    # The API doesn't return total count, but we can paginate
    # Let's just get a count estimate
    payload = {'limit': 1000, 'sort_order': 'ascending'}
    response = requests.post(
        'https://api.retellai.com/v2/list-calls',
        headers=headers,
        json=payload
    )
    if response.status_code == 200:
        calls = response.json()
        if calls:
            oldest = datetime.fromtimestamp(calls[0].get('start_timestamp', 0) / 1000)
            print(f'First 1000 calls start from: {oldest}')

if __name__ == "__main__":
    main()
