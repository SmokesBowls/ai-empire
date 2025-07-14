#!/bin/bash
echo "🧪 Testing TRAE Agent Service..."

# Test health endpoint
echo "1. Health Check:"
curl -s http://localhost:8004/health | jq .

echo -e "\n2. Status Check:"
curl -s http://localhost:8004/status | jq .

echo -e "\n3. Simple Task Test (CLI):"
curl -X POST http://localhost:8004/cli_execute \
     -H "Content-Type: application/json" \
     -d '{"task": "Create a simple hello world Python script", "working_dir": "/tmp/trae_test"}' | jq .

echo -e "\n✅ TRAE Agent tests complete"
