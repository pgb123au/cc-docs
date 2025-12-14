# Telco Warehouse - Session Status

**Last Updated:** 2025-12-14

---

## What Was Done This Session

### 1. Bug Discovered: 26K+ Retell Calls Missing Phone Numbers

**Problem:** The database has 26,327 Retell calls with `from_number = NULL` and `to_number = NULL`, but they DO have transcripts.

**Root Cause:**
- Calls were synced from the **Telco DB Sync** Retell workspace (Yes AI outbound campaign)
- At sync time, either the Retell API didn't return phone numbers OR the sync script didn't extract them
- These calls are stored separately from Zadarma calls (which have phones but no transcripts)

**Evidence:**
```
Both NULL phones: 26,329 calls, 25,706 with transcripts, avg 34.7s duration
Both populated:   11,388 calls, 583 with transcripts, avg 6.6s duration
```

### 2. Fixed: 34 Appointment Contact Calls

**Solution:** Queried Retell API directly using the correct workspace API key and updated the database.

| Phone | Company | Calls Updated |
|-------|---------|---------------|
| +61402140955 | CLG Electrics | 1 |
| +61402213582 | Finweb, Brisbane City Landscapes | 10 |
| +61404610402 | Cool Solutions | 2 |
| +61418127174 | No Show - Ian Kingston | 15 |
| +61421189252 | AJS Australia Disability | 2 |
| +61425757530 | Western AC | 1 |
| +61431413530 | Pinnacle Accounting | 1 |
| +61431587938 | Kiwi Golden Care | 2 |
| **TOTAL** | | **34** |

These calls now have:
- ✅ `from_number` populated
- ✅ `to_number` populated
- ✅ Full transcript (not truncated)
- ✅ `raw_data` with full Retell response (call_analysis, sentiment, summary, etc.)

---

## Pending Work

### Backfill Remaining 26K+ Calls

The 26,327 calls with NULL phone numbers still need to be backfilled from Retell API.

**Script ready:** `C:\Users\peter\Downloads\CC\Telcos\analysis\fetch_retell_appointments.py`

To backfill ALL calls (not just appointments), modify the script to:
1. Query all calls from Retell API (paginate through all)
2. Match by `external_call_id`
3. Update `from_number`, `to_number`, and `transcript`

**API Key for Telco DB Sync workspace:** `key_b8d6bd5512827f71f1f1202e06a4`

---

## Key Files

| File | Purpose |
|------|---------|
| `Telcos/RETELL_API_KEYS.md` | **NEW** - API keys for both Retell workspaces |
| `Telcos/TELCO_WAREHOUSE_CRM_HANDOFF.md` | CRM integration docs (updated with appointment query) |
| `Telcos/analysis/fetch_retell_appointments.py` | Script that fetched the 34 appointment calls |
| `Telcos/analysis/find_one_call.py` | Debug script to find specific call |
| `Telcos/analysis/link_retell_zadarma.py` | Links Retell transcripts to Zadarma phones by timestamp |

---

## API Keys Reference

| Workspace | API Key | Use For |
|-----------|---------|---------|
| **Telco DB Sync** | `key_b8d6bd5512827f71f1f1202e06a4` | May 2025+ outbound campaign (26K+ calls) |
| **Primary (Reignite)** | `C:\Users\peter\Downloads\Retell_API_Key.txt` | Oct 2025+ production calls |

---

## Database Connection

```python
import psycopg2
conn = psycopg2.connect(
    host='96.47.238.189',
    port=5432,
    database='telco_warehouse',
    user='telco_sync',
    password='TelcoSync2024!'
)
```

---

## Quick Verification Queries

```sql
-- Check appointment calls are now populated
SELECT to_number, COUNT(*),
       COUNT(CASE WHEN transcript IS NOT NULL THEN 1 END) as with_transcript
FROM telco.calls
WHERE to_number LIKE '+614%'
  AND provider_id = 3
GROUP BY to_number
ORDER BY COUNT(*) DESC
LIMIT 10;

-- Check NULL phone situation
SELECT
    CASE WHEN from_number IS NULL THEN 'NULL' ELSE 'Populated' END as phone_status,
    COUNT(*) as calls,
    COUNT(CASE WHEN transcript IS NOT NULL THEN 1 END) as with_transcript
FROM telco.calls
WHERE provider_id = 3
GROUP BY 1;
```

---

## Next Steps

1. **Backfill all 26K calls** - Modify `fetch_retell_appointments.py` to paginate through all Retell calls and update the database
2. **Run transcript analysis** - Once phones are backfilled, run classification on the 26K transcripts
3. **Update contacts table** - Re-aggregate stats after backfill
