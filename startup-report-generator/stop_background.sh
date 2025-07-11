#!/bin/bash

# AXL Background Automation Stopper
# This script stops the background automation

echo "🛑 Stopping AXL Automated Report Generator..."

# Check if running
if ! pgrep -f "automated_processor.py" > /dev/null; then
    echo "⚠️  Automation is not running."
    exit 1
fi

# Show current process info
echo "📊 Current process info:"
ps aux | grep automated_processor.py | grep -v grep

# Stop the process
echo "🔄 Stopping automation..."
pkill -f "automated_processor.py"

# Wait a moment for graceful shutdown
sleep 2

# Check if stopped
if ! pgrep -f "automated_processor.py" > /dev/null; then
    echo "✅ Automation stopped successfully!"
else
    echo "⚠️  Process still running, forcing stop..."
    pkill -9 -f "automated_processor.py"
    sleep 1
    
    if ! pgrep -f "automated_processor.py" > /dev/null; then
        echo "✅ Automation force-stopped successfully!"
    else
        echo "❌ Failed to stop automation"
        exit 1
    fi
fi

echo ""
echo "🔧 To start again: ./start_background.sh"
echo "📖 Final logs: tail backend/automation.log" 