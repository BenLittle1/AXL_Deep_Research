# AXL Ventures Deep Research

A professional startup report generator using a two-agent architecture to create McKinsey/BCG-style investment reports.

## 🎯 Overview

This tool generates professional investment reports for any company using AI-powered research and deterministic formatting. Perfect for investors, analysts, and business professionals who need quick, accurate company assessments.

## 🏗️ Architecture

### Two-Agent System
1. **AI Research Analyst** - Gathers comprehensive company data and market insights using Perplexity API
2. **Formatting Specialist** - Creates polished, professional reports using Jinja2 templates

### Technology Stack
- **Backend:** FastAPI, Python, Jinja2 templates, WeasyPrint PDF generation
- **Frontend:** React, Vite, modern responsive design
- **AI Integration:** Perplexity API for real-time research
- **PDF Generation:** Professional consulting-style formatting

## 🚀 Features

### Report Types
- **One-Pager:** Executive summary perfect for quick decisions (single page)
- **Deep Dive:** Comprehensive multi-page analysis with detailed insights
- **Dual Generation:** Create both reports simultaneously

### Enhanced Research
- **Company URL Integration:** Automatic research from company websites
- **Pitch Deck Content:** Include key information to improve accuracy
- **Internal Notes:** Add research notes, competitive insights, or additional context
- **Combined Intelligence:** AI cross-references provided materials with external research

### Professional Output
- McKinsey/BCG consulting-style formatting
- Clean, professional PDF reports
- Company-specific taglines and branding
- Optimized layouts for each report type

## 📋 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Perplexity API key

### Backend Setup
```bash
cd startup-report-generator/backend
pip install -r requirements.txt
cp .env.template .env
# Add your Perplexity API key to .env
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd startup-report-generator/frontend
npm install
npm run dev
```

### Environment Configuration
Create `.env` file in the backend directory:
```
AI_API_KEY=your_perplexity_api_key_here
AI_API_ENDPOINT=https://api.perplexity.ai/chat/completions
```

## 🎮 Usage

1. **Start the servers:**
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:5173`

2. **Generate reports:**
   - Enter company name and optional website URL
   - Add pitch deck content or internal notes (optional)
   - Choose report type or generate both
   - Download professional PDF reports

3. **API Usage:**
   ```bash
   curl -X POST http://localhost:8000/generate-report \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "Tesla",
       "company_url": "https://tesla.com",
       "report_type": "one_pager",
       "pitch_deck_content": "Optional pitch deck text...",
       "internal_notes": "Optional research notes..."
     }' \
     -o tesla_report.pdf
   ```

## 📊 Report Structure

### One-Pager Contents
- Executive Summary
- Key Metrics
- Business Overview
- Leadership Team
- Market Position
- Strategic Assessment

### Deep Dive Contents
- Executive Summary
- Company Overview
- Financial Overview & Funding History
- Market Analysis & Competitive Landscape
- Leadership Team
- Technology & Product
- Strategic Assessment (SWOT)
- Investment Considerations
- Recommendation

## 🛠️ Development

### Project Structure
```
startup-report-generator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI server
│   │   ├── agents.py            # Two-agent system
│   │   ├── pdf_generator.py     # PDF creation
│   │   ├── templates/           # Report templates
│   │   └── static/              # CSS styles
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx              # Main React component
    │   └── App.css              # Styling
    └── package.json
```

### API Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /generate-report` - Generate report (returns PDF)

## 🎨 Customization

### Templates
- Modify Markdown templates in `backend/app/templates/`
- Update CSS styles in `backend/app/static/`
- Templates use Jinja2 syntax for dynamic content

### Styling
- Professional consulting firm appearance
- Times New Roman fonts, clean borders
- Optimized for single-page and multi-page layouts

## 🔧 Configuration

### Report Customization
- Company-specific taglines automatically generated
- Adjustable page layouts and formatting
- Configurable content sections

### API Configuration
- Supports multiple AI providers (currently Perplexity)
- Configurable model parameters
- Timeout and error handling

## 📈 Performance

- **Generation Time:** 12-20 seconds per report
- **Concurrent Processing:** Supports simultaneous dual report generation
- **File Sizes:** One-pagers ~20KB, Deep dives ~35KB
- **Rate Limiting:** Respects API limits and includes proper error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is private and proprietary to AXL Ventures.

## 🏢 About AXL Ventures

Professional startup research and investment analysis tools for modern venture capital. 