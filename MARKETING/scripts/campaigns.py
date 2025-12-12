"""
Campaign Management for Yes AI Marketing
Create and manage email/SMS campaigns via Brevo.

Usage:
    python campaigns.py list                     # List all campaigns
    python campaigns.py stats 123                # Get campaign stats
    python campaigns.py create --template welcome # Create from template
    python campaigns.py send 123                 # Send campaign
    python campaigns.py sms "+61412345678" "Hi!" # Send single SMS
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))
from brevo_api import BrevoClient, normalize_australian_mobile

# Paths
MARKETING_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = MARKETING_ROOT / "templates"


# ========== EMAIL TEMPLATES ==========

EMAIL_TEMPLATES = {
    "yesai_intro": {
        "name": "Yes AI Introduction",
        "subject": "AI Solutions for Your Business - Yes AI",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 20px 0; }
        .logo { font-size: 28px; font-weight: bold; }
        .logo .yes { color: #e53935; }
        .logo .ai { color: #1565c0; }
        .content { padding: 20px 0; }
        .cta { background: #1565c0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }
        .footer { font-size: 12px; color: #666; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo"><span class="yes">Yes</span> <span class="ai">AI</span></div>
        </div>
        <div class="content">
            <p>Hi {{params.FIRSTNAME}},</p>

            <p>I wanted to reach out about how AI can transform your business operations.</p>

            <p>At Yes AI, we build custom AI solutions that actually work:</p>

            <ul>
                <li><strong>AI Phone Agents</strong> - Handle calls 24/7, book appointments, answer questions</li>
                <li><strong>Custom AI Assistants</strong> - Trained on your business data</li>
                <li><strong>Process Automation</strong> - Reduce manual work by 30%+</li>
            </ul>

            <p>We're offering a <strong>free 30-minute consultation</strong> to discuss how AI could help your specific situation.</p>

            <a href="https://yesai.au/contact" class="cta">Book Your Free Consultation</a>

            <p>Best regards,<br>
            Peter Ball<br>
            Yes AI</p>
        </div>
        <div class="footer">
            <p>Yes AI | Melbourne, Australia<br>
            Phone: (03) 9999 7398 | hello@yesai.au<br>
            <a href="{{unsubscribe}}">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>
"""
    },

    "healthcare_ai": {
        "name": "Healthcare AI Receptionist",
        "subject": "AI Receptionist for Healthcare Practices",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 20px 0; }
        .logo { font-size: 28px; font-weight: bold; }
        .logo .yes { color: #e53935; }
        .logo .ai { color: #1565c0; }
        .highlight { background: #f5f5f5; padding: 15px; border-left: 4px solid #1565c0; margin: 20px 0; }
        .cta { background: #1565c0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }
        .footer { font-size: 12px; color: #666; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo"><span class="yes">Yes</span> <span class="ai">AI</span></div>
        </div>
        <div class="content">
            <p>Hi {{params.FIRSTNAME}},</p>

            <p>Is your reception team overwhelmed with calls? Missing bookings after hours?</p>

            <p>Our <strong>AI Phone Receptionist</strong> is already helping healthcare practices across Australia:</p>

            <div class="highlight">
                <strong>What it does:</strong><br>
                - Answers every call, 24/7<br>
                - Books appointments directly into Cliniko/PracticeSuite<br>
                - Handles rescheduling and cancellations<br>
                - Answers FAQs about your services<br>
                - Transfers urgent calls to staff
            </div>

            <p><strong>Real results:</strong> One allied health practice reduced missed calls by 90% and freed up 20+ hours per week of admin time.</p>

            <p>Want to hear it in action? We'll set up a free demo call where you can experience the AI receptionist yourself.</p>

            <a href="https://yesai.au/healthcare" class="cta">Request a Demo</a>

            <p>Best regards,<br>
            Peter Ball<br>
            Yes AI</p>
        </div>
        <div class="footer">
            <p>Yes AI | Melbourne, Australia<br>
            Phone: (03) 9999 7398 | hello@yesai.au<br>
            <a href="{{unsubscribe}}">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>
"""
    },

    "followup": {
        "name": "Follow-up Email",
        "subject": "Following up - AI Solutions for {{params.COMPANY}}",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 20px 0; }
        .logo { font-size: 28px; font-weight: bold; }
        .logo .yes { color: #e53935; }
        .logo .ai { color: #1565c0; }
        .cta { background: #1565c0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }
        .footer { font-size: 12px; color: #666; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo"><span class="yes">Yes</span> <span class="ai">AI</span></div>
        </div>
        <div class="content">
            <p>Hi {{params.FIRSTNAME}},</p>

            <p>I wanted to follow up on my previous email about AI solutions.</p>

            <p>I know you're busy, so I'll keep this brief: if you're curious about how AI could help {{params.COMPANY}}, I'm happy to have a quick 15-minute chat - no pressure, just sharing ideas.</p>

            <p>If now's not the right time, no worries at all. Just reply "not now" and I won't follow up again.</p>

            <a href="https://yesai.au/contact" class="cta">Let's Chat</a>

            <p>Cheers,<br>
            Peter</p>
        </div>
        <div class="footer">
            <p>Yes AI | hello@yesai.au<br>
            <a href="{{unsubscribe}}">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>
"""
    }
}

# ========== SMS TEMPLATES ==========

SMS_TEMPLATES = {
    "intro": "Hi {FIRSTNAME}, this is Yes AI. We help businesses automate with AI. Interested in a free consultation? Reply YES or call (03) 9999 7398",
    "followup": "Hi {FIRSTNAME}, following up on AI solutions for your business. Have 15 mins for a quick chat? Reply YES or call (03) 9999 7398 - Peter from Yes AI",
    "demo_offer": "Hi {FIRSTNAME}, Yes AI here. We're offering free AI demos this week - see an AI phone agent in action. Reply DEMO to book. yesai.au"
}


def list_campaigns(client: BrevoClient, status: str = None):
    """List all campaigns."""
    result = client.get_campaigns(status=status, limit=50)

    if not result["success"]:
        print(f"Error: {result.get('error')}")
        return

    campaigns = result["data"].get("campaigns", [])

    if not campaigns:
        print("No campaigns found")
        return

    print(f"\n{'ID':<10} {'Status':<12} {'Name':<40} {'Sent':<10}")
    print("-" * 80)

    for c in campaigns:
        print(f"{c['id']:<10} {c['status']:<12} {c['name'][:40]:<40} {c.get('statistics', {}).get('sent', 0):<10}")


def get_campaign_stats(client: BrevoClient, campaign_id: int):
    """Get detailed campaign statistics."""
    result = client.get_campaign_stats(campaign_id)

    if not result["success"]:
        print(f"Error: {result.get('error')}")
        return

    c = result["data"]
    stats = c.get("statistics", {}).get("globalStats", {})

    print(f"\nCampaign: {c['name']}")
    print(f"Status: {c['status']}")
    print(f"Subject: {c['subject']}")
    print("-" * 50)
    print(f"Sent: {stats.get('sent', 0)}")
    print(f"Delivered: {stats.get('delivered', 0)}")
    print(f"Opens: {stats.get('uniqueOpens', 0)} ({stats.get('uniqueOpens', 0) / max(stats.get('delivered', 1), 1) * 100:.1f}%)")
    print(f"Clicks: {stats.get('uniqueClicks', 0)} ({stats.get('uniqueClicks', 0) / max(stats.get('delivered', 1), 1) * 100:.1f}%)")
    print(f"Bounces: {stats.get('hardBounces', 0) + stats.get('softBounces', 0)}")
    print(f"Unsubscribes: {stats.get('unsubscriptions', 0)}")


def create_campaign(
    client: BrevoClient,
    template: str = None,
    name: str = None,
    subject: str = None,
    list_ids: list = None
):
    """Create a new email campaign."""

    if template and template in EMAIL_TEMPLATES:
        tpl = EMAIL_TEMPLATES[template]
        name = name or f"{tpl['name']} - {datetime.now().strftime('%Y-%m-%d')}"
        subject = subject or tpl["subject"]
        html = tpl["html"]
    else:
        print(f"Available templates: {', '.join(EMAIL_TEMPLATES.keys())}")
        return

    if not list_ids:
        # Get available lists
        result = client.get_lists()
        if result["success"]:
            lists = result["data"].get("lists", [])
            print("\nAvailable lists:")
            for l in lists:
                print(f"  {l['id']}: {l['name']} ({l.get('totalSubscribers', 0)} contacts)")
            list_ids = [int(input("\nEnter list ID to send to: "))]
        else:
            print("Error getting lists")
            return

    # Create campaign
    result = client.create_email_campaign(
        name=name,
        subject=subject,
        sender_name="Yes AI",
        sender_email="hello@yesai.au",
        html_content=html,
        list_ids=list_ids,
        reply_to="hello@yesai.au"
    )

    if result["success"]:
        campaign_id = result["data"]["id"]
        print(f"\nCampaign created! ID: {campaign_id}")
        print(f"Name: {name}")
        print(f"Subject: {subject}")
        print(f"\nTo send: python campaigns.py send {campaign_id}")
    else:
        print(f"Error: {result.get('error')}")


def send_campaign(client: BrevoClient, campaign_id: int):
    """Send a campaign immediately."""
    # Confirm
    confirm = input(f"Send campaign {campaign_id} now? (yes/no): ")
    if confirm.lower() != "yes":
        print("Cancelled")
        return

    result = client.send_campaign(campaign_id)

    if result["success"]:
        print(f"Campaign {campaign_id} sent!")
    else:
        print(f"Error: {result.get('error')}")


def send_sms(client: BrevoClient, recipient: str, message: str, template: str = None):
    """Send a single SMS."""

    # Normalize phone
    recipient = normalize_australian_mobile(recipient)
    if not recipient or not recipient.startswith("+61"):
        print(f"Invalid phone number: {recipient}")
        return

    # Use template if specified
    if template and template in SMS_TEMPLATES:
        message = SMS_TEMPLATES[template]
        print(f"Using template: {template}")

    print(f"To: {recipient}")
    print(f"Message: {message}")
    print(f"Length: {len(message)} chars")

    # Confirm
    confirm = input("\nSend? (yes/no): ")
    if confirm.lower() != "yes":
        print("Cancelled")
        return

    result = client.send_sms(recipient, message)

    if result["success"]:
        print("SMS sent!")
    else:
        print(f"Error: {result.get('error')}")


def show_templates():
    """Show available templates."""
    print("\n=== EMAIL TEMPLATES ===")
    for key, tpl in EMAIL_TEMPLATES.items():
        print(f"\n{key}:")
        print(f"  Name: {tpl['name']}")
        print(f"  Subject: {tpl['subject']}")

    print("\n=== SMS TEMPLATES ===")
    for key, msg in SMS_TEMPLATES.items():
        print(f"\n{key}:")
        print(f"  {msg}")


def show_account(client: BrevoClient):
    """Show account info and limits."""
    result = client.get_account()

    if not result["success"]:
        print(f"Error: {result.get('error')}")
        return

    account = result["data"]
    print(f"\nAccount: {account.get('companyName', 'N/A')}")
    print(f"Email: {account.get('email', 'N/A')}")

    for plan in account.get("plan", []):
        print(f"\nPlan: {plan.get('type', 'N/A')}")
        print(f"Email credits: {plan.get('credits', 0)}")
        print(f"Credits type: {plan.get('creditsType', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="Brevo Campaign Management")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # list command
    list_parser = subparsers.add_parser("list", help="List campaigns")
    list_parser.add_argument("--status", help="Filter by status")

    # stats command
    stats_parser = subparsers.add_parser("stats", help="Get campaign stats")
    stats_parser.add_argument("campaign_id", type=int, help="Campaign ID")

    # create command
    create_parser = subparsers.add_parser("create", help="Create campaign")
    create_parser.add_argument("--template", "-t", help="Template name")
    create_parser.add_argument("--name", "-n", help="Campaign name")
    create_parser.add_argument("--subject", "-s", help="Email subject")
    create_parser.add_argument("--list", "-l", type=int, action="append", help="List ID")

    # send command
    send_parser = subparsers.add_parser("send", help="Send campaign")
    send_parser.add_argument("campaign_id", type=int, help="Campaign ID")

    # sms command
    sms_parser = subparsers.add_parser("sms", help="Send SMS")
    sms_parser.add_argument("recipient", help="Phone number")
    sms_parser.add_argument("message", nargs="?", help="Message text")
    sms_parser.add_argument("--template", "-t", help="SMS template name")

    # templates command
    subparsers.add_parser("templates", help="Show available templates")

    # account command
    subparsers.add_parser("account", help="Show account info")

    # lists command
    subparsers.add_parser("lists", help="Show contact lists")

    args = parser.parse_args()

    # Initialize client
    try:
        client = BrevoClient()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Execute command
    if args.command == "list":
        list_campaigns(client, args.status)
    elif args.command == "stats":
        get_campaign_stats(client, args.campaign_id)
    elif args.command == "create":
        create_campaign(client, args.template, args.name, args.subject, args.list)
    elif args.command == "send":
        send_campaign(client, args.campaign_id)
    elif args.command == "sms":
        send_sms(client, args.recipient, args.message, args.template)
    elif args.command == "templates":
        show_templates()
    elif args.command == "account":
        show_account(client)
    elif args.command == "lists":
        result = client.get_lists()
        if result["success"]:
            for l in result["data"].get("lists", []):
                print(f"{l['id']}: {l['name']} ({l.get('totalSubscribers', 0)} contacts)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
