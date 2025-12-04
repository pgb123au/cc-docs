#!/usr/bin/env python3
"""
Monthly Phone Number Report
Sends email on 1st of each month with all phone numbers from Telnyx, Zadarma, and Retell.

Usage:
    python monthly_phone_report.py           # Send report email
    python monthly_phone_report.py --test    # Print report to console (no email)
    python monthly_phone_report.py --html    # Output HTML to file for testing
"""

import os
import sys
import json
import hmac
import hashlib
import base64
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

# Configuration
CONFIG = {
    "email_to": "peter@yesai.au",
    "email_from": "reports@yr.com.au",
    "email_subject": "Monthly Phone Numbers Report - {month}",
    "smtp_host": "localhost",
    "smtp_port": 25,
    # n8n webhook for sending emails (uses Gmail OAuth)
    "n8n_email_webhook": "https://auto.yr.com.au/webhook/send-system-email",
}

# API Credentials (loaded from environment or .credentials file)
CREDENTIALS = {}


def load_credentials():
    """Load API credentials from environment or file"""
    global CREDENTIALS

    # Try environment variables first
    CREDENTIALS = {
        "TELNYX_API_KEY": os.environ.get("TELNYX_API_KEY", ""),
        "ZADARMA_API_KEY": os.environ.get("ZADARMA_API_KEY", ""),
        "ZADARMA_API_SECRET": os.environ.get("ZADARMA_API_SECRET", ""),
        "RETELL_API_KEY": os.environ.get("RETELL_API_KEY", ""),
    }

    # Try .credentials file if env vars not set (check multiple locations)
    cred_locations = [
        os.path.join(os.path.dirname(__file__), ".credentials"),  # Same directory
        os.path.join(os.path.dirname(__file__), "..", ".credentials"),  # Parent directory
        os.path.expanduser("~/telco_reports/.credentials"),  # Home directory
    ]
    cred_file = None
    for loc in cred_locations:
        if os.path.exists(loc):
            cred_file = loc
            break
    if cred_file and os.path.exists(cred_file):
        with open(cred_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if not CREDENTIALS.get(key):
                        CREDENTIALS[key] = value


def format_phone(number: str) -> str:
    """Format phone number for display"""
    if not number:
        return ""
    n = number.lstrip('+')
    if n.startswith('61') and len(n) == 11:
        # Australian format: +61 X XXXX XXXX
        return f"+61 {n[2]} {n[3:7]} {n[7:]}"
    return number


def format_currency(amount, currency="USD") -> str:
    """Format currency amount"""
    if amount is None:
        return "-"
    try:
        return f"${float(amount):.2f} {currency}"
    except:
        return str(amount)


def days_until(date_str: str) -> Optional[int]:
    """Calculate days until a date"""
    if not date_str:
        return None
    try:
        # Handle various date formats
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]:
            try:
                dt = datetime.strptime(date_str[:19], fmt[:len(date_str[:19])+2])
                return (dt - datetime.now()).days
            except:
                continue
        return None
    except:
        return None


def get_expiry_badge(days: Optional[int]) -> str:
    """Get HTML badge for expiry status"""
    if days is None:
        return ""
    if days < 0:
        return '<span style="background:#dc3545;color:white;padding:2px 6px;border-radius:3px;font-size:11px;">EXPIRED</span>'
    elif days <= 30:
        return f'<span style="background:#ffc107;color:black;padding:2px 6px;border-radius:3px;font-size:11px;">{days}d</span>'
    elif days <= 90:
        return f'<span style="background:#17a2b8;color:white;padding:2px 6px;border-radius:3px;font-size:11px;">{days}d</span>'
    return f'<span style="color:#6c757d;font-size:11px;">{days}d</span>'


# =============================================================================
# TELNYX API
# =============================================================================

def fetch_telnyx_numbers() -> List[Dict]:
    """Fetch phone numbers from Telnyx"""
    api_key = CREDENTIALS.get("TELNYX_API_KEY")
    if not api_key:
        return []

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Get phone numbers
        resp = requests.get("https://api.telnyx.com/v2/phone_numbers", headers=headers, timeout=30)
        numbers_data = resp.json().get("data", [])

        # Get FQDN connections for SIP info
        resp = requests.get("https://api.telnyx.com/v2/fqdn_connections", headers=headers, timeout=30)
        connections = {c["id"]: c for c in resp.json().get("data", [])}

        results = []
        for n in numbers_data:
            conn_id = n.get("connection_id")
            conn = connections.get(conn_id, {})

            results.append({
                "number": n.get("phone_number", ""),
                "status": n.get("status", ""),
                "type": n.get("phone_number_type", ""),
                "connection": n.get("connection_name", ""),
                "sip_region": conn.get("inbound", {}).get("sip_region", ""),
                "codecs": ", ".join(conn.get("inbound", {}).get("codecs", [])),
                "purchased": n.get("purchased_at", "")[:10] if n.get("purchased_at") else "",
                "monthly_cost": 2.00,  # Telnyx AU local numbers
                "currency": "USD",
                "expiry": None,  # Telnyx doesn't expire
                "features": [f["name"] for f in n.get("features", []) if isinstance(f, dict)],
            })

        return results
    except Exception as e:
        print(f"Error fetching Telnyx: {e}")
        return []


# =============================================================================
# ZADARMA API
# =============================================================================

def zadarma_signature(method: str, params: str = "") -> str:
    """Generate Zadarma API signature"""
    api_key = CREDENTIALS.get("ZADARMA_API_KEY", "")
    api_secret = CREDENTIALS.get("ZADARMA_API_SECRET", "")

    md5_hash = hashlib.md5(params.encode()).hexdigest()
    sign_string = f"{method}{params}{md5_hash}"
    hex_sig = hmac.new(api_secret.encode(), sign_string.encode(), hashlib.sha1).hexdigest()
    return f"{api_key}:{base64.b64encode(hex_sig.encode()).decode()}"


def fetch_zadarma_numbers() -> List[Dict]:
    """Fetch phone numbers from Zadarma"""
    api_key = CREDENTIALS.get("ZADARMA_API_KEY")
    api_secret = CREDENTIALS.get("ZADARMA_API_SECRET")
    if not api_key or not api_secret:
        return []

    try:
        method = "/v1/direct_numbers/"
        headers = {"Authorization": zadarma_signature(method)}

        resp = requests.get(f"https://api.zadarma.com{method}", headers=headers, timeout=30)
        data = resp.json()

        if data.get("status") != "success":
            return []

        results = []
        for n in data.get("info", []):
            sip_dest = n.get("sip", "")
            if "livekit.cloud" in sip_dest:
                sip_display = "RetellAI (LiveKit)"
            elif sip_dest.isdigit() or (len(sip_dest) < 10 and not "@" in sip_dest):
                sip_display = f"Zadarma SIP ({sip_dest})"
            else:
                sip_display = sip_dest

            results.append({
                "number": f"+{n.get('number', '')}",
                "status": "active" if n.get("status") == "on" else n.get("status", ""),
                "city": n.get("description", ""),
                "sip_destination": sip_display,
                "channels": n.get("channels", 3),
                "monthly_cost": n.get("monthly_fee", 3),
                "currency": n.get("currency", "USD"),
                "expiry": n.get("stop_date", ""),
                "auto_renew": n.get("autorenew_period", ""),
                "start_date": n.get("start_date", "")[:10] if n.get("start_date") else "",
            })

        return results
    except Exception as e:
        print(f"Error fetching Zadarma: {e}")
        return []


def fetch_zadarma_balance() -> Dict:
    """Fetch Zadarma account balance"""
    api_key = CREDENTIALS.get("ZADARMA_API_KEY")
    api_secret = CREDENTIALS.get("ZADARMA_API_SECRET")
    if not api_key or not api_secret:
        return {}

    try:
        method = "/v1/info/balance/"
        headers = {"Authorization": zadarma_signature(method)}
        resp = requests.get(f"https://api.zadarma.com{method}", headers=headers, timeout=30)
        data = resp.json()
        if data.get("status") == "success":
            return {"balance": data.get("balance"), "currency": data.get("currency", "USD")}
    except:
        pass
    return {}


# =============================================================================
# RETELL API
# =============================================================================

def fetch_retell_numbers() -> List[Dict]:
    """Fetch phone numbers from Retell"""
    api_key = CREDENTIALS.get("RETELL_API_KEY")
    if not api_key:
        return []

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Get phone numbers
        resp = requests.get("https://api.retellai.com/list-phone-numbers", headers=headers, timeout=30)
        numbers = resp.json() if resp.status_code == 200 else []

        # Get agents for mapping
        resp = requests.get("https://api.retellai.com/list-agents", headers=headers, timeout=30)
        agents = resp.json() if resp.status_code == 200 else []
        agent_map = {a.get("agent_id"): a.get("agent_name", "") for a in agents}

        results = []
        for n in numbers:
            inbound_agent = n.get("inbound_agent_id")
            outbound_agent = n.get("outbound_agent_id")

            results.append({
                "number": n.get("phone_number", ""),
                "type": n.get("phone_number_type", ""),
                "nickname": n.get("nickname", ""),
                "inbound_agent": agent_map.get(inbound_agent, inbound_agent or "None"),
                "outbound_agent": agent_map.get(outbound_agent, outbound_agent or "None"),
                "area_code": n.get("area_code", ""),
            })

        return results
    except Exception as e:
        print(f"Error fetching Retell: {e}")
        return []


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_html_report() -> str:
    """Generate HTML email report"""

    now = datetime.now()
    month_name = now.strftime("%B %Y")

    # Fetch all data
    telnyx_numbers = fetch_telnyx_numbers()
    zadarma_numbers = fetch_zadarma_numbers()
    zadarma_balance = fetch_zadarma_balance()
    retell_numbers = fetch_retell_numbers()

    # Calculate totals
    telnyx_monthly = sum(n.get("monthly_cost", 0) for n in telnyx_numbers)
    zadarma_monthly = sum(n.get("monthly_cost", 0) for n in zadarma_numbers)

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 10px 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #eee; }}
        .section-title {{ font-size: 18px; font-weight: 600; color: #333; margin: 0; }}
        .section-badge {{ background: #667eea; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{ background: #f8f9fa; padding: 12px 8px; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #dee2e6; }}
        td {{ padding: 10px 8px; border-bottom: 1px solid #eee; color: #333; }}
        tr:hover td {{ background: #f8f9fa; }}
        .status-active {{ color: #28a745; font-weight: 500; }}
        .status-inactive {{ color: #dc3545; }}
        .number {{ font-family: monospace; font-weight: 500; }}
        .summary-box {{ background: #f8f9fa; border-radius: 6px; padding: 15px; margin-top: 20px; }}
        .summary-row {{ display: flex; justify-content: space-between; padding: 5px 0; }}
        .summary-label {{ color: #666; }}
        .summary-value {{ font-weight: 600; color: #333; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; border-top: 1px solid #eee; }}
        .alert {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px; margin-bottom: 20px; }}
        .alert-danger {{ background: #f8d7da; border-color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Monthly Phone Numbers Report</h1>
            <p>Generated on {now.strftime("%A, %d %B %Y at %H:%M")}</p>
        </div>
        <div class="content">
"""

    # Check for expiring numbers
    expiring_soon = []
    for n in zadarma_numbers:
        days = days_until(n.get("expiry", ""))
        if days is not None and days <= 30:
            expiring_soon.append((n["number"], n.get("city", ""), days))

    if expiring_soon:
        html += '<div class="alert alert-danger"><strong>Numbers Expiring Soon:</strong><br>'
        for num, city, days in expiring_soon:
            html += f'{format_phone(num)} ({city}) - <strong>{days} days</strong><br>'
        html += '</div>'

    # TELNYX Section
    html += f"""
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">Telnyx</h2>
                    <span class="section-badge">{len(telnyx_numbers)} numbers</span>
                </div>
                <table>
                    <tr>
                        <th>Number</th>
                        <th>Status</th>
                        <th>Type</th>
                        <th>Connection</th>
                        <th>Region</th>
                        <th>Codecs</th>
                        <th>Cost/mo</th>
                    </tr>
"""
    for n in telnyx_numbers:
        status_class = "status-active" if n["status"] == "active" else "status-inactive"
        html += f"""
                    <tr>
                        <td class="number">{format_phone(n['number'])}</td>
                        <td class="{status_class}">{n['status']}</td>
                        <td>{n['type']}</td>
                        <td>{n['connection']}</td>
                        <td>{n['sip_region']}</td>
                        <td>{n['codecs']}</td>
                        <td>{format_currency(n['monthly_cost'])}</td>
                    </tr>
"""
    html += f"""
                </table>
                <div class="summary-box">
                    <div class="summary-row">
                        <span class="summary-label">Total Monthly Cost:</span>
                        <span class="summary-value">{format_currency(telnyx_monthly)}</span>
                    </div>
                </div>
            </div>
"""

    # ZADARMA Section
    balance_str = format_currency(zadarma_balance.get("balance"), zadarma_balance.get("currency", "USD")) if zadarma_balance else "N/A"
    html += f"""
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">Zadarma</h2>
                    <span class="section-badge">{len(zadarma_numbers)} numbers</span>
                </div>
                <table>
                    <tr>
                        <th>Number</th>
                        <th>City</th>
                        <th>Status</th>
                        <th>SIP Destination</th>
                        <th>Channels</th>
                        <th>Cost/mo</th>
                        <th>Expiry</th>
                        <th>Renew</th>
                    </tr>
"""
    for n in zadarma_numbers:
        status_class = "status-active" if n["status"] == "active" else "status-inactive"
        days = days_until(n.get("expiry", ""))
        expiry_display = n.get("expiry", "")[:10] if n.get("expiry") else "-"
        expiry_badge = get_expiry_badge(days)

        html += f"""
                    <tr>
                        <td class="number">{format_phone(n['number'])}</td>
                        <td>{n['city']}</td>
                        <td class="{status_class}">{n['status']}</td>
                        <td>{n['sip_destination']}</td>
                        <td>{n['channels']}</td>
                        <td>{format_currency(n['monthly_cost'], n['currency'])}</td>
                        <td>{expiry_display} {expiry_badge}</td>
                        <td>{n['auto_renew']}</td>
                    </tr>
"""
    html += f"""
                </table>
                <div class="summary-box">
                    <div class="summary-row">
                        <span class="summary-label">Account Balance:</span>
                        <span class="summary-value">{balance_str}</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Total Monthly Cost:</span>
                        <span class="summary-value">{format_currency(zadarma_monthly)}</span>
                    </div>
                </div>
            </div>
"""

    # RETELL Section
    html += f"""
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">Retell AI (Agent Assignments)</h2>
                    <span class="section-badge">{len(retell_numbers)} numbers</span>
                </div>
                <table>
                    <tr>
                        <th>Number</th>
                        <th>Type</th>
                        <th>Nickname</th>
                        <th>Inbound Agent</th>
                        <th>Outbound Agent</th>
                    </tr>
"""
    for n in retell_numbers:
        html += f"""
                    <tr>
                        <td class="number">{format_phone(n['number'])}</td>
                        <td>{n['type']}</td>
                        <td>{n['nickname']}</td>
                        <td>{n['inbound_agent'][:40]}{'...' if len(n['inbound_agent']) > 40 else ''}</td>
                        <td>{n['outbound_agent'][:40]}{'...' if len(n['outbound_agent']) > 40 else ''}</td>
                    </tr>
"""
    html += """
                </table>
            </div>
"""

    # Grand Total
    total_monthly = telnyx_monthly + zadarma_monthly
    html += f"""
            <div class="summary-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <div class="summary-row">
                    <span style="font-size: 16px;">Total Monthly Phone Costs:</span>
                    <span style="font-size: 20px; font-weight: 700;">{format_currency(total_monthly)}</span>
                </div>
                <div class="summary-row" style="opacity: 0.8; font-size: 12px;">
                    <span>Telnyx: {format_currency(telnyx_monthly)} | Zadarma: {format_currency(zadarma_monthly)}</span>
                    <span>Total Numbers: {len(telnyx_numbers) + len(zadarma_numbers)}</span>
                </div>
            </div>
        </div>
        <div class="footer">
            This report was automatically generated by the Telco Manager system.<br>
            View full details at: Telcos/SIP_OPTIMIZATION_GUIDE.md
        </div>
    </div>
</body>
</html>
"""

    return html


def send_email(html_content: str) -> bool:
    """Send the report via n8n webhook (uses Gmail OAuth)"""
    try:
        subject = CONFIG["email_subject"].format(month=datetime.now().strftime("%B %Y"))

        # Try n8n webhook first (more reliable, uses Gmail OAuth)
        webhook_url = CONFIG.get("n8n_email_webhook")
        if webhook_url:
            try:
                payload = {
                    "to": CONFIG["email_to"],
                    "subject": subject,
                    "html": html_content,
                    "report_type": "monthly_phone_numbers"
                }
                resp = requests.post(webhook_url, json=payload, timeout=30)
                if resp.status_code == 200:
                    return True
                print(f"n8n webhook returned {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                print(f"n8n webhook failed: {e}, falling back to SMTP...")

        # Fallback to direct SMTP
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = CONFIG["email_from"]
        msg["To"] = CONFIG["email_to"]

        # Plain text fallback
        text = "Please view this email in HTML format to see the phone numbers report."

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html_content, "html")

        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(CONFIG["smtp_host"], CONFIG["smtp_port"]) as server:
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Monthly Phone Numbers Report")
    parser.add_argument("--test", action="store_true", help="Print report info without sending email")
    parser.add_argument("--html", action="store_true", help="Save HTML to file for testing")
    args = parser.parse_args()

    load_credentials()

    print(f"Generating phone numbers report...")
    print(f"  Telnyx API Key: {'Set' if CREDENTIALS.get('TELNYX_API_KEY') else 'Missing'}")
    print(f"  Zadarma API Key: {'Set' if CREDENTIALS.get('ZADARMA_API_KEY') else 'Missing'}")
    print(f"  Retell API Key: {'Set' if CREDENTIALS.get('RETELL_API_KEY') else 'Missing'}")

    html = generate_html_report()

    if args.html:
        output_file = os.path.join(os.path.dirname(__file__), "report_preview.html")
        with open(output_file, "w") as f:
            f.write(html)
        print(f"\nHTML saved to: {output_file}")
        return

    if args.test:
        print("\n--- TEST MODE - Email would be sent to:", CONFIG["email_to"])
        print(f"Report generated successfully ({len(html)} bytes)")
        return

    # Send email
    print(f"\nSending email to {CONFIG['email_to']}...")
    if send_email(html):
        print("Email sent successfully!")
    else:
        print("Failed to send email!")
        sys.exit(1)


if __name__ == "__main__":
    main()
