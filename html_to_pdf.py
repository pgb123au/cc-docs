"""Convert HTML to PDF using Playwright"""
import asyncio
from pathlib import Path

async def convert_html_to_pdf():
    from playwright.async_api import async_playwright

    html_path = Path("C:/Users/peter/Downloads/CC/ROYAL_CREST_BLINDS_AUDIT_2025.html")
    pdf_path = Path("C:/Users/peter/Downloads/CC/ROYAL_CREST_BLINDS_AUDIT_2025.pdf")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Load the HTML file
        await page.goto(f'file:///{html_path.as_posix()}')

        # Wait for fonts and content to load
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)  # Extra time for fonts

        # Generate PDF
        await page.pdf(
            path=str(pdf_path),
            format='A4',
            print_background=True,
            margin={
                'top': '0',
                'right': '0',
                'bottom': '0',
                'left': '0'
            }
        )

        await browser.close()
        print(f"PDF created successfully: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(convert_html_to_pdf())
