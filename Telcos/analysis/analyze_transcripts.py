#!/usr/bin/env python3
"""
Analyze Retell call transcripts using the Telemarketing Taxonomy.

This script:
1. Fetches transcripts from telco.calls (Retell provider)
2. Applies regex-based classification from telemarketing_taxonomy.py
3. Stores results in telco.call_analysis
4. Updates telco.contacts with aggregated DNC/status flags

Usage:
    python analyze_transcripts.py                    # Analyze all unanalyzed calls
    python analyze_transcripts.py --limit 100       # Analyze first 100 unanalyzed
    python analyze_transcripts.py --reanalyze       # Re-analyze all calls
    python analyze_transcripts.py --stats           # Show analysis statistics
    python analyze_transcripts.py --test            # Test with sample transcripts
"""

import argparse
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

import psycopg2
from psycopg2.extras import execute_values, Json

# Import our taxonomy library
from telemarketing_taxonomy import TelemarketingTaxonomy, analyze_for_database


DB_CONFIG = {
    'host': '96.47.238.189',
    'port': 5432,
    'database': 'telco_warehouse',
    'user': 'telco_sync',
    'password': 'TelcoSync2024!'
}

RETELL_PROVIDER_ID = 3


def get_connection():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG)


def ensure_schema(conn):
    """Create the call_classification table if it doesn't exist.

    Note: telco.call_analysis already exists with Retell's own analysis data.
    We create call_classification for our taxonomy-based classification.
    """
    with conn.cursor() as cur:
        # Create call_classification table (separate from Retell's call_analysis)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS telco.call_classification (
                id                  SERIAL PRIMARY KEY,
                call_id             INTEGER UNIQUE,  -- References telco.calls(id)

                -- DNC Flags
                is_dnc              BOOLEAN DEFAULT FALSE,
                dnc_reason          VARCHAR(50),

                -- Contact Status
                contact_status      VARCHAR(30) DEFAULT 'active',

                -- Lead Info
                lead_status         VARCHAR(30),
                lead_score          SMALLINT,
                callback_requested  BOOLEAN DEFAULT FALSE,

                -- Cached from Retell's call_analysis table
                retell_sentiment    VARCHAR(20),
                retell_summary      TEXT,
                retell_successful   BOOLEAN,
                retell_voicemail    BOOLEAN,

                -- Flags
                hostile             BOOLEAN DEFAULT FALSE,
                voicemail_full      BOOLEAN DEFAULT FALSE,
                requires_escalation BOOLEAN DEFAULT FALSE,

                -- Raw analysis
                flags_detected      TEXT[],

                -- Metadata
                analysis_method     VARCHAR(20) DEFAULT 'taxonomy_regex',
                analyzed_at         TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        conn.commit()  # Commit table creation first

        # Try to create indexes (may fail if not owner, that's OK)
        try:
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_call_classification_dnc
                    ON telco.call_classification(is_dnc) WHERE is_dnc = TRUE;
                CREATE INDEX IF NOT EXISTS idx_call_classification_lead
                    ON telco.call_classification(lead_status);
                CREATE INDEX IF NOT EXISTS idx_call_classification_status
                    ON telco.call_classification(contact_status);
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()  # Rollback failed index creation
            print(f"  [WARN] Could not create indexes (permission issue, continuing anyway)")

        # Add columns to contacts table if they don't exist
        cur.execute("""
            DO $$
            BEGIN
                -- Add is_dnc column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'telco' AND table_name = 'contacts' AND column_name = 'is_dnc') THEN
                    ALTER TABLE telco.contacts ADD COLUMN is_dnc BOOLEAN DEFAULT FALSE;
                END IF;

                -- Add dnc_reason column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'telco' AND table_name = 'contacts' AND column_name = 'dnc_reason') THEN
                    ALTER TABLE telco.contacts ADD COLUMN dnc_reason VARCHAR(50);
                END IF;

                -- Add contact_status column (may already exist with different default)
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'telco' AND table_name = 'contacts' AND column_name = 'contact_status') THEN
                    ALTER TABLE telco.contacts ADD COLUMN contact_status VARCHAR(30) DEFAULT 'active';
                END IF;

                -- Add lead_score column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'telco' AND table_name = 'contacts' AND column_name = 'lead_score') THEN
                    ALTER TABLE telco.contacts ADD COLUMN lead_score SMALLINT;
                END IF;

                -- Add hostile_interactions column
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'telco' AND table_name = 'contacts' AND column_name = 'hostile_interactions') THEN
                    ALTER TABLE telco.contacts ADD COLUMN hostile_interactions INTEGER DEFAULT 0;
                END IF;
            END $$;
        """)

        conn.commit()
        print("[OK] Schema verified/created")


def get_unanalyzed_calls(conn, limit: Optional[int] = None) -> List[Dict]:
    """Get Retell calls that haven't been classified yet."""
    with conn.cursor() as cur:
        limit_clause = f"LIMIT {limit}" if limit else ""
        # Join with existing call_analysis to get Retell's own sentiment/summary
        cur.execute(f"""
            SELECT
                c.id,
                c.transcript,
                ca.call_summary,
                ca.user_sentiment as sentiment,
                ca.call_successful as successful,
                ca.in_voicemail as voicemail,
                c.from_number,
                c.to_number,
                c.direction,
                c.duration_seconds
            FROM telco.calls c
            LEFT JOIN telco.call_analysis ca ON c.external_call_id = ca.call_id
            LEFT JOIN telco.call_classification cc ON c.id = cc.call_id
            WHERE c.provider_id = {RETELL_PROVIDER_ID}
            AND cc.id IS NULL
            AND (c.transcript IS NOT NULL AND c.transcript != '')
            ORDER BY c.started_at DESC
            {limit_clause}
        """)

        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def get_all_retell_calls(conn, limit: Optional[int] = None) -> List[Dict]:
    """Get all Retell calls with transcripts."""
    with conn.cursor() as cur:
        limit_clause = f"LIMIT {limit}" if limit else ""
        # Join with existing call_analysis to get Retell's own sentiment/summary
        cur.execute(f"""
            SELECT
                c.id,
                c.transcript,
                ca.call_summary,
                ca.user_sentiment as sentiment,
                ca.call_successful as successful,
                ca.in_voicemail as voicemail,
                c.from_number,
                c.to_number,
                c.direction,
                c.duration_seconds
            FROM telco.calls c
            LEFT JOIN telco.call_analysis ca ON c.external_call_id = ca.call_id
            WHERE c.provider_id = {RETELL_PROVIDER_ID}
            AND (c.transcript IS NOT NULL AND c.transcript != '')
            ORDER BY c.started_at DESC
            {limit_clause}
        """)

        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def analyze_call(call: Dict) -> Dict[str, Any]:
    """Analyze a single call and return database-ready values."""
    # Use the taxonomy library
    result = analyze_for_database(
        transcript=call.get('transcript'),
        call_summary=call.get('call_summary')
    )

    # Add Retell's own analysis
    result['retell_sentiment'] = call.get('sentiment')
    result['retell_summary'] = call.get('call_summary')
    result['retell_successful'] = call.get('successful') == 'true'
    result['retell_voicemail'] = call.get('voicemail') == 'true'

    return result


def insert_analysis(conn, call_id: int, analysis: Dict) -> bool:
    """Insert classification results into database."""
    with conn.cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO telco.call_classification (
                    call_id, is_dnc, dnc_reason, contact_status,
                    lead_status, lead_score, callback_requested,
                    retell_sentiment, retell_summary, retell_successful, retell_voicemail,
                    hostile, voicemail_full, requires_escalation,
                    flags_detected, analysis_method, analyzed_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
                ON CONFLICT (call_id) DO UPDATE SET
                    is_dnc = EXCLUDED.is_dnc,
                    dnc_reason = EXCLUDED.dnc_reason,
                    contact_status = EXCLUDED.contact_status,
                    lead_status = EXCLUDED.lead_status,
                    lead_score = EXCLUDED.lead_score,
                    callback_requested = EXCLUDED.callback_requested,
                    retell_sentiment = EXCLUDED.retell_sentiment,
                    retell_summary = EXCLUDED.retell_summary,
                    retell_successful = EXCLUDED.retell_successful,
                    retell_voicemail = EXCLUDED.retell_voicemail,
                    hostile = EXCLUDED.hostile,
                    voicemail_full = EXCLUDED.voicemail_full,
                    requires_escalation = EXCLUDED.requires_escalation,
                    flags_detected = EXCLUDED.flags_detected,
                    analysis_method = EXCLUDED.analysis_method,
                    analyzed_at = NOW()
            """, (
                call_id,
                analysis['is_dnc'],
                analysis['dnc_reason'],
                analysis['contact_status'],
                analysis['lead_status'],
                analysis['lead_score'],
                analysis['callback_requested'],
                analysis['retell_sentiment'],
                analysis['retell_summary'],
                analysis['retell_successful'],
                analysis['retell_voicemail'],
                analysis['hostile'],
                analysis['voicemail_full'],
                analysis['requires_escalation'],
                analysis['flags_detected'],
                analysis['analysis_method']
            ))
            return True
        except Exception as e:
            print(f"  [ERROR] Call {call_id}: {e}")
            return False


def analyze_batch(conn, calls: List[Dict], batch_size: int = 100) -> Dict[str, int]:
    """Analyze a batch of calls."""
    stats = {
        'total': len(calls),
        'analyzed': 0,
        'dnc': 0,
        'retired': 0,
        'deceased': 0,
        'wrong_number': 0,
        'hot_leads': 0,
        'callbacks': 0,
        'hostile': 0,
        'errors': 0
    }

    for i, call in enumerate(calls):
        try:
            analysis = analyze_call(call)
            success = insert_analysis(conn, call['id'], analysis)

            if success:
                stats['analyzed'] += 1

                # Track stats
                if analysis['is_dnc']:
                    stats['dnc'] += 1
                if analysis['contact_status'] == 'retired':
                    stats['retired'] += 1
                if analysis['contact_status'] == 'deceased':
                    stats['deceased'] += 1
                if analysis['contact_status'] == 'invalid':
                    stats['wrong_number'] += 1
                if analysis['lead_status'] == 'hot':
                    stats['hot_leads'] += 1
                if analysis['callback_requested']:
                    stats['callbacks'] += 1
                if analysis['hostile']:
                    stats['hostile'] += 1
            else:
                stats['errors'] += 1

            # Commit in batches
            if (i + 1) % batch_size == 0:
                conn.commit()
                print(f"  Processed {i + 1}/{len(calls)}...")

        except Exception as e:
            print(f"  [ERROR] Call {call['id']}: {e}")
            stats['errors'] += 1

    conn.commit()
    return stats


def aggregate_to_contacts(conn):
    """Update contacts table with aggregated classification from all their calls."""
    print("\n=== Aggregating to Contacts ===")

    with conn.cursor() as cur:
        # Update DNC status - if ANY call is DNC, contact is DNC
        cur.execute("""
            UPDATE telco.contacts con
            SET
                is_dnc = TRUE,
                dnc_reason = sub.dnc_reason,
                updated_at = NOW()
            FROM (
                SELECT DISTINCT ON (phone)
                    COALESCE(
                        telco.normalize_phone(c.from_number),
                        telco.normalize_phone(c.to_number)
                    ) as phone,
                    cc.dnc_reason
                FROM telco.call_classification cc
                JOIN telco.calls c ON cc.call_id = c.id
                WHERE cc.is_dnc = TRUE
                ORDER BY phone, cc.analyzed_at DESC
            ) sub
            WHERE con.phone_normalized = sub.phone
            AND (con.is_dnc IS NULL OR con.is_dnc = FALSE)
        """)
        dnc_updated = cur.rowcount
        print(f"  DNC contacts updated: {dnc_updated}")

        # Update contact status - worst status from any call
        # Priority: deceased > closed > retired > invalid > vulnerable > left_company > active
        cur.execute("""
            UPDATE telco.contacts con
            SET
                contact_status = sub.worst_status,
                updated_at = NOW()
            FROM (
                SELECT
                    phone,
                    CASE
                        WHEN 'deceased' = ANY(statuses) THEN 'deceased'
                        WHEN 'closed' = ANY(statuses) THEN 'closed'
                        WHEN 'retired' = ANY(statuses) THEN 'retired'
                        WHEN 'invalid' = ANY(statuses) THEN 'invalid'
                        WHEN 'vulnerable' = ANY(statuses) THEN 'vulnerable'
                        WHEN 'left_company' = ANY(statuses) THEN 'left_company'
                        ELSE 'active'
                    END as worst_status
                FROM (
                    SELECT
                        COALESCE(
                            telco.normalize_phone(c.from_number),
                            telco.normalize_phone(c.to_number)
                        ) as phone,
                        ARRAY_AGG(DISTINCT cc.contact_status) as statuses
                    FROM telco.call_classification cc
                    JOIN telco.calls c ON cc.call_id = c.id
                    WHERE cc.contact_status IS NOT NULL
                    GROUP BY COALESCE(
                        telco.normalize_phone(c.from_number),
                        telco.normalize_phone(c.to_number)
                    )
                ) grouped
            ) sub
            WHERE con.phone_normalized = sub.phone
        """)
        status_updated = cur.rowcount
        print(f"  Contact statuses updated: {status_updated}")

        # Update lead score - use most recent call's score
        cur.execute("""
            UPDATE telco.contacts con
            SET
                lead_score = sub.latest_score,
                updated_at = NOW()
            FROM (
                SELECT DISTINCT ON (phone)
                    COALESCE(
                        telco.normalize_phone(c.from_number),
                        telco.normalize_phone(c.to_number)
                    ) as phone,
                    cc.lead_score as latest_score
                FROM telco.call_classification cc
                JOIN telco.calls c ON cc.call_id = c.id
                WHERE cc.lead_score IS NOT NULL
                ORDER BY phone, c.started_at DESC
            ) sub
            WHERE con.phone_normalized = sub.phone
        """)
        score_updated = cur.rowcount
        print(f"  Lead scores updated: {score_updated}")

        # Count hostile interactions
        cur.execute("""
            UPDATE telco.contacts con
            SET
                hostile_interactions = sub.hostile_count,
                updated_at = NOW()
            FROM (
                SELECT
                    COALESCE(
                        telco.normalize_phone(c.from_number),
                        telco.normalize_phone(c.to_number)
                    ) as phone,
                    COUNT(*) as hostile_count
                FROM telco.call_classification cc
                JOIN telco.calls c ON cc.call_id = c.id
                WHERE cc.hostile = TRUE
                GROUP BY COALESCE(
                    telco.normalize_phone(c.from_number),
                    telco.normalize_phone(c.to_number)
                )
            ) sub
            WHERE con.phone_normalized = sub.phone
        """)
        hostile_updated = cur.rowcount
        print(f"  Hostile interaction counts updated: {hostile_updated}")

        conn.commit()

    return {
        'dnc_updated': dnc_updated,
        'status_updated': status_updated,
        'score_updated': score_updated,
        'hostile_updated': hostile_updated
    }


def show_stats(conn):
    """Show classification statistics."""
    print("\n" + "=" * 60)
    print("TRANSCRIPT CLASSIFICATION STATISTICS")
    print("=" * 60)

    with conn.cursor() as cur:
        # Overall counts
        cur.execute("""
            SELECT
                COUNT(*) as total_calls,
                COUNT(*) FILTER (WHERE transcript IS NOT NULL AND transcript != '') as with_transcript
            FROM telco.calls WHERE provider_id = %s
        """, (RETELL_PROVIDER_ID,))
        row = cur.fetchone()
        print(f"\nRetell Calls: {row[0]:,} total, {row[1]:,} with transcripts")

        cur.execute("SELECT COUNT(*) FROM telco.call_classification")
        analyzed = cur.fetchone()[0]
        print(f"Classified: {analyzed:,}")

        # Analysis breakdown
        print("\n--- Classification Results ---")

        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE is_dnc = TRUE) as dnc,
                COUNT(*) FILTER (WHERE contact_status = 'retired') as retired,
                COUNT(*) FILTER (WHERE contact_status = 'deceased') as deceased,
                COUNT(*) FILTER (WHERE contact_status = 'closed') as closed,
                COUNT(*) FILTER (WHERE contact_status = 'invalid') as invalid,
                COUNT(*) FILTER (WHERE hostile = TRUE) as hostile,
                COUNT(*) FILTER (WHERE callback_requested = TRUE) as callback,
                COUNT(*) FILTER (WHERE voicemail_full = TRUE) as vm_full,
                COUNT(*) FILTER (WHERE lead_status = 'hot') as hot,
                COUNT(*) FILTER (WHERE lead_status = 'warm') as warm,
                COUNT(*) FILTER (WHERE lead_status = 'lost') as lost
            FROM telco.call_classification
        """)
        row = cur.fetchone()
        print(f"  DNC Flagged:      {row[0]:,}")
        print(f"  Retired:          {row[1]:,}")
        print(f"  Deceased:         {row[2]:,}")
        print(f"  Business Closed:  {row[3]:,}")
        print(f"  Invalid/Wrong:    {row[4]:,}")
        print(f"  Hostile:          {row[5]:,}")
        print(f"  Callback Request: {row[6]:,}")
        print(f"  Voicemail Full:   {row[7]:,}")
        print(f"  Hot Leads:        {row[8]:,}")
        print(f"  Warm Leads:       {row[9]:,}")
        print(f"  Lost:             {row[10]:,}")

        # Lead score distribution
        print("\n--- Lead Score Distribution ---")
        cur.execute("""
            SELECT
                CASE
                    WHEN lead_score = 0 THEN '0 (DNC/Invalid)'
                    WHEN lead_score BETWEEN 1 AND 30 THEN '1-30 (Cold)'
                    WHEN lead_score BETWEEN 31 AND 60 THEN '31-60 (Neutral)'
                    WHEN lead_score BETWEEN 61 AND 80 THEN '61-80 (Warm)'
                    WHEN lead_score BETWEEN 81 AND 100 THEN '81-100 (Hot)'
                END as score_range,
                COUNT(*) as count
            FROM telco.call_classification
            WHERE lead_score IS NOT NULL
            GROUP BY 1
            ORDER BY 1
        """)
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]:,}")

        # Contact aggregation
        print("\n--- Contact Summary ---")
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE is_dnc = TRUE) as dnc_contacts,
                COUNT(*) FILTER (WHERE contact_status = 'retired') as retired_contacts,
                COUNT(*) FILTER (WHERE contact_status = 'deceased') as deceased_contacts,
                COUNT(*) FILTER (WHERE hostile_interactions > 0) as hostile_contacts
            FROM telco.contacts
        """)
        row = cur.fetchone()
        print(f"  DNC Contacts:     {row[0] or 0:,}")
        print(f"  Retired:          {row[1] or 0:,}")
        print(f"  Deceased:         {row[2] or 0:,}")
        print(f"  Hostile History:  {row[3] or 0:,}")

        # Most common flags
        print("\n--- Top 10 Detected Flags ---")
        cur.execute("""
            SELECT unnest(flags_detected) as flag, COUNT(*) as cnt
            FROM telco.call_classification
            WHERE flags_detected IS NOT NULL
            GROUP BY flag
            ORDER BY cnt DESC
            LIMIT 10
        """)
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]:,}")


def test_analysis():
    """Test the analysis with sample transcripts."""
    print("\n" + "=" * 60)
    print("TAXONOMY ANALYSIS TEST")
    print("=" * 60)

    test_cases = [
        ("DNC Request", "Please stop calling me. Remove me from your list. I don't want any more calls."),
        ("Retired", "I'm retired now, I don't work anymore. Not interested in business services."),
        ("Deceased", "I'm sorry, he passed away last month. Please remove this number."),
        ("Business Closed", "The company has closed down. We went out of business in January."),
        ("Wrong Number", "Wrong number mate, there's no Bob here. You have the wrong number."),
        ("Hostile", "Fuck off and stop calling me! This is harassment!"),
        ("Hot Lead", "That sounds great! Let's do it. Sign me up for Tuesday."),
        ("Callback", "I'm busy right now, can you call me back next week?"),
        ("Voicemail Full", "The mailbox is full. No message could be left."),
        ("Not Interested", "No thank you, I'm not interested. We're happy with our current provider."),
    ]

    for name, transcript in test_cases:
        print(f"\n--- {name} ---")
        print(f"Transcript: {transcript[:60]}...")

        result = analyze_for_database(transcript)

        print(f"  DNC: {result['is_dnc']} ({result['dnc_reason']})")
        print(f"  Contact Status: {result['contact_status']}")
        print(f"  Lead: {result['lead_status']} (score: {result['lead_score']})")
        print(f"  Callback: {result['callback_requested']}")
        print(f"  Hostile: {result['hostile']}")
        print(f"  Flags: {result['flags_detected']}")


def main():
    parser = argparse.ArgumentParser(description='Analyze Retell call transcripts')
    parser.add_argument('--limit', type=int, help='Limit number of calls to analyze')
    parser.add_argument('--reanalyze', action='store_true', help='Re-analyze all calls')
    parser.add_argument('--stats', action='store_true', help='Show analysis statistics')
    parser.add_argument('--test', action='store_true', help='Test with sample transcripts')
    parser.add_argument('--aggregate', action='store_true', help='Only run contact aggregation')
    args = parser.parse_args()

    if args.test:
        test_analysis()
        return

    print("=" * 60)
    print("RETELL TRANSCRIPT ANALYSIS")
    print("=" * 60)

    conn = get_connection()
    print("[OK] Connected to database")

    # Ensure schema exists
    ensure_schema(conn)

    if args.stats:
        show_stats(conn)
        conn.close()
        return

    if args.aggregate:
        aggregate_to_contacts(conn)
        conn.close()
        return

    # Get calls to analyze
    if args.reanalyze:
        print("\n[INFO] Re-analyzing all calls...")
        calls = get_all_retell_calls(conn, args.limit)
    else:
        calls = get_unanalyzed_calls(conn, args.limit)

    if not calls:
        print("\n[INFO] No calls to analyze")
        show_stats(conn)
        conn.close()
        return

    print(f"\n[INFO] Found {len(calls):,} calls to analyze")

    # Analyze batch
    stats = analyze_batch(conn, calls)

    print("\n=== Analysis Complete ===")
    print(f"  Total processed: {stats['analyzed']:,}")
    print(f"  DNC flagged:     {stats['dnc']:,}")
    print(f"  Retired:         {stats['retired']:,}")
    print(f"  Deceased:        {stats['deceased']:,}")
    print(f"  Wrong numbers:   {stats['wrong_number']:,}")
    print(f"  Hot leads:       {stats['hot_leads']:,}")
    print(f"  Callbacks:       {stats['callbacks']:,}")
    print(f"  Hostile:         {stats['hostile']:,}")
    print(f"  Errors:          {stats['errors']:,}")

    # Aggregate to contacts
    aggregate_to_contacts(conn)

    # Show final stats
    show_stats(conn)

    conn.close()
    print("\n[DONE]")


if __name__ == "__main__":
    main()
