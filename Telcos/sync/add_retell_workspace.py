#!/usr/bin/env python3
"""
Add a new Retell workspace to the sync system.

Usage:
    python add_retell_workspace.py <workspace_id> <workspace_name> <api_key>

Example:
    python add_retell_workspace.py ws_new_client "New Client Name" "key_abc123..."
"""

import sys
import psycopg2
from pathlib import Path

DB_CONFIG = {
    "host": "96.47.238.189",
    "port": 5432,
    "database": "telco_warehouse",
    "user": "telco_sync",
    "password": "TelcoSync2024!"
}

def add_workspace(workspace_id, workspace_name, api_key, webhook_url=None):
    """Add a new workspace to the database"""
    conn = psycopg2.connect(**DB_CONFIG)
    api_key_prefix = api_key[:10] if api_key else None
    try:
        with conn.cursor() as cur:
            # Check if exists
            cur.execute("SELECT workspace_id FROM telco.retell_workspaces WHERE workspace_id = %s", (workspace_id,))
            if cur.fetchone():
                print(f"[WARN] Workspace {workspace_id} already exists. Updating...")
                cur.execute("""
                    UPDATE telco.retell_workspaces
                    SET workspace_name = %s, api_key_prefix = %s, api_key_full = %s, webhook_url = %s
                    WHERE workspace_id = %s
                """, (workspace_name, api_key_prefix, api_key, webhook_url, workspace_id))
            else:
                cur.execute("""
                    INSERT INTO telco.retell_workspaces
                    (workspace_id, workspace_name, api_key_prefix, api_key_full, webhook_url, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, true, NOW())
                """, (workspace_id, workspace_name, api_key_prefix, api_key, webhook_url))
                print(f"[OK] Added workspace: {workspace_name}")

            conn.commit()

            # List all workspaces
            cur.execute("SELECT workspace_id, workspace_name, is_active, total_calls FROM telco.retell_workspaces")
            print("\n=== All Workspaces ===")
            for row in cur.fetchall():
                status = "✓ active" if row[2] else "✗ inactive"
                print(f"  {row[0]}: {row[1]} ({row[3] or 0} calls) [{status}]")

    finally:
        conn.close()

def list_workspaces():
    """List all configured workspaces"""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT workspace_id, workspace_name, api_key_prefix, is_active, total_calls, last_synced, webhook_url
                FROM telco.retell_workspaces ORDER BY workspace_name
            """)
            print("=== Configured Retell Workspaces ===")
            for row in cur.fetchall():
                status = "[ACTIVE]" if row[3] else "[INACTIVE]"
                key_preview = row[2] + "..." if row[2] else "NO KEY"
                synced = row[5].strftime("%Y-%m-%d %H:%M") if row[5] else "Never"
                print(f"\n  {status} {row[1]} ({row[0]})")
                print(f"      API Key: {key_preview}")
                print(f"      Webhook: {row[6] or 'Not set'}")
                print(f"      Calls: {row[4] or 0}, Last sync: {synced}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ["-l", "--list", "list"]:
        list_workspaces()
    elif len(sys.argv) == 4:
        add_workspace(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)
