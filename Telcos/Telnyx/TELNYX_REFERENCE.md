# Telnyx Reference

## API Credentials

| Item | Value |
|------|-------|
| API Key | See `Telcos/.credentials` (git-ignored) |
| Portal | https://portal.telnyx.com |

---

## SIP Connections

### RetellAI_Reignite_AU (Primary)

| Setting | Value |
|---------|-------|
| Connection ID | `2841159272983692912` |
| Connection Name | `RetellAI_Reignite_AU` |
| Type | FQDN Connection |
| Status | Active |

**Inbound Settings:**
| Setting | Value |
|---------|-------|
| FQDN | `sip.retellai.com` |
| DNS Record Type | SRV |
| Transport | TCP |
| SIP Region | Australia |
| ANI Format | +E.164 |
| Codecs | G722, G729, OPUS |

**Outbound Settings:**
| Setting | Value |
|---------|-------|
| Auth Method | Credentials |
| Username | `pgb123` |
| Password | `280.Army.telnyx` |
| Localization | AU |
| Voice Profile ID | `2837259546655720867` |

**Webhook:**
- Event URL: `https://auto.yr.com.au/webhook/reignite-retell/email-call-summary`

---

### Forward Only (Secondary)

| Setting | Value |
|---------|-------|
| Connection ID | `2837259516800664991` |
| Connection Name | `Forward Only` |
| Type | Credential Connection |
| Username | `qx9tw63we6ds` |
| Password | `pw6Av5bEzdn6` |

---

## Phone Numbers

### +61 2 4062 0999 (NSW Office)

| Setting | Value |
|---------|-------|
| Phone Number | `+61240620999` |
| Number ID | `2838129041175741675` |
| Status | Active |
| Type | Local (AU) |
| Connection | `RetellAI_Reignite_AU` |
| Purchased | 2025-11-27 |

**Retell Integration:**
| Setting | Value |
|---------|-------|
| Inbound Agent | `agent_9247a7e76be283256c249b866f` |
| Outbound Agent | `agent_9247a7e76be283256c249b866f` |
| Nickname | `Reignite NSW Office` |

---

## API Quick Reference

### Authentication
```bash
-H "Authorization: Bearer $TELNYX_API_KEY"
```

### Common Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| List FQDN Connections | GET | `/v2/fqdn_connections` |
| List Credential Connections | GET | `/v2/credential_connections` |
| List Phone Numbers | GET | `/v2/phone_numbers` |
| Get Phone Number | GET | `/v2/phone_numbers/{phone_number}` |
| List FQDNs | GET | `/v2/fqdns` |
| Update FQDN | PATCH | `/v2/fqdns/{id}` |

### Example: Get All Phone Numbers
```bash
curl -s -X GET "https://api.telnyx.com/v2/phone_numbers" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json"
```

---

## Retell Integration Setup

For a Telnyx number to work with Retell:

### Telnyx Side
1. Create FQDN Connection with:
   - FQDN: `sip.retellai.com`
   - DNS: SRV
   - Transport: TCP
   - Codecs: G722, G729, OPUS
2. Set outbound credentials
3. Assign phone number to connection

### Retell Side
1. Import number via API or dashboard
2. Set termination URI: `sip.telnyx.com`
3. Provide SIP credentials (username/password)
4. Assign inbound/outbound agents

---

## Troubleshooting

### Inbound calls not reaching Retell
- Check FQDN is exactly `sip.retellai.com` (not `sip.retell.com`)
- Verify phone number is assigned to correct connection
- Check connection is Active

### Outbound calls failing
- Verify credentials match between Telnyx and Retell
- Check outbound voice profile is assigned
- Verify number has outbound agent in Retell

---

**Last Updated:** 2025-12-02
