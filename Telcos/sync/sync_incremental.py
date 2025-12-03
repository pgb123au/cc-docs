#!/usr/bin/env python3
"""
Incremental sync for Retell, Zadarma, and Telnyx calls
Designed to run every 5 minutes - only fetches new data since last sync
"""

import os
import sys
import json
import hashlib
import hmac
import base64
import requests
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:
    print("Installing psycopg2...")
    os.system("pip install psycopg2-binary")
    import psycopg2
    from psycopg2.extras import Json

try:
    from retell import Retell
    RETELL_AVAILABLE = True
except ImportError:
    RETELL_AVAILABLE = False

# ============================================================================
# Configuration
# ============================================================================

DB_CONFIG = {
    "host": "96.47.238.189",
    "port": 5432,
    "database": "telco_warehouse",
    "user": "telco_sync",
    "password": "TelcoSync2024!"
}

def load_credentials():
    """Load API credentials from .credentials file"""
    cred_file = Path(__file__).parent.parent / ".credentials"
    creds = {}
    if cred_file.exists():
        with open(cred_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    creds[key.strip()] = value.strip()
    return creds

CREDS = load_credentials()

def load_retell_api_key():
    """Load Retell API key"""
    if CREDS.get("RETELL_API_KEY"):
        return CREDS["RETELL_API_KEY"]
    paths = [
        Path.home() / "Downloads" / "Retell_API_Key.txt",
        Path.home() / "Downloads" / "CC" / "retell" / "Retell_API_Key.txt",
    ]
    for path in paths:
        if path.exists():
            key = path.read_text().strip()
            key = key.replace("API Key:", "").replace("key:", "").strip()
            if key:
                return key
    return None

def make_json_serializable(obj):
    """Convert object to JSON-serializable dict"""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_json_serializable(v) for v in obj]
    if hasattr(obj, '__dict__'):
        return {k: make_json_serializable(v) for k, v in obj.__dict__.items()
                if not k.startswith('_')}
    return str(obj)

def call_to_dict(call):
    """Convert Retell call object to dict"""
    if hasattr(call, '__dict__'):
        return {k: make_json_serializable(v) for k, v in call.__dict__.items()
                if not k.startswith('_')}
    return make_json_serializable(call)

# ============================================================================
# Zadarma API
# ============================================================================

class ZadarmaAPI:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.zadarma.com"

    def _generate_signature(self, method: str, params: dict = None) -> str:
        if params:
            sorted_params = sorted(params.items())
            params_string = "&".join(f"{k}={v}" for k, v in sorted_params)
        else:
            params_string = ""
        md5_hash = hashlib.md5(params_string.encode()).hexdigest()
        sign_string = f"{method}{params_string}{md5_hash}"
        hex_signature = hmac.new(
            self.api_secret.encode(),
            sign_string.encode(),
            hashlib.sha1
        ).hexdigest()
        return base64.b64encode(hex_signature.encode()).decode()

    def request(self, method: str, params: dict = None) -> dict:
        signature = self._generate_signature(method, params)
        headers = {"Authorization": f"{self.api_key}:{signature}"}
        url = f"{self.base_url}{method}"
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def get_statistics(self, start: str = None, end: str = None) -> dict:
        """Get call statistics. Dates in format YYYY-MM-DD"""
        if not start:
            start = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        if not end:
            end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.request("/v1/statistics/", {"start": start, "end": end})

# ============================================================================
# Telnyx API
# ============================================================================

class TelnyxAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.telnyx.com/v2"

    def request(self, endpoint: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=headers)
        return response.json()

    def get_call_events(self, limit: int = 50) -> dict:
        return self.request(f"/call_events?page[size]={limit}")

# ============================================================================
# Database helpers
# ============================================================================

def get_provider_id(conn, name):
    """Get provider ID by name"""
    with conn.cursor() as cur:
        cur.execute("SELECT provider_id FROM telco.providers WHERE name = %s", (name,))
        result = cur.fetchone()
        return result[0] if result else None

def get_last_sync_timestamp(conn, provider_name):
    """Get the most recent call timestamp for a provider"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT MAX(started_at)
            FROM telco.calls
            WHERE provider_id = (SELECT provider_id FROM telco.providers WHERE name = %s)
        """, (provider_name,))
        result = cur.fetchone()[0]
        if result:
            return result
    return None

def get_agent_map(conn):
    """Get agent_id -> agent_name mapping"""
    agent_map = {}
    with conn.cursor() as cur:
        cur.execute("SELECT agent_id, agent_name FROM telco.retell_agents")
        for row in cur.fetchall():
            agent_map[row[0]] = row[1]
    return agent_map

# ============================================================================
# Sync Functions
# ============================================================================

def sync_retell(conn):
    """Sync new Retell calls"""
    print("\n[RETELL]")

    if not RETELL_AVAILABLE:
        print("  [SKIP] retell-sdk not installed")
        return 0

    api_key = load_retell_api_key()
    if not api_key:
        print("  [SKIP] No API key")
        return 0

    provider_id = get_provider_id(conn, 'retell')
    if not provider_id:
        print("  [ERROR] Provider not found")
        return 0

    # Get last sync timestamp
    last_sync = get_last_sync_timestamp(conn, 'retell')
    if last_sync:
        # Convert to milliseconds, add 1ms to avoid re-fetch
        last_ts = int(last_sync.timestamp() * 1000) + 1
        print(f"  Last sync: {last_sync}")
    else:
        # Default to 1 hour ago
        last_ts = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
        print(f"  No existing data, fetching last hour")

    # Fetch new calls
    client = Retell(api_key=api_key)
    try:
        calls = client.call.list(
            limit=100,
            sort_order="descending",
            filter_criteria={
                "start_timestamp": {
                    "lower_threshold": last_ts
                }
            }
        )
        calls = [call_to_dict(c) for c in calls]
    except Exception as e:
        print(f"  [ERROR] API error: {e}")
        return 0

    if not calls:
        print(f"  No new calls")
        return 0

    print(f"  Found {len(calls)} new calls")

    # Get agent mapping
    agent_map = get_agent_map(conn)

    # Sync each call
    synced = 0
    for c in calls:
        agent_name = agent_map.get(c.get('agent_id'), c.get('agent_id', ''))
        duration_sec = (c.get('duration_ms') or 0) // 1000

        started_at = None
        ended_at = None
        if c.get('start_timestamp'):
            started_at = datetime.fromtimestamp(c['start_timestamp'] / 1000)
        if c.get('end_timestamp'):
            ended_at = datetime.fromtimestamp(c['end_timestamp'] / 1000)

        transcript = c.get('transcript', '')
        transcript_words = len(transcript.split()) if transcript else 0

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.calls
                    (provider_id, external_call_id, from_number, to_number, direction,
                     started_at, ended_at, duration_seconds, status,
                     retell_agent_id, retell_agent_name, transcript, full_transcript, transcript_words,
                     has_recording, recording_url, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (provider_id, external_call_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        transcript = EXCLUDED.transcript,
                        full_transcript = EXCLUDED.full_transcript,
                        transcript_words = EXCLUDED.transcript_words,
                        ended_at = EXCLUDED.ended_at,
                        duration_seconds = EXCLUDED.duration_seconds,
                        has_recording = EXCLUDED.has_recording,
                        recording_url = EXCLUDED.recording_url,
                        raw_data = EXCLUDED.raw_data
                """, (provider_id, c.get('call_id'), c.get('from_number'), c.get('to_number'),
                      c.get('direction'), started_at, ended_at, duration_sec,
                      c.get('call_status'), c.get('agent_id'), agent_name,
                      transcript[:500] if transcript else None,
                      transcript,
                      transcript_words,
                      bool(c.get('recording_url')),
                      c.get('recording_url'), Json(c)))

            # Sync call analysis if present
            analysis = c.get('call_analysis')
            if analysis:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO telco.call_analysis
                        (call_id, provider_id, agent_id, agent_name, call_summary,
                         call_sentiment, user_sentiment, call_successful, in_voicemail,
                         custom_analysis, latency_stats, raw_analysis)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (call_id) DO UPDATE SET
                            call_summary = EXCLUDED.call_summary,
                            call_sentiment = EXCLUDED.call_sentiment,
                            user_sentiment = EXCLUDED.user_sentiment,
                            call_successful = EXCLUDED.call_successful,
                            raw_analysis = EXCLUDED.raw_analysis
                    """, (c.get('call_id'), provider_id, c.get('agent_id'), agent_name,
                          analysis.get('call_summary', ''),
                          analysis.get('call_sentiment', ''),
                          analysis.get('user_sentiment', ''),
                          analysis.get('call_successful'),
                          analysis.get('in_voicemail'),
                          Json(analysis.get('custom_analysis_data', {})),
                          Json(c.get('latency', {})),
                          Json(analysis)))

            synced += 1
        except Exception as e:
            print(f"  [WARN] Failed to sync {c.get('call_id')}: {e}")

    conn.commit()
    print(f"  Synced {synced} calls")
    return synced


def sync_zadarma(conn):
    """Sync new Zadarma calls"""
    print("\n[ZADARMA]")

    if not CREDS.get("ZADARMA_API_KEY") or not CREDS.get("ZADARMA_API_SECRET"):
        print("  [SKIP] No credentials")
        return 0

    provider_id = get_provider_id(conn, 'zadarma')
    if not provider_id:
        print("  [ERROR] Provider not found")
        return 0

    # Get stats for last hour (Zadarma doesn't support timestamp filtering well)
    api = ZadarmaAPI(CREDS["ZADARMA_API_KEY"], CREDS["ZADARMA_API_SECRET"])

    # Fetch last hour of data
    start = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stats = api.get_statistics(start, end)

    if stats.get("status") != "success":
        print(f"  [ERROR] API error: {stats.get('message', 'unknown')}")
        return 0

    calls = stats.get("stats", [])
    if not calls:
        print("  No new calls")
        return 0

    print(f"  Found {len(calls)} calls in last hour")

    synced = 0
    for c in calls:
        call_id = c.get('id', c.get('callid', str(hash(str(c)))))
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.calls
                    (provider_id, external_call_id, from_number, to_number, direction,
                     started_at, duration_seconds, billable_seconds, status, disposition,
                     cost, currency, has_recording, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (provider_id, external_call_id) DO NOTHING
                """, (provider_id, str(call_id), c.get('src'), c.get('dst'),
                      'outbound' if c.get('direction') == 'outgoing' else 'inbound',
                      c.get('calldate'), c.get('duration', 0), c.get('billsec', 0),
                      c.get('disposition'), c.get('disposition'),
                      c.get('cost', 0), c.get('currency', 'USD'),
                      bool(c.get('recording')), Json(c)))
                if cur.rowcount > 0:
                    synced += 1
        except Exception as e:
            print(f"  [WARN] Failed to sync call {call_id}: {e}")

    conn.commit()
    print(f"  Synced {synced} new calls")
    return synced


def sync_telnyx(conn):
    """Sync new Telnyx call events"""
    print("\n[TELNYX]")

    if not CREDS.get("TELNYX_API_KEY"):
        print("  [SKIP] No credentials")
        return 0

    provider_id = get_provider_id(conn, 'telnyx')
    if not provider_id:
        print("  [ERROR] Provider not found")
        return 0

    api = TelnyxAPI(CREDS["TELNYX_API_KEY"])
    events = api.get_call_events(limit=50)

    if "data" not in events or not events["data"]:
        print("  No call events")
        return 0

    print(f"  Found {len(events['data'])} call events")

    synced = 0
    for e in events["data"]:
        event_id = e.get('id', '')
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.calls
                    (provider_id, external_call_id, from_number, to_number, direction,
                     started_at, status, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (provider_id, external_call_id) DO NOTHING
                """, (provider_id, event_id, e.get('from', ''), e.get('to', ''),
                      e.get('direction', ''), e.get('occurred_at'),
                      e.get('event_type', ''), Json(e)))
                if cur.rowcount > 0:
                    synced += 1
        except Exception as e:
            print(f"  [WARN] Failed to sync event {event_id}: {e}")

    conn.commit()
    print(f"  Synced {synced} new events")
    return synced


# ============================================================================
# Main
# ============================================================================

def sync_incremental():
    """Run incremental sync for all providers"""

    conn = psycopg2.connect(**DB_CONFIG)
    print("[OK] Connected to database")

    total = 0
    total += sync_retell(conn)
    total += sync_zadarma(conn)
    total += sync_telnyx(conn)

    conn.close()
    return total


if __name__ == "__main__":
    import time

    print("=" * 50)
    print("TELCO INCREMENTAL SYNC")
    print(f"Started: {datetime.now()}")
    print("=" * 50)

    start = time.time()
    total = sync_incremental()
    elapsed = time.time() - start

    print("\n" + "=" * 50)
    print(f"Total synced: {total} records")
    print(f"Completed in {elapsed:.2f}s")
    print("=" * 50)
