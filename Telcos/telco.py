#!/usr/bin/env python3
"""
Telco Manager - Unified view of Telnyx, Zadarma, and Retell phone numbers
"""

import os
import sys
import hashlib
import hmac
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# Try to import Retell SDK
try:
    from retell import Retell
    RETELL_AVAILABLE = True
except ImportError:
    RETELL_AVAILABLE = False

# Try to import psycopg2 for database access
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    DIM = '\033[2m'


def load_credentials() -> Dict[str, str]:
    """Load credentials from .credentials file"""
    cred_file = Path(__file__).parent / ".credentials"
    creds = {}
    if cred_file.exists():
        with open(cred_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    creds[key.strip()] = value.strip()
    return creds


def load_retell_api_key() -> Optional[str]:
    """Load Retell API key from standard locations"""
    search_paths = [
        Path(__file__).parent / ".credentials",
        Path.home() / "Downloads" / "Retell_API_Key.txt",
        Path.home() / "Downloads" / "CC" / "retell" / "Retell_API_Key.txt",
    ]

    # First check .credentials
    creds = load_credentials()
    if creds.get("RETELL_API_KEY"):
        return creds["RETELL_API_KEY"]

    # Then check Retell_API_Key.txt files
    for path in search_paths[1:]:
        if path.exists():
            try:
                with open(path) as f:
                    key = f.read().strip()
                    key = key.replace("API Key:", "").replace("key:", "").strip()
                    if key:
                        return key
            except:
                pass
    return None


# ============================================================================
# ZADARMA API
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

    def get_balance(self) -> dict:
        return self.request("/v1/info/balance/")

    def get_numbers(self) -> dict:
        return self.request("/v1/direct_numbers/")

    def get_sip_accounts(self) -> dict:
        return self.request("/v1/sip/")

    def get_statistics(self, start: str = None, end: str = None) -> dict:
        """Get call statistics. Dates in format YYYY-MM-DD"""
        if not start:
            start = datetime.now().strftime("%Y-%m-01")
        if not end:
            end = datetime.now().strftime("%Y-%m-%d")
        return self.request("/v1/statistics/", {"start": start, "end": end})


# ============================================================================
# TELNYX API
# ============================================================================

class TelnyxAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.telnyx.com/v2"

    def request(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}{endpoint}"

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        else:
            response = requests.request(method, url, headers=headers, json=data)

        return response.json()

    def get_balance(self) -> dict:
        return self.request("/balance")

    def get_phone_numbers(self) -> dict:
        return self.request("/phone_numbers")

    def get_fqdn_connections(self) -> dict:
        return self.request("/fqdn_connections")

    def get_fqdns(self) -> dict:
        return self.request("/fqdns")

    def get_outbound_voice_profiles(self) -> dict:
        return self.request("/outbound_voice_profiles")

    def get_messaging_profiles(self) -> dict:
        return self.request("/messaging_profiles")


# ============================================================================
# RETELL API
# ============================================================================

class RetellAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = Retell(api_key=api_key) if RETELL_AVAILABLE else None

    def get_phone_numbers(self) -> List[dict]:
        if not self.client:
            return []
        try:
            numbers = self.client.phone_number.list()
            return [self._number_to_dict(n) for n in numbers]
        except Exception as e:
            print(f"{Colors.RED}Retell API error: {e}{Colors.RESET}")
            return []

    def get_agents(self) -> List[dict]:
        if not self.client:
            return []
        try:
            agents = self.client.agent.list()
            return [self._agent_to_dict(a) for a in agents]
        except Exception as e:
            print(f"{Colors.RED}Retell API error: {e}{Colors.RESET}")
            return []

    def _number_to_dict(self, n) -> dict:
        return {
            "phone_number": getattr(n, 'phone_number', ''),
            "phone_number_pretty": getattr(n, 'phone_number_pretty', ''),
            "phone_number_type": getattr(n, 'phone_number_type', ''),
            "nickname": getattr(n, 'nickname', ''),
            "inbound_agent_id": getattr(n, 'inbound_agent_id', None),
            "outbound_agent_id": getattr(n, 'outbound_agent_id', None),
        }

    def _agent_to_dict(self, a) -> dict:
        return {
            "agent_id": getattr(a, 'agent_id', ''),
            "agent_name": getattr(a, 'agent_name', ''),
            "voice_id": getattr(a, 'voice_id', ''),
            "language": getattr(a, 'language', ''),
        }


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def print_header(text: str):
    width = 70
    print()
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * width}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  {text}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * width}{Colors.RESET}")


def print_subheader(text: str):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}[{text}]{Colors.RESET}")


def print_table(headers: List[str], rows: List[List[str]], col_widths: List[int] = None):
    """Print a formatted table"""
    if not col_widths:
        col_widths = [max(len(str(row[i])) for row in [headers] + rows) + 2 for i in range(len(headers))]

    # Header
    header_line = "  ".join(f"{Colors.BOLD}{h:<{col_widths[i]}}{Colors.RESET}" for i, h in enumerate(headers))
    print(f"  {header_line}")
    print(f"  {'-' * sum(col_widths)}")

    # Rows
    for row in rows:
        row_line = "  ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row)))
        print(f"  {row_line}")


def format_phone(number: str) -> str:
    """Format phone number for display"""
    if not number:
        return ""
    # Remove + prefix for consistency
    n = number.lstrip('+')
    if n.startswith('61'):
        # Australian format
        n = n[2:]
        if len(n) == 9:
            return f"+61 {n[0]} {n[1:5]} {n[5:]}"
    return number


def truncate(s: str, length: int) -> str:
    """Truncate string with ellipsis"""
    if not s:
        return ""
    return s[:length-2] + ".." if len(s) > length else s


# ============================================================================
# MENU SECTIONS
# ============================================================================

def show_zadarma_info(api: ZadarmaAPI):
    print_header("ZADARMA")

    # Balance
    print_subheader("Account Balance")
    balance = api.get_balance()
    if balance.get("status") == "success":
        print(f"  Balance: {Colors.GREEN}${balance.get('balance', '?')} {balance.get('currency', 'USD')}{Colors.RESET}")
    else:
        print(f"  {Colors.RED}Error: {balance.get('message', 'Unknown error')}{Colors.RESET}")

    # Phone Numbers
    print_subheader("Phone Numbers")
    numbers = api.get_numbers()
    if numbers.get("status") == "success":
        info = numbers.get("info", [])
        if info:
            rows = []
            for n in info:
                status_color = Colors.GREEN if n.get('status') == 'on' else Colors.RED
                rows.append([
                    format_phone(n.get('number', '')),
                    n.get('description', ''),
                    f"{status_color}{n.get('status', '?')}{Colors.RESET}",
                    truncate(n.get('sip', ''), 25),
                    f"${n.get('monthly_fee', '?')}/mo"
                ])
            print_table(["Number", "City", "Status", "SIP Destination", "Cost"], rows, [18, 12, 8, 27, 10])
        else:
            print("  No phone numbers found")

    # Monthly total
    if numbers.get("status") == "success":
        total = sum(n.get('monthly_fee', 0) for n in numbers.get('info', []))
        print(f"\n  {Colors.DIM}Total monthly: ${total} USD{Colors.RESET}")


def show_telnyx_info(api: TelnyxAPI):
    print_header("TELNYX")

    # Balance
    print_subheader("Account Balance")
    balance = api.get_balance()
    if "data" in balance:
        b = balance["data"]
        print(f"  Balance: {Colors.GREEN}${b.get('balance', '?')} {b.get('currency', 'USD')}{Colors.RESET}")
        print(f"  Credit Limit: ${b.get('credit_limit', '0')}")
    else:
        print(f"  {Colors.RED}Error: {balance.get('errors', [{}])[0].get('detail', 'Unknown')}{Colors.RESET}")

    # Phone Numbers
    print_subheader("Phone Numbers")
    numbers = api.get_phone_numbers()
    if "data" in numbers:
        data = numbers["data"]
        if data:
            rows = []
            for n in data:
                status_color = Colors.GREEN if n.get('status') == 'active' else Colors.RED
                rows.append([
                    format_phone(n.get('phone_number', '')),
                    f"{status_color}{n.get('status', '?')}{Colors.RESET}",
                    truncate(n.get('connection_name', 'None'), 25),
                    n.get('phone_number_type', ''),
                ])
            print_table(["Number", "Status", "Connection", "Type"], rows, [18, 10, 27, 10])
        else:
            print("  No phone numbers found")

    # SIP Connections
    print_subheader("SIP Connections (FQDN)")
    connections = api.get_fqdn_connections()
    if "data" in connections:
        for conn in connections["data"]:
            active = f"{Colors.GREEN}Active{Colors.RESET}" if conn.get('active') else f"{Colors.RED}Inactive{Colors.RESET}"
            print(f"  {Colors.BOLD}{conn.get('connection_name', '?')}{Colors.RESET} [{active}]")
            print(f"    ID: {conn.get('id')}")
            print(f"    Transport: {conn.get('transport_protocol', '?')}")
            print(f"    SIP Region: {conn.get('inbound', {}).get('sip_region', '?')}")

            # Get FQDNs for this connection
            fqdns = api.get_fqdns()
            if "data" in fqdns:
                for fqdn in fqdns["data"]:
                    if str(fqdn.get('connection_id')) == str(conn.get('id')):
                        print(f"    FQDN: {Colors.CYAN}{fqdn.get('fqdn')}{Colors.RESET}")


def show_retell_info(api: RetellAPI):
    print_header("RETELL AI")

    if not RETELL_AVAILABLE:
        print(f"  {Colors.RED}retell-sdk not installed. Run: pip install retell-sdk{Colors.RESET}")
        return

    # Get agents first (we'll need them for mapping)
    agents = api.get_agents()
    agent_map = {a['agent_id']: a['agent_name'] for a in agents}

    # Phone Numbers with Agent mapping
    print_subheader("Phone Numbers & Agent Assignments")
    numbers = api.get_phone_numbers()

    if numbers:
        rows = []
        for n in numbers:
            inbound = n.get('inbound_agent_id')
            outbound = n.get('outbound_agent_id')

            inbound_name = truncate(agent_map.get(inbound, inbound or 'None'), 20)
            outbound_name = truncate(agent_map.get(outbound, outbound or 'None'), 20)

            # Color code based on assignment
            if inbound:
                inbound_display = f"{Colors.GREEN}{inbound_name}{Colors.RESET}"
            else:
                inbound_display = f"{Colors.DIM}None{Colors.RESET}"

            if outbound:
                outbound_display = f"{Colors.GREEN}{outbound_name}{Colors.RESET}"
            else:
                outbound_display = f"{Colors.DIM}None{Colors.RESET}"

            rows.append([
                format_phone(n.get('phone_number', '')),
                n.get('phone_number_type', ''),
                truncate(n.get('nickname', ''), 15),
                inbound_display,
                outbound_display,
            ])

        print_table(["Number", "Type", "Nickname", "Inbound Agent", "Outbound Agent"],
                   rows, [18, 12, 17, 22, 22])
    else:
        print("  No phone numbers found")

    # Agents with numbers assigned
    print_subheader("Agents with Phone Numbers")
    if agents:
        # Only show agents that have at least one number
        active_agents = []
        seen_ids = set()
        for a in agents:
            agent_id = a.get('agent_id', '')
            if agent_id in seen_ids:
                continue
            seen_ids.add(agent_id)

            inbound_count = sum(1 for n in numbers if n.get('inbound_agent_id') == agent_id)
            outbound_count = sum(1 for n in numbers if n.get('outbound_agent_id') == agent_id)

            if inbound_count > 0 or outbound_count > 0:
                active_agents.append({
                    'name': a.get('agent_name', ''),
                    'id': agent_id,
                    'voice': a.get('voice_id', ''),
                    'inbound': inbound_count,
                    'outbound': outbound_count
                })

        if active_agents:
            rows = []
            for a in active_agents:
                rows.append([
                    truncate(a['name'], 35),
                    a['id'][:24] + "...",
                    f"{a['inbound']} in / {a['outbound']} out"
                ])
            print_table(["Agent Name", "Agent ID", "Numbers"], rows, [37, 28, 15])
        else:
            print("  No agents have phone numbers assigned")

        print(f"\n  {Colors.DIM}Total agents in Retell: {len(seen_ids)} (showing only those with numbers){Colors.RESET}")
    else:
        print("  No agents found")


def show_unified_view(zadarma: ZadarmaAPI, telnyx: TelnyxAPI, retell: RetellAPI):
    """Show all phone numbers from all providers in one view"""
    print_header("UNIFIED PHONE NUMBER VIEW")

    all_numbers = []

    # Zadarma numbers
    zad_numbers = zadarma.get_numbers()
    if zad_numbers.get("status") == "success":
        for n in zad_numbers.get("info", []):
            all_numbers.append({
                "number": f"+{n.get('number', '')}",
                "provider": "Zadarma",
                "city": n.get('description', ''),
                "status": n.get('status', ''),
                "destination": truncate(n.get('sip', ''), 30),
                "retell_agent": None
            })

    # Telnyx numbers
    tel_numbers = telnyx.get_phone_numbers()
    if "data" in tel_numbers:
        for n in tel_numbers["data"]:
            all_numbers.append({
                "number": n.get('phone_number', ''),
                "provider": "Telnyx",
                "city": "",
                "status": n.get('status', ''),
                "destination": n.get('connection_name', ''),
                "retell_agent": None
            })

    # Get Retell mappings
    if RETELL_AVAILABLE:
        retell_numbers = retell.get_phone_numbers()
        agents = retell.get_agents()
        agent_map = {a['agent_id']: a['agent_name'] for a in agents}

        for rn in retell_numbers:
            phone = rn.get('phone_number', '')
            agent_id = rn.get('inbound_agent_id')
            agent_name = agent_map.get(agent_id, '')

            # Find matching number and update
            for n in all_numbers:
                if n['number'] == phone or n['number'].replace('+', '') == phone.replace('+', ''):
                    n['retell_agent'] = agent_name
                    n['destination'] = f"Retell: {truncate(agent_name, 20)}" if agent_name else n['destination']

    # Display
    if all_numbers:
        rows = []
        for n in all_numbers:
            status_color = Colors.GREEN if n['status'] in ['on', 'active'] else Colors.YELLOW
            provider_color = Colors.CYAN if n['provider'] == 'Telnyx' else Colors.MAGENTA

            rows.append([
                format_phone(n['number']),
                f"{provider_color}{n['provider']}{Colors.RESET}",
                n['city'] or '-',
                f"{status_color}{n['status']}{Colors.RESET}",
                n['destination'] or '-'
            ])

        print_table(["Number", "Provider", "City", "Status", "Destination/Agent"],
                   rows, [18, 10, 12, 8, 32])

        print(f"\n  {Colors.DIM}Total: {len(all_numbers)} numbers across all providers{Colors.RESET}")


def get_db_connection(creds: Dict[str, str]):
    """Get database connection from credentials"""
    if not POSTGRES_AVAILABLE:
        return None
    try:
        return psycopg2.connect(
            host=creds.get("POSTGRES_HOST", "96.47.238.189"),
            port=int(creds.get("POSTGRES_PORT", 5432)),
            database=creds.get("POSTGRES_DB", "telco_warehouse"),
            user=creds.get("POSTGRES_USER", "telco_sync"),
            password=creds.get("POSTGRES_PASSWORD", "TelcoSync2024!")
        )
    except Exception as e:
        print(f"{Colors.RED}Database connection error: {e}{Colors.RESET}")
        return None


def show_warehouse_summary(creds: Dict[str, str]):
    """Show data warehouse with expandable sections - 5 rows default, click for 50"""
    print_header("TELCO DATA WAREHOUSE")

    if not POSTGRES_AVAILABLE:
        print(f"  {Colors.RED}psycopg2 not installed. Run: pip install psycopg2-binary{Colors.RESET}")
        return

    conn = get_db_connection(creds)
    if not conn:
        return

    # Track which sections to expand
    expanded_sections = set()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header("TELCO DATA WAREHOUSE")

        try:
            cur = conn.cursor()

            # Database info
            print_subheader("Database Connection")
            print(f"  Host: {Colors.CYAN}{creds.get('POSTGRES_HOST', '96.47.238.189')}{Colors.RESET}")
            print(f"  Database: {Colors.CYAN}telco_warehouse{Colors.RESET}")

            # Section definitions with queries
            sections = [
                {
                    "key": "1",
                    "name": "Phone Numbers",
                    "query": """
                        SELECT pn.phone_number, p.name, pn.status, pn.city, pn.nickname,
                               pn.retell_agent_name, pn.last_synced
                        FROM telco.phone_numbers pn
                        JOIN telco.providers p ON pn.provider_id = p.provider_id
                        ORDER BY pn.last_synced DESC NULLS LAST, pn.id DESC
                    """,
                    "headers": ["Number", "Provider", "Status", "Location", "Agent", "Synced"],
                    "widths": [18, 10, 8, 14, 20, 12],
                    "format": lambda r: [
                        format_phone(r[0] or ""),
                        f"{Colors.CYAN if r[1]=='telnyx' else Colors.MAGENTA if r[1]=='zadarma' else Colors.BLUE}{r[1]}{Colors.RESET}",
                        f"{Colors.GREEN if r[2] in ['on','active'] else Colors.YELLOW}{r[2] or '?'}{Colors.RESET}",
                        truncate(r[3] or r[4] or "-", 12),
                        truncate(r[5], 18) if r[5] else "-",
                        r[6].strftime("%m-%d %H:%M") if r[6] else "-"
                    ]
                },
                {
                    "key": "2",
                    "name": "Calls/CDRs",
                    "query": """
                        SELECT c.started_at, p.name, c.from_number, c.to_number,
                               c.duration_seconds, c.status, c.retell_agent_name, c.cost
                        FROM telco.calls c
                        JOIN telco.providers p ON c.provider_id = p.provider_id
                        ORDER BY c.started_at DESC NULLS LAST
                    """,
                    "headers": ["Time", "Provider", "From", "To", "Dur", "Status", "Agent", "Cost"],
                    "widths": [12, 10, 16, 16, 6, 10, 18, 8],
                    "format": lambda r: [
                        r[0].strftime("%m-%d %H:%M") if r[0] else "?",
                        f"{Colors.CYAN if r[1]=='telnyx' else Colors.MAGENTA if r[1]=='zadarma' else Colors.BLUE}{r[1]}{Colors.RESET}",
                        format_phone(r[2] or ""),
                        format_phone(r[3] or ""),
                        f"{r[4]}s" if r[4] else "-",
                        f"{Colors.GREEN if r[5]=='ended' else Colors.YELLOW}{r[5] or '?'}{Colors.RESET}",
                        truncate(r[6], 16) if r[6] else "-",
                        f"${r[7]:.2f}" if r[7] else "-"
                    ]
                },
                {
                    "key": "3",
                    "name": "Call Analysis (Retell)",
                    "query": """
                        SELECT ca.synced_at, ca.agent_name, ca.call_sentiment, ca.user_sentiment,
                               ca.call_successful, ca.in_voicemail, ca.call_summary
                        FROM telco.call_analysis ca
                        ORDER BY ca.synced_at DESC
                    """,
                    "headers": ["Time", "Agent", "Call Sent.", "User Sent.", "Success", "VM", "Summary"],
                    "widths": [12, 20, 10, 10, 8, 4, 30],
                    "format": lambda r: [
                        r[0].strftime("%m-%d %H:%M") if r[0] else "-",
                        truncate(r[1] or "-", 18),
                        f"{Colors.GREEN if r[2]=='positive' else Colors.RED if r[2]=='negative' else Colors.YELLOW}{r[2] or '-'}{Colors.RESET}",
                        f"{Colors.GREEN if r[3]=='positive' else Colors.RED if r[3]=='negative' else Colors.YELLOW}{r[3] or '-'}{Colors.RESET}",
                        f"{Colors.GREEN}Yes{Colors.RESET}" if r[4] else f"{Colors.RED}No{Colors.RESET}" if r[4] is False else "-",
                        "Y" if r[5] else "-",
                        truncate(r[6] or "-", 28)
                    ]
                },
                {
                    "key": "4",
                    "name": "Full Transcripts (Retell)",
                    "query": """
                        SELECT c.started_at, c.retell_agent_name, c.from_number, c.duration_seconds,
                               c.transcript_words, c.full_transcript
                        FROM telco.calls c
                        JOIN telco.providers p ON c.provider_id = p.provider_id
                        WHERE p.name = 'retell' AND c.full_transcript IS NOT NULL
                        ORDER BY c.started_at DESC
                    """,
                    "headers": ["Time", "Agent", "Caller", "Dur", "Words", "Transcript Preview"],
                    "widths": [12, 18, 16, 6, 6, 35],
                    "format": lambda r: [
                        r[0].strftime("%m-%d %H:%M") if r[0] else "-",
                        truncate(r[1] or "-", 16),
                        format_phone(r[2] or ""),
                        f"{r[3]}s" if r[3] else "-",
                        str(r[4] or 0),
                        truncate(r[5] or "-", 33) if r[5] else "-"
                    ]
                },
                {
                    "key": "5",
                    "name": "SIP Accounts (Zadarma)",
                    "query": """
                        SELECT s.sip_id, s.sip_name, s.caller_id, s.status, s.lines, s.last_synced
                        FROM telco.sip_accounts s
                        JOIN telco.providers p ON s.provider_id = p.provider_id
                        WHERE p.name = 'zadarma'
                        ORDER BY s.last_synced DESC NULLS LAST
                    """,
                    "headers": ["SIP ID", "Name", "Caller ID", "Status", "Lines", "Synced"],
                    "widths": [12, 20, 16, 10, 6, 12],
                    "format": lambda r: [
                        r[0] or "-",
                        truncate(r[1] or "-", 18),
                        r[2] or "-",
                        f"{Colors.GREEN}{r[3]}{Colors.RESET}" if r[3] == 'active' else r[3] or "-",
                        str(r[4] or 1),
                        r[5].strftime("%m-%d %H:%M") if r[5] else "-"
                    ]
                },
                {
                    "key": "6",
                    "name": "Recordings",
                    "query": """
                        SELECT r.created_at, p.name, r.duration_seconds, r.format,
                               r.recording_url, r.synced_at
                        FROM telco.recordings r
                        JOIN telco.providers p ON r.provider_id = p.provider_id
                        ORDER BY r.created_at DESC NULLS LAST
                    """,
                    "headers": ["Created", "Provider", "Duration", "Format", "URL"],
                    "widths": [12, 10, 10, 8, 50],
                    "format": lambda r: [
                        r[0].strftime("%m-%d %H:%M") if r[0] else "-",
                        f"{Colors.MAGENTA}{r[1]}{Colors.RESET}",
                        f"{r[2]}s" if r[2] else "-",
                        r[3] or "-",
                        truncate(r[4] or "-", 48)
                    ]
                },
                {
                    "key": "7",
                    "name": "SMS Messages",
                    "query": """
                        SELECT m.sent_at, p.name, m.from_number, m.to_number,
                               m.direction, m.status, m.body, m.cost
                        FROM telco.messages m
                        JOIN telco.providers p ON m.provider_id = p.provider_id
                        ORDER BY m.sent_at DESC NULLS LAST
                    """,
                    "headers": ["Sent", "Provider", "From", "To", "Dir", "Status", "Body", "Cost"],
                    "widths": [12, 10, 16, 16, 6, 10, 25, 8],
                    "format": lambda r: [
                        r[0].strftime("%m-%d %H:%M") if r[0] else "-",
                        f"{Colors.CYAN}{r[1]}{Colors.RESET}",
                        format_phone(r[2] or ""),
                        format_phone(r[3] or ""),
                        r[4] or "-",
                        r[5] or "-",
                        truncate(r[6] or "-", 23),
                        f"${r[7]:.3f}" if r[7] else "-"
                    ]
                },
                {
                    "key": "8",
                    "name": "FQDN Connections (Telnyx SIP)",
                    "query": """
                        SELECT f.connection_name, f.fqdn, f.is_active, f.transport_protocol,
                               f.sip_region, f.last_synced
                        FROM telco.fqdn_connections f
                        ORDER BY f.last_synced DESC NULLS LAST
                    """,
                    "headers": ["Connection", "FQDN", "Active", "Transport", "Region", "Synced"],
                    "widths": [25, 30, 8, 12, 15, 12],
                    "format": lambda r: [
                        truncate(r[0] or "-", 23),
                        truncate(r[1] or "-", 28),
                        f"{Colors.GREEN}Yes{Colors.RESET}" if r[2] else f"{Colors.RED}No{Colors.RESET}",
                        r[3] or "-",
                        r[4] or "-",
                        r[5].strftime("%m-%d %H:%M") if r[5] else "-"
                    ]
                },
                {
                    "key": "9",
                    "name": "Outbound Voice Profiles (Telnyx)",
                    "query": """
                        SELECT o.profile_name, o.is_enabled, o.traffic_type, o.service_plan,
                               o.daily_spend_limit, o.last_synced
                        FROM telco.outbound_profiles o
                        ORDER BY o.last_synced DESC NULLS LAST
                    """,
                    "headers": ["Profile Name", "Enabled", "Traffic Type", "Plan", "Spend Limit", "Synced"],
                    "widths": [25, 8, 16, 15, 12, 12],
                    "format": lambda r: [
                        truncate(r[0] or "-", 23),
                        f"{Colors.GREEN}Yes{Colors.RESET}" if r[1] else f"{Colors.RED}No{Colors.RESET}",
                        r[2] or "-",
                        r[3] or "-",
                        f"${r[4]:.2f}" if r[4] else "None",
                        r[5].strftime("%m-%d %H:%M") if r[5] else "-"
                    ]
                },
                {
                    "key": "A",
                    "name": "Messaging Profiles (Telnyx)",
                    "query": """
                        SELECT m.profile_name, m.is_enabled, m.number_pool_enabled, m.webhook_url, m.last_synced
                        FROM telco.messaging_profiles m
                        ORDER BY m.last_synced DESC NULLS LAST
                    """,
                    "headers": ["Profile Name", "Enabled", "Pool", "Webhook URL", "Synced"],
                    "widths": [25, 8, 6, 35, 12],
                    "format": lambda r: [
                        truncate(r[0] or "-", 23),
                        f"{Colors.GREEN}Yes{Colors.RESET}" if r[1] else f"{Colors.RED}No{Colors.RESET}",
                        "Y" if r[2] else "N",
                        truncate(r[3] or "-", 33),
                        r[4].strftime("%m-%d %H:%M") if r[4] else "-"
                    ]
                },
                {
                    "key": "B",
                    "name": "SIP Credentials (Telnyx)",
                    "query": """
                        SELECT s.sip_username, s.connection_name, s.is_active, s.created_at_provider, s.last_synced
                        FROM telco.sip_credentials s
                        ORDER BY s.last_synced DESC NULLS LAST
                    """,
                    "headers": ["SIP Username", "Connection", "Active", "Created", "Synced"],
                    "widths": [20, 25, 8, 12, 12],
                    "format": lambda r: [
                        r[0] or "-",
                        truncate(r[1] or "-", 23),
                        f"{Colors.GREEN}Yes{Colors.RESET}" if r[2] else f"{Colors.RED}No{Colors.RESET}",
                        r[3].strftime("%m-%d %H:%M") if r[3] else "-",
                        r[4].strftime("%m-%d %H:%M") if r[4] else "-"
                    ]
                },
                {
                    "key": "C",
                    "name": "Number Orders (Telnyx)",
                    "query": """
                        SELECT n.order_id, n.order_type, n.status, n.customer_reference,
                               n.requirements_met, n.ordered_at
                        FROM telco.number_orders n
                        ORDER BY n.ordered_at DESC NULLS LAST
                    """,
                    "headers": ["Order ID", "Type", "Status", "Reference", "Reqs Met", "Ordered"],
                    "widths": [25, 15, 12, 20, 8, 12],
                    "format": lambda r: [
                        truncate(r[0] or "-", 23),
                        r[1] or "-",
                        f"{Colors.GREEN if r[2]=='success' else Colors.YELLOW}{r[2] or '-'}{Colors.RESET}",
                        truncate(r[3] or "-", 18),
                        f"{Colors.GREEN}Yes{Colors.RESET}" if r[4] else f"{Colors.RED}No{Colors.RESET}" if r[4] is False else "-",
                        r[5].strftime("%m-%d %H:%M") if r[5] else "-"
                    ]
                },
                {
                    "key": "D",
                    "name": "Knowledge Bases (Retell)",
                    "query": """
                        SELECT k.kb_id, k.kb_name, k.description, k.source_count, k.last_synced
                        FROM telco.knowledge_bases k
                        ORDER BY k.last_synced DESC NULLS LAST
                    """,
                    "headers": ["KB ID", "Name", "Description", "Sources", "Synced"],
                    "widths": [25, 25, 30, 8, 12],
                    "format": lambda r: [
                        truncate(r[0] or "-", 23),
                        truncate(r[1] or "-", 23),
                        truncate(r[2] or "-", 28),
                        str(r[3] or 0),
                        r[4].strftime("%m-%d %H:%M") if r[4] else "-"
                    ]
                },
                {
                    "key": "E",
                    "name": "LLM Configurations (Retell)",
                    "query": """
                        SELECT l.llm_id, l.llm_name, l.model, l.temperature, l.last_synced
                        FROM telco.llm_configs l
                        ORDER BY l.last_synced DESC NULLS LAST
                    """,
                    "headers": ["LLM ID", "Name", "Model", "Temp", "Synced"],
                    "widths": [28, 25, 20, 6, 12],
                    "format": lambda r: [
                        truncate(r[0] or "-", 26),
                        truncate(r[1] or "-", 23),
                        r[2] or "-",
                        f"{r[3]:.1f}" if r[3] else "-",
                        r[4].strftime("%m-%d %H:%M") if r[4] else "-"
                    ]
                },
                {
                    "key": "F",
                    "name": "Voice Configs (Retell)",
                    "query": """
                        SELECT v.voice_id, v.voice_name, v.provider_voice, v.language, v.gender, v.accent
                        FROM telco.voice_configs v
                        ORDER BY v.last_synced DESC NULLS LAST
                    """,
                    "headers": ["Voice ID", "Name", "Provider", "Language", "Gender", "Accent"],
                    "widths": [20, 22, 15, 10, 8, 15],
                    "format": lambda r: [
                        truncate(r[0] or "-", 18),
                        truncate(r[1] or "-", 20),
                        r[2] or "-",
                        r[3] or "-",
                        r[4] or "-",
                        truncate(r[5] or "-", 13)
                    ]
                },
                {
                    "key": "G",
                    "name": "Retell Agents",
                    "query": """
                        SELECT agent_id, agent_name, voice_id, language, webhook_url, last_synced
                        FROM telco.retell_agents
                        ORDER BY last_synced DESC NULLS LAST
                    """,
                    "headers": ["Agent ID", "Name", "Voice", "Lang", "Webhook", "Synced"],
                    "widths": [25, 30, 15, 6, 20, 12],
                    "format": lambda r: [
                        truncate(r[0] or "-", 23),
                        truncate(r[1] or "-", 28),
                        truncate(r[2] or "-", 13),
                        r[3] or "-",
                        truncate(r[4] or "-", 18) if r[4] else "-",
                        r[5].strftime("%m-%d %H:%M") if r[5] else "-"
                    ]
                },
                {
                    "key": "H",
                    "name": "Balance Snapshots",
                    "query": """
                        SELECT b.snapshot_at, p.name, b.balance, b.currency, b.credit_limit
                        FROM telco.balance_snapshots b
                        JOIN telco.providers p ON b.provider_id = p.provider_id
                        ORDER BY b.snapshot_at DESC
                    """,
                    "headers": ["Snapshot", "Provider", "Balance", "Currency", "Credit"],
                    "widths": [18, 12, 12, 10, 12],
                    "format": lambda r: [
                        r[0].strftime("%Y-%m-%d %H:%M") if r[0] else "-",
                        f"{Colors.CYAN if r[1]=='telnyx' else Colors.MAGENTA if r[1]=='zadarma' else Colors.BLUE}{r[1]}{Colors.RESET}",
                        f"{Colors.GREEN}${r[2]:.2f}{Colors.RESET}",
                        r[3] or "USD",
                        f"${r[4]:.2f}" if r[4] else "-"
                    ]
                },
                {
                    "key": "I",
                    "name": "Concurrency Stats (Retell)",
                    "query": """
                        SELECT c.snapshot_at, c.current_concurrent, c.max_concurrent, c.calls_in_progress
                        FROM telco.concurrency_stats c
                        ORDER BY c.snapshot_at DESC
                    """,
                    "headers": ["Snapshot", "Current", "Max", "In Progress"],
                    "widths": [20, 10, 10, 12],
                    "format": lambda r: [
                        r[0].strftime("%Y-%m-%d %H:%M") if r[0] else "-",
                        str(r[1] or 0),
                        str(r[2] or 0),
                        str(r[3] or 0)
                    ]
                },
            ]

            # Display all sections
            print_subheader("Data Sections (Press key to expand/collapse)")
            print()

            for section in sections:
                key = section["key"]
                name = section["name"]
                is_expanded = key in expanded_sections
                limit = 50 if is_expanded else 5

                # Get count
                try:
                    count_query = f"SELECT COUNT(*) FROM ({section['query']}) sub"
                    cur.execute(count_query)
                    total_count = cur.fetchone()[0]
                except:
                    total_count = 0

                # Section header
                expand_indicator = f"{Colors.GREEN}[-]{Colors.RESET}" if is_expanded else f"{Colors.YELLOW}[+]{Colors.RESET}"
                count_display = f"({total_count})" if total_count > 0 else f"{Colors.DIM}(0){Colors.RESET}"
                print(f"  {Colors.CYAN}{key}.{Colors.RESET} {expand_indicator} {name} {count_display}")

                if total_count > 0:
                    # Get data
                    cur.execute(f"{section['query']} LIMIT {limit}")
                    rows = []
                    for row in cur.fetchall():
                        try:
                            formatted = section["format"](row)
                            rows.append(formatted)
                        except Exception as e:
                            rows.append([str(e)] + ["-"] * (len(section["headers"]) - 1))

                    if rows:
                        print_table(section["headers"], rows, section["widths"])
                        if total_count > limit:
                            more = total_count - limit
                            print(f"       {Colors.DIM}... {more} more (press {key} to show all 50){Colors.RESET}")
                        elif is_expanded and total_count > 5:
                            print(f"       {Colors.DIM}(press {key} to collapse){Colors.RESET}")
                    print()

            # Menu
            print(f"\n  {Colors.BOLD}Options:{Colors.RESET}")
            print(f"    Press 1-9, A-I to expand/collapse a section")
            print(f"    Press {Colors.CYAN}Q{Colors.RESET} to return to main menu")
            print()

            choice = input(f"  {Colors.BOLD}Select: {Colors.RESET}").strip().upper()

            if choice == 'Q' or choice == '':
                break
            elif choice in [s["key"] for s in sections]:
                if choice in expanded_sections:
                    expanded_sections.remove(choice)
                else:
                    expanded_sections.add(choice)

        except Exception as e:
            print(f"{Colors.RED}Error querying database: {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            break

    conn.close()


def show_menu():
    """Display main menu"""
    print()
    print(f"{Colors.BOLD}TELCO MANAGER{Colors.RESET}")
    print(f"{Colors.DIM}Unified view of Zadarma, Telnyx & Retell{Colors.RESET}")
    print()
    print(f"  {Colors.CYAN}1.{Colors.RESET} Zadarma Overview")
    print(f"  {Colors.CYAN}2.{Colors.RESET} Telnyx Overview")
    print(f"  {Colors.CYAN}3.{Colors.RESET} Retell AI Overview")
    print(f"  {Colors.CYAN}4.{Colors.RESET} Unified Number View (All Providers)")
    print(f"  {Colors.CYAN}5.{Colors.RESET} Data Warehouse (PostgreSQL)")
    print()
    print(f"  {Colors.CYAN}A.{Colors.RESET} Show All")
    print(f"  {Colors.CYAN}S.{Colors.RESET} Sync Data (Pull from APIs)")
    print(f"  {Colors.CYAN}R.{Colors.RESET} Refresh")
    print(f"  {Colors.CYAN}Q.{Colors.RESET} Quit")
    print()


def main():
    # Load credentials
    creds = load_credentials()

    # Initialize APIs
    zadarma = None
    telnyx = None
    retell = None

    if creds.get("ZADARMA_API_KEY") and creds.get("ZADARMA_API_SECRET"):
        zadarma = ZadarmaAPI(creds["ZADARMA_API_KEY"], creds["ZADARMA_API_SECRET"])
    else:
        print(f"{Colors.YELLOW}[WARN] Zadarma credentials not found in .credentials{Colors.RESET}")

    if creds.get("TELNYX_API_KEY"):
        telnyx = TelnyxAPI(creds["TELNYX_API_KEY"])
    else:
        print(f"{Colors.YELLOW}[WARN] Telnyx API key not found in .credentials{Colors.RESET}")

    retell_key = load_retell_api_key()
    if retell_key and RETELL_AVAILABLE:
        retell = RetellAPI(retell_key)
    elif not RETELL_AVAILABLE:
        print(f"{Colors.YELLOW}[WARN] retell-sdk not installed{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}[WARN] Retell API key not found{Colors.RESET}")

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_menu()

        choice = input(f"{Colors.BOLD}Select option: {Colors.RESET}").strip().lower()

        if choice == 'q':
            print(f"\n{Colors.CYAN}Goodbye!{Colors.RESET}\n")
            break

        elif choice == '1':
            if zadarma:
                show_zadarma_info(zadarma)
            else:
                print(f"{Colors.RED}Zadarma not configured{Colors.RESET}")

        elif choice == '2':
            if telnyx:
                show_telnyx_info(telnyx)
            else:
                print(f"{Colors.RED}Telnyx not configured{Colors.RESET}")

        elif choice == '3':
            if retell:
                show_retell_info(retell)
            else:
                print(f"{Colors.RED}Retell not configured{Colors.RESET}")

        elif choice == '4':
            if zadarma or telnyx:
                show_unified_view(zadarma or ZadarmaAPI("", ""),
                                 telnyx or TelnyxAPI(""),
                                 retell or RetellAPI(""))
            else:
                print(f"{Colors.RED}No providers configured{Colors.RESET}")

        elif choice == '5':
            show_warehouse_summary(creds)

        elif choice == 'a':
            if zadarma:
                show_zadarma_info(zadarma)
            if telnyx:
                show_telnyx_info(telnyx)
            if retell:
                show_retell_info(retell)
            show_warehouse_summary(creds)

        elif choice == 's':
            # Run expanded sync script
            print_header("SYNCING DATA FROM APIs")
            sync_script = Path(__file__).parent / "sync" / "sync_expanded.py"
            if sync_script.exists():
                import subprocess
                print(f"  Running: {sync_script}")
                print()
                result = subprocess.run([sys.executable, str(sync_script)], cwd=str(sync_script.parent))
                if result.returncode == 0:
                    print(f"\n  {Colors.GREEN}Sync completed successfully{Colors.RESET}")
                else:
                    print(f"\n  {Colors.RED}Sync failed with code {result.returncode}{Colors.RESET}")
            else:
                print(f"  {Colors.RED}Sync script not found: {sync_script}{Colors.RESET}")

        elif choice == 'r':
            continue

        else:
            print(f"{Colors.RED}Invalid option{Colors.RESET}")

        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")


if __name__ == "__main__":
    main()
