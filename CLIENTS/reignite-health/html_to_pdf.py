"""Convert HTML to PDF using Playwright"""
import asyncio
from pathlib import Path

async def convert_html_to_pdf():
    from playwright.async_api import async_playwright

    folder = Path("C:/Users/peter/Downloads/CC/CLIENTS/reignite-health")
    html_path = folder / "Reignite_Health_FULL_AUDIT_2025.html"
    pdf_path = folder / "Reignite_Health_FULL_AUDIT_2025.pdf"

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
