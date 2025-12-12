"""Convert 2-up Handout HTML to A4 Landscape PDF using Playwright"""
import asyncio
from pathlib import Path

async def convert_html_to_pdf():
    from playwright.async_api import async_playwright

    folder = Path("C:/Users/peter/Downloads/CC/CLIENTS/reignite-health-case-study")
    html_path = folder / "Reignite_Resident_Handout_2up.html"
    pdf_path = folder / "Reignite_Resident_Handout_2up_A4.pdf"

    print(f"Converting: {html_path}")
    print(f"Output: {pdf_path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f'file:///{html_path.as_posix()}')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        await page.pdf(
            path=str(pdf_path),
            width='297mm',
            height='210mm',
            print_background=True,
            landscape=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )
        await browser.close()
        print(f"PDF created successfully: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(convert_html_to_pdf())
