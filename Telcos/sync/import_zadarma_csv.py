#!/usr/bin/env python3
"""Import Zadarma CSV exports into telco_warehouse database"""

import csv
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import sys

CSV_FILES = [
    r"C:\Users\peter\Downloads\stats-general-user-2261273-20250531235959.csv",
    r"C:\Users\peter\Downloads\stats-general-user-2261273-20250630235959.csv",
    r"C:\Users\peter\Downloads\stats-general-user-2261273-20250731235959.csv",
    r"C:\Users\peter\Downloads\stats-general-user-2261273-20250831235959.csv",
    r"C:\Users\peter\Downloads\stats-general-user-2261273-20250930235959.csv",
]

DB_CONFIG = {
    'host': '96.47.238.189',
    'port': 5432,
    'database': 'telco_warehouse',
    'user': 'telco_sync',
    'password': 'TelcoSync2024!'
}

def import_csv(conn, csv_file, provider_id=1):
    """Import a single CSV file"""
    filename = csv_file.split('\\')[-1]
    print(f'\n=== {filename} ===')

    imported = 0
    skipped = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')

        batch = []
        for row in reader:
            # Parse date (DD.MM.YYYY HH:MM:SS)
            date_str = row['date'].strip('"')
            try:
                call_start = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
            except:
                skipped += 1
                continue

            external_id = f"csv_{row['call_id']}_{call_start.strftime('%Y%m%d%H%M%S')}"

            raw_data = dict(row)
            raw_data['source'] = 'csv_import'

            batch.append((
                provider_id,
                external_id,
                row['clid'],
                row['destination'],
                'outbound',
                call_start,
                int(row['billseconds']) if row['billseconds'] else 0,
                int(row['billseconds']) if row['billseconds'] else 0,
                row['disposition'],
                row['disposition'],
                float(row['billcost']) if row['billcost'] else 0,
                row['currency'],
                False,
                Json(raw_data)
            ))

            # Batch insert every 100 rows
            if len(batch) >= 100:
                imported += insert_batch(conn, batch)
                batch = []

        # Insert remaining
        if batch:
            imported += insert_batch(conn, batch)

    print(f'  Imported: {imported}')
    return imported

def insert_batch(conn, batch):
    """Insert a batch of records"""
    inserted = 0
    with conn.cursor() as cur:
        for record in batch:
            try:
                cur.execute("""
                    INSERT INTO telco.calls
                    (provider_id, external_call_id, from_number, to_number, direction,
                     started_at, duration_seconds, billable_seconds, status, disposition,
                     cost, currency, has_recording, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (provider_id, external_call_id) DO NOTHING
                """, record)
                if cur.rowcount > 0:
                    inserted += 1
            except Exception as e:
                print(f'  Error: {e}')
    conn.commit()
    return inserted

def main():
    print('=== Zadarma CSV Import ===')

    conn = psycopg2.connect(**DB_CONFIG)
    print('Connected to database')

    total = 0
    for csv_file in CSV_FILES:
        total += import_csv(conn, csv_file)

    print(f'\n=== TOTAL IMPORTED: {total:,} calls ===')

    # Summary
    print('\n=== Zadarma Calls by Month ===')
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                DATE_TRUNC('month', started_at) as month,
                COUNT(*) as calls,
                SUM(duration_seconds) as seconds,
                SUM(cost) as cost
            FROM telco.calls
            WHERE provider_id = 1
            GROUP BY DATE_TRUNC('month', started_at)
            ORDER BY month
        """)
        for row in cur.fetchall():
            month = row[0].strftime('%Y-%m') if row[0] else '?'
            print(f'  {month}: {row[1]:,} calls, {row[2]//60 if row[2] else 0:,} min, ${row[3]:.2f}' if row[3] else f'  {month}: {row[1]:,} calls')

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM telco.calls WHERE provider_id = 1")
        print(f'\nTotal Zadarma calls: {cur.fetchone()[0]:,}')

    conn.close()

if __name__ == '__main__':
    main()
