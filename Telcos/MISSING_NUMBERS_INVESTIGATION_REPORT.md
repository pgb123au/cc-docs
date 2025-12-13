# Missing Phone Numbers Investigation Report

**Date:** 2024-12-14
**Database:** telco_warehouse (96.47.238.189:5432)
**Investigation:** Why 5 phone numbers could not be found in CRM lookup

---

## SUMMARY OF FINDINGS

**CRITICAL DISCOVERY:** All 5 phone numbers **DO EXIST** in the telco_warehouse database, but they are:

1. **Stored WITHOUT the leading `+` sign** (normalized as `61XXXXXXXXX`)
2. **Associated with Zadarma (provider_id = 1), NOT RetellAI (provider_id = 3)**
3. **Present in BOTH `telco.calls` and `telco.contacts` tables**

The CRM search likely failed because:
- It was searching for the exact format with `+` prefix
- It may have been filtering for RetellAI calls only (provider_id = 3)
- The normalization function strips `+` but the search patterns may not have accounted for this

---

## DETAILED FINDINGS BY NUMBER

### 1. Sara Lehmann - Reignite Health
**Phone:** +61437160997

**Database Records:**
- **Normalized phone:** `61437160997` (no `+` prefix)
- **Contact ID:** 21831
- **Contact type:** customer
- **Total calls:** 1 (all Zadarma, 0 RetellAI)
- **Call record:** ID 1628737
  - Direction: Outbound (from 61399997398 -> 61437160997)
  - Provider: 1 (Zadarma)
  - Call date: 2025-09-01 11:48:36+10

**Status:** ✅ EXISTS IN DATABASE (Zadarma call)

---

### 2. Bob Chalmers - Paradise Distributors
**Phone:** +61408687109

**Database Records:**
- **Normalized phone:** `61408687109` (no `+` prefix)
- **Contact ID:** 5472
- **Contact type:** customer
- **Total calls:** 1 (all Zadarma, 0 RetellAI)
- **Call record:** ID 1627205
  - Direction: Outbound (from 61399997398 -> 61408687109)
  - Provider: 1 (Zadarma)
  - Call date: 2025-08-25 16:45:37+10

**Status:** ✅ EXISTS IN DATABASE (Zadarma call)

---

### 3. Joe Van Stripe - JTW Building Group
**Phone:** +61424023677

**Database Records:**
- **Normalized phone:** `61424023677` (no `+` prefix)
- **Contact ID:** 17250
- **Contact type:** customer
- **Total calls:** 1 (all Zadarma, 0 RetellAI)
- **Call record:** ID 1615921
  - Direction: Outbound (from 61399997398 -> 61424023677)
  - Provider: 1 (Zadarma)
  - Call date: 2025-07-16 13:34:38+10

**Status:** ✅ EXISTS IN DATABASE (Zadarma call)

---

### 4. Chantelle - Lumiere Home Renovations
**Phone:** +61423238679

**Database Records:**
- **Normalized phone:** `61423238679` (no `+` prefix)
- **Contact ID:** 16813
- **Contact type:** customer
- **Total calls:** 1 (all Zadarma, 0 RetellAI)
- **Call record:** ID 1625412
  - Direction: Outbound (from 61399997398 -> 61423238679)
  - Provider: 1 (Zadarma)
  - Call date: 2025-08-15 10:52:33+10

**Status:** ✅ EXISTS IN DATABASE (Zadarma call)

---

### 5. Chris - CLG Electrics
**Phone:** +61402140955

**Database Records:**
- **Normalized phone:** `61402140955` (no `+` prefix)
- **Contact ID:** 1502
- **Contact type:** customer
- **Total calls:** 1 (all Zadarma, 0 RetellAI)
- **Call record:** ID 1622362
  - Direction: Outbound (from 61399997398 -> 61402140955)
  - Provider: 1 (Zadarma)
  - Call date: 2025-08-04 17:52:38+10

**Status:** ✅ EXISTS IN DATABASE (Zadarma call)

---

## NORMALIZATION FUNCTION BEHAVIOR

The `telco.normalize_phone()` function behaves as follows:

| Input Format | Normalized Output |
|--------------|-------------------|
| `+61437160997` | `61437160997` |
| `+61408687109` | `61408687109` |
| `+61424023677` | `61424023677` |
| `+61423238679` | `61423238679` |
| `+61402140955` | `61402140955` |

**Pattern:** Strips the leading `+` and stores as plain numeric string starting with country code.

---

## DATABASE SEARCH PATTERNS THAT WORK

All 5 numbers were successfully found using these patterns:

✅ **Pattern 1:** Exact match without `+`
```sql
WHERE phone_normalized = '61437160997'
```

✅ **Pattern 2:** LIKE with last 9 digits
```sql
WHERE phone_normalized LIKE '%437160997'
```

✅ **Pattern 3:** LIKE with full number (no +)
```sql
WHERE phone_normalized LIKE '%61437160997%'
```

---

## SEARCH PATTERNS THAT FAILED

❌ **Pattern 1:** Exact match WITH `+`
```sql
WHERE phone_normalized = '+61437160997'
```
**Reason:** Database stores without `+`

❌ **Pattern 2:** Filtering for RetellAI only
```sql
WHERE provider_id = 3 AND phone_normalized LIKE '%437160997'
```
**Reason:** All 5 contacts have ONLY Zadarma calls (provider_id = 1), zero RetellAI calls

---

## PROVIDER DISTRIBUTION

| Provider | Provider ID | Sample Numbers in DB |
|----------|-------------|----------------------|
| **Zadarma** | 1 | All 5 missing numbers |
| **Telnyx** | 2 | (not checked) |
| **RetellAI** | 3 | +61399997398, +61240620999, etc. |

**Key observation:** RetellAI numbers in the database **DO include the `+` prefix**, but Zadarma numbers are stored **WITHOUT the `+` prefix**.

Sample RetellAI numbers found:
- `+61399997398`
- `+61240620999`
- `+61288800226`

Sample Zadarma numbers (the 5 "missing"):
- `61437160997`
- `61408687109`
- `61424023677`
- `61423238679`
- `61402140955`

---

## ROOT CAUSE ANALYSIS

### Why the CRM Lookup Failed

The CRM search patterns used:
1. `%437160997` - Last 9 digits with wildcard
2. `%+61437160997%` - Full number with `+` and wildcards
3. `%61437160997%` - Full number without `+` and wildcards

**Pattern #3 SHOULD have worked** if:
- The database field being searched is `phone_normalized` (not `phone_display`)
- No provider_id filter was applied
- The SQL syntax was correct

### Likely Issues

1. **Provider filtering:** CRM may have been searching only RetellAI calls
2. **Column selection:** CRM may have searched `phone_display` instead of `phone_normalized`
3. **Case sensitivity:** Some SQL dialects are case-sensitive (unlikely in PostgreSQL)
4. **Transaction state:** If running in a transaction that was rolled back

---

## RECOMMENDATIONS

### For CRM Search Logic

1. **Always normalize input before searching:**
   ```python
   normalized = phone.lstrip('+')  # Remove leading +
   ```

2. **Search pattern should be:**
   ```sql
   WHERE phone_normalized = normalize_phone(:input)
   OR phone_normalized LIKE CONCAT('%', normalize_phone(:input))
   OR phone_normalized LIKE CONCAT('%', SUBSTRING(normalize_phone(:input), -9))
   ```

3. **Don't filter by provider unless specifically needed:**
   - Customer may have called via Zadarma before RetellAI was implemented
   - Historical data matters

4. **Check both columns:**
   ```sql
   WHERE phone_normalized LIKE pattern
      OR phone_display LIKE pattern
   ```

### For Data Consistency

1. **Standardize phone format across providers:**
   - Either all with `+` or all without
   - Currently RetellAI uses `+`, Zadarma doesn't

2. **Update normalization function to ensure consistency:**
   ```sql
   CREATE OR REPLACE FUNCTION telco.normalize_phone(input TEXT)
   RETURNS TEXT AS $$
   BEGIN
     RETURN regexp_replace(input, '[^0-9]', '', 'g');
   END;
   $$ LANGUAGE plpgsql IMMUTABLE;
   ```

3. **Consider adding indexed computed column:**
   ```sql
   ALTER TABLE telco.contacts
   ADD COLUMN phone_search TEXT GENERATED ALWAYS AS
     (regexp_replace(phone_normalized, '[^0-9]', '', 'g')) STORED;
   CREATE INDEX idx_contacts_phone_search ON telco.contacts(phone_search);
   ```

---

## TEST QUERIES

### Find all contacts with partial number match
```sql
SELECT contact_id, phone_normalized, phone_display,
       total_calls, retell_calls, zadarma_calls
FROM telco.contacts
WHERE phone_normalized LIKE '%437160997'
   OR phone_display LIKE '%437160997';
```

### Find all calls (any provider) for a number
```sql
SELECT id, from_number, to_number, provider_id, started_at
FROM telco.calls
WHERE from_number LIKE '%437160997'
   OR to_number LIKE '%437160997'
ORDER BY started_at DESC;
```

### Universal search function (proposed)
```sql
CREATE OR REPLACE FUNCTION telco.search_phone(input_phone TEXT)
RETURNS TABLE (
  contact_id INT,
  phone_normalized VARCHAR,
  phone_display VARCHAR,
  total_calls INT,
  retell_calls INT,
  zadarma_calls INT
) AS $$
DECLARE
  clean_phone TEXT;
  last_9 TEXT;
BEGIN
  -- Remove all non-digits
  clean_phone := regexp_replace(input_phone, '[^0-9]', '', 'g');
  -- Get last 9 digits
  last_9 := RIGHT(clean_phone, 9);

  RETURN QUERY
  SELECT c.contact_id, c.phone_normalized, c.phone_display,
         c.total_calls, c.retell_calls, c.zadarma_calls
  FROM telco.contacts c
  WHERE regexp_replace(c.phone_normalized, '[^0-9]', '', 'g') = clean_phone
     OR regexp_replace(c.phone_normalized, '[^0-9]', '', 'g') LIKE '%' || last_9
     OR regexp_replace(c.phone_display, '[^0-9]', '', 'g') = clean_phone
     OR regexp_replace(c.phone_display, '[^0-9]', '', 'g') LIKE '%' || last_9;
END;
$$ LANGUAGE plpgsql;
```

---

## CONCLUSION

**The numbers are NOT missing from the database.** They exist in both `telco.calls` and `telco.contacts` tables as Zadarma call records. The CRM lookup failure is due to:

1. **Format mismatch:** Searching for `+61...` when database has `61...`
2. **Provider filtering:** Possibly filtering for RetellAI-only calls
3. **Incorrect search column:** Possible use of wrong field

**Immediate fix:** Update CRM search logic to:
- Strip `+` from input before searching
- Search `phone_normalized` field
- Don't filter by provider unless specifically needed
- Use LIKE with wildcards: `LIKE '%' || normalized_input || '%'`

**Long-term fix:** Standardize phone number storage format across all providers.
