# SIP Connection Optimization Guide

## Overview

This document details the optimized SIP configuration for RetellAI voice agents using Telnyx and Zadarma as telephony providers.

**Last Updated:** 2025-12-04
**Connection:** RetellAI_Reignite_AU
**Connection ID:** `2841159272983692912`

---

## Current Optimized Configuration

### Connection Summary

| Setting | Value | Notes |
|---------|-------|-------|
| **Connection Name** | `RetellAI_Reignite_AU` | Primary production connection |
| **FQDN** | `sip.retellai.com` | RetellAI's SIP server |
| **DNS Record Type** | `SRV` | Enables failover/load balancing |
| **Transport Protocol** | `TCP` | Required by RetellAI (UDP not supported) |
| **SIP Region** | `Australia` | Lowest latency for AU calls |
| **Anchorsite** | `Sydney, Australia` | Media processing location |
| **Localization** | `AU` | Australian number formatting |

### Codec Configuration (Priority Order)

| Priority | Codec | Bandwidth | Quality | Use Case |
|----------|-------|-----------|---------|----------|
| 1 | **OPUS** | 6-510 kbps (adaptive) | Excellent | AI voice agents - adapts to network conditions |
| 2 | **G722** | 64 kbps | HD Voice | High-quality fallback |
| 3 | **G729** | 8 kbps | Good | Low bandwidth situations |

**Why OPUS first?**
- Adaptive bitrate handles variable network conditions
- Telnyx recommends OPUS for Voice AI agents
- Maintains HD quality while being resilient to network issues

### Inbound Settings

| Setting | Value |
|---------|-------|
| ANI Format | `+E.164` |
| DNIS Format | `e164` |
| Routing Method | `sequential` |
| SIP Subdomain | `Retell-Reignite` |
| Compact Headers | `enabled` |

### Outbound Settings

| Setting | Value |
|---------|-------|
| Auth Method | `credential-authentication` |
| Username | `pgb123` |
| Localization | `AU` |
| Voice Profile ID | `2837259546655720867` |
| Instant Ringback | `enabled` |

### Additional Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| DTMF Type | `RFC 2833` | Industry standard for touch-tones |
| Comfort Noise | `enabled` | Fills silence gaps naturally |
| Noise Suppression | `disabled` | Can enable via portal if needed |
| Encrypted Media | `null` | Enable SRTP for compliance if needed |

---

## RetellAI Requirements

### Mandatory Settings (per RetellAI docs)

1. **FQDN**: Must be exactly `sip.retellai.com`
2. **Transport**: TCP (UDP temporarily unsupported)
3. **Codecs**: G722, G729, OPUS (any order)
4. **Number Format**: +E.164

### IP Whitelisting (if required)

RetellAI IP blocks for firewall rules:
- `18.98.16.120/30` (All regions)
- `143.223.88.0/21` (United States only)
- `161.115.160.0/19` (United States only)

---

## Voice Quality Best Practices

### Network Requirements

| Metric | Recommended | Acceptable |
|--------|-------------|------------|
| Latency | < 150ms | < 300ms |
| Jitter | < 30ms | < 50ms |
| Packet Loss | < 1% | < 3% |
| Bandwidth per call | 100 kbps | 64 kbps minimum |

### Quality of Service (QoS)

If you control the network:
1. Prioritize SIP signaling (port 5060)
2. Prioritize RTP media (ports 10000-20000)
3. Use separate VLANs for voice traffic if possible

### Troubleshooting Audio Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Choppy audio | Network jitter | Enable jitter buffer, check QoS |
| One-way audio | NAT/firewall issue | Check RTP port forwarding |
| Echo | Acoustic feedback | Enable echo cancellation |
| Robot voice | Packet loss | Check network stability |
| Delayed audio | High latency | Use closer SIP region |

---

## Change Log

### 2025-12-04: Codec Optimization
- **Changed**: Codec priority from `G722, G729, OPUS` to `OPUS, G722, G729`
- **Reason**: OPUS's adaptive bitrate is better suited for AI voice agents
- **Reference**: Telnyx recommendation for Voice AI applications

### 2025-12-02: Initial Setup
- Created FQDN connection `RetellAI_Reignite_AU`
- Configured for Australia region
- Set up credential authentication

---

## API Reference

### View Current Configuration

```bash
curl -X GET "https://api.telnyx.com/v2/fqdn_connections/2841159272983692912" \
  -H "Authorization: Bearer $TELNYX_API_KEY"
```

### Update Codec Order

```bash
curl -X PATCH "https://api.telnyx.com/v2/fqdn_connections/2841159272983692912" \
  -H "Authorization: Bearer $TELNYX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"inbound":{"codecs":["OPUS","G722","G729"]}}'
```

### View FQDNs

```bash
curl -X GET "https://api.telnyx.com/v2/fqdns" \
  -H "Authorization: Bearer $TELNYX_API_KEY"
```

---

## Related Documentation

| Document | Location |
|----------|----------|
| Telnyx Reference | `Telcos/Telnyx/TELNYX_REFERENCE.md` |
| Telco API Capabilities | `Telcos/TELCO_API_CAPABILITIES.md` |
| RetellAI Webhooks | `n8n/Webhooks Docs/RETELLAI_WEBHOOKS_CURRENT.md` |

---

## External References

- [RetellAI Telnyx Integration](https://docs.retellai.com/deploy/telnyx)
- [RetellAI Custom Telephony](https://docs.retellai.com/deploy/custom-telephony)
- [Telnyx Audio and Codecs](https://support.telnyx.com/en/articles/3192298-audio-and-codecs)
- [Telnyx Voice AI HD Codecs](https://telnyx.com/resources/conversational-ai-hd-voice-codecs)

---

## Zadarma Configuration

### Overview

Zadarma numbers connect to RetellAI via LiveKit's SIP infrastructure (`5t4n6j0wnrl.sip.livekit.cloud`). LiveKit is RetellAI's underlying real-time communication platform.

**Note:** Zadarma has more limited codec options compared to Telnyx - primarily G.711 (alaw/ulaw).

### Phone Numbers & Expiry Dates

| Number | City | Status | SIP Destination | Expiry Date | Auto-Renew |
|--------|------|--------|-----------------|-------------|------------|
| +61288800226 | Sydney | Active | LiveKit (RetellAI) | 2026-09-18 | Yearly |
| +61399997398 | Melbourne | Active | LiveKit (RetellAI) | 2025-12-26 | Monthly |
| +61288800208 | Sydney | Active | LiveKit (RetellAI) | 2025-12-27 | Monthly |
| +61731068880 | Brisbane | Active | LiveKit (RetellAI) | 2026-06-14 | Yearly |
| +61399997351 | Melbourne | Active | LiveKit (RetellAI) | 2026-06-14 | Yearly |
| +61399980489 | Melbourne | Active | Zadarma SIP (818506) | 2026-06-14 | Yearly |
| +61288805883 | Sydney | Active | Zadarma SIP (06557) | 2026-07-05 | Yearly |

### Zadarma SIP Settings

| Setting | Value | Notes |
|---------|-------|-------|
| **SIP Server** | `sip.zadarma.com` | Primary server |
| **Port (Standard)** | `5060` | UDP |
| **Port (Secure)** | `5061` | TLS encrypted |
| **Codecs** | G.711 alaw, G.711 ulaw | Limited options |
| **Channels per Number** | 3 | Concurrent calls |
| **Monthly Cost** | $3 USD per number | Total: ~$21/month |

### LiveKit Integration (for RetellAI)

Numbers routed to RetellAI use LiveKit's SIP endpoint:
- **FQDN**: `5t4n6j0wnrl.sip.livekit.cloud`
- **Format**: `+{number}@5t4n6j0wnrl.sip.livekit.cloud`

### Optimization Options

| Setting | Current | Recommendation | How to Change |
|---------|---------|----------------|---------------|
| **Transport** | UDP | Consider TLS (port 5061) | Zadarma Portal |
| **Encryption** | None | Enable SRTP if needed | Zadarma Portal |
| **Codec** | G.711 | Limited - no OPUS/G722 | N/A (Zadarma limitation) |

### Zadarma vs Telnyx Comparison

| Feature | Telnyx | Zadarma |
|---------|--------|---------|
| HD Codecs (OPUS/G722) | ✅ Yes | ❌ No |
| API Codec Control | ✅ Full | ❌ Limited |
| TLS/SRTP | ✅ Yes | ✅ Yes (manual) |
| Regional Servers | ✅ Sydney | ⚠️ Generic |
| Cost (AU number) | ~$2-3/mo | $3/mo |
| Best For | Primary AI agents | Backup/overflow |

### Recommendation

**Use Telnyx for primary RetellAI production numbers** due to:
- OPUS codec support (adaptive, HD quality)
- Sydney-based media servers (lower latency)
- Full API control over settings

**Use Zadarma for:**
- Backup numbers
- Cost-effective additional coverage
- Numbers already established with clients

---

## Zadarma API Reference

### List Phone Numbers with Expiry

```bash
curl -s "https://api.zadarma.com/v1/direct_numbers/" \
  -H "Authorization: {api_key}:{signature}"
```

### List SIP Accounts

```bash
curl -s "https://api.zadarma.com/v1/sip/" \
  -H "Authorization: {api_key}:{signature}"
```

See `Telcos/Zadarma/ZADARMA_REFERENCE.md` for full API documentation.
