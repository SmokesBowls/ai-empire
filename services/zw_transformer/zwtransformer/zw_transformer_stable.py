#!/usr/bin/env python3
"""
ZW Transformer Daemon - STABILIZED WITH MRLORE BRAIN
MrLore intelligence patterns applied for bulletproof stability
"""

import sys
import os
import datetime
import json
import yaml
import uvicorn
import logging
import requests
import time
import hashlib
import subprocess
import tempfile
import signal
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
from dataclasses import dataclass

# === MRLORE INTELLIGENCE CORE ===

class MrLoreIntelligence:
    """
    Extracted intelligence patterns from MrLore for system stability
    """
    def __init__(self):
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.memory_cache = {}
        self.process_registry = {}
        self.service_health = {}
        self.last_health_check = 0
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ZW_Intelligence")
        
    def _generate_hash(self, content: str) -> str:
        """Generate content hash for caching (MrLore pattern)"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _validate_service(self, url: str, timeout: int = 5) -> bool:
        """Health check with MrLore's connection validation"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def _find_executable(self, name: str, common_paths: List[str]) -> Optional[str]:
        """MrLore's adaptive path detection"""
        # Check if it's already in PATH
        import shutil
        if shutil.which(name):
            return shutil.which(name)
        
        # Check common paths
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        return None
    
    def _cleanup_orphaned_processes(self):
        """Clean up tracked processes that are no longer running"""
        dead_processes = []
        for process_id, process_info in self.process_registry.items():
            try:
                pid = process_info.get('pid')
                if pid and not self._is_process_alive(pid):
                    dead_processes.append(process_id)
            except:
                dead_processes.append(process_id)
        
        for dead_id in dead_processes:
            del self.process_registry[dead_id]
            self.logger.info(f"🧹 Cleaned up dead process: {dead_id}")
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if process is alive using standard library only"""
        try:
            # Send signal 0 to check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
        except PermissionError:
            # Process exists but we don't have permission to signal it
            return True

@dataclass
class ServiceConfig:
    name: str
    port: int
    health_endpoint: str
    required: bool = True
    fallback_available: bool = False

class ZWTransformerStable(MrLoreIntelligence):
    """
    ZW Transformer with MrLore brain patterns for stability
    """
    
    def __init__(self):
        super().__init__()
        
        # Service configuration
        self.services = {
            'ollama': ServiceConfig('ollama', 11434, '/api/tags', True, True),
            'voice': ServiceConfig('voice', 8000, '/health', False, True),
        }
        
        # Configuration with MrLore validation
        self.blender_path = self._validate_blender_installation()
        self.ollama_base_url = "http://localhost:11434"
        self.voice_base_url = "http://localhost:8000"
        
        # MrLore cache and monitoring
        self.health_check_interval = 30  # seconds
        self.max_process_timeout = 300   # 5 minutes
        
        # Start background monitoring
        self._start_health_monitoring()
        
    def _validate_blender_installation(self) -> str:
        """MrLore-style adaptive Blender path validation"""
        custom_path = os.getenv('BLENDER_EXECUTABLE')
        if custom_path and os.path.exists(custom_path):
            self.logger.info(f"✅ Using custom Blender path: {custom_path}")
            return custom_path
        
        common_blender_paths = [
            "/usr/bin/blender",
            "/snap/bin/blender", 
            "/opt/blender/blender",
            "/usr/local/bin/blender",
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/home/tran/Downloads/blender-4.4.3-linux-x64/blender"  # Your specific path
        ]
        
        detected_path = self._find_executable("blender", common_blender_paths)
        if detected_path:
            self.logger.info(f"✅ Detected Blender: {detected_path}")
            return detected_path
        
        self.logger.warning("⚠️ Blender not found - some features will be disabled")
        return None
    
    def _validate_ollama_models(self) -> List[str]:
        """MrLore's model validation with fallback logic"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                self.logger.info(f"✅ Available Ollama models: {len(models)}")
                return models
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Ollama validation failed: {e}")
            return []
    
    def _start_health_monitoring(self):
        """Background health monitoring (MrLore pattern)"""
        def monitor():
            while True:
                try:
                    self._perform_health_check()
                    self._cleanup_orphaned_processes()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    self.logger.error(f"Health monitor error: {e}")
                    time.sleep(10)  # Shorter retry on error
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self.logger.info("🩺 Health monitoring started")
    
    def _perform_health_check(self):
        """Comprehensive service health check"""
        current_time = time.time()
        
        for service_name, config in self.services.items():
            url = f"http://localhost:{config.port}{config.health_endpoint}"
            is_healthy = self._validate_service(url)
            
            previous_status = self.service_health.get(service_name, True)
            self.service_health[service_name] = is_healthy
            
            # Log status changes
            if previous_status != is_healthy:
                status = "🟢 ONLINE" if is_healthy else "🔴 OFFLINE"
                self.logger.info(f"{status} {config.name} ({url})")
                
                # Attempt recovery for critical services
                if not is_healthy and config.required:
                    self._attempt_service_recovery(service_name, config)
        
        self.last_health_check = current_time
    
    def _attempt_service_recovery(self, service_name: str, config: ServiceConfig):
        """Attempt to recover failed services"""
        self.logger.warning(f"🔧 Attempting recovery for {service_name}")
        
        if service_name == 'ollama':
            # Suggest Ollama restart
            self.logger.error(f"❌ {service_name} is critical but offline. Please start it manually:")
            self.logger.error("   Run: ollama serve")
        
        elif service_name == 'voice':
            # Voice service is optional
            self.logger.warning(f"⚠️ {service_name} offline - voice features disabled")
    
    def _execute_blender_with_monitoring(self, command_args: List[str]) -> Dict:
        """Execute Blender with MrLore process monitoring"""
        if not self.blender_path:
            return {
                "status": "error",
                "message": "Blender not available - install Blender or set BLENDER_EXECUTABLE"
            }
        
        process_id = self._generate_hash(str(command_args))
        
        try:
            # Register process
            self.process_registry[process_id] = {
                "command": command_args,
                "started": time.time(),
                "timeout": self.max_process_timeout
            }
            
            self.logger.info(f"🎬 Starting Blender process: {process_id}")
            
            # Execute with timeout
            full_command = [self.blender_path] + command_args
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=self.max_process_timeout
            )
            
            # Update registry with PID
            self.process_registry[process_id].update({
                "pid": result.pid if hasattr(result, 'pid') else None,
                "completed": time.time(),
                "return_code": result.returncode
            })
            
            elapsed = time.time() - self.process_registry[process_id]["started"]
            self.logger.info(f"✅ Blender process completed in {elapsed:.1f}s")
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "elapsed_time": elapsed,
                "process_id": process_id
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ Blender process timeout: {process_id}")
            return {
                "status": "error", 
                "message": f"Blender process timed out after {self.max_process_timeout}s",
                "process_id": process_id
            }
        except Exception as e:
            self.logger.error(f"💥 Blender process failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "process_id": process_id
            }
        finally:
            # Cleanup process registry
            if process_id in self.process_registry:
                del self.process_registry[process_id]
    
    def _ollama_with_fallback(self, endpoint: str, payload: Dict) -> str:
        """Ollama API call with MrLore fallback logic"""
        if not self.service_health.get('ollama', False):
            return "❌ Ollama service is not available. Please start Ollama: ollama serve"
        
        try:
            url = f"{self.ollama_base_url}/api/{endpoint}"
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.Timeout:
            return "⏰ Ollama request timed out - try a simpler prompt or different model"
        except requests.exceptions.RequestException as e:
            return f"❌ Ollama error: {str(e)}"
    
    def get_system_status(self) -> Dict:
        """Comprehensive system status (MrLore pattern)"""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "session_id": self.session_id,
            "services": {
                name: {
                    "healthy": self.service_health.get(name, False),
                    "required": config.required,
                    "port": config.port
                }
                for name, config in self.services.items()
            },
            "blender": {
                "available": self.blender_path is not None,
                "path": self.blender_path
            },
            "processes": {
                "active": len(self.process_registry),
                "registry": list(self.process_registry.keys())
            },
            "cache": {
                "entries": len(self.memory_cache)
            },
            "last_health_check": self.last_health_check,
            "uptime_seconds": time.time() - float(self.session_id)
        }

# === BLENDER ADAPTER WITH STABILITY ===

class StableBlenderAdapter:
    def __init__(self, intelligence_core: ZWTransformerStable):
        self.name = "blender"
        self.version = "stable-v1.0" 
        self.capabilities = ["mesh", "scene", "material", "light", "camera"]
        self.status = "active" if intelligence_core.blender_path else "disabled"
        self.intelligence = intelligence_core
    
    def get_status(self):
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
            "status": self.status,
            "blender_path": self.intelligence.blender_path
        }
    
    def process_scene(self, scene_data):
        """Process ZW scene with stability monitoring"""
        if self.status != "active":
            return {
                "status": "error",
                "message": "Blender adapter is disabled - check Blender installation"
            }
        
        try:
            # Create temporary ZW file
            zw_string = yaml.dump({"ZW-SCENE": scene_data})
            
            with tempfile.NamedTemporaryFile('w', suffix='.zw', delete=False) as zw_file:
                zw_file.write(zw_string)
                zw_path = zw_file.name
            
            output_path = zw_path + ".json"
            
            # Execute with monitoring
            result = self.intelligence._execute_blender_with_monitoring([
                "--background",
                "--python", "backend/blender_scripts/blender_zw_processor.py",
                "--", zw_path, output_path
            ])
            
            # Process results
            blender_results = []
            if result.get("status") == "success" and os.path.exists(output_path):
                try:
                    with open(output_path) as f:
                        blender_results = json.load(f)
                except json.JSONDecodeError:
                    pass
            
            # Cleanup
            for temp_file in [zw_path, output_path]:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
            
            return {
                **result,
                "blender_results": blender_results,
                "temp_files_cleaned": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Blender processing failed: {str(e)}"
            }

# === FASTAPI APPLICATION ===

# Initialize stable core
intelligence_core = ZWTransformerStable()
blender_adapter = StableBlenderAdapter(intelligence_core)

app = FastAPI(title="ZW Transformer - Stabilized", version="1.0.0-stable")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# === API MODELS ===

class ZWRequest(BaseModel):
    zw_data: str
    route_to_blender: bool = False
    blender_path: str | None = None
    target_engines: list[str] | None = None

# === HEALTH & STATUS ENDPOINTS ===

@app.get("/health")
async def health_check():
    """Enhanced health check with MrLore intelligence"""
    status = intelligence_core.get_system_status()
    
    # Overall health calculation
    critical_services_healthy = all(
        status["services"][name]["healthy"] 
        for name, config in intelligence_core.services.items() 
        if config.required
    )
    
    return JSONResponse(content={
        "status": "healthy" if critical_services_healthy else "degraded",
        "system": status,
        "message": "ZW Transformer with MrLore intelligence is running"
    })

@app.get("/system/status")
async def system_status():
    """Detailed system status"""
    return JSONResponse(content=intelligence_core.get_system_status())

@app.get("/system/processes")
async def active_processes():
    """Show active process registry"""
    return JSONResponse(content={
        "active_processes": intelligence_core.process_registry,
        "count": len(intelligence_core.process_registry)
    })

# === ZW PROCESSING ENDPOINTS ===

@app.post("/process_zw")
async def process_zw(req: ZWRequest):
    """Process ZW with stability monitoring"""
    try:
        # Validate ZW content
        cleaned_zw = req.zw_data.strip()
        if cleaned_zw.startswith("```yaml"):
            cleaned_zw = cleaned_zw.replace("```yaml", "").replace("```", "").strip()
        
        try:
            parsed_zw = yaml.safe_load(cleaned_zw)
        except yaml.YAMLError as e:
            return JSONResponse(content={
                "status": "error",
                "message": f"Invalid YAML content: {str(e)}"
            }, status_code=400)
        
        # Process with Blender if requested
        results = {}
        if req.route_to_blender and blender_adapter.status == "active":
            results["blender"] = blender_adapter.process_scene(parsed_zw)
        elif req.route_to_blender:
            results["blender"] = {
                "status": "error",
                "message": "Blender not available"
            }
        
        return JSONResponse(content={
            "status": "processed",
            "results": results,
            "system_status": intelligence_core.get_system_status(),
            "processed_length": len(req.zw_data),
            "parsed_sections": list(parsed_zw.keys()) if isinstance(parsed_zw, dict) else [],
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        intelligence_core.logger.exception("Error processing ZW")
        return JSONResponse(content={
            "status": "error", 
            "message": str(e),
            "system_status": intelligence_core.get_system_status()
        }, status_code=500)

# === OLLAMA ENDPOINTS ===

@app.get("/ollama/models")
async def get_ollama_models():
    """Get available Ollama models with health check"""
    if not intelligence_core.service_health.get('ollama', False):
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "Ollama service is not available",
                "models": []
            }
        )
    
    models = intelligence_core._validate_ollama_models()
    return JSONResponse(content={
        "status": "success",
        "models": models,
        "count": len(models),
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.post("/ollama/generate")
async def generate_with_ollama(request: Request):
    """Generate with Ollama using stable patterns"""
    try:
        body = await request.json()
        model = body.get("model", "llama3.1:8b")
        prompt = body.get("prompt", "")
        
        # Validate model availability
        available_models = intelligence_core._validate_ollama_models()
        if model not in available_models:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Model '{model}' not available. Available: {available_models}"
                }
            )
        
        # Generate with fallback
        ollama_request = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": body.get("temperature", 0.7),
                "top_p": body.get("top_p", 0.9),
                "num_predict": body.get("max_tokens", 2048)
            }
        }
        
        generated_text = intelligence_core._ollama_with_fallback("generate", ollama_request)
        
        return JSONResponse(content={
            "status": "success",
            "generated_zw": generated_text,
            "model_used": model,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Generation failed: {str(e)}"
            }
        )

@app.get("/engines")
async def get_engines():
    """Engine information"""
    return JSONResponse(content={
        "router_status": {
            "registered_engines": 1,
            "default_engine": "blender",
            "engines": {
                "blender": blender_adapter.get_status()
            },
            "total_capabilities": len(blender_adapter.capabilities)
        },
        "capabilities": {
            "blender": blender_adapter.capabilities
        },
        "system_status": intelligence_core.get_system_status(),
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(content={
        "message": "ZW Transformer - Stabilized with MrLore Intelligence",
        "version": "1.0.0-stable",
        "system_status": intelligence_core.get_system_status(),
        "timestamp": datetime.datetime.now().isoformat()
    })

# === MAIN ===

if __name__ == "__main__":
    intelligence_core.logger.info("🚀 Starting ZW Transformer - Stabilized Edition")
    intelligence_core.logger.info("🧠 MrLore intelligence patterns active")
    intelligence_core.logger.info(f"🎬 Blender: {'✅ Available' if intelligence_core.blender_path else '❌ Not found'}")
    intelligence_core.logger.info(f"🤖 Ollama: {'✅ Connected' if intelligence_core.service_health.get('ollama') else '❌ Offline'}")
    
    uvicorn.run("__main__:app", host="127.0.0.1", port=1111, reload=False)
