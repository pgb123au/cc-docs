# Brevo Import Fix Process

Iterative process to fix and verify Brevo CRM data imports until perfect.

## Prerequisites

- Brevo API credentials configured in `MARKETING/scripts/brevo_api.py`
- Source files available:
  - `C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` (HubSpot companies)
  - `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv` (appointments data)

## Process Steps

### Step 1: Audit Current Brevo Data

Run comprehensive audit to identify ALL errors and omissions:

```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts && python brevo_audit_detailed.py
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
cd /c/Users/peter/Downloads/CC/MARKETING/scripts && python delete_brevo_data.py
```

### Step 4: Update Import Script

Edit `import_3_companies_v3.py` based on errors found. Key rules:

**Company Matching:**
- EXACT name match only from HubSpot file
- If not in HubSpot, create from appointment data
- Never use domain as company name
- Phone validation: retry without phone if rejected

**Contact Attributes (ALL required):**
- FIRSTNAME, LASTNAME, COMPANY
- APPOINTMENT_DATE, APPOINTMENT_TIME, APPOINTMENT_STATUS
- DEAL_STAGE, QUALITY, FOLLOWUP_STATUS
- RETELL_LOG, WAS_CALLED, EMAIL_VALID
- MATCH_SOURCE (data quality tracking)
- SOURCE, IMPORT_BATCH (tracking)

**Phone Handling:**
- match_source='email' -> use as SMS (reliable)
- match_source='domain' -> use as PHONE_2 (less reliable)
- Handle SMS conflict: move to PHONE_2

### Step 5: Re-import Data

```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts && python import_3_companies_v3.py
```

### Step 6: Verify Data

Run audit again:

```bash
cd /c/Users/peter/Downloads/CC/MARKETING/scripts && python brevo_audit_detailed.py
```

**Expected result:** "STATUS: ALL DATA PERFECT!"

### Step 7: Iterate if Needed

If audit shows errors:
1. Document new error patterns
2. Update import script
3. Delete data
4. Re-import
5. Re-audit
6. Repeat until perfect

## Key Files

| File | Purpose |
|------|---------|
| `MARKETING/scripts/brevo_api.py` | Brevo API client |
| `MARKETING/scripts/brevo_audit_detailed.py` | Comprehensive audit |
| `MARKETING/scripts/import_3_companies_v4.py` | Import script (v4) |
| `MARKETING/scripts/brevo_audit_v4.py` | Comprehensive audit (v4) |
| `MARKETING/BREVO_FIELD_MAPPING_REPORT.md` | Field mapping report |
| `MARKETING/scripts/delete_brevo_data.py` | Data cleanup |
| `MARKETING/IMPORT_PLAN_COMPREHENSIVE.md` | Full import plan |

## V4 Fixes Applied

1. **EMAIL_VALIDATION** attribute - fixed name (was EMAIL_VALID)
2. **MATCH_SOURCE** attribute - now created and stores correctly
3. **HubSpot enrichment flows to contacts** - COMPANY_DOMAIN, INDUSTRY, BUSINESS_TYPE, etc.
4. **All HubSpot fields mapped** - social links, reviews, business description
5. **HUBSPOT_COMPANY_META** - stores legacy_id and contact_ids for linking
6. **WAS_CALLED** attribute - tracks if contact was called
7. **Phone reliability** - only use SMS for email matches, PHONE_2 for domain matches
8. **SOURCE_SHEET** tracking - tracks original data source
9. **EXACT matching only** - no partial or domain matching
10. **Phone validation fallback** - retry without phone if Brevo rejects

## Test Companies

For testing, use these 3 companies:
- **Reignite Health** - in HubSpot (has domain, industry)
- **Paradise Distributors** - not in HubSpot (Bob Chalmers, was_called=True)
- **JTW Building Group** - not in HubSpot (Joe Van Stripe)

## Success Criteria

Audit must show:
- 3 companies created with correct attributes
- 3 contacts linked to their companies
- All contact fields populated correctly
- No errors or warnings
- "STATUS: ALL DATA PERFECT!"
