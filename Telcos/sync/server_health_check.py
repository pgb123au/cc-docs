#!/usr/bin/env python3
"""
Server Health Check Script
Runs on RackNerd server and posts results to n8n webhook
Can also be run locally to check both servers
"""

import subprocess
import json
import requests
from datetime import datetime
from pathlib import Path

# Configuration
WEBHOOK_URL = "https://auto.yr.com.au/webhook/server-health-report"
ALERT_EMAIL = "peter@yr.com.au"

# Thresholds
DISK_WARNING = 80  # percent
MEMORY_WARNING = 90  # percent


def run_cmd(cmd, timeout=30):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1


def check_local_server():
    """Check health of local server (RackNerd)"""
    status = {
        "server": "RackNerd",
        "ip": "96.47.238.189",
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "issues": []
    }

    # Uptime
    output, _ = run_cmd("uptime")
    status["checks"]["uptime"] = output

    # Disk usage
    output, _ = run_cmd("df -h / | tail -1 | awk '{print $5}' | tr -d '%'")
    try:
        disk_pct = int(output)
        status["checks"]["disk_percent"] = disk_pct
        if disk_pct > DISK_WARNING:
            status["issues"].append(f"Disk usage high: {disk_pct}%")
    except:
        status["checks"]["disk_percent"] = output

    # Memory usage
    output, _ = run_cmd("free | grep Mem | awk '{printf \"%.0f\", $3/$2 * 100}'")
    try:
        mem_pct = int(output)
        status["checks"]["memory_percent"] = mem_pct
        if mem_pct > MEMORY_WARNING:
            status["issues"].append(f"Memory usage high: {mem_pct}%")
    except:
        status["checks"]["memory_percent"] = output

    # PostgreSQL
    output, code = run_cmd("systemctl is-active postgresql")
    status["checks"]["postgresql"] = "OK" if code == 0 else "DOWN"
    if code != 0:
        status["issues"].append("PostgreSQL is DOWN!")

    # Cron
    output, code = run_cmd("systemctl is-active cron")
    status["checks"]["cron"] = "OK" if code == 0 else "DOWN"
    if code != 0:
        status["issues"].append("Cron is DOWN!")

    # Docker (if installed)
    output, code = run_cmd("systemctl is-active docker 2>/dev/null")
    if code == 0:
        status["checks"]["docker"] = "OK"

    # Telco sync - check last run
    log_output, _ = run_cmd("tail -5 /var/log/telco_sync.log 2>/dev/null")
    if "Expanded sync complete" in log_output:
        status["checks"]["telco_sync"] = "OK"
    elif log_output:
        status["checks"]["telco_sync"] = "ERROR"
        status["issues"].append("Telco sync has errors - check logs")
    else:
        status["checks"]["telco_sync"] = "NO_LOG"

    # Check last sync time
    output, _ = run_cmd("stat -c %Y /var/log/telco_sync.log 2>/dev/null")
    try:
        last_sync = int(output)
        now = int(datetime.now().timestamp())
        mins_ago = (now - last_sync) // 60
        status["checks"]["last_sync_mins_ago"] = mins_ago
        if mins_ago > 10:  # Should run every 5 mins
            status["issues"].append(f"Telco sync hasn't run in {mins_ago} minutes")
    except:
        pass

    # Reboot required
    output, code = run_cmd("[ -f /var/run/reboot-required ] && echo 'YES' || echo 'NO'")
    status["checks"]["reboot_required"] = output == "YES"
    if output == "YES":
        status["issues"].append("Server needs reboot for security updates")

    # Available updates
    output, _ = run_cmd("apt list --upgradable 2>/dev/null | wc -l")
    try:
        updates = int(output) - 1  # Subtract header line
        status["checks"]["updates_available"] = updates
        if updates > 20:
            status["issues"].append(f"{updates} security updates available")
    except:
        pass

    # Database size
    output, _ = run_cmd("sudo -u postgres psql -d telco_warehouse -t -c \"SELECT pg_size_pretty(pg_database_size('telco_warehouse'));\" 2>/dev/null")
    status["checks"]["db_size"] = output.strip()

    # Call count
    output, _ = run_cmd("sudo -u postgres psql -d telco_warehouse -t -c \"SELECT COUNT(*) FROM telco.calls;\" 2>/dev/null")
    try:
        status["checks"]["total_calls"] = int(output.strip())
    except:
        pass

    return status


def post_to_webhook(status):
    """Post health status to n8n webhook"""
    try:
        response = requests.post(WEBHOOK_URL, json=status, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to post to webhook: {e}")
        return False


def main():
    print("=" * 60)
    print("SERVER HEALTH CHECK")
    print("=" * 60)

    status = check_local_server()

    print(f"\nServer: {status['server']} ({status['ip']})")
    print(f"Time: {status['timestamp']}")
    print("\nChecks:")
    for key, value in status["checks"].items():
        print(f"  {key}: {value}")

    if status["issues"]:
        print(f"\n⚠️  Issues Found ({len(status['issues'])}):")
        for issue in status["issues"]:
            print(f"  - {issue}")
    else:
        print("\n✓ All checks passed!")

    # Post to webhook if configured
    if WEBHOOK_URL and "example.com" not in WEBHOOK_URL:
        print("\nPosting to webhook...")
        if post_to_webhook(status):
            print("  [OK] Posted successfully")
        else:
            print("  [WARN] Failed to post")

    return 0 if not status["issues"] else 1


if __name__ == "__main__":
    exit(main())
