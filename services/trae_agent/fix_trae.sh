#!/bin/bash
# 🔧 Quick Fix: Deploy the REAL TRAE Integration

echo "🔧 Fixing TRAE Integration..."

# Stop current service
if [ -f trae_service.pid ]; then
    kill $(cat trae_service.pid) 2>/dev/null
    rm -f trae_service.pid
fi

# Create the REAL integration service
cat > trae_integration.py << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
🚀 TRAE Agent Integration Service
Professional AI Empire integration with Ollama support
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify

# Add TRAE to path
TRAE_PATH = "/home/tran/trae-agent-main"
sys.path.insert(0, TRAE_PATH)

# Import TRAE components
try:
    from trae_agent.agent.trae_agent import TraeAgent
    from trae_agent.utils.config import load_config
    TRAE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ TRAE import failed: {e}")
    TRAE_AVAILABLE = False

class TRAEIntegrationService:
    def __init__(self):
        self.agent = None
        self.config = None
        
        if TRAE_AVAILABLE:
            try:
                # Load and configure TRAE
                config_path = os.path.join(TRAE_PATH, "trae_config.json")
                self.config = load_config(config_path)
                
                # Configure Ollama as default provider
                self.config.default_provider = "ollama"
                if "ollama" not in self.config.model_providers:
                    self.config.model_providers["ollama"] = {}
                
                self.config.model_providers["ollama"].update({
                    "api_key": "ollama",
                    "base_url": "http://localhost:11434/v1",
                    "model": "phi3:3.8b",
                    "max_tokens": 4096,
                    "temperature": 0.7
                })
                
                # Initialize TRAE Agent
                self.agent = TraeAgent.from_config(self.config)
                print("✅ TRAE Agent initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize TRAE Agent: {e}")
        
        # Create Flask app
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "service": "TRAE Agent",
                "agent_ready": self.agent is not None,
                "trae_available": TRAE_AVAILABLE,
                "ollama_configured": self.config.default_provider == "ollama" if self.config else False
            })
        
        @self.app.route('/execute', methods=['POST'])
        def execute_task():
            """Execute a TRAE task using SDK"""
            if not self.agent:
                return jsonify({"error": "TRAE Agent not initialized"}), 500
            
            data = request.json or {}
            task = data.get("task", "")
            working_dir = data.get("working_dir", "/tmp/trae_workspace")
            
            if not task:
                return jsonify({"error": "No task provided"}), 400
            
            try:
                # Ensure working directory exists
                Path(working_dir).mkdir(parents=True, exist_ok=True)
                
                # Setup trajectory recording
                trajectory_path = self.agent.setup_trajectory_recording()
                
                # Execute task
                task_args = {
                    "project_path": working_dir,
                    "issue": task,
                    "must_patch": "false"
                }
                
                self.agent.new_task(task, task_args)
                execution = asyncio.run(self.agent.execute_task())
                
                return jsonify({
                    "success": True,
                    "result": execution.final_result if hasattr(execution, 'final_result') else "Task completed",
                    "steps": len(execution.steps) if hasattr(execution, 'steps') else 0,
                    "working_dir": working_dir,
                    "trajectory_file": trajectory_path
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "working_dir": working_dir
                }), 500
        
        @self.app.route('/cli_execute', methods=['POST'])
        def cli_execute():
            """Execute via CLI interface"""
            data = request.json or {}
            task = data.get("task", "")
            working_dir = data.get("working_dir", "/tmp/trae_workspace")
            
            if not task:
                return jsonify({"error": "No task provided"}), 400
            
            try:
                # Ensure working directory exists
                Path(working_dir).mkdir(parents=True, exist_ok=True)
                
                # Change to TRAE directory and run CLI
                cmd = [
                    "python", "-m", "trae_agent.cli", "run", 
                    task,
                    "--working-dir", working_dir,
                    "--provider", "ollama",
                    "--model", "phi3:3.8b"
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    cwd=TRAE_PATH,
                    timeout=300  # 5 minute timeout
                )
                
                return jsonify({
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "return_code": result.returncode,
                    "working_dir": working_dir
                })
                
            except subprocess.TimeoutExpired:
                return jsonify({
                    "success": False,
                    "error": "Task execution timed out (5 minutes)",
                    "working_dir": working_dir
                }), 408
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "working_dir": working_dir
                }), 500
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Get TRAE service status and configuration"""
            return jsonify({
                "service": "TRAE Agent Integration",
                "version": "1.0.0",
                "trae_path": TRAE_PATH,
                "trae_available": TRAE_AVAILABLE,
                "config": {
                    "provider": self.config.default_provider if self.config else "unknown",
                    "model": self.config.model_providers.get(self.config.default_provider, {}).get("model", "unknown") if self.config else "unknown",
                    "max_steps": getattr(self.config, 'max_steps', 20) if self.config else 20
                },
                "endpoints": {
                    "health": "GET /health",
                    "sdk_execute": "POST /execute",
                    "cli_execute": "POST /cli_execute",
                    "status": "GET /status"
                }
            })
    
    def start(self, host='0.0.0.0', port=8004):
        """Start the TRAE integration service"""
        print(f"""
🚀 TRAE Agent Integration Service Starting...
   
📍 Endpoints:
   • Health: GET  http://{host}:{port}/health
   • SDK:    POST http://{host}:{port}/execute
   • CLI:    POST http://{host}:{port}/cli_execute
   • Status: GET  http://{host}:{port}/status

🤖 Configuration:
   • TRAE Available: {TRAE_AVAILABLE}
   • Provider: {self.config.default_provider if self.config else 'unknown'}
   • Model: {self.config.model_providers.get(self.config.default_provider, {}).get('model', 'unknown') if self.config else 'unknown'}
   • TRAE Path: {TRAE_PATH}

🎯 Usage Examples:
   curl -X POST http://{host}:{port}/execute \\
        -H "Content-Type: application/json" \\
        -d '{{"task": "Create a hello world Python script"}}'
        """)
        
        self.app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    service = TRAEIntegrationService()
    service.start()
PYTHON_EOF

# Make executable
chmod +x trae_integration.py

# Update test script with correct endpoints
cat > test_trae.sh << 'TEST_EOF'
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
TEST_EOF

chmod +x test_trae.sh

echo "✅ TRAE Integration fixed!"
echo ""
echo "🚀 Now restart the service:"
echo "   ./start_trae.sh"
echo "   ./test_trae.sh"
