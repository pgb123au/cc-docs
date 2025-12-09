---
description: Convert a website audit to a professional Yes AI branded PDF report
---

Convert an existing website audit (markdown or text) into a professional, branded PDF report for Yes AI.

**Usage:** `/yesai-audit-to-pdf [client-name] [website-url]`

Example: `/yesai-audit-to-pdf "Royal Crest Blinds" royalcrestblinds.com.au`

## STEP 1: Setup Client Folder

Create folder structure:
```
C:\Users\peter\Downloads\CC\CLIENTS\[Client-Name-Kebab-Case]\
```

Example: `C:\Users\peter\Downloads\CC\CLIENTS\royal-crest-blinds\`

## STEP 2: Fetch Client Logo

Download the client's logo from their website:

```bash
# Find logo URL
curl -s -L "https://[website]" | grep -i -o 'src="[^"]*logo[^"]*"' | head -3

# Download logo
curl -s -L -o "[client-folder]/client_logo.png" "[LOGO_URL]"
```

If logo fetch fails, proceed without it and note in output.

## STEP 3: Create Professional HTML (Temporary)

Create a temporary HTML file for PDF conversion. This file will be deleted after PDF generation.

### Cover Page:
- Yes AI logo at top (from: `C:\Users\peter\Downloads\CC\Yes AI Assets\YesAI_colors_punched_transparent6.png`)
- Title: "UX, SEO & AI Search Optimization Report"
- Subtitle: "Strategic recommendations to dominate traditional search and emerge in AI-powered search results"
- "Prepared For" section with:
  - Client logo (if fetched)
  - Client name
  - Client website URL
- Date: Current month/year
- Footer: Yes AI contact details

### Page Design:
- A4 format (1122px height per page)
- Page headers: Yes AI logo (45px) + document title
- Page footers: Yes AI logo (30px) + page number
- Colors: Blue #0000ff, Red #ff0000, Dark gradient covers

### Content Sections:
- Executive Summary with score cards
- Tables with alternating row colors
- Info boxes for key insights
- Code blocks for schema/technical examples
- FAQ sections with proper formatting
- Implementation roadmap

### Back Cover:
- Large Yes AI logo (120px)
- "AI-Powered Digital Strategy" tagline
- Contact box: www.yesai.au, (03) 9999 7398, hello@yesai.au

### CSS Requirements (Critical for Clean PDF):
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

/* CRITICAL: Text Contrast on Dark Backgrounds */
/* Always use white text on dark/colored backgrounds */
.exec-summary, .section-header, .cover-page {
    color: white;
}
.exec-summary h2, .exec-summary h3, .exec-summary p,
.exec-summary strong, .exec-summary li {
    color: white !important;
}
.section-header h1, .section-header .section-title,
.section-header .section-number {
    color: white !important;
}
/* Make section-number a lighter accent color */
.section-number {
    color: #818cf8 !important;
}

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

/* Keep-together class for grouped content */
.keep-together {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
}
```

### Layout Best Practices:
- Apply `.keep-together` class to any grouped content (tables, grids, cards)
- Use compact font sizes (10-12px for body, 14-18px for headings)
- Keep padding tight (10-15px) to maximize content per page
- **ALWAYS use white text (`color: white !important`) on dark/blue backgrounds**
- If content still splits, break into smaller logical chunks

### CRITICAL - All Logos Must Use `<img>` Tags:
```html
<img src="file:///C:/Users/peter/Downloads/CC/Yes%20AI%20Assets/YesAI_colors_punched_transparent6.png" alt="Yes AI">
```

## STEP 4: Generate PDF with Chrome Headless

Use Chrome headless to convert HTML to PDF:

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless --disable-gpu --print-to-pdf="C:\Users\peter\Downloads\CC\CLIENTS\[client-folder]\[CLIENT_NAME]_AUDIT_2025.pdf" --no-margins --print-to-pdf-no-header "file:///C:/Users/peter/Downloads/CC/CLIENTS/[client-folder]/temp_audit.html"
```

## STEP 5: Clean Up

Delete the temporary HTML file after successful PDF generation:
```bash
rm "C:\Users\peter\Downloads\CC\CLIENTS\[client-folder]\temp_audit.html"
```

## STEP 6: Verify PDF

Check the PDF for:
- [ ] Cover page: Yes AI logo (top)
- [ ] Cover page: Client logo (in "Prepared For")
- [ ] All page headers: Yes AI logo
- [ ] All page footers: Yes AI logo
- [ ] Back cover: Large Yes AI logo
- [ ] **All text readable** (white on dark backgrounds, dark on light backgrounds)

## STEP 7: Commit & Report

```bash
cd /c/Users/peter/Downloads/CC
git add .
git commit -m "Audit - [Client Name] branded PDF report from Yes AI"
git push
```

## Output Format:

```
Yes AI Audit Report Created
===========================
Client: [Client Name]
Website: [website URL]
Folder: C:\Users\peter\Downloads\CC\CLIENTS\[client-folder]\

Files created:
- [CLIENT_NAME]_AUDIT_2025.pdf
- client_logo.png (if fetched)

PDF: file:///C:/Users/peter/Downloads/CC/CLIENTS/[client-folder]/[CLIENT_NAME]_AUDIT_2025.pdf

Client logo: [Fetched from website / Not available]
Yes AI branding: Applied to all pages

DONE DONE DONE
```

## Yes AI Assets Reference:
- Logo: `C:\Users\peter\Downloads\CC\Yes AI Assets\YesAI_colors_punched_transparent6.png`
- Contact: (03) 9999 7398 | hello@yesai.au | www.yesai.au
