#!/usr/bin/env python3
"""
ClutterBot Core - Central Orchestrator with MrLore Intelligence
The brain that manages all your systems with extracted MrLore patterns
"""

import os
import sys
import time
import json
import logging
import hashlib
import subprocess
import threading
import signal
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# === MRLORE INTELLIGENCE CORE (EXTRACTED) ===

class MrLoreIntelligence:
    """
    Extracted intelligence patterns from MrLore for system orchestration
    """
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = time.time()  # Fixed uptime calculation
        self.memory_cache = {}
        self.process_registry = {}
        self.service_health = {}
        self.last_health_check = 0
        
        # Initialize logging
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup intelligent logging"""
        logger = logging.getLogger(f"MrLore-{self.app_name}")
        logger.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        return logger
        
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
        import shutil
        if shutil.which(name):
            return shutil.which(name)
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        return None
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if process is alive using standard library only"""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
        except PermissionError:
            return True
    
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

# === SERVICE MANAGEMENT ===

@dataclass
class ServiceDefinition:
    name: str
    service_type: str  # 'python', 'executable', 'system_service'
    source_path: str
    health_check_url: Optional[str] = None
    start_command: Optional[List[str]] = None
    working_directory: Optional[str] = None
    required: bool = True
    auto_restart: bool = True
    restart_delay: int = 5
    max_restarts: int = 3

@dataclass
class ServiceStatus:
    name: str
    status: str  # 'stopped', 'starting', 'running', 'healthy', 'unhealthy', 'failed'
    pid: Optional[int] = None
    process: Optional[subprocess.Popen] = None
    last_health_check: float = 0
    restart_count: int = 0
    last_restart: float = 0
    uptime: float = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

# === CLUTTERBOT CORE ===

class ClutterBotCore(MrLoreIntelligence):
    """
    Central orchestrator with MrLore intelligence
    """
    
    def __init__(self, config_dir: str = "~/.clutterbot"):
        super().__init__("ClutterBot")
        
        # Configuration
        self.config_dir = Path(config_dir).expanduser()
        self.config_dir.mkdir(exist_ok=True, parents=True)
        
        self.services_dir = self.config_dir / "services"
        self.logs_dir = self.config_dir / "logs"
        self.plugins_dir = self.config_dir / "plugins"
        
        # Create directories
        for directory in [self.services_dir, self.logs_dir, self.plugins_dir]:
            directory.mkdir(exist_ok=True)
        
        # Service management
        self.services: Dict[str, ServiceDefinition] = {}
        self.service_status: Dict[str, ServiceStatus] = {}
        
        # Monitoring
        self.health_check_interval = 15  # seconds
        self.monitor_thread = None
        self.running = True
        
        # Initialize
        self.logger.info("🧠 ClutterBot Core initializing with MrLore intelligence")
        self._load_service_definitions()
        self._start_monitoring()
        
    def _load_service_definitions(self):
        """Load service definitions from configuration"""
        config_file = self.services_dir / "services.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    services_data = json.load(f)
                    
                for service_data in services_data.get('services', []):
                    service = ServiceDefinition(**service_data)
                    self.services[service.name] = service
                    self.service_status[service.name] = ServiceStatus(
                        name=service.name,
                        status='stopped'
                    )
                    
                self.logger.info(f"📋 Loaded {len(self.services)} service definitions")
            except Exception as e:
                self.logger.error(f"❌ Failed to load service definitions: {e}")
    
    def _save_service_definitions(self):
        """Save service definitions to configuration"""
        config_file = self.services_dir / "services.json"
        try:
            services_data = {
                'services': [asdict(service) for service in self.services.values()],
                'updated': datetime.now().isoformat()
            }
            
            with open(config_file, 'w') as f:
                json.dump(services_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to save service definitions: {e}")
    
    def register_service(self, service: ServiceDefinition):
        """Register a new service with ClutterBot"""
        service_id = self._generate_hash(service.name)
        
        self.services[service.name] = service
        self.service_status[service.name] = ServiceStatus(
            name=service.name,
            status='stopped'
        )
        
        self.logger.info(f"📝 Registered service: {service.name} ({service.service_type})")
        self._save_service_definitions()
        
        return service_id
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.services:
            self.logger.error(f"❌ Service not found: {service_name}")
            return False
        
        service = self.services[service_name]
        status = self.service_status[service_name]
        
        if status.status in ['running', 'starting', 'healthy']:
            self.logger.warning(f"⚠️ Service already running: {service_name}")
            return True
        
        self.logger.info(f"🚀 Starting service: {service_name}")
        status.status = 'starting'
        
        try:
            if service.service_type == 'python':
                # Start Python script
                cmd = ['python3', service.source_path]
                if service.start_command:
                    cmd.extend(service.start_command)
                    
                process = subprocess.Popen(
                    cmd,
                    cwd=service.working_directory or os.path.dirname(service.source_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True
                )
                
                status.process = process
                status.pid = process.pid
                status.status = 'running'
                status.uptime = time.time()
                
                # Register process for monitoring
                process_id = self._generate_hash(f"{service_name}_{status.pid}")
                self.process_registry[process_id] = {
                    "service_name": service_name,
                    "pid": status.pid,
                    "started": time.time(),
                    "command": cmd
                }
                
                self.logger.info(f"✅ Started {service_name} (PID: {status.pid})")
                return True
                
            elif service.service_type == 'executable':
                # Start executable
                process = subprocess.Popen(
                    service.start_command or [service.source_path],
                    cwd=service.working_directory,
                    start_new_session=True
                )
                
                status.process = process
                status.pid = process.pid
                status.status = 'running'
                status.uptime = time.time()
                
                self.logger.info(f"✅ Started {service_name} (PID: {status.pid})")
                return True
                
        except Exception as e:
            status.status = 'failed'
            status.errors.append(f"Start failed: {str(e)}")
            self.logger.error(f"💥 Failed to start {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.service_status:
            return False
        
        status = self.service_status[service_name]
        
        if status.process and status.pid:
            try:
                # Graceful termination
                status.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    status.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    status.process.kill()
                    status.process.wait()
                
                self.logger.info(f"🛑 Stopped service: {service_name}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to stop {service_name}: {e}")
                return False
        
        status.status = 'stopped'
        status.process = None
        status.pid = None
        
        return True
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a service"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        status = self.service_status[service_name]
        
        # Check restart limits
        if status.restart_count >= service.max_restarts:
            self.logger.error(f"🚨 Max restarts reached for {service_name}")
            status.status = 'failed'
            return False
        
        # Stop if running
        if status.status in ['running', 'healthy', 'unhealthy']:
            self.stop_service(service_name)
        
        # Wait for restart delay
        if service.restart_delay > 0:
            time.sleep(service.restart_delay)
        
        # Increment restart counter
        status.restart_count += 1
        status.last_restart = time.time()
        
        self.logger.info(f"🔄 Restarting {service_name} (attempt #{status.restart_count})")
        
        return self.start_service(service_name)
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        def monitor_loop():
            while self.running:
                try:
                    self._perform_health_checks()
                    self._cleanup_orphaned_processes()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    self.logger.error(f"Monitoring error: {e}")
                    time.sleep(5)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("👁️ Health monitoring started")
    
    def _perform_health_checks(self):
        """Perform health checks on all services"""
        current_time = time.time()
        
        for service_name, service in self.services.items():
            status = self.service_status[service_name]
            
            if status.status not in ['running', 'healthy', 'unhealthy']:
                continue
            
            # Check if process is still alive
            if status.pid and not self._is_process_alive(status.pid):
                self.logger.warning(f"💀 Process died: {service_name}")
                status.status = 'failed'
                
                if service.auto_restart:
                    self.restart_service(service_name)
                continue
            
            # Check health endpoint if available
            if service.health_check_url:
                is_healthy = self._validate_service(service.health_check_url)
                
                previous_status = status.status
                status.status = 'healthy' if is_healthy else 'unhealthy'
                status.last_health_check = current_time
                
                # Log status changes
                if previous_status != status.status:
                    emoji = "🟢" if is_healthy else "🔴"
                    self.logger.info(f"{emoji} {service_name}: {status.status}")
                
                # Auto-restart unhealthy services
                if not is_healthy and service.auto_restart:
                    self.logger.warning(f"🔧 Auto-restarting unhealthy service: {service_name}")
                    self.restart_service(service_name)
        
        self.last_health_check = current_time
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "uptime_seconds": time.time() - self.start_time,
            "services": {
                name: {
                    "status": status.status,
                    "pid": status.pid,
                    "restart_count": status.restart_count,
                    "uptime": time.time() - status.uptime if status.uptime else 0,
                    "last_health_check": status.last_health_check,
                    "errors": status.errors[-3:],  # Last 3 errors
                    "required": self.services[name].required
                }
                for name, status in self.service_status.items()
            },
            "processes": {
                "active": len(self.process_registry),
                "registry": list(self.process_registry.keys())
            },
            "cache": {
                "entries": len(self.memory_cache)
            },
            "last_health_check": self.last_health_check
        }
    
    def start_all_services(self):
        """Start all registered services"""
        self.logger.info("🚀 Starting all services...")
        
        for service_name in self.services:
            if self.services[service_name].required:
                self.start_service(service_name)
    
    def stop_all_services(self):
        """Stop all running services"""
        self.logger.info("🛑 Stopping all services...")
        
        for service_name in self.service_status:
            if self.service_status[service_name].status in ['running', 'healthy', 'unhealthy']:
                self.stop_service(service_name)
    
    def shutdown(self):
        """Graceful shutdown of ClutterBot"""
        self.logger.info("🏁 ClutterBot shutting down...")
        self.running = False
        
        # Stop all services
        self.stop_all_services()
        
        # Wait for monitor thread
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("👋 ClutterBot shutdown complete")

# === MAIN INTERFACE ===

def main():
    """Main ClutterBot interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ClutterBot - Intelligent Service Orchestrator")
    parser.add_argument("--config-dir", default="~/.clutterbot", help="Configuration directory")
    parser.add_argument("--register-zw", action="store_true", help="Register ZW Transformer")
    parser.add_argument("--start-all", action="store_true", help="Start all services")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--monitor", action="store_true", help="Run in monitoring mode")
    
    args = parser.parse_args()
    
    # Initialize ClutterBot
    clutterbot = ClutterBotCore(config_dir=args.config_dir)
    
    # Handle shutdown gracefully
    def signal_handler(signum, frame):
        clutterbot.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.register_zw:
            # Register ZW Transformer service
            zw_service = ServiceDefinition(
                name="ZW Transformer",
                service_type="python",
                source_path="zw_transformer_stable.py",
                health_check_url="http://localhost:1111/health",
                working_directory=os.getcwd(),
                required=True,
                auto_restart=True
            )
            clutterbot.register_service(zw_service)
            print("✅ ZW Transformer registered")
        
        if args.start_all:
            clutterbot.start_all_services()
        
        if args.status:
            status = clutterbot.get_system_status()
            print(json.dumps(status, indent=2))
        
        if args.monitor:
            print("👁️ ClutterBot monitoring mode - Press Ctrl+C to stop")
            print(f"🧠 MrLore intelligence active")
            print(f"📊 Managing {len(clutterbot.services)} services")
            
            try:
                while True:
                    time.sleep(10)
                    
                    # Print status summary every 30 seconds
                    if int(time.time()) % 30 == 0:
                        status = clutterbot.get_system_status()
                        healthy_services = sum(1 for s in status['services'].values() 
                                             if s['status'] in ['healthy', 'running'])
                        total_services = len(status['services'])
                        
                        print(f"📊 Status: {healthy_services}/{total_services} services healthy")
                        
            except KeyboardInterrupt:
                pass
        
        # If no specific action, show help
        if not any([args.register_zw, args.start_all, args.status, args.monitor]):
            parser.print_help()
            
    finally:
        clutterbot.shutdown()

if __name__ == "__main__":
    main()