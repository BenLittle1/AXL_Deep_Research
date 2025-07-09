# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os

from . import agents, pdf_generator

# Load environment variables
load_dotenv()

app = FastAPI(title="Startup Report Generator", version="2.0.0")

# Add CORS middleware for frontend integration and Airtable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Airtable and frontend
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

class AirtableWorkflowStatus(BaseModel):
    id: str
    name: str
    color: str

class AirtableWebhookRequest(BaseModel):
    company_name: str
    company_url: str = ""
    pitch_deck_content: str = ""
    internal_notes: str = ""
    airtable_record_id: str = ""
    generate_both: bool = True
    contact_email: str = ""
    workflow_status: Optional[Any] = None  # Can be string or object

@app.get("/")
async def root():
    return {"message": "Startup Report Generator API v2.0 - Two-Agent Architecture", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "architecture": "two-agent", "version": "2.0.0"}

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

@app.post("/airtable-webhook")
async def airtable_webhook(request: AirtableWebhookRequest):
    """
    Endpoint specifically designed for Airtable webhook integration.
    Generates both reports and returns status information.
    """
    print(f"🔔 Airtable webhook triggered for {request.company_name}")
    print(f"📋 Record ID: {request.airtable_record_id}")
    print(f"📧 Contact Email: {request.contact_email}")
    
    # Handle workflow_status - can be string or object
    workflow_status_name = ""
    if request.workflow_status:
        if isinstance(request.workflow_status, dict):
            workflow_status_name = request.workflow_status.get('name', '')
        else:
            workflow_status_name = str(request.workflow_status)
    
    print(f"🔄 Workflow Status: {workflow_status_name}")
    print(f"📄 Pitch Deck Content Length: {len(request.pitch_deck_content)} chars")
    print(f"📝 Internal Notes Length: {len(request.internal_notes)} chars")
    
    try:
        # Validate required fields
        if not request.company_name:
            return {
                "success": False,
                "error": "Company name is required",
                "airtable_record_id": request.airtable_record_id
            }
        
        # 1. Run Agent 1 to get the Comprehensive Intelligence Brief
        print("🤖 Executing Agent 1: Research Analyst...")
        intelligence_brief = agents.run_research_agent(
            request.company_name, 
            request.company_url or f"https://{request.company_name.lower().replace(' ', '')}.com",
            request.pitch_deck_content, 
            request.internal_notes
        )
        
        if not intelligence_brief:
            return {
                "success": False,
                "error": "Failed to retrieve company data from research agent",
                "company_name": request.company_name,
                "airtable_record_id": request.airtable_record_id
            }
        
        print(f"✅ Agent 1 completed successfully for: {intelligence_brief.get('companyName', request.company_name)}")
        
        reports_generated = []
        
        if request.generate_both:
            # Generate both reports
            for report_type in ['one_pager', 'deep_dive']:
                try:
                    print(f"📄 Generating {report_type} report...")
                    formatted_markdown = agents.run_formatting_agent(intelligence_brief, report_type)
                    pdf_bytes = pdf_generator.create_professional_pdf(formatted_markdown, report_type)
                    
                    # Generate filename
                    company_safe_name = intelligence_brief.get('companyName', request.company_name).replace(' ', '_').replace('.', '_')
                    filename = f"{company_safe_name}_{report_type}.pdf"
                    
                    # In production, you might want to save to cloud storage instead
                    # For now, we'll just track the generation without local storage
                    
                    reports_generated.append({
                        "type": report_type,
                        "filename": filename,
                        "size_bytes": len(pdf_bytes),
                        "status": "generated"
                    })
                    
                    print(f"✅ {report_type} report generated successfully ({len(pdf_bytes)} bytes)")
                    
                except Exception as e:
                    print(f"❌ Error generating {report_type}: {str(e)}")
                    reports_generated.append({
                        "type": report_type,
                        "filename": f"{request.company_name}_{report_type}.pdf",
                        "error": str(e),
                        "status": "failed"
                    })
                    continue
        
        success_count = len([r for r in reports_generated if r.get("status") == "generated"])
        
        response_data = {
            "success": success_count > 0,
            "company_name": intelligence_brief.get('companyName', request.company_name),
            "airtable_record_id": request.airtable_record_id,
            "reports_generated": reports_generated,
            "total_reports": success_count,
            "contact_email": request.contact_email,
            "workflow_status": workflow_status_name,
            "company_data": {
                "tagline": intelligence_brief.get('tagline', ''),
                "founded_year": intelligence_brief.get('foundedYear', ''),
                "total_funding": intelligence_brief.get('financials', {}).get('totalFunding', ''),
                "valuation": intelligence_brief.get('financials', {}).get('valuation', ''),
                "team_size": len(intelligence_brief.get('team', []))
            },
            "processing_time_seconds": "15-30"  # Approximate
        }
        
        print(f"🎉 Webhook completed successfully for {request.company_name}")
        print(f"📊 Generated {success_count} reports")
        
        return response_data
        
    except Exception as e:
        print(f"❌ Error in Airtable webhook: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "company_name": request.company_name,
            "airtable_record_id": request.airtable_record_id,
            "contact_email": request.contact_email
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 