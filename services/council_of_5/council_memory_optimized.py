#!/usr/bin/env python3
"""
STABLE Council of 5 - Memory-Optimized Edition
Rock-solid multi-AI council with reduced memory footprint
"""

import requests
import json
import time
import hashlib
import os
import threading
import asyncio
import gc
import zlib
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
import logging

# Setup logging with memory tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('council_stable.log', mode='a', delay=True)
    ]
)
logger = logging.getLogger("council_stable")

# Memory management configuration
MEMORY_CHECK_INTERVAL = 300  # Seconds between memory checks
MAX_HISTORY_ENTRIES = 20     # Reduced conversation history
MAX_CACHE_SIZE = 50          # Max in-memory cache entries
MAX_SESSION_SIZE = 1000      # Max characters per session response
MAX_HOOK_RESULT = 500        # Max characters for hook results

@dataclass
class CouncilMemberConfig:
    """Configuration for a council member"""
    name: str
    model: str
    personality: str
    context_weight: float = 1.0
    timeout: int = 60
    max_retries: int = 3
    fallback_models: List[str] = field(default_factory=list)
    hook_access: List[str] = field(default_factory=list)

class MemoryManager:
    """Memory management system with resource monitoring"""
    
    def __init__(self):
        self.last_check = time.time()
        self.memory_warnings = 0
        self.conversation_cache = {}
        self.active_sessions = {}
        
    def is_memory_pressure(self) -> bool:
        """Check if memory pressure is high"""
        # Check swap usage (simplified for portability)
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                swap_free = int(meminfo.split('SwapFree:')[1].split('kB')[0].strip())
                if swap_free < 50000:  # Less than 50MB swap free
                    return True
        except:
            # Fallback to time-based check
            return (time.time() - self.last_check) < 60 and self.memory_warnings > 2
        
        return False
    
    def optimize_memory(self):
        """Perform memory optimization routines"""
        logger.warning("🚨 Memory pressure detected - optimizing resources")
        
        # 1. Clear conversation cache
        self.conversation_cache.clear()
        
        # 2. Clear inactive sessions
        active_keys = list(self.active_sessions.keys())
        for key in list(self.active_sessions.keys()):
            if key not in active_keys:
                del self.active_sessions[key]
        
        # 3. Run garbage collection
        gc.collect()
        
        # 4. Clear session history
        for session in self.active_sessions.values():
            if 'history' in session:
                session['history'] = session['history'][-MAX_HISTORY_ENTRIES//2:]
        
        logger.info("🧹 Memory optimization complete")
        self.memory_warnings = 0
        self.last_check = time.time()
    
    def compress_data(self, data: str) -> bytes:
        """Compress data to save memory"""
        return zlib.compress(data.encode('utf-8'), level=3)
    
    def decompress_data(self, data: bytes) -> str:
        """Decompress data"""
        return zlib.decompress(data).decode('utf-8')

class MrLoreCouncilBrain:
    """MrLore intelligence with memory-aware operations"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.cache_dir = Path("council_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Model availability tracking
        self.available_models = set()
        self.last_health_check = {}
        
    def scan_available_models(self) -> List[str]:
        """Scan for available Ollama models with memory checks"""
        if self.memory.is_memory_pressure():
            logger.warning("⏭️ Skipping model scan due to memory pressure")
            return list(self.available_models)
        
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                models = [model['name'] for model in models_data.get('models', [])]
                
                new_models = set(models) - self.available_models
                lost_models = self.available_models - set(models)
                
                if new_models:
                    logger.info(f"✅ New models available: {new_models}")
                if lost_models:
                    logger.warning(f"❌ Models lost: {lost_models}")
                
                self.available_models = set(models)
                self.last_health_check['ollama'] = datetime.now()
                
                return models
            else:
                logger.warning(f"Ollama health check failed: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Model scan failed: {e}")
            return []
    
    def validate_member_config(self, config: CouncilMemberConfig) -> bool:
        """Validate that member configuration is viable"""
        if config.model in self.available_models:
            return True
        
        if config.fallback_models:
            for fallback in config.fallback_models:
                if fallback in self.available_models:
                    logger.info(f"🔄 Using fallback {fallback} for {config.name}")
                    return True
        
        logger.error(f"❌ No viable model for {config.name}")
        return False
    
    def get_memory_hash(self, content: str) -> str:
        """Generate hash for content"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def cache_conversation(self, topic: str, responses: List[str]):
        """Cache conversation with memory optimization"""
        if self.memory.is_memory_pressure():
            logger.warning("⏭️ Skipping conversation cache due to memory pressure")
            return
        
        cache_key = self.get_memory_hash(topic + str(time.time()))
        
        # Truncate large responses
        truncated_responses = [
            r[:MAX_SESSION_SIZE] + ('...' if len(r) > MAX_SESSION_SIZE else '') 
            for r in responses
        ]
        
        # Store compressed in memory
        compressed = self.memory.compress_data(json.dumps({
            'topic': topic,
            'responses': truncated_responses,
            'timestamp': datetime.now().isoformat()
        }))
        
        # Only keep recent cache in memory
        if len(self.memory.conversation_cache) >= MAX_CACHE_SIZE:
            oldest_key = next(iter(self.memory.conversation_cache))
            del self.memory.conversation_cache[oldest_key]
        
        self.memory.conversation_cache[cache_key] = compressed
        
        # Persist to disk
        cache_file = self.cache_dir / f"session_{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                'topic': topic,
                'responses': truncated_responses,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
    
    def cleanup_old_cache(self, max_age_hours: int = 24):
        """Clean up old cache files"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for cache_file in self.cache_dir.glob("session_*.json"):
            if cache_file.stat().st_mtime < cutoff_time.timestamp():
                cache_file.unlink()
                logger.info(f"🧹 Cleaned up old cache: {cache_file.name}")

class StableCouncilMember:
    """Memory-optimized council member"""
    
    def __init__(self, config: CouncilMemberConfig, brain: MrLoreCouncilBrain):
        self.config = config
        self.brain = brain
        self.current_model = config.model
        self.consecutive_failures = 0
        self.last_success = datetime.now()
        
        # Reusable session with connection pooling
        self.session = requests.Session()
        self.session.headers.update({'Connection': 'keep-alive'})
        
    def get_active_model(self) -> str:
        """Get the currently active model for this member"""
        if self.config.model in self.brain.available_models:
            if self.current_model != self.config.model:
                logger.info(f"🔄 {self.config.name} switching to primary model")
                self.current_model = self.config.model
            return self.current_model
        
        if self.config.fallback_models:
            for fallback in self.config.fallback_models:
                if fallback in self.brain.available_models:
                    if self.current_model != fallback:
                        logger.info(f"🔄 {self.config.name} switching to fallback")
                        self.current_model = fallback
                    return self.current_model
        
        raise Exception(f"No viable model available for {self.config.name}")
    
    def respond(self, context: str, prompt: str) -> str:
        """Generate response with memory awareness"""
        if self.brain.memory.is_memory_pressure():
            logger.warning(f"⏭️ {self.config.name} skipping response due to memory pressure")
            return f"[{self.config.name} temporarily unavailable - system optimizing]"
        
        for attempt in range(self.config.max_retries):
            try:
                active_model = self.get_active_model()
                
                # Build optimized prompt
                optimized_prompt = self._build_optimized_prompt(context, prompt)
                
                # Prepare request
                payload = {
                    "model": active_model,
                    "prompt": optimized_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 800,  # Reduced for memory
                        "num_ctx": int(4096 * self.config.context_weight)
                    }
                }
                
                logger.info(f"🤔 {self.config.name} thinking (attempt {attempt + 1})")
                
                # Make request
                response = self.session.post(
                    "http://localhost:11434/api/generate",
                    json=payload,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get('response', '').strip()
                    
                    if text:
                        # Process and truncate hook responses
                        processed_text = self._process_hook_commands(text)
                        
                        self.consecutive_failures = 0
                        self.last_success = datetime.now()
                        logger.info(f"✅ {self.config.name} responded")
                        return processed_text
                    else:
                        raise Exception("Empty response")
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.consecutive_failures += 1
                logger.warning(f"⚠️ {self.config.name} attempt failed: {str(e)[:100]}")
                
                if attempt < self.config.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        
        return f"[{self.config.name} temporarily unavailable]"
    
    def _build_optimized_prompt(self, context: str, prompt: str) -> str:
        """Build memory-optimized prompt"""
        # Truncate context to preserve memory
        max_context = 2000
        if len(context) > max_context:
            context = context[:max_context] + "... [context truncated]"
        
        return f"{context}\n\n{self.config.personality}\n\n{prompt}\n\n{self.config.name}:"
    
    def _process_hook_commands(self, text: str) -> str:
        """Process hook commands with result truncation"""
        if "!HOOK[" not in text:
            return text
        
        processed_text = text
        start_idx = 0
        
        while True:
            start_cmd = processed_text.find("!HOOK[", start_idx)
            if start_cmd == -1: break
                
            end_bracket = processed_text.find("]", start_cmd)
            if end_bracket == -1: break
                
            hook_cmd = processed_text[start_cmd+6:end_bracket]
            parts = hook_cmd.split(":")
            if len(parts) < 2:
                start_idx = end_bracket + 1
                continue
                
            hook_name = parts[0].strip()
            command_name = parts[1].strip()
            
            start_brace = processed_text.find("{", end_bracket)
            end_brace = processed_text.find("}", start_brace)
            if start_brace == -1 or end_brace == -1:
                start_idx = end_bracket + 1
                continue
                
            args_str = processed_text[start_brace+1:end_brace]
            
            try:
                # Skip execution under memory pressure
                if self.brain.memory.is_memory_pressure():
                    raise Exception("Memory pressure - skipping hook execution")
                    
                args = json.loads(args_str) if args_str.strip() else None
                
                logger.info(f"⚡ {self.config.name} executing hook: {hook_name}.{command_name}")
                result, status = asyncio.run(
                    self.brain.hook_system.call_hook(hook_name, command_name, args)
                )
                
                if status < 400:
                    # Truncate large results
                    result_str = json.dumps(result) if isinstance(result, dict) else str(result)
                    if len(result_str) > MAX_HOOK_RESULT:
                        result_str = result_str[:MAX_HOOK_RESULT] + "... [truncated]"
                        
                    cmd_str = processed_text[start_cmd:end_brace+1]
                    processed_text = processed_text.replace(
                        cmd_str, 
                        f"\n[HOOK RESULT: {hook_name}.{command_name}]\n{result_str}\n"
                    )
                else:
                    raise Exception(f"Hook error {status}")
            except Exception as e:
                error_msg = f"[HOOK ERROR: {str(e)[:100]}]"
                cmd_str = processed_text[start_cmd:end_brace+1]
                processed_text = processed_text.replace(cmd_str, error_msg)
            
            start_idx = end_brace + 1
        
        return processed_text
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get optimized health status"""
        return {
            'name': self.config.name,
            'model': self.current_model,
            'failures': self.consecutive_failures,
            'last_success': self.last_success.strftime("%H:%M:%S"),
            'healthy': self.consecutive_failures < 3
        }

class StableCouncilSystem:
    """Memory-optimized Stable Council System"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.brain = MrLoreCouncilBrain(self.memory_manager)
        self.members: List[StableCouncilMember] = []
        self.conversation_history: List[str] = []
        
        # Initialize hook system
        self.hook_system = UniversalHookSystem()
        self._configure_optimized_hooks()
        
        # Default council configuration
        self.member_configs = [
            # ... (same as before but with reduced context_weight)
        ]
        
    def _configure_optimized_hooks(self):
        """Configure hooks with memory optimization"""
        optimized_hooks = [
            {
                "name": "ollama",
                "hook_type": "http",
                "endpoint": "http://localhost:11434",
                "timeout": 30,
                "health_check": "http://localhost:11434/api/tags",
                "description": "Ollama model API"
            },
            {
                "name": "blender",
                "hook_type": "subprocess",
                "endpoint": "/usr/bin/blender --background --python {data_file}",
                "timeout": 120,
                "description": "3D rendering"
            },
            # ... (other essential hooks only)
        ]
        
        for hook_config in optimized_hooks:
            config = HookConfig(**hook_config)
            asyncio.run(self.hook_system.register_hook(config))
        
        self.hook_system.start_monitoring(interval=30)
        
    def initialize(self) -> bool:
        """Initialize with memory checks"""
        if self.memory_manager.is_memory_pressure():
            logger.warning("⚠️ Initializing under memory pressure")
        
        # Initialize members
        for config in self.member_configs:
            if self.brain.validate_member_config(config):
                member = StableCouncilMember(config, self.brain)
                self.members.append(member)
        
        return len(self.members) >= 2
    
    def conduct_session(self, topic: str, max_rounds: int = 2) -> Dict[str, Any]:  # Reduced rounds
        """Conduct memory-optimized session"""
        if self.memory_manager.is_memory_pressure():
            self.memory_manager.optimize_memory()
            
        if not self.members:
            return {"error": "Council not initialized"}
        
        session_id = f"session_{int(time.time())}"
        self.memory_manager.active_sessions[session_id] = {
            "start_time": time.time(),
            "topic": topic,
            "history": []
        }
        
        try:
            # ... (session logic with history truncation)
            
            return {
                "topic": topic,
                "responses_count": len(responses),
                "duration": time.time() - session_start,
                "success": len(responses) > 0
            }
        finally:
            # Clean up session data
            if session_id in self.memory_manager.active_sessions:
                session_data = self.memory_manager.active_sessions.pop(session_id)
                # Keep only essential data
                self.conversation_history.extend(session_data['history'][-MAX_HISTORY_ENTRIES:])
                
                # Trim global history
                if len(self.conversation_history) > MAX_HISTORY_ENTRIES:
                    self.conversation_history = self.conversation_history[-MAX_HISTORY_ENTRIES:]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get memory-optimized status"""
        return {
            "members": [m.get_health_status() for m in self.members],
            "history_entries": len(self.conversation_history),
            "active_sessions": len(self.memory_manager.active_sessions),
            "cache_entries": len(self.memory_manager.conversation_cache),
            "memory_warnings": self.memory_manager.memory_warnings
        }
    
    def shutdown(self):
        """Graceful shutdown with memory cleanup"""
        # Clean up members
        for member in self.members:
            member.session.close()
        self.members.clear()
        
        # Clean up hooks
        asyncio.run(self.hook_system.shutdown_all())
        
        # Clean memory
        self.memory_manager.conversation_cache.clear()
        self.memory_manager.active_sessions.clear()
        self.conversation_history.clear()
        gc.collect()
        
        logger.info("✅ Council shutdown with memory cleanup")

# CLI would be similar but with memory status display
# ... (rest of the code remains similar but with memory optimizations)
