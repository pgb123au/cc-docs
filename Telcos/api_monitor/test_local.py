#!/usr/bin/env python3
"""
Local test script for API Monitor
Tests fetching and change detection without sending emails
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from api_monitor import (
    load_config,
    fetch_page_content,
    check_for_changes,
    load_credentials
)


def test_single_page():
    """Test fetching a single page"""
    print("=" * 60)
    print("TEST: Single Page Fetch")
    print("=" * 60)

    # Test RetellAI changelog
    url = "https://docs.retellai.com/changelog"
    print(f"\nFetching: {url}")

    content, content_hash = fetch_page_content(url, "main, article")

    if content:
        print(f"  Content length: {len(content)} chars")
        print(f"  Hash: {content_hash}")
        print(f"\nFirst 500 chars:")
        print("-" * 40)
        # Handle Unicode for Windows console
        preview = content[:500].encode('ascii', 'replace').decode('ascii')
        print(preview)
        print("-" * 40)
    else:
        print("  FAILED to fetch content")


def test_all_providers():
    """Test fetching all configured pages"""
    print("\n" + "=" * 60)
    print("TEST: All Providers")
    print("=" * 60)

    config = load_config()

    for provider_key, provider_config in config.get('providers', {}).items():
        provider_name = provider_config.get('name', provider_key)
        print(f"\n{provider_name}:")

        for page in provider_config.get('pages', []):
            page_name = page.get('name', 'Unknown')
            url = page.get('url')
            selector = page.get('selector', 'main')

            print(f"  - {page_name}...", end=' ')
            content, content_hash = fetch_page_content(url, selector)

            if content:
                print(f"OK ({len(content)} chars, hash: {content_hash[:8]})")
            else:
                print("FAILED")


def test_change_detection():
    """Test change detection (will create snapshots on first run)"""
    print("\n" + "=" * 60)
    print("TEST: Change Detection")
    print("=" * 60)

    config = load_config()
    changes = check_for_changes(config)

    print(f"\nChanges detected: {len(changes)}")

    for change in changes:
        print(f"\n  Provider: {change.provider}")
        print(f"  Page: {change.page_name}")
        print(f"  Summary: {change.diff_summary}")


def test_credentials():
    """Check if credentials are configured"""
    print("\n" + "=" * 60)
    print("TEST: Credentials")
    print("=" * 60)

    creds = load_credentials()

    required_keys = ['ANTHROPIC_API_KEY', 'GITHUB_TOKEN']

    for key in required_keys:
        value = creds.get(key, '')
        if value and 'YOUR_' not in value and value != '':
            print(f"  {key}: Configured [OK]")
        else:
            print(f"  {key}: NOT CONFIGURED [X]")


def main():
    print("API MONITOR - LOCAL TEST")
    print("=" * 60)

    test_credentials()
    test_single_page()
    test_all_providers()
    test_change_detection()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("""
Note: On first run, this creates baseline snapshots.
Run again to test change detection (should show no changes
unless pages have actually updated).

To test with mock changes, edit a snapshot file in page_snapshots/
and run again.
""")


if __name__ == "__main__":
    main()
