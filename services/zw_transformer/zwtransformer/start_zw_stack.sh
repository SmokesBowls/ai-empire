#!/bin/bash

# ZW Transformer Complete Stack Startup Script
# Starts all services needed for the full ZW ecosystem

echo "🚀 Starting ZW Transformer Complete Stack..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running in correct directory
if [ ! -f "zw_transformer_daemon.py" ]; then
    echo -e "${RED}❌ Error: Run this script from the zwtransformer directory${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service to start
wait_for_service() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    echo -e "${YELLOW}⏳ Waiting for ${name} on port ${port}...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if check_port $port; then
            echo -e "${GREEN}✅ ${name} is ready on port ${port}${NC}"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ ${name} failed to start on port ${port}${NC}"
    return 1
}

# Function to kill process on port
kill_port() {
    local port=$1
    local name=$2
    
    if check_port $port; then
        echo -e "${YELLOW}🔫 Killing existing service on port ${port} (${name})...${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null
        sleep 1
        
        # Double check
        if check_port $port; then
            echo -e "${RED}❌ Failed to free port ${port}${NC}"
            return 1
        else
            echo -e "${GREEN}✅ Port ${port} freed${NC}"
        fi
    fi
    return 0
}

# Kill existing services by port (but skip Ollama - it should stay running)
echo -e "${BLUE}🧹 Cleaning up existing services...${NC}"
kill_port 1111 "ZW Daemon"
kill_port 5173 "React Frontend" 
kill_port 8000 "XTTS Voice"
# Note: Skip killing Ollama port 11434 - it should remain as system service

# Additional process cleanup (but not Ollama)
pkill -f "zw_transformer_daemon" 2>/dev/null
pkill -f "npm.*dev" 2>/dev/null
pkill -f "xtts_api_server" 2>/dev/null
sleep 2

# 1. Check Ollama (use existing instance if running)
echo -e "${BLUE}1️⃣ Checking for Ollama: Hold my beer, I got this...${NC}"

# More reliable Ollama detection
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${GREEN}🍺 ✅ Ollama already running and responding on port 11434 - told you I got this!${NC}"
    OLLAMA_RUNNING=true
elif lsof -i :11434 >/dev/null 2>&1; then
    echo -e "${YELLOW}🍺 ⚠️ Port 11434 occupied but Ollama API not responding - give it a sec...${NC}"
    echo -e "${YELLOW}⚠️ Assuming Ollama is starting up or needs a moment...${NC}"
    OLLAMA_RUNNING=true
else
    echo -e "${YELLOW}🍺 ⚡ No Ollama found - time to fire one up myself...${NC}"
    ollama serve &
    OLLAMA_PID=$!
    wait_for_service 11434 "Ollama"
    OLLAMA_RUNNING=true
fi

# 2. Start XTTS Voice Service (if available)
echo -e "${BLUE}2️⃣ Starting XTTS Voice Service...${NC}"
if [ -d "$(dirname $(which python))/../../xtts-api-server" ] || command -v xtts-api-server &> /dev/null; then
    # Start XTTS in background
    cd ~/xtts-api-server 2>/dev/null || echo "XTTS path may need adjustment"
    python -m xtts_api_server --port 8000 &
    XTTS_PID=$!
    cd - >/dev/null
    wait_for_service 8000 "XTTS Voice Service"
else
    echo -e "${YELLOW}⚠️ XTTS not found, voice synthesis will be unavailable${NC}"
fi

# 3. Start ZW Transformer Daemon
echo -e "${BLUE}3️⃣ Starting ZW Transformer Daemon...${NC}"
# Activate virtual environment if it exists
if [ -d "tenlabs-env" ]; then
    source tenlabs-env/bin/activate
fi

python3 zw_transformer_daemon.py &
DAEMON_PID=$!
wait_for_service 1111 "ZW Transformer Daemon"

# 4. Start React Frontend (if package.json exists)
echo -e "${BLUE}4️⃣ Starting React Frontend...${NC}"
if [ -f "package.json" ]; then
    npm run dev &
    FRONTEND_PID=$!
    wait_for_service 5173 "React Frontend"
elif [ -f "frontend/package.json" ]; then
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    wait_for_service 5173 "React Frontend"
else
    echo -e "${YELLOW}⚠️ React frontend not found${NC}"
fi

# Summary
echo -e "\n${GREEN}🎉 ZW Transformer Stack Status:${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Ollama with direct API test
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama Service:          http://localhost:11434${NC}"
elif [ "$OLLAMA_RUNNING" = true ]; then
    echo -e "${YELLOW}⚠️ Ollama Service: Running but API slow to respond${NC}"
else
    echo -e "${RED}❌ Ollama Service: FAILED${NC}"
fi

check_port 8000 && echo -e "${GREEN}✅ Voice Synthesis:         http://localhost:8000${NC}" || echo -e "${YELLOW}⚠️ Voice Synthesis: Not Available${NC}"
check_port 1111 && echo -e "${GREEN}✅ ZW Transformer Daemon:   http://localhost:1111${NC}" || echo -e "${RED}❌ ZW Transformer Daemon: FAILED${NC}"
check_port 5173 && echo -e "${GREEN}✅ React Frontend:          http://localhost:5173${NC}" || echo -e "${YELLOW}⚠️ React Frontend: Not Available${NC}"

echo -e "\n${BLUE}📋 Quick Commands:${NC}"
echo -e "Test ZW Generation:    curl -X POST http://localhost:1111/ollama/generate -H 'Content-Type: application/json' -d '{\"scenario\":\"test\",\"model\":\"dolphin-mistral:latest\"}'"
echo -e "Test Voice Synthesis:  curl -X POST http://localhost:8000/generate -H 'Content-Type: application/json' -d '{\"text\":\"Hello ZW Transformer\"}'"
echo -e "Open Web Interface:    http://localhost:5173"

echo -e "\n${YELLOW}💡 Press Ctrl+C to stop all services${NC}"

# Create cleanup trap
cleanup() {
    echo -e "\n${BLUE}🛑 Shutting down ZW Transformer Stack...${NC}"
    
    # Kill services by PID first (but preserve existing Ollama)
    [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
    [ ! -z "$DAEMON_PID" ] && kill $DAEMON_PID 2>/dev/null
    [ ! -z "$XTTS_PID" ] && kill $XTTS_PID 2>/dev/null
    # Only kill Ollama if we started it (has PID)
    [ ! -z "$OLLAMA_PID" ] && kill $OLLAMA_PID 2>/dev/null
    
    sleep 2
    
    # Force cleanup by port (but leave Ollama running if it was pre-existing)
    kill_port 5173 "React Frontend" >/dev/null 2>&1
    kill_port 1111 "ZW Daemon" >/dev/null 2>&1
    kill_port 8000 "XTTS Voice" >/dev/null 2>&1
    # Note: Don't kill port 11434 unless we started Ollama ourselves
    
    # Final process cleanup (but preserve system Ollama)
    pkill -f "zw_transformer_daemon" 2>/dev/null
    pkill -f "npm.*dev" 2>/dev/null
    pkill -f "xtts_api_server" 2>/dev/null
    
    echo -e "${GREEN}✅ ZW services stopped (Ollama preserved)${NC}"
    exit 0
}

trap cleanup SIGINT

# Keep script running
wait
