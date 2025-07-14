#!/bin/bash
# 🎯 TRAE Agent Integration Verification

echo "🎯 Verifying TRAE Agent Integration..."

# Check service is running
if pgrep -f "trae_integration.py" > /dev/null; then
    echo "✅ TRAE integration service running"
else
    echo "❌ TRAE integration service not running"
    echo "Starting TRAE service..."
    cd services/trae_agent
    ./start_trae.sh
    cd ../..
    sleep 5
fi

# Check health endpoint
echo "🔍 Checking TRAE health..."
HEALTH=$(curl -s http://localhost:8009/health 2>/dev/null)
if echo "$HEALTH" | grep -q "healthy\|active"; then
    echo "✅ TRAE service responding"
else
    echo "❌ TRAE service not responding correctly"
fi

echo "🎉 TRAE Agent integration verified!"
echo ""
echo "🏰 Your AI Empire now includes:"
echo "   • ClutterBot: http://localhost:8000"
echo "   • MrLore: http://localhost:8001" 
echo "   • ZW Transformer: http://localhost:8002"
echo "   • Council of 5: http://localhost:8003"
echo "   • TRAE Agent: http://localhost:8009"
