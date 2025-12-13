# Comprehensive Brevo Import Plan

**Created:** 2025-12-13
**Updated:** 2025-12-13 (v4 with mandatory data rule + call linking)
**Status:** READY FOR APPROVAL
**Approach:** Layer-by-layer import (contacts first, then enrich with appointments/calls)

---

## ⚠️ MANDATORY DATA IMPORT RULE (v3)

**ALL COMPANY AND CONTACT DATA AND ALL OTHER RELATED DATA MUST COME INTO BREVO!**

The ONLY exception: Do not overwrite existing good data with worse/empty data.

### What This Means:

1. **Every available field must be imported** - If it exists in source data, it goes into Brevo
2. **Companies must have ALL available attributes:**
   - Domain (from HubSpot or email domain)
   - Industry (from HubSpot)
   - Phone (from HubSpot, appointments, or contact)
   - City/Location (from HubSpot or appointments `location` field)
   - Website (from appointments `website_from_list` field)
   - All social links (from HubSpot)
   - All business intelligence (revenue, employees, etc.)
3. **Contacts must have ALL available attributes:**
   - All phone numbers (SMS, PHONE_2, PHONE_3)
   - All location fields (city, state, suburb, postal code)
   - All enrichment data from HubSpot match
   - All call log data
4. **Never leave a field empty if data exists somewhere**

### Merge Priority (when data exists in multiple sources):
1. HubSpot Companies (most complete)
2. HubSpot Contacts
3. Appointments Enriched
4. Call Logs
5. Master Contacts

---

## ⚠️ MANDATORY CALL LINKING RULE (v4)

**ALL RETELL AND ZADARMA CALLS MUST BE LINKED TO BREVO CONTACTS/COMPANIES**

### Call Data Sources:
1. **Retell AI Calls** - `call_log_sheet_export.json`, `call_log_sheet2_export.json` (22,000 calls)
2. **Zadarma Calls** - Future integration (PBX/VoIP calls)

### Linking Strategy:

**For each call, link to Brevo record by:**
1. **Phone number match** (last 9 digits) to contact's SMS, PHONE_2, or PHONE_3
2. **Company phone match** to company's phone_number attribute
3. If no match found, create a new contact with the phone number

### How Calls Are Stored:

**Option A: RETELL_LOG Attribute (Current Implementation)**
- Stores call history as text field on contact
- Format: `DD/MM/YYYY HH:MM DIRECTION (duration) - Recording: URL`
- Pros: Simple, searchable, visible in contact profile
- Cons: Limited structure, can't query individual calls

**Option B: Brevo Activities/Events API (Future Enhancement)**
- Use Brevo's activity tracking to log each call as an event
- Each call = separate activity linked to contact
- Pros: Full call analytics, timeline view, filtering
- Cons: More complex, requires activity API setup

**Current Decision:** Use Option A (RETELL_LOG) for initial import, with Option B available for future real-time integration.

### Required Call Data Fields:

| Field | Source | Brevo Storage |
|-------|--------|---------------|
| Call date/time | start_time | RETELL_LOG (text) |
| Direction | direction | RETELL_LOG (INBOUND/OUTBOUND) |
| Duration | human_duration | RETELL_LOG |
| Recording URL | recording_url | RETELL_LOG |
| Call status | status | RETELL_LOG |
| Total call count | (calculated) | CALL_COUNT (number) |
| Was ever called | (calculated) | WAS_CALLED (boolean) |

### Zadarma Integration (Future):

When Zadarma integration is added:
1. Match calls to contacts by phone number (same as Retell)
2. Append to RETELL_LOG with source tag: `[ZADARMA]` prefix
3. Update CALL_COUNT to include both sources
4. Consider separate ZADARMA_LOG attribute if call volume is high

### Example - Contact Must Have All Call Data:
```
Contact: Sara Lehmann (sara@reignitehealth.com.au)
  - RETELL_LOG:
    09/01/2025 11:48 OUTBOUND (3m 45s) - Recording: https://...
    09/03/2025 14:22 INBOUND (1m 12s) - Recording: https://...
  - CALL_COUNT: 2
  - WAS_CALLED: true
```

### Example - Company Must Have All Call Data:
```
Company: Reignite Health
  Linked calls (via contacts):
    - Sara Lehmann: 2 calls
    - (other contacts): N calls
  Total company calls: (sum of all linked contact calls)
```

### Example - Company Must Have:
```
Company: Paradise Distributors
  - name: Paradise Distributors ✅
  - domain: (extract from contact email if no HubSpot match)
  - phone_number: (from contact's phone if available)
  - city: (from location field if available)
  - website: (from website_from_list if available)
```

---

## CORRECTIONS FROM TEST IMPORT (v2)

After running a test import of 200 records, the following corrections were identified:

### 1. Company Name Source (CRITICAL)
**❌ WRONG:** Creating companies from appointment data (which often has URLs/domains as company names)
**✅ CORRECT:** Companies MUST come from HubSpot Companies file (363K records). Never use domain names as company names.

**Process:**
1. First, create companies from HubSpot Companies file ONLY
2. Match appointment contacts to existing companies by:
   - Email domain matching
   - Company name fuzzy matching
3. Flag any appointments that don't match a HubSpot company

### 2. Name Cleaning
**❌ WRONG:** Strip "?" from names before import
**✅ CORRECT:** Keep "?" in names - it indicates uncertainty in the source data (e.g., "Ken?", "Mal Stanes ?")

### 3. SMS Conflict Handling
**Problem:** Brevo only allows one phone per SMS field globally
**Solution:** If SMS field fails, store phone in PHONE_2 or NOTES field instead

### 4. Company Matching for Appointments
**❌ WRONG:** Use COMPANY field from appointments directly
**✅ CORRECT:**
1. Look up company in HubSpot Companies file (EXACT match only)
2. If found → create company from HubSpot data (domain, industry, etc.)
3. If NOT found → create company using appointment's company name (not domain)
4. Never create a company from a domain or URL

### 5. Company Name Matching Rules (v2 - Critical)
**Problems found in v1:**
- Partial matching too loose ("Aaron Climate Control" matched "Climate Control")
- Email domain matching pulled records where company name = domain
- Single-letter company names matched everything

**✅ CORRECT Matching Rules:**
1. **EXACT match only** for company names (case-insensitive)
2. **NO partial matching** - too error-prone with 363K records
3. **NO email domain matching** - HubSpot has domains as company names
4. If no exact match → create company from appointment data using the COMPANY field

### 6. Phone Validation for Companies
**Problem:** HubSpot phone numbers often fail Brevo validation
**Solution:** Try with phone first, if validation fails, retry without phone

### 7. Company Linking
**CRITICAL:** Always link contacts to company entities
- Create company FIRST
- Get company_id from response
- Create contact
- Link contact to company using: `PATCH /companies/link-unlink/{company_id}`

---

## EXECUTIVE SUMMARY

### Why Layer-by-Layer Import?

**Recommended:** Import base contacts first, then add appointment and call data separately.

| Approach | Pros | Cons |
|----------|------|------|
| **Layer-by-Layer (Recommended)** | Easier to verify each phase; Can stop if issues; Simpler scripts; Better error handling | Multiple API calls per contact |
| All-at-Once | Single import | Complex merging; Hard to debug; Can't verify intermediate steps |

### Data Volumes

| Source | Total Records | With Email | Importable |
|--------|---------------|------------|------------|
| Master Contacts | 54,086 | 34,796 | 34,796 |
| HubSpot Contacts | 207,277 | 207,277 | ~172,000 (excluding Master overlap) |
| Appointments | 87 | 82 | 82 |
| Call Logs | 22,000 | N/A | Links to 19,470 unique phones |

### Brevo Capacity

| Metric | Current | After Import | Limit | Headroom |
|--------|---------|--------------|-------|----------|
| Contact Attributes | 23 | 72 | 200 | 128 |
| Company Attributes | 15 (built-in) | 15 | Unknown | OK |
| Contacts | 0 | ~35,000 | Unlimited | OK |
| Companies | 0 | ~38 | Unlimited | OK |

---

## DATA FILES INVENTORY

### ORIGINAL SOURCE FILES (Raw Data)

#### HubSpot CRM Exports (2025-07-07)

| File | Full Path | Records | Used In Plan? |
|------|-----------|---------|---------------|
| **HubSpot Companies** | `C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` | 363,516 | YES - Phase 3 company enrichment |
| **HubSpot Contacts** | `C:\Users\peter\Documents\HS\All_Contacts_2025_07_07_Cleaned.csv` | 207,277 | YES - Phase 1B + enrichment |

**Note:** Copies also exist at `C:\Users\peter\Downloads\CC\CRM\` - identical files, use either location.

#### Telemarketer Dialer Original Files

| File | Full Path | Records | Used In Plan? |
|------|-----------|---------|---------------|
| **Massive List - Main** | `C:\Users\peter\retell-dialer\massive_list.csv` | 47,086 | NO - superseded by Master_Contacts |
| **Massive List - Victoria** | `C:\Users\peter\retell-dialer\massive_list_vic.csv` | 19,238 | NO - superseded by Master_Contacts |
| **Pakenham Companies** | `C:\Users\peter\retell-dialer\companies_pakenham.csv` | 196 | NO - merged into Master_Contacts |
| **Called Log (Text)** | `C:\Users\peter\retell-dialer\called_log.txt` | 27,785 | NO - superseded by call_log JSON |
| **Called Log (Backup)** | `C:\Users\peter\retell-dialer\called_log_backup.txt` | 13,455 | NO - backup only |
| **Called Numbers (JSON)** | `C:\Users\peter\retell-dialer\called_numbers.json` | 27,799 | NO - use Retell call logs instead |
| **Do Not Call List** | `C:\Users\peter\retell-dialer\do_not_call.txt` | 1,051 | NO - MISNAMED (see note below) |
| **Invalid Numbers** | `C:\Users\peter\retell-dialer\invalid_numbers.txt` | 12,511 | NO - reference only |

**IMPORTANT:** The `do_not_call.txt` file is MISNAMED. It contains numbers that were called (for dialer deduplication), NOT actual DNC requests. Only 1 person ever requested DNC - handle manually.

#### Retell API Call Logs

| File | Full Path | Records | Used In Plan? |
|------|-----------|---------|---------------|
| **Call Log Export 1** | `C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json` | 15,156 | YES - Phase 5 RETELL_LOG |
| **Call Log Export 2** | `C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json` | 6,844 | YES - Phase 5 RETELL_LOG |

**Total call records:** 22,000 calls covering Jun-Oct 2025

---

### DERIVED/PROCESSED FILES (Created from originals)

#### Master Contact Files

| File | Full Path | Records | Created From | Used In Plan? |
|------|-----------|---------|--------------|---------------|
| **Master Contacts With Flags** | `C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv` | 54,086 | massive_list + massive_list_vic + call logs | YES - Phase 1A primary import |
| **Fresh Leads Never Called** | `C:\Users\peter\Downloads\CC\CRM\Fresh_Leads_Never_Called.csv` | 24,335 | Master minus called contacts | NO - subset of Master |
| **Safe To Contact** | `C:\Users\peter\Downloads\CC\CRM\Safe_To_Contact.csv` | 21,693 | Called contacts (was mislabeled) | NO - subset of Master |
| **DO NOT CALL Master** | `C:\Users\peter\Downloads\CC\CRM\DO_NOT_CALL_Master.csv` | 852 | do_not_call.txt deduplicated | NO - MISNAMED, delete |
| **Brevo Import Filtered** | `C:\Users\peter\Downloads\CC\CRM\Brevo_Import_Filtered.csv` | 754 | All_Contacts + All_Companies filtered | NO - old partial export |

#### Appointment Files

| File | Full Path | Records | Source | Used In Plan? |
|------|-----------|---------|--------|---------------|
| **All Appointments Extracted** | `C:\Users\peter\Downloads\CC\CRM\All_Appointments_Extracted.csv` | 87 | Google Sheet (all 4 tabs) | NO - superseded by Enriched |
| **Appointments Enriched** | `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv` | 87 | All_Appointments + phone matching | YES - Phase 4 primary |
| **Retell Matched** | `C:\Users\peter\Downloads\CC\CRM\retell_matched_20251213_054522.json` | 84 | Appointments matched to calls | Reference only |

#### Appointment Sub-files (by Status)

| File | Full Path | Records | Used In Plan? |
|------|-----------|---------|---------------|
| **Appointments Won** | `C:\Users\peter\Downloads\CC\CRM\Appointments_won.csv` | 6 | Reference - status in Enriched |
| **Appointments Followup** | `C:\Users\peter\Downloads\CC\CRM\Appointments_followup.csv` | 15 | Reference - status in Enriched |
| **Appointments Booked** | `C:\Users\peter\Downloads\CC\CRM\Appointments_booked.csv` | 4 | Reference - status in Enriched |
| **Appointments No Show** | `C:\Users\peter\Downloads\CC\CRM\Appointments_no_show.csv` | 13 | Reference - status in Enriched |
| **Appointments Bad Prospect** | `C:\Users\peter\Downloads\CC\CRM\Appointments_bad_prospect.csv` | 16 | Reference - status in Enriched |
| **Appointments Contacted** | `C:\Users\peter\Downloads\CC\CRM\Appointments_contacted.csv` | 10 | Reference - status in Enriched |
| **Appointments Dead** | `C:\Users\peter\Downloads\CC\CRM\Appointments_dead.csv` | 1 | Reference - status in Enriched |
| **Appointments Reschedule** | `C:\Users\peter\Downloads\CC\CRM\Appointments_reschedule.csv` | 5 | Reference - status in Enriched |
| **Appointments Seen** | `C:\Users\peter\Downloads\CC\CRM\Appointments_seen.csv` | 2 | Reference - status in Enriched |

**Note:** Appointment sub-files are reference only. All status data is consolidated in `Appointments_Enriched.csv`.

---

### FILES NOT USED IN THIS PLAN

| File | Path | Records | Reason Not Used |
|------|------|---------|-----------------|
| massive_list.csv | `C:\Users\peter\retell-dialer\` | 47,086 | Superseded by Master_Contacts_With_Flags |
| massive_list_vic.csv | `C:\Users\peter\retell-dialer\` | 19,238 | Superseded by Master_Contacts_With_Flags |
| companies_pakenham.csv | `C:\Users\peter\retell-dialer\` | 196 | Merged into Master_Contacts |
| called_log.txt | `C:\Users\peter\retell-dialer\` | 27,785 | Use Retell JSON exports instead (richer data) |
| called_log_backup.txt | `C:\Users\peter\retell-dialer\` | 13,455 | Backup only |
| called_numbers.json | `C:\Users\peter\retell-dialer\` | 27,799 | Use Retell call_log exports (have recordings) |
| do_not_call.txt | `C:\Users\peter\retell-dialer\` | 1,051 | MISNAMED - not actual DNC |
| invalid_numbers.txt | `C:\Users\peter\retell-dialer\` | 12,511 | Reference only |
| DO_NOT_CALL_Master.csv | `C:\Users\peter\Downloads\CC\CRM\` | 852 | MISNAMED - should be deleted |
| Fresh_Leads_Never_Called.csv | `C:\Users\peter\Downloads\CC\CRM\` | 24,335 | Subset of Master - use Master directly |
| Safe_To_Contact.csv | `C:\Users\peter\Downloads\CC\CRM\` | 21,693 | Subset of Master - use Master directly |
| Brevo_Import_Filtered.csv | `C:\Users\peter\Downloads\CC\CRM\` | 754 | Old partial export - outdated |
| All_Appointments_Extracted.csv | `C:\Users\peter\Downloads\CC\CRM\` | 87 | Superseded by Appointments_Enriched |
| Appointment sub-files (9 files) | `C:\Users\peter\Downloads\CC\CRM\` | 72 total | Status data in Enriched file |

---

### SUMMARY: FILES ACTUALLY USED

| Phase | File | Path | Records |
|-------|------|------|---------|
| 1A | Master_Contacts_With_Flags.csv | `C:\Users\peter\Downloads\CC\CRM\` | 54,086 (34,796 with email) |
| 1B | All_Contacts_2025_07_07_Cleaned.csv | `C:\Users\peter\Documents\HS\` | 207,277 |
| 2 | All_Contacts_2025_07_07_Cleaned.csv | (same as 1B) | For enrichment |
| 3 | All_Companies_2025-07-07_Cleaned_For_HubSpot.csv | `C:\Users\peter\Documents\HS\` | 363,516 |
| 4 | Appointments_Enriched.csv | `C:\Users\peter\Downloads\CC\CRM\` | 87 (82 with email) |
| 5 | call_log_sheet_export.json | `C:\Users\peter\Downloads\CC\CRM\` | 15,156 |
| 5 | call_log_sheet2_export.json | `C:\Users\peter\Downloads\CC\CRM\` | 6,844 |

**Total unique source files used:** 5 files

---

## PHASE 0: Create Brevo Attributes

**Duration:** 5 minutes
**Risk:** Low

### New Attributes to Create (49 total)

```
CONTACT ATTRIBUTES BY CATEGORY:

Identity (3 new):
  - PHONE_2 (text)
  - PHONE_3 (text)
  - WORK_EMAIL (text)

Location (6 new):
  - STREET_ADDRESS (text)
  - CITY (text)
  - SUBURB (text)
  - STATE_REGION (text)
  - POSTAL_CODE (text)
  - COUNTRY (text)

Company (3 new):
  - COMPANY_DOMAIN (text)
  - COMPANY_EMAIL (text)
  - COMPANY_PHONE (text)

Professional (4 new):
  - SENIORITY (text)
  - INDUSTRY (text)
  - BUSINESS_TYPE (text)
  - VERTICAL (text)

Social (5 new):
  - TWITTER (text)
  - FACEBOOK (text)
  - INSTAGRAM (text)
  - YOUTUBE (text)
  - GOOGLE_PROFILE (text)

Business Intelligence (5 new):
  - ANNUAL_REVENUE (number)
  - NUMBER_OF_EMPLOYEES (number)
  - YEAR_FOUNDED (number)
  - TOTAL_MONEY_RAISED (text)
  - IS_PUBLIC (boolean)

Google Reviews (3 new):
  - GOOGLE_REVIEWS_COUNT (number)
  - GBP_RATING (number)
  - GOOGLE_5_STARS (number)

Lead/Marketing (7 new):
  - LEAD_SOURCE (text)
  - LEAD_STATUS (text)
  - LEAD_TYPE (text)
  - LEAD_SCORE (number)
  - ORIGINAL_SOURCE (text)
  - TAGS (text)
  - LAST_ACTIVITY_DATE (date)

Email Quality (4 new):
  - EMAIL_VALIDATION (text)
  - NEVERBOUNCE_RESULT (text)
  - HARD_BOUNCE_REASON (text)
  - EMAIL_QUARANTINED (boolean)

System (5 new):
  - CURRENT_MARKETING_SUPPLIER (text)
  - BUSINESS_DESCRIPTION (text)
  - WAS_CALLED (boolean)
  - CALL_COUNT (number)
  - SOURCE_LIST (text)

JSON Metadata (4 new):
  - HUBSPOT_CONTACT_META (text) - All HubSpot internal fields
  - HUBSPOT_COMPANY_META (text) - All company tracking fields
  - SOCIAL_LINKS_JSON (text) - Backup of all social links
  - LOCATION_JSON (text) - Full address as JSON
```

### Script Required
`create_brevo_attributes.py` - Creates all 49 attributes via API

### Verification
- [ ] All 49 attributes created
- [ ] Correct types assigned (text, number, date, boolean)
- [ ] Total attributes = 72

---

## PHASE 1: Import Base Contacts

**Duration:** ~2 hours (rate limited)
**Risk:** Medium

### 1A: Import Master Contacts (34,796 with emails)

**Source:** `C:\Users\peter\Downloads\CC\CRM\Master_Contacts_With_Flags.csv`

**Fields to Import:**

| Source Field | Brevo Attribute | Notes |
|--------------|-----------------|-------|
| email | email | Required, primary key |
| first_name | FIRSTNAME | Only 2.5% have names |
| last_name | LASTNAME | |
| phone | SMS | Format: +61XXXXXXXXX |
| company | COMPANY | 76% have company |
| website | WEBSITE | |
| city | CITY | |
| state | STATE_REGION | |
| source_list | SOURCE_LIST | massive_list, etc. |
| was_called | WAS_CALLED | Boolean |
| call_count | CALL_COUNT | Number |

**List Assignment:**
```python
if was_called:
    lists = [24, 25, 29]  # All + Safe + Previously Called
else:
    lists = [24, 25]  # All + Safe (Fresh leads)
```

**Script:** `import_master_contacts.py`

### 1B: Import HubSpot Contacts (not in Master)

**Source:** `C:\Users\peter\Documents\HS\All_Contacts_2025_07_07_Cleaned.csv`

**Pre-filter:** Skip emails already imported from Master (~6,800 overlap)

**Additional Fields from HubSpot:**

| Source Field | Brevo Attribute |
|--------------|-----------------|
| First Name | FIRSTNAME |
| Last Name | LASTNAME |
| Phone Number 1 | SMS |
| Mobile Phone Number | PHONE_2 |
| Mobile Phone 2 | PHONE_3 |
| Company Name | COMPANY |
| Website URL | WEBSITE |
| Job Title | JOB_TITLE |
| City | CITY |
| Postal Code | POSTAL_CODE |
| State/Region | STATE_REGION |
| Street Address | STREET_ADDRESS |
| Country | COUNTRY |
| Email Validation | EMAIL_VALIDATION |
| NeverBounce Validation Result | NEVERBOUNCE_RESULT |
| Twitter Profile | TWITTER |
| Biz- Score ACTIVE | LEAD_SCORE |
| Biz- Lead Source | LEAD_SOURCE |
| Biz- lead Status | LEAD_STATUS |
| Biz- Lead Type | LEAD_TYPE |
| Biz- Tag | TAGS |
| Biz- Last Activity Date-Time | LAST_ACTIVITY_DATE |

**JSON Blob - HUBSPOT_CONTACT_META:**
```json
{
  "legacy_record_id": "...",
  "associated_company_ids": "...",
  "contact_owner": "...",
  "create_date_time": "...",
  "original_source": "...",
  "original_source_drill_down_1": "...",
  "original_source_drill_down_2": "...",
  "record_source": "...",
  "record_source_detail": "..."
}
```

**Script:** `import_hubspot_contacts.py`

### Verification After Phase 1
- [ ] ~35,000 contacts imported
- [ ] List 24 (All) count matches
- [ ] List 25 (Safe) count matches
- [ ] List 29 (Previously Called) has ~27,790 contacts
- [ ] Sample 10 contacts - verify fields populated

---

## PHASE 2: Enrich Existing Contacts

**Duration:** ~1 hour
**Risk:** Low (updates only, no new contacts)

### 2A: Enrich Master Contacts with HubSpot Data

For the ~6,800 contacts that exist in BOTH Master and HubSpot:
- Add missing names (Master has only 2.5% names)
- Add job titles
- Add location details
- Add lead scores and status

**Data Quality Rules:**
```python
# NEVER overwrite with empty values
if new_value and not existing_value:
    update(new_value)

# For names: longer name wins
if len(new_name) > len(existing_name):
    update(new_name)

# For phones: keep all unique (SMS, PHONE_2, PHONE_3)
# For WAS_CALLED: True wins (once called, always called)
# For dates: keep most recent
```

**Script:** `enrich_contacts_from_hubspot.py`

### Verification After Phase 2
- [ ] Sample enriched contacts have names populated
- [ ] No data was overwritten with empty values
- [ ] HUBSPOT_CONTACT_META populated for matched contacts

---

## PHASE 3: Create Companies (Appointment Companies Only)

**Duration:** 10 minutes
**Risk:** Low

### Companies to Create: 38 total (29 real business + 9 personal)

**Source:** `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv`

**Only create companies where:**
1. Company name exists and is not URL-like
2. Contact has valid business email OR is won/followup status

**Brevo Company Fields:**

| Source | Brevo Field |
|--------|-------------|
| company | name |
| email domain | domain |
| (from HubSpot) | industry |
| (from HubSpot) | phone_number |
| (from HubSpot) | number_of_employees |
| (from HubSpot) | revenue |

**Script:** `create_appointment_companies.py`

### HubSpot Company Enrichment

18 of 30 appointment companies found in HubSpot Companies with rich data:
- Phone numbers
- Industry classification
- Employee count
- Revenue
- Google reviews & ratings
- Business descriptions

**Script:** `enrich_companies_from_hubspot.py`

### Verification After Phase 3
- [ ] 38 companies created
- [ ] 18 have enriched data from HubSpot
- [ ] No URL-like or personal-email companies

---

## PHASE 4: Add Appointment Data

**Duration:** 5 minutes
**Risk:** Low

### Update 82 Appointment Contacts

**Source:** `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv`

**Fields to Add:**

| Source Field | Brevo Attribute |
|--------------|-----------------|
| date | APPOINTMENT_DATE |
| time | APPOINTMENT_TIME |
| status | APPOINTMENT_STATUS |
| status_category | DEAL_STAGE |
| quality | QUALITY |
| followup | FOLLOWUP_STATUS |
| source_sheet | SOURCE (append) |

**List Assignment:**
- Add to List 28 (Had Appointments)

**Script:** `add_appointment_data.py`

### Verification After Phase 4
- [ ] List 28 has 82 contacts
- [ ] All appointment fields populated
- [ ] DEAL_STAGE correctly mapped (Won, Followup, etc.)

---

## PHASE 5: Add Call Log Data (RETELL_LOG)

**Duration:** 30 minutes
**Risk:** Low

### Match Call Logs to Contacts

**Sources:**
- `C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json` (15,156 calls)
- `C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json` (6,844 calls)

**Matching Method:**
1. Phone number match (last 9 digits of to_number)
2. 22,000 calls → 19,470 unique phones

**RETELL_LOG Format:**
```
DD/MM/YYYY HH:MM DIRECTION (duration) - Recording: URL
DD/MM/YYYY HH:MM DIRECTION (duration) - Recording: URL
...
```

**Example:**
```
08/12/2025 19:54 OUTBOUND (2m 34s) - Recording: https://...
08/25/2025 16:45 INBOUND (1m 12s) - Recording: https://...
```

**Script:** `add_call_log_data.py`

### Verification After Phase 5
- [ ] Sample contacts with calls have RETELL_LOG populated
- [ ] Recording URLs are accessible
- [ ] Multiple calls show as multiple lines

---

## PHASE 6: Link Contacts to Companies

**Duration:** 5 minutes
**Risk:** Low

### Link 82 Appointment Contacts to Their Companies

**Process:**
1. Get contact ID by email
2. Get company ID by name
3. Call Brevo API to link

**Script:** `link_contacts_to_companies.py`

### Verification After Phase 6
- [ ] Companies show linked contacts in Brevo UI
- [ ] Contacts show company association

---

## PHASE 7: Final Verification

### Expected Final Counts

| Metric | Expected |
|--------|----------|
| Total Contacts | ~35,000 |
| List 24 (All Telemarketer) | ~35,000 |
| List 25 (Safe to Contact) | ~35,000 |
| List 28 (Had Appointments) | 82 |
| List 29 (Previously Called) | ~27,790 |
| Companies | 38 |
| Contacts with RETELL_LOG | ~19,000 |
| Contacts with names | ~8,000 (all appointments + HubSpot matches) |

### Quality Checks

```bash
# Check total contacts
python verify_import.py --check counts

# Check appointment contacts quality
python verify_import.py --check appointments

# Check call log coverage
python verify_import.py --check calls

# Check company links
python verify_import.py --check companies
```

---

## DATA QUALITY HIERARCHY

### Field Priority (Never Overwrite Better Data)

| Field | Priority 1 (Best) | Priority 2 | Priority 3 |
|-------|-------------------|------------|------------|
| FIRSTNAME, LASTNAME | Appointments | HubSpot Contacts | Master/Massive |
| COMPANY | Appointments | HubSpot Contacts | Master/Massive |
| SMS (Phone) | Call logs (dialed) | Appointments | HubSpot |
| JOB_TITLE | HubSpot Contacts | - | - |
| Location fields | HubSpot Contacts | HubSpot Companies | - |
| GOOGLE_REVIEWS_* | HubSpot Companies | - | - |
| LEAD_* fields | HubSpot Contacts | - | - |
| APPOINTMENT_* | Appointments only | - | - |
| RETELL_LOG | Call logs only | - | - |

### Merge Rules

1. **NEVER overwrite with empty/null values**
2. **Names:** Longer name wins ("John Smith" > "John")
3. **Phones:** Keep ALL unique (SMS, PHONE_2, PHONE_3)
4. **Dates:** Keep most recent activity date
5. **WAS_CALLED:** True wins (once called, always called)
6. **TAGS:** Concatenate from all sources, dedupe
7. **JSON blobs:** Merge objects, don't overwrite

---

## SCRIPTS TO CREATE

| Script | Purpose | Phase |
|--------|---------|-------|
| `create_brevo_attributes.py` | Create all 49 new attributes | 0 |
| `import_master_contacts.py` | Import 34,796 Master contacts | 1A |
| `import_hubspot_contacts.py` | Import ~172,000 HubSpot contacts | 1B |
| `enrich_contacts_from_hubspot.py` | Enrich overlapping contacts | 2 |
| `create_appointment_companies.py` | Create 38 companies | 3 |
| `enrich_companies_from_hubspot.py` | Add HubSpot company data | 3 |
| `add_appointment_data.py` | Add appointment fields to 82 contacts | 4 |
| `add_call_log_data.py` | Add RETELL_LOG to contacts | 5 |
| `link_contacts_to_companies.py` | Link contacts to companies | 6 |
| `verify_import.py` | Verification checks | 7 |

---

## ROLLBACK PLAN

If issues occur at any phase:

1. **Phase 0 (Attributes):** Delete attributes via Brevo UI
2. **Phase 1-6 (Data):** Run `delete_all_brevo_data.py` and restart
3. **Partial rollback:** Export contacts, fix issues, reimport

---

## ESTIMATED TIMELINE

| Phase | Duration | Cumulative |
|-------|----------|------------|
| 0: Create Attributes | 5 min | 5 min |
| 1A: Import Master | 1 hour | 1h 5m |
| 1B: Import HubSpot | 1 hour | 2h 5m |
| 2: Enrich Contacts | 30 min | 2h 35m |
| 3: Create Companies | 10 min | 2h 45m |
| 4: Add Appointments | 5 min | 2h 50m |
| 5: Add Call Logs | 30 min | 3h 20m |
| 6: Link Contacts | 5 min | 3h 25m |
| 7: Verification | 15 min | 3h 40m |

**Total estimated time:** ~4 hours

---

## NEXT STEPS

1. [ ] Review and approve this plan
2. [ ] Create all 10 scripts
3. [ ] Test Phase 0 (attributes)
4. [ ] Test Phase 1A with 100 contacts
5. [ ] If OK, proceed with full import
6. [ ] Test each subsequent phase
7. [ ] Final verification

---

## APPENDIX: JSON Blob Contents

### HUBSPOT_CONTACT_META
```json
{
  "legacy_record_id": "...",
  "associated_company_ids": "...",
  "contact_owner": "...",
  "created_by_user_id": "...",
  "create_date_time": "...",
  "last_activity_date_time": "...",
  "email_hard_bounce_reason": "...",
  "score_active": "...",
  "team": "...",
  "ip_country_code": "...",
  "original_source": "...",
  "original_source_drill_down_1": "...",
  "original_source_drill_down_2": "...",
  "record_source": "...",
  "record_source_detail": "...",
  "associated_sequence_ids": "...",
  "associated_task_ids": "...",
  "associated_email_ids": "..."
}
```

### HUBSPOT_COMPANY_META
```json
{
  "legacy_record_id": "...",
  "company_id": "...",
  "company_owner": "...",
  "hubspot_team": "...",
  "first_contact_create_date": "...",
  "last_activity_date": "...",
  "last_modified_date": "...",
  "latest_traffic_source": "...",
  "likelihood_to_close": "...",
  "merged_company_ids": "...",
  "original_source_type": "...",
  "overall_score": "...",
  "time_first_seen": "...",
  "updated_by_user_id": "..."
}
```
