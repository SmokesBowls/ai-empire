#!/bin/bash

echo "🛑 STOPPING AI EMPIRE..."

# Kill all beacon processes
pkill -f "beacon.py" 2>/dev/null

# Kill specific service PIDs if they exist
cd "$(dirname "$0")/.."
if [ -d "logs" ]; then
    for pidfile in logs/*_service.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            kill "$pid" 2>/dev/null && echo "🛑 Stopped PID $pid"
            rm "$pidfile"
        fi
    done
fi

# Kill anything on our ports
for port in 8000 8001 8002 8003 8004; do
    fuser -k "$port/tcp" 2>/dev/null
done

echo "✅ AI Empire stopped!"
