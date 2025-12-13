"""
Contact Import Script for Yes AI Marketing
Imports XLS/CSV files into Brevo with automatic column detection.

Usage:
    python import_contacts.py                    # Process all files in pending/
    python import_contacts.py myfile.xlsx        # Process specific file
    python import_contacts.py --list "VIC Leads" # Create/use specific list

Features:
    - Auto-detects column mappings (mobile, email, name, etc.)
    - Normalizes Australian phone numbers to +61 format
    - Deduplicates against existing contacts
    - Moves processed files to processed/ or errors/
    - Generates import report
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import csv

# Add scripts folder to path
sys.path.insert(0, str(Path(__file__).parent))
from brevo_api import BrevoClient, normalize_australian_mobile, validate_email

# Paths
MARKETING_ROOT = Path(__file__).parent.parent
PENDING_DIR = MARKETING_ROOT / "imports" / "pending"
PROCESSED_DIR = MARKETING_ROOT / "imports" / "processed"
ERRORS_DIR = MARKETING_ROOT / "imports" / "errors"
REPORTS_DIR = MARKETING_ROOT / "reports"

# Column mapping patterns (lowercase)
COLUMN_PATTERNS = {
    "email": ["email", "e-mail", "email_address", "emailaddress", "mail"],
    "mobile": ["mobile", "phone", "cell", "mobile_number", "contact_number", "phone_number", "mob", "tel", "telephone"],
    "first_name": ["first_name", "firstname", "first", "given_name", "givenname", "fname"],
    "last_name": ["last_name", "lastname", "last", "surname", "family_name", "familyname", "lname"],
    "full_name": ["name", "full_name", "fullname", "contact_name", "contactname"],
    "company": ["company", "company_name", "companyname", "business", "organisation", "organization", "org"],
    "postcode": ["postcode", "post_code", "zip", "zipcode", "zip_code"],
    "suburb": ["suburb", "city", "town", "locality"],
    "state": ["state", "region", "province"],
}


def detect_columns(headers: list) -> dict:
    """
    Auto-detect column mappings from headers.

    Returns:
        Dict mapping our fields to column indices
        e.g., {"email": 2, "mobile": 3, "first_name": 0}
    """
    mappings = {}
    headers_lower = [h.lower().strip() if h else "" for h in headers]

    for field, patterns in COLUMN_PATTERNS.items():
        for i, header in enumerate(headers_lower):
            if header in patterns:
                mappings[field] = i
                break

    return mappings


def read_file(filepath: Path) -> tuple:
    """
    Read XLS, XLSX, or CSV file.

    Returns:
        (headers, rows) tuple
    """
    suffix = filepath.suffix.lower()

    if suffix == ".csv":
        return read_csv(filepath)
    elif suffix in [".xls", ".xlsx"]:
        return read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def read_csv(filepath: Path) -> tuple:
    """Read CSV file."""
    rows = []

    # Try different encodings
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(filepath, "r", encoding=encoding, newline="") as f:
                # Detect delimiter
                sample = f.read(4096)
                f.seek(0)

                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                reader = csv.reader(f, dialect)

                rows = list(reader)
                break
        except (UnicodeDecodeError, csv.Error):
            continue

    if not rows:
        raise ValueError("Could not read CSV file with any encoding")

    headers = rows[0] if rows else []
    data = rows[1:] if len(rows) > 1 else []

    return headers, data


def read_excel(filepath: Path) -> tuple:
    """Read Excel file (requires openpyxl or xlrd)."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        ws = wb.active

        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append([str(cell) if cell is not None else "" for cell in row])

        wb.close()

        headers = rows[0] if rows else []
        data = rows[1:] if len(rows) > 1 else []

        return headers, data

    except ImportError:
        try:
            import pandas as pd
            df = pd.read_excel(filepath)
            headers = df.columns.tolist()
            data = df.values.tolist()
            return headers, [[str(cell) if pd.notna(cell) else "" for cell in row] for row in data]
        except ImportError:
            raise ImportError(
                "Excel support requires openpyxl or pandas.\n"
                "Install with: pip install openpyxl\n"
                "Or: pip install pandas openpyxl"
            )


def process_row(row: list, mappings: dict) -> dict:
    """
    Process a single row into a contact dict.

    Returns:
        {"email": "...", "attributes": {...}, "valid": True/False, "errors": [...]}
    """
    contact = {
        "email": None,
        "attributes": {},
        "valid": False,
        "errors": []
    }

    # Extract fields
    def get_value(field):
        if field in mappings:
            idx = mappings[field]
            if idx < len(row):
                val = str(row[idx]).strip()
                return val if val and val.lower() not in ["none", "nan", "null", ""] else None
        return None

    # Email
    email = get_value("email")
    if email and validate_email(email):
        contact["email"] = email.lower()
    else:
        contact["errors"].append(f"Invalid/missing email: {email}")

    # Mobile
    mobile = get_value("mobile")
    if mobile:
        normalized = normalize_australian_mobile(mobile)
        if normalized and normalized.startswith("+61") and len(normalized) == 12:
            contact["attributes"]["SMS"] = normalized
        else:
            contact["errors"].append(f"Invalid mobile: {mobile}")

    # Name handling
    first_name = get_value("first_name")
    last_name = get_value("last_name")
    full_name = get_value("full_name")

    if first_name:
        contact["attributes"]["FIRSTNAME"] = first_name.title()
    if last_name:
        contact["attributes"]["LASTNAME"] = last_name.title()

    # If only full_name, try to split
    if full_name and not first_name:
        parts = full_name.strip().split(" ", 1)
        contact["attributes"]["FIRSTNAME"] = parts[0].title()
        if len(parts) > 1:
            contact["attributes"]["LASTNAME"] = parts[1].title()

    # Company
    company = get_value("company")
    if company:
        contact["attributes"]["COMPANY"] = company

    # Location
    postcode = get_value("postcode")
    if postcode:
        # Clean postcode (remove decimals from Excel)
        postcode = postcode.split(".")[0]
        if postcode.isdigit() and len(postcode) == 4:
            contact["attributes"]["POSTCODE"] = postcode

    suburb = get_value("suburb")
    if suburb:
        contact["attributes"]["SUBURB"] = suburb.title()

    state = get_value("state")
    if state:
        contact["attributes"]["STATE"] = state.upper()[:3]

    # Validation
    if contact["email"]:
        contact["valid"] = True
    elif contact["attributes"].get("SMS"):
        # Allow SMS-only contacts with generated email
        contact["email"] = f"sms_{contact['attributes']['SMS'].replace('+', '')}@placeholder.local"
        contact["valid"] = True

    return contact


def import_file(
    filepath: Path,
    client: BrevoClient,
    list_name: str = None,
    dry_run: bool = False
) -> dict:
    """
    Import a single file into Brevo.

    Returns:
        Import statistics dict
    """
    stats = {
        "file": filepath.name,
        "total_rows": 0,
        "valid": 0,
        "invalid": 0,
        "imported": 0,
        "duplicates": 0,
        "errors": [],
        "started_at": datetime.now().isoformat()
    }

    print(f"\nProcessing: {filepath.name}")
    print("-" * 50)

    # Read file
    try:
        headers, rows = read_file(filepath)
        stats["total_rows"] = len(rows)
        print(f"Rows found: {len(rows)}")
    except Exception as e:
        stats["errors"].append(f"Failed to read file: {e}")
        return stats

    # Detect columns
    mappings = detect_columns(headers)
    print(f"Detected columns: {mappings}")

    if not mappings:
        stats["errors"].append("Could not detect any valid columns")
        return stats

    if "email" not in mappings and "mobile" not in mappings:
        stats["errors"].append("No email or mobile column found")
        return stats

    # Create/get list if specified
    list_id = None
    if list_name:
        result = client.get_lists(limit=100)
        if result["success"]:
            existing = next((l for l in result["data"].get("lists", []) if l["name"] == list_name), None)
            if existing:
                list_id = existing["id"]
                print(f"Using existing list: {list_name} (ID: {list_id})")
            else:
                create_result = client.create_list(list_name)
                if create_result["success"]:
                    list_id = create_result["data"]["id"]
                    print(f"Created new list: {list_name} (ID: {list_id})")

    # Process rows
    contacts_to_import = []

    for i, row in enumerate(rows):
        contact = process_row(row, mappings)

        if contact["valid"]:
            stats["valid"] += 1
            contacts_to_import.append(contact)
        else:
            stats["invalid"] += 1
            if contact["errors"]:
                stats["errors"].append(f"Row {i+2}: {', '.join(contact['errors'])}")

    print(f"Valid contacts: {stats['valid']}")
    print(f"Invalid rows: {stats['invalid']}")

    if dry_run:
        print("\n[DRY RUN] No contacts imported")
        return stats

    # Import to Brevo
    print(f"\nImporting to Brevo...")

    for contact in contacts_to_import:
        try:
            result = client.add_contact(
                email=contact["email"],
                attributes=contact["attributes"],
                list_ids=[list_id] if list_id else None
            )

            if result["success"]:
                stats["imported"] += 1
            elif "duplicate" in str(result.get("error", "")).lower():
                stats["duplicates"] += 1
            else:
                stats["errors"].append(f"{contact['email']}: {result.get('error', 'Unknown error')}")

        except Exception as e:
            stats["errors"].append(f"{contact['email']}: {e}")

        # Progress indicator
        total = stats["imported"] + stats["duplicates"] + len([e for e in stats["errors"] if contact["email"] in e])
        if total % 50 == 0:
            print(f"  Processed {total}/{stats['valid']}...")

    stats["finished_at"] = datetime.now().isoformat()

    print(f"\nImport complete:")
    print(f"  Imported: {stats['imported']}")
    print(f"  Duplicates: {stats['duplicates']}")
    print(f"  Errors: {len(stats['errors'])}")

    return stats


def move_file(filepath: Path, success: bool, stats: dict):
    """Move processed file to appropriate directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_dir = PROCESSED_DIR if success else ERRORS_DIR

    # New filename with timestamp
    new_name = f"{timestamp}_{filepath.name}"
    dest_path = dest_dir / new_name

    filepath.rename(dest_path)
    print(f"Moved to: {dest_path}")

    # Save report
    report_path = REPORTS_DIR / f"{timestamp}_{filepath.stem}_report.json"
    with open(report_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Report: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Import contacts to Brevo")
    parser.add_argument("file", nargs="?", help="Specific file to import")
    parser.add_argument("--list", "-l", help="List name to add contacts to")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview without importing")
    args = parser.parse_args()

    # Initialize client
    try:
        client = BrevoClient()
        print("Connected to Brevo")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Find files to process
    if args.file:
        # Specific file
        filepath = Path(args.file)
        if not filepath.exists():
            filepath = PENDING_DIR / args.file
        if not filepath.exists():
            print(f"File not found: {args.file}")
            sys.exit(1)
        files = [filepath]
    else:
        # All files in pending/
        files = list(PENDING_DIR.glob("*.csv")) + \
                list(PENDING_DIR.glob("*.xlsx")) + \
                list(PENDING_DIR.glob("*.xls"))

    if not files:
        print(f"No files to process in {PENDING_DIR}")
        sys.exit(0)

    print(f"Files to process: {len(files)}")

    # Process each file
    all_stats = []
    for filepath in files:
        stats = import_file(
            filepath=filepath,
            client=client,
            list_name=args.list,
            dry_run=args.dry_run
        )
        all_stats.append(stats)

        if not args.dry_run:
            success = stats["imported"] > 0 or stats["duplicates"] > 0
            move_file(filepath, success, stats)

    # Summary
    print("\n" + "=" * 50)
    print("IMPORT SUMMARY")
    print("=" * 50)

    total_imported = sum(s["imported"] for s in all_stats)
    total_duplicates = sum(s["duplicates"] for s in all_stats)
    total_errors = sum(len(s["errors"]) for s in all_stats)

    print(f"Files processed: {len(all_stats)}")
    print(f"Total imported: {total_imported}")
    print(f"Total duplicates: {total_duplicates}")
    print(f"Total errors: {total_errors}")


if __name__ == "__main__":
    main()
