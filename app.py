import os
import requests
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import zipfile
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Read API key and master prompt
def get_api_key():
    try:
        with open('api_key.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: api_key.txt not found. Please create this file with your Perplexity API key.")
        return None

def read_master_prompt():
    try:
        with open('master_prompt.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        print("Error: master_prompt.txt not found.")
        return None

# Register fonts
def register_fonts():
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    except Exception as e:
        print(f"Warning: Could not register custom fonts: {e}")

register_fonts()

def call_perplexity_api(prompt, company_name):
    api_key = get_api_key()
    if not api_key:
        return None
    
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": f"You are analyzing a company called {company_name}. Provide comprehensive research and analysis."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 4000,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_citations": True,
        "search_domain_filter": ["perplexity.ai"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "month",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Unexpected API response format: {e}")
        return None

def clean_text_for_pdf(text):
    """Clean text for PDF generation by removing problematic characters and formatting"""
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove *italic*
    text = re.sub(r'`(.*?)`', r'\1', text)        # Remove `code`
    
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Remove markdown lists
    text = re.sub(r'^\s*[-*+]\s*', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)
    
    # Remove URLs in markdown format [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text

def create_pdf_report(content, filename, title):
    """Create a PDF report from the given content"""
    doc = SimpleDocTemplate(filename, pagesize=letter, 
                          rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor='black',
        alignment=TA_CENTER,
        fontName='DejaVuSans-Bold' if 'DejaVuSans-Bold' in pdfutils.getRegisteredFontNames() else 'Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        textColor='black',
        alignment=TA_LEFT,
        fontName='DejaVuSans' if 'DejaVuSans' in pdfutils.getRegisteredFontNames() else 'Helvetica'
    )
    
    # Build story
    story = []
    
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Clean and add content
    cleaned_content = clean_text_for_pdf(content)
    
    # Split content into paragraphs and add them
    paragraphs = cleaned_content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), body_style))
            story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)

@app.route('/')
def index():
    return render_template('batch_index.html')

@app.route('/process_companies', methods=['POST'])
def process_companies():
    try:
        data = request.get_json()
        companies = data.get('companies', [])
        
        if not companies:
            return jsonify({'error': 'No companies provided'}), 400
        
        master_prompt = read_master_prompt()
        if not master_prompt:
            return jsonify({'error': 'Master prompt not found'}), 500
        
        results = []
        
        for company in companies:
            company_name = company.get('name', 'Unknown Company')
            
            # Create prompts for both reports
            one_pager_prompt = f"{master_prompt}\n\nPlease create a concise one-page executive summary for {company_name}."
            detailed_prompt = f"{master_prompt}\n\nPlease create a comprehensive detailed analysis report for {company_name}."
            
            # Generate reports
            one_pager_content = call_perplexity_api(one_pager_prompt, company_name)
            detailed_content = call_perplexity_api(detailed_prompt, company_name)
            
            if one_pager_content and detailed_content:
                # Create PDF files
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                one_pager_filename = f"{REPORTS_FOLDER}/{company_name}_one_pager.pdf"
                detailed_filename = f"{REPORTS_FOLDER}/{company_name}_in_depth_report.pdf"
                
                create_pdf_report(one_pager_content, one_pager_filename, f"{company_name} - Executive Summary")
                create_pdf_report(detailed_content, detailed_filename, f"{company_name} - Detailed Analysis")
                
                results.append({
                    'name': company_name,
                    'status': 'success',
                    'one_pager': one_pager_filename,
                    'detailed': detailed_filename
                })
            else:
                results.append({
                    'name': company_name,
                    'status': 'error',
                    'error': 'Failed to generate report content'
                })
        
        # Create ZIP file with all reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{REPORTS_FOLDER}/batch_reports_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for result in results:
                if result['status'] == 'success':
                    zipf.write(result['one_pager'], os.path.basename(result['one_pager']))
                    zipf.write(result['detailed'], os.path.basename(result['detailed']))
        
        return jsonify({
            'success': True,
            'results': results,
            'zip_file': zip_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True, download_name=os.path.basename(filename))
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    print("Starting AXL Deep Research - Batch Company Analysis Tool")
    print("Access the application at: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080) 