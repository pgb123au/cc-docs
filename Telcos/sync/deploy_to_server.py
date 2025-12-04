#!/usr/bin/env python3
"""
Deploy sync_expanded.py to RackNerd server and set up cron job
Runs sync every 5 minutes automatically
"""

import paramiko
import os
from pathlib import Path

# Server details
SERVER_IP = "96.47.238.189"
ROOT_PASSWORD = "YiL8J7wuu05uSa6BW1"
REMOTE_DIR = "/opt/telco_sync"

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
    print("DEPLOYING TELCO SYNC TO RACKNERD SERVER")
    print("=" * 60)

    # Read local files
    script_dir = Path(__file__).parent

    sync_script = (script_dir / "sync_expanded.py").read_text()
    credentials = (script_dir.parent / ".credentials").read_text()

    # Also need to get Retell API key
    retell_key = None
    retell_paths = [
        Path.home() / "Downloads" / "Retell_API_Key.txt",
        Path.home() / "Downloads" / "CC" / "retell" / "Retell_API_Key.txt",
    ]
    for path in retell_paths:
        if path.exists():
            key = path.read_text().strip()
            key = key.replace("API Key:", "").replace("key:", "").strip()
            if key:
                retell_key = key
                break

    if retell_key:
        print(f"[OK] Found Retell API key: {retell_key[:10]}...")
        credentials += f"\nRETELL_API_KEY={retell_key}\n"
    else:
        print("[WARN] No Retell API key found - Retell sync will be skipped")

    print("\nConnecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER_IP, username='root', password=ROOT_PASSWORD, timeout=30)
        print("[OK] Connected!\n")

        # Create remote directory
        run_ssh_command(ssh, f"mkdir -p {REMOTE_DIR}")

        # Install required packages
        print("\n[1] Installing Python packages...")
        run_ssh_command(ssh, "pip3 install psycopg2-binary requests retell-sdk 2>/dev/null || pip install psycopg2-binary requests retell-sdk", timeout=120)

        # Upload sync script
        print("\n[2] Uploading sync script...")
        sftp = ssh.open_sftp()

        # Write sync_expanded.py
        with sftp.file(f"{REMOTE_DIR}/sync_expanded.py", 'w') as f:
            f.write(sync_script)
        print(f"    [OK] Uploaded sync_expanded.py")

        # Write .credentials
        with sftp.file(f"{REMOTE_DIR}/.credentials", 'w') as f:
            f.write(credentials)
        print(f"    [OK] Uploaded .credentials")

        # Create wrapper script for cron
        wrapper = f"""#!/bin/bash
cd {REMOTE_DIR}
/usr/bin/python3 sync_expanded.py >> /var/log/telco_sync.log 2>&1
"""
        with sftp.file(f"{REMOTE_DIR}/run_sync.sh", 'w') as f:
            f.write(wrapper)

        sftp.close()

        # Set secure permissions (only root can access)
        print("\n[2b] Setting secure permissions...")
        run_ssh_command(ssh, f"chmod 700 {REMOTE_DIR}")
        run_ssh_command(ssh, f"chmod 600 {REMOTE_DIR}/.credentials")
        run_ssh_command(ssh, f"chmod 700 {REMOTE_DIR}/run_sync.sh")
        run_ssh_command(ssh, f"chmod 600 {REMOTE_DIR}/sync_expanded.py")
        print("    [OK] Credentials secured (root-only access)")

        # Update the sync script to look for credentials in the same directory
        print("\n[3] Patching script for server paths...")
        patch_cmd = f"""sed -i 's|cred_file = Path(__file__).parent.parent / ".credentials"|cred_file = Path(__file__).parent / ".credentials"|' {REMOTE_DIR}/sync_expanded.py"""
        run_ssh_command(ssh, patch_cmd)

        # Test the sync
        print("\n[4] Testing sync (quick run)...")
        output, _, code = run_ssh_command(ssh, f"cd {REMOTE_DIR} && python3 sync_expanded.py 2>&1 | tail -20", timeout=180)

        if code == 0:
            print("    [OK] Sync test passed!")
        else:
            print("    [WARN] Sync had issues, check output above")

        # Set up cron job
        print("\n[5] Setting up cron job (every 5 minutes)...")

        # Remove old cron if exists, add new one
        cron_line = f"*/5 * * * * {REMOTE_DIR}/run_sync.sh"
        run_ssh_command(ssh, f"(crontab -l 2>/dev/null | grep -v 'telco_sync' ; echo '{cron_line}') | crontab -")

        # Verify cron
        print("\n[6] Verifying cron job...")
        output, _, _ = run_ssh_command(ssh, "crontab -l")

        if "telco_sync" in output:
            print("    [OK] Cron job installed!")

        # Create log rotation
        print("\n[7] Setting up log rotation...")
        logrotate_conf = f"""/var/log/telco_sync.log {{
    daily
    rotate 7
    compress
    missingok
    notifempty
}}
"""
        run_ssh_command(ssh, f"echo '{logrotate_conf}' > /etc/logrotate.d/telco_sync")

        print("\n" + "=" * 60)
        print("DEPLOYMENT COMPLETE!")
        print("=" * 60)
        print(f"""
Sync script location: {REMOTE_DIR}/sync_expanded.py
Cron schedule: Every 5 minutes
Log file: /var/log/telco_sync.log

To monitor:
  ssh root@{SERVER_IP}
  tail -f /var/log/telco_sync.log

To run manually:
  ssh root@{SERVER_IP} '{REMOTE_DIR}/run_sync.sh'

To check cron:
  ssh root@{SERVER_IP} 'crontab -l'
""")

    except Exception as e:
        print(f"[ERROR] {e}")
        raise
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
