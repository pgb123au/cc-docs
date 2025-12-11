#!/bin/bash
# API Monitor daily check
cd /opt/telco_sync/api_monitor
export $(grep -v '^#' /opt/telco_sync/.credentials | grep -v '^$' | xargs) 2>/dev/null
/opt/telco_sync/api_monitor/venv/bin/python api_monitor.py >> /var/log/api_monitor.log 2>&1
