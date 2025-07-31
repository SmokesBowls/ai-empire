#!/bin/bash

echo "🏰🚀 AI EMPIRE LAUNCHER 🚀🏰"
echo ""

# Check for Docker first
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected - launching containerized empire..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose up --build
    else
        echo "⚠️  No docker-compose.yml found, trying alternative..."
        docker build -t ai-empire . && docker run -p 8000-8009:8000-8009 ai-empire
    fi
elif command -v python3 &> /dev/null; then
    echo "🐍 Python detected - launching native empire..."
    ./scripts/start_empire.sh
else
    echo "❌ Neither Docker nor Python 3 found!"
    echo "Please install one of the following:"
    echo "  - Docker & Docker Compose (recommended)"
    echo "  - Python 3.8+ with pip"
    exit 1
fi
