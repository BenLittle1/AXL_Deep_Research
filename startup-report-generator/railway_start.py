#!/usr/bin/env python3
"""
Railway deployment startup script
Runs both the FastAPI web app and the automated processor
"""
import sys
import os
import subprocess
import time
import signal
import threading
from multiprocessing import Process

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Global process references
web_process = None
automation_process = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n🛑 Received shutdown signal ({signum})")
    
    if web_process and web_process.is_alive():
        print("📡 Stopping web server...")
        web_process.terminate()
        web_process.join(timeout=5)
    
    if automation_process and automation_process.is_alive():
        print("🤖 Stopping automation processor...")
        automation_process.terminate()
        automation_process.join(timeout=5)
    
    print("👋 Railway deployment shutdown complete")
    sys.exit(0)

def run_web_server():
    """Run the FastAPI web server"""
    try:
        print("🌐 Starting FastAPI web server...")
        import uvicorn
        from app.main import app
        
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"❌ Web server error: {e}")
        time.sleep(5)  # Wait before retry

def run_automation_processor():
    """Run the automated report processor"""
    try:
        print("🤖 Starting automated report processor...")
        
        # Change to backend directory
        original_cwd = os.getcwd()
        os.chdir(backend_path)
        
        # Import and run the automated processor
        from automated_processor import main as automation_main
        automation_main()
        
    except Exception as e:
        print(f"❌ Automation processor error: {e}")
        time.sleep(10)  # Wait before retry
    finally:
        os.chdir(original_cwd)

def health_check_loop():
    """Monitor and restart processes if they die"""
    global web_process, automation_process
    
    while True:
        try:
            # Check web server
            if not web_process or not web_process.is_alive():
                print("🔄 Restarting web server...")
                if web_process:
                    web_process.terminate()
                web_process = Process(target=run_web_server)
                web_process.daemon = True
                web_process.start()
            
            # Check automation processor
            if not automation_process or not automation_process.is_alive():
                print("🔄 Restarting automation processor...")
                if automation_process:
                    automation_process.terminate()
                automation_process = Process(target=run_automation_processor)
                automation_process.daemon = True
                automation_process.start()
            
            time.sleep(30)  # Health check every 30 seconds
            
        except Exception as e:
            print(f"❌ Health check error: {e}")
            time.sleep(30)

def main():
    """Main Railway startup function"""
    global web_process, automation_process
    
    print("🚀" + "=" * 50)
    print("   AXL VENTURES - RAILWAY DEPLOYMENT")
    print("=" * 52 + "🚀")
    print()
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Verify environment
    required_env_vars = [
        'OPENAI_API_KEY',
        'GOOGLE_CREDENTIALS_JSON'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("🔧 Please set these in Railway dashboard")
        return
    
    print("✅ Environment variables validated")
    print()
    
    try:
        # Start web server
        print("🌐 Starting web server process...")
        web_process = Process(target=run_web_server)
        web_process.daemon = True
        web_process.start()
        time.sleep(2)
        
        # Start automation processor
        print("🤖 Starting automation processor...")
        automation_process = Process(target=run_automation_processor)
        automation_process.daemon = True
        automation_process.start()
        time.sleep(2)
        
        print()
        print("✅ Both services started successfully!")
        print("🌐 Web app: Available on Railway URL")
        print("🤖 Automation: Monitoring Google Sheets every 2 minutes")
        print("📊 Logs: Available in Railway dashboard")
        print()
        print("🔄 Starting health monitoring...")
        
        # Start health check monitoring
        health_check_loop()
        
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        signal_handler(signal.SIGTERM, None)

if __name__ == "__main__":
    main() 