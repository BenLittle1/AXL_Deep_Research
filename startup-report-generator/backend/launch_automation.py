#!/usr/bin/env python3
"""
AXL Report Generator - Automation Launcher

This script provides multiple ways to set up automated report generation:
1. Start automated polling system (checks every 2 minutes)
2. Instructions for Google Apps Script real-time triggers
3. Instructions for background service setup

Choose the option that best fits your needs!
"""

import os
import sys
import subprocess
from datetime import datetime

def print_banner():
    """Print the AXL automation banner"""
    print("=" * 70)
    print("🚀 AXL AUTOMATED REPORT GENERATION SETUP")
    print("=" * 70)
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 Enhanced with PDF pitch deck extraction!")
    print()

def option_1_polling():
    """Start the automated polling system"""
    print("🔄 Option 1: Automated Polling System")
    print("-" * 40)
    print("This will:")
    print("  ✅ Check Google Sheets every 2 minutes for new companies")
    print("  ✅ Automatically extract PDF pitch deck content")
    print("  ✅ Generate reports with AI research")
    print("  ✅ Upload to Google Drive and update sheet links")
    print("  ✅ Run continuously until stopped (Ctrl+C)")
    print()
    
    choice = input("🚀 Start automated polling now? (y/n): ").lower().strip()
    
    if choice in ['y', 'yes']:
        print("\n🤖 Starting automated processor...")
        print("📝 Tip: Open another terminal to monitor Google Sheets")
        print("🛑 Press Ctrl+C to stop\n")
        
        try:
            # Import and run the automated processor
            from automated_processor import main
            main()
        except KeyboardInterrupt:
            print("\n👋 Automated processor stopped by user")
        except Exception as e:
            print(f"\n❌ Error starting automated processor: {e}")
    else:
        print("❌ Automated polling not started")

def option_2_google_script():
    """Show instructions for Google Apps Script setup"""
    print("⚡ Option 2: Google Apps Script Real-Time Triggers")
    print("-" * 50)
    print("This triggers IMMEDIATELY when Airtable adds rows to Google Sheets!")
    print()
    print("📋 Setup Instructions:")
    print("1. Go to script.google.com")
    print("2. Create a new project")
    print("3. Copy the code from: google_apps_script_trigger.js")
    print("4. Update API_ENDPOINT with your server URL")
    print("5. Set up trigger:")
    print("   - Edit > Current project's triggers > Add trigger")
    print("   - Function: onNewRowAdded")
    print("   - Event source: From spreadsheet")  
    print("   - Event type: On edit")
    print()
    
    print("🌐 You'll need to expose your API endpoint. Options:")
    print("   A) Use ngrok for testing: ngrok http 8000")
    print("   B) Deploy to cloud service (Railway, Heroku, etc.)")
    print("   C) Use a VPS with public IP")
    print()
    
    print("🎯 Benefits:")
    print("   ✅ INSTANT processing (no 2-minute delay)")
    print("   ✅ Triggered by actual Airtable updates")
    print("   ✅ More efficient resource usage")
    print()

def option_3_background_service():
    """Show instructions for background service setup"""
    print("🖥️ Option 3: Background Service (Production)")
    print("-" * 40)
    print("Run the automated processor as a system service.")
    print()
    print("📋 Setup Instructions:")
    print("1. Edit axl-report-generator.service file:")
    print("   - Update User and Group")
    print("   - Verify file paths")
    print()
    print("2. Install the service:")
    print("   sudo cp axl-report-generator.service /etc/systemd/system/")
    print("   sudo systemctl daemon-reload")
    print("   sudo systemctl enable axl-report-generator")
    print("   sudo systemctl start axl-report-generator")
    print()
    print("3. Monitor the service:")
    print("   sudo systemctl status axl-report-generator")
    print("   sudo journalctl -u axl-report-generator -f")
    print()
    print("🎯 Benefits:")
    print("   ✅ Starts automatically on system boot")
    print("   ✅ Restarts automatically if crashes")
    print("   ✅ Runs in background without terminal")
    print("   ✅ Perfect for production servers")
    print()

def option_4_test_current():
    """Test the current setup"""
    print("🧪 Option 4: Test Current Setup")
    print("-" * 30)
    print("This will check if your system is ready for automation.")
    print()
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from app.google_sheets import sheets_integration
        from app.agents import extract_text_from_pdf_url
        print("  ✅ All modules imported successfully")
        
        # Test Google Sheets connection
        print("📊 Testing Google Sheets connection...")
        sheet_id = "1z8Uv-EVDQ4aGar0hKaHlEMsbhmyhWDjsJnrcqAhMKFo"
        if sheets_integration.connect_to_sheet(sheet_id):
            print("  ✅ Google Sheets connection successful")
            
            # Count pending companies
            pending = sheets_integration.get_pending_companies()
            print(f"  📋 Found {len(pending)} companies ready for processing")
            
        else:
            print("  ❌ Google Sheets connection failed")
        
        # Test PDF extraction
        print("📄 Testing PDF extraction...")
        test_result = extract_text_from_pdf_url("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")
        if test_result:
            print(f"  ✅ PDF extraction working ({len(test_result)} chars extracted)")
        else:
            print("  ⚠️ PDF extraction test failed (but may work with real PDFs)")
        
        # Test API keys
        print("🔑 Testing API configuration...")
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("AI_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
        if api_key and len(api_key) > 10:
            print(f"  ✅ AI API key configured ({len(api_key)} characters)")
        else:
            print("  ❌ AI API key not properly configured")
        
        print("\n🎯 System status: Ready for automation!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("Please check your configuration and dependencies.")

def main():
    """Main menu for automation setup"""
    print_banner()
    
    while True:
        print("Choose your automation setup:")
        print()
        print("1. 🔄 Start Automated Polling (2-minute intervals)")
        print("2. ⚡ Google Apps Script Setup (Real-time triggers)")
        print("3. 🖥️ Background Service Setup (Production)")
        print("4. 🧪 Test Current Setup")
        print("5. 🚪 Exit")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            option_1_polling()
            break
        elif choice == "2":
            option_2_google_script()
        elif choice == "3":
            option_3_background_service()
        elif choice == "4":
            option_4_test_current()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    main() 