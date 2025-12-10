#!/usr/bin/env python3
"""
Deploy API Monitor to RackNerd Server
Sets up the API monitor with daily cron job
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuration
SERVER_IP = "96.47.238.189"
SERVER_USER = "root"
SSH_KEY = Path.home() / ".ssh" / "metabase-aws"
REMOTE_DIR = "/opt/telco_sync/api_monitor"

# Local paths
SCRIPT_DIR = Path(__file__).parent
FILES_TO_DEPLOY = [
    "api_monitor.py",
    "monitor_config.yaml",
    "analysis_context.md",
]
CREDENTIALS_FILE = SCRIPT_DIR.parent / ".credentials"


def run_ssh(cmd: str, check: bool = True) -> str:
    """Run command on remote server"""
    full_cmd = f'ssh -i "{SSH_KEY}" {SERVER_USER}@{SERVER_IP} "{cmd}"'
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        return ""
    return result.stdout.strip()


def run_scp(local: Path, remote: str):
    """Copy file to remote server"""
    cmd = f'scp -i "{SSH_KEY}" "{local}" {SERVER_USER}@{SERVER_IP}:{remote}'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error copying {local}: {result.stderr}")
        return False
    return True


def main():
    print("=" * 60)
    print("API MONITOR DEPLOYMENT")
    print("=" * 60)

    # Check SSH key exists
    if not SSH_KEY.exists():
        print(f"\nError: SSH key not found at {SSH_KEY}")
        return 1

    # Check credentials have been updated
    print("\nChecking credentials...")
    with open(CREDENTIALS_FILE, 'r') as f:
        creds_content = f.read()

    if "YOUR_ANTHROPIC_API_KEY_HERE" in creds_content:
        print("\n⚠️  WARNING: ANTHROPIC_API_KEY not set in .credentials")
        print("   The monitor will work but won't have AI analysis.")
        print("   Add your key from: https://console.anthropic.com/")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return 1

    if "YOUR_GITHUB_TOKEN_HERE" in creds_content:
        print("\n⚠️  WARNING: GITHUB_TOKEN not set in .credentials")
        print("   The monitor won't create GitHub issues automatically.")
        print("   Create a token at: https://github.com/settings/tokens")

    # Create remote directory
    print(f"\nCreating remote directory: {REMOTE_DIR}")
    run_ssh(f"mkdir -p {REMOTE_DIR}/page_snapshots")

    # Deploy files
    print("\nDeploying files...")
    for filename in FILES_TO_DEPLOY:
        local_path = SCRIPT_DIR / filename
        if local_path.exists():
            print(f"  - {filename}...", end=" ")
            if run_scp(local_path, f"{REMOTE_DIR}/{filename}"):
                print("OK")
            else:
                print("FAILED")
        else:
            print(f"  - {filename}... NOT FOUND")

    # Deploy credentials (append to existing if needed)
    print("\nUpdating credentials on server...")
    run_ssh(f"cp /opt/telco_sync/.credentials /opt/telco_sync/.credentials.bak 2>/dev/null || true")

    # Read local credentials and merge with remote
    new_creds = []
    with open(CREDENTIALS_FILE, 'r') as f:
        for line in f:
            if 'ANTHROPIC_API_KEY' in line or 'GITHUB_TOKEN' in line:
                new_creds.append(line.strip())

    if new_creds:
        # Check if keys already exist on server
        for cred in new_creds:
            key = cred.split('=')[0]
            existing = run_ssh(f"grep '^{key}=' /opt/telco_sync/.credentials 2>/dev/null || true", check=False)
            if not existing:
                print(f"  Adding {key} to server credentials...")
                run_ssh(f"echo '{cred}' >> /opt/telco_sync/.credentials")
            else:
                print(f"  {key} already exists on server")

    # Set permissions
    print("\nSetting permissions...")
    run_ssh(f"chmod 750 {REMOTE_DIR}")
    run_ssh(f"chmod 640 {REMOTE_DIR}/*.py")
    run_ssh(f"chmod 640 {REMOTE_DIR}/*.yaml")
    run_ssh(f"chmod 640 {REMOTE_DIR}/*.md")
    run_ssh(f"chmod 750 {REMOTE_DIR}/page_snapshots")

    # Install dependencies
    print("\nInstalling Python dependencies...")
    run_ssh("pip3 install pyyaml beautifulsoup4 anthropic 2>/dev/null || pip install pyyaml beautifulsoup4 anthropic")

    # Set up daily cron job
    print("\nConfiguring daily cron job...")

    # Create wrapper script
    wrapper_script = f"""#!/bin/bash
# API Monitor daily check
cd {REMOTE_DIR}
source /opt/telco_sync/.credentials 2>/dev/null || true
export $(grep -v '^#' /opt/telco_sync/.credentials | xargs) 2>/dev/null || true
/usr/bin/python3 api_monitor.py >> /var/log/api_monitor.log 2>&1
"""

    # Write wrapper script
    run_ssh(f"cat > {REMOTE_DIR}/run_monitor.sh << 'EOF'\n{wrapper_script}EOF")
    run_ssh(f"chmod 750 {REMOTE_DIR}/run_monitor.sh")

    # Add cron job (daily at 6:00 AM)
    cron_line = f"0 6 * * * {REMOTE_DIR}/run_monitor.sh"

    # Check if cron job already exists
    existing_cron = run_ssh("crontab -l 2>/dev/null || true", check=False)
    if "api_monitor" not in existing_cron and "run_monitor.sh" not in existing_cron:
        print("  Adding cron job for daily 6:00 AM check...")
        run_ssh(f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -')
    else:
        print("  Cron job already exists")

    # Verify deployment
    print("\nVerifying deployment...")
    files = run_ssh(f"ls -la {REMOTE_DIR}/")
    print(files)

    cron_jobs = run_ssh("crontab -l | grep -E '(api_monitor|run_monitor)'", check=False)
    print(f"\nCron jobs:\n{cron_jobs}")

    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE")
    print("=" * 60)
    print(f"""
Next steps:
1. Add your Anthropic API key to .credentials:
   ANTHROPIC_API_KEY=sk-ant-...

2. Add your GitHub token to .credentials:
   GITHUB_TOKEN=ghp_...

3. Run manually to test:
   ssh -i "{SSH_KEY}" {SERVER_USER}@{SERVER_IP} "{REMOTE_DIR}/run_monitor.sh"

4. Check logs:
   ssh -i "{SSH_KEY}" {SERVER_USER}@{SERVER_IP} "tail -f /var/log/api_monitor.log"

The monitor will run daily at 6:00 AM server time.
""")

    return 0


if __name__ == "__main__":
    sys.exit(main())
