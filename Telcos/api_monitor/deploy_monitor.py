#!/usr/bin/env python3
"""
Deploy API Monitor to RackNerd Server
Sets up the API monitor with daily cron job
Uses paramiko with password authentication (same as other sync scripts)
"""

import os
import sys
import paramiko
from pathlib import Path

# Server details (same as sync scripts)
SERVER_IP = "96.47.238.189"
ROOT_PASSWORD = "YiL8J7wuu05uSa6BW1"
REMOTE_DIR = "/opt/telco_sync/api_monitor"

# Local paths
SCRIPT_DIR = Path(__file__).parent
FILES_TO_DEPLOY = [
    "api_monitor.py",
    "monitor_config.yaml",
    "analysis_context.md",
    "requirements.txt",
]
CREDENTIALS_FILE = SCRIPT_DIR.parent / ".credentials"


def run_ssh_command(ssh, command, timeout=60):
    """Run command and return output"""
    print(f">>> {command[:80]}{'...' if len(command) > 80 else ''}")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace').strip()
    error = stderr.read().decode('utf-8', errors='replace').strip()
    if output:
        for line in output.split('\n')[:10]:
            print(f"    {line}")
        if output.count('\n') > 10:
            print(f"    ... ({output.count(chr(10)) - 10} more lines)")
    if error and exit_code != 0:
        print(f"    [ERROR] {error[:200]}")
    return output, error, exit_code


def main():
    print("=" * 60)
    print("API MONITOR DEPLOYMENT")
    print("=" * 60)

    # Check credentials have been updated
    print("\nChecking local credentials...")
    with open(CREDENTIALS_FILE, 'r') as f:
        creds_content = f.read()

    if "YOUR_ANTHROPIC_API_KEY_HERE" in creds_content:
        print("  WARNING: ANTHROPIC_API_KEY not set - AI analysis won't work")
    else:
        print("  ANTHROPIC_API_KEY: OK")

    if "YOUR_GITHUB_TOKEN_HERE" in creds_content:
        print("  WARNING: GITHUB_TOKEN not set - GitHub issues won't be created")
    else:
        print("  GITHUB_TOKEN: OK")

    # Connect to server
    print(f"\nConnecting to {SERVER_IP}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER_IP, username='root', password=ROOT_PASSWORD, timeout=30)
        print("  Connected!")

        # Create remote directory
        print(f"\nCreating remote directory: {REMOTE_DIR}")
        run_ssh_command(ssh, f"mkdir -p {REMOTE_DIR}/page_snapshots")

        # Deploy files via SFTP
        print("\nDeploying files...")
        sftp = ssh.open_sftp()

        for filename in FILES_TO_DEPLOY:
            local_path = SCRIPT_DIR / filename
            remote_path = f"{REMOTE_DIR}/{filename}"
            if local_path.exists():
                print(f"  - {filename}...", end=" ")
                try:
                    sftp.put(str(local_path), remote_path)
                    print("OK")
                except Exception as e:
                    print(f"FAILED: {e}")
            else:
                print(f"  - {filename}... NOT FOUND")

        sftp.close()

        # Update credentials on server
        print("\nUpdating credentials on server...")
        run_ssh_command(ssh, "cp /opt/telco_sync/.credentials /opt/telco_sync/.credentials.bak 2>/dev/null || true")

        # Read local credentials for new keys
        new_creds = []
        with open(CREDENTIALS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if 'ANTHROPIC_API_KEY' in line or 'GITHUB_TOKEN' in line:
                        if 'YOUR_' not in line:
                            new_creds.append(line)

        for cred in new_creds:
            key = cred.split('=')[0]
            # Check if key exists
            output, _, _ = run_ssh_command(ssh, f"grep '^{key}=' /opt/telco_sync/.credentials 2>/dev/null || echo 'NOT_FOUND'")
            if 'NOT_FOUND' in output or not output:
                print(f"  Adding {key}...")
                # Escape single quotes in value
                safe_cred = cred.replace("'", "'\\''")
                run_ssh_command(ssh, f"echo '{safe_cred}' >> /opt/telco_sync/.credentials")
            else:
                print(f"  {key} already exists, updating...")
                value = cred.split('=', 1)[1]
                safe_value = value.replace("'", "'\\''")
                run_ssh_command(ssh, f"sed -i 's|^{key}=.*|{key}={safe_value}|' /opt/telco_sync/.credentials")

        # Set permissions
        print("\nSetting permissions...")
        run_ssh_command(ssh, f"chmod 750 {REMOTE_DIR}")
        run_ssh_command(ssh, f"chmod 640 {REMOTE_DIR}/*.py 2>/dev/null || true")
        run_ssh_command(ssh, f"chmod 640 {REMOTE_DIR}/*.yaml 2>/dev/null || true")
        run_ssh_command(ssh, f"chmod 640 {REMOTE_DIR}/*.md 2>/dev/null || true")
        run_ssh_command(ssh, f"chmod 750 {REMOTE_DIR}/page_snapshots")

        # Install dependencies
        print("\nInstalling Python dependencies...")
        run_ssh_command(ssh, "pip3 install pyyaml beautifulsoup4 anthropic requests 2>/dev/null || pip install pyyaml beautifulsoup4 anthropic requests", timeout=120)

        # Create wrapper script
        print("\nCreating run script...")
        wrapper_script = f"""#!/bin/bash
# API Monitor daily check
cd {REMOTE_DIR}
export $(grep -v '^#' /opt/telco_sync/.credentials | grep -v '^$' | xargs) 2>/dev/null
/usr/bin/python3 api_monitor.py >> /var/log/api_monitor.log 2>&1
"""
        # Write wrapper script using heredoc
        run_ssh_command(ssh, f"cat > {REMOTE_DIR}/run_monitor.sh << 'EOFSCRIPT'\n{wrapper_script}EOFSCRIPT")
        run_ssh_command(ssh, f"chmod 750 {REMOTE_DIR}/run_monitor.sh")

        # Set up cron job (daily at 6:00 AM)
        print("\nConfiguring daily cron job...")
        cron_line = f"0 6 * * * {REMOTE_DIR}/run_monitor.sh"

        output, _, _ = run_ssh_command(ssh, "crontab -l 2>/dev/null || true")
        if "run_monitor.sh" not in output:
            print("  Adding cron job for daily 6:00 AM check...")
            run_ssh_command(ssh, f"(crontab -l 2>/dev/null | grep -v 'run_monitor'; echo '{cron_line}') | crontab -")
        else:
            print("  Cron job already exists")

        # Verify deployment
        print("\nVerifying deployment...")
        run_ssh_command(ssh, f"ls -la {REMOTE_DIR}/")

        print("\nCron jobs:")
        run_ssh_command(ssh, "crontab -l | grep -E '(api_monitor|run_monitor|telco_sync)'")

        # Run a quick test
        print("\nRunning quick test (checking if script loads)...")
        output, error, code = run_ssh_command(ssh, f"cd {REMOTE_DIR} && python3 -c 'import api_monitor; print(\"Script loads OK\")'", timeout=30)

        print("\n" + "=" * 60)
        print("DEPLOYMENT COMPLETE")
        print("=" * 60)
        print(f"""
The API Monitor is now deployed and will run daily at 6:00 AM server time.

To run manually:
  ssh root@{SERVER_IP} '{REMOTE_DIR}/run_monitor.sh'

To check logs:
  ssh root@{SERVER_IP} 'tail -f /var/log/api_monitor.log'

To check cron:
  ssh root@{SERVER_IP} 'crontab -l'
""")
        return 0

    except Exception as e:
        print(f"\nError: {e}")
        return 1

    finally:
        ssh.close()


if __name__ == "__main__":
    sys.exit(main())
