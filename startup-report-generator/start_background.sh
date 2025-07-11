#!/bin/bash

# AXL Background Automation Starter
# This script starts the automation in the background and detaches it from the terminal

echo "🚀 Starting AXL Automated Report Generator in background..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Change to backend directory
cd "$BACKEND_DIR"

# Check if already running
if pgrep -f "automated_processor.py" > /dev/null; then
    echo "⚠️  Automation is already running!"
    echo "📊 Process info:"
    ps aux | grep automated_processor.py | grep -v grep
    echo ""
    echo "🛑 To stop: ./stop_background.sh"
    echo "📖 To view logs: tail -f automation.log"
    exit 1
fi

# Start the automation in background
echo "🤖 Starting automated processor..."
nohup python automated_processor.py > automation.log 2>&1 &
PID=$!

# Wait a moment to check if it started successfully
sleep 2

if ps -p $PID > /dev/null; then
    echo "✅ Automation started successfully!"
    echo "📊 Process ID: $PID"
    echo "📁 Working directory: $BACKEND_DIR"
    echo "📖 Log file: $BACKEND_DIR/automation.log"
    echo ""
    echo "📋 What's happening:"
    echo "   🔍 Checking Google Sheets every 2 minutes"
    echo "   📊 Processing companies with status 'Reviewed - Promising'"
    echo "   📄 Generating PDF reports with AI research"
    echo "   ✅ Updating sheet with completion status"
    echo ""
    echo "🔧 Management commands:"
    echo "   📖 View logs:    tail -f automation.log"
    echo "   📊 Check status: ps aux | grep automated_processor"
    echo "   🛑 Stop:         ./stop_background.sh"
    echo ""
    echo "🎉 Automation is now running 24/7 in the background!"
else
    echo "❌ Failed to start automation"
    echo "📖 Check logs: cat automation.log"
    exit 1
fi 