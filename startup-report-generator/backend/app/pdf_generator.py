# app/pdf_generator.py
import markdown2
import os
from datetime import datetime
from weasyprint import HTML, CSS

def create_professional_pdf(markdown_content: str, report_type: str) -> bytes:
    """
    Converts formatted Markdown into a beautifully styled PDF using WeasyPrint and CSS.
    """
    print(f"Creating beautiful PDF for report type: {report_type}")
    
    # 1. Convert Markdown to HTML
    html_content = markdown2.markdown(markdown_content, extras=["tables", "metadata", "fenced-code-blocks"])
    
    # 2. Load the correct CSS stylesheet for professional styling
    css_file_path = f'./app/static/{report_type}.css'
    
    try:
        with open(css_file_path, 'r') as f:
            css_string = f.read()
        print(f"✅ Successfully loaded CSS from: {css_file_path}")
    except FileNotFoundError:
        print(f"❌ Error: CSS file not found at {css_file_path}")
        raise FileNotFoundError(f"Required CSS file missing: {css_file_path}")
    
    # 3. Create complete HTML document with professional styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Company Analysis Report</title>
        <style>
        {css_string}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # 4. Use WeasyPrint to render the HTML and CSS into a beautiful PDF
    print("🎨 Generating beautiful PDF with WeasyPrint...")
    html = HTML(string=full_html)
    pdf_bytes = html.write_pdf()
    print(f"✅ Beautiful PDF generated successfully, size: {len(pdf_bytes)} bytes")
    return pdf_bytes 