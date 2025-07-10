# Startup Report Generator

**Beautiful AI-powered company analysis reports from Google Sheets**

## Overview

This system generates stunning, professionally formatted company analysis reports by:
1. 📊 **Reading data from Google Sheets** - Extracts comprehensive company data
2. 🔍 **AI-powered research** - Enhances data with web research
3. 🎨 **Beautiful PDF generation** - Creates structured reports with professional styling
4. 📤 **Future Airtable integration** - Ready for automated data flow

## Features

✅ **Beautiful Professional Reports**
- One-pager summaries (1-2 pages)
- Deep-dive analysis (3-5 pages)  
- Professional typography and styling
- Tables, charts, and structured sections

✅ **Smart Data Integration**
- Leverages existing Google Sheets analysis (100+ data fields)
- Combines with real-time web research
- Auto-generates SWOT analysis from data scores
- Intelligent content synthesis

✅ **Automated Processing**
- Processes only new/ungenerated companies
- Marks completion status automatically
- Batch processing capabilities
- Error handling and retry logic

## Quick Start

1. **Setup Environment**
   ```bash
   cd startup-report-generator/backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Authenticate Google Sheets**
   ```bash
   gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive
   ```

3. **Generate Beautiful Reports**
   ```python
   from app.main import process_companies_from_sheets
   
   # Your Google Sheet ID
   sheet_id = "1z8Uv-EVDQ4aGar0hKaHlEMsbhmyhWDjsJnrcqAhMKFo"
   
   # Generate reports for all new companies
   results = process_companies_from_sheets(sheet_id)
   ```

4. **Test Beautiful Styling**
   ```bash
   python test_beautiful_reports.py
   ```

## Report Types

### One-Pager
- **Purpose**: Executive summary for quick decision making
- **Length**: 1-2 pages
- **Sections**: Executive summary, key metrics, investment thesis
- **Style**: Concise, data-driven, professional

### Deep-Dive  
- **Purpose**: Comprehensive analysis for detailed evaluation
- **Length**: 3-5 pages
- **Sections**: Market analysis, competitive landscape, financial projections, SWOT
- **Style**: Detailed, analytical, investor-grade

## Architecture

```
Google Sheets → Data Extraction → AI Research → Report Generation → Beautiful PDFs
     ↓               ↓               ↓               ↓               ↓
   100+ fields   Enhanced data   Intelligence    Markdown +      WeasyPrint +
   Existing      + Web research    briefs        Templates         CSS
   analysis                                                      Styling
```

## File Structure

```
startup-report-generator/
├── backend/
│   ├── app/
│   │   ├── main.py              # Core processing logic
│   │   ├── agents.py            # AI research agents  
│   │   ├── pdf_generator.py     # Beautiful PDF creation
│   │   ├── static/
│   │   │   ├── one_pager.css    # Professional styling
│   │   │   └── deep_dive.css    # Report formatting
│   │   └── templates/
│   │       ├── one_pager_template.md
│   │       └── deep_dive_template.md
│   ├── requirements.txt
│   └── test_beautiful_reports.py
└── README.md
```

## Generated Reports

Reports are saved to `./reports/` with naming pattern:
- `{company_name}_one_pager.pdf`
- `{company_name}_deep_dive.pdf`

## Next Steps

🔄 **Airtable Integration** - Automatically sync generated reports back to Airtable for complete workflow automation.

---

*Generating beautiful, professional company analysis reports with AI-powered research and stunning visual design.* 