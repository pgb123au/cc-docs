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


def strip_ansi(s: str) -> str:
    """Remove ANSI color codes from string for length calculation"""
    import re
    return re.sub(r'\033\[[0-9;]*m', '', str(s))


def print_table(headers: List[str], rows: List[List[str]], col_widths: List[int] = None):
    """Print a formatted table with proper alignment (handles ANSI colors)"""
    if not col_widths:
        col_widths = [max(len(strip_ansi(str(row[i]))) for row in [headers] + rows) + 2 for i in range(len(headers))]

    gap = "  "  # Gap between columns
    total_width = sum(col_widths) + len(gap) * (len(col_widths) - 1)

    # Header
    header_parts = []
    for i, h in enumerate(headers):
        header_parts.append(f"{Colors.BOLD}{h:<{col_widths[i]}}{Colors.RESET}")
    print(f"  {gap.join(header_parts)}")
    print(f"  {'-' * total_width}")

    # Rows - handle ANSI color codes for proper alignment
    for row in rows:
        row_parts = []
        for i in range(len(row)):
            cell = str(row[i])
            visible_len = len(strip_ansi(cell))
            padding_needed = col_widths[i] - visible_len
            row_parts.append(cell + ' ' * max(0, padding_needed))
        print(f"  {gap.join(row_parts)}")


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


def open_url(url: str):
    """Open a URL in the default browser"""
    import subprocess
    if os.name == 'nt':
        subprocess.run(['start', '', url], shell=True)
    else:
        subprocess.run(['xdg-open', url])


def show_section_detail(conn, section: dict, creds: Dict[str, str]):
    """Show a single section in detail with pagination"""
    offset = 0
    page_size = 20

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header(f"TELCO DATA WAREHOUSE - {section['name']}")

        cur = conn.cursor()

        # Get total count
        try:
            count_query = f"SELECT COUNT(*) FROM ({section['query']}) sub"
            cur.execute(count_query)
            total_count = cur.fetchone()[0]
        except:
            total_count = 0

        if total_count > 0:
            print(f"\n  {Colors.DIM}Showing {offset + 1}-{min(offset + page_size, total_count)} of {total_count} records{Colors.RESET}\n")
        else:
            print(f"\n  {Colors.DIM}No records{Colors.RESET}\n")

        # Get data with offset
        cur.execute(f"{section['query']} LIMIT {page_size} OFFSET {offset}")
        rows = []
        raw_rows = cur.fetchall()  # Keep raw for clickable URLs
        for idx, row in enumerate(raw_rows):
            try:
                formatted = section["format"](row)
                # Add row number for sections with URLs (like recordings)
                if section.get("url_column") is not None and len(formatted) > 0 and formatted[0] == "":
                    formatted[0] = str(idx + 1)
                rows.append(formatted)
            except Exception as e:
                rows.append([str(e)] + ["-"] * (len(section["headers"]) - 1))

        if rows:
            print_table(section["headers"], rows, section["widths"])
        else:
            print(f"  {Colors.DIM}No data{Colors.RESET}")

        # Check if this section has clickable URLs (recordings)
        has_urls = section.get("url_column") is not None

        print(f"\n  {Colors.BOLD}Options:{Colors.RESET}")
        if offset > 0:
            print(f"    {Colors.CYAN}P{Colors.RESET} - Previous page")
        if offset + page_size < total_count:
            print(f"    {Colors.CYAN}M{Colors.RESET} - More (next page)")
        if has_urls and raw_rows:
            print(f"    {Colors.CYAN}1-{len(raw_rows)}{Colors.RESET} - Play recording in browser")
        print(f"    {Colors.CYAN}Q{Colors.RESET} - Back to overview")
        print()

        choice = input(f"  {Colors.BOLD}Select: {Colors.RESET}").strip().upper()

        if choice == 'Q' or choice == '':
            break
        elif choice == 'M' and offset + page_size < total_count:
            offset += page_size
        elif choice == 'P' and offset > 0:
            offset -= page_size
        elif has_urls and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(raw_rows):
                url_col = section["url_column"]
                url = raw_rows[idx][url_col]
                if url:
                    print(f"\n  {Colors.GREEN}Opening recording in browser...{Colors.RESET}")
                    print(f"  {Colors.DIM}{url}{Colors.RESET}")
                    open_url(url)
                    input(f"\n  {Colors.DIM}Press Enter to continue...{Colors.RESET}")
                else:
                    print(f"\n  {Colors.RED}No recording URL available for this entry{Colors.RESET}")
                    input(f"  {Colors.DIM}Press Enter to continue...{Colors.RESET}")


def show_warehouse_summary(creds: Dict[str, str]):
    """Show data warehouse with expandable sections - press key to view section detail"""
    print_header("TELCO DATA WAREHOUSE")

    if not POSTGRES_AVAILABLE:
        print(f"  {Colors.RED}psycopg2 not installed. Run: pip install psycopg2-binary{Colors.RESET}")
        return

    conn = get_db_connection(creds)
    if not conn:
        return

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
                    "headers": ["Number", "Provider", "Status", "Location", "Agent Name", "Synced"],
                    "widths": [20, 12, 10, 20, 55, 16],
                    "format": lambda r: [
                        format_phone(r[0] or ""),
                        f"{Colors.CYAN if r[1]=='telnyx' else Colors.MAGENTA if r[1]=='zadarma' else Colors.BLUE}{r[1]}{Colors.RESET}",
                        f"{Colors.GREEN if r[2] in ['on','active'] else Colors.YELLOW}{r[2] or '?'}{Colors.RESET}",
                        truncate(r[3] or r[4] or "-", 18),
                        r[5] or "-",  # Full agent name
                        r[6].strftime("%Y-%m-%d %H:%M") if r[6] else "-"
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
                    "headers": ["Time", "Provider", "From", "To", "Dur", "Status", "Agent Name", "Cost"],
                    "widths": [18, 12, 20, 20, 8, 10, 55, 10],
                    "format": lambda r: [
                        r[0].strftime("%Y-%m-%d %H:%M") if r[0] else "?",
                        f"{Colors.CYAN if r[1]=='telnyx' else Colors.MAGENTA if r[1]=='zadarma' else Colors.BLUE}{r[1]}{Colors.RESET}",
                        format_phone(r[2] or ""),
                        format_phone(r[3] or ""),
                        f"{r[4]}s" if r[4] else "-",
                        f"{Colors.GREEN if r[5]=='ended' else Colors.YELLOW}{r[5] or '?'}{Colors.RESET}",
                        r[6] or "-",  # Full agent name
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
                    "headers": ["Time", "Agent Name", "Call Sent.", "User Sent.", "Success", "VM", "Summary"],
                    "widths": [18, 50, 12, 12, 8, 4, 55],
                    "format": lambda r: [
                        r[0].strftime("%Y-%m-%d %H:%M") if r[0] else "-",
                        r[1] or "-",  # Full agent name
                        f"{Colors.GREEN if r[2]=='positive' else Colors.RED if r[2]=='negative' else Colors.YELLOW}{r[2] or '-'}{Colors.RESET}",
                        f"{Colors.GREEN if r[3]=='positive' else Colors.RED if r[3]=='negative' else Colors.YELLOW}{r[3] or '-'}{Colors.RESET}",
                        f"{Colors.GREEN}Yes{Colors.RESET}" if r[4] else f"{Colors.RED}No{Colors.RESET}" if r[4] is False else "-",
                        "Y" if r[5] else "-",
                        truncate((r[6] or "-").replace('\n', ' ').replace('\r', ''), 53)
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
                    "headers": ["Time", "Agent Name", "Caller", "Dur", "Words", "Transcript Preview"],
                    "widths": [18, 50, 20, 8, 8, 60],
                    "format": lambda r: [
                        r[0].strftime("%Y-%m-%d %H:%M") if r[0] else "-",
                        r[1] or "-",  # Full agent name
                        format_phone(r[2] or ""),
                        f"{r[3]}s" if r[3] else "-",
                        str(r[4] or 0),
                        truncate((r[5] or "-").replace('\n', ' ').replace('\r', ''), 58) if r[5] else "-"
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
                    "widths": [16, 35, 20, 12, 8, 18],
                    "format": lambda r: [
                        r[0] or "-",
                        truncate(r[1] or "-", 33),
                        r[2] or "-",
                        f"{Colors.GREEN}{r[3]}{Colors.RESET}" if r[3] == 'active' else r[3] or "-",
                        str(r[4] or 1),
                        r[5].strftime("%Y-%m-%d %H:%M") if r[5] else "-"
                    ]
                },
                {
                    "key": "6",
                    "name": "Recordings (All Providers)",
                    "query": """
                        SELECT created_at, provider, duration_seconds, format, recording_url, agent_name, caller
                        FROM (
                            SELECT r.created_at, p.name as provider, r.duration_seconds, r.format,
                                   r.recording_url, NULL as agent_name, NULL as caller
                            FROM telco.recordings r
                            JOIN telco.providers p ON r.provider_id = p.provider_id
                            UNION ALL
                            SELECT c.started_at as created_at, 'retell' as provider, c.duration_seconds,
                                   'mp3' as format, c.recording_url, c.retell_agent_name as agent_name,
                                   c.from_number as caller
                            FROM telco.calls c
                            JOIN telco.providers p ON c.provider_id = p.provider_id
                            WHERE p.name = 'retell' AND c.recording_url IS NOT NULL
                        ) combined
                        ORDER BY created_at DESC NULLS LAST
                    """,
                    "headers": ["#", "Time", "Provider", "Dur", "Agent/Caller", "Recording URL"],
                    "widths": [4, 18, 12, 8, 50, 70],
                    "url_column": 4,  # Index in raw row for recording_url (0-based in SELECT)
                    "format": lambda r: [
                        "",  # Row number filled by display
                        r[0].strftime("%Y-%m-%d %H:%M") if r[0] else "-",
                        f"{Colors.BLUE if r[1]=='retell' else Colors.MAGENTA}{r[1]}{Colors.RESET}",
                        f"{r[2]}s" if r[2] else "-",
                        truncate(r[5] or r[6] or "-", 48),  # agent_name or caller
                        truncate(r[4] or "-", 68)
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
                    "widths": [14, 10, 18, 18, 6, 10, 40, 8],
                    "format": lambda r: [
                        r[0].strftime("%m-%d %H:%M") if r[0] else "-",
                        f"{Colors.CYAN}{r[1]}{Colors.RESET}",
                        format_phone(r[2] or ""),
                        format_phone(r[3] or ""),
                        r[4] or "-",
                        r[5] or "-",
                        truncate((r[6] or "-").replace('\n', ' ').replace('\r', ''), 38),
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
                    "widths": [35, 40, 8, 12, 18, 14],
                    "format": lambda r: [
                        truncate(r[0] or "-", 33),
                        truncate(r[1] or "-", 38),
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
                    "widths": [40, 8, 18, 20, 14, 14],
                    "format": lambda r: [
                        truncate(r[0] or "-", 38),
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
                    "widths": [40, 8, 6, 55, 14],
                    "format": lambda r: [
                        truncate(r[0] or "-", 38),
                        f"{Colors.GREEN}Yes{Colors.RESET}" if r[1] else f"{Colors.RED}No{Colors.RESET}",
                        "Y" if r[2] else "N",
                        truncate(r[3] or "-", 53),
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
                    "widths": [30, 40, 8, 14, 14],
                    "format": lambda r: [
                        truncate(r[0] or "-", 28),
                        truncate(r[1] or "-", 38),
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
                    "widths": [40, 18, 14, 30, 10, 14],
                    "format": lambda r: [
                        truncate(r[0] or "-", 38),
                        r[1] or "-",
                        f"{Colors.GREEN if r[2]=='success' else Colors.YELLOW}{r[2] or '-'}{Colors.RESET}",
                        truncate(r[3] or "-", 28),
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
                    "widths": [35, 35, 45, 10, 14],
                    "format": lambda r: [
                        truncate(r[0] or "-", 33),
                        truncate(r[1] or "-", 33),
                        truncate(r[2] or "-", 43),
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
                    "widths": [40, 40, 25, 6, 14],
                    "format": lambda r: [
                        truncate(r[0] or "-", 38),
                        truncate(r[1] or "-", 38),
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
                    "widths": [35, 30, 18, 12, 10, 20],
                    "format": lambda r: [
                        truncate(r[0] or "-", 33),
                        truncate(r[1] or "-", 28),
                        r[2] or "-",
                        r[3] or "-",
                        r[4] or "-",
                        truncate(r[5] or "-", 18)
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
                    "headers": ["Agent ID", "Agent Name", "Voice ID", "Lang", "Webhook", "Synced"],
                    "widths": [30, 45, 25, 6, 25, 14],
                    "format": lambda r: [
                        truncate(r[0] or "-", 28),
                        r[1] or "-",  # Full agent name - no truncation
                        truncate(r[2] or "-", 23),
                        r[3] or "-",
                        truncate(r[4] or "-", 23) if r[4] else "-",
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
                    "headers": ["Snapshot", "Provider", "Balance", "Currency", "Credit Limit"],
                    "widths": [20, 14, 14, 10, 14],
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
                    "headers": ["Snapshot", "Current Concurrent", "Max Concurrent", "Calls In Progress"],
                    "widths": [22, 20, 16, 18],
                    "format": lambda r: [
                        r[0].strftime("%Y-%m-%d %H:%M") if r[0] else "-",
                        str(r[1] or 0),
                        str(r[2] or 0),
                        str(r[3] or 0)
                    ]
                },
            ]

            # Display all sections with preview (5 rows each)
            print_subheader("Data Sections (Press key to view full section)")
            print()

            for section in sections:
                key = section["key"]
                name = section["name"]

                # Get count
                try:
                    count_query = f"SELECT COUNT(*) FROM ({section['query']}) sub"
                    cur.execute(count_query)
                    total_count = cur.fetchone()[0]
                except:
                    total_count = 0

                # Section header
                count_display = f"({total_count})" if total_count > 0 else f"{Colors.DIM}(0){Colors.RESET}"
                print(f"  {Colors.CYAN}{key}.{Colors.RESET} {Colors.YELLOW}[+]{Colors.RESET} {name} {count_display}")

                if total_count > 0:
                    # Get preview data (5 rows)
                    cur.execute(f"{section['query']} LIMIT 5")
                    rows = []
                    raw_rows = cur.fetchall()
                    for idx, row in enumerate(raw_rows):
                        try:
                            formatted = section["format"](row)
                            # Add row number for recordings section
                            if section.get("url_column") is not None and formatted[0] == "":
                                formatted[0] = str(idx + 1)
                            rows.append(formatted)
                        except Exception as e:
                            rows.append([str(e)] + ["-"] * (len(section["headers"]) - 1))

                    if rows:
                        print_table(section["headers"], rows, section["widths"])
                        if total_count > 5:
                            print(f"       {Colors.DIM}... {total_count - 5} more (press {key} to view all){Colors.RESET}")
                    print()

            # Menu
            print(f"\n  {Colors.BOLD}Options:{Colors.RESET}")
            print(f"    Press {Colors.CYAN}1-9, A-I{Colors.RESET} to view a section in detail")
            print(f"    Press {Colors.CYAN}Q{Colors.RESET} to return to main menu")
            print()

            choice = input(f"  {Colors.BOLD}Select: {Colors.RESET}").strip().upper()

            if choice == 'Q' or choice == '':
                break
            elif choice in [s["key"] for s in sections]:
                # Find the section and show detail view
                for section in sections:
                    if section["key"] == choice:
                        show_section_detail(conn, section, creds)
                        break

        except Exception as e:
            print(f"{Colors.RED}Error querying database: {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            break

    conn.close()


# ============================================================================
# RETELL CALLS EXPLORER
# ============================================================================

def show_retell_calls_explorer(creds: Dict[str, str]):
    """Comprehensive Retell Calls Explorer - view all data for calls and export"""
    if not POSTGRES_AVAILABLE:
        print(f"  {Colors.RED}psycopg2 not installed. Run: pip install psycopg2-binary{Colors.RESET}")
        return

    conn = get_db_connection(creds)
    if not conn:
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header("RETELL CALLS EXPLORER")
        print(f"\n  {Colors.DIM}View comprehensive call data with all related information{Colors.RESET}\n")

        cur = conn.cursor()

        # Get 10 most recent Retell calls
        cur.execute("""
            SELECT c.external_call_id, c.started_at, c.from_number, c.to_number,
                   c.duration_seconds, c.status, c.retell_agent_name,
                   c.direction, c.recording_url
            FROM telco.calls c
            JOIN telco.providers p ON c.provider_id = p.provider_id
            WHERE p.name = 'retell'
            ORDER BY c.started_at DESC NULLS LAST
            LIMIT 10
        """)
        calls = cur.fetchall()

        if not calls:
            print(f"  {Colors.YELLOW}No Retell calls found in database{Colors.RESET}")
            print(f"\n  {Colors.DIM}Try syncing data first (option S from main menu){Colors.RESET}")
            input(f"\n{Colors.DIM}Press Enter to go back...{Colors.RESET}")
            conn.close()
            return

        # Display calls with selection numbers
        print(f"  {Colors.BOLD}10 Most Recent Retell Calls:{Colors.RESET}\n")

        headers = ["#", "Time", "From", "To", "Dur", "Status", "Agent", "Dir"]
        col_widths = [4, 18, 18, 18, 8, 12, 40, 6]

        rows = []
        for idx, call in enumerate(calls, 1):
            call_id, started_at, from_num, to_num, duration, status, agent_name, direction, rec_url = call
            time_str = started_at.strftime("%Y-%m-%d %H:%M") if started_at else "-"
            dur_str = f"{duration}s" if duration else "-"
            agent_short = (agent_name[:38] + "..") if agent_name and len(agent_name) > 40 else (agent_name or "-")
            dir_str = direction[:3].upper() if direction else "-"
            has_rec = f"{Colors.GREEN}●{Colors.RESET}" if rec_url else ""

            rows.append([
                f"{Colors.CYAN}{idx}{Colors.RESET}",
                time_str,
                from_num or "-",
                to_num or "-",
                dur_str,
                status or "-",
                agent_short,
                dir_str + has_rec
            ])

        print_table(headers, rows, col_widths)

        print(f"\n  {Colors.BOLD}Options:{Colors.RESET}")
        print(f"    - Enter number (e.g., {Colors.CYAN}1{Colors.RESET}) for single call")
        print(f"    - Enter range (e.g., {Colors.CYAN}1-3{Colors.RESET}) for multiple")
        print(f"    - Enter comma-separated (e.g., {Colors.CYAN}1,3,5{Colors.RESET})")
        print(f"    - Enter {Colors.CYAN}A{Colors.RESET} for all 10 calls")
        print(f"    - Enter {Colors.CYAN}S{Colors.RESET} to {Colors.BOLD}Search transcripts{Colors.RESET}")
        print(f"    - Enter {Colors.CYAN}Q{Colors.RESET} to go back")
        print()

        choice = input(f"  {Colors.BOLD}Selection: {Colors.RESET}").strip()

        if not choice or choice.upper() == 'Q':
            break

        # Handle search option
        if choice.upper() == 'S':
            search_transcripts(conn, creds)
            continue

        # Parse selection
        selected_indices = []
        if choice.upper() == 'A':
            selected_indices = list(range(10))
        else:
            try:
                parts = choice.replace(' ', '').split(',')
                for part in parts:
                    if '-' in part:
                        start, end = part.split('-')
                        selected_indices.extend(range(int(start) - 1, int(end)))
                    else:
                        selected_indices.append(int(part) - 1)
            except:
                print(f"\n  {Colors.RED}Invalid selection format{Colors.RESET}")
                input(f"  {Colors.DIM}Press Enter to try again...{Colors.RESET}")
                continue

        # Validate indices
        selected_indices = [i for i in selected_indices if 0 <= i < len(calls)]
        if not selected_indices:
            print(f"\n  {Colors.RED}No valid calls selected{Colors.RESET}")
            input(f"  {Colors.DIM}Press Enter to try again...{Colors.RESET}")
            continue

        # Get selected call IDs
        selected_calls = [calls[i] for i in selected_indices]
        selected_call_ids = [call[0] for call in selected_calls]

        # Show detailed view for selected calls
        show_call_details(conn, selected_call_ids, creds)

    conn.close()


def search_transcripts(conn, creds: Dict[str, str]):
    """Search all transcripts for a string and list matching calls"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_header("TRANSCRIPT SEARCH")

    print(f"\n  {Colors.DIM}Search for text within call transcripts{Colors.RESET}\n")

    search_term = input(f"  {Colors.BOLD}Enter search term: {Colors.RESET}").strip()

    if not search_term:
        print(f"\n  {Colors.RED}No search term entered{Colors.RESET}")
        input(f"  {Colors.DIM}Press Enter to go back...{Colors.RESET}")
        return

    cur = conn.cursor()

    # Search transcripts (case-insensitive)
    cur.execute("""
        SELECT c.external_call_id, c.started_at, c.from_number, c.to_number,
               c.duration_seconds, c.status, c.retell_agent_name,
               c.direction, c.recording_url, c.transcript, c.full_transcript
        FROM telco.calls c
        JOIN telco.providers p ON c.provider_id = p.provider_id
        WHERE p.name = 'retell'
          AND (c.transcript ILIKE %s OR c.full_transcript ILIKE %s)
        ORDER BY c.started_at DESC NULLS LAST
        LIMIT 50
    """, (f'%{search_term}%', f'%{search_term}%'))

    results = cur.fetchall()

    if not results:
        print(f"\n  {Colors.YELLOW}No calls found containing '{search_term}'{Colors.RESET}")
        input(f"\n  {Colors.DIM}Press Enter to go back...{Colors.RESET}")
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header(f"TRANSCRIPT SEARCH: '{search_term}'")
        print(f"\n  {Colors.GREEN}Found {len(results)} call(s) matching '{search_term}'{Colors.RESET}\n")

        headers = ["#", "Time", "From", "To", "Dur", "Agent", "Transcript Preview"]
        col_widths = [4, 18, 16, 16, 8, 30, 50]

        rows = []
        for idx, result in enumerate(results, 1):
            call_id, started_at, from_num, to_num, duration, status, agent_name, direction, rec_url, transcript, full_transcript = result

            time_str = started_at.strftime("%Y-%m-%d %H:%M") if started_at else "-"
            dur_str = f"{duration}s" if duration else "-"
            agent_short = (agent_name[:28] + "..") if agent_name and len(agent_name) > 30 else (agent_name or "-")

            # Get transcript preview with search term highlighted
            text = full_transcript or transcript or ""
            text = text.replace('\n', ' ').replace('\r', '')

            # Find the search term and show context around it
            lower_text = text.lower()
            lower_term = search_term.lower()
            pos = lower_text.find(lower_term)
            if pos != -1:
                start = max(0, pos - 20)
                end = min(len(text), pos + len(search_term) + 30)
                preview = ("..." if start > 0 else "") + text[start:end] + ("..." if end < len(text) else "")
                # Highlight the search term
                preview_lower = preview.lower()
                term_pos = preview_lower.find(lower_term)
                if term_pos != -1:
                    preview = preview[:term_pos] + f"{Colors.YELLOW}{preview[term_pos:term_pos+len(search_term)]}{Colors.RESET}" + preview[term_pos+len(search_term):]
            else:
                preview = text[:50] + "..." if len(text) > 50 else text

            rows.append([
                f"{Colors.CYAN}{idx}{Colors.RESET}",
                time_str,
                from_num or "-",
                to_num or "-",
                dur_str,
                agent_short,
                preview
            ])

        print_table(headers, rows, col_widths)

        print(f"\n  {Colors.BOLD}Options:{Colors.RESET}")
        print(f"    - Enter number (e.g., {Colors.CYAN}1{Colors.RESET}) for single call")
        print(f"    - Enter range (e.g., {Colors.CYAN}1-3{Colors.RESET}) for multiple")
        print(f"    - Enter comma-separated (e.g., {Colors.CYAN}1,3,5{Colors.RESET})")
        print(f"    - Enter {Colors.CYAN}A{Colors.RESET} for all matching calls")
        print(f"    - Enter {Colors.CYAN}N{Colors.RESET} for new search")
        print(f"    - Enter {Colors.CYAN}Q{Colors.RESET} to go back")
        print()

        choice = input(f"  {Colors.BOLD}Selection: {Colors.RESET}").strip()

        if not choice or choice.upper() == 'Q':
            break

        if choice.upper() == 'N':
            # Recursive call for new search
            search_transcripts(conn, creds)
            break

        # Parse selection
        selected_indices = []
        if choice.upper() == 'A':
            selected_indices = list(range(len(results)))
        else:
            try:
                parts = choice.replace(' ', '').split(',')
                for part in parts:
                    if '-' in part:
                        start, end = part.split('-')
                        selected_indices.extend(range(int(start) - 1, int(end)))
                    else:
                        selected_indices.append(int(part) - 1)
            except:
                print(f"\n  {Colors.RED}Invalid selection format{Colors.RESET}")
                input(f"  {Colors.DIM}Press Enter to try again...{Colors.RESET}")
                continue

        # Validate indices
        selected_indices = [i for i in selected_indices if 0 <= i < len(results)]
        if not selected_indices:
            print(f"\n  {Colors.RED}No valid calls selected{Colors.RESET}")
            input(f"  {Colors.DIM}Press Enter to try again...{Colors.RESET}")
            continue

        # Get selected call IDs
        selected_call_ids = [results[i][0] for i in selected_indices]

        # Show detailed view for selected calls
        show_call_details(conn, selected_call_ids, creds)


def show_full_transcripts(all_call_data: List[dict]):
    """Display full transcripts for selected calls with pagination"""
    call_index = 0

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        data = all_call_data[call_index]
        call_info = data.get("call_info", {})
        call_id = data.get("call_id", "Unknown")

        total_calls = len(all_call_data)
        print_header(f"FULL TRANSCRIPT - Call {call_index + 1} of {total_calls}")

        # Call summary
        print(f"\n  {Colors.BOLD}Call ID:{Colors.RESET} {call_id}")
        print(f"  {Colors.BOLD}Time:{Colors.RESET} {call_info.get('started_at', '-')}")
        print(f"  {Colors.BOLD}From:{Colors.RESET} {call_info.get('from_number', '-')} → {call_info.get('to_number', '-')}")
        print(f"  {Colors.BOLD}Agent:{Colors.RESET} {call_info.get('retell_agent_name', '-')}")
        print(f"  {Colors.BOLD}Duration:{Colors.RESET} {call_info.get('duration_seconds', '-')} seconds")

        transcript = call_info.get('full_transcript') or call_info.get('transcript') or ''

        if transcript:
            word_count = len(transcript.split())
            print(f"  {Colors.BOLD}Words:{Colors.RESET} {word_count}")
            print(f"\n  {Colors.BOLD}{'='*70}{Colors.RESET}")
            print(f"\n{Colors.CYAN}TRANSCRIPT:{Colors.RESET}\n")

            # Format transcript for readability - wrap long lines
            lines = transcript.split('\n')
            for line in lines:
                # Wrap lines longer than 100 chars
                while len(line) > 100:
                    # Find a space to break at
                    break_point = line.rfind(' ', 0, 100)
                    if break_point == -1:
                        break_point = 100
                    print(f"  {line[:break_point]}")
                    line = line[break_point:].lstrip()
                print(f"  {line}")

            print(f"\n  {Colors.BOLD}{'='*70}{Colors.RESET}")
        else:
            print(f"\n  {Colors.YELLOW}No transcript available for this call{Colors.RESET}")

        # Navigation
        print(f"\n  {Colors.BOLD}Navigation:{Colors.RESET}")
        if call_index > 0:
            print(f"    {Colors.CYAN}P{Colors.RESET} - Previous call")
        if call_index < total_calls - 1:
            print(f"    {Colors.CYAN}N{Colors.RESET} - Next call")
        if total_calls > 1:
            print(f"    {Colors.CYAN}1-{total_calls}{Colors.RESET} - Jump to specific call")
        print(f"    {Colors.CYAN}Q{Colors.RESET} - Back to call details")
        print()

        choice = input(f"  {Colors.BOLD}Select: {Colors.RESET}").strip().upper()

        if choice == 'Q' or choice == '':
            break
        elif choice == 'P' and call_index > 0:
            call_index -= 1
        elif choice == 'N' and call_index < total_calls - 1:
            call_index += 1
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < total_calls:
                call_index = idx


def show_call_timeline(all_call_data: List[dict]):
    """Display call timeline showing transcript interleaved with tool calls"""
    import json
    import shutil
    from pathlib import Path

    call_index = 0
    # Get terminal width, default to 120 if can't detect
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 120
    # Use most of the width
    width = min(term_width - 2, 200)
    # Fixed column widths for alignment
    col_time = 7
    col_delta = 9
    col_type = 14
    col_content = width - col_time - col_delta - col_type - 3  # 3 for separators

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        data = all_call_data[call_index]
        call_info = data.get("call_info", {})
        call_id = data.get("call_id", "Unknown")
        raw_data = call_info.get("raw_data", {})

        total_calls = len(all_call_data)
        print_header(f"CALL TIMELINE - Call {call_index + 1} of {total_calls}")

        # Call summary - compact single line
        duration = call_info.get('duration_seconds', 0) or 0
        agent = call_info.get('retell_agent_name', '-')
        started = str(call_info.get('started_at', '-'))[:19]
        print(f"\n{Colors.DIM}Call:{Colors.RESET} {call_id}  {Colors.DIM}|{Colors.RESET}  {started}  {Colors.DIM}|{Colors.RESET}  {duration}s  {Colors.DIM}|{Colors.RESET}  {agent}")

        # Get timeline data - try multiple sources
        timeline = raw_data.get("transcript_with_tool_calls", []) if raw_data else []
        used_fallback = False

        # Check if call is still ongoing
        call_status = raw_data.get("call_status", "") if raw_data else ""

        if not timeline:
            # Try fallback to transcript_object (basic conversation without tools)
            transcript_obj = raw_data.get("transcript_object", []) if raw_data else []
            if transcript_obj:
                timeline = transcript_obj
                used_fallback = True

        if not timeline:
            if call_status == "ongoing":
                print(f"\n{Colors.YELLOW}Call is still in progress - timeline not yet available{Colors.RESET}")
                print(f"{Colors.DIM}Refresh the data after the call ends to see the timeline{Colors.RESET}")
            else:
                print(f"\n{Colors.YELLOW}No timeline data available for this call{Colors.RESET}")
                print(f"{Colors.DIM}(transcript_with_tool_calls not found in raw_data){Colors.RESET}")

            # Show public log URL if available
            public_log = raw_data.get("public_log_url", "") if raw_data else ""
            if public_log:
                print(f"\n{Colors.CYAN}Public log URL:{Colors.RESET} {public_log}")
        else:
            if used_fallback:
                print(f"{Colors.YELLOW}Note: Using basic transcript (tool calls not available){Colors.RESET}")

            # Pre-process timeline to extract timestamps and calculate deltas
            processed = []
            prev_time = 0.0
            node_counter = 0

            for item in timeline:
                role = item.get("role", "")
                words = item.get("words", [])

                # Get timestamp from words if available
                curr_time = None
                if words and len(words) > 0 and isinstance(words[0], dict):
                    curr_time = words[0].get("start", 0)

                # Track node transitions
                if role == "node_transition":
                    node_counter += 1

                # Calculate delta
                delta = None
                if curr_time is not None:
                    delta = curr_time - prev_time
                    prev_time = curr_time

                processed.append({
                    "item": item,
                    "time": curr_time,
                    "delta": delta,
                    "node_num": node_counter
                })

            # Header
            print(f"\n{Colors.BOLD}{'─'*width}{Colors.RESET}")
            print(f"{Colors.BOLD}{'TIME':>{col_time}} {'DELTA':>{col_delta}}  {'TYPE':<{col_type}}  CONTENT{Colors.RESET}")
            print(f"{Colors.DIM}{'─'*width}{Colors.RESET}")

            for p in processed:
                item = p["item"]
                role = item.get("role", "")
                content = item.get("content", "")
                curr_time = p["time"]
                delta = p["delta"]
                node_num = p["node_num"]

                # Format timestamp (right-aligned)
                time_str = f"{curr_time:.1f}s" if curr_time is not None else ""

                # Format delta - highlight slow responses (right-aligned)
                if delta is not None:
                    delta_val = f"+{delta:.1f}s"
                    if delta > 5.0:
                        delta_str = f"{Colors.RED}{delta_val:>{col_delta}}{Colors.RESET}"
                    elif delta > 2.0:
                        delta_str = f"{Colors.YELLOW}{delta_val:>{col_delta}}{Colors.RESET}"
                    else:
                        delta_str = f"{Colors.DIM}{delta_val:>{col_delta}}{Colors.RESET}"
                else:
                    delta_str = " " * col_delta

                # Format based on role
                if role == "agent":
                    text = content[:col_content-3] + "..." if len(content or "") > col_content else content or ""
                    print(f"{time_str:>{col_time}} {delta_str}  {Colors.CYAN}{'AGENT':<{col_type}}{Colors.RESET}  {text}")

                elif role == "user":
                    text = content[:col_content-3] + "..." if len(content or "") > col_content else content or ""
                    print(f"{time_str:>{col_time}} {delta_str}  {Colors.GREEN}{'USER':<{col_type}}{Colors.RESET}  {text}")

                elif role == "tool_call_invocation":
                    tool_name = item.get("name", "unknown")
                    args = item.get("arguments", "")
                    # Parse args if JSON
                    try:
                        args_dict = json.loads(args) if args else {}
                        args_parts = [f"{k}={repr(v)}" for k, v in args_dict.items()]
                        args_preview = ", ".join(args_parts)
                        max_args = col_content - len(tool_name) - 3
                        if len(args_preview) > max_args:
                            args_preview = args_preview[:max_args-3] + "..."
                    except:
                        args_preview = args[:col_content - len(tool_name) - 6] if args else ""
                    print(f"{time_str:>{col_time}} {delta_str}  {Colors.YELLOW}{'TOOL CALL':<{col_type}}{Colors.RESET}  {Colors.BOLD}{tool_name}{Colors.RESET}({args_preview})")

                elif role == "tool_call_result":
                    result = content or ""
                    # Parse result if JSON
                    try:
                        result_dict = json.loads(result) if result else {}
                        # Extract key info based on common patterns
                        if "error" in result_dict:
                            result_preview = f"{Colors.RED}ERROR: {result_dict.get('error', '')[:col_content-10]}{Colors.RESET}"
                        elif "found" in result_dict:
                            result_preview = f"found={result_dict.get('found')}"
                            if result_dict.get("patient", {}).get("full_name"):
                                result_preview += f", patient={result_dict['patient']['full_name']}"
                        elif "success" in result_dict:
                            success = result_dict.get('success')
                            result_preview = f"{Colors.GREEN}success={success}{Colors.RESET}" if success else f"{Colors.RED}success={success}{Colors.RESET}"
                            # Add more context from result
                            if result_dict.get("message"):
                                result_preview += f" - {result_dict['message'][:60]}"
                            elif result_dict.get("class_name"):
                                result_preview += f" - {result_dict.get('class_name')} ({result_dict.get('spots_available', '?')} spots)"
                        elif "classes" in result_dict:
                            classes = result_dict.get("classes", [])
                            result_preview = f"{len(classes)} classes found"
                        elif "slots" in result_dict:
                            slots = result_dict.get("slots", [])
                            result_preview = f"{len(slots)} slots available"
                        elif "appointments" in result_dict:
                            appts = result_dict.get("appointments", [])
                            result_preview = f"{len(appts)} appointments"
                        elif "booking_id" in result_dict:
                            result_preview = f"{Colors.GREEN}booking_id={result_dict.get('booking_id')}{Colors.RESET}"
                        else:
                            result_preview = str(result_dict)
                            if len(result_preview) > col_content:
                                result_preview = result_preview[:col_content-3] + "..."
                    except:
                        result_preview = result[:col_content-3] + "..." if len(result) > col_content else result

                    # Add duration if available
                    duration_ms = ""
                    try:
                        result_dict = json.loads(result) if result else {}
                        if "duration_ms" in result_dict:
                            duration_ms = f" {Colors.DIM}({result_dict['duration_ms']}ms){Colors.RESET}"
                    except:
                        pass

                    print(f"{time_str:>{col_time}} {delta_str}  {Colors.MAGENTA}{'TOOL RESULT':<{col_type}}{Colors.RESET}  {result_preview}{duration_ms}")

                elif role == "node_transition":
                    # Clean node separator line
                    label = f" node {node_num} "
                    side_len = (width - len(label) - col_time - col_delta - 4) // 2
                    print(f"{time_str:>{col_time}} {delta_str}  {Colors.DIM}{'─'*side_len}{label}{'─'*side_len}{Colors.RESET}")

            print(f"{Colors.BOLD}{'─'*width}{Colors.RESET}")

            # Summary stats - compact
            agent_msgs = sum(1 for i in timeline if i.get("role") == "agent")
            user_msgs = sum(1 for i in timeline if i.get("role") == "user")
            tool_calls = sum(1 for i in timeline if i.get("role") == "tool_call_invocation")
            tool_results = sum(1 for i in timeline if i.get("role") == "tool_call_result")

            print(f"\n{Colors.BOLD}Summary:{Colors.RESET} Agent: {agent_msgs} | User: {user_msgs} | Tool calls: {tool_calls} | Tool results: {tool_results}")

        # Navigation - compact
        print(f"\n{Colors.BOLD}Options:{Colors.RESET} ", end="")
        opts = []
        if call_index > 0:
            opts.append(f"{Colors.CYAN}P{Colors.RESET}=Prev")
        if call_index < total_calls - 1:
            opts.append(f"{Colors.CYAN}N{Colors.RESET}=Next")
        if total_calls > 1:
            opts.append(f"{Colors.CYAN}1-{total_calls}{Colors.RESET}=Jump")
        opts.append(f"{Colors.CYAN}F{Colors.RESET}=Full View")
        opts.append(f"{Colors.CYAN}E{Colors.RESET}=Export")
        opts.append(f"{Colors.CYAN}D{Colors.RESET}=Debug Export")
        opts.append(f"{Colors.CYAN}Q{Colors.RESET}=Back")
        print(" | ".join(opts))

        choice = input(f"\n{Colors.BOLD}Select: {Colors.RESET}").strip().upper()

        if choice == 'Q' or choice == '':
            break
        elif choice == 'P' and call_index > 0:
            call_index -= 1
        elif choice == 'N' and call_index < total_calls - 1:
            call_index += 1
        elif choice == 'F':
            # Show full detailed timeline view
            show_full_timeline_view(call_id, call_info, raw_data, timeline)
        elif choice == 'E':
            # Export timeline to file (compact format)
            export_path = export_timeline(call_id, call_info, timeline)
            if export_path:
                print(f"\n{Colors.GREEN}Exported to:{Colors.RESET} {export_path}")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        elif choice == 'D':
            # Full debug export with all data
            print(f"\n{Colors.YELLOW}Exporting full debug data (may take a moment to fetch logs)...{Colors.RESET}")
            export_path = export_full_debug(call_id, call_info, raw_data, timeline)
            if export_path:
                print(f"\n{Colors.GREEN}Full debug exported to:{Colors.RESET} {export_path}")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < total_calls:
                call_index = idx


def show_full_timeline_view(call_id: str, call_info: dict, raw_data: dict, timeline: list):
    """Display full detailed timeline on screen with scrolling"""
    import json
    import shutil

    # Get terminal dimensions
    try:
        term_width = shutil.get_terminal_size().columns
        term_height = shutil.get_terminal_size().lines
    except:
        term_width = 120
        term_height = 40

    width = min(term_width - 4, 200)
    page_size = term_height - 10  # Leave room for header/footer

    # Build the full output
    lines = []

    # Header
    lines.append(f"{Colors.BOLD}{'═' * width}{Colors.RESET}")
    lines.append(f"{Colors.BOLD}  FULL TIMELINE VIEW{Colors.RESET}")
    lines.append(f"{Colors.BOLD}{'═' * width}{Colors.RESET}")
    lines.append("")

    # Call info
    lines.append(f"{Colors.CYAN}Call ID:{Colors.RESET}    {call_id}")
    lines.append(f"{Colors.CYAN}Agent:{Colors.RESET}      {call_info.get('retell_agent_name', '-')}")
    lines.append(f"{Colors.CYAN}From:{Colors.RESET}       {call_info.get('from_number', '-')} → {call_info.get('to_number', '-')}")
    lines.append(f"{Colors.CYAN}Started:{Colors.RESET}    {str(call_info.get('started_at', '-'))[:19]}")
    lines.append(f"{Colors.CYAN}Duration:{Colors.RESET}   {call_info.get('duration_seconds', 0)}s")
    lines.append(f"{Colors.CYAN}Status:{Colors.RESET}     {call_info.get('status', '-')}")

    # Disconnection reason if present
    disconnect = raw_data.get('disconnection_reason', '') if raw_data else ''
    if disconnect:
        lines.append(f"{Colors.CYAN}Disconnect:{Colors.RESET} {disconnect}")

    lines.append("")
    lines.append(f"{Colors.DIM}{'─' * width}{Colors.RESET}")

    # Dynamic variables section
    collected_vars = raw_data.get('collected_dynamic_variables', {}) if raw_data else {}
    if collected_vars:
        lines.append("")
        lines.append(f"{Colors.BOLD}Dynamic Variables (Final State):{Colors.RESET}")
        for k, v in collected_vars.items():
            lines.append(f"  {Colors.CYAN}{k}:{Colors.RESET} {v}")
        lines.append("")
        lines.append(f"{Colors.DIM}{'─' * width}{Colors.RESET}")

    # Timeline section
    lines.append("")
    lines.append(f"{Colors.BOLD}Timeline Events:{Colors.RESET}")
    lines.append("")

    if not timeline:
        lines.append(f"  {Colors.YELLOW}No timeline data available{Colors.RESET}")
    else:
        prev_time = 0.0
        node_counter = 0

        for idx, item in enumerate(timeline):
            role = item.get("role", "")
            content = item.get("content", "")
            words = item.get("words", [])

            # Get timestamp
            curr_time = None
            if words and len(words) > 0 and isinstance(words[0], dict):
                curr_time = words[0].get("start", 0)

            if role == "node_transition":
                node_counter += 1

            # Calculate delta
            delta = None
            if curr_time is not None:
                delta = curr_time - prev_time
                prev_time = curr_time

            # Format time and delta
            time_str = f"{curr_time:.2f}s" if curr_time is not None else "     -"
            if delta is not None:
                if delta > 5.0:
                    delta_str = f"{Colors.RED}+{delta:.2f}s ⚠{Colors.RESET}"
                elif delta > 2.0:
                    delta_str = f"{Colors.YELLOW}+{delta:.2f}s{Colors.RESET}"
                else:
                    delta_str = f"{Colors.DIM}+{delta:.2f}s{Colors.RESET}"
            else:
                delta_str = ""

            # Event header line
            event_num = f"[{idx + 1:3d}]"

            if role == "node_transition":
                lines.append("")
                lines.append(f"{Colors.DIM}{'─' * 20} Node {node_counter} {'─' * (width - 30)}{Colors.RESET}")
                lines.append("")

            elif role == "agent":
                lines.append(f"{event_num} {Colors.CYAN}▶ AGENT{Colors.RESET}  {time_str}  {delta_str}")
                # Word wrap content
                wrapped = _wrap_text(content, width - 12)
                for line in wrapped:
                    lines.append(f"           {line}")
                lines.append("")

            elif role == "user":
                lines.append(f"{event_num} {Colors.GREEN}◀ USER{Colors.RESET}   {time_str}  {delta_str}")
                wrapped = _wrap_text(content, width - 12)
                for line in wrapped:
                    lines.append(f"           {line}")
                lines.append("")

            elif role == "tool_call_invocation":
                tool_name = item.get("name", "unknown")
                tool_id = item.get("tool_call_id", "")
                args = item.get("arguments", "{}")

                lines.append(f"{event_num} {Colors.YELLOW}⚡ TOOL CALL{Colors.RESET}  {time_str}  {delta_str}")
                lines.append(f"           {Colors.BOLD}Function:{Colors.RESET} {tool_name}")
                if tool_id:
                    lines.append(f"           {Colors.DIM}ID: {tool_id}{Colors.RESET}")

                # Parse and display arguments nicely
                try:
                    args_dict = json.loads(args) if args else {}
                    if args_dict:
                        lines.append(f"           {Colors.BOLD}Arguments:{Colors.RESET}")
                        for k, v in args_dict.items():
                            v_str = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                            if len(v_str) > width - 25:
                                v_str = v_str[:width - 28] + "..."
                            lines.append(f"             {Colors.CYAN}{k}:{Colors.RESET} {v_str}")
                except:
                    lines.append(f"           {Colors.DIM}Args: {args[:width-20]}{Colors.RESET}")
                lines.append("")

            elif role == "tool_call_result":
                lines.append(f"{event_num} {Colors.MAGENTA}↩ TOOL RESULT{Colors.RESET}  {time_str}  {delta_str}")

                # Parse and display result
                try:
                    result = json.loads(content) if content else {}

                    # Check for errors first
                    if result.get("error"):
                        lines.append(f"           {Colors.RED}ERROR: {result['error']}{Colors.RESET}")
                    elif result.get("success") == False:
                        lines.append(f"           {Colors.RED}SUCCESS: false{Colors.RESET}")
                        if result.get("message"):
                            lines.append(f"           {Colors.RED}Message: {result['message']}{Colors.RESET}")
                    else:
                        # Show key fields
                        for k, v in result.items():
                            v_str = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                            if len(v_str) > width - 25:
                                v_str = v_str[:width - 28] + "..."
                            # Color success green
                            if k == "success" and v == True:
                                lines.append(f"             {Colors.GREEN}{k}: {v_str}{Colors.RESET}")
                            elif k == "error":
                                lines.append(f"             {Colors.RED}{k}: {v_str}{Colors.RESET}")
                            else:
                                lines.append(f"             {Colors.CYAN}{k}:{Colors.RESET} {v_str}")
                except:
                    wrapped = _wrap_text(content or "(empty)", width - 12)
                    for line in wrapped:
                        lines.append(f"           {line}")
                lines.append("")

            else:
                # Unknown role
                lines.append(f"{event_num} {Colors.DIM}{role.upper()}{Colors.RESET}  {time_str}  {delta_str}")
                if content:
                    wrapped = _wrap_text(content, width - 12)
                    for line in wrapped:
                        lines.append(f"           {line}")
                lines.append("")

    lines.append(f"{Colors.DIM}{'─' * width}{Colors.RESET}")

    # Summary
    if timeline:
        agent_msgs = sum(1 for i in timeline if i.get("role") == "agent")
        user_msgs = sum(1 for i in timeline if i.get("role") == "user")
        tool_calls = sum(1 for i in timeline if i.get("role") == "tool_call_invocation")
        tool_results = sum(1 for i in timeline if i.get("role") == "tool_call_result")
        nodes = sum(1 for i in timeline if i.get("role") == "node_transition")

        lines.append("")
        lines.append(f"{Colors.BOLD}Summary:{Colors.RESET} {agent_msgs} agent | {user_msgs} user | {tool_calls} tool calls | {tool_results} results | {nodes} nodes")

    lines.append(f"{Colors.BOLD}{'═' * width}{Colors.RESET}")

    # Now paginate the output
    total_lines = len(lines)
    current_pos = 0

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        # Show current page
        end_pos = min(current_pos + page_size, total_lines)
        for i in range(current_pos, end_pos):
            print(lines[i])

        # Navigation
        print(f"\n{Colors.DIM}Line {current_pos + 1}-{end_pos} of {total_lines}{Colors.RESET}")
        nav = []
        if current_pos > 0:
            nav.append(f"{Colors.CYAN}U{Colors.RESET}=Up")
        if end_pos < total_lines:
            nav.append(f"{Colors.CYAN}D{Colors.RESET}=Down")
        nav.append(f"{Colors.CYAN}T{Colors.RESET}=Top")
        nav.append(f"{Colors.CYAN}B{Colors.RESET}=Bottom")
        nav.append(f"{Colors.CYAN}Q{Colors.RESET}=Back")
        print(f"{Colors.BOLD}Nav:{Colors.RESET} " + " | ".join(nav))

        choice = input(f"{Colors.BOLD}>{Colors.RESET} ").strip().upper()

        if choice == 'Q' or choice == '':
            break
        elif choice == 'U' and current_pos > 0:
            current_pos = max(0, current_pos - page_size)
        elif choice == 'D' and end_pos < total_lines:
            current_pos = min(total_lines - page_size, current_pos + page_size)
            current_pos = max(0, current_pos)
        elif choice == 'T':
            current_pos = 0
        elif choice == 'B':
            current_pos = max(0, total_lines - page_size)


def _wrap_text(text: str, width: int) -> list:
    """Wrap text to specified width, returning list of lines"""
    if not text:
        return [""]
    words = text.split()
    lines = []
    current_line = []
    current_len = 0

    for word in words:
        if current_len + len(word) + 1 <= width:
            current_line.append(word)
            current_len += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines if lines else [""]


def export_timeline(call_id: str, call_info: dict, timeline: list) -> str:
    """Export timeline to a markdown file optimized for Claude analysis"""
    import json
    from pathlib import Path
    from datetime import datetime

    downloads = Path.home() / "Downloads"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"timeline_{call_id[:20]}_{ts}.md"
    filepath = downloads / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        # Header for Claude
        f.write("# Call Timeline Analysis\n\n")
        f.write("This is a timeline export from a RetellAI voice agent call. ")
        f.write("Use this to debug agent behavior, identify slow tool responses, ")
        f.write("and understand conversation flow.\n\n")

        # Call metadata
        f.write("## Call Information\n\n")
        f.write(f"| Field | Value |\n")
        f.write(f"|-------|-------|\n")
        f.write(f"| Call ID | `{call_id}` |\n")
        f.write(f"| Started | {call_info.get('started_at', '-')} |\n")
        f.write(f"| Duration | {call_info.get('duration_seconds', '-')} seconds |\n")
        f.write(f"| Agent | {call_info.get('retell_agent_name', '-')} |\n")
        f.write(f"| From | {call_info.get('from_number', '-')} |\n")
        f.write(f"| To | {call_info.get('to_number', '-')} |\n")
        f.write(f"| Status | {call_info.get('status', '-')} |\n\n")

        # Pre-process to calculate deltas and identify issues
        prev_time = 0.0
        node_counter = 0
        slow_responses = []
        errors = []
        processed = []

        for item in timeline:
            role = item.get("role", "")
            content = item.get("content", "")
            words = item.get("words", [])

            curr_time = None
            if words and len(words) > 0 and isinstance(words[0], dict):
                curr_time = words[0].get("start", 0)

            delta = None
            if curr_time is not None:
                delta = curr_time - prev_time
                prev_time = curr_time

            if role == "node_transition":
                node_counter += 1

            # Track issues
            if delta is not None and delta > 5.0:
                slow_responses.append({"time": curr_time, "delta": delta, "role": role, "content": content[:50]})

            if role == "tool_call_result" and content:
                try:
                    result = json.loads(content)
                    if result.get("error") or result.get("success") == False:
                        errors.append({"time": curr_time, "content": content})
                except:
                    pass

            processed.append({
                "item": item,
                "time": curr_time,
                "delta": delta,
                "node_num": node_counter
            })

        # Issues summary for Claude
        if slow_responses or errors:
            f.write("## Issues Detected\n\n")
            if slow_responses:
                f.write("### Slow Responses (>5s delay)\n\n")
                for s in slow_responses:
                    f.write(f"- **{s['time']:.1f}s** (+{s['delta']:.1f}s): {s['role']} - {s['content']}...\n")
                f.write("\n")
            if errors:
                f.write("### Errors\n\n")
                for e in errors:
                    f.write(f"- **{e['time']:.1f}s**: ")
                    try:
                        err = json.loads(e['content'])
                        f.write(f"`{err.get('error', err.get('message', 'Unknown error'))}`\n")
                    except:
                        f.write(f"`{e['content'][:100]}`\n")
                f.write("\n")

        # Timeline
        f.write("## Full Timeline\n\n")
        f.write("Legend: TIME = seconds from call start, DELTA = time since previous event\n\n")
        f.write("```\n")
        f.write(f"{'TIME':>7} {'DELTA':>8}  {'TYPE':<14}  CONTENT\n")
        f.write("-" * 100 + "\n")

        for p in processed:
            item = p["item"]
            role = item.get("role", "")
            content = item.get("content", "")
            curr_time = p["time"]
            delta = p["delta"]
            node_num = p["node_num"]

            time_str = f"{curr_time:.1f}s" if curr_time is not None else ""
            delta_str = f"+{delta:.1f}s" if delta is not None else ""

            # Mark slow with asterisk
            slow_marker = " *SLOW*" if delta is not None and delta > 5.0 else ""

            if role == "agent":
                f.write(f"{time_str:>7} {delta_str:>8}  {'AGENT':<14}  {content}\n")
            elif role == "user":
                f.write(f"{time_str:>7} {delta_str:>8}  {'USER':<14}  {content}\n")
            elif role == "tool_call_invocation":
                tool_name = item.get("name", "unknown")
                f.write(f"{time_str:>7} {delta_str:>8}  {'TOOL_CALL':<14}  {tool_name}{slow_marker}\n")
                try:
                    args = json.loads(item.get("arguments", "{}"))
                    for k, v in args.items():
                        f.write(f"{'':>7} {'':>8}  {'':>14}    {k}: {json.dumps(v)}\n")
                except:
                    pass
            elif role == "tool_call_result":
                f.write(f"{time_str:>7} {delta_str:>8}  {'TOOL_RESULT':<14}  ")
                try:
                    result = json.loads(content) if content else {}
                    # Compact important fields
                    if "error" in result:
                        f.write(f"ERROR: {result['error']}\n")
                    elif "found" in result:
                        f.write(f"found={result['found']}")
                        if result.get("patient", {}).get("full_name"):
                            f.write(f", patient={result['patient']['full_name']}")
                        f.write("\n")
                    elif "success" in result:
                        f.write(f"success={result['success']}")
                        if result.get("message"):
                            f.write(f", message={result['message']}")
                        if result.get("duration_ms"):
                            f.write(f" ({result['duration_ms']}ms)")
                        f.write("\n")
                        # Show relevant details on next lines
                        for key in ['class_name', 'class_date', 'spots_available', 'booking_id']:
                            if key in result:
                                f.write(f"{'':>7} {'':>8}  {'':>14}    {key}: {result[key]}\n")
                    else:
                        # Compact JSON output
                        compact = json.dumps(result, separators=(',', ':'))
                        if len(compact) > 80:
                            f.write(f"\n")
                            for k, v in result.items():
                                f.write(f"{'':>7} {'':>8}  {'':>14}    {k}: {json.dumps(v)[:60]}\n")
                        else:
                            f.write(f"{compact}\n")
                except:
                    f.write(f"{content[:80]}\n")
            elif role == "node_transition":
                f.write(f"{'':>7} {'':>8}  {'----- NODE ' + str(node_num) + ' -----':<60}\n")

        f.write("```\n\n")

        # Summary stats
        agent_msgs = sum(1 for i in timeline if i.get("role") == "agent")
        user_msgs = sum(1 for i in timeline if i.get("role") == "user")
        tool_calls = sum(1 for i in timeline if i.get("role") == "tool_call_invocation")
        tool_results = sum(1 for i in timeline if i.get("role") == "tool_call_result")
        nodes = sum(1 for i in timeline if i.get("role") == "node_transition")

        f.write("## Summary\n\n")
        f.write(f"| Metric | Count |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Agent messages | {agent_msgs} |\n")
        f.write(f"| User messages | {user_msgs} |\n")
        f.write(f"| Tool calls | {tool_calls} |\n")
        f.write(f"| Tool results | {tool_results} |\n")
        f.write(f"| Node transitions | {nodes} |\n")
        f.write(f"| Slow responses (>5s) | {len(slow_responses)} |\n")
        f.write(f"| Errors | {len(errors)} |\n")

        # Analysis hints for Claude
        f.write("\n## Analysis Notes\n\n")
        f.write("When analyzing this call:\n")
        f.write("1. Check for slow responses (marked *SLOW* or >5s delta) - these indicate webhook or processing delays\n")
        f.write("2. Look for errors in TOOL_RESULT - these may indicate webhook failures or invalid data\n")
        f.write("3. Node transitions show agent flow - unexpected transitions may indicate logic issues\n")
        f.write("4. Compare user intent vs agent response to identify misunderstandings\n")
        f.write("5. Check if tool calls have correct parameters based on conversation context\n")

    return str(filepath)


def export_full_debug(call_id: str, call_info: dict, raw_data: dict, timeline: list) -> str:
    """Export comprehensive debug info for Claude - includes everything"""
    import json
    import requests
    from pathlib import Path
    from datetime import datetime

    downloads = Path.home() / "Downloads"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debug_{call_id[:20]}_{ts}.md"
    filepath = downloads / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        # Header
        f.write("# Full Call Debug Export\n\n")
        f.write("**Complete debug information for RetellAI call analysis.**\n")
        f.write("This export contains ALL available data - use for deep debugging of agent/webhook issues.\n\n")
        f.write("---\n\n")

        # ==================== CALL METADATA ====================
        f.write("## 1. Call Metadata\n\n")
        f.write("| Field | Value |\n")
        f.write("|-------|-------|\n")
        f.write(f"| Call ID | `{call_id}` |\n")
        f.write(f"| Agent ID | `{call_info.get('retell_agent_id', '-')}` |\n")
        f.write(f"| Agent Name | {call_info.get('retell_agent_name', '-')} |\n")
        f.write(f"| Direction | {call_info.get('direction', '-')} |\n")
        f.write(f"| From | {call_info.get('from_number', '-')} |\n")
        f.write(f"| To | {call_info.get('to_number', '-')} |\n")
        f.write(f"| Started | {call_info.get('started_at', '-')} |\n")
        f.write(f"| Ended | {call_info.get('ended_at', '-')} |\n")
        f.write(f"| Duration | {call_info.get('duration_seconds', '-')} seconds |\n")
        f.write(f"| Status | {call_info.get('status', '-')} |\n")
        f.write(f"| Disposition | {call_info.get('disposition', '-')} |\n")
        f.write(f"| Hangup Cause | {call_info.get('hangup_cause', '-')} |\n")
        f.write(f"| Disconnection Reason | {raw_data.get('disconnection_reason', '-')} |\n")
        f.write(f"| Cost | {call_info.get('cost', '-')} {call_info.get('currency', '')} |\n\n")

        # ==================== LATENCY METRICS ====================
        latency = raw_data.get('latency', {})
        if latency and any(v is not None for v in latency.values()):
            f.write("## 2. Latency Metrics\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            for k, v in latency.items():
                if v is not None:
                    f.write(f"| {k} | {v} ms |\n")
            f.write("\n")

        # ==================== DYNAMIC VARIABLES ====================
        collected_vars = raw_data.get('collected_dynamic_variables', {})
        llm_vars = raw_data.get('retell_llm_dynamic_variables', {})

        if collected_vars or llm_vars:
            f.write("## 3. Dynamic Variables\n\n")

            if collected_vars:
                f.write("### Collected Variables (Final State)\n\n")
                f.write("```json\n")
                f.write(json.dumps(collected_vars, indent=2))
                f.write("\n```\n\n")

            if llm_vars:
                f.write("### LLM Dynamic Variables\n\n")
                f.write("```json\n")
                f.write(json.dumps(llm_vars, indent=2))
                f.write("\n```\n\n")

        # ==================== CALL ANALYSIS ====================
        analysis = raw_data.get('call_analysis', {})
        if analysis:
            f.write("## 4. Call Analysis (AI-Generated)\n\n")
            f.write("```json\n")
            f.write(json.dumps(analysis, indent=2))
            f.write("\n```\n\n")

        # ==================== TIMELINE WITH FULL DETAILS ====================
        f.write("## 5. Full Timeline\n\n")

        if timeline:
            # Pre-process for timing
            prev_time = 0.0
            node_counter = 0

            for idx, item in enumerate(timeline):
                role = item.get("role", "")
                content = item.get("content", "")
                words = item.get("words", [])

                # Get timestamp
                curr_time = None
                if words and len(words) > 0 and isinstance(words[0], dict):
                    curr_time = words[0].get("start", 0)

                if role == "node_transition":
                    node_counter += 1

                # Calculate delta
                delta = None
                delta_note = ""
                if curr_time is not None:
                    delta = curr_time - prev_time
                    prev_time = curr_time
                    if delta > 5.0:
                        delta_note = " **⚠️ SLOW**"
                    elif delta > 2.0:
                        delta_note = " *(slow)*"

                time_str = f"{curr_time:.2f}s" if curr_time is not None else "-"
                delta_str = f"+{delta:.2f}s" if delta is not None else "-"

                f.write(f"### Event {idx + 1}: {role.upper()}\n\n")
                f.write(f"- **Time:** {time_str}\n")
                f.write(f"- **Delta:** {delta_str}{delta_note}\n")

                if role == "agent":
                    f.write(f"- **Type:** Agent Speech\n\n")
                    f.write(f"**Content:**\n> {content}\n\n")

                elif role == "user":
                    f.write(f"- **Type:** User Speech\n\n")
                    f.write(f"**Content:**\n> {content}\n\n")

                elif role == "tool_call_invocation":
                    tool_name = item.get("name", "unknown")
                    tool_id = item.get("tool_call_id", "")
                    args = item.get("arguments", "{}")

                    f.write(f"- **Type:** Tool Call\n")
                    f.write(f"- **Tool Name:** `{tool_name}`\n")
                    if tool_id:
                        f.write(f"- **Tool Call ID:** `{tool_id}`\n")
                    f.write(f"\n**Arguments:**\n```json\n")
                    try:
                        args_dict = json.loads(args) if args else {}
                        f.write(json.dumps(args_dict, indent=2))
                    except:
                        f.write(args)
                    f.write("\n```\n\n")

                elif role == "tool_call_result":
                    f.write(f"- **Type:** Tool Result\n\n")
                    f.write(f"**Result:**\n```json\n")
                    try:
                        result = json.loads(content) if content else {}
                        f.write(json.dumps(result, indent=2))
                    except:
                        f.write(content or "(empty)")
                    f.write("\n```\n\n")

                elif role == "node_transition":
                    f.write(f"- **Type:** Node Transition (Node {node_counter})\n\n")
                    f.write("---\n\n")
                else:
                    f.write(f"- **Type:** {role}\n\n")
                    if content:
                        f.write(f"**Content:**\n```\n{content}\n```\n\n")
        else:
            f.write("*No timeline data available for this call.*\n\n")

        # ==================== TOKEN USAGE ====================
        token_usage = raw_data.get('llm_token_usage', {})
        if token_usage:
            f.write("## 6. LLM Token Usage\n\n")
            f.write("```json\n")
            f.write(json.dumps(token_usage, indent=2))
            f.write("\n```\n\n")

        # ==================== SIP HEADERS ====================
        sip_headers = raw_data.get('custom_sip_headers', {})
        if sip_headers:
            f.write("## 7. Custom SIP Headers\n\n")
            f.write("```json\n")
            f.write(json.dumps(sip_headers, indent=2))
            f.write("\n```\n\n")

        # ==================== PUBLIC LOG ====================
        public_log_url = raw_data.get('public_log_url', '')
        if public_log_url:
            f.write("## 8. Public Log (LLM Reasoning)\n\n")
            f.write(f"**URL:** {public_log_url}\n\n")

            # Try to fetch the log
            try:
                resp = requests.get(public_log_url, timeout=30)
                if resp.status_code == 200:
                    log_content = resp.text
                    f.write("**Log Contents:**\n\n")
                    f.write("```\n")
                    # Limit to reasonable size
                    if len(log_content) > 50000:
                        f.write(log_content[:50000])
                        f.write("\n\n... (truncated - log exceeds 50KB) ...\n")
                    else:
                        f.write(log_content)
                    f.write("\n```\n\n")
                else:
                    f.write(f"*Could not fetch log: HTTP {resp.status_code}*\n\n")
            except Exception as e:
                f.write(f"*Could not fetch log: {str(e)}*\n\n")

        # ==================== RAW DATA DUMP ====================
        f.write("## 9. Complete Raw Data\n\n")
        f.write("Full raw_data from RetellAI API (for reference):\n\n")
        f.write("```json\n")
        # Remove the transcript_with_tool_calls since we already showed it above
        raw_copy = {k: v for k, v in raw_data.items() if k not in ['transcript_with_tool_calls', 'transcript_object']}
        f.write(json.dumps(raw_copy, indent=2, default=str))
        f.write("\n```\n\n")

        # ==================== DEBUGGING CHECKLIST ====================
        f.write("---\n\n")
        f.write("## Debugging Checklist\n\n")
        f.write("When analyzing this call, check:\n\n")
        f.write("1. **Slow Responses** - Look for `⚠️ SLOW` markers in timeline (>5s delay)\n")
        f.write("2. **Tool Errors** - Check tool results for `error`, `success: false`, or unexpected values\n")
        f.write("3. **Node Flow** - Verify node transitions match expected agent flow\n")
        f.write("4. **Variables** - Check collected_dynamic_variables for state issues\n")
        f.write("5. **Disconnection** - Check disconnection_reason for unexpected hangups\n")
        f.write("6. **Public Log** - Search for LLM reasoning issues in Section 8\n")
        f.write("7. **Tool Arguments** - Verify webhook calls have correct parameters\n")

    return str(filepath)


def show_call_details(conn, call_ids: List[str], creds: Dict[str, str]):
    """Show comprehensive details for selected calls with export option"""
    import json

    cur = conn.cursor()
    all_call_data = []

    for call_id in call_ids:
        call_data = {"call_id": call_id}

        # Get main call data
        cur.execute("""
            SELECT c.*, p.name as provider_name
            FROM telco.calls c
            JOIN telco.providers p ON c.provider_id = p.provider_id
            WHERE c.external_call_id = %s
        """, (call_id,))

        call_row = cur.fetchone()
        if call_row:
            col_names = [desc[0] for desc in cur.description]
            call_data["call_info"] = dict(zip(col_names, call_row))

            # Convert datetime objects to strings for JSON
            for key, val in call_data["call_info"].items():
                if isinstance(val, datetime):
                    call_data["call_info"][key] = val.isoformat()

        # Get call analysis if available
        cur.execute("""
            SELECT * FROM telco.call_analysis WHERE call_id = %s
        """, (call_id,))

        analysis_row = cur.fetchone()
        if analysis_row:
            col_names = [desc[0] for desc in cur.description]
            call_data["call_analysis"] = dict(zip(col_names, analysis_row))
            for key, val in call_data["call_analysis"].items():
                if isinstance(val, datetime):
                    call_data["call_analysis"][key] = val.isoformat()

        # Get agent info if we have agent_id
        agent_id = call_data.get("call_info", {}).get("agent_id") or call_data.get("call_info", {}).get("retell_agent_id")
        if agent_id:
            cur.execute("""
                SELECT * FROM telco.retell_agents WHERE agent_id = %s
            """, (agent_id,))

            agent_row = cur.fetchone()
            if agent_row:
                col_names = [desc[0] for desc in cur.description]
                call_data["agent_info"] = dict(zip(col_names, agent_row))
                for key, val in call_data["agent_info"].items():
                    if isinstance(val, datetime):
                        call_data["agent_info"][key] = val.isoformat()

                # Get voice config if we have voice_id
                voice_id = call_data["agent_info"].get("voice_id")
                if voice_id:
                    cur.execute("""
                        SELECT * FROM telco.voice_configs WHERE voice_id = %s
                    """, (voice_id,))
                    voice_row = cur.fetchone()
                    if voice_row:
                        col_names = [desc[0] for desc in cur.description]
                        call_data["voice_config"] = dict(zip(col_names, voice_row))
                        for key, val in call_data["voice_config"].items():
                            if isinstance(val, datetime):
                                call_data["voice_config"][key] = val.isoformat()

        all_call_data.append(call_data)

    # Display the data
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header(f"CALL DETAILS - {len(call_ids)} Call(s) Selected")

        for idx, data in enumerate(all_call_data, 1):
            call_info = data.get("call_info", {})
            analysis = data.get("call_analysis", {})
            agent = data.get("agent_info", {})
            voice = data.get("voice_config", {})

            print(f"\n  {Colors.BOLD}{'='*70}{Colors.RESET}")
            print(f"  {Colors.CYAN}CALL {idx}: {data['call_id']}{Colors.RESET}")
            print(f"  {Colors.BOLD}{'='*70}{Colors.RESET}")

            # Basic call info
            print(f"\n  {Colors.BOLD}CALL INFORMATION:{Colors.RESET}")
            print(f"    Started:     {call_info.get('started_at', '-')}")
            print(f"    Ended:       {call_info.get('ended_at', '-')}")
            print(f"    From:        {call_info.get('from_number', '-')}")
            print(f"    To:          {call_info.get('to_number', '-')}")
            print(f"    Direction:   {call_info.get('direction', '-')}")
            print(f"    Duration:    {call_info.get('duration_seconds', '-')} seconds")
            print(f"    Status:      {call_info.get('status', '-')}")
            print(f"    Cost:        ${call_info.get('cost', 0) or 0:.4f}")

            if call_info.get('recording_url'):
                print(f"    Recording:   {Colors.GREEN}Available{Colors.RESET}")

            # Agent info
            if agent:
                print(f"\n  {Colors.BOLD}AGENT INFORMATION:{Colors.RESET}")
                print(f"    Agent Name:  {agent.get('agent_name', '-')}")
                print(f"    Agent ID:    {agent.get('agent_id', '-')}")
                print(f"    Voice ID:    {agent.get('voice_id', '-')}")
                print(f"    Language:    {agent.get('language', '-')}")
                if agent.get('webhook_url'):
                    print(f"    Webhook:     {agent.get('webhook_url', '-')}")
            else:
                print(f"\n  {Colors.BOLD}AGENT INFORMATION:{Colors.RESET}")
                print(f"    Agent Name:  {call_info.get('retell_agent_name', '-')}")

            # Voice config
            if voice:
                print(f"\n  {Colors.BOLD}VOICE CONFIGURATION:{Colors.RESET}")
                print(f"    Voice Name:  {voice.get('voice_name', '-')}")
                print(f"    Provider:    {voice.get('provider_voice', '-')}")
                print(f"    Language:    {voice.get('language', '-')}")
                print(f"    Gender:      {voice.get('gender', '-')}")
                print(f"    Accent:      {voice.get('accent', '-')}")

            # Call analysis
            if analysis:
                print(f"\n  {Colors.BOLD}CALL ANALYSIS:{Colors.RESET}")
                print(f"    Summary:     {analysis.get('call_summary', '-')}")
                print(f"    Sentiment:   Call: {analysis.get('call_sentiment', '-')} | User: {analysis.get('user_sentiment', '-')}")
                print(f"    Successful:  {analysis.get('call_successful', '-')}")
                print(f"    Voicemail:   {analysis.get('in_voicemail', '-')}")
                if analysis.get('latency_stats'):
                    print(f"    Latency:     {analysis.get('latency_stats', '-')}")

            # Transcript preview
            transcript = call_info.get('full_transcript', '')
            if transcript:
                print(f"\n  {Colors.BOLD}TRANSCRIPT PREVIEW:{Colors.RESET}")
                preview = transcript[:500].replace('\n', ' ').replace('\r', '')
                if len(transcript) > 500:
                    preview += "..."
                print(f"    {Colors.DIM}{preview}{Colors.RESET}")
                print(f"    {Colors.DIM}(Total: {call_info.get('transcript_words', 0)} words){Colors.RESET}")

            # Raw data available
            if call_info.get('raw_data'):
                print(f"\n  {Colors.DIM}Raw API data available in export{Colors.RESET}")

        # Options
        print(f"\n  {Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"\n  {Colors.BOLD}OPTIONS:{Colors.RESET}")
        print(f"    {Colors.CYAN}T{Colors.RESET} - {Colors.BOLD}View full transcript(s){Colors.RESET}")
        print(f"    {Colors.CYAN}L{Colors.RESET} - {Colors.BOLD}View call timeline{Colors.RESET} (transcript + tool calls)")
        print(f"    {Colors.CYAN}P{Colors.RESET} - Play recording(s) in browser")
        print()
        print(f"  {Colors.BOLD}EXPORT:{Colors.RESET}")
        print(f"    {Colors.CYAN}1{Colors.RESET} - Export to current folder (default)")
        print(f"    {Colors.CYAN}2{Colors.RESET} - Export to Downloads folder")
        print(f"    {Colors.CYAN}3{Colors.RESET} - Export to Desktop")
        print(f"    {Colors.CYAN}4{Colors.RESET} - Export to CC folder")
        print(f"    {Colors.CYAN}5{Colors.RESET} - Custom path")
        print()
        print(f"    {Colors.CYAN}Q{Colors.RESET} - Back to call list")
        print()

        choice = input(f"  {Colors.BOLD}Select: {Colors.RESET}").strip().upper()

        if choice == 'Q' or choice == '':
            break

        elif choice == 'T':
            # Show full transcripts
            show_full_transcripts(all_call_data)

        elif choice == 'L':
            # Show call timeline
            show_call_timeline(all_call_data)

        elif choice == 'P':
            # Play recordings
            for data in all_call_data:
                rec_url = data.get("call_info", {}).get("recording_url")
                if rec_url:
                    print(f"\n  {Colors.GREEN}Opening recording: {data['call_id']}{Colors.RESET}")
                    open_url(rec_url)
            input(f"\n  {Colors.DIM}Press Enter to continue...{Colors.RESET}")

        elif choice in ['1', '2', '3', '4', '5']:
            # Determine export path
            if choice == '1':
                export_dir = Path.cwd()
            elif choice == '2':
                export_dir = Path.home() / "Downloads"
            elif choice == '3':
                export_dir = Path.home() / "Desktop"
            elif choice == '4':
                export_dir = Path.home() / "Downloads" / "CC"
            elif choice == '5':
                custom_path = input(f"  Enter path: ").strip()
                if not custom_path:
                    print(f"  {Colors.RED}No path entered{Colors.RESET}")
                    input(f"  {Colors.DIM}Press Enter to continue...{Colors.RESET}")
                    continue
                export_dir = Path(custom_path)

            # Create directory if needed
            export_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if len(call_ids) == 1:
                filename = f"retell_call_{call_ids[0][:8]}_{timestamp}.json"
            else:
                filename = f"retell_calls_{len(call_ids)}calls_{timestamp}.json"

            export_path = export_dir / filename

            # Prepare export data
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "call_count": len(all_call_data),
                "calls": all_call_data
            }

            # Write JSON file
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)

                print(f"\n  {Colors.GREEN}Exported successfully!{Colors.RESET}")
                print(f"  {Colors.DIM}{export_path}{Colors.RESET}")

                # Also create a readable text version
                txt_path = export_path.with_suffix('.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"RETELL CALLS EXPORT\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Calls: {len(all_call_data)}\n")
                    f.write("="*70 + "\n\n")

                    for data in all_call_data:
                        call_info = data.get("call_info", {})
                        analysis = data.get("call_analysis", {})

                        f.write(f"CALL ID: {data['call_id']}\n")
                        f.write("-"*50 + "\n")
                        f.write(f"Time: {call_info.get('started_at', '-')}\n")
                        f.write(f"From: {call_info.get('from_number', '-')}\n")
                        f.write(f"To: {call_info.get('to_number', '-')}\n")
                        f.write(f"Duration: {call_info.get('duration_seconds', '-')} seconds\n")
                        f.write(f"Agent: {call_info.get('retell_agent_name', '-')}\n")
                        f.write(f"Status: {call_info.get('status', '-')}\n")
                        if call_info.get('recording_url'):
                            f.write(f"Recording: {call_info.get('recording_url')}\n")

                        if analysis:
                            f.write(f"\nAnalysis:\n")
                            f.write(f"  Summary: {analysis.get('call_summary', '-')}\n")
                            f.write(f"  Sentiment: {analysis.get('call_sentiment', '-')}\n")
                            f.write(f"  Successful: {analysis.get('call_successful', '-')}\n")

                        if call_info.get('full_transcript'):
                            f.write(f"\nTranscript:\n{call_info.get('full_transcript')}\n")

                        f.write("\n" + "="*70 + "\n\n")

                print(f"  {Colors.DIM}Text version: {txt_path}{Colors.RESET}")

            except Exception as e:
                print(f"\n  {Colors.RED}Export failed: {e}{Colors.RESET}")

            input(f"\n  {Colors.DIM}Press Enter to continue...{Colors.RESET}")


# ============================================================================
# LATENCY COMPARISON
# ============================================================================

def show_latency_comparison(creds: Dict[str, str]):
    """Compare voice agent latency for calls through Telnyx vs Zadarma"""
    if not POSTGRES_AVAILABLE:
        print(f"  {Colors.RED}psycopg2 not installed. Run: pip install psycopg2-binary{Colors.RESET}")
        return

    conn = get_db_connection(creds)
    if not conn:
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    print_header("TELCO LATENCY COMPARISON")

    print(f"""
  {Colors.BOLD}Understanding Voice Agent Latency{Colors.RESET}
  {Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}

  When a caller speaks to an AI voice agent, the total response delay (E2E) includes:

  {Colors.CYAN}1. Telco Network Delay{Colors.RESET}     - Audio packets through carrier network
  {Colors.CYAN}2. Speech-to-Text (STT){Colors.RESET}   - Converting speech to text (Retell)
  {Colors.CYAN}3. LLM Processing{Colors.RESET}         - AI thinking time (GPT-4o, Claude, etc.)
  {Colors.CYAN}4. Knowledge Base{Colors.RESET}         - Looking up information
  {Colors.CYAN}5. Text-to-Speech (TTS){Colors.RESET}   - Converting response to audio
  {Colors.CYAN}6. Telco Return Path{Colors.RESET}      - Audio back to caller

  {Colors.YELLOW}Note:{Colors.RESET} Telco delay is embedded in E2E but not separately measured.
  We compare calls through different telcos to infer network differences.

  {Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
""")

    cur = conn.cursor()

    # Map phone numbers to telcos
    ZADARMA_NUMBER = '+61288800226'
    TELNYX_NUMBER = '+61240620999'

    # Get latency stats for Zadarma-routed calls
    cur.execute("""
        SELECT
            COUNT(*) as total_calls,
            COUNT(CASE WHEN raw_data->'latency' IS NOT NULL THEN 1 END) as calls_with_latency,
            AVG((raw_data->'latency'->'e2e'->>'p50')::float) as avg_e2e_p50,
            AVG((raw_data->'latency'->'e2e'->>'p90')::float) as avg_e2e_p90,
            AVG((raw_data->'latency'->'llm'->>'p50')::float) as avg_llm_p50,
            AVG((raw_data->'latency'->'tts'->>'p50')::float) as avg_tts_p50,
            AVG((raw_data->'latency'->'knowledge_base'->>'p50')::float) as avg_kb_p50,
            MIN((raw_data->'latency'->'e2e'->>'min')::float) as best_e2e,
            MAX((raw_data->'latency'->'e2e'->>'max')::float) as worst_e2e,
            AVG(duration_seconds) as avg_duration
        FROM telco.calls c
        JOIN telco.providers p ON c.provider_id = p.provider_id
        WHERE p.name = 'retell'
          AND to_number = %s
          AND raw_data->'latency'->'e2e' IS NOT NULL
    """, (ZADARMA_NUMBER,))
    zadarma_stats = cur.fetchone()

    # Get latency stats for Telnyx-routed calls
    cur.execute("""
        SELECT
            COUNT(*) as total_calls,
            COUNT(CASE WHEN raw_data->'latency' IS NOT NULL THEN 1 END) as calls_with_latency,
            AVG((raw_data->'latency'->'e2e'->>'p50')::float) as avg_e2e_p50,
            AVG((raw_data->'latency'->'e2e'->>'p90')::float) as avg_e2e_p90,
            AVG((raw_data->'latency'->'llm'->>'p50')::float) as avg_llm_p50,
            AVG((raw_data->'latency'->'tts'->>'p50')::float) as avg_tts_p50,
            AVG((raw_data->'latency'->'knowledge_base'->>'p50')::float) as avg_kb_p50,
            MIN((raw_data->'latency'->'e2e'->>'min')::float) as best_e2e,
            MAX((raw_data->'latency'->'e2e'->>'max')::float) as worst_e2e,
            AVG(duration_seconds) as avg_duration
        FROM telco.calls c
        JOIN telco.providers p ON c.provider_id = p.provider_id
        WHERE p.name = 'retell'
          AND to_number = %s
          AND raw_data->'latency'->'e2e' IS NOT NULL
    """, (TELNYX_NUMBER,))
    telnyx_stats = cur.fetchone()

    # Display comparison table
    print(f"  {Colors.BOLD}AGGREGATE STATISTICS{Colors.RESET}")
    print(f"  {Colors.DIM}(All times in milliseconds){Colors.RESET}\n")

    headers = ["Metric", "Zadarma", "Telnyx", "Difference", "Winner"]
    col_widths = [25, 15, 15, 15, 12]

    def safe_val(val, fmt=".0f"):
        if val is None:
            return "-"
        return f"{val:{fmt}}"

    def compare(z_val, t_val, lower_better=True):
        if z_val is None or t_val is None:
            return "-", "-"
        diff = z_val - t_val
        if lower_better:
            winner = f"{Colors.GREEN}Telnyx{Colors.RESET}" if diff > 0 else f"{Colors.GREEN}Zadarma{Colors.RESET}"
        else:
            winner = f"{Colors.GREEN}Zadarma{Colors.RESET}" if diff > 0 else f"{Colors.GREEN}Telnyx{Colors.RESET}"
        diff_str = f"+{diff:.0f}" if diff > 0 else f"{diff:.0f}"
        return diff_str, winner

    rows = []

    # Calls analyzed
    z_calls = zadarma_stats[0] if zadarma_stats else 0
    t_calls = telnyx_stats[0] if telnyx_stats else 0
    rows.append(["Calls Analyzed", str(z_calls), str(t_calls), "-", "-"])

    # E2E Latency (p50)
    z_e2e = zadarma_stats[2] if zadarma_stats else None
    t_e2e = telnyx_stats[2] if telnyx_stats else None
    diff, winner = compare(z_e2e, t_e2e)
    rows.append([f"{Colors.BOLD}E2E Latency (p50){Colors.RESET}", safe_val(z_e2e), safe_val(t_e2e), diff, winner])

    # E2E Latency (p90)
    z_e2e90 = zadarma_stats[3] if zadarma_stats else None
    t_e2e90 = telnyx_stats[3] if telnyx_stats else None
    diff, winner = compare(z_e2e90, t_e2e90)
    rows.append(["E2E Latency (p90)", safe_val(z_e2e90), safe_val(t_e2e90), diff, winner])

    # Best E2E
    z_best = zadarma_stats[7] if zadarma_stats else None
    t_best = telnyx_stats[7] if telnyx_stats else None
    diff, winner = compare(z_best, t_best)
    rows.append(["Best E2E", safe_val(z_best), safe_val(t_best), diff, winner])

    # Worst E2E
    z_worst = zadarma_stats[8] if zadarma_stats else None
    t_worst = telnyx_stats[8] if telnyx_stats else None
    diff, winner = compare(z_worst, t_worst)
    rows.append(["Worst E2E", safe_val(z_worst), safe_val(t_worst), diff, winner])

    rows.append(["", "", "", "", ""])  # Spacer

    # Breakdown
    rows.append([f"{Colors.DIM}--- Latency Breakdown ---{Colors.RESET}", "", "", "", ""])

    # LLM
    z_llm = zadarma_stats[4] if zadarma_stats else None
    t_llm = telnyx_stats[4] if telnyx_stats else None
    diff, winner = compare(z_llm, t_llm)
    rows.append(["LLM Processing (p50)", safe_val(z_llm), safe_val(t_llm), diff, winner])

    # TTS
    z_tts = zadarma_stats[5] if zadarma_stats else None
    t_tts = telnyx_stats[5] if telnyx_stats else None
    diff, winner = compare(z_tts, t_tts)
    rows.append(["TTS (p50)", safe_val(z_tts), safe_val(t_tts), diff, winner])

    # KB
    z_kb = zadarma_stats[6] if zadarma_stats else None
    t_kb = telnyx_stats[6] if telnyx_stats else None
    diff, winner = compare(z_kb, t_kb)
    rows.append(["Knowledge Base (p50)", safe_val(z_kb), safe_val(t_kb), diff, winner])

    # Inferred telco delay
    if z_e2e and z_llm and z_tts and t_e2e and t_llm and t_tts:
        z_other = z_e2e - z_llm - z_tts - (z_kb or 0)
        t_other = t_e2e - t_llm - t_tts - (t_kb or 0)
        diff, winner = compare(z_other, t_other)
        rows.append([f"{Colors.YELLOW}Other (STT+Network){Colors.RESET}", safe_val(z_other), safe_val(t_other), diff, winner])

    print_table(headers, rows, col_widths)

    # Get recent calls for each
    print(f"\n\n  {Colors.BOLD}LAST 10 CALLS - ZADARMA ({ZADARMA_NUMBER}){Colors.RESET}\n")

    cur.execute("""
        SELECT started_at, duration_seconds, retell_agent_name,
               (raw_data->'latency'->'e2e'->>'p50')::float as e2e,
               (raw_data->'latency'->'llm'->>'p50')::float as llm,
               (raw_data->'latency'->'tts'->>'p50')::float as tts
        FROM telco.calls c
        JOIN telco.providers p ON c.provider_id = p.provider_id
        WHERE p.name = 'retell'
          AND to_number = %s
          AND raw_data->'latency'->'e2e' IS NOT NULL
        ORDER BY started_at DESC
        LIMIT 10
    """, (ZADARMA_NUMBER,))

    zadarma_calls = cur.fetchall()
    if zadarma_calls:
        headers2 = ["Time", "Dur", "Agent", "E2E", "LLM", "TTS"]
        widths2 = [18, 6, 40, 10, 10, 10]
        rows2 = []
        for call in zadarma_calls:
            time_str = call[0].strftime("%Y-%m-%d %H:%M") if call[0] else "-"
            agent = (call[2][:38] + "..") if call[2] and len(call[2]) > 40 else (call[2] or "-")
            rows2.append([
                time_str,
                f"{call[1]}s" if call[1] else "-",
                agent,
                f"{call[3]:.0f}ms" if call[3] else "-",
                f"{call[4]:.0f}ms" if call[4] else "-",
                f"{call[5]:.0f}ms" if call[5] else "-"
            ])
        print_table(headers2, rows2, widths2)
    else:
        print(f"  {Colors.YELLOW}No Zadarma calls with latency data{Colors.RESET}")

    print(f"\n\n  {Colors.BOLD}LAST 10 CALLS - TELNYX ({TELNYX_NUMBER}){Colors.RESET}\n")

    cur.execute("""
        SELECT started_at, duration_seconds, retell_agent_name,
               (raw_data->'latency'->'e2e'->>'p50')::float as e2e,
               (raw_data->'latency'->'llm'->>'p50')::float as llm,
               (raw_data->'latency'->'tts'->>'p50')::float as tts
        FROM telco.calls c
        JOIN telco.providers p ON c.provider_id = p.provider_id
        WHERE p.name = 'retell'
          AND to_number = %s
          AND raw_data->'latency'->'e2e' IS NOT NULL
        ORDER BY started_at DESC
        LIMIT 10
    """, (TELNYX_NUMBER,))

    telnyx_calls = cur.fetchall()
    if telnyx_calls:
        rows2 = []
        for call in telnyx_calls:
            time_str = call[0].strftime("%Y-%m-%d %H:%M") if call[0] else "-"
            agent = (call[2][:38] + "..") if call[2] and len(call[2]) > 40 else (call[2] or "-")
            rows2.append([
                time_str,
                f"{call[1]}s" if call[1] else "-",
                agent,
                f"{call[3]:.0f}ms" if call[3] else "-",
                f"{call[4]:.0f}ms" if call[4] else "-",
                f"{call[5]:.0f}ms" if call[5] else "-"
            ])
        print_table(headers2, rows2, widths2)
    else:
        print(f"  {Colors.YELLOW}No Telnyx calls with latency data{Colors.RESET}")

    # Analysis summary
    print(f"\n\n  {Colors.BOLD}ANALYSIS{Colors.RESET}")
    print(f"  {Colors.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}\n")

    if z_e2e and t_e2e and z_llm and t_llm:
        # Calculate isolated network difference
        z_network_est = z_e2e - z_llm - z_tts - (z_kb or 0)
        t_network_est = t_e2e - t_llm - t_tts - (t_kb or 0)
        net_diff = z_network_est - t_network_est

        print(f"  {Colors.CYAN}E2E Comparison:{Colors.RESET}")
        print(f"    Zadarma avg: {z_e2e:.0f}ms | Telnyx avg: {t_e2e:.0f}ms")
        e2e_diff = z_e2e - t_e2e
        if abs(e2e_diff) < 50:
            print(f"    {Colors.GREEN}→ Difference is negligible (<50ms){Colors.RESET}")
        elif e2e_diff > 0:
            print(f"    {Colors.YELLOW}→ Telnyx is {e2e_diff:.0f}ms faster on average{Colors.RESET}")
        else:
            print(f"    {Colors.YELLOW}→ Zadarma is {-e2e_diff:.0f}ms faster on average{Colors.RESET}")

        print(f"\n  {Colors.CYAN}Estimated Network Component:{Colors.RESET}")
        print(f"    (E2E - LLM - TTS - KB = STT + Network overhead)")
        print(f"    Zadarma: ~{z_network_est:.0f}ms | Telnyx: ~{t_network_est:.0f}ms")

        if abs(net_diff) < 30:
            print(f"    {Colors.GREEN}→ Network performance is comparable{Colors.RESET}")
        elif net_diff > 0:
            print(f"    {Colors.YELLOW}→ Telnyx network appears ~{net_diff:.0f}ms faster{Colors.RESET}")
        else:
            print(f"    {Colors.YELLOW}→ Zadarma network appears ~{-net_diff:.0f}ms faster{Colors.RESET}")

        print(f"\n  {Colors.CYAN}Important Caveats:{Colors.RESET}")
        print(f"    • Sample sizes differ ({z_calls} vs {t_calls} calls)")
        print(f"    • Different callers/times may affect results")
        print(f"    • LLM/TTS times dominate; network is minor factor")
        print(f"    • Both telcos route to same Retell servers")
    else:
        print(f"  {Colors.YELLOW}Insufficient data for detailed analysis{Colors.RESET}")
        print(f"  Need calls with latency data through both Zadarma and Telnyx numbers")

    conn.close()
    input(f"\n\n  {Colors.DIM}Press Enter to continue...{Colors.RESET}")


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
    print(f"  {Colors.CYAN}6.{Colors.RESET} Retell Calls Explorer")
    print(f"  {Colors.CYAN}7.{Colors.RESET} {Colors.BOLD}Latency Comparison{Colors.RESET} {Colors.GREEN}NEW{Colors.RESET}")
    print()
    print(f"  {Colors.CYAN}A.{Colors.RESET} Show All")
    print(f"  {Colors.CYAN}S.{Colors.RESET} Full Sync (Pull all data from APIs)")
    print(f"  {Colors.CYAN}R.{Colors.RESET} Quick Sync (Fetch latest since last sync)")
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

        elif choice == '6':
            show_retell_calls_explorer(creds)

        elif choice == '7':
            show_latency_comparison(creds)

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
            # Run incremental sync (quick refresh of latest data)
            print_header("QUICK SYNC - Fetching Latest Data")
            sync_script = Path(__file__).parent / "sync" / "sync_incremental.py"
            if sync_script.exists():
                import subprocess
                print(f"  Running incremental sync...")
                print()
                result = subprocess.run([sys.executable, str(sync_script)], cwd=str(sync_script.parent))
                if result.returncode == 0:
                    print(f"\n  {Colors.GREEN}Sync completed{Colors.RESET}")
                else:
                    print(f"\n  {Colors.RED}Sync failed with code {result.returncode}{Colors.RESET}")
            else:
                print(f"  {Colors.RED}Incremental sync script not found: {sync_script}{Colors.RESET}")
                print(f"  {Colors.DIM}Use 'S' for full sync instead{Colors.RESET}")

        else:
            print(f"{Colors.RED}Invalid option{Colors.RESET}")

        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")


if __name__ == "__main__":
    main()
