"""Find actual calls for our test contacts."""
import json
import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CALL_LOG_1 = Path(r'C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json')
CALL_LOG_2 = Path(r'C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json')

calls = []
for path in [CALL_LOG_1, CALL_LOG_2]:
    with open(path, 'r', encoding='utf-8') as f:
        calls.extend(json.load(f))

print(f'Total calls loaded: {len(calls)}')

# Find calls for phone 61402213582 (Bob Chalmers from appointments)
print('\n' + '=' * 60)
print('CALLS FOR BOB CHALMERS (61402213582):')
print('=' * 60)

bob_calls = []
for call in calls:
    to_num = str(call.get('to_number', ''))
    if to_num and to_num[-9:] == '402213582':
        bob_calls.append(call)

print(f'Found {len(bob_calls)} calls')
for call in bob_calls:
    start = call.get('start_time', '')
    duration = call.get('human_duration', '')
    direction = call.get('direction', 'outbound').upper()
    recording = call.get('recording_url', '')

    print(f'\n  Start: {start}')
    print(f'  Direction: {direction}')
    print(f'  Duration: {duration}')
    if recording and str(recording) != 'N/A':
        print(f'  Recording: {recording}')

print('\n' + '=' * 60)
print('WHAT RETELL_LOG SHOULD LOOK LIKE:')
print('=' * 60)

for call in bob_calls:
    start = call.get('start_time', '')
    duration = call.get('human_duration', 'N/A')
    direction = call.get('direction', 'outbound').upper()
    recording = call.get('recording_url', '')

    if start:
        # Parse "25/08/2025, 16:45:30" format
        date_part = start.split(',')[0].strip()
        time_full = start.split(',')[1].strip() if ',' in start else ''
        time_short = ':'.join(time_full.split(':')[:2])  # Remove seconds

        log_line = f'{date_part} {time_short} {direction} ({duration})'
        if recording and str(recording) != 'N/A':
            log_line += f' - Recording: {recording}'
        print(log_line)

print('\n' + '=' * 60)
print('CURRENTLY IN BREVO (from appointments CSV):')
print('=' * 60)
print('08/25/2025 16:45 phone_call')
print('\nMISSING: Direction, Duration, Recording URL!')
