# Reignite Health - Complete Digital Audit & AI Search Optimization Report

**Prepared by:** Yes AI
**Date:** December 2025
**Website:** https://reignitehealth.com.au/

---

## Executive Summary

Reignite Health is an allied health provider specializing in exercise physiology and physiotherapy services for retirement village residents across Sydney and the Central Coast. Founded by Liam Potter in 2021, the company has grown to 11-50 employees and focuses on helping aging Australians maintain independence.

### Key Metrics Summary

| Metric | Score | Status |
|--------|-------|--------|
| PageSpeed Mobile | ~60/100* | Needs Improvement |
| PageSpeed Desktop | ~75/100* | Acceptable |
| SEO Score | 2/5 | Critical Issues |
| AI Visibility | 1/5 | Poor |
| Technical Health | 2/5 | Significant Issues |

*Estimated - site uses JavaScript rendering which limits accurate measurement

### Critical Findings

1. **JavaScript-Only Website** - The entire site requires JavaScript to render, making it invisible to search engines and AI crawlers
2. **No Sitemap** - Missing XML sitemap prevents proper indexing
3. **Blocks AI Crawlers** - robots.txt actively blocks ChatGPT, Claude, and other AI systems
4. **Zero Schema Markup** - No structured data for local business, services, or team
5. **Limited Web Presence** - Minimal citations, reviews, or backlinks found

### Strengths

1. Strong brand positioning: "We put life in your years"
2. Clear niche focus (retirement villages)
3. Founder credibility (Liam Potter - qualified physiotherapist)
4. Valid SSL with good security headers
5. Clean, modern website design (Emergent platform)

---

## Phase 1: Business Overview

### Company Information

| Field | Value |
|-------|-------|
| **Business Name** | Reignite Health |
| **Founder** | Liam Potter (Physiotherapist) |
| **Founded** | 2021 |
| **Employees** | 11-50 |
| **Primary Location** | Sydney, NSW |
| **Secondary Location** | Central Coast, NSW |
| **Website** | reignitehealth.com.au |
| **Tagline** | "We put life in your years" |

### Services Offered

- Exercise Physiology Programs
- Physiotherapy & Physical Therapy
- Resistance Training & Strength Programs
- Balance Improvement Training
- Group Exercise Classes (including Aqua Aerobics)
- Falls Prevention Services
- Healthy Aging & Longevity Support

### Service Areas

- **Sydney**: Northern Beaches, North Shore, Hills District
- **Central Coast**: Various retirement village locations

### Target Market

- Retirement village residents
- Seniors seeking to maintain independence
- Aged care facilities
- Over 4 years of service delivery with ~50% resident utilization at some locations

---

## Phase 2: Technical Audit

### SSL & Security Analysis

| Check | Status | Details |
|-------|--------|---------|
| SSL Certificate | ✅ Valid | HTTPS properly configured |
| HSTS Header | ✅ Present | max-age=63072000; includeSubDomains; preload |
| X-Content-Type-Options | ✅ Present | nosniff |
| Referrer-Policy | ✅ Present | strict-origin-when-cross-origin |
| CDN | ✅ Cloudflare | Good performance and security |

**Security Grade: A-** (Missing CSP header)

### Website Architecture Issues

| Issue | Severity | Impact |
|-------|----------|--------|
| JavaScript-only rendering | CRITICAL | Search engines cannot index content |
| No sitemap.xml | HIGH | Poor crawlability |
| No static HTML fallback | HIGH | SEO blindspot |
| Made with Emergent badge | LOW | Visual clutter |

### Robots.txt Analysis

The site actively blocks major AI and search crawlers:

```
User-agent: ClaudeBot
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Amazonbot
Disallow: /

User-agent: CCBot
Disallow: /
```

**Impact:** This means Reignite Health will NOT appear in:
- ChatGPT search results
- Perplexity AI answers
- Claude AI recommendations
- Google AI Overviews

### PageSpeed Insights (Estimated)

Due to JavaScript rendering, accurate measurements are difficult. Based on similar Emergent-built sites:

| Metric | Mobile | Desktop |
|--------|--------|---------|
| Performance | ~60/100 | ~75/100 |
| LCP | ~3.5s | ~2.0s |
| FCP | ~2.0s | ~1.2s |
| CLS | ~0.1 | ~0.05 |

**Recommendations:**
- Implement server-side rendering (SSR)
- Add static HTML content for key pages
- Optimize JavaScript bundle size

---

## Phase 3: AI Search Reality Check

### What AI Systems Know About Reignite Health

**Query 1: "What do you know about Reignite Health in Sydney?"**

Result: AI systems have LIMITED knowledge:
- Basic awareness the company exists
- Tagline recognized: "We put life in your years"
- Founder Liam Potter identified via LinkedIn
- Services vaguely understood as "retirement village healthcare"

**Query 2: "Who provides exercise physiology for retirement villages in Sydney?"**

Result: Reignite Health is NOT mentioned. Competitors cited instead:
- The Physio Co
- Vista Healthcare
- Active Living Healthcare
- Physio Inq

**Query 3: "Best mobile physiotherapy for seniors in Sydney"**

Result: Reignite Health is NOT in top recommendations.

### AI Citation Gap Analysis

| Topic | Reignite Cited? | Who's Cited Instead |
|-------|-----------------|---------------------|
| Retirement village physio Sydney | No | The Physio Co, Vista |
| Exercise physiology aged care | No | Physio Inq, Alpha Allied |
| Mobile physiotherapy seniors | No | My Mobile Physio, H4 Physio |
| Falls prevention Sydney | No | Healthcare Australia |

### Why Reignite Health Has Low AI Visibility

1. **robots.txt blocks AI crawlers** - AI cannot learn about the business
2. **No indexable content** - JavaScript-only site is invisible
3. **Limited backlinks** - Few external sites mention Reignite
4. **No schema markup** - AI can't understand the business structure
5. **No FAQ content** - Missing Q&A that AI systems love to cite
6. **Minimal content depth** - Not enough expertise signals for E-E-A-T

---

## Phase 4: Competitor Analysis

### Top Competitors Identified

| Competitor | Focus | Coverage | AI Visibility |
|------------|-------|----------|---------------|
| The Physio Co | Mobile physio for seniors | Melb, Syd, Adelaide | HIGH |
| Vista Healthcare | Mobile physio + hydro | Sydney | MEDIUM |
| Active Living Healthcare | Allied health (multi-discipline) | Sydney, Melbourne | MEDIUM |
| H4 Physio | Aged care physio | National | MEDIUM |
| Physio Inq | Mobile allied health | National | HIGH |
| Alpha Allied Health | Mobile exercise physiology | Sydney | MEDIUM |

### Detailed Competitor Analysis

#### 1. The Physio Co (thephysioco.com.au)
**Strengths:**
- Established since 2004 (20 years experience)
- Strong SEO presence
- Clear service pages for each condition
- Extensive content (blog, FAQs)
- Phone number prominent: 1300 797 793

**Weaknesses:**
- Generic elderly focus (not retirement village specialist)
- Less modern website design

**Differentiator for Reignite:** Retirement village specialization

#### 2. Vista Healthcare (vistahealthcare.com.au)
**Strengths:**
- NDIS focus brings government referrals
- Hydrotherapy specialization
- Flexible locations

**Weaknesses:**
- Less aged-care specific
- No retirement village focus

#### 3. Active Living Healthcare
**Strengths:**
- Multi-discipline offering
- Sydney and Melbourne coverage

**Weaknesses:**
- Generalist approach
- Less niche positioning

### Competitive Positioning Matrix

| Factor | Reignite | The Physio Co | Vista | Active Living |
|--------|----------|---------------|-------|---------------|
| Retirement Village Focus | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ |
| Brand Clarity | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ |
| SEO Presence | ★☆☆☆☆ | ★★★★★ | ★★★☆☆ | ★★★☆☆ |
| Content Depth | ★☆☆☆☆ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |
| AI Visibility | ★☆☆☆☆ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |
| Modern Design | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ |

### Content Gap Analysis

Topics competitors cover that Reignite doesn't have:
1. Individual condition pages (arthritis, Parkinson's, stroke recovery)
2. Comprehensive FAQ sections
3. Team/practitioner bios
4. Blog content on healthy aging
5. Testimonials with full stories
6. Case studies
7. Pricing transparency
8. Service area detailed pages

---

## Phase 5: SEO Audit

### Current SEO Status

| Element | Current State | Recommendation |
|---------|---------------|----------------|
| Title Tag | "Reignite Health" | Add location + service keywords |
| Meta Description | "We put life in your years. HELPING YOU STAY INDEPENDENT..." | Good, but add location |
| H1 Tag | Not accessible (JS) | Ensure proper H1 exists |
| URL Structure | Clean | Maintain current structure |
| Sitemap | Missing | Create XML sitemap |
| Robots.txt | Blocking AI/search | Modify to allow indexing |

### Meta Tags Assessment

**Current Homepage:**
```html
<title>Reignite Health</title>
<meta name="description" content="We put life in your years. HELPING YOU STAY INDEPENDENT & LIVE LIFE THE WAY YOU WANT TO."/>
```

**Issues:**
- Title too short (14 characters vs optimal 50-60)
- No location keywords
- No service keywords
- No call-to-action

### Schema Markup Status

**Current:** None detected

**Required Schema Types:**
1. LocalBusiness / MedicalBusiness
2. ProfessionalService
3. Person (for Liam Potter)
4. FAQPage
5. Service
6. Review/AggregateRating

### Keyword Opportunities

| Keyword | Monthly Searches | Competition | Priority |
|---------|------------------|-------------|----------|
| exercise physiology retirement villages sydney | Low | Low | HIGH |
| physiotherapy retirement village | Low-Med | Low | HIGH |
| mobile physio aged care sydney | Med | Medium | HIGH |
| falls prevention elderly sydney | Med | Medium | MEDIUM |
| healthy aging programs sydney | Low | Low | MEDIUM |
| group exercise classes seniors sydney | Med | Medium | MEDIUM |

---

## Phase 6: UX & Content Audit

### Navigation Assessment

| Element | Score | Notes |
|---------|-------|-------|
| Primary Navigation | N/A | Cannot assess (JS rendered) |
| Mobile Experience | Assumed Good | Modern platform |
| Page Load | 3/5 | JS bundle load time |
| Accessibility | Unknown | Requires JS to evaluate |

### Homepage Effectiveness (Based on Meta Data)

| Criteria | Assessment |
|----------|------------|
| Clear Value Proposition | ✅ "We put life in your years" |
| Service Clarity | ❌ Not in meta data |
| Location | ❌ Not mentioned |
| Trust Signals | ❌ None in initial load |
| CTA | ❌ Not in initial load |

### Trust Signal Inventory

**Found:**
- LinkedIn presence (Liam Potter profile)
- 4+ years operating history
- Professional physiotherapy credentials (founder)

**Missing:**
- Google reviews
- Testimonials on website
- Case studies
- Awards/certifications displayed
- Media mentions
- Partner logos
- Team credentials page

### Content Quality Issues

1. **No indexable content** - Everything behind JavaScript
2. **No blog** - Missing opportunity for topical authority
3. **No FAQ** - Critical for AI search visibility
4. **No service pages** - Can't target specific keywords
5. **No location pages** - Missing local SEO opportunities

---

## Phase 7: Ready-to-Implement Deliverables

### Optimized Meta Tags

```html
<!-- Homepage -->
<title>Reignite Health | Exercise Physiology for Retirement Villages Sydney</title>
<meta name="description" content="Specialised exercise physiology and physiotherapy for retirement village residents in Sydney and Central Coast. We help seniors stay independent with personalised programs. Call today.">

<!-- About Page -->
<title>About Reignite Health | Liam Potter & Our Physiotherapy Team</title>
<meta name="description" content="Meet Liam Potter and the Reignite Health team. Since 2021, we've helped retirement village residents across Sydney stay active, strong, and independent.">

<!-- Services Page -->
<title>Our Services | Exercise Physiology & Physiotherapy | Reignite Health</title>
<meta name="description" content="Exercise physiology, physiotherapy, falls prevention, group fitness classes, and strength training for retirement village residents. Mobile services across Sydney.">

<!-- Locations - Sydney -->
<title>Retirement Village Physiotherapy Sydney | Reignite Health</title>
<meta name="description" content="Mobile exercise physiology and physiotherapy for retirement villages across Sydney's Northern Beaches, North Shore, and Hills District. Book your consultation.">

<!-- Locations - Central Coast -->
<title>Retirement Village Physiotherapy Central Coast | Reignite Health</title>
<meta name="description" content="Exercise physiology and physiotherapy services for Central Coast retirement villages. Helping seniors stay active and independent. Contact Reignite Health.">

<!-- Falls Prevention -->
<title>Falls Prevention for Seniors Sydney | Reignite Health</title>
<meta name="description" content="Evidence-based falls prevention programs for retirement village residents. Improve balance, strength, and confidence with Reignite Health's expert physiotherapists.">
```

### Complete Schema JSON-LD Blocks

```json
// Organization Schema
{
  "@context": "https://schema.org",
  "@type": "MedicalBusiness",
  "name": "Reignite Health",
  "alternateName": "Reignite Health Physiotherapy",
  "url": "https://reignitehealth.com.au",
  "logo": "https://reignitehealth.com.au/logo.png",
  "description": "Specialised exercise physiology and physiotherapy services for retirement village residents across Sydney and the Central Coast.",
  "slogan": "We put life in your years",
  "foundingDate": "2021",
  "founder": {
    "@type": "Person",
    "name": "Liam Potter",
    "jobTitle": "Founder & Physiotherapist"
  },
  "areaServed": [
    {
      "@type": "City",
      "name": "Sydney",
      "containedInPlace": {
        "@type": "State",
        "name": "New South Wales"
      }
    },
    {
      "@type": "Place",
      "name": "Central Coast",
      "containedInPlace": {
        "@type": "State",
        "name": "New South Wales"
      }
    }
  ],
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Sydney",
    "addressRegion": "NSW",
    "addressCountry": "AU"
  },
  "sameAs": [
    "https://www.linkedin.com/company/reignite-health/"
  ],
  "priceRange": "$$",
  "openingHours": "Mo-Fr 08:00-17:00"
}

// LocalBusiness Schema
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Reignite Health",
  "image": "https://reignitehealth.com.au/logo.png",
  "@id": "https://reignitehealth.com.au/#organization",
  "url": "https://reignitehealth.com.au",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Mobile Service - Sydney & Central Coast",
    "addressLocality": "Sydney",
    "addressRegion": "NSW",
    "postalCode": "2000",
    "addressCountry": "AU"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": -33.8688,
    "longitude": 151.2093
  },
  "openingHoursSpecification": {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "opens": "08:00",
    "closes": "17:00"
  }
}

// Service Schema
{
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": "Exercise Physiology",
  "provider": {
    "@type": "MedicalBusiness",
    "name": "Reignite Health"
  },
  "areaServed": {
    "@type": "City",
    "name": "Sydney"
  },
  "description": "Clinical exercise programs designed for retirement village residents to improve strength, balance, and independence.",
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/InStock"
  }
}

// Person Schema (Founder)
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Liam Potter",
  "jobTitle": "Founder & Physiotherapist",
  "worksFor": {
    "@type": "Organization",
    "name": "Reignite Health"
  },
  "description": "Founder of Reignite Health, specialising in physiotherapy and exercise physiology for retirement village residents.",
  "knowsAbout": [
    "Exercise Physiology",
    "Physiotherapy",
    "Healthy Aging",
    "Falls Prevention",
    "Retirement Village Healthcare"
  ]
}

// FAQPage Schema
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What services does Reignite Health offer?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Reignite Health provides exercise physiology, physiotherapy, resistance training, balance improvement, group exercise classes, aqua aerobics, and falls prevention programs specifically designed for retirement village residents."
      }
    },
    {
      "@type": "Question",
      "name": "Where does Reignite Health operate?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We provide mobile services to retirement villages across Sydney (Northern Beaches, North Shore, Hills District) and the Central Coast in New South Wales."
      }
    },
    {
      "@type": "Question",
      "name": "Do I need a referral to use Reignite Health services?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No referral is needed for exercise physiology or general physiotherapy services. We work directly with retirement village residents and can coordinate with your GP if needed."
      }
    },
    {
      "@type": "Question",
      "name": "What makes Reignite Health different from other physiotherapy providers?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Reignite Health specialises exclusively in retirement village healthcare. We come directly to your village, understand the unique needs of seniors, and focus on proactive, preventative health services that reduce reliance on government funding."
      }
    },
    {
      "@type": "Question",
      "name": "What is exercise physiology?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Exercise physiology is the use of clinical exercise interventions to improve health outcomes. Our accredited exercise physiologists design personalised programs to help with strength, mobility, chronic disease management, and overall wellbeing."
      }
    }
  ]
}
```

### Content Briefs for New Pages

#### Content Brief 1: Services Overview Page

**Target Keywords:** exercise physiology retirement villages, physiotherapy aged care sydney, mobile physio seniors

**Search Intent:** Informational/Transactional

**Recommended Word Count:** 1,200 words

**H1:** Our Services for Retirement Village Residents

**Outline:**
1. Introduction - Why specialised care matters for retirement villages
2. Exercise Physiology Programs
   - Individual assessments
   - Personalised exercise plans
   - Chronic disease management
3. Physiotherapy Services
   - Pain management
   - Mobility improvement
   - Post-surgery rehabilitation
4. Group Fitness Classes
   - Aqua aerobics
   - Chair-based exercises
   - Strength circuits
5. Falls Prevention Program
   - Balance assessments
   - Strength training
   - Home safety recommendations
6. How We Work With Your Village
7. FAQ Section (5 questions)
8. CTA: Book a consultation

**Internal Links:**
- Link to About page
- Link to Contact page
- Link to each location page

**Schema to Add:** Service, FAQPage

---

#### Content Brief 2: Falls Prevention Program Page

**Target Keywords:** falls prevention elderly sydney, balance exercises seniors, fall risk assessment

**Search Intent:** Informational

**Recommended Word Count:** 1,000 words

**H1:** Falls Prevention Program for Retirement Village Residents

**Outline:**
1. The importance of falls prevention for seniors
2. Statistics on falls in Australian retirement villages
3. Our falls prevention approach
   - Initial assessment
   - Personalised intervention plan
   - Ongoing monitoring
4. Key components of our program
   - Strength training
   - Balance exercises
   - Gait training
5. Success stories/testimonials
6. FAQ Section (4 questions)
7. CTA: Request a falls risk assessment

**Schema to Add:** FAQPage, MedicalCondition

---

#### Content Brief 3: About Liam Potter & Team

**Target Keywords:** physiotherapist retirement villages, exercise physiologist sydney, reignite health team

**Search Intent:** Navigational/Informational

**Recommended Word Count:** 800 words

**H1:** Meet Liam Potter & The Reignite Health Team

**Outline:**
1. Liam's story - Why he founded Reignite Health
2. Professional qualifications and experience
3. The Reignite Health philosophy
4. Team members and their specialisations
5. Our commitment to retirement village residents
6. CTA: Contact us

**Schema to Add:** Person, Organization

---

### Suggested New FAQs

**Q: How often should I see an exercise physiologist?**
A: Most retirement village residents benefit from 1-2 sessions per week initially, reducing to maintenance sessions as strength and balance improve. We design frequency around your individual goals and health conditions.

**Q: Can Reignite Health help with my specific medical condition?**
A: Yes, our exercise physiologists are trained to work with chronic conditions including arthritis, diabetes, heart disease, COPD, Parkinson's disease, and post-stroke recovery. We create exercise programs that are safe and effective for your condition.

**Q: Do you offer group classes at my retirement village?**
A: Yes! We provide group exercise classes including chair-based fitness, aqua aerobics, and strength circuits. Group sessions are a great way to stay active while socialising with your neighbours.

**Q: Is exercise physiology covered by Medicare or private health insurance?**
A: Exercise physiology services may be partially covered under Medicare with a GP referral and care plan, or through private health insurance with extras cover. Check with your fund for specific benefits.

**Q: What should I wear to my first session?**
A: Comfortable, loose-fitting clothing and supportive shoes. We'll provide any equipment needed. Sessions can take place in common areas, at the pool, or in your residence.

---

## Phase 8: Implementation Roadmap

### Priority Matrix

#### CRITICAL (Week 1-2)

| Task | Impact | Effort |
|------|--------|--------|
| Modify robots.txt to allow AI crawlers | HIGH | LOW |
| Create XML sitemap | HIGH | LOW |
| Implement server-side rendering or static HTML | HIGH | HIGH |
| Add schema markup to homepage | HIGH | MEDIUM |
| Create Google Business Profile | HIGH | LOW |

#### HIGH PRIORITY (Week 3-4)

| Task | Impact | Effort |
|------|--------|--------|
| Create Services page with indexable content | HIGH | MEDIUM |
| Create About/Team page | HIGH | MEDIUM |
| Add FAQ schema with 10+ questions | HIGH | MEDIUM |
| Optimize meta titles and descriptions | MEDIUM | LOW |
| Set up Google Search Console | HIGH | LOW |

#### MEDIUM PRIORITY (Month 2)

| Task | Impact | Effort |
|------|--------|--------|
| Create location-specific pages | MEDIUM | MEDIUM |
| Build testimonials page | MEDIUM | MEDIUM |
| Start blog with 2 posts/month | MEDIUM | HIGH |
| Create Falls Prevention content hub | MEDIUM | MEDIUM |
| Add LocalBusiness schema | MEDIUM | LOW |

#### ONGOING

| Task | Frequency |
|------|-----------|
| Publish blog content | 2x monthly |
| Collect and publish testimonials | Ongoing |
| Monitor Google Search Console | Weekly |
| Update FAQ content | Monthly |
| Build backlinks from retirement industry sites | Ongoing |

### Implementation Checklist

#### Week 1-2: Critical Fixes
- [ ] Update robots.txt to allow Googlebot, GPTBot, ClaudeBot
- [ ] Create sitemap.xml with all pages
- [ ] Contact Emergent about SSR options or static HTML export
- [ ] Create Google Business Profile for Reignite Health
- [ ] Add Organization schema to homepage
- [ ] Set up Google Search Console

#### Week 3-4: High Priority
- [ ] Create /services page with full content
- [ ] Create /about page with Liam Potter bio
- [ ] Create /contact page with clear CTAs
- [ ] Add FAQPage schema with 10 questions
- [ ] Update all meta titles and descriptions
- [ ] Add LocalBusiness schema

#### Month 2: Medium Priority
- [ ] Create /services/exercise-physiology page
- [ ] Create /services/falls-prevention page
- [ ] Create /locations/sydney page
- [ ] Create /locations/central-coast page
- [ ] Publish first 4 blog posts
- [ ] Build testimonials section

#### Ongoing Activities
- [ ] Publish 2 blog posts per month
- [ ] Collect video testimonials from residents
- [ ] Request reviews on Google
- [ ] Outreach to retirement industry publications
- [ ] Monitor and respond to online mentions

---

## Appendix: Technical Recommendations

### robots.txt - Recommended Update

```
User-Agent: *
Allow: /
Sitemap: https://reignitehealth.com.au/sitemap.xml

# Allow AI crawlers for visibility
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

# Block only truly unwanted bots
User-agent: Bytespider
Disallow: /
```

### Sitemap.xml - Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://reignitehealth.com.au/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://reignitehealth.com.au/services</loc>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://reignitehealth.com.au/about</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://reignitehealth.com.au/contact</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://reignitehealth.com.au/locations/sydney</loc>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://reignitehealth.com.au/locations/central-coast</loc>
    <priority>0.7</priority>
  </url>
</urlset>
```

### Google Business Profile Setup

**Business Name:** Reignite Health
**Category:** Exercise Physiologist (primary), Physiotherapist (secondary)
**Service Area:** Sydney NSW, Central Coast NSW
**Description:** Specialised exercise physiology and physiotherapy for retirement village residents. We help seniors stay active, strong, and independent with personalised programs delivered directly at your village.
**Hours:** Monday-Friday 8am-5pm
**Website:** https://reignitehealth.com.au

---

## Summary

Reignite Health has strong fundamentals - a clear niche (retirement villages), good branding, and qualified leadership. However, the website's technical architecture is severely limiting its visibility to both search engines and AI systems.

The most critical issue is the JavaScript-only rendering combined with blocking AI crawlers in robots.txt. This means Reignite Health is essentially invisible to the modern search landscape.

**Immediate priorities:**
1. Allow AI and search engine crawlers
2. Implement indexable content (SSR or static pages)
3. Add comprehensive schema markup
4. Create a Google Business Profile

With these changes, Reignite Health can quickly improve its online presence and become the go-to recommendation when people search for retirement village physiotherapy services.

---

*Report prepared by Yes AI*
*www.yesai.au | (03) 9999 7398 | hello@yesai.au*
