#!/bin/bash
echo "🛑 Stopping TRAE Agent Service..."

if [ -f trae_service.pid ]; then
    PID=$(cat trae_service.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "✅ TRAE Agent stopped (PID: $PID)"
    else
        echo "⚠️ TRAE Agent not running"
    fi
    rm -f trae_service.pid
else
    echo "⚠️ No PID file found"
fi
