# Nutrition Science Group
## Comprehensive UX, SEO & AI Search Optimization Audit

---

**Prepared for:** Nutrition Science Group
**Website:** https://nutritionsciencegroup.com
**Audit Date:** December 8, 2025
**Prepared by:** Digital Strategy Audit Team

---

# Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Critical Issues & Priority Matrix](#critical-issues--priority-matrix)
4. [Technical SEO Audit](#technical-seo-audit)
5. [UX/UI Analysis](#uxui-analysis)
6. [Content Strategy Assessment](#content-strategy-assessment)
7. [AI Search Optimization (AEO)](#ai-search-optimization-aeo)
8. [Local SEO Analysis](#local-seo-analysis)
9. [Competitive Analysis](#competitive-analysis)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Appendices](#appendices)

---

# Executive Summary

## Overview

The Nutrition Science Group website presents a compelling opportunity for significant improvement in search visibility, user experience, and—critically—**AI search engine optimization**. While the site contains valuable content and credentialed team members, several fundamental issues are severely limiting its digital performance.

## Key Findings at a Glance

| Area | Current Score | Target Score | Priority |
|------|---------------|--------------|----------|
| **Search Visibility** | 2/10 | 8/10 | CRITICAL |
| **Technical SEO** | 4/10 | 9/10 | HIGH |
| **UX/UI Design** | 5/10 | 8/10 | MEDIUM |
| **Content Strategy** | 4/10 | 9/10 | HIGH |
| **AI Search Readiness** | 2/10 | 9/10 | CRITICAL |
| **Local SEO** | 3/10 | 8/10 | HIGH |
| **E-E-A-T Signals** | 4/10 | 9/10 | CRITICAL |

## Critical Discovery: Search Index Crisis

**Only 2 pages from your entire website appear in Google search results.** This represents a severe indexing problem that requires immediate attention. Your competitors have hundreds of indexed pages generating organic traffic.

## Top 5 Immediate Actions Required

1. **Fix Search Index Issues** - Submit sitemap to Google Search Console, resolve crawlability problems
2. **Implement Comprehensive Schema Markup** - Add MedicalBusiness, Person, FAQPage, and Article schemas
3. **Create Structured, AI-Friendly Content** - Reformat content for featured snippets and AI citation
4. **Establish Author Authority Pages** - Showcase team credentials for E-E-A-T compliance
5. **Optimize Google Business Profile** - Fully complete and actively manage your listing

## Projected Impact

| Metric | Current (Est.) | 6-Month Target | 12-Month Target |
|--------|----------------|----------------|-----------------|
| Indexed Pages | 2 | 50+ | 100+ |
| Monthly Organic Visits | ~50 | 500+ | 2,000+ |
| AI Search Citations | 0 | 5-10/month | 50+/month |
| Featured Snippets | 0 | 10+ | 30+ |
| Local Pack Appearances | Rare | Regular | Dominant |

---

# Current State Analysis

## Website Overview

| Attribute | Current State |
|-----------|---------------|
| **Platform** | WordPress |
| **Domain Age** | Established |
| **SSL Certificate** | Active (HTTPS) |
| **Mobile Responsive** | Yes |
| **Page Builder** | Detected (likely Elementor) |
| **Copyright Year** | 2022 (outdated) |

## Content Inventory

| Content Type | Count | Status |
|--------------|-------|--------|
| Blog Posts | 6+ visible | Needs expansion |
| Team Profiles | 7 | Good foundation |
| FAQ Items | 10 | Needs schema markup |
| Video Content | 5+ | Underoptimized |
| Event Pages | 1 active | Good for local SEO |

## Current SEO Elements Detected

### Positive Elements
- Basic Organization schema present
- Address and contact info in footer
- HTTPS enabled
- Sitemap exists at `/wp-sitemap.xml`

### Critical Gaps
- Meta description showing placeholder text: *"This is an example page. It's different from a blog post..."*
- Minimal schema markup implementation
- No author attribution on blog posts
- No FAQ schema despite having FAQ content
- No LocalBusiness/MedicalBusiness schema
- Limited internal linking structure

---

# Critical Issues & Priority Matrix

## Priority 1: CRITICAL (Address Immediately)

### Issue 1.1: Catastrophic Index Coverage
**Problem:** Only 2 pages indexed by Google
**Impact:** 95%+ of potential organic traffic lost
**Evidence:** `site:nutritionsciencegroup.com` returns only 2 results

**Root Causes:**
- Potential robots.txt misconfiguration
- Possible noindex tags on pages
- Thin content or duplicate content issues
- Lack of Google Search Console monitoring

**Action Required:**
```
1. Set up Google Search Console (if not exists)
2. Submit XML sitemap manually
3. Request indexing for all key pages
4. Review Coverage report for errors
5. Check for noindex tags in page source
```

### Issue 1.2: Broken Meta Description
**Problem:** Homepage meta description shows placeholder text
**Impact:** Poor click-through rates, unprofessional appearance in search results

**Current:**
> "This is an example page. It's different from a blog post because it will stay in one place and will show up in your site navigation (in most themes). Most"

**Recommended:**
> "Expert keto and low-carb nutrition coaching in Victoria, Australia. Our team of doctors, dietitians, and wellness coaches help reverse type 2 diabetes and achieve lasting weight loss. Free 15-minute consultation available."

### Issue 1.3: Missing E-E-A-T Signals for YMYL Content
**Problem:** Health advice website without visible author credentials
**Impact:** Google may suppress YMYL content lacking expertise signals

**Current State:**
- Blog posts show no author attribution
- No "medically reviewed by" badges
- Team credentials scattered, not prominently displayed
- No citations to peer-reviewed sources

---

## Priority 2: HIGH (Address Within 30 Days)

### Issue 2.1: No Schema Markup for Key Content Types
**Problem:** Missing structured data across the site
**Impact:** Ineligible for rich results, AI systems cannot parse content effectively

**Required Schemas:**
| Schema Type | Pages | Status |
|-------------|-------|--------|
| MedicalBusiness | Homepage | Missing |
| LocalBusiness | Contact/All | Missing |
| FAQPage | FAQ page | Missing |
| Article | Blog posts | Missing |
| Person | Team profiles | Missing |
| Event | Events page | Missing |
| VideoObject | Videos page | Missing |
| Review/Testimonial | Homepage | Missing |

### Issue 2.2: Content Not Optimized for Featured Snippets
**Problem:** Valuable content buried in unstructured paragraphs
**Impact:** Zero featured snippet ownership, invisible to AI systems

**Example - Current FAQ Answer:**
> Long paragraph explaining ketosis without clear structure or scannable format.

**Example - Optimized for Snippets:**
> **What is ketosis?**
> Ketosis is a metabolic state where your body burns fat for fuel instead of carbohydrates.
>
> **How to achieve ketosis:**
> - Reduce carbohydrate intake to under 50g/day
> - Increase healthy fat consumption
> - Moderate protein intake
> - Consider intermittent fasting
>
> Blood ketone levels of 1.0-3.0 mmol/L indicate nutritional ketosis.

### Issue 2.3: No Google Business Profile Optimization
**Problem:** Local presence underutilized
**Impact:** Missing 82% of patients who use Google to find healthcare providers

---

## Priority 3: MEDIUM (Address Within 60 Days)

| Issue | Problem | Impact |
|-------|---------|--------|
| Outdated copyright (2022) | Signals abandoned site | Trust erosion |
| Inconsistent contact info | Two different phone numbers found | Confusion, NAP issues |
| No clear service pages | Services mixed into homepage | Poor user journey |
| Videos not transcribed | YouTube embeds without text | SEO opportunity lost |
| No testimonial schema | Reviews exist but not marked up | Missing rich results |

---

# Technical SEO Audit

## Crawlability & Indexation

### Robots.txt Analysis
```
User-agent: *
Disallow: /now22/wp-admin/
Allow: /now22/wp-admin/admin-ajax.php
Sitemap: https://nutritionsciencegroup.com/wp-sitemap.xml
```

**Assessment:** Basic configuration is acceptable, but does not explain indexation issues.

**Recommendation:** Add specific crawler allowances:
```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

# AI Search Crawlers - EXPLICITLY ALLOW
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Anthropic-ai
Allow: /

Sitemap: https://nutritionsciencegroup.com/wp-sitemap.xml
Sitemap: https://nutritionsciencegroup.com/sitemap.xml
```

### XML Sitemap Analysis

**Current Sitemaps Found:**
1. `wp-sitemap.xml` (index)
2. `wp-sitemap-posts-post-1.xml`
3. `wp-sitemap-posts-page-1.xml`
4. `wp-sitemap-posts-our_team-1.xml`
5. `wp-sitemap-posts-videos-1.xml`
6. `wp-sitemap-posts-event-1.xml`
7. `wp-sitemap-taxonomies-category-1.xml`
8. `wp-sitemap-taxonomies-post_tag-1.xml`
9. `wp-sitemap-users-1.xml`

**Issues:**
- No `lastmod` dates included
- No priority values set
- Users sitemap may expose author pages unintentionally

**Recommendations:**
1. Install Yoast SEO or Rank Math for enhanced sitemap control
2. Add `lastmod` dates to all entries
3. Set priority values (1.0 for homepage, 0.8 for services, 0.6 for blog)
4. Submit to Google Search Console AND Bing Webmaster Tools

## Page Speed & Core Web Vitals

### Target Metrics (2025)

| Metric | Target | Importance |
|--------|--------|------------|
| **LCP** (Largest Contentful Paint) | < 2.5 seconds | User experience, SEO ranking |
| **INP** (Interaction to Next Paint) | < 200ms | Engagement, bounce rate |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Visual stability |

### Recommended Optimizations

**Image Optimization:**
- Convert all images to WebP format
- Implement lazy loading for below-fold images
- Add explicit width/height attributes to prevent CLS
- Compress hero images (target: under 100KB)

**JavaScript/CSS Optimization:**
- Defer non-critical JavaScript
- Inline critical CSS
- Remove unused CSS from page builder
- Minify all assets

**Caching Implementation:**
```
Recommended Plugins:
1. WP Rocket (premium) - Best overall performance
2. LiteSpeed Cache (free) - If on LiteSpeed server
3. W3 Total Cache (free) - Comprehensive free option
```

**Server-Side:**
- Enable GZIP compression
- Implement browser caching headers
- Consider CDN (Cloudflare free tier)

## Mobile Optimization

**Current Status:** Responsive design detected

**Recommendations:**
- Test all forms on mobile devices
- Ensure tap targets are 48px minimum
- Verify phone numbers are click-to-call
- Test booking flow on mobile
- Check font sizes (minimum 16px body text)

## URL Structure & Internal Linking

**Current URL Patterns:**
- `/our-team/` - Good
- `/faq/` - Good
- `/blog/` - Good
- `/the-best-sleep-diary-app-for-tracking-sleep/` - Too long

**Recommendations:**
- Shorten blog URLs: `/blog/best-sleep-diary-app/`
- Create hub pages for topic clusters
- Add breadcrumb navigation
- Implement related posts functionality
- Cross-link team members to their authored content

---

# UX/UI Analysis

## Navigation & Information Architecture

### Current Structure
```
Home
├── Our Team
├── Events
│   └── Low Carb Dinner with Ron Schweitzer
├── Blog
├── Videos
├── FAQ
└── Contact

CTA: Coaching Session
```

### Recommended Structure
```
Home
├── About Us
│   ├── Our Story
│   ├── Our Team
│   └── Our Approach
├── Services
│   ├── Free 15-Min Consultation
│   ├── Individual Coaching
│   ├── Group Programs
│   └── Corporate Wellness
├── Conditions We Help
│   ├── Type 2 Diabetes
│   ├── Weight Loss
│   ├── PCOS & Fertility
│   ├── Mental Health
│   └── Heart Health
├── Resources
│   ├── Blog
│   ├── Videos
│   ├── FAQ
│   └── Recipes
├── Events
└── Contact

Primary CTA: Book Free Consultation
Secondary CTA: Take Health Quiz
```

## Homepage Analysis

### Above the Fold Content

**Current:**
- H1: "Kick Sugar, Go KETO, Join the 'I Feel Amazing' Club"
- CTA: "Coaching Session"

**Issues:**
- H1 is catchy but not SEO-optimized
- No clear value proposition
- No trust signals immediately visible
- No credentials shown

**Recommended Above-the-Fold Elements:**
1. Clear H1 with primary keywords
2. Subheadline explaining the value proposition
3. Trust badges (credentials, media features)
4. Primary CTA with urgency element
5. Social proof (testimonial snippet or stats)

**Example Redesign:**
```
H1: Expert Low-Carb & Keto Coaching in Victoria, Australia

Subheadline: Our team of doctors, dietitians, and certified coaches
have helped hundreds reverse type 2 diabetes and achieve lasting weight loss.

Trust Badges: [Featured on SBS] [Medical Team] [10+ Years Experience]

CTA: Book Your Free 15-Minute Consultation

Social Proof: "Lost 30kg in 5 months" - Christine & Warwick, Melbourne
```

## User Journey Optimization

### Current Journey Issues

| Step | Current Problem | User Impact |
|------|-----------------|-------------|
| 1. Arrival | No clear value proposition | Confusion, bounce |
| 2. Understanding | Services scattered across page | Frustration |
| 3. Trust-building | Credentials not prominent | Skepticism |
| 4. Decision | Single CTA type | Limited options |
| 5. Conversion | External booking link | Friction |

### Recommended User Journeys

**Journey A: Information Seeker**
```
Homepage → Conditions Page → Team Credentials → FAQ → Book Consultation
```

**Journey B: Ready to Act**
```
Homepage → Services → Testimonials → Book Consultation
```

**Journey C: Researcher**
```
Blog Post → Related Articles → Team Profile → Services → Book Consultation
```

## Call-to-Action Optimization

### Current CTAs Found
- "REGISTER HERE" (events)
- "FREE 15-Minute Coaching" (repeated)
- "Click Here for FREE 15-Minute Coaching Session"

### CTA Improvement Recommendations

| Location | Current | Recommended |
|----------|---------|-------------|
| Header | "Coaching Session" | "Book Free Consultation" |
| Homepage Hero | Generic text link | Button: "Start Your Health Journey - Free" |
| Blog Posts | None | "Questions? Book a Free 15-Min Chat" |
| Footer | None | "Ready to Transform Your Health?" |
| Exit Intent | None | Popup: "Get Our Free Keto Starter Guide" |

### CTA Button Design Best Practices
- High contrast colors (avoid grey)
- Action-oriented text (Start, Get, Book, Discover)
- Sufficient padding (min 12px vertical, 24px horizontal)
- Mobile-friendly size (min 44px tap target)
- Clear hover/active states

## Trust Signal Enhancement

### Current Trust Signals
- SBS Insight feature mention
- Team credentials (buried in profiles)
- Testimonials (not prominently displayed)
- Physical address in footer

### Recommended Trust Architecture

**Above the Fold:**
```
[As Seen On: SBS Insight]  [Medical Team Led]  [Est. 2018]
```

**Throughout Site:**
- Media mention logos
- Patient count or success metrics
- Professional association memberships
- "Medically Reviewed" badges on health content
- Real patient video testimonials
- Before/after results (with permission)

---

# Content Strategy Assessment

## Current Content Audit

### Blog Content Analysis

| Post Title | SEO Potential | AI Citation Potential | Status |
|------------|---------------|----------------------|--------|
| Insulin Resistance: The Hidden Cause | HIGH | HIGH | Needs optimization |
| Time Restricted Feeding | MEDIUM | HIGH | Needs structure |
| Menopause: Health Risks | HIGH | HIGH | Needs author byline |
| Olive Oil's Effects | MEDIUM | MEDIUM | Add statistics |
| Low Carb Yeast Bread | LOW | LOW | Recipe schema needed |
| Best Sleep Diary App | LOW | LOW | Update for 2025 |

### Content Gaps Identified

**High-Priority Topics Not Covered:**
1. "What is a keto diet?" (definitive guide)
2. "Low carb diet for beginners Australia"
3. "How to reverse type 2 diabetes naturally"
4. "Keto diet meal plan Australia"
5. "Low carb dietitian near me" (local landing page)
6. "LCHF diet benefits and risks"
7. "Ketogenic diet for PCOS"
8. "Low carb diet for weight loss over 50"

**Question-Based Content Needed:**
- How many carbs per day for ketosis?
- Is the keto diet safe long-term?
- What can I eat on a low-carb diet?
- How long does it take to get into ketosis?
- Can diabetics do the keto diet?

## Content Quality Standards for YMYL

### Required Elements for Health Content

Every health-related article MUST include:

1. **Author Attribution**
   ```
   Written by: [Name], [Credentials]
   Reviewed by: Dr. [Name], [Specialty]
   Last Updated: [Date]
   ```

2. **Medical Disclaimer**
   ```
   This information is for educational purposes only and is not
   intended as medical advice. Please consult your healthcare
   provider before making dietary changes.
   ```

3. **Source Citations**
   - Link to peer-reviewed studies
   - Reference reputable health organizations
   - Cite specific statistics with sources

4. **Clear Structure**
   - Table of contents for long articles
   - H2/H3 hierarchy
   - Bulleted key takeaways
   - TL;DR summary at top

### Example: Optimized Article Structure

```markdown
# How to Reverse Type 2 Diabetes with a Low-Carb Diet

**Written by:** Dr. John Stewart, BVSc | Wellness Coach
**Medically Reviewed by:** Dr. Glen Davies, FRACGP
**Last Updated:** December 2025
**Reading Time:** 12 minutes

## Key Takeaways
- Type 2 diabetes can often be reversed through dietary intervention
- Low-carb diets reduce insulin requirements by 50-90% in many cases
- The Virta Health study showed 60% of participants reversed diabetes

## Table of Contents
1. [Understanding Type 2 Diabetes](#understanding)
2. [How Low-Carb Diets Work](#how-it-works)
3. [Scientific Evidence](#evidence)
4. [Getting Started Safely](#getting-started)
5. [FAQs](#faqs)

---

## Understanding Type 2 Diabetes {#understanding}

[Content with citations]

**Source:** American Diabetes Association, 2024

---

## FAQs {#faqs}

### Can type 2 diabetes be reversed?
Yes, research shows that type 2 diabetes can be reversed in many
cases through significant weight loss and dietary changes. A 2019
study in The Lancet found that 46% of participants achieved
remission after one year of a low-calorie intervention.

[Continue with schema-ready Q&A format]
```

## Content Calendar Recommendation

### Monthly Publishing Schedule

| Week | Content Type | Topic Focus |
|------|--------------|-------------|
| 1 | Pillar Article | Comprehensive guide (2000+ words) |
| 2 | FAQ Expansion | 5 new Q&As for FAQ page |
| 3 | Success Story | Patient case study |
| 4 | Quick Tips | Practical advice post |

### Quarterly Content Initiatives

| Quarter | Initiative | Goal |
|---------|------------|------|
| Q1 | Condition-Specific Guides | 4 pillar pages (Diabetes, Weight Loss, PCOS, Mental Health) |
| Q2 | Video Content Expansion | 12 educational videos with transcripts |
| Q3 | Recipe Library | 20 keto recipes with schema markup |
| Q4 | Research Roundups | Quarterly evidence summaries |

---

# AI Search Optimization (AEO)

## Understanding AI Search in 2025

### The Landscape

| Platform | Daily Searches | Key Characteristics |
|----------|---------------|---------------------|
| **ChatGPT** | 37.5 million | Conversational, citation-focused |
| **Google AI Overviews** | 16% of searches | Integrated with traditional SERP |
| **Perplexity AI** | Growing rapidly | Source-heavy, real-time data |
| **Bing Copilot** | Microsoft ecosystem | Strong for B2B queries |

### Why This Matters

- **60% of searches** now end without a click (zero-click)
- **25% of organic traffic** expected to shift to AI by 2026 (Gartner)
- **Top Bing result appears in ChatGPT** 63% of the time
- AI systems favor **structured, citable content**

## Current AI Search Readiness: CRITICAL

### Assessment Results

| Factor | Current Score | Notes |
|--------|---------------|-------|
| Structured Data | 1/10 | Minimal schema present |
| Content Format | 3/10 | Long paragraphs, no clear answers |
| Author Authority | 2/10 | Credentials hidden |
| Citation Worthiness | 3/10 | No statistics, few sources |
| Update Frequency | 4/10 | Content appears dated |
| Brand Mentions | 2/10 | Minimal online presence |

## AEO Implementation Strategy

### 1. Content Structure for AI Citation

**Transform Content from This:**
```
The ketogenic diet works by reducing carbohydrate intake which
lowers insulin levels and forces the body to burn fat for fuel
instead of glucose. This metabolic state called ketosis can help
with weight loss and improving blood sugar control.
```

**To This (AI-Optimized):**
```
## What is the Ketogenic Diet?

The ketogenic diet is a high-fat, low-carbohydrate eating plan
that shifts your body into a metabolic state called ketosis.

### How the Keto Diet Works

1. **Carbohydrate Restriction:** Limit carbs to 20-50g per day
2. **Increased Fat Intake:** 70-80% of calories from healthy fats
3. **Moderate Protein:** 20-25% of calories from protein
4. **Metabolic Shift:** Body switches from glucose to ketones for fuel

### Key Benefits (Research-Backed)

| Benefit | Evidence Level | Source |
|---------|---------------|--------|
| Weight Loss | Strong | Volek et al., 2019 |
| Blood Sugar Control | Strong | Virta Health Study |
| Reduced Inflammation | Moderate | Multiple RCTs |

> **Expert Insight:** "A well-formulated ketogenic diet can reduce
> HbA1c levels by 1-2% within 3 months." — Dr. John Stewart,
> Nutrition Science Group
```

### 2. Question-First Content Architecture

Create dedicated pages answering specific questions AI systems frequently receive:

**Priority Questions to Target:**

| Question | Search Volume | AI Frequency |
|----------|---------------|--------------|
| What is the keto diet? | HIGH | Very High |
| Is keto safe for diabetics? | HIGH | High |
| How to start a low carb diet? | HIGH | Very High |
| What are ketosis symptoms? | MEDIUM | High |
| Best foods for keto diet? | HIGH | Very High |
| How many carbs for ketosis? | MEDIUM | High |

**Page Template:**
```
URL: /faq/what-is-keto-diet/

# What is the Keto Diet?

[30-50 word direct answer paragraph]

## Quick Answer
The ketogenic (keto) diet is a low-carb, high-fat eating plan that
puts your body into ketosis, burning fat for fuel instead of carbs.

## Detailed Explanation
[Expanded content with subheadings]

## Key Facts
- Carb limit: 20-50g per day
- Typical macro ratio: 70% fat, 25% protein, 5% carbs
- Time to reach ketosis: 2-7 days
- Originally developed for epilepsy treatment in 1920s

## Related Questions
- [How long does it take to get into ketosis?](/faq/ketosis-timeline/)
- [Is the keto diet safe?](/faq/keto-diet-safety/)

## Sources
1. [Study Name](URL) - Journal, Year
2. [Organization](URL) - Publication Date
```

### 3. Expert Authority Amplification

AI systems heavily weight content from recognized experts.

**Action Items:**

**A. Create Comprehensive Author Pages**
```
URL: /team/dr-john-stewart/

# Dr. John Stewart, BVSc
## Wellness Coach | Nutrition Science Group

### Credentials
- Bachelor of Veterinary Science
- Certified in Low Carb Nutrition (Nutrition Network)
- 15+ years clinical experience
- Featured on SBS Insight

### Areas of Expertise
- Metabolic health optimization
- Type 2 diabetes reversal
- Ketogenic nutrition protocols

### Publications & Media
- [SBS Insight Interview](link)
- [Article Title](link)

### Philosophy
[200-word personal statement]

### Articles by Dr. Stewart
[Dynamic list of authored content]

### Book a Consultation
[CTA to booking]
```

**B. Add Schema Markup for People**
```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Dr. John Stewart",
  "jobTitle": "Wellness Coach",
  "worksFor": {
    "@type": "MedicalBusiness",
    "name": "Nutrition Science Group"
  },
  "alumniOf": "University Name",
  "hasCredential": [
    {
      "@type": "EducationalOccupationalCredential",
      "credentialCategory": "degree",
      "name": "Bachelor of Veterinary Science"
    }
  ],
  "knowsAbout": ["ketogenic diet", "metabolic health", "type 2 diabetes"],
  "sameAs": [
    "https://linkedin.com/in/...",
    "https://twitter.com/..."
  ]
}
```

### 4. Citation-Worthy Content Creation

**Elements That Get Cited:**

| Element | Why AI Cites It | Implementation |
|---------|-----------------|----------------|
| Statistics | Provides evidence | Add data points with sources |
| Expert Quotes | Adds authority | Include team member insights |
| Definitions | Answers directly | Write clear, citable definitions |
| Lists | Easy to extract | Use numbered/bulleted formats |
| Tables | Structured data | Compare options, show data |
| Original Research | Unique value | Survey patients, analyze outcomes |

**Example: Creating Citable Content**

**Before (Not Citable):**
> Our patients generally see good results with low-carb diets.

**After (Highly Citable):**
> In a review of 150 Nutrition Science Group clients over 12 months,
> 73% achieved their target weight loss goals, with an average
> reduction of 12kg. Type 2 diabetic patients saw average HbA1c
> reductions of 1.4%.

### 5. Technical Implementation for AI Crawlers

**Robots.txt Addition:**
```
# Explicitly allow AI search crawlers
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /
```

**Sitemap Enhancement:**
- Create separate sitemap for AI-priority content
- Include all FAQ pages
- Update `lastmod` when content is refreshed

### 6. Brand Mention Strategy

AI systems learn from brand mentions across the web.

**Actions:**
1. **Guest Post** on health/nutrition websites
2. **HARO/Qwoted Responses** - Answer journalist queries
3. **Podcast Appearances** - With show notes and transcripts
4. **Professional Directory Listings:**
   - HealthEngine.com.au
   - Nutrition Australia directory
   - Low Carb Down Under
   - Australasian Society of Lifestyle Medicine
5. **Wikipedia** - Create/update relevant articles (follow guidelines)
6. **Local Citations** - Yelp, Yellow Pages, True Local

---

# Local SEO Analysis

## Current Local Presence

### Business Information Consistency (NAP)

| Source | Name | Address | Phone |
|--------|------|---------|-------|
| Website Footer | Nutrition Science Group | 309 Army Road, Pakenham VIC 3810 | +61 425 310 625 |
| Schema Markup | The Nutrition Science Group | 309 Army Rd, VIC 3810 | Not found |
| Google Search Result | Nutrition Science Group | 309 Army Rd Pakenham | +61 425310625 |

**Issues Found:**
- Inconsistent "Road" vs "Rd" abbreviation
- Phone number formatting varies
- "The" prefix inconsistent

**Standardize To:**
```
Business Name: Nutrition Science Group
Address: 309 Army Road, Pakenham, VIC 3810, Australia
Phone: +61 425 310 625
Email: hello@nutritionsciencegroup.com
```

## Google Business Profile Optimization

### Required Actions

**1. Profile Completeness (Current: ~40% estimated)**

| Element | Status | Action |
|---------|--------|--------|
| Business Name | Needs verification | Standardize naming |
| Address | Present | Verify accuracy |
| Phone | Present | Make primary |
| Hours | Present | Verify current |
| Website | Present | Add UTM tracking |
| Description | Unknown | Write 750-char description |
| Categories | Likely incomplete | Add all relevant |
| Services | Unknown | List all offerings with prices |
| Photos | Unknown | Add 20+ professional photos |
| Posts | Unknown | Weekly posting schedule |
| Q&A | Unknown | Seed with common questions |
| Reviews | Unknown | Implement review strategy |

**2. Category Selection**

Primary Category: `Nutritionist`

Additional Categories:
- Health Consultant
- Weight Loss Service
- Dietitian
- Wellness Center
- Health Coach

**3. Business Description (Optimized)**

```
Nutrition Science Group is Victoria's trusted source for evidence-based
low-carb and ketogenic nutrition coaching. Led by a team of qualified
doctors, dietitians, and certified wellness coaches, we specialize in
helping clients reverse type 2 diabetes, achieve sustainable weight loss,
and optimize metabolic health.

Our approach combines the latest scientific research with personalized
coaching to help you transform your health. Services include free
15-minute consultations, individual coaching programs, and group workshops.

Featured on SBS Insight, our team has helped hundreds of Victorians
achieve lasting health improvements through nutrition science.

🔬 Evidence-based approach
👨‍⚕️ Medical professional team
📍 Pakenham, Victoria | Australia-wide telehealth
📞 Book your free consultation today
```

**4. Review Generation Strategy**

| Method | Implementation |
|--------|---------------|
| Post-Session Request | Email 24hrs after consultation |
| SMS Follow-up | 1 week after positive milestone |
| In-Office Signage | QR code to review page |
| Email Signature | Link to leave review |
| Thank You Cards | Printed QR codes |

**Review Response Templates:**

*5-Star Review:*
```
Thank you [Name] for sharing your experience! We're thrilled to hear
about your progress with [specific achievement mentioned]. Your
dedication to [specific action] has been inspiring. We look forward
to supporting you on your continued health journey. - Dr. John Stewart
```

*Negative Review:*
```
Thank you for your feedback, [Name]. We're sorry to hear your
experience didn't meet expectations. We take all feedback seriously
and would welcome the opportunity to discuss this further. Please
contact us at hello@nutritionsciencegroup.com so we can address your
concerns directly. - The NSG Team
```

**5. Google Posts Strategy**

| Week | Post Type | Content Example |
|------|-----------|-----------------|
| 1 | What's New | Latest blog post highlight |
| 2 | Offer | Free consultation promotion |
| 3 | Event | Upcoming workshop |
| 4 | Health Tip | Quick actionable advice |

### Local Landing Pages

Create suburb-specific pages:

```
/locations/pakenham-nutritionist/
/locations/melbourne-keto-coach/
/locations/victoria-low-carb-doctor/
```

**Template:**
```
# Keto Nutritionist in [Suburb], Victoria

Looking for expert ketogenic and low-carb nutrition coaching in
[Suburb]? Nutrition Science Group provides evidence-based nutrition
programs to help [Suburb] residents achieve lasting health
improvements.

## Our [Suburb] Services
- Free 15-minute health consultations
- Personalized nutrition coaching
- Type 2 diabetes reversal programs
- Weight loss support

## Why Choose Us
[Local credibility points]

## Serving [Suburb] and Surrounding Areas
[List nearby suburbs]

## Book Your Free Consultation
[Contact form + Google Maps embed]
```

### Local Schema Implementation

```json
{
  "@context": "https://schema.org",
  "@type": "MedicalBusiness",
  "name": "Nutrition Science Group",
  "description": "Evidence-based low-carb and ketogenic nutrition coaching in Victoria, Australia",
  "url": "https://nutritionsciencegroup.com",
  "telephone": "+61425310625",
  "email": "hello@nutritionsciencegroup.com",
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
    "latitude": -38.0752,
    "longitude": 145.4867
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "17:00"
    }
  ],
  "priceRange": "$$",
  "areaServed": [
    {"@type": "City", "name": "Melbourne"},
    {"@type": "State", "name": "Victoria"},
    {"@type": "Country", "name": "Australia"}
  ],
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Nutrition Services",
    "itemListElement": [
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "Free 15-Minute Consultation",
          "description": "Initial health assessment with a nutrition coach"
        }
      },
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "Individual Coaching Program",
          "description": "Personalized low-carb nutrition coaching"
        }
      }
    ]
  }
}
```

---

# Competitive Analysis

## Competitor Overview

| Competitor | Strengths | Weaknesses | Opportunity |
|------------|-----------|------------|-------------|
| **Melbourne Low Carb Clinic** | Strong local SEO, Multiple locations, Medical doctor | Limited content marketing | Out-content them with educational resources |
| **The Low Carb Clinic** | Professional team page, Clear services, Media mentions | Generic content | Dominate condition-specific keywords |
| **Low Carb Keto Health** | Detailed programs, Price transparency | Adelaide-focused | Own Victorian market |
| **Keto Buddies** | Strong community aspect, Affordable | Less medical credibility | Emphasize your medical team |
| **Menu Concepts** | Large dietitian network, Insurance rebates | Corporate feel | Personal touch, story-driven content |

## Competitive Content Gap Analysis

### Keywords Competitors Own (You Don't)

| Keyword | Top Competitor | Your Ranking | Opportunity |
|---------|---------------|--------------|-------------|
| "low carb doctor melbourne" | Melbourne Low Carb Clinic | Not ranking | Create dedicated page |
| "keto dietitian victoria" | Multiple | Not ranking | Team credential pages |
| "reverse diabetes diet australia" | Various | Not ranking | Comprehensive guide |
| "metabolic health coaching" | Low Carb Keto Health | Not ranking | Service page optimization |

### Content Competitors Are Missing

**Opportunities to Lead:**
1. Video content library (transcribed for SEO)
2. Patient success story database
3. Research summaries and evidence reviews
4. Condition-specific microsites
5. Interactive tools (carb calculator, keto readiness quiz)
6. Local event marketing content

## Differentiation Strategy

### Your Unique Advantages

1. **Diverse Expertise Team** - Doctors, dietitians, OT, researcher
2. **SBS Media Feature** - National credibility
3. **Published Authors** - Dr. Popovic, Peter Symons
4. **Research Connection** - PhD candidate on team
5. **Local Community Events** - In-person engagement

### Messaging Differentiation

**Current (Generic):**
> "We help people with low-carb eating"

**Recommended (Differentiated):**
> "Victoria's only nutrition practice combining medical expertise,
> published researchers, and certified coaches—all practicing what
> we teach. Featured on SBS Insight, our evidence-based approach has
> helped hundreds reverse chronic disease through nutrition science."

---

# Implementation Roadmap

## Phase 1: Foundation (Weeks 1-4)

### Week 1: Critical Technical Fixes

| Task | Owner | Tools Needed |
|------|-------|--------------|
| Set up Google Search Console | Dev | Google account |
| Submit sitemap, request indexing | Dev | GSC |
| Fix homepage meta description | Content | WordPress/Yoast |
| Install Yoast SEO or Rank Math | Dev | WordPress |
| Update robots.txt with AI crawlers | Dev | FTP access |
| Update copyright to 2025 | Dev | Theme settings |
| Standardize NAP across site | Content | Manual review |

### Week 2: Schema Markup Implementation

| Schema Type | Pages | Priority |
|-------------|-------|----------|
| Organization | Homepage | Critical |
| MedicalBusiness | Homepage | Critical |
| LocalBusiness | All pages | Critical |
| Person | Team pages | High |
| FAQPage | FAQ page | High |
| Article | Blog posts | High |

### Week 3: Google Business Profile

| Task | Status |
|------|--------|
| Claim/verify GBP listing | Required |
| Complete all profile sections | Required |
| Add 20+ photos | Required |
| Write optimized description | Required |
| Set up categories properly | Required |
| Create first Google Post | Required |

### Week 4: Content Foundation

| Task | Deliverable |
|------|-------------|
| Create author bio boxes | Template for all posts |
| Add medical review badges | Visual trust signal |
| Update 3 highest-potential posts | Optimized for snippets |
| Create "Medically Reviewed" process | Internal workflow |

---

## Phase 2: Content & Authority (Weeks 5-12)

### Content Publishing Schedule

| Week | Content Piece | Target Keyword |
|------|---------------|----------------|
| 5 | Ultimate Keto Diet Guide | keto diet australia |
| 6 | Type 2 Diabetes Reversal Guide | reverse diabetes naturally |
| 7 | 5 FAQ pages | various question keywords |
| 8 | Low Carb for Beginners | low carb diet beginners |
| 9 | Keto for PCOS | keto pcos australia |
| 10 | Success Story Collection | (brand searches) |
| 11 | Video Transcripts (5) | various |
| 12 | Local Landing Pages (3) | suburb + service keywords |

### Authority Building Activities

| Activity | Frequency | Goal |
|----------|-----------|------|
| Guest posts | 2/month | Backlinks, brand mentions |
| HARO responses | 3/week | Media citations |
| Directory submissions | 10 total | NAP consistency, citations |
| Review generation | Ongoing | 2-3 new reviews/month |
| Google Posts | Weekly | Local visibility |

---

## Phase 3: Optimization & Scale (Weeks 13-24)

### Advanced SEO Initiatives

| Initiative | Timeline | Expected Impact |
|------------|----------|-----------------|
| Core Web Vitals optimization | Week 13-14 | Better rankings, UX |
| Internal linking audit | Week 15 | Improved crawlability |
| Competitor backlink analysis | Week 16 | Link opportunities |
| Featured snippet optimization | Week 17-20 | Position zero results |
| AI citation monitoring | Ongoing | AEO visibility |

### Content Expansion

| Content Type | Volume | Focus |
|--------------|--------|-------|
| Blog posts | 2/month | Long-tail keywords |
| Video content | 4/month | YouTube SEO |
| Case studies | 1/month | Social proof |
| Recipes | 4/month | Recipe schema |
| Research roundups | Quarterly | Authority content |

### Performance Monitoring

**Weekly Metrics:**
- Google Search Console impressions/clicks
- Rankings for target keywords
- Website traffic by source

**Monthly Metrics:**
- Indexed page count
- Featured snippet ownership
- Local pack appearances
- Review count and rating
- Conversion rate (consultations booked)

**Quarterly Metrics:**
- AI citation monitoring (manual checks)
- Backlink profile growth
- Content performance analysis
- Competitor ranking comparison

---

# Appendices

## Appendix A: Complete Schema Markup Code

### Homepage Organization + MedicalBusiness Schema

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://nutritionsciencegroup.com/#organization",
      "name": "Nutrition Science Group",
      "url": "https://nutritionsciencegroup.com",
      "logo": {
        "@type": "ImageObject",
        "url": "https://nutritionsciencegroup.com/logo.png"
      },
      "sameAs": [
        "https://www.facebook.com/nutritionsciencegroup",
        "https://www.linkedin.com/company/nutritionsciencegroup",
        "https://www.youtube.com/@nutritionsciencegroup",
        "https://www.instagram.com/nutritionsciencegroup"
      ]
    },
    {
      "@type": "MedicalBusiness",
      "@id": "https://nutritionsciencegroup.com/#medicalbusiness",
      "name": "Nutrition Science Group",
      "description": "Evidence-based low-carb and ketogenic nutrition coaching helping Australians reverse type 2 diabetes and achieve lasting weight loss.",
      "url": "https://nutritionsciencegroup.com",
      "telephone": "+61425310625",
      "email": "hello@nutritionsciencegroup.com",
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
        "latitude": -38.0752,
        "longitude": 145.4867
      },
      "openingHoursSpecification": [
        {
          "@type": "OpeningHoursSpecification",
          "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
          "opens": "09:00",
          "closes": "17:00"
        }
      ],
      "priceRange": "$$",
      "image": "https://nutritionsciencegroup.com/hero-image.jpg"
    },
    {
      "@type": "WebSite",
      "@id": "https://nutritionsciencegroup.com/#website",
      "url": "https://nutritionsciencegroup.com",
      "name": "Nutrition Science Group",
      "publisher": {
        "@id": "https://nutritionsciencegroup.com/#organization"
      }
    }
  ]
}
</script>
```

### FAQ Page Schema

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is ketosis?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Ketosis is a metabolic state where your body burns fat for fuel instead of carbohydrates. This occurs when carbohydrate intake is reduced to approximately 20-50 grams per day. Blood ketone levels of 1.0-3.0 mmol/L indicate nutritional ketosis."
      }
    },
    {
      "@type": "Question",
      "name": "Is saturated fat bad for heart disease?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Recent meta-analyses have found no significant association between saturated fat intake and cardiovascular disease. The Nutrition Science Group recommends focusing on eliminating trans fats and processed seed oils while including healthy fats from sources like extra virgin olive oil, avocados, and fatty fish."
      }
    },
    {
      "@type": "Question",
      "name": "How do I measure my ketone levels?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Blood ketone testing is the most accurate method to confirm ketosis. Using a blood ketone meter (such as Abbott or Genesis Biotech devices), target readings of 1.0-3.0 mmol/L indicate nutritional ketosis. Urine strips are less accurate but can be useful for beginners."
      }
    }
  ]
}
</script>
```

### Article Schema Template

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How to Reverse Type 2 Diabetes with a Low-Carb Diet",
  "description": "Evidence-based guide to reversing type 2 diabetes through low-carb and ketogenic nutrition.",
  "image": "https://nutritionsciencegroup.com/article-image.jpg",
  "author": {
    "@type": "Person",
    "name": "Dr. John Stewart",
    "url": "https://nutritionsciencegroup.com/team/dr-john-stewart/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Nutrition Science Group",
    "logo": {
      "@type": "ImageObject",
      "url": "https://nutritionsciencegroup.com/logo.png"
    }
  },
  "datePublished": "2025-01-15",
  "dateModified": "2025-12-01",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://nutritionsciencegroup.com/blog/reverse-type-2-diabetes/"
  }
}
</script>
```

### Person Schema (Team Member)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Dr. John Stewart",
  "jobTitle": "Wellness Coach",
  "description": "Wellness coach specializing in metabolic health, ketogenic nutrition, and type 2 diabetes reversal.",
  "image": "https://nutritionsciencegroup.com/team/john-stewart.jpg",
  "url": "https://nutritionsciencegroup.com/team/dr-john-stewart/",
  "worksFor": {
    "@type": "MedicalBusiness",
    "name": "Nutrition Science Group"
  },
  "alumniOf": {
    "@type": "EducationalOrganization",
    "name": "University Name"
  },
  "hasCredential": [
    {
      "@type": "EducationalOccupationalCredential",
      "name": "Bachelor of Veterinary Science (BVSc)",
      "credentialCategory": "degree"
    },
    {
      "@type": "EducationalOccupationalCredential",
      "name": "Low Carb Nutrition Certification",
      "credentialCategory": "certificate",
      "recognizedBy": {
        "@type": "Organization",
        "name": "Nutrition Network"
      }
    }
  ],
  "knowsAbout": [
    "Ketogenic Diet",
    "Metabolic Health",
    "Type 2 Diabetes",
    "Low-Carb Nutrition",
    "Intermittent Fasting"
  ]
}
</script>
```

---

## Appendix B: Meta Description Templates

### Homepage
```
Expert keto & low-carb nutrition coaching in Victoria, Australia. Our medical team helps reverse type 2 diabetes & achieve lasting weight loss. Free 15-min consultation. ☎️ 0425 310 625
```
(155 characters)

### Team Page
```
Meet the Nutrition Science Group team: doctors, dietitians & certified coaches helping Victorians achieve metabolic health through evidence-based nutrition.
```
(156 characters)

### Blog Post Template
```
[Topic]: Learn how [benefit] with expert guidance from Nutrition Science Group. Evidence-based advice from our medical team. Read our complete guide.
```

### FAQ Page
```
Get answers to common keto & low-carb diet questions from Nutrition Science Group's medical team. Expert advice on ketosis, diabetes, weight loss & more.
```
(154 characters)

### Service Page Template
```
[Service Name] in Victoria, Australia. Personalized [benefit] with Nutrition Science Group's qualified [practitioners]. Book your free consultation today.
```

---

## Appendix C: Content Brief Templates

### Pillar Content Brief

```markdown
# Content Brief: [Topic]

## Target Keyword: [primary keyword]
## Secondary Keywords: [3-5 related terms]
## Search Intent: Informational/Commercial/Transactional
## Word Count Target: 2,500-3,500 words

## Audience
- Primary: [demographic]
- Pain points: [list]
- Questions they have: [list]

## Article Structure

### H1: [Optimized title with primary keyword]

### Introduction (150-200 words)
- Hook with statistic or question
- Define the problem
- Preview what reader will learn
- Include primary keyword naturally

### H2: [Section 1 - Definition/Overview]
- Clear definition paragraph (40-60 words)
- Bullet point breakdown
- Expert quote from team member

### H2: [Section 2 - How It Works]
- Step-by-step process
- Numbered list format
- Supporting evidence with citation

### H2: [Section 3 - Benefits/Evidence]
- Table comparing options/results
- Statistics with sources
- Research summary

### H2: [Section 4 - Getting Started]
- Actionable steps
- Practical tips
- Common mistakes to avoid

### H2: Frequently Asked Questions
- 5-7 questions in Q&A format
- Direct, concise answers
- Schema markup ready

### Conclusion + CTA
- Summary of key points
- Clear next step
- Link to consultation booking

## Required Elements
- [ ] Author byline with credentials
- [ ] Medical review badge
- [ ] Last updated date
- [ ] 3+ internal links
- [ ] 3+ external citations
- [ ] 1+ data table
- [ ] 1+ expert quote
- [ ] Featured image with alt text
- [ ] Meta description (150-160 chars)

## SEO Checklist
- [ ] Primary keyword in H1
- [ ] Primary keyword in first 100 words
- [ ] Primary keyword in meta description
- [ ] Secondary keywords in H2s
- [ ] Image alt text includes keyword
- [ ] URL slug optimized
```

---

## Appendix D: Recommended Tools & Plugins

### WordPress Plugins

| Plugin | Purpose | Priority |
|--------|---------|----------|
| Yoast SEO or Rank Math | SEO management, schema | Critical |
| WP Rocket or LiteSpeed Cache | Performance | High |
| ShortPixel or Imagify | Image optimization | High |
| Schema Pro | Advanced schema markup | Medium |
| TablePress | Structured data tables | Medium |
| MonsterInsights | Google Analytics | Medium |
| Wordfence | Security | High |

### SEO & Analytics Tools

| Tool | Purpose | Cost |
|------|---------|------|
| Google Search Console | Index monitoring | Free |
| Google Analytics 4 | Traffic analysis | Free |
| Bing Webmaster Tools | Bing indexing | Free |
| Ahrefs or Semrush | Keyword research, backlinks | Paid |
| Screaming Frog | Technical audits | Free/Paid |
| PageSpeed Insights | Core Web Vitals | Free |

### AI Search Monitoring

| Tool | Purpose |
|------|---------|
| Manual ChatGPT queries | Check citation frequency |
| Perplexity searches | Monitor AI visibility |
| Google AI Overviews | Check for inclusion |

---

## Appendix E: Key Performance Indicators (KPIs)

### Monthly Dashboard Metrics

| Metric | Baseline | 3-Month Target | 6-Month Target |
|--------|----------|----------------|----------------|
| Indexed Pages | 2 | 30 | 75 |
| Organic Sessions | TBD | +100% | +300% |
| Organic Clicks (GSC) | TBD | +150% | +400% |
| Impressions (GSC) | TBD | +200% | +500% |
| Average Position | TBD | Top 20 | Top 10 |
| Featured Snippets | 0 | 5 | 15 |
| GBP Views | TBD | +200% | +500% |
| Reviews (Total) | TBD | +10 | +25 |
| Consultations Booked | TBD | +50% | +150% |

### AI Search KPIs (New Metrics)

| Metric | How to Measure | Target |
|--------|----------------|--------|
| ChatGPT Citations | Monthly manual audit | 5+ mentions |
| Perplexity Citations | Monthly manual audit | 3+ mentions |
| Brand Mention Growth | Google Alerts | +20%/quarter |

---

## Appendix F: Sources & References

### AI Search Optimization
- [CXL: Answer Engine Optimization Guide 2025](https://cxl.com/blog/answer-engine-optimization-aeo-the-comprehensive-guide-for-2025/)
- [Neil Patel: Answer Engine Optimization](https://neilpatel.com/blog/answer-engine-optimization/)
- [Backlinko: AEO Guide](https://backlinko.com/answer-engine-optimization-aeo)
- [How to Appear in ChatGPT Answers](https://www.seo.com/ai/how-to-appear-in-chatgpt-answers/)
- [Rank Math: ChatGPT Search Indexing](https://rankmath.com/kb/indexing-in-chatgpt-search/)

### Healthcare SEO & Schema
- [Healthcare Success: Schema Markup Guide](https://healthcaresuccess.com/blog/seo/schema-markup-healthcare.html)
- [Schema.org: Health and Medical Types](https://schema.org/docs/meddocs.html)
- [Healthcare E-E-A-T Guidelines](https://healthcaresuccess.com/blog/healthcare-marketing/google-e-a-t-and-healthcare-content-how-to-deliver-the-quality-google-demands.html)

### Local SEO Australia
- [Local SEO for Australian Medical Practices 2025](https://kodedigital.com.au/2025/09/19/local-seo-for-australian-medical-practices-dominate-your-suburb-in-2025/)
- [Birdeye: Local SEO Australia Guide](https://birdeye.com/blog/local-seo-australia/)
- [Healthcare SEO Complete Guide 2025](https://www.balmeragency.com.au/healthcare-seo-in-australia-the-complete-2025-guide-for-medical-practices/)

### Core Web Vitals
- [WP Beginner: Core Web Vitals Guide](https://www.wpbeginner.com/wp-tutorials/how-to-optimize-core-web-vitals-for-wordpress-ultimate-guide/)
- [Elementor: Page Speed Optimization](https://elementor.com/blog/page-speed-optimization-for-wordpress/)

### Featured Snippets
- [Search Engine Land: Featured Snippet Optimization](https://searchengineland.com/google-featured-snippets-optimization-guidelines-389951)
- [Backlinko: Featured Snippets Guide](https://backlinko.com/hub/seo/featured-snippets)

---

**End of Audit Report**

*This comprehensive audit was prepared to provide actionable insights for improving the Nutrition Science Group's digital presence, with particular emphasis on emerging AI search optimization strategies. Implementation of these recommendations should be prioritized according to the roadmap provided.*

*For questions or clarification on any recommendations, please contact the audit team.*

---

**Document Version:** 1.0
**Created:** December 8, 2025
**Classification:** Strategic Planning Document
