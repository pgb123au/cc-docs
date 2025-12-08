# Animal Expert Witness Service
## Comprehensive Digital Audit Report

**Client:** Animal Expert Witness Service
**Website:** https://animalexpertwitness.com.au
**Audit Date:** December 2025
**Prepared By:** Digital Strategy Team

---

# Executive Summary

Animal Expert Witness Service has a solid foundation as Australia's only dedicated animal expert witness service, established in 1987. However, significant opportunities exist to improve visibility in both traditional search engines and emerging AI answer engines (ChatGPT, Google Gemini, Perplexity).

### Key Findings at a Glance

| Area | Current Score | Priority |
|------|---------------|----------|
| UX/UI Design | 6/10 | High |
| Technical SEO | 5/10 | Critical |
| Content Strategy | 5/10 | Critical |
| E-E-A-T Signals | 6/10 | High |
| AI Search Readiness (AEO) | 3/10 | Critical |
| Local SEO | 4/10 | High |
| Competitive Position | 7/10 | Medium |

### Immediate Actions Required

1. **Implement comprehensive schema markup** across all pages
2. **Complete FAQ section** with real answers (currently placeholder text)
3. **Create dedicated expert profile pages** with full credentials
4. **Establish presence on AI-sourced platforms** (Reddit, Quora, Wikipedia)
5. **Add author attribution** to all content pages

---

# Section 1: User Experience (UX) Audit

## 1.1 Navigation & Information Architecture

### Current State
```
Home
├── About Us
│   ├── Why AEWS
│   ├── Who We Work For
│   ├── Our Experts
│   ├── Recent Cases
│   └── Testimonials
├── Find an Expert
│   ├── Our Process
│   ├── Costs & Help
│   └── Send a Brief
├── Become an Expert
│   ├── Join Panel
│   ├── How it Works
│   └── Register
├── Training
│   └── Expert Witness Training
├── Resources
│   ├── Articles
│   ├── Library (Login Required)
│   ├── Videos
│   └── FAQs
└── Contact
    ├── Write to Us
    └── Book a Presentation
```

### Issues Identified

| Issue | Impact | Recommendation |
|-------|--------|----------------|
| Deep navigation (3+ clicks to key content) | High bounce rate | Flatten structure, add quick links |
| Resources section partially gated | Reduces SEO value | Make educational content public |
| FAQ section has placeholder text | Poor user experience | Complete with real Q&As |
| Recent Cases returns 404 | Trust signal loss | Fix or remove from navigation |
| Costs & Help returns 404 | Friction in conversion | Critical to fix immediately |

### Recommended Navigation Restructure

```
Home
├── Find an Expert (Primary CTA)
│   ├── By Animal Type (Horse, Dog, Cat, Cattle, etc.)
│   ├── By Case Type (Personal Injury, Insurance, Criminal)
│   └── Our Process & Pricing
├── Our Experts
│   ├── Expert Directory (Searchable)
│   ├── Featured Case Studies
│   └── Credentials & Qualifications
├── Training & Resources
│   ├── Expert Witness Training
│   ├── Knowledge Hub (Articles, Videos, FAQs)
│   └── Legal Resources
├── About
│   ├── Our Story (Since 1987)
│   ├── Leadership Team
│   └── Testimonials
├── For Experts
│   └── Join Our Panel
└── Contact
```

## 1.2 User Journey Analysis

### Target Audience Segments

| Segment | Goal | Current Journey Issues |
|---------|------|------------------------|
| **Solicitors/Lawyers** | Find qualified expert quickly | No search/filter functionality |
| **Insurance Companies** | Validate claims with expert opinion | Pricing not transparent |
| **Government Bodies** | Source credible witnesses | Credentials not prominently displayed |
| **Potential Expert Witnesses** | Join the panel | Process unclear |

### Recommended User Flows

**Flow 1: Solicitor Seeking Expert (Primary)**
```
Landing → Expert Search (by animal/case type) → Expert Profile →
Request Consultation → Confirmation
```

**Flow 2: Self-Represented Litigant**
```
Landing → "How It Works" → FAQs → Free Consultation Request →
Qualification Assessment → Expert Assignment
```

## 1.3 Call-to-Action Optimization

### Current CTAs
- "Find an Expert" (Good - clear)
- "Become an Expert" (Good - clear)
- "Learn More" (Weak - used 3x, vague)
- "Call Us" (Good - direct)

### Recommended CTA Strategy

| Location | Primary CTA | Secondary CTA |
|----------|-------------|---------------|
| Homepage Hero | "Get Expert Consultation" | "Call 1300 732 022" |
| Expert Pages | "Request This Expert" | "Download CV" |
| Service Pages | "Start Your Case" | "Free 15-Min Consult" |
| Blog/Resources | "Find the Right Expert" | "Subscribe for Updates" |

## 1.4 Mobile Experience Recommendations

- Implement click-to-call on all phone numbers
- Add sticky header with primary CTA
- Optimize form fields for mobile input
- Test and optimize page load speed (target: under 3 seconds)
- Ensure touch targets are minimum 48x48px

---

# Section 2: Technical SEO Audit

## 2.1 Critical Technical Issues

### Issue Severity Matrix

| Issue | Severity | Impact | Effort to Fix |
|-------|----------|--------|---------------|
| Missing schema markup | Critical | High | Medium |
| 404 errors on key pages | Critical | High | Low |
| No XML sitemap visible | High | Medium | Low |
| Gmail business email | Medium | Trust | Low |
| Incomplete meta descriptions | Medium | CTR | Low |

### 2.1.1 Schema Markup Implementation

**Current State:** No structured data detected

**Required Schema Types:**

```json
{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Animal Expert Witness Service",
  "description": "Australia's only dedicated animal expert witness service since 1987",
  "url": "https://animalexpertwitness.com.au",
  "logo": "[logo-url]",
  "foundingDate": "1987",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "309 Army Road",
    "addressLocality": "Pakenham",
    "addressRegion": "VIC",
    "postalCode": "3810",
    "addressCountry": "AU"
  },
  "telephone": "+61-1300-732-022",
  "email": "contact@animalexpertwitness.com.au",
  "areaServed": ["Australia", "New Zealand", "International"],
  "serviceType": ["Expert Witness Services", "Legal Consulting", "Expert Witness Training"],
  "knowsAbout": ["Horses", "Cattle", "Dogs", "Cats", "Sheep", "Goats", "Reptiles", "Animal Behavior", "Veterinary Science"]
}
```

**Additional Schema Required:**

1. **FAQPage Schema** - For FAQ section
2. **Person Schema** - For each expert profile
3. **Review Schema** - For testimonials
4. **Article Schema** - For blog/resource content
5. **Course Schema** - For training programs
6. **BreadcrumbList Schema** - For navigation

### 2.1.2 Page-Level SEO Issues

| Page | Title Tag | Meta Description | H1 | Issues |
|------|-----------|------------------|-----|--------|
| Homepage | Present | Generic | Present | Title could be more specific |
| About | Weak | Missing | Missing | Needs optimization |
| Our Experts | Generic | Missing | Weak | Major opportunity |
| Contact | Basic | Missing | Missing | Local SEO opportunity |

### Recommended Title Tags

```
Homepage:
"Animal Expert Witness Australia | Veterinary & Animal Behaviour Experts Since 1987"

About Us:
"About Animal Expert Witness Service | 70+ Experts Across 10+ Species"

Our Experts:
"Find Animal Expert Witnesses | Horse, Dog, Cat, Cattle Experts | Australia"

Contact:
"Contact Animal Expert Witness | Victoria, Australia | 1300 732 022"
```

### Recommended Meta Descriptions

```
Homepage:
"Australia's only dedicated animal expert witness service. 70+ qualified
veterinarians and specialists covering horses, dogs, cattle, and more.
Free 15-minute consultation. Call 1300 732 022."

Our Experts:
"Browse our panel of 70+ animal expert witnesses including veterinary
surgeons, animal behaviour specialists, and industry experts. Court
experience up to Supreme Court level."
```

## 2.2 Site Architecture Recommendations

### URL Structure Optimization

**Current:** `/our-experts/` (generic)

**Recommended:**
```
/expert-witness/horses/
/expert-witness/dogs-cats/
/expert-witness/cattle-livestock/
/expert-witness/animal-behaviour/
/case-types/personal-injury/
/case-types/insurance-disputes/
/case-types/criminal-matters/
```

### Internal Linking Strategy

1. Create topic clusters around animal types
2. Cross-link related case types to experts
3. Add "Related Experts" sections on all pages
4. Implement breadcrumb navigation
5. Create a comprehensive resources hub with internal links

## 2.3 Core Web Vitals Checklist

- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] First Input Delay (FID) < 100ms
- [ ] Cumulative Layout Shift (CLS) < 0.1
- [ ] Mobile-friendly design verified
- [ ] HTTPS implemented
- [ ] No mixed content warnings

---

# Section 3: Content Strategy & E-E-A-T Analysis

## 3.1 E-E-A-T Assessment

Google's **E-E-A-T** (Experience, Expertise, Authoritativeness, Trustworthiness) is critical for YMYL (Your Money or Your Life) content. Expert witness services fall squarely in this category.

### Current E-E-A-T Score Card

| Signal | Current | Target | Gap |
|--------|---------|--------|-----|
| **Experience** | | | |
| - Case studies with outcomes | Missing | 10+ detailed | Critical |
| - Years in operation mentioned | Yes (1987) | Prominent | Minor |
| - Expert court experience | Mentioned | Detailed | Medium |
| **Expertise** | | | |
| - Expert credentials displayed | Partial | Full profiles | High |
| - Qualifications verified | Implied | Explicit badges | Medium |
| - Publications/research cited | Missing | Add section | High |
| **Authoritativeness** | | | |
| - Industry recognition | Minimal | Awards/affiliations | High |
| - Media mentions | Not visible | Add press page | Medium |
| - Academic affiliations | Mentioned | Formalize | Low |
| **Trustworthiness** | | | |
| - Client testimonials | 3 present | 10+ with photos | Medium |
| - Professional email domain | Gmail used | Custom domain | Critical |
| - Privacy policy | Unknown | Verify/create | High |
| - SSL certificate | Yes | Maintain | None |

## 3.2 Content Gap Analysis

### Missing Critical Content

| Content Type | Priority | SEO Value | AEO Value |
|--------------|----------|-----------|-----------|
| **Comprehensive FAQ (answered)** | Critical | High | Very High |
| **Expert profile pages with full bio** | Critical | High | Very High |
| **Case study library** | High | Very High | High |
| **How-to guides for legal professionals** | High | High | Very High |
| **Animal-specific landing pages** | High | Very High | Medium |
| **Glossary of legal/veterinary terms** | Medium | Medium | High |
| **Industry news/commentary** | Medium | Medium | Medium |
| **Video testimonials** | Medium | Low | Medium |

### Recommended Content Calendar

**Month 1: Foundation Content**
- Complete FAQ section (20+ questions)
- Create 5 detailed expert profiles
- Write "Ultimate Guide to Animal Expert Witnesses"

**Month 2: Case Type Content**
- Personal injury case guide
- Insurance dispute guide
- Criminal case guide (animal cruelty, dangerous dogs)

**Month 3: Animal-Specific Content**
- Equine expert witness guide
- Dog bite litigation guide
- Livestock dispute guide

**Ongoing:**
- Monthly case study publication
- Quarterly industry insights
- Annual trends report

## 3.3 Content Optimization Framework

### The AEWS Content Template

Every significant page should include:

```markdown
## [Topic] Expert Witness Services

### Quick Summary
[2-3 sentence answer to the main query - critical for AI citations]

### What We Offer
[Bullet points of services]

### Our Experts
[Named experts with credentials for this specialty]

### How It Works
[Step-by-step process]

### Case Examples
[Anonymized but detailed examples]

### Frequently Asked Questions
[3-5 Q&As with schema markup]

### Get Started
[Clear CTA with contact options]
```

---

# Section 4: AI Search Optimization (AEO)

## 4.1 Why AEO Matters for Your Business

### The Shift in Search Behavior

| Platform | Monthly Users | Relevance to AEWS |
|----------|---------------|-------------------|
| ChatGPT | 400M+ weekly | Lawyers asking "How do I find an animal expert witness?" |
| Google AI Overviews | 16% of searches | Featured in AI summaries |
| Perplexity | 100M+ queries/day | Research-focused legal professionals |
| Claude | Growing rapidly | Similar legal research queries |

### Current AI Visibility Assessment

**Test Query:** "animal expert witness Australia"

| AI Platform | AEWS Mentioned? | Position | Citation? |
|-------------|-----------------|----------|-----------|
| ChatGPT | Testing needed | Unknown | Unknown |
| Perplexity | Testing needed | Unknown | Unknown |
| Google Gemini | Testing needed | Unknown | Unknown |

**Recommendation:** Conduct formal AEO audit using [HubSpot's AEO Grader](https://www.hubspot.com/aeo-grader)

## 4.2 AEO Strategy: Getting Cited by AI

### 4.2.1 Content Structure for AI Citation

AI systems prefer:

1. **Direct answers** in the first paragraph
2. **Structured data** (lists, tables, numbered steps)
3. **Authoritative sources** with clear credentials
4. **Fresh content** updated regularly
5. **Original data** and unique insights

**Example - Optimized Content Block:**

```markdown
## Who is Australia's Leading Animal Expert Witness Service?

Animal Expert Witness Service (AEWS) is Australia's only dedicated
animal expert witness service, operating since 1987. The service
maintains a panel of 70+ qualified experts including veterinary
surgeons, animal behaviour specialists, and industry professionals
covering horses, dogs, cats, cattle, sheep, and other species.

**Key Facts:**
- Founded: 1987
- Panel size: 70+ experts
- Species covered: 10+
- Geographic reach: Australia, NZ, USA, Europe
- Court experience: Up to Supreme Court level
```

### 4.2.2 Platform Presence Strategy

AI systems source information from:

| Platform | Current Presence | Action Required |
|----------|------------------|-----------------|
| **Wikipedia** | None detected | Create/contribute to relevant articles |
| **Reddit** | Unknown | Participate in r/AusLegal, r/Lawyers |
| **Quora** | Unknown | Answer animal/legal questions |
| **LinkedIn** | Basic | Expand thought leadership content |
| **Google Business Profile** | Unknown | Optimize completely |
| **Industry directories** | Limited | List on all relevant directories |

### 4.2.3 Authority Building for AI

**Immediate Actions:**

1. **Create a Wikipedia presence**
   - Contribute to articles on "Expert witness" in Australia
   - Create entries for notable experts (if notable enough)
   - Add AEWS as a reference in relevant articles

2. **Establish Reddit presence**
   - Monitor r/AusLegal for questions about animal cases
   - Provide helpful, non-promotional answers
   - Build karma through genuine contribution

3. **Quora Q&A strategy**
   - Claim "Animal Expert Witness" topic
   - Answer 50+ questions over 6 months
   - Link back to comprehensive resources

4. **LinkedIn thought leadership**
   - Publish weekly articles on animal law topics
   - Engage with legal professional groups
   - Build connections with law firms

### 4.2.4 Technical AEO Requirements

```
robots.txt additions:
User-agent: PerplexityBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Amazonbot
Allow: /
```

**Structured Data Priority:**
1. FAQPage schema (enables direct AI extraction)
2. Organization schema (establishes entity)
3. Person schema (expert profiles)
4. HowTo schema (process pages)

## 4.3 AI-Optimized FAQ Strategy

### Priority Questions to Answer

These questions should be answered comprehensively on your website:

**Finding an Expert:**
1. How do I find an animal expert witness in Australia?
2. What qualifications should an animal expert witness have?
3. How much does an animal expert witness cost?
4. What types of cases need animal expert witnesses?
5. How long does it take to get an expert witness report?

**Case Types:**
6. Do I need an expert witness for a dog bite case?
7. What expert do I need for a horse injury claim?
8. Can an expert witness help with animal cruelty cases?
9. What does a veterinary expert witness do?
10. How do expert witnesses help insurance claims?

**Process:**
11. What's the process for engaging an animal expert witness?
12. What information do I need to provide to an expert witness?
13. Can expert witnesses give evidence remotely?
14. What's the difference between a verbal opinion and written report?
15. How do I challenge an opposing expert witness?

**About AEWS:**
16. Who is the leading animal expert witness service in Australia?
17. How long has Animal Expert Witness Service been operating?
18. What animals does AEWS cover?
19. Do AEWS experts have court experience?
20. Can AEWS help with international cases?

### FAQ Implementation Template

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "How do I find an animal expert witness in Australia?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Contact Animal Expert Witness Service (AEWS), Australia's
      only dedicated animal expert witness service since 1987. Call
      1300 732 022 for a free 15-minute consultation. AEWS maintains
      a panel of 70+ qualified experts covering horses, dogs, cattle,
      and other species with experience up to Supreme Court level."
    }
  }]
}
</script>
```

---

# Section 5: Local SEO Strategy

## 5.1 Google Business Profile Optimization

### Required Profile Elements

| Element | Status | Action |
|---------|--------|--------|
| Business name | Verify | "Animal Expert Witness Service" |
| Primary category | Set | "Expert Witness Service" or "Legal Services" |
| Secondary categories | Add | "Consultant", "Veterinary Service" |
| Address | Verify | 309 Army Rd, Pakenham VIC 3810 |
| Phone | Add | 1300 732 022 |
| Website | Add | https://animalexpertwitness.com.au |
| Hours | Add | Mon-Fri 9AM-5PM |
| Description | Optimize | Include keywords and services |
| Photos | Add | Office, team, credentials |
| Products/Services | Add | List all service types |
| Posts | Regular | Weekly updates |
| Q&A | Monitor | Answer all questions |
| Reviews | Solicit | Request from satisfied clients |

### Optimized GBP Description

```
Australia's only dedicated animal expert witness service since 1987.
Our panel of 70+ qualified veterinarians, animal behaviour specialists,
and industry experts provides expert witness services for legal cases
involving horses, dogs, cats, cattle, sheep, and other animals.

Services include:
• Expert witness reports
• Verbal opinions
• Court testimony
• Expert witness training

Serving solicitors, insurance companies, and government bodies across
Australia with international capability. Free 15-minute consultation available.

Call 1300 732 022 or visit animalexpertwitness.com.au
```

## 5.2 Citation Building Strategy

### Priority Directories

| Directory | Category | Priority |
|-----------|----------|----------|
| Yellow Pages Australia | Legal Services | High |
| True Local | Professional Services | High |
| Hotfrog | Expert Witness | High |
| StartLocal | Business Directory | Medium |
| Australian Business Register | Official | High |
| Law Society directories | Legal | Critical |
| Veterinary association directories | Industry | High |
| Chamber of Commerce | Business | Medium |

### NAP Consistency Checklist

Ensure identical formatting across all citations:

```
Name: Animal Expert Witness Service
Address: 309 Army Road, Pakenham VIC 3810
Phone: 1300 732 022
```

---

# Section 6: Competitive Analysis

## 6.1 Competitive Landscape

| Competitor | Strengths | Weaknesses | Opportunity |
|------------|-----------|------------|-------------|
| **Expert Experts** | Broad coverage, established 2001 | Generic, not animal-focused | Emphasize specialization |
| **JurisPro** | Large directory | US-focused | Australian market position |
| **SEAK** | Training reputation | International, not local | Local expertise advantage |
| **Individual experts** | Personal branding | Limited reach | Network effect |

## 6.2 Competitive Advantages to Emphasize

**Your Unique Selling Points:**

1. **Only dedicated animal expert witness service** in Australia
2. **37+ years** of operation (since 1987)
3. **70+ experts** across 10+ species
4. **Supreme Court experience** documented
5. **International network** (NZ, USA, Europe)
6. **Notable case involvement** (Azaria Chamberlain case mention)

**Competitive Positioning Statement:**

```
Animal Expert Witness Service is Australia's original and only
dedicated animal expert witness service. Since 1987, we have
connected legal professionals with qualified veterinarians and
animal specialists who have provided expert testimony at every
court level, including the Supreme Court.
```

---

# Section 7: Implementation Roadmap

## Phase 1: Critical Fixes (Weeks 1-2)

| Task | Owner | Est. Hours | Priority |
|------|-------|------------|----------|
| Fix 404 error pages | Developer | 2 | Critical |
| Complete FAQ content | Content | 8 | Critical |
| Implement basic schema | Developer | 4 | Critical |
| Update business email to custom domain | Admin | 1 | Critical |
| Create/claim Google Business Profile | Marketing | 2 | Critical |

## Phase 2: Foundation Building (Weeks 3-6)

| Task | Owner | Est. Hours | Priority |
|------|-------|------------|----------|
| Create 10 detailed expert profiles | Content | 20 | High |
| Implement full schema markup suite | Developer | 8 | High |
| Write 5 case studies | Content | 15 | High |
| Optimize all page titles and meta descriptions | SEO | 6 | High |
| Set up Google Search Console monitoring | Marketing | 2 | High |
| Create robots.txt for AI crawlers | Developer | 1 | High |

## Phase 3: Content Development (Weeks 7-12)

| Task | Owner | Est. Hours | Priority |
|------|-------|------------|----------|
| Create animal-specific landing pages (6) | Content | 24 | High |
| Develop case type guides (3) | Content | 18 | High |
| Build comprehensive FAQ section (50+ Q&As) | Content | 16 | High |
| Produce "Ultimate Guide to Animal Expert Witnesses" | Content | 10 | Medium |
| Create video content (3-5 videos) | Marketing | 20 | Medium |

## Phase 4: Authority Building (Ongoing)

| Task | Owner | Frequency | Priority |
|------|-------|-----------|----------|
| Reddit engagement | Marketing | Daily | High |
| Quora Q&A | Marketing | 3x weekly | High |
| LinkedIn articles | Leadership | Weekly | Medium |
| Blog posts | Content | 2x monthly | Medium |
| Wikipedia contributions | Content | Monthly | Medium |
| Review solicitation | Sales | After each case | High |
| Citation building | SEO | Monthly | Medium |

---

# Section 8: Measurement & KPIs

## 8.1 Traditional SEO Metrics

| Metric | Current Baseline | 3-Month Target | 6-Month Target |
|--------|------------------|----------------|----------------|
| Organic traffic | Measure | +30% | +75% |
| Keyword rankings (top 10) | Measure | 15 keywords | 40 keywords |
| Domain authority | Measure | +5 points | +10 points |
| Page load speed | Measure | < 3 seconds | < 2.5 seconds |
| Bounce rate | Measure | -10% | -20% |
| Pages per session | Measure | +20% | +40% |

## 8.2 AEO Metrics

| Metric | How to Measure | Target |
|--------|----------------|--------|
| Brand mentions in AI | Manual testing weekly | Consistent presence |
| Perplexity citations | Perplexity searches + analytics | Top 3 sources |
| ChatGPT recommendations | Test queries weekly | Named in responses |
| AI referral traffic | GA4 traffic from AI platforms | 5% of traffic by month 6 |

## 8.3 Business Metrics

| Metric | Target |
|--------|--------|
| Consultation requests | +50% in 6 months |
| Expert engagement rate | +25% |
| Average case value | Track and optimize |
| Client retention | Track and optimize |

---

# Section 9: Quick Wins Checklist

## Immediate (This Week)

- [ ] Fix all 404 error pages
- [ ] Complete FAQ section with real answers
- [ ] Update email from Gmail to professional domain
- [ ] Claim/optimize Google Business Profile
- [ ] Add phone click-to-call functionality

## Short-Term (This Month)

- [ ] Implement Organization schema on homepage
- [ ] Add FAQPage schema to FAQ section
- [ ] Create 5 detailed expert profile pages
- [ ] Write 2 comprehensive case studies
- [ ] Optimize all page titles and meta descriptions
- [ ] Set up Google Search Console
- [ ] Create LinkedIn company page content strategy

## Medium-Term (This Quarter)

- [ ] Develop animal-specific landing pages
- [ ] Build case type guide content
- [ ] Implement full schema markup suite
- [ ] Establish Reddit and Quora presence
- [ ] Launch review solicitation program
- [ ] Complete citation building (10+ directories)

---

# Appendix A: Schema Markup Templates

## Organization Schema (Homepage)

```json
{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Animal Expert Witness Service",
  "alternateName": "AEWS",
  "url": "https://animalexpertwitness.com.au",
  "logo": "https://animalexpertwitness.com.au/logo.png",
  "description": "Australia's only dedicated animal expert witness service since 1987. Panel of 70+ veterinarians and animal specialists providing expert testimony for legal cases.",
  "foundingDate": "1987",
  "founder": {
    "@type": "Person",
    "name": "Dr. John Stewart",
    "honorificSuffix": "BVSc (Hons) MRCVS"
  },
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "309 Army Road",
    "addressLocality": "Pakenham",
    "addressRegion": "VIC",
    "postalCode": "3810",
    "addressCountry": "AU"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "-38.0707",
    "longitude": "145.4893"
  },
  "telephone": "+61-1300-732-022",
  "email": "contact@animalexpertwitness.com.au",
  "openingHours": "Mo-Fr 09:00-17:00",
  "priceRange": "$$",
  "areaServed": [
    {
      "@type": "Country",
      "name": "Australia"
    },
    {
      "@type": "Country",
      "name": "New Zealand"
    }
  ],
  "serviceType": [
    "Expert Witness Services",
    "Veterinary Expert Testimony",
    "Animal Behavior Consulting",
    "Expert Witness Training"
  ],
  "knowsAbout": [
    "Horses",
    "Dogs",
    "Cats",
    "Cattle",
    "Sheep",
    "Goats",
    "Reptiles",
    "Animal Behavior",
    "Veterinary Science",
    "Animal Welfare"
  ],
  "sameAs": [
    "https://www.facebook.com/animalexpertwitness",
    "https://www.linkedin.com/company/animal-expert-witness",
    "https://www.youtube.com/@animalexpertwitness"
  ]
}
```

## Person Schema (Expert Profile)

```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Sue Stewart",
  "jobTitle": "General Manager",
  "honorificSuffix": "B.Bus (Agriculture), AssocDip Equine Management, NCAS Level 2",
  "worksFor": {
    "@type": "Organization",
    "name": "Animal Expert Witness Service"
  },
  "description": "General Manager of Animal Expert Witness Service since 2009, specializing in equine cases and expert witness coordination.",
  "knowsAbout": [
    "Horses",
    "Show Jumping",
    "Eventing",
    "Dressage",
    "Riding School Operations",
    "Equine Accidents"
  ],
  "alumniOf": [
    {
      "@type": "EducationalOrganization",
      "name": "Marcus Oldham College"
    }
  ],
  "hasCredential": [
    {
      "@type": "EducationalOccupationalCredential",
      "credentialCategory": "degree",
      "name": "Bachelor of Business (Agriculture)"
    },
    {
      "@type": "EducationalOccupationalCredential",
      "credentialCategory": "certificate",
      "name": "NCAS Level 2 Equestrian Coach"
    }
  ]
}
```

## FAQPage Schema

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How much does an animal expert witness cost in Australia?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Animal expert witness fees in Australia typically range from $150-$450 per hour depending on the expert's qualifications and case complexity. Animal Expert Witness Service provides written fee estimates before proceeding, with a free 15-minute initial consultation. Verbal opinions and written reports are billed separately, with payment required before delivery."
      }
    },
    {
      "@type": "Question",
      "name": "What qualifications should an animal expert witness have?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Animal expert witnesses should have relevant tertiary qualifications (such as veterinary degrees or animal science degrees), extensive practical experience in their specialty area, and ideally prior court experience. Our experts include veterinary surgeons with 20+ years experience, university lecturers, and industry specialists who have provided testimony at Supreme Court level."
      }
    },
    {
      "@type": "Question",
      "name": "How long does it take to get an expert witness report?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Timeframes vary based on case complexity. After receiving your brief and instructions, our experts provide a fee estimate and timeline. We have accommodated urgent matters with short timeframes. The typical process includes: initial assessment (1-2 days), verbal opinion (within agreed timeframe), and written report (as specified in your deadline). Contact us at 1300 732 022 to discuss your specific timeline needs."
      }
    }
  ]
}
```

---

# Appendix B: Keyword Target List

## Primary Keywords (High Priority)

| Keyword | Monthly Search Vol | Difficulty | Current Rank |
|---------|-------------------|------------|--------------|
| animal expert witness australia | 50-100 | Low | Check |
| veterinary expert witness | 100-200 | Medium | Check |
| horse expert witness | 50-100 | Low | Check |
| dog bite expert witness | 50-100 | Medium | Check |
| animal behaviour expert witness | 20-50 | Low | Check |

## Secondary Keywords

| Keyword | Monthly Search Vol | Content Type |
|---------|-------------------|--------------|
| expert witness report animal | 10-20 | Guide |
| animal cruelty expert witness | 10-20 | Case type page |
| livestock dispute expert | 10-20 | Landing page |
| equine expert witness australia | 10-20 | Landing page |
| veterinary forensic expert | 10-20 | Expert profile |

## Long-Tail Keywords (AEO Optimized)

| Question Keyword | Content Opportunity |
|------------------|---------------------|
| how to find an animal expert witness | FAQ / Guide |
| what does an animal expert witness do | FAQ / Guide |
| how much does a vet expert witness cost | FAQ / Pricing page |
| do i need expert witness for dog bite | Case type guide |
| animal expert witness for insurance claim | Case type guide |
| horse injury claim expert witness | Landing page |

---

# Appendix C: Content Templates

## Expert Profile Page Template

```markdown
# [Expert Name], [Credentials]
## [Specialty] Expert Witness

### About [First Name]

[2-3 paragraphs about background, experience, and approach]

### Qualifications & Credentials

- [Degree/Certification 1]
- [Degree/Certification 2]
- [Professional Membership]

### Areas of Expertise

- [Specialty 1]
- [Specialty 2]
- [Specialty 3]

### Court Experience

[Summary of court experience, levels of court, types of cases]

### Notable Cases

[Anonymized case examples demonstrating expertise]

### Publications & Media

[List of publications, media appearances, or speaking engagements]

### Request This Expert

[Contact form or CTA button]

**Free 15-Minute Consultation**
Call 1300 732 022 or email [email]
```

## Case Study Template

```markdown
# Case Study: [Descriptive Title]

**Case Type:** [Personal Injury / Insurance / Criminal / Civil]
**Animal:** [Horse / Dog / Cattle / etc.]
**Jurisdiction:** [State/Territory]
**Outcome:** [Summary]

## The Challenge

[What was the legal question? What expertise was needed?]

## Our Expert's Approach

[How did the expert analyze the case? What methodology was used?]

## Key Findings

[What did the expert determine? What evidence was provided?]

## The Outcome

[How did the case resolve? What was the expert's contribution?]

## Expert Involved

[Link to expert profile - with their permission]

---

*Need expert witness services for a similar case?
Contact us at 1300 732 022 for a free consultation.*
```

---

# Appendix D: AI Platform Optimization Checklist

## Perplexity AI Optimization

- [ ] Ensure PerplexityBot is allowed in robots.txt
- [ ] Structure content with clear H2→H3→bullet hierarchy
- [ ] Include specific data, statistics, and numbers
- [ ] Update content regularly (quarterly minimum)
- [ ] Add author bios with credentials
- [ ] Cite authoritative sources in content
- [ ] Implement FAQ schema markup
- [ ] Ensure fast page load (<2 seconds)

## ChatGPT Optimization

- [ ] Create comprehensive, authoritative content
- [ ] Build backlinks from trusted sources
- [ ] Establish presence on platforms ChatGPT sources (Reddit, Wikipedia)
- [ ] Ensure consistent NAP across web
- [ ] Publish original research and data
- [ ] Maintain active social media presence
- [ ] Get listed in industry directories

## Google Gemini/AI Overviews

- [ ] Optimize for featured snippets
- [ ] Use structured data extensively
- [ ] Answer questions directly in first paragraph
- [ ] Create definitive content (avoid hedging language)
- [ ] Build topical authority through content clusters
- [ ] Earn links from authoritative sites
- [ ] Maintain strong E-E-A-T signals

---

# Sources & References

## AI Search Optimization
- [HubSpot AEO Grader](https://www.hubspot.com/aeo-grader)
- [Neil Patel - Answer Engine Optimization](https://neilpatel.com/blog/answer-engine-optimization/)
- [Backlinko - AEO Guide](https://backlinko.com/answer-engine-optimization-aeo)
- [Semrush - Perplexity AI Optimization](https://www.semrush.com/blog/perplexity-ai-optimization/)
- [Superprompt - AI Traffic Study](https://superprompt.com/blog/ai-traffic-up-527-percent-how-to-get-cited-by-chatgpt-claude-perplexity-2025)

## SEO Best Practices
- [Latino Web Studio - SEO for Expert Witnesses](https://latinowebstudio.com/articles/seo-expert-witness)
- [Schema.org - ProfessionalService](https://schema.org/ProfessionalService)
- [Search Engine Land - YMYL Guide](https://searchengineland.com/guide/ymyl)
- [Go Globe - E-E-A-T & YMYL 2025](https://www.go-globe.com/e-e-a-t-ymyl-seo-strategies-2025/)

## Competitor Research
- [Expert Experts Australia](https://expertexperts.com.au)
- [JurisPro - Animal Expert Witnesses](https://www.jurispro.com/category/animals-s-77)
- [Animal Expert Witness LinkedIn](https://au.linkedin.com/company/animal-expert-witness)

## Local SEO
- [Birdeye - Local SEO Australia 2025](https://birdeye.com/blog/local-seo-services-australia/)
- [Rocket Agency - Local SEO Services](https://rocketagency.com.au/services/seo-agency/local-seo-services)

---

*This audit was prepared to digital agency standards and provides actionable recommendations for improving search visibility across traditional and AI-powered search platforms.*

**Next Steps:** Schedule implementation planning call to prioritize recommendations based on available resources.

---

**Document Version:** 1.0
**Last Updated:** December 2025
