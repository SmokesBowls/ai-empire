#!/bin/bash

echo "📊 AI EMPIRE STATUS:"
echo "==================="

check_service() {
    local name=$1
    local port=$2
    
    if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
        echo "🟢 $name (port $port) - HEALTHY"
        
        # Get capabilities
        echo "   📋 Capabilities:"
        curl -s "http://localhost:$port/capabilities" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for cap in data.get('capabilities', []):
        print(f'      • {cap[\"name\"]}: {cap[\"description\"]}')
except:
    pass
"
    else
        echo "🔴 $name (port $port) - NOT RESPONDING"
    fi
    echo ""
}

check_service "ClutterBot" "8000"
check_service "MrLore" "8001"
check_service "ZW Transformer" "8002"
check_service "Council of 5" "8003"
check_service "TRAE Agent" "8004"

echo "💡 Use './scripts/logs_empire.sh [service]' to view logs"
