# Mobile Numbers from Appointments Dataset

Generated: 2025-12-14
Total appointments: 87

## Summary
- Unique phone numbers found: 8
- Total phone entries: 14

- Unique companies: 38

## All Contacts with Phone Numbers and Call History

| Company | Contact | Phone | Source | Calls (provider:count) |
|---------|---------|-------|--------|------------------------|
| Finweb | Bipin Josie| +61402213582 | excel_list | retell:8, zadarma:10 |
| Brisbane City Landscapes | Jack Blair-Swanell| +61402213582 | excel_list | retell:8, zadarma:10 |
| Pinnacle Accounting Advis | Mina Baselyous| +61431413530 | excel_list | zadarma:1 |
| CLG Electrics | Chris| +61402140955 | excel_list | zadarma:1 |
| Western AC | Richard Sikorski| +61425757530 | excel_list | zadarma:1 |
| Paradise Distributors | Bob Chalmers| +61402213582 | excel_list | retell:8, zadarma:10 |
| Awash Care ? | ∙| +61402213582 | excel_list | retell:8, zadarma:10 |
| kiwi Golden care | | +61431587938 | excel_list | zadarma:2 |
| AJS Australia Disability  | Shirley| +61421189252 | excel_list | retell:2, zadarma:2 |
| Silver Fern Accounting | Cameron Gibson| +61402213582 | excel_list | retell:8, zadarma:10 |
| VVFX | Ricky| +61402213582 | excel_list | retell:8, zadarma:10 |
| Snappy Removals | Kevin| +61402213582 | excel_list | retell:8, zadarma:10 |
| Cool Solutions | Mal Stanes ?| +61404610402 | excel_list | zadarma:2 |
| No Show - CB 8/6/25 | Ian Kingston| +61418127174 | excel_list | retell:12, zadarma:15 |

## Raw Phone List (for bulk operations)

```
+61402140955
+61402213582
+61404610402
+61418127174
+61421189252
+61425757530
+61431413530
+61431587938
```

## Key Finding

The 5 original test companies (Reignite Health, Paradise Distributors, JTW Building,
Lumiere Home Renovations, CLG Electrics) were called via **Zadarma**, not Retell.
The retell_log field in appointments is misleadingly named - it logs ALL calls.

Some OTHER contacts in the appointments set have Retell calls:
- +61402213582: 8 Retell calls
- +61418127174: 12 Retell calls
- +61421189252: 2 Retell calls