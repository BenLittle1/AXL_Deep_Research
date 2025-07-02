import os
import re
import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import navy, black

def read_document(file_path):
    """
    Reads content from a file, supporting both .pdf and .txt extensions.
    """
    if not os.path.exists(file_path):
        return None

    _, extension = os.path.splitext(file_path)

    if extension.lower() == '.pdf':
        try:
            with fitz.open(file_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
                return text
        except Exception as e:
            print(f"  - Error reading PDF {file_path}: {e}")
            return None
    elif extension.lower() == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"  - Error reading TXT {file_path}: {e}")
            return None
    else:
        # Unsupported file type
        return None

def create_pdf_report(content, title, output_path):
    """
    Creates a professional, beautifully formatted PDF report from markdown text.
    """
    try:
        # Use more standard margins for better readability
        doc = SimpleDocTemplate(output_path, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        styles = getSampleStyleSheet()

        # Refined styles for a smaller, more minimal report title
        styles.add(ParagraphStyle(name='ReportTitle', fontName='Helvetica', fontSize=18, alignment=1, spaceAfter=18))
        styles.add(ParagraphStyle(name='H1', fontName='Helvetica-Bold', fontSize=18, spaceBefore=24, spaceAfter=8, textColor=navy))
        styles.add(ParagraphStyle(name='H2', fontName='Helvetica-Bold', fontSize=16, spaceBefore=22, spaceAfter=6))
        styles.add(ParagraphStyle(name='H3', fontName='Helvetica-Bold', fontSize=14, spaceBefore=18, spaceAfter=5))
        # Dimension titles are now 2pt larger than body text, and still italic
        styles.add(ParagraphStyle(name='H4', fontName='Helvetica-BoldOblique', fontSize=13, spaceBefore=12, spaceAfter=4))
        styles.add(ParagraphStyle(name='H5', fontName='Helvetica-Oblique', fontSize=12, spaceBefore=10, spaceAfter=4))
        
        # Use a consistent sans-serif font for the body, with improved spacing
        styles.add(ParagraphStyle(name='ReportBody', parent=styles['BodyText'], fontName='Helvetica', fontSize=11, leading=14, spaceAfter=6))
        
        # Use hanging indents for list items for much-improved readability
        list_left_indent = 0.5 * inch # 36 points
        list_bullet_indent = 0.25 * inch # 18 points

        styles.add(ParagraphStyle(name='CustomBullet', parent=styles['ReportBody'], leftIndent=list_left_indent, bulletIndent=list_bullet_indent, spaceBefore=2, spaceAfter=4))
        styles.add(ParagraphStyle(name='NumberedList', parent=styles['ReportBody'], leftIndent=list_left_indent, bulletIndent=list_bullet_indent, spaceBefore=2, spaceAfter=4))
        
        story = []
        
        # Title
        story.append(Paragraph(title, styles['ReportTitle']))
        story.append(Spacer(1, 0.2*inch))

        # Process the report content line by line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.strip() == '---':
                continue

            # Add extra space before a new dimension heading
            is_heading = line.startswith(('#', '##', '###', '####', '#####'))
            if is_heading and i > 0:
                # Check if previous line was not a heading to avoid double spacing
                prev_line = lines[i-1].strip()
                if prev_line and not prev_line.startswith('#'):
                     story.append(Spacer(1, 12)) # 12 points = 1 line space

            # Remove bracketed numerical citations (e.g., [1], [2, 3])
            line = re.sub(r'\[[\d,\s]+\]', '', line)

            # Handle inline markdown (bold)
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)

            if line.startswith('---'):
                story.append(PageBreak())
                continue
            elif line.startswith('##### '):
                story.append(Paragraph(line.replace('##### ', ''), styles['H5']))
            elif line.startswith('#### '):
                story.append(Paragraph(line.replace('#### ', ''), styles['H4']))
            elif line.startswith('### '):
                story.append(Paragraph(line.replace('### ', ''), styles['H3']))
            elif line.startswith('## '):
                story.append(Paragraph(line.replace('## ', ''), styles['H2']))
            elif line.startswith('# '):
                story.append(Paragraph(line.replace('# ', ''), styles['H1']))
            elif line.startswith('* ') or line.startswith('- '):
                text_content = line[1:].lstrip()
                story.append(Paragraph(text_content, styles['CustomBullet'], bulletText='•'))
            elif re.match(r'^\d+\.\s', line):
                match = re.match(r'^(\d+\.)\s*(.*)', line, re.DOTALL)
                if match:
                    number, text_content = match.groups()
                    story.append(Paragraph(text_content, styles['NumberedList'], bulletText=number))
                else: # Fallback for safety
                    story.append(Paragraph(line, styles['ReportBody']))
            else:
                story.append(Paragraph(line, styles['ReportBody']))
        
        doc.build(story)
        print(f"  - Successfully generated PDF report at '{output_path}'")
    except Exception as e:
        print(f"  - Failed to create PDF report. Error: {e}")

def call_perplexity_api(api_key, prompt):
    """
    Calls the Perplexity API with a given prompt and returns the response.
    """
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Perplexity API: {e}")
        return None

def remove_redundant_title(content, keywords):
    """
    Removes the first line of content if it contains any of the specified keywords.
    """
    lines = content.split('\n')
    if lines:
        first_line_lower = lines[0].lower()
        # Check if the line is a heading and contains a keyword
        if any(keyword in first_line_lower for keyword in keywords):
            # Check for markdown heading characters
            if first_line_lower.lstrip().startswith(('#', '*', '-')):
                return '\n'.join(lines[1:]).lstrip()
            # Check for simple text equality
            if first_line_lower.strip() in keywords:
                 return '\n'.join(lines[1:]).lstrip()
    return content

def generate_reports():
    """
    Generates company-specific reports by finding and grouping document files
    in the 'companies' directory.
    """
    load_dotenv()
    api_key = os.getenv("PERPLEXITY_API_KEY")

    if not api_key:
        print("Error: PERPLEXITY_API_KEY not found in .env file.")
        return

    master_prompt_path = "master_prompt.txt"
    companies_dir = "companies"
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    try:
        with open(master_prompt_path, 'r') as f:
            master_prompt = f.read()
    except FileNotFoundError:
        print(f"Error: The master prompt file was not found at '{master_prompt_path}'")
        return
    
    try:
        all_files = os.listdir(companies_dir)
    except FileNotFoundError:
        print(f"Error: The companies directory was not found at '{companies_dir}'")
        return

    company_files = {}
    file_pattern = re.compile(r"(.+?)_(pitch_deck|internal_notes)\.(pdf|txt)$", re.IGNORECASE)

    for filename in all_files:
        match = file_pattern.match(filename)
        if match:
            company_name, doc_type, _ = match.groups()
            company_files.setdefault(company_name, {})[doc_type] = os.path.join(companies_dir, filename)
    
    if not company_files:
        print("No valid company document files found in the 'companies' directory.")
        print("Please name your files like 'CompanyName_pitch_deck.pdf' or 'CompanyName_internal_notes.txt'.")
        return

    # Process each company
    for company_name, files in company_files.items():
        print(f"Processing {company_name}...")
        
        pitch_deck_path = files.get("pitch_deck")
        internal_notes_path = files.get("internal_notes")

        if not pitch_deck_path:
            print(f"  - Skipping {company_name}: Missing pitch_deck file.")
            continue
        if not internal_notes_path:
            print(f"  - Skipping {company_name}: Missing internal_notes file.")
            continue

        pitch_deck = read_document(pitch_deck_path)
        internal_notes = read_document(internal_notes_path)

        if pitch_deck is None or internal_notes is None:
            continue

        # Create the company-specific prompt
        company_prompt = master_prompt.replace("[COMPANY NAME]", company_name)
        company_prompt = company_prompt.replace("[PITCH DECK HERE]", pitch_deck)
        company_prompt = company_prompt.replace("[INTERNAL NOTES HERE]", internal_notes)

        # Call the Perplexity API
        print(f"  - Calling Perplexity API for {company_name}...")
        api_response = call_perplexity_api(api_key, company_prompt)

        if api_response and api_response.get('choices'):
            report_content = api_response['choices'][0]['message']['content']
            
            # Split the content into one-pager and in-depth report
            if '---' in report_content:
                parts = report_content.split('---', 1)
                one_pager_content = parts[0].strip()
                in_depth_content = parts[1].strip()

                # Remove redundant titles
                one_pager_content = remove_redundant_title(one_pager_content, ["one-pager", "company snapshot"])
                in_depth_content = remove_redundant_title(in_depth_content, ["in-depth report"])

                # Generate One-Pager PDF
                one_pager_output_path = os.path.join(reports_dir, f"{company_name}_one_pager.pdf")
                one_pager_title = f"AI Signal Sweep: One-Page Analysis for {company_name}"
                create_pdf_report(one_pager_content, one_pager_title, one_pager_output_path)

                # Generate In-Depth Report PDF
                in_depth_output_path = os.path.join(reports_dir, f"{company_name}_in_depth_report.pdf")
                in_depth_title = f"AI Signal Sweep: In-Depth Report for {company_name}"
                create_pdf_report(in_depth_content, in_depth_title, in_depth_output_path)
            else:
                # Fallback if the separator is missing
                print(f"  - Warning: Separator '---' not found for {company_name}. Generating a single combined report.")
                output_path = os.path.join(reports_dir, f"{company_name}_report.pdf")
                title = f"AI Signal Sweep Report: {company_name}"
                create_pdf_report(report_content, title, output_path)
        else:
            print(f"  - Failed to generate report for {company_name}. API response: {api_response}")


if __name__ == "__main__":
    generate_reports()