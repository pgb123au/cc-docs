# SIP Connection Optimization Guide

## Overview

This document details the optimized SIP configuration for RetellAI voice agents using Telnyx as the telephony provider.

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
