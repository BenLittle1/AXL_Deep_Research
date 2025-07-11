#!/bin/bash

# AXL Background Automation Status Checker

echo "📊 AXL Automated Report Generator Status"
echo "=" * 50

# Check if automation is running
if pgrep -f "automated_processor.py" > /dev/null; then
    echo "✅ Status: RUNNING"
    echo ""
    echo "📊 Process Information:"
    ps aux | grep automated_processor.py | grep -v grep | while read line; do
        echo "   $line"
    done
    
    PID=$(pgrep -f "automated_processor.py")
    echo ""
    echo "📋 Details:"
    echo "   🆔 Process ID: $PID"
    echo "   ⏰ Started: $(ps -o lstart= -p $PID 2>/dev/null || echo 'Unknown')"
    echo "   💾 Memory: $(ps -o rss= -p $PID 2>/dev/null | awk '{print $1/1024 " MB"}' || echo 'Unknown')"
    
    # Check log file
    if [ -f "backend/automation.log" ]; then
        echo ""
        echo "📖 Recent Log Activity (last 10 lines):"
        echo "   📁 Log file: backend/automation.log"
        tail -10 backend/automation.log | sed 's/^/   /'
    else
        echo ""
        echo "⚠️  Log file not found: backend/automation.log"
    fi
    
    echo ""
    echo "🔧 Management Commands:"
    echo "   📖 View live logs: tail -f backend/automation.log"
    echo "   🛑 Stop:          ./stop_background.sh"
    echo "   🔄 Restart:       ./stop_background.sh && ./start_background.sh"
    
else
    echo "❌ Status: NOT RUNNING"
    echo ""
    echo "🔧 To start: ./start_background.sh"
    
    # Check if log file exists for debugging
    if [ -f "backend/automation.log" ]; then
        echo ""
        echo "📖 Last log entries (may show why it stopped):"
        tail -5 backend/automation.log | sed 's/^/   /'
    fi
fi

echo ""
echo "📈 Quick Stats:"
if [ -f "backend/automation.log" ]; then
    processed_count=$(grep -c "✅.*processed.*successfully" backend/automation.log 2>/dev/null || echo "0")
    error_count=$(grep -c "❌.*error\|❌.*failed" backend/automation.log 2>/dev/null || echo "0")
    echo "   📊 Companies Processed: $processed_count"
    echo "   ❌ Errors: $error_count"
    echo "   📂 Log Size: $(wc -l < backend/automation.log 2>/dev/null || echo "0") lines"
else
    echo "   📂 No log file found"
fi 