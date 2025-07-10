#!/usr/bin/env python3
"""
Google Sheets to Airtable Sync Script

This script syncs your Google Sheets data to Airtable automatically.
It can be integrated into your existing automated report generation workflow.

Usage:
    python airtable_sync.py

Features:
- Sync all data or only changes
- Configurable field mapping
- Batch processing for efficiency
- Error handling and logging
- Integration with existing Google Sheets connection
"""

import os
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import existing Google Sheets integration
from app.google_sheets import sheets_integration

class AirtableSync:
    def __init__(self):
        # Airtable configuration
        self.base_id = os.getenv('AIRTABLE_BASE_ID')
        self.table_name = os.getenv('AIRTABLE_TABLE_NAME', 'Companies')
        self.api_key = os.getenv('AIRTABLE_API_KEY')
        
        # Google Sheets configuration
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID', '1z8Uv-EVDQ4aGar0hKaHlEMsbhmyhWDjsJnrcqAhMKFo')
        self.worksheet_name = os.getenv('GOOGLE_WORKSHEET_NAME', 'Sheet1')
        
        # Field mapping: Google Sheets column -> Airtable field name
        self.field_mapping = {
            'company_name': 'Company Name',
            'Status': 'Status',
            'website': 'Website',
            'problem_statement': 'Problem Statement',
            'problem_statement_commentary': 'Problem Commentary',
            'problem_statement_score': 'Problem Score',
            'industry': 'Industry',
            'competitors': 'Competitors',
            'target_audience': 'Target Audience',
            'mvp': 'MVP Status',
            'progress': 'Product Progress',
            'founder_fit': 'Founder Fit',
            'team_growth': 'Team Growth',
            'traction': 'Traction',
            'pricing': 'Pricing Model',
            'location': 'Location',
            'pdf_url': 'PDF URL',
            'one_pager_link': 'One-Pager Link',
            'deep_dive_link': 'Deep-Dive Link',
            'generated': 'Reports Generated'
        }
        
        # Sync configuration
        self.batch_size = 10
        self.unique_field = 'Company Name'
        self.rate_limit_delay = 0.2  # 200ms between requests
        
        self.validate_config()
    
    def validate_config(self):
        """Validate that all required configuration is present"""
        if not self.api_key:
            raise ValueError("AIRTABLE_API_KEY not found in environment variables")
        if not self.base_id:
            raise ValueError("AIRTABLE_BASE_ID not found in environment variables")
        
        print(f"✅ Airtable configuration validated")
        print(f"   - Base ID: {self.base_id}")
        print(f"   - Table: {self.table_name}")
        print(f"   - Sheet ID: {self.sheet_id}")
    
    def get_google_sheets_data(self) -> List[Dict]:
        """Get all company data from Google Sheets"""
        try:
            print(f"📊 Connecting to Google Sheets...")
            
            # Connect to the sheet
            if not sheets_integration.connect_to_sheet(self.sheet_id, self.worksheet_name):
                raise Exception("Failed to connect to Google Sheets")
            
            # Get all companies (not just pending ones)
            all_values = sheets_integration.worksheet.get_all_values()
            if not all_values:
                return []
            
            headers = all_values[0]
            rows = all_values[1:]
            
            companies = []
            for i, row in enumerate(rows, start=2):
                row_dict = {}
                for j, header in enumerate(headers):
                    if j < len(row):
                        row_dict[header] = row[j]
                        row_dict[header.lower().replace(' ', '_').replace('-', '_')] = row[j]
                    else:
                        row_dict[header] = ""
                        row_dict[header.lower().replace(' ', '_').replace('-', '_')] = ""
                
                row_dict['row_number'] = i
                
                # Only include rows with company names
                if row_dict.get('company_name', '').strip():
                    companies.append(row_dict)
            
            print(f"📋 Found {len(companies)} companies in Google Sheets")
            return companies
            
        except Exception as e:
            print(f"❌ Error getting Google Sheets data: {e}")
            return []
    
    def get_airtable_records(self) -> List[Dict]:
        """Get existing records from Airtable"""
        try:
            url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            all_records = []
            offset = None
            
            while True:
                params = {}
                if offset:
                    params['offset'] = offset
                
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                all_records.extend(data.get('records', []))
                
                offset = data.get('offset')
                if not offset:
                    break
                
                time.sleep(self.rate_limit_delay)
            
            print(f"📋 Found {len(all_records)} existing records in Airtable")
            return all_records
            
        except Exception as e:
            print(f"❌ Error getting Airtable records: {e}")
            return []
    
    def convert_to_airtable_record(self, sheet_row: Dict) -> Dict:
        """Convert Google Sheets row to Airtable record format"""
        fields = {}
        
        for sheet_field, airtable_field in self.field_mapping.items():
            value = sheet_row.get(sheet_field, '').strip()
            
            if value:
                # Handle different data types
                if sheet_field in ['problem_statement_score', 'problem_frequency_score']:
                    # Convert scores to numbers if possible
                    try:
                        if '/' in value:
                            # Handle "8/10" format
                            numerator = value.split('/')[0]
                            value = float(numerator)
                        else:
                            value = float(value)
                    except ValueError:
                        pass  # Keep as string if conversion fails
                
                fields[airtable_field] = value
        
        return {'fields': fields}
    
    def find_existing_record(self, airtable_records: List[Dict], company_name: str) -> Optional[Dict]:
        """Find existing record in Airtable by company name"""
        for record in airtable_records:
            if record.get('fields', {}).get(self.unique_field) == company_name:
                return record
        return None
    
    def create_airtable_record(self, fields: Dict) -> bool:
        """Create new record in Airtable"""
        try:
            url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {'fields': fields}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating record: {e}")
            return False
    
    def update_airtable_record(self, record_id: str, fields: Dict) -> bool:
        """Update existing record in Airtable"""
        try:
            url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}/{record_id}"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {'fields': fields}
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating record: {e}")
            return False
    
    def sync_to_airtable(self, create_new: bool = True, update_existing: bool = True) -> Dict:
        """Main sync function"""
        try:
            print("🔄 Starting Google Sheets to Airtable sync...")
            
            # Get data from both sources
            sheet_data = self.get_google_sheets_data()
            airtable_records = self.get_airtable_records()
            
            if not sheet_data:
                return {'success': False, 'error': 'No data found in Google Sheets'}
            
            # Process records
            created_count = 0
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            for sheet_row in sheet_data:
                try:
                    company_name = sheet_row.get('company_name', '').strip()
                    if not company_name:
                        skipped_count += 1
                        continue
                    
                    # Convert to Airtable format
                    airtable_record = self.convert_to_airtable_record(sheet_row)
                    fields = airtable_record['fields']
                    
                    if not fields:
                        skipped_count += 1
                        continue
                    
                    # Check if record exists
                    existing_record = self.find_existing_record(airtable_records, company_name)
                    
                    if existing_record and update_existing:
                        # Update existing record
                        if self.update_airtable_record(existing_record['id'], fields):
                            updated_count += 1
                            print(f"✅ Updated: {company_name}")
                        else:
                            error_count += 1
                    elif not existing_record and create_new:
                        # Create new record
                        if self.create_airtable_record(fields):
                            created_count += 1
                            print(f"✅ Created: {company_name}")
                        else:
                            error_count += 1
                    else:
                        skipped_count += 1
                        print(f"⏭️ Skipped: {company_name}")
                    
                    # Rate limiting
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    print(f"❌ Error processing {sheet_row.get('company_name', 'unknown')}: {e}")
                    error_count += 1
            
            # Summary
            total_processed = created_count + updated_count + skipped_count + error_count
            
            print("\n✅ Sync completed!")
            print(f"📊 Summary:")
            print(f"   - Total processed: {total_processed}")
            print(f"   - Created: {created_count}")
            print(f"   - Updated: {updated_count}")
            print(f"   - Skipped: {skipped_count}")
            print(f"   - Errors: {error_count}")
            
            return {
                'success': True,
                'total_processed': total_processed,
                'created': created_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'errors': error_count
            }
            
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_connection(self) -> bool:
        """Test connections to both Google Sheets and Airtable"""
        print("🧪 Testing connections...")
        
        # Test Google Sheets
        try:
            sheet_data = self.get_google_sheets_data()
            print(f"✅ Google Sheets: Connected ({len(sheet_data)} companies)")
        except Exception as e:
            print(f"❌ Google Sheets: Failed - {e}")
            return False
        
        # Test Airtable
        try:
            airtable_records = self.get_airtable_records()
            print(f"✅ Airtable: Connected ({len(airtable_records)} records)")
        except Exception as e:
            print(f"❌ Airtable: Failed - {e}")
            return False
        
        # Test field mapping
        print("🔄 Field mapping:")
        for sheet_field, airtable_field in self.field_mapping.items():
            print(f"  {sheet_field} -> {airtable_field}")
        
        return True

def main():
    """Main function for command-line usage"""
    print("🔄 AXL Google Sheets to Airtable Sync")
    print("=" * 50)
    
    try:
        sync = AirtableSync()
        
        # Test connection first
        if not sync.test_connection():
            print("❌ Connection test failed. Please check your configuration.")
            return
        
        # Run sync
        result = sync.sync_to_airtable()
        
        if result['success']:
            print(f"\n🎉 Sync completed successfully!")
        else:
            print(f"\n❌ Sync failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 