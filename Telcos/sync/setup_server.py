#!/usr/bin/env python3
"""
Setup PostgreSQL on RackNerd server and create telco schema
"""

import paramiko
import time

# Server details
SERVER_IP = "96.47.238.189"
ROOT_PASSWORD = "YiL8J7wuu05uSa6BW1"

def run_ssh_command(ssh, command, timeout=60):
    """Run command and return output"""
    print(f">>> {command}")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace').strip()
    error = stderr.read().decode('utf-8', errors='replace').strip()
    if output:
        # Handle Windows console encoding issues
        try:
            print(output)
        except UnicodeEncodeError:
            print(output.encode('ascii', errors='replace').decode())
    if error and exit_code != 0:
        try:
            print(f"STDERR: {error}")
        except UnicodeEncodeError:
            print(f"STDERR: {error.encode('ascii', errors='replace').decode()}")
    return output, error, exit_code

def main():
    print("=" * 60)
    print("Connecting to RackNerd server...")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER_IP, username='root', password=ROOT_PASSWORD, timeout=30)
        print("[OK] Connected successfully!\n")

        # Check system info
        run_ssh_command(ssh, "uname -a")
        run_ssh_command(ssh, "cat /etc/os-release | head -5")

        # Check if PostgreSQL is installed
        print("\n" + "=" * 60)
        print("Checking PostgreSQL installation...")
        print("=" * 60)

        output, _, code = run_ssh_command(ssh, "which psql")

        if code != 0:
            print("\n[INFO] PostgreSQL not found. Installing...")

            # Detect OS and install
            output, _, _ = run_ssh_command(ssh, "cat /etc/os-release | grep -i 'ID='")

            if 'ubuntu' in output.lower() or 'debian' in output.lower():
                run_ssh_command(ssh, "apt-get update -y", timeout=120)
                run_ssh_command(ssh, "apt-get install -y postgresql postgresql-contrib", timeout=180)
            elif 'centos' in output.lower() or 'rocky' in output.lower() or 'alma' in output.lower():
                run_ssh_command(ssh, "dnf install -y postgresql-server postgresql-contrib", timeout=180)
                run_ssh_command(ssh, "postgresql-setup --initdb", timeout=60)
            else:
                print(f"[WARN] Unknown OS. Trying apt...")
                run_ssh_command(ssh, "apt-get update -y && apt-get install -y postgresql postgresql-contrib", timeout=180)

        # Start PostgreSQL
        print("\n" + "=" * 60)
        print("Starting PostgreSQL service...")
        print("=" * 60)
        run_ssh_command(ssh, "systemctl start postgresql")
        run_ssh_command(ssh, "systemctl enable postgresql")
        run_ssh_command(ssh, "systemctl status postgresql | head -5")

        # Get PostgreSQL version
        run_ssh_command(ssh, "psql --version")

        # Create telco database and user
        print("\n" + "=" * 60)
        print("Creating telco database and user...")
        print("=" * 60)

        # Set password for postgres user and create telco user
        commands = [
            "sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'postgres';\"",
            "sudo -u postgres psql -c \"CREATE USER telco_sync WITH PASSWORD 'TelcoSync2024!';\"",
            "sudo -u postgres psql -c \"CREATE DATABASE telco_warehouse OWNER telco_sync;\"",
            "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE telco_warehouse TO telco_sync;\"",
        ]

        for cmd in commands:
            run_ssh_command(ssh, cmd)

        # Create schema and tables
        print("\n" + "=" * 60)
        print("Creating telco schema and tables...")
        print("=" * 60)

        schema_sql = '''
-- Create schema
CREATE SCHEMA IF NOT EXISTS telco;

-- Grant permissions
GRANT ALL ON SCHEMA telco TO telco_sync;

-- Providers table
CREATE TABLE IF NOT EXISTS telco.providers (
    provider_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    api_type VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Phone numbers table
CREATE TABLE IF NOT EXISTS telco.phone_numbers (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    phone_number VARCHAR(20) NOT NULL,
    phone_number_e164 VARCHAR(20),
    nickname VARCHAR(100),
    status VARCHAR(20),
    city VARCHAR(50),
    monthly_cost DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    retell_agent_id VARCHAR(50),
    retell_agent_name VARCHAR(100),
    metadata JSONB,
    last_synced TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, phone_number)
);

-- Calls/CDR table
CREATE TABLE IF NOT EXISTS telco.calls (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    external_call_id VARCHAR(100),
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    direction VARCHAR(10),
    started_at TIMESTAMPTZ,
    answered_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_seconds INT,
    billable_seconds INT,
    status VARCHAR(30),
    disposition VARCHAR(50),
    hangup_cause VARCHAR(50),
    cost DECIMAL(10,4),
    currency VARCHAR(3) DEFAULT 'USD',
    retell_agent_id VARCHAR(50),
    retell_agent_name VARCHAR(100),
    transcript TEXT,
    sentiment VARCHAR(20),
    has_recording BOOLEAN DEFAULT FALSE,
    recording_url TEXT,
    recording_duration_seconds INT,
    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, external_call_id)
);

-- Recordings table
CREATE TABLE IF NOT EXISTS telco.recordings (
    id SERIAL PRIMARY KEY,
    call_id INT REFERENCES telco.calls(id),
    provider_id INT REFERENCES telco.providers(provider_id),
    external_recording_id VARCHAR(100),
    recording_url TEXT,
    duration_seconds INT,
    file_size_bytes BIGINT,
    format VARCHAR(10),
    s3_bucket VARCHAR(100),
    s3_key VARCHAR(255),
    local_path VARCHAR(255),
    transcription TEXT,
    transcription_confidence DECIMAL(3,2),
    created_at TIMESTAMPTZ,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, external_recording_id)
);

-- Messages table
CREATE TABLE IF NOT EXISTS telco.messages (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    external_message_id VARCHAR(100),
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    direction VARCHAR(10),
    message_type VARCHAR(10),
    body TEXT,
    media_urls JSONB,
    status VARCHAR(30),
    segments INT,
    cost DECIMAL(10,4),
    currency VARCHAR(3) DEFAULT 'USD',
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, external_message_id)
);

-- Balance snapshots
CREATE TABLE IF NOT EXISTS telco.balance_snapshots (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    balance DECIMAL(10,2),
    currency VARCHAR(3),
    credit_limit DECIMAL(10,2),
    snapshot_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sync log
CREATE TABLE IF NOT EXISTS telco.sync_log (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    sync_type VARCHAR(50),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    records_fetched INT,
    records_inserted INT,
    records_updated INT,
    date_range_start TIMESTAMPTZ,
    date_range_end TIMESTAMPTZ,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Retell agents reference
CREATE TABLE IF NOT EXISTS telco.retell_agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) UNIQUE,
    agent_name VARCHAR(100),
    voice_id VARCHAR(50),
    language VARCHAR(10),
    total_calls INT,
    total_minutes DECIMAL(10,2),
    avg_duration_seconds INT,
    last_synced TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert providers
INSERT INTO telco.providers (name, api_type) VALUES
    ('zadarma', 'rest'),
    ('telnyx', 'rest'),
    ('retell', 'sdk')
ON CONFLICT (name) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_calls_started_at ON telco.calls(started_at);
CREATE INDEX IF NOT EXISTS idx_calls_from_number ON telco.calls(from_number);
CREATE INDEX IF NOT EXISTS idx_calls_to_number ON telco.calls(to_number);
CREATE INDEX IF NOT EXISTS idx_calls_provider_date ON telco.calls(provider_id, started_at);

-- Grant permissions on all tables
GRANT ALL ON ALL TABLES IN SCHEMA telco TO telco_sync;
GRANT ALL ON ALL SEQUENCES IN SCHEMA telco TO telco_sync;
'''

        # Write SQL to temp file and execute
        run_ssh_command(ssh, f"cat > /tmp/telco_schema.sql << 'EOSQL'\n{schema_sql}\nEOSQL")
        run_ssh_command(ssh, "sudo -u postgres psql -d telco_warehouse -f /tmp/telco_schema.sql")

        # Configure PostgreSQL to accept remote connections
        print("\n" + "=" * 60)
        print("Configuring PostgreSQL for remote access...")
        print("=" * 60)

        # Find pg_hba.conf location
        output, _, _ = run_ssh_command(ssh, "sudo -u postgres psql -t -c \"SHOW hba_file;\"")
        hba_file = output.strip()
        print(f"pg_hba.conf location: {hba_file}")

        output, _, _ = run_ssh_command(ssh, "sudo -u postgres psql -t -c \"SHOW config_file;\"")
        conf_file = output.strip()
        print(f"postgresql.conf location: {conf_file}")

        # Add remote access rule
        run_ssh_command(ssh, f"echo 'host    telco_warehouse    telco_sync    0.0.0.0/0    md5' >> {hba_file}")

        # Configure listen_addresses
        run_ssh_command(ssh, f"sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/\" {conf_file}")

        # Restart PostgreSQL
        run_ssh_command(ssh, "systemctl restart postgresql")

        # Check if firewall needs to be configured
        print("\n" + "=" * 60)
        print("Configuring firewall...")
        print("=" * 60)

        # Try ufw first, then firewalld
        run_ssh_command(ssh, "ufw allow 5432/tcp 2>/dev/null || firewall-cmd --permanent --add-port=5432/tcp 2>/dev/null && firewall-cmd --reload 2>/dev/null || iptables -A INPUT -p tcp --dport 5432 -j ACCEPT")

        # Verify setup
        print("\n" + "=" * 60)
        print("Verifying setup...")
        print("=" * 60)

        run_ssh_command(ssh, "sudo -u postgres psql -d telco_warehouse -c '\\dt telco.*'")
        run_ssh_command(ssh, "sudo -u postgres psql -d telco_warehouse -c 'SELECT * FROM telco.providers;'")

        print("\n" + "=" * 60)
        print("[SUCCESS] PostgreSQL setup complete!")
        print("=" * 60)
        print(f"""
Connection Details:
  Host: {SERVER_IP}
  Port: 5432
  Database: telco_warehouse
  User: telco_sync
  Password: TelcoSync2024!
  Schema: telco
""")

    except Exception as e:
        print(f"[ERROR] {e}")
        raise
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
