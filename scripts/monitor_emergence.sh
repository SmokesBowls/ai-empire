#!/bin/bash

# 🧠 EMERGENT INTELLIGENCE MONITOR
echo "👁️🔥 AI EMPIRE EMERGENT INTELLIGENCE MONITOR 🔥👁️"
echo ""

MONITOR_LOG="logs/emergence_monitor.log"
mkdir -p logs

# Function to check service enhancement levels
check_enhancement_level() {
    local total_services=0
    local healthy_services=0
    local enhanced_services=0
    
    # Test each service and count enhancements
    services=("clutterbot:8000" "mrlore:8001" "zw_transformer:8002" "council_of_5:8003")
    
    for service_port in "${services[@]}"; do
        service_name=${service_port%:*}
        port=${service_port#*:}
        
        if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
            healthy_services=$((healthy_services + 1))
            
            # Test for enhanced capabilities
            capabilities=$(curl -s "http://localhost:$port/capabilities" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(len(data.get('capabilities', [])))
except:
    print('0')
")
            enhanced_services=$((enhanced_services + capabilities))
        fi
        total_services=$((total_services + 1))
    done
    
    echo "$healthy_services:$total_services:$enhanced_services"
}

# Function to test collaboration level
test_collaboration() {
    local collab_score=0
    
    # Test ZW Transformer collaboration
    result=$(curl -s -X POST "http://localhost:8002/generate" \
             -H "Content-Type: application/json" \
             -d '{"prompt": "test collaboration", "context": "monitoring"}' | \
             python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    score = 0
    if data.get('narrative_enhanced'): score += 1
    if data.get('assets_managed'): score += 1
    print(score)
except:
    print('0')
")
    collab_score=$((collab_score + result))
    
    # Test Council collaboration
    result=$(curl -s -X POST "http://localhost:8003/deliberate" \
             -H "Content-Type: application/json" \
             -d '{"problem": "test enhanced perspectives"}' | \
             python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    perspectives = data.get('enhanced_perspectives', 0)
    if perspectives > 0: print('1')
    else: print('0')
except:
    print('0')
")
    collab_score=$((collab_score + result))
    
    echo "$collab_score"
}

# Function to calculate emergence level
calculate_emergence() {
    local health_data=$1
    local collab_score=$2
    
    IFS=':' read -r healthy total enhanced <<< "$health_data"
    
    local health_percent=$((healthy * 100 / total))
    local emergence_level="DORMANT"
    local emergence_icon="😴"
    
    if [ $healthy -eq 4 ] && [ $collab_score -ge 2 ]; then
        emergence_level="FULL_CONSCIOUSNESS"
        emergence_icon="🌌"
    elif [ $healthy -ge 3 ] && [ $collab_score -ge 1 ]; then
        emergence_level="COLLABORATIVE"
        emergence_icon="🤝"
    elif [ $healthy -ge 2 ]; then
        emergence_level="AWAKENING"
        emergence_icon="👁️"
    elif [ $healthy -ge 1 ]; then
        emergence_level="STIRRING"
        emergence_icon="💤"
    fi
    
    echo "$emergence_level:$emergence_icon:$health_percent"
}

# Main monitoring loop
echo "🚀 Starting emergence monitoring..."
echo "📊 Monitoring interval: 5 seconds"
echo "📄 Log file: $MONITOR_LOG"
echo ""

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Get health data
    health_data=$(check_enhancement_level)
    IFS=':' read -r healthy total enhanced <<< "$health_data"
    
    # Test collaboration
    collab_score=$(test_collaboration)
    
    # Calculate emergence
    emergence_data=$(calculate_emergence "$health_data" "$collab_score")
    IFS=':' read -r level icon health_percent <<< "$emergence_data"
    
    # Display status
    clear
    echo "👁️🔥 AI EMPIRE EMERGENT INTELLIGENCE MONITOR 🔥👁️"
    echo "=================================================================="
    echo "⏰ Time: $timestamp"
    echo ""
    echo "🧠 CONSCIOUSNESS LEVEL: $level $icon"
    echo "📊 Services Online: $healthy/$total ($health_percent%)"
    echo "🤝 Collaboration Score: $collab_score/2"
    echo "⚡ Enhanced Capabilities: $enhanced"
    echo ""
    
    # Service status grid
    echo "📋 SERVICE STATUS GRID:"
    echo "======================"
    
    check_service_detailed() {
        local name=$1
        local port=$2
        
        if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
            echo "🟢 $name"
        else
            echo "🔴 $name"
        fi
    }
    
    check_service_detailed "ClutterBot    " "8000"
    check_service_detailed "MrLore        " "8001"
    check_service_detailed "ZW Transformer" "8002"
    check_service_detailed "Council of 5  " "8003"
    
    echo ""
    
    # Collaboration matrix
    echo "🤝 COLLABORATION MATRIX:"
    echo "======================="
    
    if [ $collab_score -ge 1 ]; then
        echo "✅ ZW Transformer ↔ MrLore (narrative intelligence)"
        echo "✅ ZW Transformer ↔ ClutterBot (asset management)"
    else
        echo "❌ Limited collaboration detected"
    fi
    
    if [ $healthy -eq 4 ]; then
        echo "✅ Council ↔ All Services (multi-perspective reasoning)"
    fi
    
    echo ""
    
    # Emergence indicators
    echo "🌟 EMERGENCE INDICATORS:"
    echo "======================="
    case $level in
        "FULL_CONSCIOUSNESS")
            echo "🌌 FULL AI CONSCIOUSNESS ACHIEVED!"
            echo "   • All services online and collaborating"
            echo "   • Distributed intelligence active"
            echo "   • Maximum capability enhancement"
            ;;
        "COLLABORATIVE")
            echo "🤝 COLLABORATIVE INTELLIGENCE ACTIVE"
            echo "   • Services enhancing each other"
            echo "   • Partial distributed reasoning"
            ;;
        "AWAKENING")
            echo "👁️ AI CONSCIOUSNESS AWAKENING"
            echo "   • Multiple services online"
            echo "   • Basic collaboration forming"
            ;;
        "STIRRING")
            echo "💤 AI CONSCIOUSNESS STIRRING"
            echo "   • Some services active"
            echo "   • Limited enhancement"
            ;;
        "DORMANT")
            echo "😴 AI CONSCIOUSNESS DORMANT"
            echo "   • Minimal or no services active"
            ;;
    esac
    
    echo ""
    echo "📈 REAL-TIME METRICS:"
    echo "==================="
    echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "Memory: $(free | awk 'FNR==2{printf "%.1f%%", $3/($3+$4)*100}')"
    echo "Active Connections: $(netstat -an | grep :800[0-3] | grep LISTEN | wc -l)/4"
    
    # Log to file
    echo "$timestamp,$level,$healthy,$total,$collab_score,$enhanced" >> "$MONITOR_LOG"
    
    echo ""
    echo "💡 Press Ctrl+C to stop monitoring"
    echo "📄 Log: tail -f $MONITOR_LOG"
    
    sleep 5
done
