#!/usr/bin/env python3
"""
Import Telnyx Phone Number to RetellAI
Imports a Telnyx number and links it to an agent for inbound/outbound calls.

Place Retell_API_Key.txt in the same folder or Downloads folder.
"""

import os
import json
from pathlib import Path
from typing import Optional

try:
    from retell import Retell
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

# Configuration - Edit these values
PHONE_NUMBER = "+61240620999"
AGENT_ID = "agent_9247a7e76be283256c249b866f"
NICKNAME = "Reignite NSW Office"


def load_credentials():
    """Load credentials from .credentials file"""
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


# Load Telnyx SIP credentials from .credentials file
_creds = load_credentials()
TELNYX_TERMINATION_URI = "sip.telnyx.com"
TELNYX_USERNAME = _creds.get("TELNYX_SIP_USERNAME", os.environ.get("TELNYX_SIP_USERNAME", ""))
TELNYX_PASSWORD = _creds.get("TELNYX_SIP_PASSWORD", os.environ.get("TELNYX_SIP_PASSWORD", ""))


class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'


def print_header(text: str):
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print("=" * 60)


def print_error(text: str):
    print(f"{Colors.RED}[ERROR] {text}{Colors.RESET}")


def print_success(text: str):
    print(f"{Colors.GREEN}[OK] {text}{Colors.RESET}")


def print_info(text: str):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.RESET}")


def read_api_key_from_file() -> Optional[str]:
    """Read API key from Retell_API_Key.txt"""
    search_paths = [
        Path.cwd() / "Retell_API_Key.txt",
        Path(__file__).parent / "Retell_API_Key.txt",
        Path(__file__).parent.parent / "Retell_API_Key.txt",
        Path.home() / "Downloads" / "Retell_API_Key.txt",
        Path.home() / "Downloads" / "CC" / "retell" / "Retell_API_Key.txt",
    ]

    for api_key_file in search_paths:
        if api_key_file.exists():
            try:
                with open(api_key_file, 'r') as f:
                    api_key = f.read().strip()
                    api_key = api_key.replace("API Key:", "").replace("key:", "").strip()
                    if api_key:
                        print_info(f"Found API key in: {api_key_file}")
                        return api_key
            except Exception as e:
                print_error(f"Error reading {api_key_file}: {e}")

    return None


def get_phone_number(api_key: str) -> dict:
    """Get existing phone number details"""
    try:
        client = Retell(api_key=api_key)
        response = client.phone_number.retrieve(phone_number=PHONE_NUMBER)
        return response
    except Exception as e:
        return None


def update_phone_number(api_key: str) -> bool:
    """Update existing phone number with agent bindings"""
    try:
        client = Retell(api_key=api_key)

        print_info(f"Updating phone number: {PHONE_NUMBER}")
        print_info(f"Agent ID: {AGENT_ID}")

        response = client.phone_number.update(
            phone_number=PHONE_NUMBER,
            inbound_agent_id=AGENT_ID,
            outbound_agent_id=AGENT_ID,
            nickname=NICKNAME
        )

        print_success("Phone number updated successfully!")
        print()
        print(f"  Phone Number: {response.phone_number}")
        print(f"  Pretty Format: {response.phone_number_pretty}")
        print(f"  Type: {response.phone_number_type}")
        print(f"  Inbound Agent: {response.inbound_agent_id}")
        print(f"  Outbound Agent: {response.outbound_agent_id}")
        print(f"  Nickname: {getattr(response, 'nickname', 'N/A')}")

        return True

    except Exception as e:
        print_error(f"Failed to update phone number: {e}")
        if hasattr(e, 'body'):
            print_error(f"Error details: {e.body}")
        return False


def import_phone_number(api_key: str) -> bool:
    """Import the Telnyx phone number to RetellAI"""
    try:
        client = Retell(api_key=api_key)

        print_info(f"Importing phone number: {PHONE_NUMBER}")
        print_info(f"Agent ID: {AGENT_ID}")
        print_info(f"Termination URI: {TELNYX_TERMINATION_URI}")

        # Import the phone number
        response = client.phone_number.import_(
            phone_number=PHONE_NUMBER,
            termination_uri=TELNYX_TERMINATION_URI,
            sip_trunk_auth_username=TELNYX_USERNAME,
            sip_trunk_auth_password=TELNYX_PASSWORD,
            inbound_agent_id=AGENT_ID,
            outbound_agent_id=AGENT_ID,
            nickname=NICKNAME
        )

        print_success("Phone number imported successfully!")
        print()
        print(f"  Phone Number: {response.phone_number}")
        print(f"  Pretty Format: {response.phone_number_pretty}")
        print(f"  Type: {response.phone_number_type}")
        print(f"  Inbound Agent: {response.inbound_agent_id}")
        print(f"  Outbound Agent: {response.outbound_agent_id}")
        print(f"  Nickname: {getattr(response, 'nickname', 'N/A')}")

        return True

    except Exception as e:
        error_msg = str(e)

        # Check if number already exists - offer to update instead
        if "already exists" in error_msg.lower():
            print_info("Phone number already exists in Retell. Checking current config...")
            existing = get_phone_number(api_key)

            if existing:
                print()
                print(f"  Current Inbound Agent:  {existing.inbound_agent_id or 'None'}")
                print(f"  Current Outbound Agent: {existing.outbound_agent_id or 'None'}")
                print(f"  Current Nickname:       {getattr(existing, 'nickname', 'N/A')}")
                print()

                update = input(f"{Colors.YELLOW}Update to new agent? (y/n): {Colors.RESET}").strip().lower()
                if update == 'y':
                    return update_phone_number(api_key)

            return False

        print_error(f"Failed to import phone number: {e}")
        if hasattr(e, 'body'):
            print_error(f"Error details: {e.body}")

        return False


def main():
    print_header("Import Telnyx Number to RetellAI")

    if not SDK_AVAILABLE:
        print_error("retell-sdk is not installed!")
        print_info("Install with: pip install retell-sdk")
        return

    # Get API key
    api_key = read_api_key_from_file()
    if not api_key:
        print_error("Could not find Retell_API_Key.txt!")
        print_info("Create Retell_API_Key.txt with your API key in one of these locations:")
        print_info("  - Current directory")
        print_info("  - retell/scripts/ folder")
        print_info("  - Downloads folder")
        return

    print_success(f"API key found: {api_key[:20]}...")

    # Show configuration
    print_header("Configuration")
    print(f"  Phone Number:    {PHONE_NUMBER}")
    print(f"  Agent ID:        {AGENT_ID}")
    print(f"  Nickname:        {NICKNAME}")
    print(f"  Termination URI: {TELNYX_TERMINATION_URI}")
    print(f"  SIP Username:    {TELNYX_USERNAME}")
    print(f"  SIP Password:    {'*' * len(TELNYX_PASSWORD)}")
    print()

    # Confirm
    confirm = input(f"{Colors.YELLOW}Proceed with import? (y/n): {Colors.RESET}").strip().lower()
    if confirm != 'y':
        print_info("Import cancelled")
        return

    # Import
    print_header("Importing Phone Number")
    success = import_phone_number(api_key)

    if success:
        print_header("Import Complete!")
        print_info("The number is now ready for inbound and outbound calls")
        print_info(f"View in dashboard: https://dashboard.retellai.com/phone-numbers")


if __name__ == "__main__":
    main()
