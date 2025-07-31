#!/usr/bin/env python3
"""
🚀 TRAE Agent Integration Service - Fixed Config Handling
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
                # Load TRAE configuration
                config_path = os.path.join(TRAE_PATH, "trae_config.json")
                self.config = load_config(config_path)
                
                # Initialize TRAE Agent using create_agent pattern
                from trae_agent.cli import create_agent
                self.agent = create_agent(self.config)
                print("✅ TRAE Agent initialized successfully")
                
            except Exception as e:
                print(f"❌ Failed to initialize TRAE Agent: {e}")
                import traceback
                traceback.print_exc()
        
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
                "trae_available": TRAE_AVAILABLE
            })
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Get TRAE service status and configuration"""
            try:
                # Safely get config info
                provider = getattr(self.config, 'default_provider', 'unknown') if self.config else 'unknown'
                
                # Get model info safely
                model = 'unknown'
                if self.config and hasattr(self.config, 'model_providers'):
                    provider_config = getattr(self.config.model_providers, provider, None)
                    if provider_config and hasattr(provider_config, 'model'):
                        model = provider_config.model
                
                max_steps = getattr(self.config, 'max_steps', 20) if self.config else 20
                
                return jsonify({
                    "service": "TRAE Agent Integration",
                    "version": "1.0.0", 
                    "trae_path": TRAE_PATH,
                    "trae_available": TRAE_AVAILABLE,
                    "agent_ready": self.agent is not None,
                    "config": {
                        "provider": provider,
                        "model": model,
                        "max_steps": max_steps
                    },
                    "endpoints": {
                        "health": "GET /health",
                        "status": "GET /status",
                        "cli_execute": "POST /cli_execute",
                        "execute": "POST /execute"
                    }
                })
            except Exception as e:
                return jsonify({
                    "service": "TRAE Agent Integration",
                    "error": str(e),
                    "trae_available": TRAE_AVAILABLE
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
                import traceback
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
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
                
                # Use the TRAE CLI directly
                cmd = [
                    "/home/tran/trae-agent-main/.venv/bin/python", 
                    "-m", "trae_agent.cli", "run", 
                    task,
                    "--working-dir", working_dir
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
                    "working_dir": working_dir,
                    "command": " ".join(cmd)
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
    
    def start(self, host='0.0.0.0', port=8009):
        """Start the TRAE integration service"""
        print(f"""
🚀 TRAE Agent Integration Service Starting...
   
📍 Endpoints:
   • Health: GET  http://{host}:{port}/health
   • Status: GET  http://{host}:{port}/status  
   • SDK:    POST http://{host}:{port}/execute
   • CLI:    POST http://{host}:{port}/cli_execute

🤖 Configuration:
   • TRAE Available: {TRAE_AVAILABLE}
   • Agent Ready: {self.agent is not None}
   • TRAE Path: {TRAE_PATH}
        """)
        
        self.app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    service = TRAEIntegrationService()
    service.start()
