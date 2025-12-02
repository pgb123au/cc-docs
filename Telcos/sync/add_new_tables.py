#!/usr/bin/env python3
"""
Add new tables for expanded data types
"""

import paramiko

SERVER_IP = "96.47.238.189"
ROOT_PASSWORD = "YiL8J7wuu05uSa6BW1"

def run_ssh_command(ssh, command, timeout=60):
    """Run command and return output"""
    print(f">>> {command[:80]}...")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace').strip()
    error = stderr.read().decode('utf-8', errors='replace').strip()
    if output:
        try:
            print(output)
        except UnicodeEncodeError:
            print(output.encode('ascii', errors='replace').decode())
    if error and exit_code != 0:
        print(f"STDERR: {error}")
    return output, error, exit_code

def main():
    print("=" * 60)
    print("Adding new tables to telco_warehouse...")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER_IP, username='root', password=ROOT_PASSWORD, timeout=30)
        print("[OK] Connected\n")

        schema_sql = '''
-- ============================================================================
-- NEW TABLES FOR EXPANDED DATA TYPES
-- ============================================================================

-- Zadarma SIP Accounts
CREATE TABLE IF NOT EXISTS telco.sip_accounts (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    sip_id VARCHAR(50),
    sip_name VARCHAR(100),
    caller_id VARCHAR(50),
    status VARCHAR(20),
    lines INT,
    metadata JSONB,
    last_synced TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, sip_id)
);

-- Zadarma Voicemail
CREATE TABLE IF NOT EXISTS telco.voicemails (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    external_id VARCHAR(100),
    sip_id VARCHAR(50),
    caller_number VARCHAR(30),
    duration_seconds INT,
    recording_url TEXT,
    received_at TIMESTAMPTZ,
    is_read BOOLEAN DEFAULT FALSE,
    transcription TEXT,
    metadata JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, external_id)
);

-- Zadarma Caller ID Settings
CREATE TABLE IF NOT EXISTS telco.caller_ids (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    sip_id VARCHAR(50),
    caller_id VARCHAR(50),
    name VARCHAR(100),
    is_default BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    last_synced TIMESTAMPTZ,
    UNIQUE(provider_id, sip_id, caller_id)
);

-- Telnyx FQDN Connections (SIP Trunks)
CREATE TABLE IF NOT EXISTS telco.fqdn_connections (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    connection_id VARCHAR(50),
    connection_name VARCHAR(100),
    fqdn VARCHAR(255),
    is_active BOOLEAN,
    transport_protocol VARCHAR(10),
    sip_region VARCHAR(50),
    metadata JSONB,
    last_synced TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, connection_id)
);

-- Telnyx Outbound Voice Profiles
CREATE TABLE IF NOT EXISTS telco.outbound_profiles (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    profile_id VARCHAR(50),
    profile_name VARCHAR(100),
    is_enabled BOOLEAN,
    traffic_type VARCHAR(30),
    service_plan VARCHAR(50),
    daily_spend_limit DECIMAL(10,2),
    metadata JSONB,
    last_synced TIMESTAMPTZ,
    UNIQUE(provider_id, profile_id)
);

-- Telnyx Messaging Profiles
CREATE TABLE IF NOT EXISTS telco.messaging_profiles (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    profile_id VARCHAR(50),
    profile_name VARCHAR(100),
    is_enabled BOOLEAN,
    number_pool_enabled BOOLEAN,
    webhook_url TEXT,
    metadata JSONB,
    last_synced TIMESTAMPTZ,
    UNIQUE(provider_id, profile_id)
);

-- Telnyx SIP Credentials
CREATE TABLE IF NOT EXISTS telco.sip_credentials (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    credential_id VARCHAR(50),
    sip_username VARCHAR(100),
    connection_id VARCHAR(50),
    connection_name VARCHAR(100),
    is_active BOOLEAN,
    created_at_provider TIMESTAMPTZ,
    last_synced TIMESTAMPTZ,
    UNIQUE(provider_id, credential_id)
);

-- Telnyx Number Orders
CREATE TABLE IF NOT EXISTS telco.number_orders (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    order_id VARCHAR(50),
    order_type VARCHAR(30),
    status VARCHAR(30),
    phone_numbers JSONB,
    customer_reference VARCHAR(100),
    requirements_met BOOLEAN,
    ordered_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, order_id)
);

-- Telnyx Porting Orders
CREATE TABLE IF NOT EXISTS telco.porting_orders (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    porting_order_id VARCHAR(50),
    status VARCHAR(30),
    phone_numbers JSONB,
    old_carrier VARCHAR(100),
    port_scheduled_at TIMESTAMPTZ,
    port_completed_at TIMESTAMPTZ,
    metadata JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, porting_order_id)
);

-- Retell Call Analysis (detailed)
CREATE TABLE IF NOT EXISTS telco.call_analysis (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(100) UNIQUE,
    provider_id INT REFERENCES telco.providers(provider_id),
    agent_id VARCHAR(50),
    agent_name VARCHAR(100),
    call_summary TEXT,
    call_sentiment VARCHAR(20),
    user_sentiment VARCHAR(20),
    call_successful BOOLEAN,
    in_voicemail BOOLEAN,
    custom_analysis JSONB,
    latency_stats JSONB,
    raw_analysis JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW()
);

-- Retell Knowledge Bases
CREATE TABLE IF NOT EXISTS telco.knowledge_bases (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    kb_id VARCHAR(50) UNIQUE,
    kb_name VARCHAR(100),
    description TEXT,
    source_count INT,
    last_synced TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Retell LLM Configurations
CREATE TABLE IF NOT EXISTS telco.llm_configs (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    llm_id VARCHAR(50) UNIQUE,
    llm_name VARCHAR(100),
    model VARCHAR(50),
    temperature DECIMAL(3,2),
    agent_id VARCHAR(50),
    agent_name VARCHAR(100),
    metadata JSONB,
    last_synced TIMESTAMPTZ
);

-- Retell Voice Configs
CREATE TABLE IF NOT EXISTS telco.voice_configs (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    voice_id VARCHAR(50) UNIQUE,
    voice_name VARCHAR(100),
    provider_voice VARCHAR(50),
    language VARCHAR(20),
    gender VARCHAR(20),
    accent VARCHAR(50),
    sample_audio_url TEXT,
    metadata JSONB,
    last_synced TIMESTAMPTZ
);

-- Retell Webhook Events
CREATE TABLE IF NOT EXISTS telco.webhook_events (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    event_id VARCHAR(100),
    event_type VARCHAR(50),
    call_id VARCHAR(100),
    agent_id VARCHAR(50),
    payload JSONB,
    received_at TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    UNIQUE(provider_id, event_id)
);

-- Retell Batch Jobs
CREATE TABLE IF NOT EXISTS telco.batch_jobs (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    batch_id VARCHAR(50) UNIQUE,
    batch_name VARCHAR(100),
    agent_id VARCHAR(50),
    agent_name VARCHAR(100),
    status VARCHAR(30),
    total_calls INT,
    completed_calls INT,
    failed_calls INT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB,
    last_synced TIMESTAMPTZ
);

-- Retell Concurrency Stats
CREATE TABLE IF NOT EXISTS telco.concurrency_stats (
    id SERIAL PRIMARY KEY,
    provider_id INT REFERENCES telco.providers(provider_id),
    snapshot_at TIMESTAMPTZ DEFAULT NOW(),
    current_concurrent INT,
    max_concurrent INT,
    calls_in_progress INT,
    metadata JSONB
);

-- Add new columns to existing calls table for transcripts
ALTER TABLE telco.calls ADD COLUMN IF NOT EXISTS full_transcript TEXT;
ALTER TABLE telco.calls ADD COLUMN IF NOT EXISTS transcript_words INT;

-- Add new columns to retell_agents for more detail
ALTER TABLE telco.retell_agents ADD COLUMN IF NOT EXISTS llm_id VARCHAR(50);
ALTER TABLE telco.retell_agents ADD COLUMN IF NOT EXISTS knowledge_base_ids JSONB;
ALTER TABLE telco.retell_agents ADD COLUMN IF NOT EXISTS webhook_url TEXT;
ALTER TABLE telco.retell_agents ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_call_analysis_call_id ON telco.call_analysis(call_id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_call_id ON telco.webhook_events(call_id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_received ON telco.webhook_events(received_at);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON telco.batch_jobs(status);

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA telco TO telco_sync;
GRANT ALL ON ALL SEQUENCES IN SCHEMA telco TO telco_sync;
'''

        # Write SQL to temp file and execute
        run_ssh_command(ssh, f"cat > /tmp/new_tables.sql << 'EOSQL'\n{schema_sql}\nEOSQL")
        run_ssh_command(ssh, "sudo -u postgres psql -d telco_warehouse -f /tmp/new_tables.sql")

        # Verify
        print("\n" + "=" * 60)
        print("Verifying tables...")
        print("=" * 60)
        run_ssh_command(ssh, "sudo -u postgres psql -d telco_warehouse -c '\\dt telco.*'")

        print("\n[SUCCESS] New tables added!")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
