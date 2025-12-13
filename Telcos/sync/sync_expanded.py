#!/usr/bin/env python3
"""
Expanded sync - Pull all data types from Zadarma, Telnyx, and Retell
Includes: SIP accounts, voicemail, CDRs, SMS, FQDN connections, voice configs, etc.
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
    # On server: /opt/telco_sync/.credentials (same dir as script)
    # Local: parent.parent would be CC/.credentials
    cred_file = Path(__file__).parent / ".credentials"
    if not cred_file.exists():
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
    return psycopg2.connect(**DB_CONFIG)

def get_provider_id(conn, name):
    with conn.cursor() as cur:
        cur.execute("SELECT provider_id FROM telco.providers WHERE name = %s", (name,))
        row = cur.fetchone()
        return row[0] if row else None

# ============================================================================
# Zadarma API (Expanded)
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
        if not start:
            start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end:
            end = datetime.now().strftime("%Y-%m-%d")
        return self.request("/v1/statistics/", {"start": start, "end": end})

    def get_sip_accounts(self):
        """Get SIP accounts (virtual PBX extensions)"""
        return self.request("/v1/sip/")

    def get_voicemail(self):
        """Get voicemail messages"""
        return self.request("/v1/voicemail/")

    def get_caller_ids(self):
        """Get caller ID settings"""
        return self.request("/v1/info/lists_callerid/")

    def get_recordings(self, start=None, end=None):
        """Get call recordings list"""
        if not start:
            start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not end:
            end = datetime.now().strftime("%Y-%m-%d")
        return self.request("/v1/statistics/", {"start": start, "end": end})

# ============================================================================
# Telnyx API (Expanded)
# ============================================================================

class TelnyxAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.telnyx.com/v2"

    def request(self, endpoint, params=None):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = requests.get(f"{self.base_url}{endpoint}", headers=headers, params=params)
        return resp.json()

    def request_url(self, url):
        """Request a full URL (for pagination)"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = requests.get(url, headers=headers)
        return resp.json()

    def get_balance(self):
        return self.request("/balance")

    def get_numbers(self):
        return self.request("/phone_numbers")

    def get_call_events_all(self, max_pages=50):
        """Get ALL call events with pagination"""
        all_events = []
        page = 1
        while page <= max_pages:
            result = self.request("/call_events", {"page[size]": 250, "page[number]": page})
            if "data" not in result or not result["data"]:
                break
            all_events.extend(result["data"])
            # Check if there are more pages
            meta = result.get("meta", {})
            total_pages = meta.get("total_pages", 1)
            if page >= total_pages:
                break
            page += 1
        return {"data": all_events}

    def get_call_events(self, limit=50):
        """Legacy method - use get_call_events_all for full sync"""
        return self.request("/call_events", {"page[size]": limit})

    def get_fqdn_connections(self):
        return self.request("/fqdn_connections")

    def get_fqdns(self):
        return self.request("/fqdns")

    def get_outbound_voice_profiles(self):
        return self.request("/outbound_voice_profiles")

    def get_messaging_profiles(self):
        return self.request("/messaging_profiles")

    def get_credential_connections(self):
        return self.request("/credential_connections")

    def get_number_orders(self, limit=50):
        return self.request("/number_orders", {"page[size]": limit})

    def get_porting_orders(self, limit=50):
        return self.request("/porting_orders", {"page[size]": limit})

    def get_messages_all(self, max_pages=50):
        """Get ALL SMS/MMS messages with pagination"""
        all_messages = []
        page = 1
        while page <= max_pages:
            result = self.request("/messages", {"page[size]": 250, "page[number]": page})
            if "data" not in result or not result["data"]:
                break
            all_messages.extend(result["data"])
            meta = result.get("meta", {})
            total_pages = meta.get("total_pages", 1)
            if page >= total_pages:
                break
            page += 1
        return {"data": all_messages}

    def get_messages(self, limit=50):
        """Get SMS/MMS messages"""
        return self.request("/messages", {"page[size]": limit})

    def get_cdr_requests(self):
        """Get CDR report requests"""
        return self.request("/reports/cdr_requests")

# ============================================================================
# Retell API (Expanded)
# ============================================================================

class RetellAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = Retell(api_key=api_key) if RETELL_AVAILABLE else None
        self.base_url = "https://api.retellai.com"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def _http_get(self, endpoint):
        """Direct HTTP request for endpoints not in SDK"""
        resp = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
        if resp.status_code == 200:
            return resp.json()
        return None

    def get_calls(self, limit=50):
        if not self.client:
            return []
        try:
            calls = self.client.call.list(limit=limit, sort_order="descending")
            return [self._call_to_dict(c) for c in calls]
        except Exception as e:
            print(f"  [ERROR] Retell calls: {e}")
            return []

    def get_call_detail(self, call_id):
        """Get detailed call info including full transcript"""
        if not self.client:
            return None
        try:
            call = self.client.call.retrieve(call_id)
            return self._call_to_dict(call)
        except Exception as e:
            print(f"  [ERROR] Call detail {call_id}: {e}")
            return None

    def get_agents(self):
        if not self.client:
            return []
        try:
            agents = self.client.agent.list()
            return [self._agent_to_dict(a) for a in agents]
        except Exception as e:
            print(f"  [ERROR] Retell agents: {e}")
            return []

    def get_agent_detail(self, agent_id):
        """Get detailed agent config"""
        if not self.client:
            return None
        try:
            agent = self.client.agent.retrieve(agent_id)
            return make_json_serializable(agent)
        except:
            return None

    def get_numbers(self):
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

    def get_llms(self):
        """Get LLM configurations"""
        try:
            llms = self.client.llm.list()
            return [make_json_serializable(l) for l in llms]
        except Exception as e:
            print(f"  [ERROR] Retell LLMs: {e}")
            return []

    def get_voices(self):
        """Get available voices"""
        try:
            voices = self.client.voice.list()
            return [make_json_serializable(v) for v in voices]
        except Exception as e:
            print(f"  [ERROR] Retell voices: {e}")
            return []

    def get_knowledge_bases(self):
        """Get knowledge bases - may not be in SDK"""
        # Try SDK first
        try:
            if hasattr(self.client, 'knowledge_base'):
                kbs = self.client.knowledge_base.list()
                return [make_json_serializable(k) for k in kbs]
        except:
            pass
        # Fall back to HTTP
        result = self._http_get("/knowledge-base")
        return result if result else []

    def get_concurrency(self):
        """Get current concurrency usage"""
        try:
            result = self._http_get("/get-concurrency")
            return result
        except:
            return None

    def _call_to_dict(self, c):
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
            "agent_name": getattr(c, 'agent_name', ''),
            "from_number": getattr(c, 'from_number', ''),
            "to_number": getattr(c, 'to_number', ''),
            "direction": getattr(c, 'direction', ''),
            "call_status": getattr(c, 'call_status', ''),
            "start_timestamp": getattr(c, 'start_timestamp', None),
            "end_timestamp": getattr(c, 'end_timestamp', None),
            "duration_ms": getattr(c, 'duration_ms', 0),
            "transcript": getattr(c, 'transcript', ''),
            "transcript_object": make_json_serializable(getattr(c, 'transcript_object', [])),
            "transcript_with_tool_calls": make_json_serializable(getattr(c, 'transcript_with_tool_calls', [])),
            "recording_url": getattr(c, 'recording_url', ''),
            "public_log_url": getattr(c, 'public_log_url', ''),
            "call_analysis": call_analysis,
            "call_cost": make_json_serializable(getattr(c, 'call_cost', None)),
            "llm_token_usage": make_json_serializable(getattr(c, 'llm_token_usage', None)),
            "disconnection_reason": getattr(c, 'disconnection_reason', ''),
            "call_type": getattr(c, 'call_type', ''),
            "latency": make_json_serializable(getattr(c, 'latency', None)),
            "agent_version": getattr(c, 'agent_version', None),
            "collected_dynamic_variables": make_json_serializable(getattr(c, 'collected_dynamic_variables', {})),
            "retell_llm_dynamic_variables": make_json_serializable(getattr(c, 'retell_llm_dynamic_variables', {})),
            "custom_sip_headers": make_json_serializable(getattr(c, 'custom_sip_headers', {})),
            "data_storage_setting": getattr(c, 'data_storage_setting', ''),
            "opt_in_signed_url": getattr(c, 'opt_in_signed_url', False),
        }

    def _agent_to_dict(self, a):
        return {
            "agent_id": getattr(a, 'agent_id', ''),
            "agent_name": getattr(a, 'agent_name', ''),
            "voice_id": getattr(a, 'voice_id', ''),
            "language": getattr(a, 'language', ''),
            "llm_websocket_url": getattr(a, 'llm_websocket_url', ''),
            "webhook_url": getattr(a, 'webhook_url', ''),
        }

# ============================================================================
# Sync Functions
# ============================================================================

def sync_zadarma(conn):
    """Sync all Zadarma data"""
    print("\n" + "=" * 60)
    print("SYNCING ZADARMA (EXPANDED)")
    print("=" * 60)

    if not CREDS.get("ZADARMA_API_KEY"):
        print("  [SKIP] No Zadarma credentials")
        return

    api = ZadarmaAPI(CREDS["ZADARMA_API_KEY"], CREDS["ZADARMA_API_SECRET"])
    provider_id = get_provider_id(conn, "zadarma")

    # Balance
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

    # Phone numbers
    print("\n[Phone Numbers]")
    numbers = api.get_numbers()
    if numbers.get("status") == "success":
        count = 0
        for n in numbers.get("info", []):
            phone = f"+{n.get('number', '')}"
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
            count += 1
        conn.commit()
        print(f"  [OK] {count} numbers synced")

    # SIP Accounts (NEW)
    print("\n[SIP Accounts]")
    sip = api.get_sip_accounts()
    if sip.get("status") == "success":
        count = 0
        for s in sip.get("sips", []):
            sip_id = s.get('id', s.get('login', ''))
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.sip_accounts
                    (provider_id, sip_id, sip_name, caller_id, status, lines, metadata, last_synced)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (provider_id, sip_id) DO UPDATE SET
                        caller_id = EXCLUDED.caller_id, status = EXCLUDED.status,
                        metadata = EXCLUDED.metadata, last_synced = NOW()
                """, (provider_id, sip_id, s.get('display_name', ''),
                      s.get('caller_id', ''), s.get('status', 'active'),
                      s.get('lines', 1), Json(s)))
            count += 1
        conn.commit()
        print(f"  [OK] {count} SIP accounts synced")
    else:
        print(f"  [INFO] SIP API response: {sip.get('status', 'unknown')}")

    # Call Recordings (from statistics with recording_url) (NEW)
    print("\n[Call Recordings]")
    stats = api.get_statistics()
    recording_count = 0
    if stats.get("status") == "success":
        for c in stats.get("stats", []):
            if c.get('recording'):
                call_id = c.get('id', c.get('callid', str(hash(str(c)))))
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO telco.recordings
                        (provider_id, external_recording_id, recording_url, duration_seconds, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (provider_id, external_recording_id) DO NOTHING
                    """, (provider_id, str(call_id), c.get('recording'),
                          c.get('billsec', 0), c.get('calldate')))
                recording_count += 1
        conn.commit()
    print(f"  [OK] {recording_count} recordings synced")

    # Caller IDs (NEW)
    print("\n[Caller IDs]")
    caller_ids = api.get_caller_ids()
    if caller_ids.get("status") == "success":
        count = 0
        for cid in caller_ids.get("info", []):
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.caller_ids
                    (provider_id, sip_id, caller_id, name, is_default, metadata, last_synced)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (provider_id, sip_id, caller_id) DO UPDATE SET
                        is_default = EXCLUDED.is_default, last_synced = NOW()
                """, (provider_id, cid.get('sip', ''), cid.get('number', ''),
                      cid.get('description', ''), cid.get('default', False), Json(cid)))
            count += 1
        conn.commit()
        print(f"  [OK] {count} caller IDs synced")
    else:
        print(f"  [INFO] Caller ID API: {caller_ids.get('status', 'unknown')}")

    # Call history
    print("\n[Call History]")
    if stats.get("status") == "success":
        calls = stats.get("stats", [])[:50]
        for c in calls:
            call_id = c.get('id', c.get('callid', str(hash(str(c)))))
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
        conn.commit()
        print(f"  [OK] {len(calls)} calls synced")


def sync_telnyx(conn):
    """Sync all Telnyx data"""
    print("\n" + "=" * 60)
    print("SYNCING TELNYX (EXPANDED)")
    print("=" * 60)

    if not CREDS.get("TELNYX_API_KEY"):
        print("  [SKIP] No Telnyx credentials")
        return

    api = TelnyxAPI(CREDS["TELNYX_API_KEY"])
    provider_id = get_provider_id(conn, "telnyx")

    # Balance
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

    # Phone numbers
    print("\n[Phone Numbers]")
    numbers = api.get_numbers()
    if "data" in numbers:
        for n in numbers["data"]:
            phone = n.get("phone_number", "")
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

    # CDRs from call_events - NOW WITH FULL PAGINATION
    print("\n[Call Events/CDRs]")
    events = api.get_call_events_all(max_pages=100)  # Get ALL events
    if "data" in events and events["data"]:
        count = 0
        inserted = 0
        for e in events["data"]:
            event_id = e.get('id', '')
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
                    inserted += 1
            count += 1
        conn.commit()
        print(f"  [OK] {count} call events checked, {inserted} new records inserted")
    else:
        print("  [INFO] No call events found")

    # SMS Messages - NOW WITH FULL PAGINATION
    print("\n[SMS Messages]")
    messages = api.get_messages_all(max_pages=100)  # Get ALL messages
    if "data" in messages and messages["data"]:
        count = 0
        inserted = 0
        for m in messages["data"]:
            msg_id = m.get('id', '')
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.messages
                    (provider_id, external_message_id, from_number, to_number, direction,
                     message_type, body, status, segments, cost, currency, sent_at, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (provider_id, external_message_id) DO NOTHING
                """, (provider_id, msg_id,
                      m.get('from', {}).get('phone_number', '') if isinstance(m.get('from'), dict) else m.get('from', ''),
                      m.get('to', [{}])[0].get('phone_number', '') if isinstance(m.get('to'), list) else m.get('to', ''),
                      m.get('direction', ''),
                      m.get('type', 'SMS'),
                      m.get('text', ''),
                      m.get('to', [{}])[0].get('status', '') if isinstance(m.get('to'), list) else '',
                      m.get('parts', 1),
                      m.get('cost', {}).get('amount') if isinstance(m.get('cost'), dict) else None,
                      m.get('cost', {}).get('currency', 'USD') if isinstance(m.get('cost'), dict) else 'USD',
                      m.get('sent_at'),
                      Json(m)))
                if cur.rowcount > 0:
                    inserted += 1
            count += 1
        conn.commit()
        print(f"  [OK] {count} messages checked, {inserted} new records inserted")
    else:
        print("  [INFO] No messages found")

    # FQDN Connections (NEW - item 10)
    print("\n[FQDN Connections]")
    fqdn_conns = api.get_fqdn_connections()
    fqdns = api.get_fqdns()
    if "data" in fqdn_conns:
        count = 0
        for conn_data in fqdn_conns["data"]:
            conn_id = conn_data.get('id', '')
            # Find matching FQDN
            fqdn_value = ''
            if "data" in fqdns:
                for f in fqdns["data"]:
                    if str(f.get('connection_id')) == str(conn_id):
                        fqdn_value = f.get('fqdn', '')
                        break
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.fqdn_connections
                    (provider_id, connection_id, connection_name, fqdn, is_active,
                     transport_protocol, sip_region, metadata, last_synced)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (provider_id, connection_id) DO UPDATE SET
                        connection_name = EXCLUDED.connection_name, is_active = EXCLUDED.is_active,
                        fqdn = EXCLUDED.fqdn, last_synced = NOW()
                """, (provider_id, conn_id, conn_data.get('connection_name', ''),
                      fqdn_value, conn_data.get('active', False),
                      conn_data.get('transport_protocol', ''),
                      conn_data.get('inbound', {}).get('sip_region', ''), Json(conn_data)))
            count += 1
        conn.commit()
        print(f"  [OK] {count} FQDN connections synced")

    # Outbound Voice Profiles (NEW - item 11)
    print("\n[Outbound Voice Profiles]")
    profiles = api.get_outbound_voice_profiles()
    if "data" in profiles:
        count = 0
        for p in profiles["data"]:
            with conn.cursor() as cur:
                # Handle empty string for daily_spend_limit
                spend_limit = p.get('daily_spend_limit')
                if spend_limit == '' or spend_limit is None:
                    spend_limit = None
                else:
                    try:
                        spend_limit = float(spend_limit)
                    except:
                        spend_limit = None
                cur.execute("""
                    INSERT INTO telco.outbound_profiles
                    (provider_id, profile_id, profile_name, is_enabled, traffic_type,
                     service_plan, daily_spend_limit, metadata, last_synced)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (provider_id, profile_id) DO UPDATE SET
                        profile_name = EXCLUDED.profile_name, is_enabled = EXCLUDED.is_enabled,
                        last_synced = NOW()
                """, (provider_id, p.get('id', ''), p.get('name', ''),
                      p.get('enabled', True), p.get('traffic_type', ''),
                      p.get('service_plan', ''),
                      spend_limit, Json(p)))
            count += 1
        conn.commit()
        print(f"  [OK] {count} outbound profiles synced")

    # Messaging Profiles (NEW - item 12)
    print("\n[Messaging Profiles]")
    msg_profiles = api.get_messaging_profiles()
    if "data" in msg_profiles:
        count = 0
        for p in msg_profiles["data"]:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.messaging_profiles
                    (provider_id, profile_id, profile_name, is_enabled, number_pool_enabled,
                     webhook_url, metadata, last_synced)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (provider_id, profile_id) DO UPDATE SET
                        profile_name = EXCLUDED.profile_name, is_enabled = EXCLUDED.is_enabled,
                        last_synced = NOW()
                """, (provider_id, p.get('id', ''), p.get('name', ''),
                      p.get('enabled', True), (p.get('number_pool_settings') or {}).get('enabled', False),
                      p.get('webhook_url', ''), Json(p)))
            count += 1
        conn.commit()
        print(f"  [OK] {count} messaging profiles synced")

    # SIP Credentials (NEW - item 13)
    print("\n[SIP Credentials]")
    cred_conns = api.get_credential_connections()
    if "data" in cred_conns:
        count = 0
        for c in cred_conns["data"]:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.sip_credentials
                    (provider_id, credential_id, sip_username, connection_id, connection_name,
                     is_active, created_at_provider, last_synced)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (provider_id, credential_id) DO UPDATE SET
                        is_active = EXCLUDED.is_active, last_synced = NOW()
                """, (provider_id, c.get('id', ''), c.get('user_name', ''),
                      c.get('id', ''), c.get('connection_name', ''),
                      c.get('active', True), c.get('created_at')))
            count += 1
        conn.commit()
        print(f"  [OK] {count} SIP credentials synced")

    # Number Orders (NEW - item 14)
    print("\n[Number Orders]")
    orders = api.get_number_orders(limit=50)
    if "data" in orders:
        count = 0
        for o in orders["data"]:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.number_orders
                    (provider_id, order_id, order_type, status, phone_numbers,
                     customer_reference, requirements_met, ordered_at, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (provider_id, order_id) DO UPDATE SET
                        status = EXCLUDED.status
                """, (provider_id, o.get('id', ''), o.get('record_type', ''),
                      o.get('status', ''), Json(o.get('phone_numbers', [])),
                      o.get('customer_reference', ''), o.get('requirements_met', True),
                      o.get('created_at'), Json(o)))
            count += 1
        conn.commit()
        print(f"  [OK] {count} number orders synced")


def get_retell_workspaces(conn):
    """Get all active Retell workspaces from database"""
    workspaces = []
    with conn.cursor() as cur:
        cur.execute("""
            SELECT workspace_id, workspace_name, api_key_full
            FROM telco.retell_workspaces
            WHERE is_active = TRUE
        """)
        for row in cur.fetchall():
            workspaces.append({
                'workspace_id': row[0],
                'workspace_name': row[1],
                'api_key': row[2]
            })
    return workspaces


def sync_retell_workspace_calls(conn, provider_id, workspace_id, workspace_name, api_key, agent_map):
    """Sync ALL calls from a single Retell workspace using timestamp pagination"""
    from retell import Retell

    client = Retell(api_key=api_key)

    # Get the oldest call timestamp we already have for this workspace
    with conn.cursor() as cur:
        cur.execute("""
            SELECT MIN(started_at) FROM telco.calls
            WHERE provider_id = %s AND workspace_id = %s
        """, (provider_id, workspace_id))
        result = cur.fetchone()
        existing_oldest = result[0] if result and result[0] else None

    # Also get newest to check for new calls
    with conn.cursor() as cur:
        cur.execute("""
            SELECT MAX(started_at) FROM telco.calls
            WHERE provider_id = %s AND workspace_id = %s
        """, (provider_id, workspace_id))
        result = cur.fetchone()
        existing_newest = result[0] if result and result[0] else None

    total_synced = 0
    total_new = 0

    # Strategy: Get new calls (after newest) and old calls (before oldest)

    # 1. Get NEW calls (if any existing data)
    if existing_newest:
        newest_ts = int(existing_newest.timestamp() * 1000) + 1
        print(f"    Checking for new calls after {existing_newest}...")
        batch_count = 0
        while batch_count < 100:
            try:
                calls = client.call.list(
                    limit=1000,
                    sort_order='ascending',
                    filter_criteria={'start_timestamp': {'lower_threshold': newest_ts}}
                )
                if not calls:
                    break

                for c in calls:
                    call_dict = make_json_serializable(c.__dict__) if hasattr(c, '__dict__') else {}
                    inserted = sync_single_retell_call(conn, provider_id, workspace_id, workspace_name,
                                                       call_dict, agent_map)
                    total_synced += 1
                    if inserted:
                        total_new += 1

                    ts = getattr(c, 'start_timestamp', None)
                    if ts and ts > newest_ts:
                        newest_ts = ts + 1

                conn.commit()
                batch_count += 1

                if len(calls) < 1000:
                    break

            except Exception as e:
                print(f"    [ERROR] {e}")
                break

    # 2. Get OLD historical calls (before oldest or all if no existing)
    if existing_oldest:
        oldest_ts = int(existing_oldest.timestamp() * 1000) - 1
        print(f"    Backfilling calls before {existing_oldest}...")
    else:
        oldest_ts = None
        print(f"    Initial sync - fetching all historical calls...")

    batch_count = 0
    while batch_count < 100:  # Safety limit
        try:
            filter_criteria = {}
            if oldest_ts:
                filter_criteria = {'start_timestamp': {'upper_threshold': oldest_ts}}

            calls = client.call.list(
                limit=1000,
                sort_order='descending',
                filter_criteria=filter_criteria
            )

            if not calls:
                break

            for c in calls:
                call_dict = make_json_serializable(c.__dict__) if hasattr(c, '__dict__') else {}
                inserted = sync_single_retell_call(conn, provider_id, workspace_id, workspace_name,
                                                   call_dict, agent_map)
                total_synced += 1
                if inserted:
                    total_new += 1

                ts = getattr(c, 'start_timestamp', None)
                if ts:
                    if oldest_ts is None or ts < oldest_ts:
                        oldest_ts = ts - 1

            conn.commit()
            batch_count += 1
            print(f"      Batch {batch_count}: {len(calls)} calls (total new: {total_new})")

            if len(calls) < 1000:
                break

        except Exception as e:
            print(f"    [ERROR] {e}")
            break

    return total_synced, total_new


def sync_single_retell_call(conn, provider_id, workspace_id, workspace_name, c, agent_map):
    """Sync a single Retell call to database. Returns True if inserted (new)."""
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

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO telco.calls
            (provider_id, external_call_id, from_number, to_number, direction,
             started_at, ended_at, duration_seconds, status,
             retell_agent_id, retell_agent_name, transcript, full_transcript, transcript_words,
             has_recording, recording_url, workspace_id, workspace_name, raw_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (provider_id, external_call_id) DO UPDATE SET
                from_number = COALESCE(NULLIF(EXCLUDED.from_number, ''), telco.calls.from_number),
                to_number = COALESCE(NULLIF(EXCLUDED.to_number, ''), telco.calls.to_number),
                direction = COALESCE(NULLIF(EXCLUDED.direction, ''), telco.calls.direction),
                ended_at = COALESCE(EXCLUDED.ended_at, telco.calls.ended_at),
                duration_seconds = COALESCE(EXCLUDED.duration_seconds, telco.calls.duration_seconds),
                status = EXCLUDED.status,
                transcript = COALESCE(NULLIF(EXCLUDED.transcript, ''), telco.calls.transcript),
                full_transcript = COALESCE(NULLIF(EXCLUDED.full_transcript, ''), telco.calls.full_transcript),
                transcript_words = GREATEST(EXCLUDED.transcript_words, telco.calls.transcript_words),
                has_recording = EXCLUDED.has_recording OR telco.calls.has_recording,
                recording_url = COALESCE(NULLIF(EXCLUDED.recording_url, ''), telco.calls.recording_url),
                workspace_id = COALESCE(EXCLUDED.workspace_id, telco.calls.workspace_id),
                workspace_name = COALESCE(EXCLUDED.workspace_name, telco.calls.workspace_name),
                raw_data = EXCLUDED.raw_data
        """, (provider_id, c.get('call_id'), c.get('from_number') or None, c.get('to_number') or None,
              c.get('direction') or None, started_at, ended_at, duration_sec,
              c.get('call_status'), c.get('agent_id'), agent_name,
              transcript[:500] if transcript else None,
              transcript,
              transcript_words,
              bool(c.get('recording_url')),
              c.get('recording_url'),
              workspace_id, workspace_name,
              Json(c)))
        inserted = cur.rowcount > 0

    # Insert call analysis if present
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
                    call_sentiment = EXCLUDED.call_sentiment
            """, (c.get('call_id'), provider_id, c.get('agent_id'), agent_name,
                  analysis.get('call_summary', ''),
                  analysis.get('call_sentiment', ''),
                  analysis.get('user_sentiment', ''),
                  analysis.get('call_successful'),
                  analysis.get('in_voicemail'),
                  Json(analysis.get('custom_analysis_data', {})),
                  Json(c.get('latency', {})),
                  Json(analysis)))

    return inserted


def sync_retell(conn):
    """Sync all Retell data from ALL workspaces"""
    print("\n" + "=" * 60)
    print("SYNCING RETELL (MULTI-WORKSPACE)")
    print("=" * 60)

    if not RETELL_AVAILABLE:
        print("  [SKIP] retell-sdk not installed")
        return

    provider_id = get_provider_id(conn, "retell")

    # Get all active workspaces
    workspaces = get_retell_workspaces(conn)
    if not workspaces:
        # Fallback to single API key from credentials
        api_key = load_retell_api_key()
        if api_key:
            workspaces = [{'workspace_id': 'ws_primary', 'workspace_name': 'Primary', 'api_key': api_key}]
        else:
            print("  [SKIP] No Retell workspaces or API key configured")
            return

    print(f"  Found {len(workspaces)} workspace(s)")

    # Build global agent map from all workspaces
    agent_map = {}

    for ws in workspaces:
        print(f"\n  --- Workspace: {ws['workspace_name']} ---")

        try:
            api = RetellAPI(ws['api_key'])

            # Sync agents for this workspace
            agents = api.get_agents()
            for a in agents:
                agent_map[a['agent_id']] = a['agent_name']
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO telco.retell_agents
                        (agent_id, agent_name, voice_id, language, webhook_url, last_synced)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (agent_id) DO UPDATE SET
                            agent_name = EXCLUDED.agent_name, webhook_url = EXCLUDED.webhook_url, last_synced = NOW()
                    """, (a['agent_id'], a['agent_name'], a.get('voice_id'),
                          a.get('language'), a.get('webhook_url')))
            conn.commit()
            print(f"    [OK] {len(agents)} agents synced")

            # Sync phone numbers
            numbers = api.get_numbers()
            for n in numbers:
                phone = n.get("phone_number", "")
                agent_name_for_num = agent_map.get(n.get('inbound_agent_id'), '')
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
                          n.get('inbound_agent_id'), agent_name_for_num))
            conn.commit()
            print(f"    [OK] {len(numbers)} numbers synced")

            # Sync ALL calls with pagination
            print(f"    [Syncing calls...]")
            total, new = sync_retell_workspace_calls(
                conn, provider_id, ws['workspace_id'], ws['workspace_name'],
                ws['api_key'], agent_map
            )
            print(f"    [OK] {total} calls checked, {new} new records")

            # Update workspace stats
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE telco.retell_workspaces
                    SET last_synced = NOW(),
                        total_calls = (SELECT COUNT(*) FROM telco.calls WHERE workspace_id = %s)
                    WHERE workspace_id = %s
                """, (ws['workspace_id'], ws['workspace_id']))
            conn.commit()

        except Exception as e:
            print(f"    [ERROR] {e}")
            continue

    # Sync shared resources from primary workspace
    api_key = load_retell_api_key()
    if api_key:
        api = RetellAPI(api_key)

        # Knowledge Bases
        print("\n[Knowledge Bases]")
        kbs = api.get_knowledge_bases()
        if kbs:
            count = 0
            for kb in kbs:
                kb_id = kb.get('knowledge_base_id', kb.get('id', ''))
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO telco.knowledge_bases
                        (provider_id, kb_id, kb_name, description, last_synced)
                        VALUES (%s, %s, %s, %s, NOW())
                        ON CONFLICT (kb_id) DO UPDATE SET
                            kb_name = EXCLUDED.kb_name, last_synced = NOW()
                    """, (provider_id, kb_id, kb.get('knowledge_base_name', kb.get('name', '')),
                          kb.get('description', '')))
                count += 1
            conn.commit()
            print(f"  [OK] {count} knowledge bases synced")

        # LLM Configs
        print("\n[LLM Configurations]")
        llms = api.get_llms()
        if llms:
            count = 0
            for llm in llms:
                llm_id = llm.get('llm_id', llm.get('id', ''))
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO telco.llm_configs
                        (provider_id, llm_id, llm_name, model, temperature, metadata, last_synced)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (llm_id) DO UPDATE SET
                            llm_name = EXCLUDED.llm_name, last_synced = NOW()
                    """, (provider_id, llm_id, llm.get('llm_name', ''),
                          llm.get('model', ''), llm.get('general_temperature'),
                          Json(llm)))
                count += 1
            conn.commit()
            print(f"  [OK] {count} LLM configs synced")

        # Voice Configs
        print("\n[Voice Configurations]")
        voices = api.get_voices()
        if voices:
            count = 0
            for v in voices:
                voice_id = v.get('voice_id', v.get('id', ''))
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO telco.voice_configs
                        (provider_id, voice_id, voice_name, provider_voice, language, gender, accent, metadata, last_synced)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (voice_id) DO UPDATE SET
                            voice_name = EXCLUDED.voice_name, last_synced = NOW()
                    """, (provider_id, voice_id, v.get('voice_name', ''),
                          v.get('provider', ''), v.get('language', ''),
                          v.get('gender', ''), v.get('accent', ''), Json(v)))
                count += 1
            conn.commit()
            print(f"  [OK] {count} voices synced")

        # Concurrency Stats
        print("\n[Concurrency Stats]")
        conc = api.get_concurrency()
        if conc:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO telco.concurrency_stats
                    (provider_id, current_concurrent, max_concurrent, calls_in_progress, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                """, (provider_id, conc.get('current_concurrency', 0),
                      conc.get('concurrency_limit', 0),
                      conc.get('current_concurrency', 0), Json(conc)))
            conn.commit()
            print(f"  [OK] Concurrency: {conc.get('current_concurrency', 0)}/{conc.get('concurrency_limit', 0)}")
        else:
            print("  [INFO] Concurrency API not available")


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("TELCO WAREHOUSE - EXPANDED SYNC")
    print("Pulling from Zadarma, Telnyx, and Retell")
    print("=" * 60)

    try:
        conn = get_db_connection()
        print(f"\n[OK] Connected to {DB_CONFIG['host']}")
    except Exception as e:
        print(f"[ERROR] Database connection: {e}")
        return

    try:
        sync_zadarma(conn)
        sync_telnyx(conn)
        sync_retell(conn)

        # Summary
        print("\n" + "=" * 60)
        print("SYNC COMPLETE - Summary")
        print("=" * 60)

        tables = [
            ("Phone Numbers", "telco.phone_numbers"),
            ("Calls/CDRs", "telco.calls"),
            ("Call Analysis", "telco.call_analysis"),
            ("Messages/SMS", "telco.messages"),
            ("Recordings", "telco.recordings"),
            ("SIP Accounts", "telco.sip_accounts"),
            ("FQDN Connections", "telco.fqdn_connections"),
            ("Voice Configs", "telco.voice_configs"),
            ("LLM Configs", "telco.llm_configs"),
            ("Knowledge Bases", "telco.knowledge_bases"),
            ("Retell Agents", "telco.retell_agents"),
            ("Balance Snapshots", "telco.balance_snapshots"),
        ]

        with conn.cursor() as cur:
            for name, table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"  {name}: {count}")

        print("\n[OK] Expanded sync complete!")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
