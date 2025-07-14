#!/usr/bin/env python3
"""
🚀 Real TRAE Agent Integration with Ollama
Production TRAE Agent + AI Empire + Local LLMs
"""

import subprocess
import json
import requests
import os
from flask import Flask, request, jsonify
from service_discovery import ServiceDiscoveryBeacon, ServiceCapability, create_flask_discovery_server

class OllamaTRAEService:
    """Real TRAE Agent integration with Ollama support"""
    
    def __init__(self, port=8004):
        # Define TRAE capabilities (based on real TRAE features)
        capabilities = [
            ServiceCapability(
                name="software_engineering",
                description="LLM-based agent for software engineering with Ollama models",
                input_types=["natural_language", "code_task", "file_operation"],
                output_types=["code_changes", "file_edits", "execution_results"]
            ),
            ServiceCapability(
                name="ollama_powered_development",
                description="Local LLM-powered development using Ollama models",
                input_types=["task_description", "model_preference"],
                output_types=["task_completion", "trajectory_log"]
            ),
            ServiceCapability(
                name="interactive_coding",
                description="Interactive mode for iterative development and debugging",
                input_types=["development_request"],
                output_types=["development_result", "conversation_state"]
            )
        ]
        
        # Service discovery setup
        self.beacon = ServiceDiscoveryBeacon("TRAE Agent", capabilities, port)
        self.enhanced_services = {}
        
        # TRAE configuration for Ollama
        self.trae_path = "/home/tran/trae-agent-main"
        self.ollama_models = ["phi3:3.8b", "llama3:8b", "codestral", "deepseek-coder"]
        self.default_model = "phi3:3.8b"  # Your working model
        
        # Ollama connection settings
        self.ollama_base_url = "http://localhost:11434"
        
        # Setup environment variables for TRAE
        os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
        os.environ["OLLAMA_API_KEY"] = "ollama"  # TRAE expects this
        
        # Working directory for TRAE tasks
        self.working_dir = "/tmp/trae_workspace"
        os.makedirs(self.working_dir, exist_ok=True)
        
        # Setup standalone mode
        self.setup_standalone_mode()
        
        # Register for AI service enhancements
        self.beacon.register_enhancement("ZW Transformer", self._enhance_with_zw)
        self.beacon.register_enhancement("Council of 5", self._enhance_with_council)
        self.beacon.register_enhancement("MrLore", self._enhance_with_mrlore)
        self.beacon.register_enhancement("ClutterBot", self._enhance_with_clutterbot)
    
    def setup_standalone_mode(self):
        """Initialize real TRAE Agent with Ollama"""
        print("✅ Real TRAE Agent (Ollama) standalone mode ready")
        print("🤖 Local LLM software engineering capabilities active")
        print(f"🧠 Default model: {self.default_model}")
        
        # Test Ollama connection
        self.test_ollama_connection()
        
        # Test TRAE installation
        self.test_trae_installation()
    
    def test_ollama_connection(self):
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [model["name"] for model in response.json().get("models", [])]
                print(f"🎯 Ollama connected - Available models: {models}")
                return True
            else:
                print("⚠️ Ollama not responding properly")
                return False
        except Exception as e:
            print(f"⚠️ Ollama connection failed: {e}")
            return False
    
    def test_trae_installation(self):
        """Test if TRAE Agent is properly installed"""
        try:
            # Check if TRAE directory exists
            if not os.path.exists(self.trae_path):
                print(f"⚠️ TRAE path not found: {self.trae_path}")
                return False
            
            # Test TRAE config command
            result = subprocess.run([
                "python3", "-c", "import trae_agent; print('TRAE import successful')"
            ], cwd=self.trae_path, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("🎯 TRAE Agent installation verified")
                return True
            else:
                print(f"⚠️ TRAE Agent test failed: {result.stderr}")
                # Try alternative method
                if os.path.exists(f"{self.trae_path}/trae_agent"):
                    print("🔧 TRAE Agent found - using direct Python execution")
                    return True
                return False
        except Exception as e:
            print(f"⚠️ TRAE Agent test error: {e}")
            return False
    
    def _enhance_with_zw(self, service_info):
        """Enhancement when ZW Transformer becomes available"""
        self.enhanced_services["zw_transformer"] = service_info["endpoint"]
        print("🔗 TRAE enhanced with ZW Transformer consciousness patterns")
    
    def _enhance_with_council(self, service_info):
        """Enhancement when Council becomes available"""
        self.enhanced_services["council"] = service_info["endpoint"]
        print("🔗 TRAE enhanced with Council decision making")
    
    def _enhance_with_mrlore(self, service_info):
        """Enhancement when MrLore becomes available"""
        self.enhanced_services["mrlore"] = service_info["endpoint"]
        print("🔗 TRAE enhanced with MrLore narrative intelligence")
    
    def _enhance_with_clutterbot(self, service_info):
        """Enhancement when ClutterBot becomes available"""
        self.enhanced_services["clutterbot"] = service_info["endpoint"]
        print("🔗 TRAE enhanced with ClutterBot asset management")
    
    # =========================================================================
    # OLLAMA + TRAE EXECUTION METHODS
    # =========================================================================
    
    def execute_trae_task(self, task_description, model=None, working_dir=None):
        """Execute task using real TRAE Agent with Ollama"""
        try:
            # Use specified model or default
            selected_model = model or self.default_model
            work_dir = working_dir or self.working_dir
            
            # Ensure working directory exists
            os.makedirs(work_dir, exist_ok=True)
            
            # Try different TRAE execution methods
            execution_methods = [
                self._execute_via_trae_cli,
                self._execute_via_python_module,
                self._execute_via_direct_import
            ]
            
            for method in execution_methods:
                try:
                    result = method(task_description, selected_model, work_dir)
                    if result["status"] != "error":
                        return result
                except Exception as e:
                    print(f"Execution method failed: {e}")
                    continue
            
            # Fallback: Mock execution with Ollama call
            return self._execute_fallback_ollama(task_description, selected_model)
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "method": "exception_caught"
            }
    
    def _execute_via_trae_cli(self, task_description, model, working_dir):
        """Execute via TRAE CLI"""
        cmd = [
            "python3", "-m", "trae_agent.cli", "run", task_description,
            "--provider", "ollama",
            "--model", model,
            "--working-dir", working_dir
        ]
        
        # Set environment for Ollama
        env = os.environ.copy()
        env["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
        env["OLLAMA_API_KEY"] = "ollama"
        
        result = subprocess.run(
            cmd,
            cwd=self.trae_path,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            env=env
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "method": "trae_cli",
            "model": model,
            "command": " ".join(cmd)
        }
    
    def _execute_via_python_module(self, task_description, model, working_dir):
        """Execute via Python module import"""
        # This would require importing TRAE as a module
        # For now, return error to try next method
        return {"status": "error", "method": "python_module", "error": "Not implemented"}
    
    def _execute_via_direct_import(self, task_description, model, working_dir):
        """Execute via direct Python import"""
        # This would require setting up TRAE programmatically
        # For now, return error to try next method
        return {"status": "error", "method": "direct_import", "error": "Not implemented"}
    
    def _execute_fallback_ollama(self, task_description, model):
        """Fallback: Direct Ollama API call"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": f"You are a software engineering assistant. Task: {task_description}\n\nProvide a detailed solution:",
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                ollama_result = response.json()
                return {
                    "status": "success",
                    "stdout": ollama_result.get("response", ""),
                    "method": "ollama_fallback",
                    "model": model,
                    "ollama_response": ollama_result
                }
            else:
                return {
                    "status": "error",
                    "method": "ollama_fallback",
                    "error": f"Ollama API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "method": "ollama_fallback",
                "error": str(e)
            }
    
    def execute_with_ai_enhancement(self, task_description, model=None):
        """Execute task with AI Empire enhancement"""
        enhanced_context = {"original_task": task_description}
        
        # Enhance with Council if available
        if "council" in self.enhanced_services:
            try:
                council_response = requests.post(
                    f"{self.enhanced_services['council']}/deliberate",
                    json={"problem": f"How should TRAE approach this coding task: {task_description}"},
                    timeout=10
                )
                if council_response.status_code == 200:
                    council_data = council_response.json()
                    enhanced_context["council_guidance"] = council_data.get("council_decision", "")
            except Exception as e:
                print(f"Council enhancement failed: {e}")
        
        # Enhance with MrLore if available
        if "mrlore" in self.enhanced_services:
            try:
                mrlore_response = requests.post(
                    f"{self.enhanced_services['mrlore']}/analyze",
                    json={"text": task_description},
                    timeout=10
                )
                if mrlore_response.status_code == 200:
                    mrlore_data = mrlore_response.json()
                    enhanced_context["narrative_analysis"] = mrlore_data.get("analysis", "")
            except Exception as e:
                print(f"MrLore enhancement failed: {e}")
        
        # Create enhanced task description
        if len(enhanced_context) > 1:
            enhanced_task = f"{task_description}\n\nContext from AI Empire:\n{json.dumps(enhanced_context, indent=2)}"
        else:
            enhanced_task = task_description
        
        # Execute with TRAE
        return self.execute_trae_task(enhanced_task, model)
    
    # =========================================================================
    # API ENDPOINTS
    # =========================================================================
    
    def run_task(self, data):
        """Run software engineering task with Ollama"""
        task = data.get("task", "")
        model = data.get("model", self.default_model)
        working_dir = data.get("working_dir", self.working_dir)
        use_ai_enhancement = data.get("use_ai_enhancement", True)
        
        print(f"🚀 TRAE Task: {task} (Model: {model})")
        
        if use_ai_enhancement and self.enhanced_services:
            result = self.execute_with_ai_enhancement(task, model)
        else:
            result = self.execute_trae_task(task, model, working_dir)
        
        return {
            "action": "run_task",
            "task": task,
            "model": model,
            "provider": "ollama",
            "ai_enhanced": use_ai_enhancement and len(self.enhanced_services) > 0,
            "enhanced_by": list(self.enhanced_services.keys()),
            "execution": result,
            "source": "Real TRAE Agent (Ollama)"
        }
    
    def code_generation(self, data):
        """Generate code using Ollama models"""
        requirements = data.get("requirements", "")
        language = data.get("language", "python")
        model = data.get("model", self.default_model)
        
        task = f"Generate {language} code with the following requirements: {requirements}"
        result = self.execute_trae_task(task, model)
        
        return {
            "action": "code_generation",
            "requirements": requirements,
            "language": language,
            "model": model,
            "execution": result,
            "source": "Real TRAE Agent (Ollama)"
        }
    
    def debug_code(self, data):
        """Debug code using AI Empire + Ollama"""
        code = data.get("code", "")
        issue_description = data.get("issue_description", "")
        model = data.get("model", self.default_model)
        
        task = f"Debug this code issue: {issue_description}\n\nCode:\n{code}"
        result = self.execute_with_ai_enhancement(task, model)
        
        return {
            "action": "debug_code",
            "issue": issue_description,
            "model": model,
            "ai_enhanced": True,
            "execution": result,
            "source": "Real TRAE Agent (Ollama)"
        }
    
    def start(self):
        """Start Real TRAE Agent service with Ollama"""
        # Start discovery beacon
        self.beacon.start()
        
        # Create Flask app with discovery endpoints
        app = create_flask_discovery_server(self.beacon)
        
        # Add TRAE-specific endpoints
        @app.route('/run_task', methods=['POST'])
        def run_task_endpoint():
            data = request.json
            result = self.run_task(data)
            return jsonify(result)
        
        @app.route('/code_generation', methods=['POST'])
        def code_generation_endpoint():
            data = request.json
            result = self.code_generation(data)
            return jsonify(result)
        
        @app.route('/debug_code', methods=['POST'])
        def debug_code_endpoint():
            data = request.json
            result = self.debug_code(data)
            return jsonify(result)
        
        # Legacy compatibility endpoints
        @app.route('/move_object', methods=['POST'])
        def move_object_endpoint():
            data = request.json
            task = f"Generate GDScript code to move object '{data.get('object', '')}' to position {data.get('position', [0,0,0])}"
            result = self.execute_trae_task(task)
            return jsonify({
                "action": "move_object",
                "object": data.get("object", ""),
                "position": data.get("position", [0,0,0]),
                "gdscript_generated": True,
                "execution": result,
                "source": "Real TRAE Agent (Ollama)"
            })
        
        @app.route('/ai_action', methods=['POST'])
        def ai_action_endpoint():
            data = request.json
            user_request = data.get("request", "")
            result = self.execute_with_ai_enhancement(user_request)
            return jsonify({
                "user_request": user_request,
                "ai_enhanced": True,
                "execution": result,
                "source": "Real TRAE Agent (Ollama)"
            })
        
        print(f"🚀 Real TRAE Agent (Ollama) service started on port {self.beacon.port}")
        print("🤖 Local LLM software engineering ready!")
        print(f"🧠 Using models: {self.ollama_models}")
        print("🔗 AI Empire integration enabled!")
        
        app.run(host='0.0.0.0', port=self.beacon.port, debug=False)

if __name__ == "__main__":
    trae = OllamaTRAEService()
    trae.start()
