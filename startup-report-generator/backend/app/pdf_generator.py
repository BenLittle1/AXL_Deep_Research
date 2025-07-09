# app/pdf_generator.py
from weasyprint import HTML, CSS
import markdown2
import os
from datetime import datetime

def create_professional_pdf(markdown_content: str, report_type: str) -> bytes:
    """
    Converts formatted Markdown into a styled PDF.
    """
    print(f"Creating PDF for report type: {report_type}")
    
    # 1. Convert Markdown to HTML
    html_content = markdown2.markdown(markdown_content, extras=["tables", "metadata", "fenced-code-blocks"])
    
    # 2. Load the correct CSS stylesheet for professional styling
    css_file_path = f'./app/static/{report_type}.css'
    
    try:
        with open(css_file_path, 'r') as f:
            css_string = f.read()
        print(f"Successfully loaded CSS from: {css_file_path}")
    except FileNotFoundError:
        print(f"Warning: CSS file not found at {css_file_path}. Using basic styling.")
        # Fallback CSS
        css_string = """
        @page { size: letter; margin: 1in; }
        body { font-family: 'Inter', Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #333; }
        h1 { font-size: 24pt; color: #2c3e50; margin-bottom: 20px; }
        h2 { font-size: 18pt; color: #34495e; margin-top: 20px; margin-bottom: 10px; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
        h3 { font-size: 14pt; color: #2c3e50; margin-top: 15px; margin-bottom: 8px; }
        p { margin-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f8f9fa; font-weight: 600; }
        """
    
    # 3. Create complete HTML document
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
    
    # 4. Use WeasyPrint to render the HTML and CSS into a PDF
    try:
        print("Generating PDF with WeasyPrint...")
        html = HTML(string=full_html)
        pdf_bytes = html.write_pdf()
        print(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
        return pdf_bytes
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # Return a minimal PDF if all else fails
        simple_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Report Generation Error</title>
        </head>
        <body>
            <h1>Report Generation Error</h1>
            <p>There was an error generating the styled report.</p>
            <hr>
            <div>{html_content}</div>
        </body>
        </html>
        """
        return HTML(string=simple_html).write_pdf() 