#!/usr/bin/env python3
"""
Automated Report Generation System

This script continuously monitors Google Sheets for new companies and automatically
generates reports when they appear. Perfect for integration with Airtable workflows.

Usage:
    python automated_processor.py

The script will:
1. Check Google Sheets every 2 minutes for new companies
2. Automatically process any companies with blank "generated" status
3. Extract PDF pitch deck content if PDF_URL exists
4. Generate beautiful reports with AI research
5. Upload to Google Drive and update sheet links
6. Continue monitoring indefinitely
"""

import time
import traceback
import signal
import sys
from datetime import datetime
from app.google_sheets import process_companies_from_sheets

# Configuration
SHEET_ID = "1z8Uv-EVDQ4aGar0hKaHlEMsbhmyhWDjsJnrcqAhMKFo"  # Your Google Sheet ID
WORKSHEET_NAME = "Sheet1"  # Your worksheet name
CHECK_INTERVAL_MINUTES = 2  # How often to check for new companies
MAX_COMPANIES_PER_BATCH = 5  # Process maximum 5 companies at once

class AutomatedProcessor:
    def __init__(self, sheet_id: str, worksheet_name: str = "Sheet1"):
        self.sheet_id = sheet_id
        self.worksheet_name = worksheet_name
        self.running = True
        self.processed_count = 0
        self.error_count = 0
        
        # Set up graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received shutdown signal ({signum})")
        print("📊 Final Statistics:")
        print(f"   - Companies processed: {self.processed_count}")
        print(f"   - Errors encountered: {self.error_count}")
        print("👋 Shutting down automated processor...")
        self.running = False
        sys.exit(0)
    
    def start_monitoring(self):
        """Start the automated monitoring and processing loop"""
        print("🤖 AXL AUTOMATED REPORT GENERATOR STARTED")
        print("=" * 60)
        print(f"📊 Configuration:")
        print(f"   - Google Sheet ID: {self.sheet_id}")
        print(f"   - Worksheet: {self.worksheet_name}")
        print(f"   - Check interval: {CHECK_INTERVAL_MINUTES} minutes")
        print(f"   - Max batch size: {MAX_COMPANIES_PER_BATCH} companies")
        print(f"   - Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("🔄 Monitoring for new companies... (Ctrl+C to stop)")
        
        while self.running:
            try:
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"\n⏰ [{current_time}] Checking for new companies...")
                
                # Process companies from Google Sheets
                results = process_companies_from_sheets(self.sheet_id, self.worksheet_name)
                
                if results.get("success"):
                    companies_processed = results.get("companies_processed", 0)
                    companies_failed = results.get("companies_failed", 0)
                    
                    if companies_processed > 0:
                        self.processed_count += companies_processed
                        print(f"✅ [{current_time}] Processed {companies_processed} companies successfully!")
                        
                        # Show details of processed companies
                        for company in results.get("processed_companies", []):
                            company_name = company.get("company_name", "Unknown")
                            reports = company.get("reports", [])
                            drive_links = company.get("drive_links", {})
                            
                            print(f"   🏢 {company_name}:")
                            for report in reports:
                                if report.get("status") == "generated":
                                    report_type = report.get("type", "unknown")
                                    size_kb = report.get("size_bytes", 0) // 1024
                                    print(f"      ✅ {report_type}: {size_kb}KB")
                            
                            if drive_links:
                                print(f"      📁 Drive links: {len(drive_links)} uploaded")
                    
                    if companies_failed > 0:
                        self.error_count += companies_failed
                        print(f"❌ [{current_time}] {companies_failed} companies failed processing")
                        
                        # Show error details
                        for error in results.get("errors", []):
                            print(f"   ❌ {error}")
                    
                    if companies_processed == 0 and companies_failed == 0:
                        print(f"📭 [{current_time}] No new companies found")
                
                else:
                    error_msg = results.get("errors", ["Unknown error"])[0] if results.get("errors") else "Unknown error"
                    print(f"❌ [{current_time}] Processing failed: {error_msg}")
                    self.error_count += 1
                
                # Show running statistics
                if self.processed_count > 0 or self.error_count > 0:
                    print(f"📊 Running totals: {self.processed_count} processed, {self.error_count} errors")
                
                # Wait before next check
                print(f"⏳ Waiting {CHECK_INTERVAL_MINUTES} minutes until next check...")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)
                
            except KeyboardInterrupt:
                print(f"\n🛑 Interrupted by user")
                break
            except Exception as e:
                error_time = datetime.now().strftime('%H:%M:%S')
                print(f"❌ [{error_time}] Unexpected error: {str(e)}")
                print(f"❌ Error details: {traceback.format_exc()}")
                self.error_count += 1
                
                # Wait a bit before retrying
                print(f"⏳ Waiting {CHECK_INTERVAL_MINUTES} minutes before retry...")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)
        
        print("\n👋 Automated processor stopped.")

def main():
    """Main entry point"""
    processor = AutomatedProcessor(SHEET_ID, WORKSHEET_NAME)
    processor.start_monitoring()

if __name__ == "__main__":
    main() 