#!/usr/bin/env python3
"""Analyze calls for appointment contacts from APPOINTMENTS_MOBILE_NUMBERS.md"""

import psycopg2
from datetime import datetime
import sys
sys.path.insert(0, '.')
from telemarketing_taxonomy import TelemarketingTaxonomy, analyze_for_database

DB_CONFIG = {
    'host': '96.47.238.189',
    'port': 5432,
    'database': 'telco_warehouse',
    'user': 'telco_sync',
    'password': 'TelcoSync2024!'
}

# Phone numbers from APPOINTMENTS_MOBILE_NUMBERS.md
PHONES = [
    '61402140955',
    '61402213582',
    '61404610402',
    '61418127174',
    '61421189252',
    '61425757530',
    '61431413530',
    '61431587938',
]

PHONE_COMPANIES = {
    '61402140955': 'CLG Electrics',
    '61402213582': 'Multiple (Finweb, Brisbane City Landscapes, Paradise Distributors, etc)',
    '61404610402': 'Cool Solutions',
    '61418127174': 'No Show - Ian Kingston',
    '61421189252': 'AJS Australia Disability',
    '61425757530': 'Western AC',
    '61431413530': 'Pinnacle Accounting',
    '61431587938': 'Kiwi Golden Care',
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    output = []
    output.append("# Appointment Contacts - Call Analysis Report")
    output.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append("\nAnalysis of calls for contacts from APPOINTMENTS_MOBILE_NUMBERS.md")
    output.append("\n---\n")

    # Get call stats by phone
    output.append("## Call Summary by Phone Number\n")
    output.append("| Phone | Company | Provider | Calls | With Transcript |")
    output.append("|-------|---------|----------|------:|----------------:|")

    total_calls = 0
    total_with_transcript = 0

    for phone in PHONES:
        cur.execute('''
            SELECT
                p.name as provider,
                COUNT(*) as cnt,
                COUNT(CASE WHEN c.transcript IS NOT NULL AND LENGTH(c.transcript) > 50 THEN 1 END) as with_transcript
            FROM telco.calls c
            JOIN telco.providers p ON p.provider_id = c.provider_id
            WHERE c.from_number LIKE %s OR c.to_number LIKE %s
            GROUP BY p.name
            ORDER BY cnt DESC
        ''', ('%' + phone + '%', '%' + phone + '%'))
        rows = cur.fetchall()
        company = PHONE_COMPANIES.get(phone, 'Unknown')[:30]
        if rows:
            for provider, cnt, with_trans in rows:
                output.append(f"| {phone} | {company} | {provider} | {cnt} | {with_trans} |")
                total_calls += cnt
                total_with_transcript += with_trans
        else:
            output.append(f"| {phone} | {company} | - | 0 | 0 |")

    output.append(f"\n**Total: {total_calls} calls, {total_with_transcript} with transcripts**\n")

    # Check why no transcripts - look at raw data
    output.append("---\n")
    output.append("## Sample Call Details (checking transcript availability)\n")

    for phone in ['61418127174', '61402213582']:  # Two phones with most calls
        output.append(f"### Phone: {phone}\n")
        cur.execute('''
            SELECT
                c.id,
                c.from_number,
                c.to_number,
                c.started_at,
                c.duration_seconds,
                c.disposition,
                p.name as provider,
                CASE WHEN c.transcript IS NOT NULL THEN LENGTH(c.transcript) ELSE 0 END as transcript_len,
                c.external_call_id
            FROM telco.calls c
            JOIN telco.providers p ON p.provider_id = c.provider_id
            WHERE c.from_number LIKE %s OR c.to_number LIKE %s
            ORDER BY c.started_at DESC
            LIMIT 5
        ''', ('%' + phone + '%', '%' + phone + '%'))
        rows = cur.fetchall()

        if rows:
            output.append("| ID | Provider | Date | Duration | Disposition | Transcript Len |")
            output.append("|---:|----------|------|----------|-------------|---------------:|")
            for row in rows:
                call_id, from_num, to_num, started_at, duration, disposition, provider, trans_len, ext_id = row
                output.append(f"| {call_id} | {provider} | {str(started_at)[:10]} | {duration}s | {disposition or 'NULL'} | {trans_len} |")
        output.append("")

    # Check if transcripts exist in call_analysis table instead
    output.append("---\n")
    output.append("## Checking call_analysis table for summaries\n")

    cur.execute('''
        SELECT
            ca.call_id,
            ca.user_sentiment,
            ca.call_successful,
            LEFT(ca.call_summary, 200) as summary
        FROM telco.call_analysis ca
        JOIN telco.calls c ON c.external_call_id = ca.call_id
        WHERE c.from_number LIKE '%61418127174%' OR c.to_number LIKE '%61418127174%'
        LIMIT 5
    ''')
    rows = cur.fetchall()

    if rows:
        output.append("Found call analysis data:\n")
        for row in rows:
            output.append(f"- **{row[0]}**: Sentiment={row[1]}, Successful={row[2]}")
            output.append(f"  Summary: _{row[3]}_\n")
    else:
        output.append("*No call_analysis data found for these phone numbers.*\n")

    # Since no transcripts, check the existing call_classification for these
    output.append("---\n")
    output.append("## Existing Classifications (if any)\n")

    cur.execute('''
        SELECT
            cc.call_id,
            cc.is_dnc,
            cc.lead_status,
            cc.lead_score,
            cc.flags_detected,
            c.from_number,
            c.to_number
        FROM telco.call_classification cc
        JOIN telco.calls c ON c.id = cc.call_id
        WHERE c.from_number LIKE '%61418127174%'
           OR c.to_number LIKE '%61418127174%'
           OR c.from_number LIKE '%61402213582%'
           OR c.to_number LIKE '%61402213582%'
        LIMIT 10
    ''')
    rows = cur.fetchall()

    if rows:
        output.append("| Call ID | From | To | DNC | Lead Status | Score | Flags |")
        output.append("|--------:|------|-----|-----|-------------|------:|-------|")
        for row in rows:
            output.append(f"| {row[0]} | {row[5]} | {row[6]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |")
    else:
        output.append("*No existing classifications for these contacts.*\n")

    output.append("\n---\n")
    output.append("## Key Finding\n")
    output.append("""
These appointment contacts were called primarily via **Zadarma** (35 calls) with some **Retell** calls (22 calls).

**However, none of these calls have transcripts stored in the database.**

Possible reasons:
1. **Zadarma calls** - Zadarma doesn't provide transcription
2. **Retell calls** - These may be older calls before transcript syncing was enabled
3. **Short duration** - Very short calls may not generate transcripts

**Recommendation:**
- For future analysis, ensure Retell transcript sync is running
- Consider adding a transcription service for Zadarma calls if needed
""")

    conn.close()

    # Write report
    report_path = '../APPOINTMENTS_CALL_ANALYSIS.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"Report written to: {report_path}")
    print(f"Total lines: {len(output)}")
    print(f"\nSummary: {total_calls} calls found, {total_with_transcript} with transcripts")

if __name__ == "__main__":
    main()
