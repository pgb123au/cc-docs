# Brevo CRM Import - Status Report

**Last Updated:** 2025-12-13 08:00 AEDT
**Session:** Marketing Automation Setup

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
- `APPOINTMENT_STATUS` - Status (e.g., "Seen - Client")
- `DEAL_STAGE` - Won/Lost/Negotiation/etc.

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

**Reignite Health (COMPLETE):**
```
Contact:
  Email: sara@reignitehealth.com.au
  FIRSTNAME: Sara
  LASTNAME: Lehmann
  COMPANY: Reignite Health
  APPOINTMENT_DATE: 2025-09-17
  APPOINTMENT_STATUS: Seen - Client
  DEAL_STAGE: Won
  SOURCE: Telemarketer Campaign
  Lists: [24, 25, 28]

Company:
  Name: Reignite Health
  Domain: reignitehealth.com.au
  Linked Contacts: [778]
```

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
7. [ ] Optionally: Import Google Sheet call data (needs auth)
