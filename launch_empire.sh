#!/bin/bash

echo "🏰🚀 AI EMPIRE LAUNCHER 🚀🏰"
echo ""

# Check for Docker first
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected - launching containerized empire..."
    
    # Check for docker-compose.yml in root or docker/ directory
    if [ -f "docker-compose.yml" ]; then
        docker-compose up --build
    elif [ -f "docker/docker-compose.yml" ]; then
        echo "📁 Using docker-compose.yml from docker/ directory..."
        # Change directory but come back after
        (cd docker && docker-compose up --build)
    elif [ -f "Dockerfile" ]; then
        echo "🏗️ Building from Dockerfile..."
        docker build -t ai-empire . && docker run -p 8000-8009:8000-8009 ai-empire
    elif [ -f "docker/Dockerfile" ]; then
        echo "🏗️ Building from docker/Dockerfile..."
        docker build -f docker/Dockerfile -t ai-empire . && docker run -p 8000-8009:8000-8009 ai-empire
    else
        echo "⚠️  No Docker configuration found, falling back to Python..."
        ./scripts/start_empire.sh
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
