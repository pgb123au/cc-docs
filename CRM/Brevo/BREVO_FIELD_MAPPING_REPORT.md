# Brevo Field Mapping Report

**Generated:** 2025-12-13
**Purpose:** Map ALL available source data to Brevo CRM fields

---

## Source Files

| File | Path | Records | Purpose |
|------|------|---------|---------|
| HubSpot Companies | `C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` | ~363K | Company data with enrichment |
| Appointments Enriched | `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv` | Varies | Appointment/contact data |
| Call Log 1 | `C:\Users\peter\Downloads\CC\CRM\call_log_sheet_export.json` | Varies | RetellAI call records |
| Call Log 2 | `C:\Users\peter\Downloads\CC\CRM\call_log_sheet2_export.json` | Varies | RetellAI call records |

---

## HubSpot Companies File (63 columns)

| # | Source Column | Brevo Field | Status | Notes |
|---|---------------|-------------|--------|-------|
| 1 | Legacy Record ID | HUBSPOT_COMPANY_META | NOT MAPPED | Store for reference |
| 2 | Company ID | HUBSPOT_COMPANY_META | NOT MAPPED | Store for reference |
| 3 | Company name | Company.name | MAPPED | Primary identifier |
| 4 | Company Domain Name | Company.domain | MAPPED | Used for enrichment |
| 5 | Company Email | COMPANY_EMAIL | NOT MAPPED | Available in Brevo |
| 6 | Company Phone Number | Company.phone_number | MAPPED | May fail validation |
| 7 | Company Phone 2 | PHONE_2 | NOT MAPPED | Available in Brevo |
| 8 | Company Phone 3 | PHONE_3 | NOT MAPPED | Available in Brevo |
| 9 | State/Region | STATE_REGION | NOT MAPPED | Available in Brevo |
| 10 | Street Address 1 | STREET_ADDRESS | NOT MAPPED | Available in Brevo |
| 11 | Street Address 2 | STREET_ADDRESS | NOT MAPPED | Concatenate with #10 |
| 12 | Suburb | SUBURB | NOT MAPPED | Available in Brevo |
| 13 | City | Company.city / CITY | PARTIAL | Company only |
| 14 | Postal Code | POSTAL_CODE | NOT MAPPED | Available in Brevo |
| 15 | Country/Region | COUNTRY | NOT MAPPED | Available in Brevo |
| 16 | Country/Region Code | - | SKIP | Use #15 instead |
| 17 | Time Zone | CONTACT_TIMEZONE | NOT MAPPED | Available in Brevo |
| 18 | Create Date-Time | - | SKIP | Brevo tracks internally |
| 19 | Annual Revenue | ANNUAL_REVENUE | NOT MAPPED | Available in Brevo |
| 20 | Business type | BUSINESS_TYPE | NOT MAPPED | Available in Brevo |
| 21 | Vertical | VERTICAL | NOT MAPPED | Available in Brevo |
| 22 | Industry | Company.industry / INDUSTRY | PARTIAL | Company only |
| 23 | Year Founded | YEAR_FOUNDED | NOT MAPPED | Available in Brevo |
| 24 | Google profile link | GOOGLE_PROFILE | NOT MAPPED | Available in Brevo |
| 25 | Total Google reviews 2 | GOOGLE_REVIEWS_COUNT | NOT MAPPED | Available in Brevo |
| 26 | Total Google reviews | GOOGLE_REVIEWS_COUNT | NOT MAPPED | Use latest value |
| 27 | GBP rating | GBP_RATING | NOT MAPPED | Available in Brevo |
| 28 | Google # of 5-stars | GOOGLE_5_STARS | NOT MAPPED | Available in Brevo |
| 29 | Biz - Company owner | - | SKIP | Internal HubSpot |
| 30 | Current Online Marketing Supplier | CURRENT_MARKETING_SUPPLIER | NOT MAPPED | Available in Brevo |
| 31 | Business Description | BUSINESS_DESCRIPTION | NOT MAPPED | Available in Brevo |
| 32 | Facebook Company Page | FACEBOOK | NOT MAPPED | Available in Brevo |
| 33 | Twitter Handle | TWITTER | NOT MAPPED | Available in Brevo |
| 34 | LinkedIn Bio | - | SKIP | Use LinkedIn page |
| 35 | LinkedIn Company Page | LINKEDIN | NOT MAPPED | Available in Brevo |
| 36 | instagram page | INSTAGRAM | NOT MAPPED | Available in Brevo |
| 37 | Youtube handle | YOUTUBE | NOT MAPPED | Available in Brevo |
| 38-45 | Biz - * fields | - | SKIP | Internal HubSpot metadata |
| 46-57 | Biz - * fields | - | SKIP | Internal HubSpot metadata |
| 58 | Biz - Associated Contact IDs | HUBSPOT_CONTACT_META | **KEY FOR LINKING** | Match contacts to companies |
| 59 | Biz - Contact with Primary Company IDs | HUBSPOT_CONTACT_META | **KEY FOR LINKING** | Primary contact relationship |
| 60-62 | Biz - Associated * IDs | - | SKIP | Internal HubSpot refs |
| 63 | HubSpot_LongText_JSON | HUBSPOT_COMPANY_META | NOT MAPPED | Extended data |

---

## Appointments Enriched File (19 columns)

| # | Source Column | Brevo Field | Status | Notes |
|---|---------------|-------------|--------|-------|
| 1 | source_sheet | SOURCE | MAPPED | Combined with company_source |
| 2 | company | COMPANY | MAPPED | Text attribute on contact |
| 3 | name | FIRSTNAME, LASTNAME | MAPPED | Split on space |
| 4 | email | Contact.email | MAPPED | Primary identifier |
| 5 | phone | SMS | NOT MAPPED | Usually empty |
| 6 | date | APPOINTMENT_DATE | MAPPED | |
| 7 | time | APPOINTMENT_TIME | MAPPED | |
| 8 | status | APPOINTMENT_STATUS | MAPPED | |
| 9 | quality | QUALITY | MAPPED | |
| 10 | followup | FOLLOWUP_STATUS | MAPPED | |
| 11 | retell_log | RETELL_LOG | MAPPED | Simplified format |
| 12 | status_category | DEAL_STAGE | MAPPED | won/lost/followup |
| 13 | email_valid | EMAIL_VALID | PARTIAL | Not importing when empty |
| 14 | match_source | MATCH_SOURCE | PARTIAL | Not importing when empty |
| 15 | phone_from_list | SMS or PHONE_2 | MAPPED | Based on match_source reliability |
| 16 | was_called | WAS_CALLED | MAPPED | Boolean |
| 17 | company_from_list | - | NOT MAPPED | Could enhance company matching |
| 18 | website_from_list | WEBSITE | NOT MAPPED | Available in Brevo |
| 19 | location | Company.city | PARTIAL | Only if no HubSpot data |

---

## Call Log Files (25-35 columns)

| # | Source Column | Brevo Field | Status | Notes |
|---|---------------|-------------|--------|-------|
| 1 | row_number | - | SKIP | Internal |
| 2 | call_id | RETELL_LOG | PARTIAL | Could include in log |
| 3 | agent_id | - | SKIP | Internal |
| 4 | agent_version | - | SKIP | Internal |
| 5 | status | RETELL_LOG | PARTIAL | Include in log |
| 6 | start_time | RETELL_LOG | PARTIAL | Currently only date/time |
| 7 | end_time | - | SKIP | Derive duration |
| 8 | duration_ms | - | SKIP | Use human_duration |
| 9 | human_duration | RETELL_LOG | **MISSING** | Should include |
| 10 | formatted_transcript | - | SKIP | Too large |
| 11 | plain_transcript | - | SKIP | Too large |
| 12 | recording_url | RETELL_LOG | **MISSING** | Should include |
| 13 | public_log_url | - | SKIP | Internal |
| 14 | disconnection_reason | RETELL_LOG | **MISSING** | Useful for analysis |
| 15 | from_number | - | SKIP | Our number |
| 16 | to_number | - | Used for matching | Match to phone_from_list |
| 17 | caller_name | - | SKIP | May be inaccurate |
| 18 | direction | RETELL_LOG | **MISSING** | Should include |
| 19 | batch_call_id | - | SKIP | Internal |
| 20+ | cost/latency tables | - | SKIP | Internal analytics |

---

## Brevo Contact Attributes (Available but NOT USED)

These Brevo attributes exist but are NOT being populated:

| Attribute | Type | Potential Source | Priority |
|-----------|------|------------------|----------|
| COMPANY_DOMAIN | text | HubSpot Domain | HIGH |
| COMPANY_EMAIL | text | HubSpot Company Email | MEDIUM |
| COMPANY_PHONE | text | HubSpot Company Phone | MEDIUM |
| INDUSTRY | text | HubSpot Industry | HIGH |
| BUSINESS_TYPE | text | HubSpot Business type | MEDIUM |
| VERTICAL | text | HubSpot Vertical | MEDIUM |
| STREET_ADDRESS | text | HubSpot Street Address 1+2 | LOW |
| SUBURB | text | HubSpot Suburb | LOW |
| CITY | text | HubSpot City | MEDIUM |
| STATE_REGION | text | HubSpot State/Region | MEDIUM |
| POSTAL_CODE | text | HubSpot Postal Code | LOW |
| COUNTRY | text | HubSpot Country/Region | LOW |
| WEBSITE | text | Appointments website_from_list | MEDIUM |
| GOOGLE_PROFILE | text | HubSpot Google profile link | LOW |
| GOOGLE_REVIEWS_COUNT | float | HubSpot Total Google reviews | LOW |
| GBP_RATING | float | HubSpot GBP rating | LOW |
| ANNUAL_REVENUE | float | HubSpot Annual Revenue | LOW |
| NUMBER_OF_EMPLOYEES | float | HubSpot Number of Employees | LOW |
| YEAR_FOUNDED | float | HubSpot Year Founded | LOW |
| TWITTER | text | HubSpot Twitter Handle | LOW |
| FACEBOOK | text | HubSpot Facebook Page | LOW |
| LINKEDIN | text | HubSpot LinkedIn Page | LOW |
| INSTAGRAM | text | HubSpot instagram page | LOW |
| YOUTUBE | text | HubSpot Youtube handle | LOW |
| BUSINESS_DESCRIPTION | text | HubSpot Business Description | MEDIUM |
| CURRENT_MARKETING_SUPPLIER | text | HubSpot Current Marketing Supplier | LOW |
| HUBSPOT_COMPANY_META | text | HubSpot IDs (JSON) | HIGH |
| HUBSPOT_CONTACT_META | text | HubSpot Contact IDs (JSON) | HIGH |
| EMAIL_VALIDATION | text | Appointments email_valid | MEDIUM |
| CALL_COUNT | float | Count from call logs | MEDIUM |

---

## CRITICAL GAPS IDENTIFIED

### 1. RETELL_LOG is Incomplete
**Current:** `MM/DD/YYYY HH:MM phone_call`
**Should Include:**
- Direction (inbound/outbound)
- Duration (human_duration)
- Recording URL
- Disconnection reason

**Example Improved Format:**
```
25/08/2025 16:45 OUTBOUND (2m 34s) - Recording: https://...
```

### 2. HubSpot Enrichment Not Flowing to Contacts
When company found in HubSpot, contact should receive:
- COMPANY_DOMAIN
- INDUSTRY
- BUSINESS_TYPE
- Location fields

### 3. EMAIL_VALID Not Storing Boolean
Currently showing empty when source is `True` - should store as boolean.

### 4. MATCH_SOURCE Not Storing
Should store the match quality indicator from appointments.

### 5. HubSpot Matching Fields Not Used
`Biz - Associated Contact IDs` and `Biz - Contact with Primary Company IDs` could enable:
- Better company-contact linking
- Finding contacts that belong to same company

---

## RECOMMENDATIONS

### Phase 1: Fix Immediate Issues
1. Fix EMAIL_VALID boolean storage
2. Fix MATCH_SOURCE storage
3. Enhance RETELL_LOG format with full call data

### Phase 2: Add HubSpot Enrichment
1. When company matches HubSpot, copy to contact:
   - COMPANY_DOMAIN
   - INDUSTRY
   - STATE_REGION, CITY
   - Social links

### Phase 3: Use HubSpot Linking Fields
1. Store `Biz - Associated Contact IDs` in HUBSPOT_CONTACT_META
2. Use for finding related contacts
3. Enable better deduplication

### Phase 4: Full Data Import
1. Add all LOW priority fields
2. Enable comprehensive reporting
3. Support segmentation by industry/location/etc.

---

## Test Data Status (Current)

| Company | Linked | Domain | Industry | All Fields |
|---------|--------|--------|----------|------------|
| Reignite Health | YES | YES | YES | PARTIAL |
| Paradise Distributors | YES | NO | NO | PARTIAL |
| JTW Building Group | YES | NO | NO | PARTIAL |

**Contacts ARE linked to companies** (verified via API).

---

## Files to Update

1. `MARKETING/scripts/import_3_companies_v3.py` - Add missing field mappings
2. `MARKETING/scripts/brevo_audit_detailed.py` - Add checks for new fields
3. `MARKETING/IMPORT_PLAN_COMPREHENSIVE.md` - Update with new mappings
