"""
Mobile Message SMS API Integration for Yes AI Marketing
https://mobilemessage.com.au/

Usage:
    from mobilemessage import MobileMessageClient
    client = MobileMessageClient()
    client.send_sms("0412345678", "Hello from Yes AI!")
"""

import requests
from pathlib import Path

# API credentials from n8n workflow
API_USERNAME = "03KnC9"
API_PASSWORD = "TthH29CLiQ7S8Jd22jMq4UWr16YgtuJBPgjMNX23faP"
BASE_URL = "https://api.mobilemessage.com.au"


def normalize_phone(phone: str) -> str:
    """Normalize Australian mobile to 61XXXXXXXXX format."""
    if not phone:
        return None

    phone = ''.join(c for c in str(phone) if c.isdigit() or c == '+')
    phone = phone.replace('+', '')

    if phone.startswith('0') and len(phone) == 10:
        phone = '61' + phone[1:]
    elif phone.startswith('4') and len(phone) == 9:
        phone = '61' + phone

    if phone.startswith('61') and len(phone) == 11:
        return phone

    return None


class MobileMessageClient:
    """Mobile Message SMS API client."""

    def __init__(self, username: str = None, password: str = None):
        self.username = username or API_USERNAME
        self.password = password or API_PASSWORD

    def send_sms(
        self,
        to: str,
        message: str,
        sender: str = "YesAI"
    ) -> dict:
        """
        Send an SMS message.

        Args:
            to: Phone number (any Australian format)
            message: SMS message content (max 918 chars)
            sender: Sender ID (e.g., "YesAI" or "61412111000")

        Returns:
            {"success": True/False, "response": {...}, "error": "..."}
        """
        # Normalize phone number
        phone = normalize_phone(to)
        if not phone:
            return {"success": False, "error": f"Invalid phone number: {to}"}

        # Validate message length
        if len(message) > 918:
            return {"success": False, "error": f"Message too long: {len(message)} chars (max 918)"}

        # Use simple API endpoint (GET with query params)
        url = f"{BASE_URL}/simple/send-sms"
        params = {
            "api_username": self.username,
            "api_password": self.password,
            "sender": sender,
            "to": phone,
            "message": message
        }

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return {
                    "success": True,
                    "to": phone,
                    "message_length": len(message),
                    "response": response.text
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "to": phone
                }

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def send_bulk_sms(
        self,
        recipients: list,
        message: str,
        sender: str = "YesAI"
    ) -> dict:
        """
        Send SMS to multiple recipients.

        Args:
            recipients: List of phone numbers
            message: SMS message (can include {FIRSTNAME} etc.)
            sender: Sender ID

        Returns:
            {"success": int, "failed": int, "results": [...]}
        """
        results = []
        success_count = 0
        failed_count = 0

        for recipient in recipients:
            # If recipient is dict, extract phone and personalize message
            if isinstance(recipient, dict):
                phone = recipient.get('phone') or recipient.get('mobile') or recipient.get('SMS')
                personalized = message
                for key, value in recipient.items():
                    personalized = personalized.replace(f"{{{key.upper()}}}", str(value or ''))
            else:
                phone = recipient
                personalized = message

            result = self.send_sms(phone, personalized, sender)
            results.append(result)

            if result.get('success'):
                success_count += 1
            else:
                failed_count += 1

        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(recipients),
            "results": results
        }

    def get_balance(self) -> dict:
        """Get account balance (if API supports it)."""
        # Mobile Message uses simple URL API, balance check may need different endpoint
        # For now, return info about API
        return {
            "success": True,
            "message": "Mobile Message uses pay-per-SMS model (2c/SMS). Check balance at mobilemessage.com.au"
        }


# ========== CLI TESTING ==========

if __name__ == "__main__":
    import sys

    print("Mobile Message SMS Client - Testing")
    print("-" * 50)

    client = MobileMessageClient()

    if len(sys.argv) > 2:
        # Send test SMS: python mobilemessage.py 0412345678 "Test message"
        phone = sys.argv[1]
        message = sys.argv[2]
        print(f"Sending to: {phone}")
        print(f"Message: {message}")
        print("-" * 50)
        result = client.send_sms(phone, message)
        print(f"Result: {result}")
    else:
        print("Usage: python mobilemessage.py <phone> <message>")
        print("\nExample:")
        print('  python mobilemessage.py 0412111000 "Test from Yes AI"')
        print("\nAPI configured:")
        print(f"  Username: {API_USERNAME}")
        print(f"  Endpoint: {BASE_URL}/simple/send-sms")
