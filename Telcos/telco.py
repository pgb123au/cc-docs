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
    print()
    print(f"  {Colors.CYAN}A.{Colors.RESET} Show All")
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

        elif choice == 'a':
            if zadarma:
                show_zadarma_info(zadarma)
            if telnyx:
                show_telnyx_info(telnyx)
            if retell:
                show_retell_info(retell)

        elif choice == 'r':
            continue

        else:
            print(f"{Colors.RED}Invalid option{Colors.RESET}")

        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")


if __name__ == "__main__":
    main()
