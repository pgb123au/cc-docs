#!/usr/bin/env python3
"""Export analysis results to markdown for review."""

import psycopg2
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

    output = []
    output.append("# Transcript Classification Analysis Results")
    output.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append("\n---\n")

    # Overall stats
    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE is_dnc = TRUE) as dnc_count,
            COUNT(*) FILTER (WHERE lead_score = 100) as hot_leads,
            COUNT(*) FILTER (WHERE lead_score >= 80 AND lead_score < 100) as warm_leads,
            COUNT(*) FILTER (WHERE contact_status = 'invalid') as invalid,
            COUNT(*) FILTER (WHERE contact_status = 'retired') as retired,
            COUNT(*) FILTER (WHERE contact_status = 'deceased') as deceased,
            COUNT(*) FILTER (WHERE contact_status = 'closed') as closed,
            COUNT(*) FILTER (WHERE hostile = TRUE) as hostile,
            COUNT(*) FILTER (WHERE callback_requested = TRUE) as callbacks,
            COUNT(*) FILTER (WHERE voicemail_full = TRUE) as voicemail_full
        FROM telco.call_classification
    """)
    stats = cur.fetchone()

    output.append("## Summary Statistics\n")
    output.append("| Metric | Count |")
    output.append("|--------|------:|")
    output.append(f"| **Total Analyzed** | {stats[0]} |")
    output.append(f"| DNC Flagged | {stats[1]} |")
    output.append(f"| Hot Leads (score=100) | {stats[2]} |")
    output.append(f"| Warm Leads (score 80-99) | {stats[3]} |")
    output.append(f"| Invalid/Wrong Number | {stats[4]} |")
    output.append(f"| Retired | {stats[5]} |")
    output.append(f"| Deceased | {stats[6]} |")
    output.append(f"| Business Closed | {stats[7]} |")
    output.append(f"| Hostile Interactions | {stats[8]} |")
    output.append(f"| Callback Requested | {stats[9]} |")
    output.append(f"| Voicemail Full | {stats[10]} |")

    # Lead score distribution
    cur.execute("""
        SELECT lead_status, COUNT(*) as cnt
        FROM telco.call_classification
        GROUP BY lead_status
        ORDER BY cnt DESC
    """)
    lead_dist = cur.fetchall()
    output.append("\n### Lead Status Distribution\n")
    output.append("| Status | Count |")
    output.append("|--------|------:|")
    for row in lead_dist:
        output.append(f"| {row[0] or 'NULL'} | {row[1]} |")

    output.append("\n---\n")

    # DNC Flagged - Full Details
    output.append("## DNC Flagged Calls (Full Details)\n")
    cur.execute("""
        SELECT
            cc.call_id,
            cc.dnc_reason,
            cc.contact_status,
            cc.lead_score,
            cc.hostile,
            cc.flags_detected,
            cc.retell_sentiment,
            cc.retell_summary,
            c.from_number,
            c.to_number,
            c.started_at,
            c.duration_seconds,
            c.transcript
        FROM telco.call_classification cc
        JOIN telco.calls c ON c.id = cc.call_id
        WHERE cc.is_dnc = TRUE
        ORDER BY cc.analyzed_at DESC
    """)
    dnc_calls = cur.fetchall()

    if not dnc_calls:
        output.append("*No DNC flagged calls found.*\n")
    else:
        for i, call in enumerate(dnc_calls, 1):
            output.append(f"### DNC Call #{i}\n")
            output.append(f"- **Call ID:** {call[0]}")
            output.append(f"- **DNC Reason:** `{call[1]}`")
            output.append(f"- **Contact Status:** {call[2]}")
            output.append(f"- **Lead Score:** {call[3]}")
            output.append(f"- **Hostile:** {call[4]}")
            output.append(f"- **Flags Detected:** `{call[5]}`")
            output.append(f"- **Retell Sentiment:** {call[6]}")
            output.append(f"- **From:** `{call[8]}`")
            output.append(f"- **To:** `{call[9]}`")
            output.append(f"- **Date:** {call[10]}")
            output.append(f"- **Duration:** {call[11]} seconds")
            output.append(f"\n**Retell Summary:**\n> {call[7] or 'N/A'}\n")
            transcript = call[12] or "No transcript"
            output.append(f"**Full Transcript:**\n```\n{transcript[:2000]}{'...(truncated)' if len(transcript) > 2000 else ''}\n```\n")

    output.append("---\n")

    # Hot Leads - Sample with Details
    output.append("## Hot Leads (Score = 100) - Sample\n")
    cur.execute("""
        SELECT
            cc.call_id,
            cc.lead_status,
            cc.lead_score,
            cc.callback_requested,
            cc.flags_detected,
            cc.retell_sentiment,
            cc.retell_summary,
            c.from_number,
            c.to_number,
            c.started_at,
            c.duration_seconds,
            c.transcript
        FROM telco.call_classification cc
        JOIN telco.calls c ON c.id = cc.call_id
        WHERE cc.lead_score = 100
        ORDER BY c.duration_seconds DESC
        LIMIT 5
    """)
    hot_leads = cur.fetchall()

    for i, lead in enumerate(hot_leads, 1):
        output.append(f"### Hot Lead #{i}\n")
        output.append(f"- **Call ID:** {lead[0]}")
        output.append(f"- **Lead Status:** {lead[1]}")
        output.append(f"- **Lead Score:** {lead[2]}")
        output.append(f"- **Callback Requested:** {lead[3]}")
        output.append(f"- **Flags Detected:** `{lead[4]}`")
        output.append(f"- **Retell Sentiment:** {lead[5]}")
        output.append(f"- **From:** `{lead[7]}`")
        output.append(f"- **To:** `{lead[8]}`")
        output.append(f"- **Date:** {lead[9]}")
        output.append(f"- **Duration:** {lead[10]} seconds")
        output.append(f"\n**Retell Summary:**\n> {lead[6] or 'N/A'}\n")
        transcript = lead[11] or "No transcript"
        output.append(f"**Transcript (first 1500 chars):**\n```\n{transcript[:1500]}{'...' if len(transcript) > 1500 else ''}\n```\n")

    output.append("---\n")

    # Invalid/Wrong Numbers
    output.append("## Invalid/Wrong Number Calls\n")
    cur.execute("""
        SELECT
            cc.call_id,
            cc.contact_status,
            cc.lead_status,
            cc.lead_score,
            cc.flags_detected,
            cc.retell_sentiment,
            cc.retell_summary,
            c.from_number,
            c.to_number,
            c.started_at,
            c.duration_seconds,
            c.transcript
        FROM telco.call_classification cc
        JOIN telco.calls c ON c.id = cc.call_id
        WHERE cc.contact_status = 'invalid'
        ORDER BY cc.analyzed_at DESC
    """)
    invalid_calls = cur.fetchall()

    if not invalid_calls:
        output.append("*No invalid/wrong number calls found.*\n")
    else:
        for i, call in enumerate(invalid_calls, 1):
            output.append(f"### Invalid #{i}\n")
            output.append(f"- **Call ID:** {call[0]}")
            output.append(f"- **Contact Status:** {call[1]}")
            output.append(f"- **Lead Score:** {call[3]}")
            output.append(f"- **Flags Detected:** `{call[4]}`")
            output.append(f"- **From:** `{call[7]}`")
            output.append(f"- **To:** `{call[8]}`")
            output.append(f"- **Date:** {call[9]}")
            output.append(f"- **Duration:** {call[10]} seconds")
            output.append(f"\n**Retell Summary:**\n> {call[6] or 'N/A'}\n")
            transcript = call[11] or "No transcript"
            output.append(f"**Full Transcript:**\n```\n{transcript[:2000]}{'...(truncated)' if len(transcript) > 2000 else ''}\n```\n")

    output.append("---\n")

    # Hostile Interactions
    output.append("## Hostile Interactions\n")
    cur.execute("""
        SELECT
            cc.call_id,
            cc.is_dnc,
            cc.dnc_reason,
            cc.flags_detected,
            cc.retell_sentiment,
            cc.retell_summary,
            c.from_number,
            c.to_number,
            c.started_at,
            c.duration_seconds,
            c.transcript
        FROM telco.call_classification cc
        JOIN telco.calls c ON c.id = cc.call_id
        WHERE cc.hostile = TRUE
        ORDER BY cc.analyzed_at DESC
        LIMIT 5
    """)
    hostile_calls = cur.fetchall()

    if not hostile_calls:
        output.append("*No hostile interactions found.*\n")
    else:
        for i, call in enumerate(hostile_calls, 1):
            output.append(f"### Hostile Call #{i}\n")
            output.append(f"- **Call ID:** {call[0]}")
            output.append(f"- **Flagged DNC:** {call[1]} (reason: {call[2]})")
            output.append(f"- **Flags Detected:** `{call[3]}`")
            output.append(f"- **Retell Sentiment:** {call[4]}")
            output.append(f"- **From:** `{call[6]}`")
            output.append(f"- **To:** `{call[7]}`")
            output.append(f"- **Date:** {call[8]}")
            output.append(f"- **Duration:** {call[9]} seconds")
            output.append(f"\n**Retell Summary:**\n> {call[5] or 'N/A'}\n")
            transcript = call[10] or "No transcript"
            output.append(f"**Full Transcript:**\n```\n{transcript[:2000]}{'...(truncated)' if len(transcript) > 2000 else ''}\n```\n")

    output.append("---\n")

    # Callback Requests - Sample
    output.append("## Callback Requests - Sample\n")
    cur.execute("""
        SELECT
            cc.call_id,
            cc.lead_status,
            cc.lead_score,
            cc.flags_detected,
            cc.retell_sentiment,
            cc.retell_summary,
            c.from_number,
            c.to_number,
            c.started_at,
            c.duration_seconds
        FROM telco.call_classification cc
        JOIN telco.calls c ON c.id = cc.call_id
        WHERE cc.callback_requested = TRUE
        ORDER BY c.started_at DESC
        LIMIT 10
    """)
    callbacks = cur.fetchall()

    output.append("| Call ID | From | Date | Duration | Lead Score | Flags | Summary |")
    output.append("|---------|------|------|----------|------------|-------|---------|")
    for cb in callbacks:
        summary = (cb[5] or "N/A")[:80] + "..." if cb[5] and len(cb[5]) > 80 else (cb[5] or "N/A")
        flags = str(cb[3])[:40] if cb[3] else "None"
        output.append(f"| {cb[0]} | `{cb[6]}` | {str(cb[8])[:10]} | {cb[9]}s | {cb[2]} | {flags} | {summary} |")

    output.append("\n---\n")

    # Representative samples of different flag types
    output.append("## Representative Samples by Flag Type\n")

    flag_types = [
        ('RETIRED', 'Retired Contacts'),
        ('DECEASED', 'Deceased Contacts'),
        ('OUT_OF_BUSINESS', 'Business Closed'),
        ('VOICEMAIL_GENERIC', 'Voicemail Detected'),
        ('SALE_CLOSED', 'Sales Closed'),
        ('HARD_OBJECTION', 'Hard Objections'),
        ('SOFT_OBJECTION_CALLBACK', 'Soft Objections/Callbacks'),
        ('SENTIMENT_POSITIVE', 'Positive Sentiment'),
        ('SENTIMENT_ANGRY', 'Angry Sentiment'),
    ]

    for flag, title in flag_types:
        cur.execute("""
            SELECT
                cc.call_id,
                cc.lead_score,
                cc.contact_status,
                cc.flags_detected,
                cc.retell_summary,
                c.from_number,
                c.started_at,
                c.duration_seconds,
                LEFT(c.transcript, 500) as transcript_preview
            FROM telco.call_classification cc
            JOIN telco.calls c ON c.id = cc.call_id
            WHERE %s = ANY(cc.flags_detected)
            ORDER BY c.started_at DESC
            LIMIT 2
        """, (flag,))
        samples = cur.fetchall()

        if samples:
            output.append(f"### {title} (`{flag}`)\n")
            for j, s in enumerate(samples, 1):
                output.append(f"**Sample {j}:**")
                output.append(f"- Call ID: {s[0]} | Score: {s[1]} | Status: {s[2]}")
                output.append(f"- From: `{s[5]}` | Date: {str(s[6])[:10]} | Duration: {s[7]}s")
                output.append(f"- All flags: `{s[3]}`")
                output.append(f"- Summary: {s[4] or 'N/A'}")
                output.append(f"- Transcript preview: _{s[8][:200] if s[8] else 'None'}_\n")

    output.append("---\n")
    output.append("## Notes\n")
    output.append("- Analysis performed using regex-based taxonomy classification")
    output.append("- ~26,000 transcripts remaining to be analyzed")
    output.append("- Run `python analyze_transcripts.py` to complete full analysis")

    conn.close()

    # Write to file
    with open('ANALYSIS_RESULTS_REVIEW.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"Results exported to ANALYSIS_RESULTS_REVIEW.md")
    print(f"Total lines: {len(output)}")

if __name__ == "__main__":
    main()
