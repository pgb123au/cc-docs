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

# ========== ALLIED HEALTH EMAIL TEMPLATES ==========

ALLIED_HEALTH_EMAILS = {
    "ah_problem_solution": {
        "name": "Allied Health - Problem/Solution",
        "subject": "Your receptionist called in sick - now what?",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .logo { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
        .logo .yes { color: #e53935; }
        .logo .ai { color: #1565c0; }
        ul { margin: 15px 0; }
        li { margin: 8px 0; }
        .cta { background: #1565c0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 15px 0; }
        .footer { font-size: 12px; color: #666; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        a { color: #1565c0; }
    </style>
</head>
<body>
    <div class="logo"><span class="yes">Yes</span> <span class="ai">AI</span></div>

    <p>Hi {{params.FIRSTNAME}},</p>

    <p>Quick question: what happens to the calls that come in when your team is busy with patients, at lunch, or after 5pm?</p>

    <p>For most allied health practices, the honest answer is... they go to voicemail. And voicemails often mean lost bookings.</p>

    <p>We've just helped Reignite Health (allied health provider across 10 aged care villages) solve this with an AI receptionist that:</p>

    <ul>
        <li>Answers every call 24/7 in a natural voice</li>
        <li>Books directly into Cliniko in real-time</li>
        <li>Handles DVA, HCP, Medicare & NDIS funding queries</li>
        <li>Speaks 30+ languages for diverse patient bases</li>
    </ul>

    <p>The result? No more missed calls. No more voicemail phone tag. Appointments just appear in Cliniko.</p>

    <p>Would you be open to a 15-minute call to see if this could work for your practice?</p>

    <a href="https://cal.com/p-b-ttzvpm/15min" class="cta">Book a 15-min Demo</a>

    <p>Cheers,<br>
    Peter Ball<br>
    YES AI | (03) 9999 7398</p>

    <p><a href="https://yesai.au/case-studies/reignite-health">See the full case study</a></p>

    <div class="footer">
        <p>Yes AI | Melbourne, Australia | hello@yesai.au<br>
        <a href="{{unsubscribe}}">Unsubscribe</a></p>
    </div>
</body>
</html>
"""
    },

    "ah_case_study": {
        "name": "Allied Health - Case Study",
        "subject": "How 877 patients now book appointments without waiting on hold",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .logo { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
        .logo .yes { color: #e53935; }
        .logo .ai { color: #1565c0; }
        .stats { background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .stats li { margin: 8px 0; }
        .cta { background: #1565c0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 15px 0; }
        .footer { font-size: 12px; color: #666; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        a { color: #1565c0; }
    </style>
</head>
<body>
    <div class="logo"><span class="yes">Yes</span> <span class="ai">AI</span></div>

    <p>Hi {{params.FIRSTNAME}},</p>

    <p>I wanted to share something relevant for your practice.</p>

    <p>We recently completed an AI voice receptionist implementation for Reignite Health, an allied health provider serving aged care residents across Sydney and the Central Coast.</p>

    <p><strong>The challenge:</strong></p>
    <ul>
        <li>High call volume overwhelming reception</li>
        <li>Multiple funding types (DVA, HCP, Medicare, NDIS, private)</li>
        <li>Calls going to voicemail after hours</li>
        <li>Staff spending hours on routine booking calls</li>
    </ul>

    <p><strong>The solution:</strong> An AI receptionist that integrates directly with Cliniko to answer calls 24/7, check real-time availability, and create bookings.</p>

    <div class="stats">
        <strong>Key stats:</strong>
        <ul>
            <li>10 villages served</li>
            <li>877+ patients in the system</li>
            <li>26 different service types</li>
            <li>80+ features built into the AI</li>
            <li>2,000+ classes booked per year</li>
        </ul>
    </div>

    <p>Worth a 15-minute look?</p>

    <a href="https://cal.com/p-b-ttzvpm/15min" class="cta">Book a Demo</a>

    <p>Best,<br>
    Peter Ball<br>
    YES AI | (03) 9999 7398</p>

    <p>
        <a href="https://yesai.au/case-studies/reignite-health">Read the full case study</a> |
        <a href="https://yesai.au/case-studies/Reignite_Health_Case_Study_2025.pdf">Download PDF</a>
    </p>

    <div class="footer">
        <p>Yes AI | Melbourne, Australia | hello@yesai.au<br>
        <a href="{{unsubscribe}}">Unsubscribe</a></p>
    </div>
</body>
</html>
"""
    },

    "ah_after_hours": {
        "name": "Allied Health - After Hours",
        "subject": "What happens when a patient calls at 7pm?",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .logo { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
        .logo .yes { color: #e53935; }
        .logo .ai { color: #1565c0; }
        .highlight { background: #fff3e0; padding: 15px; border-left: 4px solid #ff9800; margin: 20px 0; }
        .cta { background: #1565c0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 15px 0; }
        .footer { font-size: 12px; color: #666; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        a { color: #1565c0; }
    </style>
</head>
<body>
    <div class="logo"><span class="yes">Yes</span> <span class="ai">AI</span></div>

    <p>Hi {{params.FIRSTNAME}},</p>

    <div class="highlight">
        <strong>Did you know?</strong> 23% of healthcare appointment requests come outside business hours.
    </div>

    <p>If your practice goes to voicemail after 5pm, you're almost certainly losing bookings to competitors who answer.</p>

    <p>We solved this for Reignite Health with an AI receptionist that:</p>

    <ul>
        <li>Answers every call, 24/7/365</li>
        <li>Books into Cliniko in real-time</li>
        <li>Handles Medicare referrals, NDIS funding, HCP claims</li>
        <li>Sounds completely natural</li>
    </ul>

    <p><strong>Their result:</strong> Zero missed calls. Appointments appearing overnight. Staff arriving to a full schedule instead of a voicemail queue.</p>

    <a href="https://cal.com/p-b-ttzvpm/15min" class="cta">See it in Action</a>

    <p>Peter<br>
    YES AI | (03) 9999 7398</p>

    <div class="footer">
        <p>Yes AI | hello@yesai.au<br>
        <a href="{{unsubscribe}}">Unsubscribe</a></p>
    </div>
</body>
</html>
"""
    },

    "ah_funding": {
        "name": "Allied Health - Funding Complexity",
        "subject": "DVA, HCP, Medicare, NDIS, Private - all handled automatically",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .logo { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
        .logo .yes { color: #e53935; }
        .logo .ai { color: #1565c0; }
        .steps { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .steps ol { margin: 10px 0 10px 20px; }
        .cta { background: #1565c0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 15px 0; }
        .footer { font-size: 12px; color: #666; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        a { color: #1565c0; }
    </style>
</head>
<body>
    <div class="logo"><span class="yes">Yes</span> <span class="ai">AI</span></div>

    <p>Hi {{params.FIRSTNAME}},</p>

    <p>The hardest thing about training a receptionist in allied health?</p>

    <p>It's not the booking system. It's explaining the difference between DVA white cards, HCP packages, NDIS plan-managed vs self-managed, Medicare Enhanced Primary Care referrals, and when to ask for a claim number vs a package number.</p>

    <p><strong>Our AI already knows all of this.</strong></p>

    <div class="steps">
        When a patient calls and says "I'm on a home care package through Baptist Care and I need to see the physio," the AI:
        <ol>
            <li>Verifies HCP funding eligibility</li>
            <li>Checks the patient's approved services</li>
            <li>Finds the next available physio slot</li>
            <li>Books directly into Cliniko</li>
            <li>Adds all the right notes for billing</li>
        </ol>
    </div>

    <p>No training required. No mistakes. No "can I put you on hold while I check?"</p>

    <p>This is what we built for Reignite Health (10 villages, 877 patients, all funding types).</p>

    <a href="https://cal.com/p-b-ttzvpm/15min" class="cta">See How It Works</a>

    <p>Peter Ball<br>
    YES AI | (03) 9999 7398</p>

    <div class="footer">
        <p>Yes AI | hello@yesai.au | <a href="https://yesai.au/case-studies/reignite-health">Case Study</a><br>
        <a href="{{unsubscribe}}">Unsubscribe</a></p>
    </div>
</body>
</html>
"""
    },

    "ah_roi": {
        "name": "Allied Health - ROI/Numbers",
        "subject": "The math on AI reception (it's cheaper than you think)",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .logo { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
        .logo .yes { color: #e53935; }
        .logo .ai { color: #1565c0; }
        .math { background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; font-family: monospace; }
        .result { background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4caf50; }
        .cta { background: #1565c0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 15px 0; }
        .footer { font-size: 12px; color: #666; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        a { color: #1565c0; }
    </style>
</head>
<body>
    <div class="logo"><span class="yes">Yes</span> <span class="ai">AI</span></div>

    <p>Hi {{params.FIRSTNAME}},</p>

    <p>Quick math:</p>

    <div class="math">
        Average initial physio consultation: $85-120<br>
        Average patient lifetime value: $500-2,000+<br>
        Calls that go to voicemail and don't return: 30-50%<br>
        <br>
        <strong>If you miss 5 calls/week that would have booked...</strong><br>
        = $2,500-10,000+ potential revenue lost. Every month.
    </div>

    <p>Now compare that to an AI receptionist that:</p>
    <ul>
        <li>Costs a fraction of a full-time hire</li>
        <li>Never calls in sick</li>
        <li>Works 24/7</li>
        <li>Books directly into Cliniko</li>
    </ul>

    <div class="result">
        <strong>Our clients see:</strong><br>
        30% average cost reduction | 3x typical ROI
    </div>

    <p>Reignite Health is now handling 877 patients across 10 villages with this system.</p>

    <a href="https://cal.com/p-b-ttzvpm/15min" class="cta">Run the Numbers for Your Practice</a>

    <p>Peter Ball<br>
    YES AI | (03) 9999 7398</p>

    <div class="footer">
        <p><a href="https://yesai.au/case-studies/reignite-health">Full case study with numbers</a><br>
        <a href="{{unsubscribe}}">Unsubscribe</a></p>
    </div>
</body>
</html>
"""
    },

    "ah_breakup": {
        "name": "Allied Health - Final/Break-up",
        "subject": "Closing the loop on AI reception",
        "html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .logo { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
        .logo .yes { color: #e53935; }
        .logo .ai { color: #1565c0; }
        .cta { background: #1565c0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 15px 0; }
        .footer { font-size: 12px; color: #666; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
        a { color: #1565c0; }
    </style>
</head>
<body>
    <div class="logo"><span class="yes">Yes</span> <span class="ai">AI</span></div>

    <p>Hi {{params.FIRSTNAME}},</p>

    <p>I've sent a few emails about our AI receptionist for Cliniko practices and haven't heard back - which is totally fine.</p>

    <p>I don't want to keep bothering you, so this will be my last email.</p>

    <p>If AI phone reception isn't the right fit for your practice right now, I completely understand. Healthcare is busy and there are a million priorities.</p>

    <p>But if it ever becomes relevant - maybe you're hiring a receptionist and wondering about alternatives, or you're frustrated with after-hours voicemails - the offer stands:</p>

    <p>
        <a href="https://cal.com/p-b-ttzvpm/15min" class="cta">Book a Demo Anytime</a>
    </p>

    <p>
        <a href="https://yesai.au/case-studies/reignite-health">View Case Study</a>
    </p>

    <p>Either way, I wish you and the team all the best.</p>

    <p>Cheers,<br>
    Peter Ball<br>
    YES AI | (03) 9999 7398</p>

    <div class="footer">
        <p>Yes AI | hello@yesai.au<br>
        <a href="{{unsubscribe}}">Unsubscribe</a></p>
    </div>
</body>
</html>
"""
    }
}

# Merge Allied Health templates into main EMAIL_TEMPLATES
EMAIL_TEMPLATES.update(ALLIED_HEALTH_EMAILS)


# ========== SMS TEMPLATES ==========

SMS_TEMPLATES = {
    "intro": "Hi {FIRSTNAME}, this is Yes AI. We help businesses automate with AI. Interested in a free consultation? Reply YES or call (03) 9999 7398",
    "followup": "Hi {FIRSTNAME}, following up on AI solutions for your business. Have 15 mins for a quick chat? Reply YES or call (03) 9999 7398 - Peter from Yes AI",
    "demo_offer": "Hi {FIRSTNAME}, Yes AI here. We're offering free AI demos this week - see an AI phone agent in action. Reply DEMO to book. yesai.au",

    # Allied Health SMS Templates
    "ah_initial": "Hi {FIRSTNAME}, Peter from YES AI. We help Cliniko practices answer every call 24/7 with AI. Just helped Reignite Health (10 villages, 877 patients) go live. 15-min demo? cal.com/p-b-ttzvpm/15min",
    "ah_followup": "Hi {FIRSTNAME}, following up - would a short demo of the AI receptionist be useful? Books directly into Cliniko, handles DVA/HCP/Medicare/NDIS. 15 mins: cal.com/p-b-ttzvpm/15min - Peter",
    "ah_after_hours": "Quick Q {FIRSTNAME} - how many calls does your practice miss after 5pm? Our AI answers 24/7 and books into Cliniko. Case study: yesai.au/case-studies/reignite-health - Peter",
    "ah_case_study": "Hi {FIRSTNAME}, case study for you - Reignite Health (allied health, 10 villages) using AI to handle all booking calls. Details: yesai.au/case-studies/reignite-health - Peter, YES AI",
    "ah_stats": "{FIRSTNAME} - our allied health AI: 877 patients, 26 service types, 80+ features, 24/7. All booking into Cliniko. 15-min demo? cal.com/p-b-ttzvpm/15min - Peter",
    "ah_funding": "{FIRSTNAME}, our AI handles Medicare/DVA/HCP/NDIS automatically - no training. Just helped Reignite Health (10 villages) go live. Demo? cal.com/p-b-ttzvpm/15min - Peter",
    "ah_roi": "{FIRSTNAME}, missed calls = missed revenue. Our AI catches every call 24/7 and books into Cliniko. 30% avg cost reduction. Demo: cal.com/p-b-ttzvpm/15min - Peter",
    "ah_pdf": "Hi {FIRSTNAME}, full case study PDF on AI reception for allied health. Download: yesai.au/case-studies/Reignite_Health_Case_Study_2025.pdf - Peter, YES AI",
    "ah_voice": '{FIRSTNAME}, "Does it sound robotic?" - #1 question we get. Short answer: patients don\'t notice. Hear a demo: cal.com/p-b-ttzvpm/15min - Peter',
    "ah_breakup": "{FIRSTNAME}, last msg from me! If AI reception isn't right for you now, no worries. If things change: cal.com/p-b-ttzvpm/15min - Peter"
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
