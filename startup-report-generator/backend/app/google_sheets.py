# app/google_sheets.py
import os
import json
import gspread
import google.auth
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
import time
from datetime import datetime


class GoogleSheetsIntegration:
    def __init__(self):
        """Initialize Google Sheets client with service account credentials."""
        self.client = None
        self.sheet = None
        self.worksheet = None
        self._setup_client()
    
    def _setup_client(self):
        """Set up the Google Sheets client using available credentials."""
        try:
            # Define the scope
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = None
            
            # Try service account credentials first
            credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
            credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'google_sheets_credentials.json')
            
            if credentials_json:
                print("🔑 Using service account from environment variable")
                credentials_info = json.loads(credentials_json)
                credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
            elif os.path.exists(credentials_file):
                print("🔑 Using service account from file")
                credentials = Credentials.from_service_account_file(credentials_file, scopes=scopes)
            else:
                # Fall back to Application Default Credentials
                print("🔄 Service account credentials not found, trying Application Default Credentials...")
                try:
                    credentials, project = google.auth.default(scopes=scopes)
                    print("✅ Using Application Default Credentials (your personal Google account)")
                except Exception as adc_error:
                    print(f"❌ Application Default Credentials failed: {str(adc_error)}")
                    print("💡 Try running: gcloud auth application-default login")
                    return
            
            if not credentials:
                print("❌ No valid credentials found")
                return
            
            # Create the client
            self.client = gspread.authorize(credentials)
            print("✅ Google Sheets client initialized successfully")
            
        except Exception as e:
            print(f"❌ Error setting up Google Sheets client: {str(e)}")
            print("💡 Try one of these solutions:")
            print("   1. Run: gcloud auth application-default login")
            print("   2. Set up service account credentials")
            print("   3. Check the GOOGLE_CLOUD_ALTERNATIVES.md guide")
            self.client = None
    
    def connect_to_sheet(self, sheet_id: str, worksheet_name: str = "Sheet1") -> bool:
        """Connect to a specific Google Sheet and worksheet."""
        try:
            if not self.client:
                print("❌ Google Sheets client not initialized")
                return False
            
            # Open the spreadsheet by ID
            self.sheet = self.client.open_by_key(sheet_id)
            
            # Get the specific worksheet
            self.worksheet = self.sheet.worksheet(worksheet_name)
            
            print(f"✅ Connected to Google Sheet: {self.sheet.title}")
            print(f"✅ Using worksheet: {worksheet_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to Google Sheet: {str(e)}")
            return False
    
    def get_pending_companies(self) -> List[Dict]:
        """
        Get all companies that need processing from the Google Sheet.
        Uses the 'generated' field to determine if processing is needed.
        Extracts ALL existing company data from the sheet fields.
        
        Logic:
        - Process if 'generated' field is blank/empty
        - Skip if 'generated' field = 'yes' (already processed)
        - Extract comprehensive company data from all fields
        """
        try:
            if not self.worksheet:
                print("❌ No worksheet connected")
                return []
            
            # Get all values from the worksheet
            all_values = self.worksheet.get_all_values()
            
            if not all_values:
                print("❌ No data found in worksheet")
                return []
            
            # Assume first row is headers
            headers = all_values[0]
            rows = all_values[1:]
            
            print(f"📊 Found {len(rows)} data rows in sheet")
            
            # Find the 'generated' column
            generated_col_index = None
            for i, header in enumerate(headers):
                if header.lower() == 'generated':
                    generated_col_index = i
                    print(f"📍 Found 'generated' column at position {i+1}")
                    break
            
            if generated_col_index is None:
                print("❌ 'generated' column not found! Please add a 'generated' column to your sheet.")
                return []
            
            pending_companies = []
            processed_count = 0
            skipped_count = 0
            
            for i, row in enumerate(rows, start=2):  # Start at 2 because of header row
                # Create a comprehensive dictionary from headers and row values
                row_dict = {}
                for j, header in enumerate(headers):
                    if j < len(row):
                        # Keep original header names for structured data
                        row_dict[header] = row[j]
                        # Also create lowercase underscore version for compatibility
                        row_dict[header.lower().replace(' ', '_').replace('-', '_')] = row[j]
                    else:
                        row_dict[header] = ""
                        row_dict[header.lower().replace(' ', '_').replace('-', '_')] = ""
                
                # Add row number for updates
                row_dict['row_number'] = i
                
                # Get key fields for processing decision
                company_name = row_dict.get('company_name', '').strip()
                status = row_dict.get('Status', '').strip()
                
                # Get the 'generated' field value
                generated_value = row[generated_col_index] if generated_col_index < len(row) else ""
                generated_value = generated_value.strip().lower()
                
                # Skip if no company name
                if not company_name:
                    continue
                
                # Check if already generated
                if generated_value in ['yes', 'y', 'true', '1', 'done', 'completed']:
                    processed_count += 1
                    print(f"⏭️  Skipping {company_name} - Already generated (Row {i})")
                    continue
                
                # Check if status indicates it should be processed
                if status in ['Pending', 'Reviewed - Promising', 'Ready', 'New', 'To Process']:
                    # Extract and organize the rich company data
                    company_data = self._extract_company_data(row_dict)
                    company_data['row_number'] = i
                    
                    pending_companies.append(company_data)
                    print(f"📋 Found NEW company for processing: {company_name} (Row {i})")
                    print(f"📊 Extracted {len([k for k,v in company_data.items() if v and k != 'row_number'])} populated data fields")
                else:
                    skipped_count += 1
                    print(f"⏭️  Skipping {company_name} - Status: '{status}' (Row {i})")
            
            print(f"\n📊 Processing Summary:")
            print(f"   ✅ NEW companies ready for processing: {len(pending_companies)}")
            print(f"   ⏭️  Already generated companies: {processed_count}")
            print(f"   ⏭️  Other status companies: {skipped_count}")
            
            return pending_companies
            
        except Exception as e:
            print(f"❌ Error getting pending companies: {str(e)}")
            return []
    
    def _extract_company_data(self, row_dict: Dict) -> Dict:
        """
        Extract and organize all the rich company data from the sheet fields.
        Returns a structured dictionary with all available company information.
        """
        company_data = {
            # Basic company info
            'company_name': row_dict.get('company_name', ''),
            'email': row_dict.get('email', ''),
            'website': row_dict.get('website', ''),
            'status': row_dict.get('Status', ''),
            
            # Problem Analysis
            'problem_analysis': {
                'statement': row_dict.get('problem_statement', ''),
                'commentary': row_dict.get('problem_statement_commentary', ''),
                'score': row_dict.get('problem_statement_score', ''),
                'frequency': row_dict.get('problem_frequency', ''),
                'frequency_commentary': row_dict.get('problem_frequency_commentary', ''),
                'frequency_score': row_dict.get('problem_frequency_score', ''),
            },
            
            # Market Analysis
            'market_analysis': {
                'industry': row_dict.get('industry', ''),
                'industry_commentary': row_dict.get('industry_commentary', ''),
                'industry_score': row_dict.get('industry_score', ''),
                'competitors': row_dict.get('competitors', ''),
                'competitors_commentary': row_dict.get('competitors_commentary', ''),
                'competitors_score': row_dict.get('competitors_score', ''),
                'target_audience': row_dict.get('target_audience', ''),
                'target_audience_commentary': row_dict.get('target_audience_commentary', ''),
                'target_audience_score': row_dict.get('target_audience_score', ''),
                'ideal_customer': row_dict.get('ideal_customer', ''),
                'ideal_customer_commentary': row_dict.get('ideal_customer_commentary', ''),
                'ideal_customer_score': row_dict.get('ideal_customer_score', ''),
            },
            
            # Product Analysis
            'product_analysis': {
                'mvp': row_dict.get('mvp', ''),
                'mvp_commentary': row_dict.get('mvp_commentary', ''),
                'mvp_score': row_dict.get('mvp_score', ''),
                'progress': row_dict.get('progress', ''),
                'progress_commentary': row_dict.get('progress_commentary', ''),
                'progress_score': row_dict.get('progress_score', ''),
            },
            
            # Team Analysis  
            'team_analysis': {
                'founder_fit': row_dict.get('founder_fit', ''),
                'founder_fit_commentary': row_dict.get('founder_fit_commentary', ''),
                'founder_fit_score': row_dict.get('founder_fit_score', ''),
                'role': row_dict.get('role', ''),
                'role_commentary': row_dict.get('role_commentary', ''),
                'role_score': row_dict.get('role_score', ''),
                'team_growth': row_dict.get('team_growth', ''),
                'team_growth_commentary': row_dict.get('team_growth_commentary', ''),
                'team_growth_score': row_dict.get('team_growth_score', ''),
            },
            
            # Business Analysis
            'business_analysis': {
                'traction': row_dict.get('traction', ''),
                'traction_commentary': row_dict.get('traction_commentary', ''),
                'traction_score': row_dict.get('traction_score', ''),
                'pricing': row_dict.get('pricing', ''),
                'pricing_commentary': row_dict.get('pricing_commentary', ''),
                'pricing_score': row_dict.get('pricing_score', ''),
                'buyers': row_dict.get('buyers', ''),
                'buyers_commentary': row_dict.get('buyers_commentary', ''),
                'buyers_score': row_dict.get('buyers_score', ''),
            },
            
            # Additional context
            'additional_context': {
                'location': row_dict.get('location', ''),
                'location_commentary': row_dict.get('location_commentary', ''),
                'idea_source': row_dict.get('idea_source', ''),
                'idea_source_commentary': row_dict.get('idea_source_commentary', ''),
                'created_at': row_dict.get('Created_At', ''),
                'pdf_url': row_dict.get('PDF_URL', ''),
            },
            
            # Keep all original data for any fields we might have missed
            'raw_data': row_dict
        }
        
        return company_data
    
    def mark_company_as_processed(self, row_number: int, success: bool = True, error_message: str = "", reports_generated: List[str] = None) -> bool:
        """
        Mark a company as processed by updating the 'generated' column.
        """
        try:
            if not self.worksheet:
                print("❌ No worksheet available")
                return False
            
            # The 'generated' column is at position 100 (column CV)
            column_letter = self._number_to_column_letter(100)
            
            if success:
                value = "yes"
                print(f"✅ Marking row {row_number} as successfully processed")
            else:
                value = "failed"
                if error_message:
                    value = f"failed: {error_message[:50]}"  # Truncate long error messages
                print(f"❌ Marking row {row_number} as failed: {error_message}")
            
            # Update the cell
            cell_address = f"{column_letter}{row_number}"
            self.worksheet.update(cell_address, value)
            
            print(f"📝 Updated {cell_address} with: {value}")
            return True
            
        except Exception as e:
            print(f"❌ Error marking company as processed: {str(e)}")
            return False

    def update_drive_links(self, row_number: int, one_pager_link: str = "", deep_dive_link: str = "") -> bool:
        """
        Update the Google Sheet with Drive links for generated reports using existing columns.
        
        Args:
            row_number: Row number in the sheet
            one_pager_link: Google Drive link for one-pager PDF
            deep_dive_link: Google Drive link for deep-dive PDF
            
        Returns:
            bool: Success status
        """
        try:
            if not self.worksheet:
                print("❌ No worksheet available")
                return False
            
            updates = []
            
            # Add one-pager link (column 98 - existing "One-Pager" field)
            if one_pager_link:
                one_pager_column = self._number_to_column_letter(98)
                updates.append({
                    'range': f"{one_pager_column}{row_number}",
                    'values': [[one_pager_link]]
                })
                print(f"📝 Will update one-pager link at {one_pager_column}{row_number}")
            
            # Add deep-dive link (column 99 - existing "Deep-Dive" field)
            if deep_dive_link:
                deep_dive_column = self._number_to_column_letter(99)
                updates.append({
                    'range': f"{deep_dive_column}{row_number}",
                    'values': [[deep_dive_link]]
                })
                print(f"📝 Will update deep-dive link at {deep_dive_column}{row_number}")
            
            # Batch update if we have any updates
            if updates:
                self.worksheet.batch_update(updates)
                print(f"✅ Successfully updated {len(updates)} Drive links for row {row_number}")
                return True
            else:
                print("⚠️ No links provided to update")
                return False
                
        except Exception as e:
            print(f"❌ Error updating Drive links: {str(e)}")
            return False

    def add_drive_link_headers(self) -> bool:
        """
        Check that existing One-Pager and Deep-Dive columns are available for Drive links.
        """
        try:
            if not self.worksheet:
                print("❌ No worksheet available")
                return False
            
            # Get current headers
            headers = self.worksheet.row_values(1)
            
            # Check that existing columns are available
            one_pager_found = False
            deep_dive_found = False
            
            for i, header in enumerate(headers, 1):
                if header and 'one' in header.lower() and 'pager' in header.lower():
                    one_pager_found = True
                    print(f"✅ Found existing 'One-Pager' field at column {i}")
                elif header and 'deep' in header.lower() and 'dive' in header.lower():
                    deep_dive_found = True
                    print(f"✅ Found existing 'Deep-Dive' field at column {i}")
            
            if one_pager_found and deep_dive_found:
                print("✅ Existing One-Pager and Deep-Dive columns ready for Drive links")
                return True
            else:
                print("⚠️ Missing required columns - please ensure 'One-Pager' and 'Deep-Dive' fields exist")
                return False
                
        except Exception as e:
            print(f"❌ Error checking Drive link columns: {str(e)}")
            return False

    def _number_to_column_letter(self, col_num: int) -> str:
        """
        Convert a column number to Excel-style column letter (1 = A, 26 = Z, 27 = AA, etc.)
        """
        result = ""
        while col_num > 0:
            col_num -= 1  # Adjust for 1-based indexing
            result = chr(col_num % 26 + ord('A')) + result
            col_num //= 26
        return result
    
    def get_sheet_info(self) -> Dict:
        """Get information about the connected sheet."""
        if not self.sheet or not self.worksheet:
            return {"error": "No sheet connected"}
        
        try:
            return {
                "sheet_title": self.sheet.title,
                "worksheet_title": self.worksheet.title,
                "row_count": self.worksheet.row_count,
                "col_count": self.worksheet.col_count,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}


# Global instance
sheets_integration = GoogleSheetsIntegration()


def _create_intelligence_brief_from_enhanced_research(enhanced_research: Dict) -> Dict:
    """
    Convert enhanced research data (existing + web research) into the intelligence brief format
    expected by the formatting agent for compatibility.
    """
    try:
        company_data = enhanced_research.get('existing_data', {})
        web_research = enhanced_research.get('web_research', {})
        
        # Build intelligence brief structure matching template expectations
        intelligence_brief = {
            'companyName': company_data.get('company_name', ''),
            'tagline': _extract_tagline(company_data, web_research),
            'foundedYear': _extract_founded_year(company_data, web_research),
            'website': company_data.get('website', '') or company_data.get('raw_data', {}).get('website', ''),
            
            # Executive summary combining all key points
            'executiveSummary': _create_executive_summary(company_data, web_research),
            
            # Problem statement from existing data + validation from web research
            'problemStatement': _create_problem_statement(company_data, web_research),
            
            # Solution description from existing analysis
            'solution': _create_solution_description(company_data, web_research),
            
            # Business model from existing data
            'businessModel': _create_business_model(company_data, web_research),
            
            # Market analysis combining both sources
            'marketAnalysis': _create_market_analysis(company_data, web_research),
            
            # Team information
            'team': _create_team_info(company_data, web_research),
            
            # Financial information
            'financials': _create_financials_info(company_data, web_research),
            
            # Product overview
            'productOverview': _create_product_overview(company_data, web_research),
            
            # Technology stack from analysis
            'technologyStack': _extract_technology_stack(company_data, web_research),
            
            # Intellectual property
            'intellectualProperty': _extract_ip_info(company_data, web_research),
            
            # SWOT Analysis (required by templates)
            'swotAnalysis': _create_swot_analysis(company_data, web_research)
        }
        
        return intelligence_brief
        
    except Exception as e:
        print(f"❌ Error creating intelligence brief: {str(e)}")
        return {}

def _extract_tagline(company_data: Dict, web_research: Dict) -> str:
    """Extract or generate tagline from available data."""
    # Try existing data first
    raw_data = company_data.get('raw_data', {})
    tagline = raw_data.get('tagline', '') or raw_data.get('description', '')
    
    if not tagline:
        # Try to extract from problem statement
        problem_analysis = company_data.get('problem_analysis', {})
        statement = problem_analysis.get('statement', '')
        if statement and len(statement) < 200:
            tagline = statement
    
    return tagline or f"Innovative solution in {company_data.get('market_analysis', {}).get('industry', 'emerging market')}"

def _extract_founded_year(company_data: Dict, web_research: Dict) -> str:
    """Extract founded year from available data."""
    raw_data = company_data.get('raw_data', {})
    return raw_data.get('founded_year', '') or raw_data.get('created_at', '')[:4] if raw_data.get('created_at') else ''

def _create_business_overview(company_data: Dict, web_research: Dict) -> str:
    """Create comprehensive business overview combining existing data with web research."""
    overview_parts = []
    
    # Problem statement
    problem_analysis = company_data.get('problem_analysis', {})
    if problem_analysis.get('statement'):
        overview_parts.append(f"Problem: {problem_analysis['statement']}")
    
    # Industry context
    market_analysis = company_data.get('market_analysis', {})
    if market_analysis.get('industry'):
        overview_parts.append(f"Industry: {market_analysis['industry']}")
    
    # MVP/Product status
    product_analysis = company_data.get('product_analysis', {})
    if product_analysis.get('mvp'):
        overview_parts.append(f"Product Status: {product_analysis['mvp']}")
    
    # Add web research insights
    web_summary = web_research.get('summary', '')
    if web_summary:
        overview_parts.append(f"Recent Developments: {web_summary}")
    
    return " | ".join(overview_parts) if overview_parts else "Comprehensive business overview combining existing analysis with current market research."

def _create_problem_statement(company_data: Dict, web_research: Dict) -> str:
    """Create problem statement as string combining existing analysis with market validation."""
    problem_analysis = company_data.get('problem_analysis', {})
    statement = problem_analysis.get('statement', '')
    
    if not statement:
        # Try to extract from web research if no existing statement
        statement = web_research.get('problem_validation', 'Problem statement to be analyzed')
    
    return statement

def _create_market_analysis(company_data: Dict, web_research: Dict) -> Dict:
    """Create market analysis structure matching template expectations."""
    market_analysis = company_data.get('market_analysis', {})
    
    # Extract market size info or use defaults
    tam = market_analysis.get('market_size', '') or market_analysis.get('tam', '') or ''
    sam = market_analysis.get('sam', '') or ''
    som = market_analysis.get('som', '') or ''
    
    # Build target customer description
    target_customer = (
        market_analysis.get('target_audience', '') or 
        market_analysis.get('ideal_customer', '') or 
        'Target customer segment identified in market research'
    )
    
    # Create competitors array from existing data
    competitors = []
    competitors_text = market_analysis.get('competitors', '')
    if competitors_text:
        # Split competitor names and create array structure
        competitor_names = [name.strip() for name in competitors_text.split(',') if name.strip()]
        for name in competitor_names[:5]:  # Limit to 5 competitors
            competitors.append({
                'name': name,
                'description': f'Competitor in {market_analysis.get("industry", "the market")}'
            })
    
    # Key trends from industry analysis
    key_trends = []
    industry = market_analysis.get('industry', '')
    if industry:
        key_trends.append(f'Growth in {industry} sector')
    if market_analysis.get('industry_commentary'):
        key_trends.append('Market dynamics supporting innovation')
    
    return {
        'sizeTAM': tam,
        'sizeSAM': sam, 
        'sizeSOM': som,
        'keyTrends': key_trends or ['Market trends available in detailed analysis'],
        'targetCustomer': target_customer,
        'competitors': competitors
    }

def _create_competitive_landscape(company_data: Dict, web_research: Dict) -> Dict:
    """Create competitive landscape combining known competitors with additional research."""
    market_analysis = company_data.get('market_analysis', {})
    
    return {
        'knownCompetitors': market_analysis.get('competitors', ''),
        'competitorsCommentary': market_analysis.get('competitors_commentary', ''),
        'competitorsScore': market_analysis.get('competitors_score', ''),
        'additionalCompetitors': web_research.get('additional_competitors', 'See web research for additional competitive analysis'),
        'dataSource': 'existing_analysis_plus_web_research'
    }

def _create_team_info(company_data: Dict, web_research: Dict) -> List[Dict]:
    """Create team information array matching template expectations."""
    team_members = []
    team_analysis = company_data.get('team_analysis', {})
    
    # Try to extract founder info from existing data
    founder_fit = team_analysis.get('founder_fit', '')
    role = team_analysis.get('role', '')
    
    if founder_fit or role:
        # Create founder entry from available data
        team_members.append({
            'name': 'Founder',
            'title': role or 'Founder & CEO',
            'background': founder_fit or 'Founder background detailed in analysis'
        })
    
    # Add web research team info if available
    web_team_info = web_research.get('team_background', '')
    if web_team_info and 'founder' not in web_team_info.lower():
        team_members.append({
            'name': 'Team Member',
            'title': 'Key Team Member',
            'background': web_team_info
        })
    
    # If no team info found, add placeholder
    if not team_members:
        team_members.append({
            'name': 'Leadership Team',
            'title': 'Management',
            'background': 'Team information available in detailed analysis'
        })
    
    return team_members

def _create_product_info(company_data: Dict, web_research: Dict) -> Dict:
    """Create product information from existing data and web research."""
    product_analysis = company_data.get('product_analysis', {})
    
    return {
        'mvp': product_analysis.get('mvp', ''),
        'mvpCommentary': product_analysis.get('mvp_commentary', ''),
        'mvpScore': product_analysis.get('mvp_score', ''),
        'progress': product_analysis.get('progress', ''),
        'progressCommentary': product_analysis.get('progress_commentary', ''),
        'technologyDetails': web_research.get('technology_details', 'See web research for technology details'),
        'dataSource': 'existing_analysis_plus_web_research'
    }

def _create_traction_info(company_data: Dict, web_research: Dict) -> Dict:
    """Create traction information from existing data and web research."""
    business_analysis = company_data.get('business_analysis', {})
    
    return {
        'existingTraction': business_analysis.get('traction', ''),
        'tractionCommentary': business_analysis.get('traction_commentary', ''),
        'tractionScore': business_analysis.get('traction_score', ''),
        'customerEvidence': web_research.get('customer_traction', 'See web research for customer traction evidence'),
        'dataSource': 'existing_analysis_plus_web_research'
    }

def _create_financials_info(company_data: Dict, web_research: Dict) -> Dict:
    """Create financial information structure matching template expectations."""
    business_analysis = company_data.get('business_analysis', {})
    raw_data = company_data.get('raw_data', {})
    
    # Try to extract financial data from various sources
    total_funding = (
        raw_data.get('total_funding', '') or 
        raw_data.get('funding', '') or 
        web_research.get('funding_status', '')
    )
    
    revenue = (
        raw_data.get('revenue', '') or 
        raw_data.get('arr', '') or 
        business_analysis.get('traction', '') if 'revenue' in business_analysis.get('traction', '').lower() else ''
    )
    
    valuation = (
        raw_data.get('valuation', '') or 
        raw_data.get('value', '') or
        ''
    )
    
    # Create funding rounds array if data is available
    funding_rounds = []
    last_round = raw_data.get('last_round', '') or web_research.get('funding_status', '')
    if last_round:
        funding_rounds.append({
            'type': 'Latest Round',
            'amount': total_funding,
            'date': raw_data.get('funding_date', 'Recent'),
            'leadInvestor': 'See detailed analysis'
        })
    
    return {
        'totalFunding': total_funding,
        'lastRound': last_round,
        'revenue': revenue,
        'valuation': valuation,
        'fundingRounds': funding_rounds
    }

def _create_executive_summary(company_data: Dict, web_research: Dict) -> str:
    """Create executive summary combining key points from existing analysis."""
    company_name = company_data.get('company_name', '')
    problem_analysis = company_data.get('problem_analysis', {})
    market_analysis = company_data.get('market_analysis', {})
    business_analysis = company_data.get('business_analysis', {})
    
    summary_parts = []
    
    # Company introduction
    industry = market_analysis.get('industry', 'technology')
    summary_parts.append(f"{company_name} is an innovative {industry} company")
    
    # Problem/solution fit
    if problem_analysis.get('statement'):
        summary_parts.append(f"addressing {problem_analysis['statement'][:100]}...")
    
    # Market positioning
    if market_analysis.get('target_audience'):
        summary_parts.append(f"serving {market_analysis['target_audience']}")
    
    # Traction/business status
    if business_analysis.get('traction'):
        summary_parts.append(f"with {business_analysis['traction']}")
    
    # Combine into cohesive summary
    if len(summary_parts) >= 2:
        return f"{summary_parts[0]} {summary_parts[1]}. The company has demonstrated {' and '.join(summary_parts[2:])} positioning them well for continued growth in the market."
    else:
        return f"{company_name} is a technology company with innovative solutions and strong market positioning, demonstrating potential for significant growth and value creation."

def _create_solution_description(company_data: Dict, web_research: Dict) -> str:
    """Create solution description from existing analysis."""
    product_analysis = company_data.get('product_analysis', {})
    problem_analysis = company_data.get('problem_analysis', {})
    
    solution = product_analysis.get('mvp', '') or product_analysis.get('description', '')
    if not solution:
        # Derive solution from problem statement
        problem = problem_analysis.get('statement', '')
        if problem:
            solution = f"Technology solution addressing {problem}"
        else:
            solution = "Innovative technology platform providing comprehensive solutions to market challenges"
    
    return solution

def _create_business_model(company_data: Dict, web_research: Dict) -> str:
    """Create business model description from existing analysis."""
    business_analysis = company_data.get('business_analysis', {})
    
    pricing = business_analysis.get('pricing', '')
    buyers = business_analysis.get('buyers', '')
    
    if pricing and buyers:
        return f"{pricing} targeting {buyers}"
    elif pricing:
        return f"{pricing} subscription model"
    elif buyers:
        return f"Service model targeting {buyers}"
    else:
        return "Scalable business model with multiple revenue streams including subscriptions and enterprise services"

def _create_product_overview(company_data: Dict, web_research: Dict) -> str:
    """Create product overview from existing analysis."""
    product_analysis = company_data.get('product_analysis', {})
    
    mvp = product_analysis.get('mvp', '')
    progress = product_analysis.get('progress', '')
    
    if mvp and progress:
        return f"{mvp}. Current development status: {progress}"
    elif mvp:
        return mvp
    elif progress:
        return f"Product development: {progress}"
    else:
        return "Technology platform designed to address market needs with scalable architecture and user-focused design"

def _extract_technology_stack(company_data: Dict, web_research: Dict) -> List[str]:
    """Extract technology stack information."""
    # Try to derive from product or market analysis
    product_analysis = company_data.get('product_analysis', {})
    market_analysis = company_data.get('market_analysis', {})
    
    tech_stack = []
    
    # Derive likely tech based on industry
    industry = market_analysis.get('industry', '').lower()
    if 'ai' in industry or 'artificial intelligence' in industry:
        tech_stack.extend(['Machine Learning', 'Python', 'TensorFlow'])
    elif 'saas' in industry or 'software' in industry:
        tech_stack.extend(['Cloud Infrastructure', 'API Integration', 'Database Management'])
    elif 'fintech' in industry:
        tech_stack.extend(['Secure Payment Processing', 'Blockchain', 'Data Analytics'])
    elif 'healthtech' in industry:
        tech_stack.extend(['Healthcare APIs', 'HIPAA Compliance', 'Data Security'])
    else:
        tech_stack.extend(['Modern Web Technologies', 'Cloud Computing', 'Mobile Development'])
    
    return tech_stack[:5]  # Limit to 5 items

def _extract_ip_info(company_data: Dict, web_research: Dict) -> List[str]:
    """Extract intellectual property information."""
    # Most startups won't have detailed IP info, provide placeholder
    return ['Proprietary technology and trade secrets']

def _extract_investment_status(company_data: Dict, web_research: Dict) -> str:
    """Extract investment status from web research primarily."""
    return web_research.get('investment_status', 'Investment status available in web research results')

def _create_swot_analysis(company_data: Dict, web_research: Dict) -> Dict:
    """Create SWOT analysis combining existing data insights with web research."""
    
    # Extract insights from existing data for SWOT
    strengths = []
    weaknesses = []
    opportunities = []
    threats = []
    
    # Analyze existing data for strengths
    problem_analysis = company_data.get('problem_analysis', {})
    if problem_analysis.get('score'):
        try:
            score = int(problem_analysis['score'].split('/')[0])
            if score >= 8:
                strengths.append("Strong problem-market fit identified")
            elif score >= 6:
                strengths.append("Good problem understanding")
        except:
            pass
    
    market_analysis = company_data.get('market_analysis', {})
    if market_analysis.get('industry_score'):
        try:
            score = int(market_analysis['industry_score'].split('/')[0])
            if score >= 8:
                strengths.append("Strong industry positioning")
        except:
            pass
    
    team_analysis = company_data.get('team_analysis', {})
    if team_analysis.get('founder_fit_score'):
        try:
            score = int(team_analysis['founder_fit_score'].split('/')[0])
            if score >= 8:
                strengths.append("Excellent founder-market fit")
            elif score < 6:
                weaknesses.append("Potential founder-market fit concerns")
        except:
            pass
    
    business_analysis = company_data.get('business_analysis', {})
    if business_analysis.get('traction'):
        traction = business_analysis['traction'].lower()
        if any(word in traction for word in ['strong', 'excellent', 'good', 'growing']):
            strengths.append("Demonstrated market traction")
        elif any(word in traction for word in ['limited', 'early', 'minimal']):
            weaknesses.append("Limited market traction")
    
    # Analyze for opportunities and threats
    if market_analysis.get('industry'):
        industry = market_analysis['industry'].lower()
        if any(word in industry for word in ['ai', 'saas', 'fintech', 'healthtech']):
            opportunities.append("Operating in high-growth technology sector")
        if 'enterprise' in industry:
            opportunities.append("Large enterprise market opportunity")
    
    if market_analysis.get('competitors'):
        competitors = market_analysis['competitors'].lower()
        if any(word in competitors for word in ['few', 'limited', 'niche']):
            opportunities.append("Limited direct competition")
        elif any(word in competitors for word in ['many', 'saturated', 'crowded']):
            threats.append("Highly competitive market")
    
    # Add web research insights if available
    if web_research.get('market_insights'):
        opportunities.append("Current market trends support growth")
    
    # Ensure we have some default content
    if not strengths:
        strengths = ["Existing structured analysis available", "Comprehensive data foundation"]
    if not weaknesses:
        weaknesses = ["Areas for improvement identified in analysis"]
    if not opportunities:
        opportunities = ["Market expansion potential", "Technology advancement opportunities"]
    if not threats:
        threats = ["Competitive market dynamics", "Technology disruption risk"]
    
    return {
        'strengths': strengths,
        'weaknesses': weaknesses, 
        'opportunities': opportunities,
        'threats': threats
    }


def process_companies_from_sheets(sheet_id: str, worksheet_name: str = "Sheet1") -> Dict:
    """
    Main function to process companies from Google Sheets with Drive upload and link updates.
    Returns summary of processing results.
    """
    results = {
        "success": False,
        "companies_processed": 0,
        "companies_failed": 0,
        "errors": [],
        "processed_companies": []
    }
    
    try:
        # Connect to the sheet
        if not sheets_integration.connect_to_sheet(sheet_id, worksheet_name):
            results["errors"].append("Failed to connect to Google Sheet")
            return results
        
        # Check that existing One-Pager and Deep-Dive columns are available for Drive links
        sheets_integration.add_drive_link_headers()
        
        # Get pending companies
        pending_companies = sheets_integration.get_pending_companies()
        
        if not pending_companies:
            results["success"] = True
            results["message"] = "No pending companies found"
            return results
        
        print(f"🚀 Starting to process {len(pending_companies)} companies...")
        
        # Import here to avoid circular imports
        from . import agents, pdf_generator
        from .google_drive import GoogleDriveManager
        
        # Initialize Google Drive manager
        try:
            drive_manager = GoogleDriveManager()
            print("✅ Google Drive manager initialized")
        except Exception as drive_error:
            print(f"⚠️ Google Drive initialization failed: {drive_error}")
            drive_manager = None
        
        for company_data in pending_companies:
            company_name = company_data.get('company_name', '')
            row_number = company_data.get('row_number')
            
            try:
                print(f"\n🏢 Processing: {company_name}")
                
                # Use NEW enhanced research agent (Agent 1) that combines existing data with web research
                research_result = agents.research_company(company_data, "comprehensive")
                
                if not research_result.get('success'):
                    raise Exception(f"Enhanced research agent failed: {research_result.get('error', 'Unknown error')}")
                
                # The enhanced research agent returns a ready-to-use intelligence brief
                intelligence_brief = research_result.get('research_data', {})
                
                if not intelligence_brief:
                    raise Exception("Enhanced research agent returned empty intelligence brief")
                
                # Generate both reports
                reports_generated = []
                report_types_list = []  # Track which reports were actually generated
                drive_links = {}  # Store Drive links for sheet update
                
                for report_type in ['one_pager', 'deep_dive']:
                    try:
                        formatted_markdown = agents.run_formatting_agent(intelligence_brief, report_type)
                        pdf_bytes = pdf_generator.create_professional_pdf(formatted_markdown, report_type)
                        
                        # Save PDF to file
                        company_safe_name = company_name.replace(' ', '_').replace('.', '_').replace('/', '_')
                        filename = f"{company_safe_name}_{report_type}.pdf"
                        filepath = f"./reports/{filename}"
                        
                        # Create reports directory if it doesn't exist
                        import os
                        os.makedirs("./reports", exist_ok=True)
                        
                        # Write PDF to file
                        with open(filepath, 'wb') as f:
                            f.write(pdf_bytes)
                        
                        print(f"💾 Saved {report_type} report to: {filepath}")
                        
                        # Upload to Google Drive if available
                        drive_link = ""
                        if drive_manager:
                            try:
                                upload_result = drive_manager.upload_pdf_to_drive(
                                    pdf_bytes, 
                                    filename,
                                    "AXL Startup Reports"
                                )
                                if upload_result:
                                    drive_link = upload_result.get('shareable_link', '')
                                    print(f"☁️ Uploaded to Drive: {drive_link}")
                                    drive_links[report_type] = drive_link
                            except Exception as upload_error:
                                print(f"⚠️ Drive upload failed for {filename}: {upload_error}")
                        
                        reports_generated.append({
                            "type": report_type,
                            "size_bytes": len(pdf_bytes),
                            "filename": filename,
                            "filepath": filepath,
                            "drive_link": drive_link,
                            "status": "generated"
                        })
                        report_types_list.append(report_type)  # Track successful generation
                        print(f"✅ Generated {report_type} report ({len(pdf_bytes)} bytes)")
                        
                    except Exception as report_error:
                        print(f"❌ Failed to generate {report_type}: {str(report_error)}")
                        reports_generated.append({
                            "type": report_type,
                            "error": str(report_error),
                            "status": "failed"
                        })
                
                # Update Google Sheet with Drive links
                if drive_links:
                    try:
                        sheets_integration.update_drive_links(
                            row_number,
                            one_pager_link=drive_links.get('one_pager', ''),
                            deep_dive_link=drive_links.get('deep_dive', '')
                        )
                        print(f"📋 Updated Google Sheet with {len(drive_links)} Drive links")
                    except Exception as link_error:
                        print(f"⚠️ Failed to update Drive links in sheet: {link_error}")
                
                # Mark as processed - simply set 'generated' field to 'yes' if any reports succeeded
                success = len(report_types_list) > 0  # At least one report was generated
                error_msg = "" if success else "Failed to generate any reports"
                
                sheets_integration.mark_company_as_processed(
                    row_number, 
                    success, 
                    error_message=error_msg
                )
                
                results["companies_processed"] += 1
                results["processed_companies"].append({
                    "company_name": company_name,
                    "reports": reports_generated,
                    "row_number": row_number,
                    "drive_links": drive_links
                })
                
                print(f"✅ Successfully processed {company_name}")
                
            except Exception as company_error:
                error_msg = f"Failed to process {company_name}: {str(company_error)}"
                print(f"❌ {error_msg}")
                
                # Mark as failed
                sheets_integration.mark_company_as_processed(row_number, False, str(company_error))
                
                results["companies_failed"] += 1
                results["errors"].append(error_msg)
        
        results["success"] = True
        print(f"\n🎉 Processing complete! Processed: {results['companies_processed']}, Failed: {results['companies_failed']}")
        
    except Exception as e:
        error_msg = f"Critical error in process_companies_from_sheets: {str(e)}"
        print(f"❌ {error_msg}")
        results["errors"].append(error_msg)
    
    return results 