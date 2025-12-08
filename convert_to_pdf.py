#!/usr/bin/env python3
"""Convert HTML audit report to PDF"""

import sys

# Try xhtml2pdf first
try:
    from xhtml2pdf import pisa

    input_file = r"C:\Users\peter\Downloads\CC\NutritionScienceGroup_Audit_YesAI.html"
    output_file = r"C:\Users\peter\Downloads\CC\NutritionScienceGroup_Audit_YesAI.pdf"

    print(f"Converting {input_file} to PDF using xhtml2pdf...")

    with open(input_file, 'r', encoding='utf-8') as source:
        html_content = source.read()

    with open(output_file, 'wb') as output:
        pisa_status = pisa.CreatePDF(html_content, dest=output, encoding='utf-8')

    if pisa_status.err:
        print(f"Error during conversion: {pisa_status.err}")
        sys.exit(1)
    else:
        print(f"SUCCESS! PDF created at: {output_file}")
        sys.exit(0)

except Exception as e:
    print(f"xhtml2pdf error: {e}")
    print("\nAlternative: Open the HTML file in Chrome and use Print > Save as PDF")
    print(f"HTML file: C:\\Users\\peter\\Downloads\\CC\\NutritionScienceGroup_Audit_YesAI.html")
    sys.exit(1)
