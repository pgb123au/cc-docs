# Comprehensive Brevo Import Plan

**Created:** 2025-12-13
**Status:** READY FOR APPROVAL
**Approach:** Layer-by-layer import (contacts first, then enrich with appointments/calls)

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
