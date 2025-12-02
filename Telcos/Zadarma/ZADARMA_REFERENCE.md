# Zadarma Reference

## API Credentials

| Item | Value |
|------|-------|
| API Key | See `Telcos/.credentials` (git-ignored) |
| API Secret | See `Telcos/.credentials` (git-ignored) |
| Portal | https://my.zadarma.com |
| API Base | https://api.zadarma.com |

**Rate Limits:**
- Common: 100 requests/minute
- Statistics: 10 requests/minute

---

## Account Summary

| Item | Value |
|------|-------|
| Balance | $73.89 USD |
| Total Numbers | 7 |
| Monthly Cost | ~$21 USD |

---

## Virtual Phone Numbers

### +61 3 9999 7398 (Melbourne)
| Setting | Value |
|---------|-------|
| Number | `+61399997398` |
| City | Melbourne |
| Status | Active |
| SIP | `+61399997398@5t4n6j0wnrl.sip.livekit.cloud` |
| Channels | 3 |
| Monthly Fee | $3 USD |

### +61 2 8880 0208 (Sydney)
| Setting | Value |
|---------|-------|
| Number | `+61288800208` |
| City | Sydney |
| Status | Active |
| SIP | `+61399997398@5t4n6j0wnrl.sip.livekit.cloud` |
| Channels | 3 |
| Monthly Fee | $3 USD |

### +61 3 9998 0489 (Melbourne)
| Setting | Value |
|---------|-------|
| Number | `+61399980489` |
| City | Melbourne |
| Status | Active |
| SIP | `818506` |
| Channels | 3 |
| Monthly Fee | $3 USD |

### +61 7 3106 8880 (Brisbane)
| Setting | Value |
|---------|-------|
| Number | `+61731068880` |
| City | Brisbane |
| Status | Active |
| SIP | `+61731068880@5t4n6j0wnrl.sip.livekit.cloud` |
| Channels | 3 |
| Monthly Fee | $3 USD |

### +61 3 9999 7351 (Melbourne)
| Setting | Value |
|---------|-------|
| Number | `+61399997351` |
| City | Melbourne |
| Status | Active |
| SIP | `+61399997351@5t4n6j0wnrl.sip.livekit.cloud` |
| Channels | 3 |
| Monthly Fee | $3 USD |

### +61 2 8880 5883 (Sydney)
| Setting | Value |
|---------|-------|
| Number | `+61288805883` |
| City | Sydney |
| Status | Active |
| SIP | `06557` |
| Channels | 3 |
| Monthly Fee | $3 USD |

### +61 2 8880 0226 (Sydney - Reignite)
| Setting | Value |
|---------|-------|
| Number | `+61288800226` |
| City | Sydney |
| Status | Active |
| SIP | `+61288800226@5t4n6j0wnrl.sip.livekit.cloud` |
| Channels | 3 |
| Monthly Fee | $3 USD |

---

## SIP Accounts

| SIP ID | Display Name |
|--------|--------------|
| 932808 | SIP |
| 818506 | SIP |
| 829204 | SIP-61399997398 |
| 307641 | SIP-61399997351 |
| 06557 | SIP-61399997351 |
| 218697 | SIP-Reignite-61288800226 |

---

## LiveKit Integration

Several numbers are routed to LiveKit SIP:
- Domain: `5t4n6j0wnrl.sip.livekit.cloud`

---

## API Quick Reference

### Authentication

Zadarma uses HMAC-SHA1 signature authentication:

```python
# Signature generation
sign_string = method + params_string + md5(params_string)
hex_signature = hmac.sha1(sign_string, secret_key).hexdigest()
signature = base64.encode(hex_signature)

# Header format
Authorization: {api_key}:{signature}
```

### Common Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Get Balance | GET | `/v1/info/balance/` |
| List SIP Accounts | GET | `/v1/sip/` |
| List Phone Numbers | GET | `/v1/direct_numbers/` |
| Get Call Statistics | GET | `/v1/statistics/` |
| Available Countries | GET | `/v1/direct_numbers/countries/` |

### Example: Get Balance
```bash
# Use the Python script
cd C:\Users\peter\Downloads\CC\Telcos\Zadarma
python get_zadarma_numbers.py
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `get_zadarma_numbers.py` | Fetch account info, SIP accounts, and phone numbers |

---

## Number Summary by City

| City | Count | Numbers |
|------|-------|---------|
| Sydney | 3 | +61288800208, +61288805883, +61288800226 |
| Melbourne | 3 | +61399997398, +61399980489, +61399997351 |
| Brisbane | 1 | +61731068880 |

---

**Last Updated:** 2025-12-02
