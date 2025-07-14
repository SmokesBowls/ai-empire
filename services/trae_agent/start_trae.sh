#!/bin/bash
echo "🚀 Starting TRAE Agent Service on port 8009..."

# Stop any existing service
if [ -f trae_service.pid ]; then
    kill $(cat trae_service.pid) 2>/dev/null
    rm -f trae_service.pid
fi

# Start with explicit port
nohup /home/tran/trae-agent-main/.venv/bin/python trae_integration.py > ../../logs/trae_service.log 2>&1 &
echo $! > trae_service.pid

echo "✅ TRAE Agent started on port 8009"
echo "📝 Logs: /home/tran/ai_empire_deployable/logs/trae_service.log"
