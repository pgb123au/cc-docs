#!/usr/bin/env python3
"""
Initial sync - Pull 10 most recent records from each provider
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

# Add parent dir for imports
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

def load_retell_api_key():
    """Load Retell API key"""
    creds = load_credentials()
    if creds.get("RETELL_API_KEY"):
        return creds["RETELL_API_KEY"]

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

CREDS = load_credentials()

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

# ============================================================================
# Database Functions
# ============================================================================

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_provider_id(conn, name):
    """Get provider ID by name"""
    with conn.cursor() as cur:
        cur.execute("SELECT provider_id FROM telco.providers WHERE name = %s", (name,))
        row = cur.fetchone()
        return row[0] if row else None

# ============================================================================
# Zadarma API
# ============================================================================

class ZadarmaAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.zadarma.com"

    def _sign(self, method, params=None):
        params_string = "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
        md5_hash = hashlib.md5(params_string.encode()).hexdigest()
        sign_string = f"{method}{params_string}{md5_hash}"
        hex_sig = hmac.new(self.api_secret.encode(), sign_string.encode(), hashlib.sha1).hexdigest()
        return base64.b64encode(hex_sig.encode()).decode()

    def request(self, method, params=None):
        headers = {"Authorization": f"{self.api_key}:{self._sign(method, params)}"}
        resp = requests.get(f"{self.base_url}{method}", headers=headers, params=params)
        return resp.json()

    def get_balance(self):
        return self.request("/v1/info/balance/")

    def get_numbers(self):
        return self.request("/v1/direct_numbers/")

    def get_statistics(self, start=None, end=None):
        """Get call history"""
        if not start:
            start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end:
            end = datetime.now().strftime("%Y-%m-%d")
        return self.request("/v1/statistics/", {"start": start, "end": end})

# ============================================================================
# Telnyx API
# ============================================================================

class TelnyxAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.telnyx.com/v2"

    def request(self, endpoint, params=None):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = requests.get(f"{self.base_url}{endpoint}", headers=headers, params=params)
        return resp.json()

    def get_balance(self):
        return self.request("/balance")

    def get_numbers(self):
        return self.request("/phone_numbers")

    def get_call_events(self, limit=10):
        """Get recent call events"""
        return self.request("/call_events", {"page[size]": limit})

# ============================================================================
# Retell API
# ============================================================================

class RetellAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = Retell(api_key=api_key) if RETELL_AVAILABLE else None

    def get_calls(self, limit=10):
        """Get recent calls"""
        if not self.client:
            return []
        try:
            calls = self.client.call.list(limit=limit, sort_order="descending")
            return [self._call_to_dict(c) for c in calls]
        except Exception as e:
            print(f"  [ERROR] Retell calls: {e}")
            return []

    def get_agents(self):
        """Get all agents"""
        if not self.client:
            return []
        try:
            agents = self.client.agent.list()
            return [{"agent_id": a.agent_id, "agent_name": a.agent_name,
                     "voice_id": getattr(a, 'voice_id', ''),
                     "language": getattr(a, 'language', '')} for a in agents]
        except Exception as e:
            print(f"  [ERROR] Retell agents: {e}")
            return []

    def get_numbers(self):
        """Get phone numbers"""
        if not self.client:
            return []
        try:
            numbers = self.client.phone_number.list()
            return [{"phone_number": n.phone_number,
                     "nickname": getattr(n, 'nickname', ''),
                     "inbound_agent_id": getattr(n, 'inbound_agent_id', None),
                     "outbound_agent_id": getattr(n, 'outbound_agent_id', None)} for n in numbers]
        except Exception as e:
            print(f"  [ERROR] Retell numbers: {e}")
            return []

    def _call_to_dict(self, c):
        # Handle call_analysis - convert to dict if it's an object
        call_analysis = getattr(c, 'call_analysis', None)
        if call_analysis and hasattr(call_analysis, '__dict__'):
            try:
                call_analysis = {k: v for k, v in call_analysis.__dict__.items()
                                if not k.startswith('_')}
            except:
                call_analysis = str(call_analysis)

        return {
            "call_id": getattr(c, 'call_id', ''),
            "agent_id": getattr(c, 'agent_id', ''),
            "from_number": getattr(c, 'from_number', ''),
            "to_number": getattr(c, 'to_number', ''),
            "direction": getattr(c, 'direction', ''),
            "call_status": getattr(c, 'call_status', ''),
            "start_timestamp": getattr(c, 'start_timestamp', None),
            "end_timestamp": getattr(c, 'end_timestamp', None),
            "duration_ms": getattr(c, 'duration_ms', 0),
            "transcript": getattr(c, 'transcript', ''),
            "recording_url": getattr(c, 'recording_url', ''),
            "call_analysis": call_analysis,
        }

# ============================================================================
# Sync Functions
# ============================================================================

def sync_zadarma(conn):
    """Sync Zadarma data"""
    print("\n" + "=" * 60)
    print("SYNCING ZADARMA")
    print("=" * 60)

    if not CREDS.get("ZADARMA_API_KEY"):
        print("  [SKIP] No Zadarma credentials")
        return

    api = ZadarmaAPI(CREDS["ZADARMA_API_KEY"], CREDS["ZADARMA_API_SECRET"])
    provider_id = get_provider_id(conn, "zadarma")

    # Balance snapshot
    print("\n[Balance]")
    balance = api.get_balance()
    if balance.get("status") == "success":
        bal = float(balance.get("balance", 0))
        cur = balance.get("currency", "USD")
        print(f"  Balance: ${bal} {cur}")

        with conn.cursor() as cur_db:
            cur_db.execute("""
                INSERT INTO telco.balance_snapshots (provider_id, balance, currency)
                VALUES (%s, %s, %s)
            """, (provider_id, bal, cur))
        conn.commit()
        print("  [OK] Balance snapshot saved")

    # Phone numbers
    print("\n[Phone Numbers]")
    numbers = api.get_numbers()
    if numbers.get("status") == "success":
        for n in numbers.get("info", [])[:10]:
            phone = f"+{n.get('number', '')}"
            print(f"  {phone} - {n.get('description', '')}")

            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.phone_numbers
                    (provider_id, phone_number, phone_number_e164, status, city, monthly_cost, currency, metadata, last_synced)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (provider_id, phone_number) DO UPDATE SET
                        status = EXCLUDED.status, monthly_cost = EXCLUDED.monthly_cost,
                        metadata = EXCLUDED.metadata, last_synced = NOW()
                """, (provider_id, phone, phone, n.get('status'), n.get('description'),
                      n.get('monthly_fee'), 'USD', Json(n)))
        conn.commit()
        print(f"  [OK] {len(numbers.get('info', []))} numbers synced")

    # Call history (last 10)
    print("\n[Call History - Last 10]")
    stats = api.get_statistics()
    if stats.get("status") == "success":
        calls = stats.get("stats", [])[:10]
        for c in calls:
            call_id = c.get('id', c.get('callid', str(hash(str(c)))))
            print(f"  {c.get('calldate', '?')} | {c.get('src', '?')} -> {c.get('dst', '?')} | {c.get('billsec', 0)}s | ${c.get('cost', 0)}")

            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.calls
                    (provider_id, external_call_id, from_number, to_number, direction,
                     started_at, duration_seconds, billable_seconds, status, disposition,
                     cost, currency, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (provider_id, external_call_id) DO NOTHING
                """, (provider_id, str(call_id), c.get('src'), c.get('dst'),
                      'outbound' if c.get('direction') == 'outgoing' else 'inbound',
                      c.get('calldate'), c.get('duration', 0), c.get('billsec', 0),
                      c.get('disposition'), c.get('disposition'),
                      c.get('cost', 0), c.get('currency', 'USD'), Json(c)))
        conn.commit()
        print(f"  [OK] {len(calls)} calls synced")
    else:
        print(f"  [WARN] {stats}")

def sync_telnyx(conn):
    """Sync Telnyx data"""
    print("\n" + "=" * 60)
    print("SYNCING TELNYX")
    print("=" * 60)

    if not CREDS.get("TELNYX_API_KEY"):
        print("  [SKIP] No Telnyx credentials")
        return

    api = TelnyxAPI(CREDS["TELNYX_API_KEY"])
    provider_id = get_provider_id(conn, "telnyx")

    # Balance snapshot
    print("\n[Balance]")
    balance = api.get_balance()
    if "data" in balance:
        bal = float(balance["data"].get("balance", 0))
        cur = balance["data"].get("currency", "USD")
        credit = float(balance["data"].get("credit_limit", 0))
        print(f"  Balance: ${bal} {cur} (Credit: ${credit})")

        with conn.cursor() as cur_db:
            cur_db.execute("""
                INSERT INTO telco.balance_snapshots (provider_id, balance, currency, credit_limit)
                VALUES (%s, %s, %s, %s)
            """, (provider_id, bal, cur, credit))
        conn.commit()
        print("  [OK] Balance snapshot saved")

    # Phone numbers
    print("\n[Phone Numbers]")
    numbers = api.get_numbers()
    if "data" in numbers:
        for n in numbers["data"][:10]:
            phone = n.get("phone_number", "")
            print(f"  {phone} - {n.get('connection_name', 'No connection')}")

            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.phone_numbers
                    (provider_id, phone_number, phone_number_e164, status, nickname, metadata, last_synced)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (provider_id, phone_number) DO UPDATE SET
                        status = EXCLUDED.status, metadata = EXCLUDED.metadata, last_synced = NOW()
                """, (provider_id, phone, phone, n.get('status'),
                      n.get('connection_name'), Json(n)))
        conn.commit()
        print(f"  [OK] {len(numbers.get('data', []))} numbers synced")

    # Note: Telnyx CDRs require separate CDR API access
    print("\n[Call History]")
    print("  [INFO] Telnyx CDRs require CDR API endpoint - checking call_events...")
    events = api.get_call_events(limit=10)
    if "data" in events and events["data"]:
        for e in events["data"][:10]:
            print(f"  {e.get('occurred_at', '?')} | {e.get('event_type', '?')}")
    else:
        print("  [INFO] No recent call events or CDR API not enabled")

def sync_retell(conn):
    """Sync Retell data"""
    print("\n" + "=" * 60)
    print("SYNCING RETELL")
    print("=" * 60)

    api_key = load_retell_api_key()
    if not api_key:
        print("  [SKIP] No Retell API key")
        return

    if not RETELL_AVAILABLE:
        print("  [SKIP] retell-sdk not installed")
        return

    api = RetellAPI(api_key)
    provider_id = get_provider_id(conn, "retell")

    # Agents
    print("\n[Agents]")
    agents = api.get_agents()
    agent_map = {}
    for a in agents[:50]:  # Limit to first 50
        agent_map[a['agent_id']] = a['agent_name']
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO telco.retell_agents (agent_id, agent_name, voice_id, language, last_synced)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (agent_id) DO UPDATE SET
                    agent_name = EXCLUDED.agent_name, last_synced = NOW()
            """, (a['agent_id'], a['agent_name'], a.get('voice_id'), a.get('language')))
    conn.commit()
    print(f"  [OK] {len(agents)} agents synced")

    # Phone numbers
    print("\n[Phone Numbers]")
    numbers = api.get_numbers()
    for n in numbers:
        phone = n.get("phone_number", "")
        agent_name = agent_map.get(n.get('inbound_agent_id'), '')
        print(f"  {phone} -> {agent_name or 'No agent'}")

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO telco.phone_numbers
                (provider_id, phone_number, phone_number_e164, nickname,
                 retell_agent_id, retell_agent_name, last_synced)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (provider_id, phone_number) DO UPDATE SET
                    retell_agent_id = EXCLUDED.retell_agent_id,
                    retell_agent_name = EXCLUDED.retell_agent_name,
                    last_synced = NOW()
            """, (provider_id, phone, phone, n.get('nickname'),
                  n.get('inbound_agent_id'), agent_name))
    conn.commit()
    print(f"  [OK] {len(numbers)} numbers synced")

    # Recent calls (last 10)
    print("\n[Call History - Last 10]")
    calls = api.get_calls(limit=10)
    for c in calls:
        agent_name = agent_map.get(c.get('agent_id'), c.get('agent_id', ''))
        duration_sec = (c.get('duration_ms') or 0) // 1000

        # Format timestamp
        start_ts = c.get('start_timestamp')
        if start_ts:
            try:
                dt = datetime.fromtimestamp(start_ts / 1000)
                start_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                start_str = str(start_ts)
        else:
            start_str = "?"

        print(f"  {start_str} | {c.get('from_number', '?')} -> {c.get('to_number', '?')} | {duration_sec}s | {c.get('call_status', '?')}")

        with conn.cursor() as cur:
            # Convert timestamps
            started_at = None
            ended_at = None
            if c.get('start_timestamp'):
                started_at = datetime.fromtimestamp(c['start_timestamp'] / 1000)
            if c.get('end_timestamp'):
                ended_at = datetime.fromtimestamp(c['end_timestamp'] / 1000)

            cur.execute("""
                INSERT INTO telco.calls
                (provider_id, external_call_id, from_number, to_number, direction,
                 started_at, ended_at, duration_seconds, status,
                 retell_agent_id, retell_agent_name, transcript,
                 has_recording, recording_url, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (provider_id, external_call_id) DO UPDATE SET
                    status = EXCLUDED.status, transcript = EXCLUDED.transcript
            """, (provider_id, c.get('call_id'), c.get('from_number'), c.get('to_number'),
                  c.get('direction'), started_at, ended_at, duration_sec,
                  c.get('call_status'), c.get('agent_id'), agent_name,
                  c.get('transcript'), bool(c.get('recording_url')),
                  c.get('recording_url'), Json(make_json_serializable(c))))
    conn.commit()
    print(f"  [OK] {len(calls)} calls synced")

# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("TELCO WAREHOUSE - INITIAL SYNC")
    print("Pulling 10 most recent records from each provider")
    print("=" * 60)

    # Test database connection
    print("\n[Database Connection]")
    try:
        conn = get_db_connection()
        print(f"  [OK] Connected to {DB_CONFIG['host']}")
    except Exception as e:
        print(f"  [ERROR] {e}")
        return

    try:
        # Sync each provider
        sync_zadarma(conn)
        sync_telnyx(conn)
        sync_retell(conn)

        # Summary
        print("\n" + "=" * 60)
        print("SYNC COMPLETE - Summary")
        print("=" * 60)

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM telco.phone_numbers")
            print(f"  Phone Numbers: {cur.fetchone()[0]}")

            cur.execute("SELECT COUNT(*) FROM telco.calls")
            print(f"  Calls: {cur.fetchone()[0]}")

            cur.execute("SELECT COUNT(*) FROM telco.balance_snapshots")
            print(f"  Balance Snapshots: {cur.fetchone()[0]}")

            cur.execute("SELECT COUNT(*) FROM telco.retell_agents")
            print(f"  Retell Agents: {cur.fetchone()[0]}")

        print("\n[OK] Initial sync complete!")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
