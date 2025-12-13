"""
Brevo API Wrapper for Yes AI Marketing Automation
Uses REST API directly (not SDK) for better reliability.

Usage:
    from brevo_api import BrevoClient
    client = BrevoClient()
    client.add_contact("test@example.com", {"FIRSTNAME": "John", "SMS": "+61412345678"})
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Load API key from file (CC/Brevo_API_Key.txt - 4 levels up from scripts/)
API_KEY_PATH = Path(__file__).parent.parent.parent.parent / "Brevo_API_Key.txt"

def get_api_key():
    """Load Brevo API key from file."""
    if API_KEY_PATH.exists():
        return API_KEY_PATH.read_text().strip()

    # Try environment variable as fallback
    key = os.environ.get("BREVO_API_KEY")
    if key:
        return key

    raise ValueError(
        f"Brevo API key not found!\n"
        f"Please create: {API_KEY_PATH}\n"
        f"Or set BREVO_API_KEY environment variable"
    )


class BrevoClient:
    """Simple Brevo REST API client."""

    BASE_URL = "https://api.brevo.com/v3"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or get_api_key()
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None):
        """Make API request with error handling."""
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )

            # Handle response
            if response.status_code in [200, 201, 202, 204]:
                if response.content:
                    return {"success": True, "data": response.json()}
                return {"success": True, "data": None}
            else:
                error_msg = response.text
                try:
                    error_msg = response.json().get("message", response.text)
                except:
                    pass
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    # ========== CONTACTS ==========

    def add_contact(self, email: str, attributes: dict = None, list_ids: list = None):
        """
        Add or update a contact.

        Args:
            email: Contact email address
            attributes: Dict of attributes (FIRSTNAME, LASTNAME, SMS, etc.)
            list_ids: List of list IDs to add contact to

        Returns:
            {"success": True/False, "data": {...}, "error": "..."}
        """
        data = {
            "email": email,
            "updateEnabled": True  # Update if exists
        }

        if attributes:
            data["attributes"] = attributes

        if list_ids:
            data["listIds"] = list_ids

        return self._request("POST", "contacts", data)

    def get_contact(self, email: str):
        """Get contact details by email."""
        return self._request("GET", f"contacts/{email}")

    def delete_contact(self, email: str):
        """Delete a contact."""
        return self._request("DELETE", f"contacts/{email}")

    def update_contact(self, email: str, attributes: dict):
        """Update contact attributes."""
        return self._request("PUT", f"contacts/{email}", {"attributes": attributes})

    def get_contacts(self, limit: int = 50, offset: int = 0, list_id: int = None):
        """Get list of contacts."""
        params = {"limit": limit, "offset": offset}
        if list_id:
            params["listIds"] = str(list_id)
        return self._request("GET", "contacts", params=params)

    # ========== LISTS ==========

    def create_list(self, name: str, folder_id: int = 1):
        """Create a new contact list."""
        return self._request("POST", "contacts/lists", {
            "name": name,
            "folderId": folder_id
        })

    def get_lists(self, limit: int = 50, offset: int = 0):
        """Get all contact lists."""
        return self._request("GET", "contacts/lists", params={"limit": limit, "offset": offset})

    def get_list(self, list_id: int):
        """Get specific list details."""
        return self._request("GET", f"contacts/lists/{list_id}")

    def add_contacts_to_list(self, list_id: int, emails: list):
        """Add multiple contacts to a list."""
        return self._request("POST", f"contacts/lists/{list_id}/contacts/add", {
            "emails": emails
        })

    # ========== EMAIL CAMPAIGNS ==========

    def create_email_campaign(
        self,
        name: str,
        subject: str,
        sender_name: str,
        sender_email: str,
        html_content: str,
        list_ids: list,
        reply_to: str = None,
        schedule_at: str = None
    ):
        """
        Create an email campaign.

        Args:
            name: Campaign name
            subject: Email subject line
            sender_name: From name
            sender_email: From email
            html_content: HTML email body
            list_ids: List IDs to send to
            reply_to: Reply-to email (optional)
            schedule_at: ISO datetime to schedule (optional)
        """
        data = {
            "name": name,
            "subject": subject,
            "sender": {"name": sender_name, "email": sender_email},
            "type": "classic",
            "htmlContent": html_content,
            "recipients": {"listIds": list_ids}
        }

        if reply_to:
            data["replyTo"] = reply_to
        if schedule_at:
            data["scheduledAt"] = schedule_at

        return self._request("POST", "emailCampaigns", data)

    def send_campaign(self, campaign_id: int):
        """Send a campaign immediately."""
        return self._request("POST", f"emailCampaigns/{campaign_id}/sendNow")

    def get_campaign_stats(self, campaign_id: int):
        """Get campaign statistics."""
        return self._request("GET", f"emailCampaigns/{campaign_id}")

    def get_campaigns(self, status: str = None, limit: int = 50, offset: int = 0):
        """
        Get list of campaigns.

        Args:
            status: Filter by status (draft, sent, queued, etc.)
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        return self._request("GET", "emailCampaigns", params=params)

    # ========== TRANSACTIONAL EMAIL ==========

    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        sender_name: str = "Yes AI",
        sender_email: str = "hello@yesai.au"
    ):
        """Send a single transactional email."""
        return self._request("POST", "smtp/email", {
            "sender": {"name": sender_name, "email": sender_email},
            "to": [{"email": to_email, "name": to_name}],
            "subject": subject,
            "htmlContent": html_content
        })

    # ========== SMS ==========

    def send_sms(self, recipient: str, content: str, sender: str = "YesAI"):
        """
        Send an SMS message.

        Args:
            recipient: Phone number in international format (+61...)
            content: SMS message content
            sender: Sender ID (max 11 chars for alphanumeric)
        """
        return self._request("POST", "transactionalSMS/sms", {
            "sender": sender,
            "recipient": recipient,
            "content": content
        })

    def get_sms_stats(self, start_date: str = None, end_date: str = None):
        """Get SMS campaign statistics."""
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self._request("GET", "transactionalSMS/statistics/reports", params=params)

    # ========== ACCOUNT ==========

    def get_account(self):
        """Get account details and limits."""
        return self._request("GET", "account")

    def get_senders(self):
        """Get list of validated sender emails."""
        return self._request("GET", "senders")

    # ========== BLOCKLIST / SUPPRESSION ==========

    def blocklist_contact(self, email: str = None, phone: str = None):
        """
        Add a contact to the blocklist (suppression list).

        Args:
            email: Email to blocklist
            phone: Phone to blocklist (for SMS)
        """
        if email:
            # For email blocklist, update contact with emailBlacklisted: true
            return self._request("PUT", f"contacts/{email}", {
                "emailBlacklisted": True
            })
        return {"success": False, "error": "Email required for blocklist"}

    def blocklist_contacts_bulk(self, emails: list):
        """
        Blocklist multiple contacts.

        Args:
            emails: List of email addresses to blocklist
        """
        results = {"success": 0, "failed": 0, "errors": []}

        for email in emails:
            result = self.blocklist_contact(email=email)
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"email": email, "error": result.get("error")})

        return results

    def import_blocklist_from_csv(self, csv_path: str, email_column: str = "email"):
        """
        Import blocklist from CSV file.

        Args:
            csv_path: Path to CSV file
            email_column: Name of column containing emails
        """
        import csv

        emails = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get(email_column, '').strip().lower()
                if email and '@' in email:
                    emails.append(email)

        print(f"Found {len(emails)} emails to blocklist")
        return self.blocklist_contacts_bulk(emails)

    # ========== DEALS (CRM) ==========

    def create_deal(
        self,
        name: str,
        attributes: dict = None
    ):
        """
        Create a CRM deal.

        Args:
            name: Deal name
            attributes: Deal attributes (deal_stage, deal_owner, amount, etc.)
        """
        data = {"name": name}
        if attributes:
            data["attributes"] = attributes
        return self._request("POST", "crm/deals", data)

    def get_deals(self, limit: int = 50, offset: int = 0):
        """Get list of deals."""
        return self._request("GET", "crm/deals", params={"limit": limit, "offset": offset})

    def update_deal(self, deal_id: str, attributes: dict):
        """Update a deal."""
        return self._request("PATCH", f"crm/deals/{deal_id}", {"attributes": attributes})


# ========== UTILITY FUNCTIONS ==========

def normalize_australian_mobile(phone: str) -> str:
    """
    Normalize Australian mobile number to +61 format.

    Examples:
        0412345678 -> +61412345678
        61412345678 -> +61412345678
        +61412345678 -> +61412345678
        04 1234 5678 -> +61412345678
    """
    if not phone:
        return None

    # Remove spaces, dashes, parentheses
    phone = ''.join(c for c in phone if c.isdigit() or c == '+')

    # Handle different formats
    if phone.startswith('+61'):
        return phone
    elif phone.startswith('61') and len(phone) == 11:
        return '+' + phone
    elif phone.startswith('0') and len(phone) == 10:
        return '+61' + phone[1:]
    elif len(phone) == 9 and phone.startswith('4'):
        return '+61' + phone

    return phone  # Return as-is if can't normalize


def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email or ''))


# ========== CLI TESTING ==========

if __name__ == "__main__":
    import sys

    print("Brevo API Client - Testing Connection...")
    print("-" * 50)

    try:
        client = BrevoClient()

        # Test account info
        result = client.get_account()
        if result["success"]:
            account = result["data"]
            print(f"Account: {account.get('companyName', 'N/A')}")
            print(f"Email: {account.get('email', 'N/A')}")

            # Show plan info
            plan = account.get("plan", [{}])
            if plan:
                print(f"Plan: {plan[0].get('type', 'N/A')}")
                credits = plan[0].get('credits', 0)
                print(f"Email credits: {credits}")

            print("-" * 50)
            print("Connection successful!")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except ValueError as e:
        print(f"Setup required: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
