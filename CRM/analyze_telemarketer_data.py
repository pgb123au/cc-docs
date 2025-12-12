"""Analyze telemarketer dialer data files."""
import csv
import json
from collections import Counter

MASSIVE_LIST = r'C:\Users\peter\retell-dialer\massive_list.csv'
VIC_LIST = r'C:\Users\peter\retell-dialer\massive_list_vic.csv'
CALLED_LOG = r'C:\Users\peter\retell-dialer\called_log.txt'
CALLED_JSON = r'C:\Users\peter\retell-dialer\called_numbers.json'


def analyze_massive_list(filepath, name):
    print(f"\n{'='*60}")
    print(f"ANALYSIS: {name}")
    print(f"{'='*60}")

    stats = {
        'total': 0,
        'has_email': 0,
        'has_mobile': 0,
        'has_first_name': 0,
        'has_last_name': 0,
        'has_company': 0,
        'has_website': 0,
    }
    mobile_numbers = set()

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats['total'] += 1

            if row.get('Email', '').strip() and '@' in row.get('Email', ''):
                stats['has_email'] += 1

            mobile = row.get('Mobile Phone Number', '').strip()
            phone_raw = row.get('phone_number', '').strip()
            if mobile or phone_raw:
                stats['has_mobile'] += 1
                # Normalize to set
                if phone_raw and phone_raw.isdigit():
                    mobile_numbers.add(phone_raw)

            if row.get('First Name', '').strip():
                stats['has_first_name'] += 1

            if row.get('Last Name', '').strip():
                stats['has_last_name'] += 1

            if row.get('Company Name', '').strip():
                stats['has_company'] += 1

            if row.get('Website URL', '').strip():
                stats['has_website'] += 1

    print(f"\nTotal Records: {stats['total']:,}")
    print(f"\n--- COVERAGE ---")
    pct = lambda x: f"{x:,} ({x/stats['total']*100:.1f}%)"
    print(f"Has Email:      {pct(stats['has_email'])}")
    print(f"Has Mobile:     {pct(stats['has_mobile'])}")
    print(f"Has First Name: {pct(stats['has_first_name'])}")
    print(f"Has Last Name:  {pct(stats['has_last_name'])}")
    print(f"Has Company:    {pct(stats['has_company'])}")
    print(f"Has Website:    {pct(stats['has_website'])}")

    return stats, mobile_numbers


def analyze_called():
    print(f"\n{'='*60}")
    print("CALL LOG ANALYSIS")
    print(f"{'='*60}")

    # Called log (plain text)
    called_txt = set()
    with open(CALLED_LOG, 'r') as f:
        for line in f:
            num = line.strip()
            if num:
                called_txt.add(num)

    print(f"\ncalled_log.txt: {len(called_txt):,} unique numbers")

    # Called JSON
    with open(CALLED_JSON, 'r') as f:
        called_json = json.load(f)

    # Normalize (remove +)
    called_json_normalized = set()
    for num in called_json:
        normalized = num.replace('+', '')
        called_json_normalized.add(normalized)

    print(f"called_numbers.json: {len(called_json_normalized):,} unique numbers")

    overlap = called_txt & called_json_normalized
    print(f"Overlap: {len(overlap):,}")

    return called_txt, called_json_normalized


def main():
    # Analyze lists
    stats1, mobiles1 = analyze_massive_list(MASSIVE_LIST, "massive_list.csv (All Australia)")
    stats2, mobiles2 = analyze_massive_list(VIC_LIST, "massive_list_vic.csv (VIC Only)")

    # Analyze call logs
    called_txt, called_json = analyze_called()

    # Cross-reference
    print(f"\n{'='*60}")
    print("CROSS-REFERENCE")
    print(f"{'='*60}")

    already_called_all = mobiles1 & called_txt
    already_called_vic = mobiles2 & called_txt

    print(f"\nFrom massive_list.csv already called: {len(already_called_all):,}")
    print(f"From massive_list_vic.csv already called: {len(already_called_vic):,}")

    not_called_all = mobiles1 - called_txt
    not_called_vic = mobiles2 - called_txt

    print(f"\nNOT YET CALLED (massive_list): {len(not_called_all):,}")
    print(f"NOT YET CALLED (vic_list): {len(not_called_vic):,}")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"""
TELEMARKETER DATA INVENTORY:
- massive_list.csv: {stats1['total']:,} records (all Australia)
- massive_list_vic.csv: {stats2['total']:,} records (VIC only)
- Numbers already dialed: {len(called_txt):,}
- Numbers NOT yet called: ~{len(not_called_all):,}

DATA QUALITY (massive_list):
- {stats1['has_email']/stats1['total']*100:.0f}% have email
- {stats1['has_mobile']/stats1['total']*100:.0f}% have mobile
- {stats1['has_first_name']/stats1['total']*100:.0f}% have first name
- {stats1['has_company']/stats1['total']*100:.0f}% have company

NOTE: These are from previous RetellAI outbound dialer campaigns.
To link with Zadarma/Retell recordings, cross-reference by phone number.
""")


if __name__ == "__main__":
    main()
