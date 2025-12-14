# Brevo CRM Import - Project Status

**Last Updated:** 2025-12-14
**Current Import Version:** v8 (import_3_companies_v8.py)
**Status:** ALL DATA PERFECT - 5 test companies imported successfully

---

## Current State

### What's Working
- 5 test companies imported to Brevo with full data
- HubSpot company/contact enrichment working
- Telco Warehouse integration working (PostgreSQL)
- Retell transcript extraction working (v8)
- Audit passes with no errors

### Test Companies Imported
| Company | Contact | Source | Calls | Retell Transcripts |
|---------|---------|--------|-------|-------------------|
| Reignite Health | Sara Lehmann | HubSpot | 1 Zadarma | 0 |
| Paradise Distributors | Bob Chalmers | HubSpot | 1 Zadarma | 0 |
| JTW Building Group | Joe Van Stripe | Appointment | 1 Zadarma | 0 |
| Lumiere Home Renovations | Chantelle | HubSpot | 1 Zadarma | 0 |
| CLG Electrics | Chris | Appointment | 1 Zadarma | **1 Retell** |

### Key Discovery
The 5 test companies were called via **Zadarma** (not Retell). The `retell_log` field in appointments is misleadingly named - it logs ALL calls from any provider. Only Chris (CLG Electrics) has a Retell call in the database.

---

## Scripts & Versions

### Import Scripts (use latest)
| Script | Version | Purpose |
|--------|---------|---------|
| `import_3_companies_v8.py` | **LATEST** | Full import with Retell transcripts |
| `import_3_companies_v7.py` | Previous | Uses telco.contacts table |
| `import_3_companies_v6.py` | Older | First telco.calls integration |

### Other Scripts
| Script | Purpose |
|--------|---------|
| `brevo_audit_v4.py` | Comprehensive data audit |
| `delete_brevo_silent.py` | Delete all Brevo data (silent mode) |
| `brevo_api.py` | Brevo API client |

---

## Data Sources

### Files
| Source | Path | Records |
|--------|------|---------|
| HubSpot Companies | `C:\Users\peter\Documents\HS\All_Companies_2025-07-07_Cleaned_For_HubSpot.csv` | 363K |
| HubSpot Contacts | `C:\Users\peter\Documents\HS\All_Contacts_2025_07_07_Cleaned.csv` | 207K |
| Appointments | `C:\Users\peter\Downloads\CC\CRM\Appointments_Enriched.csv` | 87 |
| Excel (Phone Call data) | OneDrive - `AI Appointments Set 2025-copy2025-12-12.xlsx` | 39 phones |

### Telco Warehouse (PostgreSQL)
```
Host:     96.47.238.189
Port:     5432
Database: telco_warehouse
User:     telco_sync
Password: TelcoSync2024!
Schema:   telco
```

**Key Tables:**
- `telco.contacts` - Pre-aggregated stats per phone number
- `telco.calls` - Raw call data with transcripts (use for Retell data)
- `telco.providers` - Provider lookup (retell=3, zadarma=1, telnyx=2)

**Important:** Always use `telco.normalize_phone()` for lookups!

---

## V8 Import Features

### Retell Fields Added
| Brevo Attribute | Source |
|-----------------|--------|
| RETELL_CALL_ID | telco.calls.external_call_id |
| RETELL_TRANSCRIPT | telco.calls.transcript |
| RETELL_CALL_SUMMARY | telco.calls.raw_data->'call_analysis'->>'call_summary' |
| TELCO_SENTIMENT | telco.calls.raw_data->'call_analysis'->>'user_sentiment' |
| RETELL_CALL_DURATION | telco.calls.duration_seconds |
| RETELL_CALL_DIRECTION | telco.calls.direction |
| RETELL_CALL_TIME | telco.calls.started_at |
| RETELL_SUCCESSFUL | telco.calls.raw_data->'call_analysis'->>'call_successful' |
| RETELL_VOICEMAIL | telco.calls.raw_data->'call_analysis'->>'in_voicemail' |
| RETELL_DISCONNECT_REASON | telco.calls.raw_data->>'disconnection_reason' |

### Aggregated Stats (from telco.contacts)
| Brevo Attribute | Source |
|-----------------|--------|
| TELCO_TOTAL_CALLS | telco.contacts.total_calls |
| RETELL_CALL_COUNT | telco.contacts.retell_calls |
| ZADARMA_CALL_COUNT | telco.contacts.zadarma_calls |
| TELCO_PROVIDER | Comma-separated list of providers |
| TELCO_IS_DNC | telco.contacts.is_dnc |
| TELCO_DNC_REASON | telco.contacts.dnc_reason |
| TELCO_CONTACT_STATUS | telco.contacts.contact_status |
| TELCO_LEAD_SCORE | telco.contacts.lead_score |

---

## Quick Commands

### Run Full Import Process
```bash
# 1. Delete existing data
cd /c/Users/peter/Downloads/CC/CRM/Brevo/scripts && python delete_brevo_silent.py

# 2. Run import
python import_3_companies_v8.py

# 3. Verify
python brevo_audit_v4.py
```

### Use Slash Command
```
/brevo-import-fix
```

### Query Retell Calls Directly
```sql
SELECT
    c.external_call_id,
    c.to_number,
    c.started_at,
    c.duration_seconds,
    LEFT(c.transcript, 200) as transcript_preview,
    c.raw_data->'call_analysis'->>'call_summary' as summary,
    c.raw_data->'call_analysis'->>'user_sentiment' as sentiment
FROM telco.calls c
WHERE c.provider_id = 3
  AND c.transcript IS NOT NULL
ORDER BY c.started_at DESC
LIMIT 10;
```

---

## Next Steps (When Continuing)

1. **Expand to more contacts** - Currently only 5 test companies, ready for full import
2. **Add more Brevo fields** - See `brevo-import-fix.md` for fields NOT yet populated
3. **DNC handling** - `telco.contacts.is_dnc` and `dnc_reason` are captured but not enforced

---

## Related Documentation

| Doc | Purpose |
|-----|---------|
| `.claude/commands/brevo-import-fix.md` | Slash command with full process |
| `CRM/Brevo/BREVO_FIELD_MAPPING_REPORT.md` | All field mappings |
| `CRM/Brevo/IMPORT_PLAN_COMPREHENSIVE.md` | Full import strategy |
| `Telcos/TELCO_WAREHOUSE_CRM_HANDOFF.md` | Telco database reference |
| `CRM/APPOINTMENTS_MOBILE_NUMBERS.md` | All mobile numbers from appointments |

---

## Troubleshooting

### Telco DB Connection Flaky
The connection sometimes fails with "password authentication failed" - just retry. Add delay between attempts:
```python
for attempt in range(5):
    try:
        conn = psycopg2.connect(**TELCO_DB)
        break
    except:
        time.sleep(3)
```

### No Retell Calls Found
Check the phone number format - Retell uses `+61...` format. Always use `telco.normalize_phone()`:
```sql
SELECT * FROM telco.calls
WHERE telco.normalize_phone(to_number) = telco.normalize_phone('+61402140955')
  AND provider_id = 3;
```
