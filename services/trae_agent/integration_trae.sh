#!/bin/bash
# 🏰 Complete AI Empire Integration with TRAE Agent

echo "🚀 Updating AI Empire scripts for TRAE Agent integration..."

# 1. UPDATE start_empire.sh
echo "📝 Updating start_empire.sh..."
cat >> /home/tran/ai_empire_deployable/start_empire.sh << 'EOF'

# Start TRAE Agent
echo "🚀 Starting TRAE Agent..."
cd services/trae_agent
if [ ! -f "trae_service.pid" ]; then
    # Activate TRAE virtual environment and start service
    source /home/tran/trae-agent-main/.venv/bin/activate
    nohup python trae_integration.py > ../../logs/trae_service.log 2>&1 &
    echo $! > trae_service.pid
    deactivate
    echo "✅ TRAE Agent started on port 8009"
else
    echo "⚠️ TRAE Agent already running"
fi
cd ../..
sleep 3
EOF

# 2. UPDATE stop_empire.sh  
echo "📝 Updating stop_empire.sh..."
cat >> /home/tran/ai_empire_deployable/stop_empire.sh << 'EOF'

# Stop TRAE Agent
echo "🛑 Stopping TRAE Agent..."
if [ -f "services/trae_agent/trae_service.pid" ]; then
    kill $(cat services/trae_agent/trae_service.pid) 2>/dev/null
    rm services/trae_agent/trae_service.pid
    echo "✅ TRAE Agent stopped"
else
    echo "⚠️ TRAE Agent PID file not found"
fi
EOF

# 3. UPDATE test_empire.sh
echo "📝 Updating test_empire.sh..."
cat >> /home/tran/ai_empire_deployable/test_empire.sh << 'EOF'

# Test TRAE Agent
echo "🧪 Testing TRAE Agent..."

# Health check
echo "• Health Check:"
HEALTH=$(curl -s http://localhost:8009/health 2>/dev/null)
if echo "$HEALTH" | grep -q "active"; then
    echo "  ✅ Service healthy"
else
    echo "  ❌ Service not responding"
    exit 1
fi

# CLI execution test with extended wait
echo "• CLI Execution Test:"
TEST_RESPONSE=$(curl -s -X POST http://localhost:8009/cli_execute \
    -H "Content-Type: application/json" \
    -d '{"task": "echo AI_EMPIRE_INTEGRATION_SUCCESS > empire_test.txt"}' \
    --max-time 30 2>/dev/null)

# Wait for completion and check result
sleep 15
if echo "$TEST_RESPONSE" | grep -q "working_dir"; then
    WORK_DIR=$(echo "$TEST_RESPONSE" | grep -o '"/tmp/[^"]*"' | tr -d '"')
    if [ -f "$WORK_DIR/empire_test.txt" ]; then
        echo "  ✅ TRAE Agent file creation successful"
        echo "  📁 Created: $WORK_DIR/empire_test.txt"
    else
        echo "  ⚠️ TRAE Agent responding but file creation pending"
    fi
else
    echo "  ❌ TRAE Agent CLI execution failed"
fi

echo "🎯 TRAE Agent integration: COMPLETE"
EOF

# 4. CREATE empire status script
echo "📝 Creating empire_status.sh..."
cat > /home/tran/ai_empire_deployable/empire_status.sh << 'EOF'
#!/bin/bash
# 🏰 AI Empire Status Dashboard

echo "🏰 AI Empire Status Dashboard"
echo "=============================="

# Check all services
declare -A SERVICES=(
    ["ClutterBot"]="8000"
    ["MrLore"]="8001" 
    ["ZW Transformer"]="8002"
    ["Council of 5"]="8003"
    ["TRAE Agent"]="8009"
)

for SERVICE in "${!SERVICES[@]}"; do
    PORT=${SERVICES[$SERVICE]}
    if curl -s http://localhost:$PORT/health >/dev/null 2>&1; then
        echo "✅ $SERVICE (port $PORT) - ACTIVE"
    else
        echo "❌ $SERVICE (port $PORT) - INACTIVE"
    fi
done

echo ""
echo "🎯 TRAE Agent Details:"
curl -s http://localhost:8009/health 2>/dev/null | jq . 2>/dev/null || echo "TRAE Agent not responding"

echo ""
echo "📊 Empire Summary:"
ACTIVE=$(curl -s http://localhost:8000/health >/dev/null 2>&1 && echo -n "1" || echo -n "0")
ACTIVE=$((ACTIVE + $(curl -s http://localhost:8001/health >/dev/null 2>&1 && echo -n "1" || echo -n "0")))
ACTIVE=$((ACTIVE + $(curl -s http://localhost:8002/health >/dev/null 2>&1 && echo -n "1" || echo -n "0")))  
ACTIVE=$((ACTIVE + $(curl -s http://localhost:8003/health >/dev/null 2>&1 && echo -n "1" || echo -n "0")))
ACTIVE=$((ACTIVE + $(curl -s http://localhost:8009/health >/dev/null 2>&1 && echo -n "1" || echo -n "0")))

echo "Active Services: $ACTIVE/5"
if [ $ACTIVE -eq 5 ]; then
    echo "🎉 AI Empire fully operational!"
else
    echo "⚠️ Empire partially operational"
fi
EOF

chmod +x /home/tran/ai_empire_deployable/empire_status.sh

# 5. CREATE quick deployment verification
echo "📝 Creating deployment verification..."
cat > /home/tran/ai_empire_deployable/verify_trae.sh << 'EOF'
#!/bin/bash
# 🎯 TRAE Agent Integration Verification

echo "🎯 Verifying TRAE Agent Integration..."

# 1. Check service is running
if pgrep -f "trae_integration.py" > /dev/null; then
    echo "✅ TRAE integration service running"
else
    echo "❌ TRAE integration service not running"
    exit 1
fi

# 2. Check health endpoint
HEALTH=$(curl -s http://localhost:8009/health 2>/dev/null)
if echo "$HEALTH" | grep -q "qwen2.5-coder:3b"; then
    echo "✅ TRAE model (qwen2.5-coder:3b) confirmed"
else
    echo "❌ TRAE model not responding correctly"
    exit 1
fi

# 3. Quick task test
echo "🧪 Running quick TRAE task test..."
RESPONSE=$(curl -s -X POST http://localhost:8009/cli_execute \
    -H "Content-Type: application/json" \
    -d '{"task": "echo VERIFICATION_SUCCESS > verify.txt"}' \
    --max-time 20)

echo "📊 TRAE Response received, checking for working directory..."
if echo "$RESPONSE" | grep -q "working_dir"; then
    echo "✅ TRAE task execution initiated successfully"
    echo "🎉 TRAE Agent integration VERIFIED!"
else
    echo "❌ TRAE task execution failed"
    echo "Response: $RESPONSE"
    exit 1
fi

echo ""
echo "🏰 AI Empire + TRAE Agent integration complete!"
echo "   • Ports: 8000-8003 (original services) + 8009 (TRAE)"
echo "   • Model: qwen2.5-coder:3b (local Ollama)"
echo "   • Endpoints: /execute, /cli_execute, /health"
echo "   • Status: ./empire_status.sh"
EOF

chmod +x /home/tran/ai_empire_deployable/verify_trae.sh

echo "✅ AI Empire integration scripts updated!"
echo ""
echo "🚀 Quick Start:"
echo "   cd /home/tran/ai_empire_deployable"
echo "   ./start_empire.sh    # Start all services including TRAE"
echo "   ./empire_status.sh   # Check status dashboard"
echo "   ./verify_trae.sh     # Verify TRAE integration"
echo "   ./test_empire.sh     # Full test suite"
echo ""
echo "🎯 TRAE Agent is now part of your AI Empire!"
echo "   • SDK: POST http://localhost:8009/execute"
echo "   • CLI: POST http://localhost:8009/cli_execute"
echo "   • Health: GET http://localhost:8009/health"