# Telco Sync Server Setup

## Overview
The telco sync runs automatically on the RackNerd server every 5 minutes via cron.
This eliminates CMD popups on your PC and ensures 24/7 operation.

## Server Details

| Item | Value |
|------|-------|
| Server IP | `96.47.238.189` |
| SSH User | `root` |
| Sync Directory | `/opt/telco_sync/` |
| Log File | `/var/log/telco_sync.log` |
| Cron Schedule | Every 5 minutes (`*/5 * * * *`) |

## Files on Server

| File | Purpose |
|------|---------|
| `/opt/telco_sync/sync_expanded.py` | Main sync script |
| `/opt/telco_sync/.credentials` | API keys (Retell, Telnyx, Zadarma, PostgreSQL) |
| `/opt/telco_sync/run_sync.sh` | Cron wrapper script |

## Security Configuration

### Permissions
```
drwxr-x--- root:telco_sync  /opt/telco_sync/
-rw-r----- root:telco_sync  .credentials (IMMUTABLE)
-rw-r----- root:telco_sync  sync_expanded.py
-rwxr-x--- root:telco_sync  run_sync.sh
```

### Security Layers
1. **Dedicated service user**: `telco_sync` with no login shell
2. **Group-based access**: Only root and telco_sync group can access
3. **Immutable credentials**: `.credentials` has `chattr +i` flag
4. **No world-readable files**: All permissions are 640/750

## Common Commands

### Monitor sync logs
```bash
ssh root@96.47.238.189 'tail -f /var/log/telco_sync.log'
```

### Run sync manually
```bash
ssh root@96.47.238.189 '/opt/telco_sync/run_sync.sh'
```

### Check cron job
```bash
ssh root@96.47.238.189 'crontab -l | grep telco'
```

### View last sync results
```bash
ssh root@96.47.238.189 'tail -30 /var/log/telco_sync.log'
```

## Updating Credentials

The credentials file is immutable. To update:

```bash
ssh root@96.47.238.189

# Remove immutable flag
chattr -i /opt/telco_sync/.credentials

# Edit credentials
nano /opt/telco_sync/.credentials

# Re-apply immutable flag
chattr +i /opt/telco_sync/.credentials
```

## Updating the Sync Script

Run the deployment script from your PC:
```bash
cd C:\Users\peter\Downloads\CC\Telcos\sync
python deploy_to_server.py
```

Or manually:
```bash
# Copy new script
scp sync_expanded.py root@96.47.238.189:/opt/telco_sync/

# SSH in and fix path + permissions
ssh root@96.47.238.189
sed -i 's|cred_file = Path(__file__).parent.parent / ".credentials"|cred_file = Path(__file__).parent / ".credentials"|' /opt/telco_sync/sync_expanded.py
chmod 640 /opt/telco_sync/sync_expanded.py
chown root:telco_sync /opt/telco_sync/sync_expanded.py
```

## Troubleshooting

### Sync not running?
```bash
# Check cron is running
ssh root@96.47.238.189 'systemctl status cron'

# Check recent log entries
ssh root@96.47.238.189 'tail -50 /var/log/telco_sync.log'
```

### Permission denied errors?
```bash
# Reset permissions
ssh root@96.47.238.189 '
chmod 750 /opt/telco_sync
chmod 640 /opt/telco_sync/.credentials
chmod 640 /opt/telco_sync/sync_expanded.py
chmod 750 /opt/telco_sync/run_sync.sh
chown -R root:telco_sync /opt/telco_sync
'
```

### Need to reinstall Python packages?
```bash
ssh root@96.47.238.189 'pip3 install --break-system-packages psycopg2-binary retell-sdk requests'
```

## Credentials Format

The `.credentials` file format:
```
# Telnyx
TELNYX_API_KEY=KEY...

# Zadarma
ZADARMA_API_KEY=...
ZADARMA_API_SECRET=...

# Retell
RETELL_API_KEY=key_...

# PostgreSQL (local on same server)
POSTGRES_HOST=96.47.238.189
POSTGRES_PORT=5432
POSTGRES_DB=telco_warehouse
POSTGRES_USER=telco_sync
POSTGRES_PASSWORD=TelcoSync2024!
```

## Related Files

| Local File | Purpose |
|------------|---------|
| `Telcos/sync/sync_expanded.py` | Source sync script |
| `Telcos/sync/deploy_to_server.py` | Deployment automation |
| `Telcos/.credentials` | Local copy of credentials |
| `Telcos/telco.py` | Telco Manager UI |

---

## Automated Health Monitoring

### Health Check Script
A health check script runs daily at 6 AM and checks:
- Disk usage (warns at >80%)
- Memory usage (warns at >90%)
- PostgreSQL status
- Cron service status
- Telco sync last run time
- Reboot requirements
- Available security updates
- Database size and call count

### Cron Schedule
```
35 3 * * * /usr/bin/python3 /opt/telco_sync/server_health_check.py
```

### Manual Health Check
```bash
ssh root@96.47.238.189 '/usr/bin/python3 /opt/telco_sync/server_health_check.py'
```

### Health Check Log
```bash
ssh root@96.47.238.189 'cat /var/log/telco_health.log'
```

### n8n Workflows (import to n8n)
- `Server_Health_Receiver.json` - Webhook to receive health reports and send alerts
- `Server_Health_Monitor_Complete.json` - Full AWS server monitoring

---

## Version Information

| Component | Current Version | Check Command |
|-----------|----------------|---------------|
| n8n | Check latest | `docker exec n8n-n8n-1 n8n --version` |
| PostgreSQL | 16.x | `psql --version` |
| Ubuntu | 24.04 LTS | `lsb_release -d` |

### Check for n8n Updates
```bash
# Current version
docker exec n8n-n8n-1 n8n --version

# Latest available
curl -s https://api.github.com/repos/n8n-io/n8n/releases/latest | grep tag_name
```

---
*Last updated: 2025-12-04*
