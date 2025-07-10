#!/usr/bin/env python3
"""
Airtable Sync Menu System

Interactive menu to help you choose and configure the best
Google Sheets to Airtable sync option for your needs.
"""

import os
import subprocess
import webbrowser
from typing import Dict, Any

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header"""
    print("🔄" + "=" * 60)
    print("     AXL VENTURES - GOOGLE SHEETS TO AIRTABLE SYNC")
    print("=" * 62 + "🔄")
    print()

def print_options():
    """Print the main menu options"""
    print("📋 SYNC OPTIONS:")
    print()
    print("1. 🌟 Airtable Sync (Recommended - 5 minutes)")
    print("   ✅ Built-in, reliable, no coding required")
    print("   ⏰ 15 min to daily sync frequency")
    print("   💰 Free with all Airtable plans")
    print()
    print("2. 🔗 Zapier Integration (Real-time)")
    print("   ✅ Instant updates, visual setup")
    print("   ⚡ Real-time triggers on changes")
    print("   💰 Free tier: 100 tasks/month")
    print()
    print("3. 🛠️  Google Apps Script (Advanced)")
    print("   ✅ Custom logic, free with Google")
    print("   🎯 Advanced field transformations")
    print("   💰 Free with Google Workspace")
    print()
    print("4. 🐍 Python Script Integration")
    print("   ✅ Works with existing system")
    print("   🔧 Advanced data processing")
    print("   💰 Free (server costs only)")
    print()
    print("5. 🧪 Test Airtable Connection")
    print("6. 📖 View Setup Guide")
    print("7. ❌ Exit")
    print()

def get_user_choice() -> str:
    """Get user's menu choice"""
    while True:
        choice = input("👉 Enter your choice (1-7): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            return choice
        print("❌ Invalid choice. Please enter 1-7.")

def option_1_airtable_sync():
    """Guide user through Airtable's built-in sync"""
    clear_screen()
    print_header()
    print("🌟 AIRTABLE SYNC SETUP")
    print("=" * 40)
    print()
    print("This is the EASIEST option! Let's get you set up:")
    print()
    print("📋 Step-by-step instructions:")
    print()
    print("1. Open your Airtable base in a browser")
    print("2. Click the '+' button to add a new table")
    print("3. Select 'Sync with external data'")
    print("4. Choose 'Google Sheets' from the list")
    print("5. Authenticate with your Google account")
    print("6. Select your Google Sheet and worksheet")
    print("7. Configure sync frequency (recommend: every hour)")
    print("8. Map your fields (see the setup guide for mapping)")
    print("9. Click 'Sync' to start!")
    print()
    
    choice = input("🌐 Open Airtable in browser? (y/n): ").lower()
    if choice == 'y':
        webbrowser.open('https://airtable.com')
        print("✅ Airtable opened in browser")
    
    print()
    print("📖 Need the field mapping guide?")
    choice = input("Open setup guide? (y/n): ").lower()
    if choice == 'y':
        guide_path = os.path.join(os.path.dirname(__file__), '..', 'AIRTABLE_SYNC_SETUP.md')
        if os.path.exists(guide_path):
            if os.name == 'nt':  # Windows
                os.startfile(guide_path)
            else:  # macOS/Linux
                subprocess.run(['open', guide_path] if os.name == 'darwin' else ['xdg-open', guide_path])
        else:
            print("📖 Setup guide: ./AIRTABLE_SYNC_SETUP.md")
    
    input("\n✅ Press Enter when you're done setting up...")

def option_2_zapier_integration():
    """Guide user through Zapier setup"""
    clear_screen()
    print_header()
    print("🔗 ZAPIER INTEGRATION SETUP")
    print("=" * 40)
    print()
    print("Real-time sync with advanced automation!")
    print()
    print("📋 Setup steps:")
    print()
    print("1. Create a Zapier account (zapier.com)")
    print("2. Create a new Zap")
    print("3. Trigger: Google Sheets - 'New/Updated Row'")
    print("4. Action: Airtable - 'Create/Update Record'")
    print("5. Connect both accounts")
    print("6. Map your fields")
    print("7. Test and activate!")
    print()
    
    print("💰 Pricing:")
    print("   - Free: 100 tasks/month")
    print("   - Starter: $19.99/month for 750 tasks")
    print("   - Professional: $49/month for 2,000 tasks")
    print()
    
    choice = input("🌐 Open Zapier in browser? (y/n): ").lower()
    if choice == 'y':
        webbrowser.open('https://zapier.com/app/zaps')
        print("✅ Zapier opened in browser")
    
    input("\n✅ Press Enter to continue...")

def option_3_google_apps_script():
    """Guide user through Google Apps Script setup"""
    clear_screen()
    print_header()
    print("🛠️ GOOGLE APPS SCRIPT SETUP")
    print("=" * 40)
    print()
    print("Advanced automation with custom logic!")
    print()
    print("📋 You'll need:")
    print("   ✅ Airtable API credentials")
    print("   ✅ Basic JavaScript knowledge (optional)")
    print()
    
    print("🔑 First, get your Airtable credentials:")
    print("   1. Go to airtable.com/account")
    print("   2. Create a personal access token")
    print("   3. Note your Base ID from airtable.com/api")
    print()
    
    choice = input("🌐 Open Airtable account page? (y/n): ").lower()
    if choice == 'y':
        webbrowser.open('https://airtable.com/account')
        print("✅ Airtable account page opened")
    
    print()
    print("📝 Next, set up the script:")
    print("   1. Go to script.google.com")
    print("   2. Create new project")
    print("   3. Copy the script from: google_sheets_to_airtable_sync.js")
    print("   4. Update the configuration with your credentials")
    print("   5. Test the connection")
    print("   6. Set up automatic triggers")
    print()
    
    choice = input("🌐 Open Google Apps Script? (y/n): ").lower()
    if choice == 'y':
        webbrowser.open('https://script.google.com')
        print("✅ Google Apps Script opened")
    
    script_path = os.path.join(os.path.dirname(__file__), 'google_sheets_to_airtable_sync.js')
    print(f"\n📄 Script file location: {script_path}")
    
    input("\n✅ Press Enter to continue...")

def option_4_python_script():
    """Guide user through Python script setup"""
    clear_screen()
    print_header()
    print("🐍 PYTHON SCRIPT INTEGRATION")
    print("=" * 40)
    print()
    print("Integrate with your existing Python workflow!")
    print()
    
    # Check if in virtual environment
    in_venv = hasattr(subprocess.sys, 'real_prefix') or (
        hasattr(subprocess.sys, 'base_prefix') and subprocess.sys.base_prefix != subprocess.sys.prefix
    )
    
    print("🔍 Environment check:")
    print(f"   Python version: {subprocess.sys.version.split()[0]}")
    print(f"   Virtual environment: {'✅ Active' if in_venv else '❌ Not detected'}")
    print()
    
    if not in_venv:
        print("⚠️  Recommendation: Activate your virtual environment first")
        print("   cd startup-report-generator/backend")
        print("   source venv/bin/activate  # or venv\\Scripts\\activate on Windows")
        print()
    
    print("📋 Setup steps:")
    print("   1. Install required packages")
    print("   2. Configure environment variables (.env)")
    print("   3. Test the connection")
    print("   4. Integrate with existing workflow")
    print()
    
    print("🔑 Required environment variables:")
    print("   AIRTABLE_BASE_ID=appXXXXXXXXXXXX")
    print("   AIRTABLE_TABLE_NAME=Companies")
    print("   AIRTABLE_API_KEY=patXXXXXXXXXXXX")
    print()
    
    choice = input("🚀 Run setup commands now? (y/n): ").lower()
    if choice == 'y':
        print("\n🔧 Running setup...")
        try:
            # Install requirements
            subprocess.run(['pip', 'install', 'requests', 'python-dotenv'], check=True)
            print("✅ Packages installed successfully")
            
            # Check if .env exists
            env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
            if not os.path.exists(env_path):
                print("\n📝 Creating .env template...")
                with open(env_path, 'w') as f:
                    f.write("# Airtable Configuration\n")
                    f.write("AIRTABLE_BASE_ID=appXXXXXXXXXXXX\n")
                    f.write("AIRTABLE_TABLE_NAME=Companies\n")
                    f.write("AIRTABLE_API_KEY=patXXXXXXXXXXXX\n")
                    f.write("\n# Google Sheets Configuration\n")
                    f.write("GOOGLE_SHEET_ID=1z8Uv-EVDQ4aGar0hKaHlEMsbhmyhWDjsJnrcqAhMKFo\n")
                    f.write("GOOGLE_WORKSHEET_NAME=Sheet1\n")
                print(f"✅ .env template created: {env_path}")
                print("📝 Please edit this file with your actual credentials")
            else:
                print("✅ .env file already exists")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error during setup: {e}")
    
    input("\n✅ Press Enter to continue...")

def option_5_test_connection():
    """Test Airtable connection"""
    clear_screen()
    print_header()
    print("🧪 TEST AIRTABLE CONNECTION")
    print("=" * 40)
    print()
    
    # Check if environment variables are set
    base_id = os.getenv('AIRTABLE_BASE_ID')
    api_key = os.getenv('AIRTABLE_API_KEY')
    table_name = os.getenv('AIRTABLE_TABLE_NAME', 'Companies')
    
    print("🔍 Checking configuration...")
    print(f"   Base ID: {'✅ Set' if base_id else '❌ Not set'}")
    print(f"   API Key: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"   Table Name: {table_name}")
    print()
    
    if not base_id or not api_key:
        print("❌ Missing required environment variables!")
        print("   Please set AIRTABLE_BASE_ID and AIRTABLE_API_KEY in your .env file")
        print()
        print("🔑 Get credentials from:")
        print("   - API Key: https://airtable.com/account")
        print("   - Base ID: https://airtable.com/api")
        print()
        choice = input("🌐 Open Airtable account page? (y/n): ").lower()
        if choice == 'y':
            webbrowser.open('https://airtable.com/account')
    else:
        print("🧪 Testing connection...")
        try:
            from airtable_sync import AirtableSync
            sync = AirtableSync()
            if sync.test_connection():
                print("🎉 Connection test successful!")
            else:
                print("❌ Connection test failed")
        except ImportError:
            print("❌ airtable_sync.py not found or has import errors")
            print("   Make sure you're in the correct directory and have installed requirements")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    input("\n✅ Press Enter to continue...")

def option_6_view_guide():
    """Open the setup guide"""
    clear_screen()
    print_header()
    print("📖 SETUP GUIDE")
    print("=" * 40)
    print()
    
    guide_path = os.path.join(os.path.dirname(__file__), '..', 'AIRTABLE_SYNC_SETUP.md')
    
    if os.path.exists(guide_path):
        print(f"📄 Opening setup guide: {guide_path}")
        try:
            if os.name == 'nt':  # Windows
                os.startfile(guide_path)
            elif os.name == 'darwin':  # macOS
                subprocess.run(['open', guide_path])
            else:  # Linux
                subprocess.run(['xdg-open', guide_path])
            print("✅ Guide opened in your default markdown viewer")
        except Exception as e:
            print(f"❌ Could not open automatically: {e}")
            print(f"📖 Please open manually: {guide_path}")
    else:
        print("❌ Setup guide not found!")
        print(f"Expected location: {guide_path}")
    
    print()
    print("🌐 You can also view the guide online or in your text editor")
    
    input("\n✅ Press Enter to continue...")

def main():
    """Main menu loop"""
    while True:
        clear_screen()
        print_header()
        print_options()
        
        choice = get_user_choice()
        
        if choice == '1':
            option_1_airtable_sync()
        elif choice == '2':
            option_2_zapier_integration()
        elif choice == '3':
            option_3_google_apps_script()
        elif choice == '4':
            option_4_python_script()
        elif choice == '5':
            option_5_test_connection()
        elif choice == '6':
            option_6_view_guide()
        elif choice == '7':
            clear_screen()
            print("👋 Thanks for using AXL Airtable Sync!")
            print("📧 Need help? Contact the development team")
            break

if __name__ == "__main__":
    main() 