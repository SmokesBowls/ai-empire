#!/bin/bash

echo "🧪 TESTING AI EMPIRE COLLABORATION:"
echo "==================================="

echo ""
echo "📡 Testing MrLore analysis..."
curl -s -X POST "http://localhost:8001/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "Test narrative analysis"}' | python3 -m json.tool

echo ""
echo "📡 Testing ZW Transformer generation..."
curl -s -X POST "http://localhost:8002/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Create a mystical forest", "context": "fantasy game"}' | python3 -m json.tool

echo ""
echo "📡 Testing Council deliberation..."
curl -s -X POST "http://localhost:8003/deliberate" \
     -H "Content-Type: application/json" \
     -d '{"problem": "Design the perfect game level"}' | python3 -m json.tool

echo ""
echo "📡 Testing ClutterBot organization..."
curl -s -X POST "http://localhost:8000/organize" \
     -H "Content-Type: application/json" \
     -d '{"directory": "/test", "theme": "game_assets"}' | python3 -m json.tool

echo ""
echo "✅ Empire collaboration tests complete!"

echo ""
echo "📡 Testing TRAE Agent code generation (Ollama)..."
curl -s -X POST "http://localhost:8004/code_generation" \
     -H "Content-Type: application/json" \
     -d '{"requirements": "Create a simple calculator function", "language": "python", "model": "phi3:3.8b"}' | python3 -m json.tool 2>/dev/null || echo "❌ TRAE Agent not responding"

echo ""
echo "📡 Testing TRAE Agent task execution (Ollama)..."
curl -s -X POST "http://localhost:8004/run_task" \
     -H "Content-Type: application/json" \
     -d '{"task": "Create a hello world script", "model": "phi3:3.8b", "use_ai_enhancement": true}' | python3 -m json.tool 2>/dev/null || echo "❌ TRAE Agent not responding"

echo ""
echo "📡 Testing TRAE Agent AI-enhanced action..."
curl -s -X POST "http://localhost:8004/ai_action" \
     -H "Content-Type: application/json" \
     -d '{"request": "Generate GDScript for a 3D game character controller"}' | python3 -m json.tool 2>/dev/null || echo "❌ TRAE Agent not responding"
