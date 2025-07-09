# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from . import agents, pdf_generator

# Load environment variables
load_dotenv()

app = FastAPI(title="Startup Report Generator", version="2.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    company_name: str
    company_url: str
    report_type: str  # 'one_pager' or 'deep_dive'
    pitch_deck_content: str = ""  # Optional pitch deck content
    internal_notes: str = ""  # Optional internal notes

@app.get("/")
async def root():
    return {"message": "Startup Report Generator API v2.0 - Two-Agent Architecture"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "architecture": "two-agent"}

@app.post("/generate-report",
          response_class=Response,
          responses={200: {"content": {"application/pdf": {}}}})
async def generate_report(request: ReportRequest):
    """
    Main endpoint to generate a company report using the two-agent architecture.
    """
    print(f"Starting report generation for {request.company_name}...")
    print(f"Report type: {request.report_type}")
    print(f"Company URL: {request.company_url}")

    # Validate report type
    if request.report_type not in ['one_pager', 'deep_dive']:
        raise HTTPException(
            status_code=400, 
            detail="Invalid report type. Must be 'one_pager' or 'deep_dive'"
        )

    try:
        # 1. Run Agent 1 to get the Comprehensive Intelligence Brief
        print("Executing Agent 1: Research Analyst...")
        intelligence_brief = agents.run_research_agent(
            request.company_name, 
            request.company_url, 
            request.pitch_deck_content, 
            request.internal_notes
        )
        
        if not intelligence_brief:
            raise HTTPException(status_code=500, detail="Agent 1 failed to retrieve company data.")
        
        print(f"Agent 1 completed. Retrieved data for: {intelligence_brief.get('companyName', 'Unknown')}")

        # 2. Run Agent 2 to format the report
        print("Executing Agent 2: Formatting Specialist...")
        formatted_markdown = agents.run_formatting_agent(intelligence_brief, request.report_type)
        print(f"Agent 2 completed. Formatted report length: {len(formatted_markdown)} characters")

        # 3. Render the final PDF
        print("Executing PDF Renderer...")
        pdf_bytes = pdf_generator.create_professional_pdf(formatted_markdown, request.report_type)

        print("Report generation complete.")
        
        # Generate filename
        company_safe_name = intelligence_brief.get('companyName', request.company_name).replace(' ', '_').replace('.', '_')
        filename = f"{company_safe_name}_{request.report_type}.pdf"
        
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf", 
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        print(f"Error during report generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 