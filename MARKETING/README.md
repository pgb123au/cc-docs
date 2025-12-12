# Yes AI Marketing Automation

Automated marketing system using Brevo for email/SMS campaigns.

## Quick Start

### 1. Get Your Brevo API Key

1. Create free account at [brevo.com](https://www.brevo.com)
2. Go to: Settings → SMTP & API → API Keys
3. Create a new API key
4. Save it to: `C:\Users\peter\Downloads\CC\Brevo_API_Key.txt`

### 2. Test Connection

```bash
cd C:\Users\peter\Downloads\CC\MARKETING\scripts
python brevo_api.py
```

Should show your account details if connected.

### 3. Import Contacts

**Drop files here:**
```
C:\Users\peter\Downloads\CC\MARKETING\imports\pending\
```

Supported formats: `.csv`, `.xlsx`, `.xls`

**Run import:**
```bash
python import_contacts.py
```

**Or with list name:**
```bash
python import_contacts.py --list "VIC Healthcare Leads"
```

### 4. Create Campaign

```bash
python campaigns.py templates              # See available templates
python campaigns.py create --template yesai_intro
python campaigns.py send 123               # Send campaign ID 123
```

### 5. Send SMS

```bash
python campaigns.py sms "+61412345678" "Hi, this is Yes AI..."
python campaigns.py sms "+61412345678" --template intro
```

---

## Folder Structure

```
MARKETING/
├── imports/
│   ├── pending/      ← DROP XLS/CSV FILES HERE
│   ├── processed/    ← Successfully imported
│   └── errors/       ← Files with issues
├── campaigns/        ← Campaign definitions
├── templates/        ← Custom email templates
├── reports/          ← Auto-generated import reports
└── scripts/
    ├── brevo_api.py       ← API wrapper
    ├── import_contacts.py ← Bulk import
    └── campaigns.py       ← Campaign management
```

---

## Column Auto-Detection

The import script automatically detects these columns:

| Field | Detected Headers |
|-------|------------------|
| Email | email, e-mail, email_address |
| Mobile | mobile, phone, cell, contact_number |
| First Name | first_name, firstname, first |
| Last Name | last_name, lastname, surname |
| Full Name | name, full_name, contact_name |
| Company | company, business, organisation |
| Postcode | postcode, post_code, zip |
| Suburb | suburb, city, town |
| State | state, region |

---

## Commands Reference

### Import Contacts
```bash
python import_contacts.py                      # All files in pending/
python import_contacts.py myfile.xlsx          # Specific file
python import_contacts.py --list "VIC Leads"   # Create/use list
python import_contacts.py --dry-run            # Preview only
```

### Campaigns
```bash
python campaigns.py list                       # List all campaigns
python campaigns.py stats 123                  # Campaign statistics
python campaigns.py create --template yesai_intro
python campaigns.py send 123                   # Send campaign
python campaigns.py account                    # Show account/credits
python campaigns.py lists                      # Show contact lists
```

### SMS
```bash
python campaigns.py sms "+61412345678" "Your message"
python campaigns.py sms "+61412345678" --template intro
```

---

## Email Templates

| Template | Purpose |
|----------|---------|
| `yesai_intro` | General Yes AI introduction |
| `healthcare_ai` | Healthcare-focused AI receptionist pitch |
| `followup` | Follow-up email for non-responders |

---

## SMS Templates

| Template | Message |
|----------|---------|
| `intro` | Initial outreach with consultation offer |
| `followup` | Follow-up for non-responders |
| `demo_offer` | Demo invitation |

---

## Workflow: You Send Data, Claude Does Everything

1. **You:** Drop XLS/CSV into `imports/pending/`
2. **Claude:** Import contacts, dedupe, normalize phones
3. **Claude:** Create campaign from template
4. **Claude:** Send to your list
5. **Claude:** Report back stats

---

## Dependencies

```bash
pip install requests openpyxl
```

For pandas (optional, alternative Excel reading):
```bash
pip install pandas openpyxl
```

---

## Brevo Free Plan Limits

- 300 emails/day (9,000/month)
- Unlimited contacts
- SMS: Pay per message (~$0.05 AUD)
- 1 sales pipeline, 50 deals

---

## API Key Location

The scripts look for your API key in this order:
1. `C:\Users\peter\Downloads\CC\Brevo_API_Key.txt`
2. Environment variable: `BREVO_API_KEY`

---

## Support

- Brevo Dashboard: [app.brevo.com](https://app.brevo.com)
- Brevo API Docs: [developers.brevo.com](https://developers.brevo.com)
- Yes AI: hello@yesai.au
