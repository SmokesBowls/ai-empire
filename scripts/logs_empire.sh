#!/bin/bash

cd "$(dirname "$0")/.."

if [ $# -eq 0 ]; then
    echo "📄 Available service logs:"
    ls logs/*_service.log 2>/dev/null | sed 's/logs\///g' | sed 's/_service.log//g' | sed 's/^/   • /'
    echo ""
    echo "💡 Usage: $0 [service_name]"
    echo "💡 Example: $0 mrlore"
    echo "💡 Or view all: $0 all"
else
    if [ "$1" = "all" ]; then
        echo "📄 ALL SERVICE LOGS:"
        echo "==================="
        for log in logs/*_service.log; do
            if [ -f "$log" ]; then
                echo ""
                echo "🔍 $(basename "$log" .log | tr '[:lower:]' '[:upper:]'):"
                echo "----------------------------------------"
                tail -n 20 "$log"
            fi
        done
    else
        log_file="logs/${1}_service.log"
        if [ -f "$log_file" ]; then
            echo "📄 $1 SERVICE LOG:"
            echo "=================="
            tail -f "$log_file"
        else
            echo "❌ Log file not found: $log_file"
        fi
    fi
fi
