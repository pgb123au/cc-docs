#!/usr/bin/env python3
"""
Zadarma API - Get Phone Numbers
Fetches all virtual phone numbers from Zadarma account.
"""

import hashlib
import hmac
import base64
import requests
from datetime import datetime

# API Credentials - loaded from .credentials file
import os
from pathlib import Path

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

_creds = load_credentials()
API_KEY = _creds.get("ZADARMA_API_KEY", os.environ.get("ZADARMA_API_KEY", ""))
API_SECRET = _creds.get("ZADARMA_API_SECRET", os.environ.get("ZADARMA_API_SECRET", ""))
API_BASE = "https://api.zadarma.com"

if not API_KEY or not API_SECRET:
    print("ERROR: Zadarma credentials not found!")
    print("Set ZADARMA_API_KEY and ZADARMA_API_SECRET in Telcos/.credentials or environment")


def generate_signature(method: str, params: dict = None) -> str:
    """Generate HMAC-SHA1 signature for Zadarma API

    Based on official zadarma/user-api-py-v1 implementation:
    1. Sort params, create query string
    2. Build: method + params_string + md5(params_string)
    3. HMAC-SHA1 hexdigest
    4. Base64 encode the hexdigest
    """
    if params:
        # Sort parameters alphabetically by key
        sorted_params = sorted(params.items())
        # URL encode like PHP's http_build_query
        params_string = "&".join(f"{k}={v}" for k, v in sorted_params)
    else:
        params_string = ""

    # MD5 hash of params string (hex digest)
    md5_hash = hashlib.md5(params_string.encode()).hexdigest()

    # Create string to sign: method + params_string + md5(params_string)
    sign_string = f"{method}{params_string}{md5_hash}"

    # Generate HMAC-SHA1 signature - use hexdigest, then base64
    hex_signature = hmac.new(
        API_SECRET.encode(),
        sign_string.encode(),
        hashlib.sha1
    ).hexdigest()

    # Base64 encode the hex string
    return base64.b64encode(hex_signature.encode()).decode()


def api_request(method: str, params: dict = None) -> dict:
    """Make authenticated request to Zadarma API"""
    signature = generate_signature(method, params)

    headers = {
        "Authorization": f"{API_KEY}:{signature}"
    }

    url = f"{API_BASE}{method}"

    if params:
        response = requests.get(url, headers=headers, params=params)
    else:
        response = requests.get(url, headers=headers)

    return response.json()


def get_direct_numbers():
    """Get all virtual phone numbers"""
    return api_request("/v1/direct_numbers/")


def get_sip_numbers():
    """Get SIP account info"""
    return api_request("/v1/sip/")


def get_balance():
    """Get account balance"""
    return api_request("/v1/info/balance/")


def main():
    print("=" * 60)
    print("Zadarma Account Information")
    print("=" * 60)

    # Get balance
    print("\n[Balance]")
    balance = get_balance()
    if balance.get("status") == "success":
        print(f"  Balance: {balance.get('balance', 'N/A')} {balance.get('currency', '')}")
    else:
        print(f"  Error: {balance}")

    # Get SIP accounts
    print("\n[SIP Accounts]")
    sip_info = get_sip_numbers()
    if sip_info.get("status") == "success":
        sips = sip_info.get("sips", [])
        for sip in sips:
            print(f"  SIP ID: {sip.get('id')}")
            print(f"    Display Name: {sip.get('display_name', 'N/A')}")
            print(f"    Caller ID: {sip.get('caller_id', 'N/A')}")
            print()
    else:
        print(f"  Error: {sip_info}")

    # Get phone numbers
    print("\n[Virtual Phone Numbers]")
    numbers = get_direct_numbers()
    if numbers.get("status") == "success":
        info = numbers.get("info", [])
        if not info:
            print("  No virtual numbers found")
        else:
            for num in info:
                print(f"  Number: +{num.get('number')}")
                print(f"    Status: {num.get('status')}")
                print(f"    Country: {num.get('country')}")
                print(f"    Description: {num.get('description', 'N/A')}")
                print(f"    SIP: {num.get('sip')}")
                print(f"    Channels: {num.get('channels')}")
                print(f"    Monthly Fee: {num.get('monthly_fee')} {num.get('currency', 'USD')}")
                print(f"    Auto-renew: {num.get('autorenew')}")
                print()
    else:
        print(f"  Error: {numbers}")

    # Return raw data for documentation
    return {
        "balance": balance,
        "sip": sip_info,
        "numbers": numbers
    }


if __name__ == "__main__":
    main()
