# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os
import traceback
import time

from . import agents, pdf_generator
from .google_sheets import process_companies_from_sheets, sheets_integration

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

class GoogleSheetsRequest(BaseModel):
    sheet_id: str
    worksheet_name: str = "Sheet1"

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
    start_time = time.time()
    
    print("="*80)
    print("🔔 AIRTABLE WEBHOOK STARTED")
    print("="*80)
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Company Name: {request.company_name}")
    print(f"📋 Record ID: {request.airtable_record_id}")
    print(f"📧 Contact Email: {request.contact_email}")
    print(f"🌐 Company URL: {request.company_url}")
    
    # Handle workflow_status - can be string or object
    workflow_status_name = ""
    try:
        if request.workflow_status:
            if isinstance(request.workflow_status, dict):
                workflow_status_name = request.workflow_status.get('name', '')
                print(f"🔄 Workflow Status (object): {request.workflow_status}")
            else:
                workflow_status_name = str(request.workflow_status)
                print(f"🔄 Workflow Status (string): {workflow_status_name}")
        else:
            print("🔄 Workflow Status: None")
    except Exception as e:
        print(f"❌ Error processing workflow_status: {str(e)}")
        workflow_status_name = "Error parsing status"
    
    print(f"📄 Pitch Deck Content Length: {len(request.pitch_deck_content)} chars")
    print(f"📝 Internal Notes Length: {len(request.internal_notes)} chars")
    print(f"🔄 Generate Both Reports: {request.generate_both}")
    
    # Check environment variables
    print("\n🔧 ENVIRONMENT CHECK:")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    if perplexity_key:
        print(f"✅ PERPLEXITY_API_KEY: Found (length: {len(perplexity_key)})")
    else:
        print("❌ PERPLEXITY_API_KEY: Not found")
    
    ai_api_key = os.getenv("AI_API_KEY")
    if ai_api_key:
        print(f"✅ AI_API_KEY: Found (length: {len(ai_api_key)})")
    else:
        print("❌ AI_API_KEY: Not found")
    
    ai_endpoint = os.getenv("AI_API_ENDPOINT")
    if ai_endpoint:
        print(f"✅ AI_API_ENDPOINT: {ai_endpoint}")
    else:
        print("❌ AI_API_ENDPOINT: Not found")
    
    try:
        print("\n📊 STEP 1: VALIDATING INPUT")
        # Validate required fields
        if not request.company_name:
            error_msg = "Company name is required"
            print(f"❌ Validation failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "airtable_record_id": request.airtable_record_id,
                "step_failed": "validation"
            }
        
        # Validate email format if provided
        if request.contact_email and "@" not in request.contact_email:
            print(f"⚠️ Warning: contact_email may be invalid: {request.contact_email}")
        
        print(f"✅ Input validation passed")
        
        print("\n📊 STEP 2: EXECUTING AGENT 1 (RESEARCH ANALYST)")
        print(f"🤖 Calling agents.run_research_agent with:")
        print(f"   - company_name: {request.company_name}")
        print(f"   - company_url: {request.company_url or 'Generated from company name'}")
        print(f"   - pitch_deck_content length: {len(request.pitch_deck_content)}")
        print(f"   - internal_notes length: {len(request.internal_notes)}")
        
        # 1. Run Agent 1 to get the Comprehensive Intelligence Brief
        try:
            intelligence_brief = agents.run_research_agent(
                request.company_name, 
                request.company_url or f"https://{request.company_name.lower().replace(' ', '')}.com",
                request.pitch_deck_content, 
                request.internal_notes
            )
            
            if not intelligence_brief:
                error_msg = "Agent 1 returned None/empty response"
                print(f"❌ Agent 1 failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "company_name": request.company_name,
                    "airtable_record_id": request.airtable_record_id,
                    "step_failed": "agent_1"
                }
            
            if not isinstance(intelligence_brief, dict):
                error_msg = f"Agent 1 returned invalid type: {type(intelligence_brief)}"
                print(f"❌ Agent 1 failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "company_name": request.company_name,
                    "airtable_record_id": request.airtable_record_id,
                    "step_failed": "agent_1"
                }
            
            print(f"✅ Agent 1 completed successfully!")
            print(f"   - Company Name from AI: {intelligence_brief.get('companyName', 'Not found')}")
            print(f"   - Tagline: {intelligence_brief.get('tagline', 'Not found')}")
            print(f"   - Executive Summary length: {len(intelligence_brief.get('executiveSummary', ''))}")
            print(f"   - Team members: {len(intelligence_brief.get('team', []))}")
            print(f"   - Brief structure keys: {list(intelligence_brief.keys())}")
            
        except Exception as agent1_error:
            error_msg = f"Agent 1 exception: {str(agent1_error)}"
            print(f"❌ Agent 1 exception: {error_msg}")
            print(f"❌ Agent 1 traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": error_msg,
                "company_name": request.company_name,
                "airtable_record_id": request.airtable_record_id,
                "step_failed": "agent_1",
                "traceback": traceback.format_exc()
            }
        
        reports_generated = []
        
        if request.generate_both:
            print(f"\n📊 STEP 3: GENERATING BOTH REPORTS")
            # Generate both reports
            for report_type in ['one_pager', 'deep_dive']:
                try:
                    print(f"\n📄 Generating {report_type} report...")
                    
                    print(f"📊 STEP 3.{report_type[0]}: EXECUTING AGENT 2 (FORMATTING SPECIALIST)")
                    try:
                        formatted_markdown = agents.run_formatting_agent(intelligence_brief, report_type)
                        if not formatted_markdown:
                            raise ValueError(f"Agent 2 returned empty markdown for {report_type}")
                        
                        print(f"✅ Agent 2 completed for {report_type}")
                        print(f"   - Formatted markdown length: {len(formatted_markdown)} characters")
                        
                    except Exception as agent2_error:
                        error_msg = f"Agent 2 failed for {report_type}: {str(agent2_error)}"
                        print(f"❌ {error_msg}")
                        print(f"❌ Agent 2 traceback: {traceback.format_exc()}")
                        reports_generated.append({
                            "type": report_type,
                            "filename": f"{request.company_name}_{report_type}.pdf",
                            "error": error_msg,
                            "status": "failed",
                            "step_failed": "agent_2"
                        })
                        continue
                    
                    print(f"📊 STEP 3.{report_type[0]}b: EXECUTING PDF GENERATOR")
                    try:
                        pdf_bytes = pdf_generator.create_professional_pdf(formatted_markdown, report_type)
                        if not pdf_bytes:
                            raise ValueError(f"PDF generator returned empty bytes for {report_type}")
                        
                        print(f"✅ PDF generator completed for {report_type}")
                        print(f"   - PDF size: {len(pdf_bytes)} bytes")
                        
                    except Exception as pdf_error:
                        error_msg = f"PDF generator failed for {report_type}: {str(pdf_error)}"
                        print(f"❌ {error_msg}")
                        print(f"❌ PDF generator traceback: {traceback.format_exc()}")
                        reports_generated.append({
                            "type": report_type,
                            "filename": f"{request.company_name}_{report_type}.pdf",
                            "error": error_msg,
                            "status": "failed",
                            "step_failed": "pdf_generator"
                        })
                        continue
                    
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
                    error_msg = f"Unexpected error generating {report_type}: {str(e)}"
                    print(f"❌ {error_msg}")
                    print(f"❌ Unexpected error traceback: {traceback.format_exc()}")
                    reports_generated.append({
                        "type": report_type,
                        "filename": f"{request.company_name}_{report_type}.pdf",
                        "error": error_msg,
                        "status": "failed",
                        "step_failed": "unexpected",
                        "traceback": traceback.format_exc()
                    })
                    continue
        
        success_count = len([r for r in reports_generated if r.get("status") == "generated"])
        processing_time = round(time.time() - start_time, 2)
        
        print(f"\n📊 STEP 4: PREPARING RESPONSE")
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
            "processing_time_seconds": processing_time,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"✅ Response prepared successfully")
        print(f"🎉 Webhook completed successfully for {request.company_name}")
        print(f"📊 Generated {success_count} reports in {processing_time} seconds")
        print("="*80)
        
        return response_data
        
    except Exception as e:
        processing_time = round(time.time() - start_time, 2)
        error_msg = f"Unexpected error in Airtable webhook: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        print(f"⏰ Processing time before error: {processing_time} seconds")
        print("="*80)
        
        return {
            "success": False,
            "error": error_msg,
            "company_name": request.company_name,
            "airtable_record_id": request.airtable_record_id,
            "contact_email": request.contact_email,
            "step_failed": "unexpected_top_level",
            "processing_time_seconds": processing_time,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "traceback": traceback.format_exc()
        }

@app.post("/google-sheets-process")
async def process_google_sheets(request: GoogleSheetsRequest):
    """
    Process companies from a Google Sheet.
    This endpoint reads companies from the specified Google Sheet and generates reports for them.
    """
    print("="*80)
    print("📊 GOOGLE SHEETS PROCESSING STARTED")
    print("="*80)
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Sheet ID: {request.sheet_id}")
    print(f"📋 Worksheet: {request.worksheet_name}")
    
    try:
        # Process companies from the Google Sheet
        results = process_companies_from_sheets(request.sheet_id, request.worksheet_name)
        
        print(f"✅ Google Sheets processing completed")
        print(f"📊 Processed: {results.get('companies_processed', 0)}")
        print(f"📊 Failed: {results.get('companies_failed', 0)}")
        print("="*80)
        
        return results
        
    except Exception as e:
        error_msg = f"Error processing Google Sheets: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        print("="*80)
        
        return {
            "success": False,
            "error": error_msg,
            "companies_processed": 0,
            "companies_failed": 0,
            "errors": [error_msg],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "traceback": traceback.format_exc()
        }

@app.get("/google-sheets-info/{sheet_id}")
async def get_google_sheets_info(sheet_id: str, worksheet_name: str = "Sheet1"):
    """
    Get information about a Google Sheet without processing it.
    Useful for testing connectivity and viewing sheet structure.
    """
    try:
        # Connect to the sheet
        if not sheets_integration.connect_to_sheet(sheet_id, worksheet_name):
            raise HTTPException(status_code=400, detail="Failed to connect to Google Sheet")
        
        # Get sheet info
        info = sheets_integration.get_sheet_info()
        
        # Get pending companies count
        pending_companies = sheets_integration.get_pending_companies()
        info['pending_companies_count'] = len(pending_companies)
        
        return {
            "success": True,
            "sheet_info": info,
            "pending_companies": len(pending_companies),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        error_msg = f"Error getting Google Sheets info: {str(e)}"
        print(f"❌ {error_msg}")
        
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 