# Retell API Keys for Telco Analysis

## Workspaces

| Workspace | API Key | Date Range | Notes |
|-----------|---------|------------|-------|
| **Telco DB Sync** | `key_b8d6bd5512827f71f1f1202e06a4` | May 2025+ | Yes AI outbound campaign, 26K+ calls |
| **Primary (Reignite)** | See `C:\Users\peter\Downloads\Retell_API_Key.txt` | Oct 2025+ | Current production |

## Usage

```python
# Telco DB Sync (old Yes AI campaign)
TELCO_API_KEY = 'key_b8d6bd5512827f71f1f1202e06a4'

# Primary (Reignite)
PRIMARY_API_KEY = open('C:/Users/peter/Downloads/Retell_API_Key.txt').read().strip()
```

## Important

- The **Telco DB Sync** workspace contains the original outbound campaign data
- Phone numbers for appointment contacts are in this workspace
- Always use the correct workspace API key when querying historical data
