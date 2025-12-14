# Brevo Import Fix Process

Iterative process to fix and verify Brevo CRM data imports until perfect.

## Prerequisites

- Brevo API credentials configured in `CRM/Brevo/scripts/brevo_api.py`
- Source files available:
  - `C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` (HubSpot companies - 363K records, 63 columns)
  - `C:\Users\peter\Documents\HS\All_Contacts_2025_07_07_Cleaned.csv` (HubSpot contacts - 207K records)
  - `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv` (appointments data - 19 columns)
  - `C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json` (Retell call logs)
  - `C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json` (Retell call logs 2)
  - **Telco Warehouse PostgreSQL** (74K calls - Retell + Zadarma + Telnyx) - See `Telcos/TELCO_WAREHOUSE_CRM_HANDOFF.md`

## IMPORTANT: Always Use Latest Versions

Before starting, find the latest version numbers:

```bash
# Find latest import script version
ls -la /c/Users/peter/Downloads/CC/CRM/Brevo/scripts/import_3_companies_v*.py | tail -1

# Find latest audit script version
ls -la /c/Users/peter/Downloads/CC/CRM/Brevo/scripts/brevo_audit*.py | tail -1
```

**Current latest:** `import_3_companies_v8.py`, `brevo_audit_v4.py`

---

## Process Steps

### Step 1: Audit Current Brevo Data

Run the **LATEST** version of the audit script:

```bash
cd /c/Users/peter/Downloads/CC/CRM/Brevo/scripts && python brevo_audit_v4.py
```

Review output for:
- Companies: domain, industry, phone, city, linked contacts
- Contacts: all required attributes populated
- Error list at bottom

### Step 2: Analyze Errors

Common error patterns to check:

| Error Type | Cause | Fix |
|------------|-------|-----|
| Domain used as company name | Partial/domain matching | Use EXACT company name matching only |
| Wrong company linked | Loose matching | Match by exact company name only |
| Missing fields | Not imported | Add fields to import script |
| Phone validation failed | Invalid format | Retry without phone, log warning |
| SMS conflict | Duplicate phone | Move to PHONE_2 attribute |

### Step 3: Delete Existing Data

If errors found, delete ALL test data in Brevo:

```bash
cd /c/Users/peter/Downloads/CC/CRM/Brevo/scripts && python delete_brevo_silent.py
```

### Step 4: Update Import Script

**IMPORTANT: Create a NEW version file with incremented version number.**

1. Copy the latest version: `import_3_companies_v7.py` -> `import_3_companies_v8.py`
2. Update the version in filename AND `IMPORT_BATCH` constant
3. Apply fixes based on errors found

**Company Matching:**
- EXACT name match only from HubSpot file
- If not in HubSpot, create from appointment data
- Never use domain as company name
- Phone validation: retry without phone if rejected

**Contact Attributes (ALL required):**
- FIRSTNAME, LASTNAME, COMPANY
- APPOINTMENT_DATE, APPOINTMENT_TIME, APPOINTMENT_STATUS
- DEAL_STAGE, QUALITY, FOLLOWUP_STATUS
- RETELL_LOG, WAS_CALLED, EMAIL_VALIDATION
- MATCH_SOURCE (data quality tracking)
- SOURCE, IMPORT_BATCH (tracking)

**Phone Handling:**
- match_source='email' -> use as SMS (reliable)
- match_source='domain' -> use as PHONE_2 (less reliable)
- Handle SMS conflict: move to PHONE_2

**Telco Warehouse (v7+):**
- Use `telco.contacts` table with pre-aggregated stats
- Use `telco.normalize_phone()` for proper matching
- Query ALL phones: Excel, Appointment, AND Company phone

### Step 5: Re-import Data

Run the **LATEST** version of the import script:

```bash
cd /c/Users/peter/Downloads/CC/CRM/Brevo/scripts && python import_3_companies_v8.py
```

### Step 6: Verify Data

Run audit again with **LATEST** version:

```bash
cd /c/Users/peter/Downloads/CC/CRM/Brevo/scripts && python brevo_audit_v4.py
```

**Expected result:** "STATUS: ALL DATA PERFECT!"

### Step 7: Iterate if Needed

If audit shows errors:
1. Document new error patterns
2. **Increment version number** and create new import script
3. Delete data
4. Re-import with new version
5. Re-audit
6. Repeat until perfect

---

## Field Mapping Completeness

**RULE: All Brevo fields should be populated IF we have appropriate source data available.**

### Brevo Fields NOT Currently Populated

These Brevo attributes exist but are NOT being used (should be added):

| Attribute | Source Available | Priority |
|-----------|------------------|----------|
| ANNUAL_REVENUE | HubSpot `Annual Revenue` | LOW |
| VERTICAL | HubSpot `Vertical` | LOW |
| GOOGLE_PROFILE | HubSpot `Google profile link` | LOW |
| GOOGLE_5_STARS | HubSpot `Google # of 5-stars` | LOW |
| CURRENT_MARKETING_SUPPLIER | HubSpot `Current Online Marketing Supplier` | LOW |
| INSTAGRAM | HubSpot `instagram page` | LOW |
| YOUTUBE | HubSpot `Youtube handle` | LOW |
| CONTACT_TIMEZONE | HubSpot `Time Zone` | LOW |
| RETELL_CALL_ID | Telco Warehouse `external_call_id` | MEDIUM |
| RETELL_RECORDING_URL | Telco Warehouse `recording_url` | MEDIUM |
| RETELL_TRANSCRIPT | Telco Warehouse `transcript` | LOW (large) |
| RETELL_CALL_DIRECTION | Telco Warehouse `direction` | MEDIUM |
| RETELL_CALL_DURATION | Telco Warehouse `duration_seconds` | MEDIUM |
| RETELL_CALL_STATUS | Telco Warehouse `status` | LOW |
| RETELL_DISCONNECT_REASON | Telco Warehouse `hangup_cause` | LOW |
| TELCO_SENTIMENT | Telco Warehouse `sentiment` | MEDIUM |
| TELCO_IS_DNC | Telco `contacts.is_dnc` | HIGH |
| TELCO_DNC_REASON | Telco `contacts.dnc_reason` | HIGH |
| TELCO_CONTACT_STATUS | Telco `contacts.contact_status` | MEDIUM |
| TELCO_LEAD_SCORE | Telco `contacts.lead_score` | MEDIUM |

### Source Data Fields NOT in Brevo

These source fields exist but have NO Brevo attribute:

**HubSpot Companies (`All_Companies_2025-07-07_Cleaned_For_HubSpot.csv`):**
| Column | Notes |
|--------|-------|
| Company Phone 2, Company Phone 3 | Could map to PHONE_2, PHONE_3 |
| LinkedIn Bio | Redundant with LinkedIn Page |
| Biz - Company owner | Internal HubSpot metadata |
| Biz - Last Modified Date | Could track for sync freshness |
| Biz - First Contact Create Date | Could track original create date |
| Biz - Record source | Track where company came from |
| HubSpot_LongText_JSON | Extended data blob |

**HubSpot Contacts (`All_Contacts_2025_07_07_Cleaned.csv`):**
| Column | Notes |
|--------|-------|
| Job Title | Could map to JOBTITLE |
| Biz- Lead Source | Could map to LEAD_SOURCE |
| Biz- lead Status | Could map to LEAD_STATUS |
| Mobile Phone Number | Could use for SMS if more reliable |

**Appointments Enriched (`Appointments_Enriched.csv`):**
| Column | Notes |
|--------|-------|
| company_from_list | Could enhance company matching |
| website_from_list | Could map to WEBSITE |
| location | Only used as fallback for CITY |

**Telco Warehouse (PostgreSQL `telco.contacts`):**
| Column | Notes |
|--------|-------|
| notes | CRM notes field |
| tags | Array of tags |
| hostile_interactions | Count of hostile calls |
| total_sms | SMS count |
| sms_sent | Outbound SMS count |

---

## Key Files

| File | Purpose |
|------|---------|
| `CRM/Brevo/scripts/brevo_api.py` | Brevo API client |
| `CRM/Brevo/scripts/brevo_audit_v4.py` | Comprehensive audit (latest) |
| `CRM/Brevo/scripts/import_3_companies_v8.py` | Import script (latest) |
| `CRM/Brevo/scripts/delete_brevo_silent.py` | Data cleanup (silent mode) |
| `CRM/Brevo/BREVO_FIELD_MAPPING_REPORT.md` | Field mapping report |
| `CRM/Brevo/IMPORT_PLAN_COMPREHENSIVE.md` | Full import plan |
| `Telcos/TELCO_WAREHOUSE_CRM_HANDOFF.md` | Telco database reference |

---

## Version History

| Version | Key Changes |
|---------|-------------|
| v4 | EMAIL_VALIDATION fix, MATCH_SOURCE, HubSpot enrichment |
| v5 | Excel phone extraction, improved call logs |
| v6 | Telco Warehouse PostgreSQL (telco.calls) |
| v7 | Uses telco.contacts table with normalize_phone() |
| v8 | Retell transcripts from telco.calls (RETELL_CALL_ID, RETELL_TRANSCRIPT, TELCO_SENTIMENT) |

---

## Test Companies

For testing, use these 5 companies:
- **Reignite Health** - in HubSpot (has domain, industry, company phone with calls)
- **Paradise Distributors** - in HubSpot (Bob Chalmers, was_called=True)
- **JTW Building Group** - not in HubSpot (Joe Van Stripe)
- **Lumiere Home Renovations** - in HubSpot (HubSpot contact too)
- **CLG Electrics** - not in HubSpot (HubSpot contact only)

---

## Success Criteria

Audit must show:
- 5 companies created with correct attributes
- 5 contacts linked to their companies
- All contact fields populated correctly (where source data exists)
- Telco call data for all contacts with phone numbers
- No errors or warnings
- "STATUS: ALL DATA PERFECT!"
