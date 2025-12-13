# Next Steps - Brevo Import Continuation

**Read first:** `BREVO_IMPORT_STATUS.md` for full context

---

## IMMEDIATE TODO (Priority Order)

### 1. Update All Contacts with COMPANY Attribute
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python update_contact_attributes.py
```
- Takes ~30 minutes
- Updates 32,000+ contacts with COMPANY, SOURCE, names
- Can run with `--limit 1000` to test first

### 2. Import All Appointments
```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts
python import_appointments.py
```
- Imports 87 appointments
- Adds full data: dates, status, deal stage
- Assigns to "Had Appointments" list (ID: 28)

### 3. Verify Data
```bash
python -c "
from brevo_api import BrevoClient
client = BrevoClient()
# Check a few contacts
for email in ['sara@reignitehealth.com.au', 'admin@coolsolutions.com.au']:
    c = client.get_contact(email)
    if c.get('success'):
        print(f'{email}: {c[\"data\"].get(\"attributes\", {})}')
"
```

---

## VERIFICATION CHECKLIST

After running imports, verify in Brevo UI:

- [ ] Search for "Reignite Health" - should show Sara Lehmann with all data
- [ ] Check Companies page - should have 68+ companies
- [ ] Check contact lists - should show subscriber counts (may be delayed)
- [ ] Search for DNC contact - should show emailBlacklisted=true

---

## KNOWN STATES

### Contacts: 35,493
- All imported to Brevo
- ~1,000 have COMPANY attribute updated
- Rest need `update_contact_attributes.py`

### Companies: 68
- 17 have real names (from appointments)
- 51 have domain names (from telemarketer list)
- All linked to contacts

### Lists (IDs 24-29)
- Created and contacts assigned
- Subscriber counts may show 0 (Brevo cache issue)
- Contacts DO have correct listIds

### DNC: 658
- Should be blocklisted (emailBlacklisted=true)
- In list ID 27 "DO NOT CALL"

---

## KEY FILES TO READ

1. `BREVO_IMPORT_STATUS.md` - Full status report
2. `SCRIPTS_REFERENCE.md` - How to use each script
3. `C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv` - Source data

---

## RETELL WORKSPACES

Two different Retell workspaces exist:

1. **Reignite Receptionist** (main)
   - API Key: `C:\Users\peter\Downloads\Retell_API_Key.txt`
   - Used for AI receptionist

2. **Telemarketer Dialer**
   - API Key: `key_48d1b17aad7e13d3ea841faaee47`
   - Has outbound call history
   - Google Sheet with call data (needs auth to access)

---

## QUICK FIXES

### If lists show 0 subscribers
Run `assign_contacts_to_lists.py` to re-assign

### If company not linked to contact
```python
from brevo_api import BrevoClient
client = BrevoClient()

# Get contact ID
contact = client.get_contact('email@example.com')
contact_id = contact['data']['id']

# Link to company
client._request('PATCH', f'companies/link-unlink/{company_id}', {
    'linkContactIds': [contact_id]
})
```

### If need to send email
Must use `yesrightau@gmail.com` as sender (verified in Brevo)
