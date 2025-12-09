---
description: Complete website audit with AI reality check, technical testing, competitor analysis, and branded PDF report
---

# Yes AI Complete Website Audit

**Usage:** `/yesai-full-audit [website-url]`

Example: `/yesai-full-audit animalexpertwitness.com.au`

This command performs a comprehensive website audit including:
- Live technical testing (speed, mobile, SSL, broken links)
- AI Search Reality Check (what ChatGPT/Perplexity say about the business)
- Deep competitor analysis
- Full UX, SEO, and AEO audit
- Schema markup validation and generation
- Accessibility quick check
- Ready-to-implement deliverables
- Professional Yes AI branded PDF
- Draft email to send with report

---

## PHASE 1: SETUP

### Step 1.1: Get Website URL
Prompt user if not provided:
```
What website would you like me to audit?
Enter the full URL (e.g., example.com.au):
```

### Step 1.2: Create Client Folder
```bash
# Convert website to folder name (kebab-case, no TLD)
# example.com.au → example
# royal-crest-blinds.com.au → royal-crest-blinds

mkdir -p "C:/Users/peter/Downloads/CC/CLIENTS/[client-folder]"
```

### Step 1.3: Fetch Client Logo
```bash
# Try multiple logo detection patterns
curl -s -L "https://[website]" | grep -i -oE 'src="[^"]*\.(png|jpg|svg)[^"]*"' | head -10

# Download best match
curl -s -L -o "[client-folder]/client_logo.png" "[LOGO_URL]"
```

If logo fetch fails, proceed without and note in output.

---

## PHASE 2: WEBSITE DISCOVERY & CONTENT ANALYSIS

### Step 2.1: Crawl All Key Pages
Use WebFetch on each page, extract and document:

| Page | What to Extract |
|------|-----------------|
| Homepage | Hero messaging, CTAs, value proposition, navigation structure |
| About | Company story, team info, credentials, E-E-A-T signals |
| Services/Products | Offerings, pricing hints, unique selling points |
| Contact | NAP (Name, Address, Phone), forms, response promises |
| FAQs | Question/answer pairs, topic coverage |
| Testimonials | Review content, client names, credentials |
| Blog/Resources | Content topics, publishing frequency, depth |
| Any other key pages | Document purpose and content quality |

### Step 2.2: Document Site Structure
Create inventory of:
- All pages found (with URLs)
- Navigation structure
- Internal linking patterns
- 404 errors encountered
- Redirect chains found

---

## PHASE 3: LIVE TECHNICAL TESTING

### Step 3.1: Page Speed Analysis
```bash
# Fetch Google PageSpeed Insights (if API available)
# Otherwise, use WebFetch to get PageSpeed results page
```

Use WebFetch on: `https://pagespeed.web.dev/analysis?url=https://[website]`

Extract and document:
- Performance score (mobile & desktop)
- Largest Contentful Paint (LCP)
- First Input Delay (FID) / Interaction to Next Paint (INP)
- Cumulative Layout Shift (CLS)
- First Contentful Paint (FCP)
- Time to First Byte (TTFB)
- Specific recommendations

### Step 3.2: SSL/Security Check
```bash
# Check SSL certificate
curl -sI "https://[website]" | head -20

# Check for security headers
curl -sI "https://[website]" | grep -iE "(strict-transport|content-security|x-frame|x-content-type)"
```

Document:
- SSL certificate valid? (Yes/No)
- HTTPS redirect working? (Yes/No)
- Security headers present? (list them)
- Mixed content warnings? (Yes/No)

### Step 3.3: Mobile Rendering Check
Use WebFetch with mobile context or document mobile considerations from page analysis.

Check for:
- Viewport meta tag present
- Responsive design indicators
- Touch-friendly navigation
- Mobile-specific issues

### Step 3.4: Sitemap & Robots.txt Analysis
```bash
# Fetch sitemap
curl -s "https://[website]/sitemap.xml" | head -100

# Fetch robots.txt
curl -s "https://[website]/robots.txt"
```

Document:
- Sitemap exists? (Yes/No)
- Number of URLs in sitemap
- Sitemap last modified date
- Robots.txt rules
- Any pages being blocked that shouldn't be

### Step 3.5: Broken Link Scan
While crawling pages, track all internal links and note:
- Links returning 404
- Links returning other errors
- Redirect chains (301/302)
- External links (sample check)

---

## PHASE 4: AI SEARCH REALITY CHECK

### Step 4.1: ChatGPT/Claude Knowledge Test
Query Claude (yourself) with these prompts and document responses:

**Query 1 - Direct Business Search:**
```
What do you know about [Business Name] in [Location]?
```

**Query 2 - Service Search:**
```
Who provides [main service] in [Location]? What are the best options?
```

**Query 3 - Expert Search (if applicable):**
```
Who are the leading experts in [niche] in Australia?
```

Document:
- Is the business mentioned? (Yes/No)
- How is it described?
- Are competitors mentioned instead?
- What information is missing or wrong?

### Step 4.2: Perplexity Search Simulation
Use WebSearch to find what information is publicly available:

```
Search: "[Business Name]" + "[main service]"
Search: "best [service] [location]"
Search: "[Business Name] reviews"
```

Document:
- What sources mention the business?
- What's the sentiment?
- Are there citation opportunities being missed?

### Step 4.3: AI Citation Gap Analysis
Based on findings, identify:
- Topics where business should be cited but isn't
- Competitor advantages in AI visibility
- Content gaps that prevent AI citation
- Entity recognition issues

---

## PHASE 5: COMPETITOR ANALYSIS

### Step 5.1: Identify Top Competitors
Use WebSearch:
```
Search: "[main service] [location]"
Search: "best [service] near [location]"
Search: "[service] Australia"
```

Identify top 3-5 competitors by:
- Search ranking
- Ad presence
- Review volume
- Content depth

### Step 5.2: Competitor Content Audit
For each top competitor, use WebFetch to analyze:

| Metric | Document |
|--------|----------|
| Homepage messaging | Value proposition, CTAs |
| Service pages | Depth, detail, unique angles |
| Blog/Resources | Topics, frequency, quality |
| FAQs | Number of questions, depth |
| Testimonials | Volume, quality, recency |
| Schema markup | What structured data they use |

### Step 5.3: Content Gap Analysis
Compare client vs competitors:
- Topics competitors cover that client doesn't
- Content depth comparison
- Keyword opportunities being missed
- Feature/service gaps

### Step 5.4: Competitive Positioning Matrix
Create comparison table:

| Factor | Client | Competitor 1 | Competitor 2 | Competitor 3 |
|--------|--------|--------------|--------------|--------------|
| Homepage clarity | Score 1-5 | | | |
| Service depth | Score 1-5 | | | |
| Trust signals | Score 1-5 | | | |
| Content volume | Score 1-5 | | | |
| Schema markup | Yes/No | | | |
| FAQ coverage | Score 1-5 | | | |

---

## PHASE 6: UX & CONTENT AUDIT

### Step 6.1: Navigation & Information Architecture
Evaluate:
- Primary navigation clarity (1-5)
- Mobile navigation usability (1-5)
- Footer navigation completeness (1-5)
- Breadcrumb presence (Yes/No)
- Search functionality (Yes/No)
- User journey clarity (1-5)

### Step 6.2: Homepage Effectiveness
Evaluate:
- Clear value proposition within 5 seconds (Yes/No)
- Primary CTA visible above fold (Yes/No)
- Trust signals visible (Yes/No)
- Contact info accessible (Yes/No)
- Mobile experience (1-5)

### Step 6.3: Content Quality Assessment
For each major page, score:

| Criteria | Score 1-5 | Notes |
|----------|-----------|-------|
| Clarity of messaging | | |
| Depth of information | | |
| Readability (sentence length, jargon) | | |
| Visual appeal | | |
| CTA effectiveness | | |
| E-E-A-T signals | | |

### Step 6.4: Trust Signal Inventory
Document all trust signals found:
- Testimonials (count, quality, recency)
- Credentials/certifications
- Awards/recognition
- Media mentions
- Professional affiliations
- Client logos
- Case studies
- Team credentials

### Step 6.5: CTA Inventory
List all CTAs across the site:

| Page | CTA Text | Destination | Effectiveness (1-5) |
|------|----------|-------------|---------------------|
| | | | |

---

## PHASE 7: SEO AUDIT

### Step 7.1: On-Page SEO Analysis
For each key page, extract and evaluate:

| Element | Current | Recommendation |
|---------|---------|----------------|
| Title tag | [extract] | [suggest improvement] |
| Meta description | [extract] | [suggest improvement] |
| H1 | [extract] | [evaluate] |
| H2-H6 structure | [document] | [evaluate hierarchy] |
| URL structure | [document] | [evaluate] |
| Image alt text | [sample] | [evaluate] |
| Internal links | [count] | [evaluate] |

### Step 7.2: Keyword Analysis
Identify:
- Primary keywords being targeted (explicit or implicit)
- Keyword gaps vs competitors
- Long-tail opportunities
- Local keyword opportunities
- Question-based keywords for FAQs

### Step 7.3: Schema Markup Validation
Check for existing structured data:
```bash
# Look for JSON-LD in page source
curl -s "https://[website]" | grep -o '<script type="application/ld+json">.*</script>'
```

Document:
- Schema types found
- Validation errors
- Missing recommended schema
- Priority schema to add

### Step 7.4: Local SEO Check (if applicable)
- Google Business Profile status
- NAP consistency across site
- Local keywords in content
- Service area clarity
- LocalBusiness schema present

---

## PHASE 8: ACCESSIBILITY QUICK CHECK

### Step 8.1: Image Alt Text Audit
Sample 10-20 images across the site:

| Image | Alt Text Present | Alt Text Quality (1-5) |
|-------|------------------|------------------------|
| | Yes/No | |

### Step 8.2: Heading Hierarchy Check
Document heading structure per page:
- Single H1 per page? (Yes/No)
- Logical H2-H6 hierarchy? (Yes/No)
- Headings describe content? (Yes/No)

### Step 8.3: Link Text Quality
Sample internal links:
- Descriptive link text used? (Yes/No)
- "Click here" patterns found? (list them)
- Links distinguishable from text? (Yes/No)

### Step 8.4: Form Accessibility
Check contact/lead forms:
- Labels associated with inputs? (Yes/No)
- Error messages clear? (Yes/No)
- Required fields indicated? (Yes/No)
- Keyboard navigable? (Yes/No)

---

## PHASE 9: READY-TO-IMPLEMENT DELIVERABLES

### Step 9.1: Meta Tags for All Pages
Generate complete, ready-to-copy meta tags:

```html
<!-- Homepage -->
<title>[Optimized title - 50-60 chars]</title>
<meta name="description" content="[Optimized description - 150-160 chars]">

<!-- About Page -->
<title>[Optimized title]</title>
<meta name="description" content="[Optimized description]">

<!-- [Continue for all pages] -->
```

### Step 9.2: Complete Schema JSON-LD Blocks
Generate ready-to-implement structured data:

```json
// Organization Schema
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Business Name]",
  "url": "https://[website]",
  "logo": "https://[website]/logo.png",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "[phone]",
    "contactType": "customer service"
  },
  "sameAs": [
    "[social media URLs]"
  ]
}

// LocalBusiness Schema (if applicable)
{
  "@context": "https://schema.org",
  "@type": "[specific business type]",
  "name": "[Business Name]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[address]",
    "addressLocality": "[city]",
    "addressRegion": "[state]",
    "postalCode": "[postcode]",
    "addressCountry": "AU"
  },
  "telephone": "[phone]",
  "url": "https://[website]"
}

// FAQPage Schema
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question 1]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer 1]"
      }
    }
    // Continue for all FAQs
  ]
}

// ProfessionalService Schema (if applicable)
{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "[Business Name]",
  "description": "[Description]",
  "areaServed": "[Service area]",
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Services",
    "itemListElement": [
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "[Service 1]"
        }
      }
    ]
  }
}

// Person Schema (for expert/team pages)
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "[Expert Name]",
  "jobTitle": "[Title]",
  "worksFor": {
    "@type": "Organization",
    "name": "[Business Name]"
  },
  "description": "[Bio summary]",
  "knowsAbout": ["[expertise 1]", "[expertise 2]"]
}

// Review Schema
{
  "@context": "https://schema.org",
  "@type": "Review",
  "reviewRating": {
    "@type": "Rating",
    "ratingValue": "5"
  },
  "author": {
    "@type": "Person",
    "name": "[Reviewer Name]"
  },
  "reviewBody": "[Review text]"
}
```

### Step 9.3: Content Briefs for New Pages
For each recommended new page, provide:

```markdown
## Content Brief: [Page Title]

**Target Keywords:** [primary], [secondary], [long-tail]

**Search Intent:** [informational/transactional/navigational]

**Recommended Word Count:** [X] words

**H1:** [Suggested headline]

**Outline:**
1. [Section 1 - what to cover]
2. [Section 2 - what to cover]
3. [Section 3 - what to cover]
4. FAQ section with [X] questions
5. CTA: [what action to drive]

**Key Points to Cover:**
- [Point 1]
- [Point 2]
- [Point 3]

**Internal Links to Include:**
- Link to [page 1]
- Link to [page 2]

**Schema to Add:** [FAQPage / Article / HowTo]
```

### Step 9.4: FAQ Content Suggestions
Generate draft FAQ content for gaps identified:

```markdown
## Suggested New FAQs

### Q: [Question based on search data]
A: [Draft answer - 50-100 words, comprehensive but concise]

### Q: [Question based on competitor analysis]
A: [Draft answer]

### Q: [Question based on AI search gaps]
A: [Draft answer]
```

### Step 9.5: Backlink Outreach Template
```markdown
Subject: [Collaboration opportunity / Resource suggestion]

Hi [Name],

I came across your article about [topic] on [their website] and found it really valuable.

I wanted to share a resource that might be useful for your readers - [client business] has published [specific content piece] that covers [relevant topic].

Given your audience's interest in [topic], I thought it might make a helpful addition to your article or a future piece.

Happy to discuss further if you're interested.

Best regards,
[Name]
```

---

## PHASE 10: IMPLEMENTATION ROADMAP

### Priority Matrix
Organize all recommendations into:

**CRITICAL (Week 1-2):**
- Items blocking SEO performance
- Items hurting user experience
- Quick wins with high impact

**HIGH PRIORITY (Week 3-4):**
- Schema markup implementation
- Key content gaps
- Technical fixes

**MEDIUM PRIORITY (Month 2):**
- Content expansion
- Competitor response items
- Enhancement opportunities

**ONGOING:**
- Content calendar items
- Link building activities
- Monitoring and optimization

### Implementation Checklist
Create checkbox list of all action items:

```markdown
## Week 1-2: Critical Fixes
- [ ] [Task 1]
- [ ] [Task 2]

## Week 3-4: High Priority
- [ ] [Task 1]
- [ ] [Task 2]

## Month 2: Medium Priority
- [ ] [Task 1]
- [ ] [Task 2]

## Ongoing Activities
- [ ] [Task 1]
- [ ] [Task 2]
```

---

## PHASE 11: CREATE AUDIT REPORT

### Step 11.1: Generate Markdown Report
Save comprehensive audit to:
```
C:\Users\peter\Downloads\CC\CLIENTS\[client-folder]\[CLIENT_NAME]_FULL_AUDIT_2025.md
```

Include all sections from Phases 2-10.

### Step 11.2: Create Professional HTML
Convert to branded HTML with Yes AI styling.

**Cover Page:**
- Yes AI logo (from: `C:\Users\peter\Downloads\CC\Yes AI Assets\YesAI_colors_punched_transparent6.png`)
- Title: "Complete Digital Audit & AI Search Optimization Report"
- Subtitle: "Technical analysis, competitive intelligence, and implementation roadmap"
- Client logo (if fetched)
- Client name and website
- Date: Current month/year
- Footer: Yes AI contact

**CSS Requirements (Critical for Clean PDF):**
```css
/* Page Setup */
@page { margin: 0; size: A4; }
@media print {
    .page { height: 297mm; width: 210mm; }
}

/* Logo Sizing */
.yesai-logo img { height: auto; width: auto; }
.cover-logo .yesai-logo img { max-height: 100px; }
.page-logo .yesai-logo img { max-height: 45px; }
.page-footer-logo img { max-height: 30px; }

/* CRITICAL: Page Break Prevention */
table, .info-box, .score-card, .timeline-item, .priority-grid,
.faq-item, .implementation-card, .feature-grid, .action-item,
h2, h3, h4, ul, ol, .keep-together {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
}

/* Force page breaks before major sections */
.page-break-before { page-break-before: always; break-before: page; }

/* Prevent orphans/widows */
p, li { orphans: 3; widows: 3; }

/* Compact Spacing (prevents blank areas) */
.page-content { padding: 15px 25px; }
h2 { font-size: 18px; margin: 15px 0 10px 0; }
h3 { font-size: 14px; margin: 12px 0 8px 0; }
p, li { font-size: 11px; line-height: 1.4; margin: 6px 0; }
table { font-size: 10px; margin: 10px 0; }
th, td { padding: 6px 8px; }
.info-box { padding: 10px 12px; margin: 10px 0; font-size: 11px; }

/* CRITICAL: Footer overlap prevention - content must not overlap fixed footer */
.content-page { padding: 25px 35px 70px 35px; } /* Extra 70px bottom padding for fixed footer */
.page-footer { position: absolute; bottom: 20px; left: 35px; right: 35px; }

/* Keep-together class for grouped content */
.keep-together {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
}
```

**All Logos Must Use `<img>` Tags:**
```html
<img src="file:///C:/Users/peter/Downloads/CC/Yes%20AI%20Assets/YesAI_colors_punched_transparent6.png" alt="Yes AI">
```

**Score Cards for Key Metrics:**
```html
<div class="score-grid keep-together">
    <div class="score-card">
        <div class="score-value">[X]/100</div>
        <div class="score-label">PageSpeed Mobile</div>
    </div>
    <div class="score-card">
        <div class="score-value">[X]/100</div>
        <div class="score-label">PageSpeed Desktop</div>
    </div>
    <div class="score-card">
        <div class="score-value">[X]/5</div>
        <div class="score-label">SEO Score</div>
    </div>
    <div class="score-card">
        <div class="score-value">[X]/5</div>
        <div class="score-label">AI Visibility</div>
    </div>
</div>
```

**Back Cover:**
- Large Yes AI logo (120px)
- "AI-Powered Digital Strategy" tagline
- Contact box: www.yesai.au | (03) 9999 7398 | hello@yesai.au

Save HTML to:
```
C:\Users\peter\Downloads\CC\CLIENTS\[client-folder]\[CLIENT_NAME]_FULL_AUDIT_2025.html
```

### Step 11.3: Create PDF Conversion Script
Create `html_to_pdf.py` in client folder:

```python
"""Convert HTML to PDF using Playwright"""
import asyncio
from pathlib import Path

async def convert_html_to_pdf():
    from playwright.async_api import async_playwright

    folder = Path("C:/Users/peter/Downloads/CC/CLIENTS/[client-folder]")
    html_path = folder / "[CLIENT_NAME]_FULL_AUDIT_2025.html"
    pdf_path = folder / "[CLIENT_NAME]_FULL_AUDIT_2025.pdf"

    print(f"Converting: {html_path}")
    print(f"Output: {pdf_path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f'file:///{html_path.as_posix()}')
        await page.wait_for_load_state('networkidle')

        # Wait for fonts and images to load
        await asyncio.sleep(3)

        await page.pdf(
            path=str(pdf_path),
            format='A4',
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )
        await browser.close()
        print(f"PDF created successfully: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(convert_html_to_pdf())
```

### Step 11.4: Generate PDF
```bash
cd C:\Users\peter\Downloads\CC\CLIENTS\[client-folder]
python html_to_pdf.py
```

### Step 11.5: Verify PDF Quality
Check:
- [ ] Cover page: Yes AI logo visible
- [ ] Cover page: Client logo visible (if fetched)
- [ ] All page headers: Yes AI logo
- [ ] All page footers: Yes AI logo + page numbers
- [ ] No content splitting across pages
- [ ] No large blank areas
- [ ] All tables render correctly
- [ ] Score cards display properly
- [ ] Schema code blocks readable
- [ ] Back cover: Large Yes AI logo

---

## PHASE 12: DRAFT EMAIL

### Step 12.1: Generate Email Draft
Save to: `C:\Users\peter\Downloads\CC\CLIENTS\[client-folder]\EMAIL_DRAFT.txt`

```
Subject: Your Complete Digital Audit & AI Search Optimization Report - [Business Name]

Hi [First Name],

I've completed a comprehensive digital audit of [website] and I'm excited to share the findings with you.

This isn't a typical website review. I've analyzed your site from three critical angles:

1. TRADITIONAL SEO & UX
   - Technical performance (your PageSpeed score is [X]/100)
   - User experience and conversion optimization
   - On-page SEO and content structure

2. AI SEARCH VISIBILITY (The New Frontier)
   - How ChatGPT, Google Gemini, and Perplexity describe your business
   - Citation gaps costing you AI-driven traffic
   - Strategies to become THE recommended answer

3. COMPETITIVE POSITIONING
   - How you stack up against [Competitor 1] and [Competitor 2]
   - Content gaps they're exploiting
   - Quick wins to leapfrog the competition

THE GOOD NEWS:
[Insert 2-3 positive findings - strengths to build on]

THE OPPORTUNITIES:
[Insert 2-3 key opportunities - framed positively]

WHAT'S INSIDE THE REPORT:
- Executive summary with priority scores
- Technical audit with specific fixes
- AI search reality check (what AI actually says about you)
- Competitor analysis matrix
- Ready-to-implement schema markup (just copy & paste)
- Optimized meta tags for every page
- Content briefs for recommended new pages
- 90-day implementation roadmap

I've prioritized everything so you know exactly what to tackle first for maximum impact.

Want to discuss the findings? I'm happy to jump on a quick call to walk through the highlights and answer any questions.

Best regards,

[Your Name]
Yes AI
(03) 9999 7398
hello@yesai.au
www.yesai.au

P.S. The AI search landscape is changing fast. Businesses that optimize for answer engines now will dominate when this becomes mainstream. Your report includes specific steps to get ahead of this curve.
```

---

## PHASE 13: COMMIT & REPORT

### Step 13.1: Git Commit
```bash
cd /c/Users/peter/Downloads/CC
git add .
git commit -m "Audit - [Client Name] complete digital audit with AI analysis from Yes AI"
git push
```

### Step 13.2: Final Output
```
============================================
YES AI COMPLETE DIGITAL AUDIT
============================================

Client: [Client Name]
Website: [website URL]
Folder: C:\Users\peter\Downloads\CC\CLIENTS\[client-folder]\

FILES CREATED:
--------------
- [CLIENT_NAME]_FULL_AUDIT_2025.md (comprehensive markdown)
- [CLIENT_NAME]_FULL_AUDIT_2025.html (branded HTML)
- [CLIENT_NAME]_FULL_AUDIT_2025.pdf (final deliverable)
- html_to_pdf.py (PDF conversion script)
- client_logo.png (if fetched)
- EMAIL_DRAFT.txt (ready to send)

KEY METRICS:
------------
PageSpeed Mobile: [X]/100
PageSpeed Desktop: [X]/100
SEO Score: [X]/5
AI Visibility: [X]/5
Competitor Position: [X] of [Y]

CRITICAL FINDINGS:
------------------
1. [Most important finding]
2. [Second most important finding]
3. [Third most important finding]

PDF LOCATION:
file:///C:/Users/peter/Downloads/CC/CLIENTS/[client-folder]/[CLIENT_NAME]_FULL_AUDIT_2025.pdf

EMAIL DRAFT:
file:///C:/Users/peter/Downloads/CC/CLIENTS/[client-folder]/EMAIL_DRAFT.txt

Client logo: [Fetched from website / Not available]
Yes AI branding: Applied to all pages

DONE DONE DONE
```

---

## YES AI ASSETS REFERENCE

| Asset | Location |
|-------|----------|
| Logo | `C:\Users\peter\Downloads\CC\Yes AI Assets\YesAI_colors_punched_transparent6.png` |
| Phone | (03) 9999 7398 |
| Email | hello@yesai.au |
| Website | www.yesai.au |

---

## QUALITY CHECKLIST

Before marking complete:

**Research Phase:**
- [ ] All key pages crawled and documented
- [ ] PageSpeed data retrieved
- [ ] SSL/security checked
- [ ] Sitemap and robots.txt analyzed
- [ ] Broken links documented
- [ ] AI search queries performed
- [ ] Top 3 competitors analyzed

**Analysis Phase:**
- [ ] UX scored and documented
- [ ] Content quality assessed
- [ ] SEO issues identified
- [ ] Schema opportunities listed
- [ ] Accessibility basics checked
- [ ] Competitive gaps identified

**Deliverables Phase:**
- [ ] Meta tags generated for all pages
- [ ] Schema JSON-LD blocks created
- [ ] Content briefs written
- [ ] FAQ suggestions drafted
- [ ] Implementation roadmap prioritized

**Output Phase:**
- [ ] Markdown report complete
- [ ] HTML branded correctly
- [ ] PDF renders cleanly (no splits, no blanks)
- [ ] Email draft personalized
- [ ] All files committed to git

**Time Estimate:** 2-4 hours depending on site complexity
