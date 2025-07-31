#!/bin/bash

# 🏰⚡ AI EMPIRE MASTER LAUNCHER ⚡🏰
echo "🏰🔥 LAUNCHING THE AI EMPIRE! 🔥🏰"
echo ""

cd "$(dirname "$0")/.."

# Function to start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local script_name=$3
    local port=$4
    
    echo "🚀 Starting $service_name on port $port..."
    
    if [ -d "services/$service_dir" ] && [ -f "services/$service_dir/$script_name" ]; then
        cd "services/$service_dir"
        nohup python3 "$script_name" > "../../logs/${service_name,,}_service.log" 2>&1 &
        local pid=$!
        echo "$pid" > "../../logs/${service_name,,}_service.pid"
        echo "  ✅ $service_name started (PID: $pid)"
        cd - >/dev/null
        sleep 2
    else
        echo "  ❌ $service_name not found"
    fi
}

# Create logs directory
mkdir -p logs

# Stop any existing services
echo "🛑 Stopping existing services..."
./scripts/stop_empire.sh >/dev/null 2>&1

echo ""
echo "🚀 LAUNCHING SERVICES:"
echo "====================="

# Start services in order with delays for proper discovery
start_service "ClutterBot" "clutterbot" "clutterbot_beacon.py" "8000"
start_service "MrLore" "mrlore" "mrlore_beacon.py" "8001"
start_service "ZW Transformer" "zw_transformer" "zw_beacon.py" "8002"
start_service "Council of 5" "council_of_5" "council_beacon.py" "8003"

if [ -d "services/trae_agent" ]; then
    start_service "TRAE Agent" "trae_agent" "trae_beacon.py" "8004"
fi

if [ -d "services/trae_agent" ]; then
    start_service "TRAE Agent" "trae_agent" "trae_beacon.py" "8004"
fi

echo ""
echo "⏳ Waiting for services to discover each other..."
sleep 10

echo ""
echo "🔍 CHECKING SERVICE STATUS:"
echo "=========================="

check_service() {
    local name=$1
    local port=$2
    
    if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
        echo "✅ $name (port $port) - HEALTHY"
    else
        echo "❌ $name (port $port) - NOT RESPONDING"
    fi
}

check_service "ClutterBot" "8000"
check_service "MrLore" "8001"
check_service "ZW Transformer" "8002"
check_service "Council of 5" "8003"
check_service "TRAE Agent" "8004"

echo ""
echo "🎯🔥 AI EMPIRE DEPLOYMENT COMPLETE! 🔥🎯"
echo ""
echo "📊 SERVICE ENDPOINTS:"
echo "===================="
echo "🗂️ ClutterBot:     http://localhost:8000"
echo "📚 MrLore:         http://localhost:8001"
echo "🧠 ZW Transformer: http://localhost:8002"
echo "🏛️ Council of 5:   http://localhost:8003"
echo "⚡ TRAE Agent:     http://localhost:8004"

echo ""
echo "💡 USEFUL COMMANDS:"
echo "=================="
echo "📋 Check status:    ./scripts/status_empire.sh"
echo "🛑 Stop all:        ./scripts/stop_empire.sh"
echo "📄 View logs:       ./scripts/logs_empire.sh"
echo "🧪 Test APIs:       ./scripts/test_empire.sh"

echo ""
echo "🌟 Your AI Empire is now autonomous and collaborative!"
echo "🚀 Services will auto-discover and enhance each other!"
