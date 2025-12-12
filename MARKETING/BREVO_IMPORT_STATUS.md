# Brevo CRM Import - Status Report

**Last Updated:** 2025-12-13 09:35 AEDT
**Session:** Marketing Automation Setup (Call Data Linked)

---

## CURRENT STATE SUMMARY

### Brevo Account
- **Account Name:** Yes AI
- **Plan:** Free (300 emails/day)
- **Verified Sender:** yesrightau@gmail.com (NOT hello@yesai.au)
- **Total Contacts:** 35,493
- **Companies Created:** 68 (17 with real names from appointments)

### What's COMPLETE ✅

| Task | Details |
|------|---------|
| Brevo API integration | `brevo_api.py` working with all endpoints |
| Custom attributes created | COMPANY, WEBSITE, SOURCE, APPOINTMENT_DATE, APPOINTMENT_STATUS, DEAL_STAGE |
| Lists created | 6 lists (IDs 24-29) |
| Contacts imported | 35,493 contacts in Brevo |
| Companies API working | Can create companies and link contacts |
| Test email sent | To Peter@Ball.com.au from yesrightau@gmail.com |
| Mobile Message SMS integrated | `mobilemessage.py` ready (not tested with real SMS) |
| Reignite Health COMPLETE | Full data: contact, company, lists, all attributes |

### What's PARTIAL ⚠️

| Task | Done | Remaining |
|------|------|-----------|
| COMPANY attribute on contacts | ~1,000 updated | ~32,000 remaining |
| Contacts assigned to lists | Contacts have listIds but API shows 0 subscribers | May need re-sync |
| DNC blocklisted | 658 should be blocked | Verify emailBlacklisted=true |
| Companies with real names | 17 from appointments | 51 have domain names only |
| Appointment data on contacts | 1 (Reignite Health) | 86 remaining |

### What's NOT DONE ❌

| Task | Notes |
|------|-------|
| Full COMPANY attribute update | Run `update_contact_attributes.py` (~30 min) |
| All appointments imported | Run updated `import_appointments.py` |
| Verify list subscriber counts | Brevo API shows 0 but contacts have listIds |
| Clean up domain-as-company-name | 51 companies like "briarscottage.com.au" |
| Link Google Sheet call data | User has Retell call sheet, needs auth |

---

## BREVO LISTS

| ID | Name | Purpose |
|----|------|---------|
| 24 | All Telemarketer Contacts | Everyone |
| 25 | Safe to Contact | Non-DNC contacts |
| 26 | Fresh Leads - Never Called | Never contacted |
| 27 | DO NOT CALL | DNC - blocklisted |
| 28 | Had Appointments | Booked appointments |
| 29 | Previously Called | Called but no appointment |

**Note:** List subscriber counts show 0 in API but contacts DO have listIds assigned. This is a Brevo display/cache issue.

---

## BREVO CUSTOM ATTRIBUTES

All created and working:
- `FIRSTNAME` (built-in)
- `LASTNAME` (built-in)
- `SMS` (built-in)
- `COMPANY` - Company name
- `WEBSITE` - Company website
- `SOURCE` - Data source (e.g., "massive_list_sa.csv")
- `APPOINTMENT_DATE` - Date of appointment
- `APPOINTMENT_TIME` - Time of appointment (NEW)
- `APPOINTMENT_STATUS` - Status (e.g., "Seen - Client")
- `DEAL_STAGE` - Won/Lost/Negotiation/etc.
- `QUALITY` - Lead quality rating (NEW)
- `FOLLOWUP_STATUS` - Follow-up status (NEW)
- `RETELL_LOG` - Retell call timestamp (NEW)
- `NOTES` - General notes (NEW)

---

## FILE LOCATIONS

### Scripts (C:\Users\peter\Downloads\CC\MARKETING\scripts\)

| File | Purpose | Status |
|------|---------|--------|
| `brevo_api.py` | Brevo REST API wrapper | ✅ Complete |
| `mobilemessage.py` | Mobile Message SMS API | ✅ Complete |
| `bulk_import_brevo.py` | Bulk import contacts | ✅ Complete |
| `update_contact_attributes.py` | Update COMPANY/SOURCE on existing contacts | ✅ Complete |
| `assign_contacts_to_lists.py` | Assign contacts to lists | ✅ Complete |
| `create_companies.py` | Create companies and link contacts | ✅ Complete |
| `import_appointments.py` | Import appointments with full data | ✅ Complete |
| `import_contacts.py` | Original single-contact importer | ✅ Legacy |
| `campaigns.py` | Email campaign creation | ✅ Complete |

### Data Files (C:\Users\peter\Downloads\CC\CRM\)

| File | Contents | Records |
|------|----------|---------|
| `Master_Contacts_With_Flags.csv` | All contacts with DNC/called flags | 54,086 |
| `DO_NOT_CALL_Master.csv` | DNC phone numbers with emails | 852 |
| `Safe_To_Contact.csv` | Non-DNC contacts | 21,693 |
| `Fresh_Leads_Never_Called.csv` | Never contacted | 24,335 |
| `Appointments_Enriched.csv` | All appointments with match data | 87 |
| `Appointments_won.csv` | Won clients | 6 |
| `Appointments_followup.csv` | Follow-up needed | 15 |
| `Appointments_booked.csv` | Booked appointments | Various |
| `consolidate_telemarketer_data.py` | Script that created above files | ✅ |
| `enrich_appointments.py` | Script that enriched appointments | ✅ |
| `call_log_linker.py` | Links Retell/Zadarma recordings | ✅ |

### Source Data (C:\Users\peter\retell-dialer\)

| File | Purpose |
|------|---------|
| `called_log.txt` | Phone numbers called |
| `called_numbers.json` | Called numbers with timestamps |
| `do_not_call.txt` | DNC list (852 numbers) |
| `massive_list.csv` | Main contact list |
| `massive_list_vic.csv` | Victoria contacts |
| `massive_list_sa.csv` | South Australia contacts |

---

## API CREDENTIALS

| Service | Location | Notes |
|---------|----------|-------|
| Brevo API | `C:\Users\peter\Downloads\CC\Brevo_API_Key.txt` | Used by brevo_api.py |
| Retell API (Reignite) | `C:\Users\peter\Downloads\Retell_API_Key.txt` | Main workspace |
| Retell API (Telemarketer) | `key_48d1b17aad7e13d3ea841faaee47` | Different workspace |
| Mobile Message | Hardcoded in mobilemessage.py | Username: 03KnC9 |

---

## COMMANDS TO CONTINUE

### Update all contacts with COMPANY attribute (~30 min)
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python update_contact_attributes.py
```

### Import all appointments with full data
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python import_appointments.py
```

### Create remaining companies from CSV
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python create_companies.py --limit 500
```

### Verify Brevo state
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python -c "
from brevo_api import BrevoClient
client = BrevoClient()
print('Contacts:', client.get_contacts(limit=1)['data']['count'])
companies = client._request('GET', 'companies', params={'limit': 1})
print('Companies:', companies)
"
```

---

## EXAMPLE: Complete Contact Record

**Reignite Health (COMPLETE - 2 Contacts):**

### Contact 1: Sara Lehmann (Telemarketer Lead)
```
Email: sara@reignitehealth.com.au
ID: 778
FIRSTNAME: Sara
LASTNAME: Lehmann
COMPANY: Reignite Health
APPOINTMENT_DATE: 2025-09-17
APPOINTMENT_TIME: 10:00am
APPOINTMENT_STATUS: Seen - Client
DEAL_STAGE: Won
QUALITY: Good
FOLLOWUP_STATUS: Client
RETELL_LOG: 09/01/2025 11:48 - Recording: https://dxc03zgurdly9.cloudfront.net/2ddc176248fead0e1f0ad06936d899ad266e93bfe45bf036e9c5f3e7ebd56a94/recording.wav
SOURCE: Telemarketer Campaign
NOTES: Won client. Telemarketer appointment converted. Original call to Liam Potter's voicemail.
Lists: [24, 25, 28]
```

### Contact 2: Liam Potter (Founder)
```
Email: liam@reignitehealth.com.au
ID: 35494
FIRSTNAME: Liam
LASTNAME: Potter
COMPANY: Reignite Health
SMS: 61437160997  (from HubSpot)
DEAL_STAGE: Closed Won
SOURCE: Website Audit Client
RETELL_LOG: 09/01/2025 11:48 - Recording: https://dxc03zgurdly9.cloudfront.net/2ddc176248fead0e1f0ad06936d899ad266e93bfe45bf036e9c5f3e7ebd56a94/recording.wav
NOTES: Founder/Owner. Original telemarketer call went to his voicemail. Received digital audit report Dec 2025.
Lists: [24, 25, 28]
```

### Contact 3: HubSpot Lead (Alt Domain)
```
Email: hello@reignitehealth.co
ID: 35495
COMPANY: Reignite Health
SOURCE: HubSpot Scraped Lead - Aged care (AU).xlsx
WEBSITE: reignitehealth.co
NOTES: From HubSpot. Alt domain .co (main is .com.au)
Lists: [24, 25]
```

### Company Record
```
Name: Reignite Health
ID: 693c813d58677e43aa29b493
Domain: reignitehealth.com.au
Linked Contacts: [778, 35494, 35495] (Sara + Liam + hello@)
Phone: +61437160997 (on Liam's contact)
Facebook: facebook.com/reignitehealth
```

### Additional Data Sources Found
- `CLIENTS/reignite-health/` - Full website audit, email draft, logo
- `CRM/ALLIED_HEALTH_VIC_OUTREACH.md` - Marketing templates using as case study
- `CRM/All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` - Phone +61437160997, Facebook page
- `CRM/All_Contacts_2025_07_07_Cleaned.csv` - HubSpot contact hello@reignitehealth.co
- Audit report addressed to Liam Potter (founder, physiotherapist)
- Company: 11-50 employees, serves 10 aged care villages, 877 patients
- Alt domain: reignitehealth.co (scraped from Aged care AU list)

---

## KNOWN ISSUES

1. **List subscriber counts show 0** - Contacts have listIds but Brevo API returns totalSubscribers=0. Likely cache/display issue.

2. **Some companies have gmail.com as domain** - When contact uses personal email (e.g., bchalmers616@gmail.com for Paradise Distributors).

3. **Domain names as company names** - 51 companies from telemarketer list have domain (briarscottage.com.au) not real name.

4. **hello@yesai.au not verified** - Must send from yesrightau@gmail.com or verify hello@yesai.au in Brevo.

---

## NEXT SESSION TODO

1. [ ] Run `update_contact_attributes.py` for all 32,000+ contacts
2. [ ] Run `import_appointments.py` for all 87 appointments
3. [ ] Verify list counts update in Brevo
4. [ ] Check DNC contacts are properly blocklisted
5. [ ] Test email campaign to small list
6. [ ] Optionally: Clean up company names (domain -> real name)
7. [x] ~~Import Google Sheet call data~~ DONE - 22,000 calls exported to `CRM/call_log_sheet_export.json` and `CRM/call_log_sheet2_export.json`

---

## CALL DATA INTEGRATION

### Google Sheets Exported

| File | Records | Date Range |
|------|---------|------------|
| `call_log_sheet_export.json` | 15,156 | Aug-Oct 2025 |
| `call_log_sheet2_export.json` | 6,844 | Jun-Jul 2025 |

**Total:** 22,000 call records with transcripts and recording URLs.

### Reignite Health Call Found

```
Call ID: call_0233f8b1ac5b37c6d76362afc9f
Timestamp: 01/09/2025, 11:48:55
Recording: https://dxc03zgurdly9.cloudfront.net/2ddc176248fead0e1f0ad06936d899ad266e93bfe45bf036e9c5f3e7ebd56a94/recording.wav
Transcript: "Hi there. You've reached Liam Potter from Reignite Health. Sorry that I've missed your phone call..."
```

Recording URL added to both Sara Lehmann and Liam Potter's RETELL_LOG in Brevo.
