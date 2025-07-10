#!/usr/bin/env python3
"""
Railway Deployment Helper Script

This script helps you prepare for deploying your AXL automated report generator to Railway.
It will check your environment variables and prepare them for Railway deployment.
"""

import os
import json
import sys
from pathlib import Path

def print_header():
    """Print header"""
    print("🚀" + "=" * 60)
    print("    AXL VENTURES - RAILWAY DEPLOYMENT HELPER")
    print("=" * 62 + "🚀")
    print()

def check_local_env():
    """Check current local environment variables"""
    print("🔍 CHECKING LOCAL ENVIRONMENT VARIABLES")
    print("-" * 40)
    
    env_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GOOGLE_CREDENTIALS_JSON': os.getenv('GOOGLE_CREDENTIALS_JSON'),
        'GOOGLE_SHEET_ID': os.getenv('GOOGLE_SHEET_ID'),
        'GOOGLE_WORKSHEET_NAME': os.getenv('GOOGLE_WORKSHEET_NAME'),
        'PERPLEXITY_API_KEY': os.getenv('PERPLEXITY_API_KEY'),
        'AI_API_KEY': os.getenv('AI_API_KEY'),
        'AI_API_ENDPOINT': os.getenv('AI_API_ENDPOINT'),
        'GOOGLE_DRIVE_PARENT_FOLDER_ID': os.getenv('GOOGLE_DRIVE_PARENT_FOLDER_ID')
    }
    
    required_vars = ['OPENAI_API_KEY', 'GOOGLE_CREDENTIALS_JSON', 'GOOGLE_SHEET_ID']
    optional_vars = ['PERPLEXITY_API_KEY', 'AI_API_KEY', 'AI_API_ENDPOINT', 'GOOGLE_DRIVE_PARENT_FOLDER_ID']
    
    all_good = True
    
    print("📋 REQUIRED VARIABLES:")
    for var in required_vars:
        value = env_vars[var]
        if value:
            if var == 'GOOGLE_CREDENTIALS_JSON':
                # Test if it's valid JSON
                try:
                    json.loads(value)
                    print(f"   ✅ {var}: Valid JSON ({len(value)} chars)")
                except json.JSONDecodeError:
                    print(f"   ❌ {var}: Invalid JSON format")
                    all_good = False
            else:
                # Show partial value for security
                masked_value = value[:8] + "..." if len(value) > 8 else value
                print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ❌ {var}: Not set")
            all_good = False
    
    print("\n📋 OPTIONAL VARIABLES:")
    for var in optional_vars:
        value = env_vars[var]
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ⚪ {var}: Not set")
    
    print()
    return all_good, env_vars

def generate_railway_env_file(env_vars):
    """Generate a Railway environment variables file"""
    print("📝 GENERATING RAILWAY ENVIRONMENT FILE")
    print("-" * 40)
    
    railway_env_file = "railway_env_variables.txt"
    
    with open(railway_env_file, 'w') as f:
        f.write("# Railway Environment Variables\n")
        f.write("# Copy and paste these into Railway dashboard > Variables tab\n")
        f.write("# " + "=" * 60 + "\n\n")
        
        for var, value in env_vars.items():
            if value:
                # For Google credentials, ensure it's on one line
                if var == 'GOOGLE_CREDENTIALS_JSON':
                    # Remove any newlines and format as single line
                    clean_value = value.replace('\n', '').replace(' ', '')
                    f.write(f"{var}={clean_value}\n")
                else:
                    f.write(f"{var}={value}\n")
        
        f.write("\n# Additional Railway-specific variables\n")
        f.write("PORT=8000\n")
        f.write("RAILWAY=true\n")
    
    print(f"✅ Environment file created: {railway_env_file}")
    print(f"📋 Copy the contents to Railway dashboard > Variables tab")
    return railway_env_file

def check_files():
    """Check if required files exist"""
    print("📁 CHECKING DEPLOYMENT FILES")
    print("-" * 40)
    
    required_files = [
        'requirements.txt',
        'railway_start.py',
        'backend/automated_processor.py',
        'backend/app/main.py'
    ]
    
    optional_files = [
        'railway.json',
        'Procfile'
    ]
    
    all_files_exist = True
    
    print("📋 REQUIRED FILES:")
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path}: Missing")
            all_files_exist = False
    
    print("\n📋 DEPLOYMENT CONFIG FILES:")
    for file_path in optional_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ⚪ {file_path}: Not found")
    
    print()
    return all_files_exist

def show_next_steps():
    """Show next steps for deployment"""
    print("🎯 NEXT STEPS FOR RAILWAY DEPLOYMENT")
    print("-" * 40)
    print()
    print("1. 🌐 Go to https://railway.app and sign up/log in")
    print("2. 📂 Click 'Start a New Project' > 'Deploy from GitHub repo'")
    print("3. 🔗 Connect your GitHub repository")
    print("4. 📁 Select the 'startup-report-generator' folder")
    print("5. ⚙️  In Railway dashboard, go to 'Variables' tab")
    print("6. 📝 Copy variables from 'railway_env_variables.txt'")
    print("7. 🚀 Click 'Deploy' and wait for build to complete")
    print("8. 📊 Check logs for startup messages")
    print("9. 🧪 Test with a company in your Google Sheet")
    print()
    print("💡 Detailed instructions: ./RAILWAY_DEPLOYMENT_GUIDE.md")

def main():
    """Main function"""
    print_header()
    
    # Check if we're in the right directory
    if not os.path.exists('backend/app/main.py'):
        print("❌ ERROR: Run this script from the startup-report-generator directory")
        print("📁 Current directory:", os.getcwd())
        print("🔄 Please cd to the startup-report-generator directory first")
        return
    
    # Check local environment
    env_ok, env_vars = check_local_env()
    
    # Check files
    files_ok = check_files()
    
    if env_ok and files_ok:
        print("✅ ALL CHECKS PASSED - READY FOR RAILWAY DEPLOYMENT!")
        print()
        
        # Generate Railway env file
        railway_env_file = generate_railway_env_file(env_vars)
        print()
        
        # Show next steps
        show_next_steps()
        
        print()
        print("🎉 You're ready to deploy to Railway!")
        
    else:
        print("❌ DEPLOYMENT NOT READY")
        print()
        if not env_ok:
            print("🔧 Fix environment variables:")
            print("   - Create/update your .env file")
            print("   - Source the environment: source backend/venv/bin/activate")
            print("   - Load .env: set -a; source .env; set +a")
        
        if not files_ok:
            print("🔧 Missing deployment files:")
            print("   - Make sure you're in the startup-report-generator directory")
            print("   - Ensure all required files exist")
        
        print()
        print("📖 See RAILWAY_DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main() 