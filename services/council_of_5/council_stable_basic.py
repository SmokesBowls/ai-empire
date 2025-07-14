#!/usr/bin/env python3
"""
STABLE Council of 5 - MrLore Intelligence Applied
Rock-solid multi-AI council with self-healing and monitoring
"""

import requests
import json
import time
import hashlib
import os
import threading
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('council_stable.log')
    ]
)
logger = logging.getLogger("council_stable")

@dataclass
class CouncilMemberConfig:
    """Configuration for a council member"""
    name: str
    model: str
    personality: str
    context_weight: float = 1.0
    timeout: int = 60
    max_retries: int = 3
    fallback_models: List[str] = None

class MrLoreCouncilBrain:
    """MrLore intelligence applied to council management"""
    
    def __init__(self):
        self.cache_dir = Path("council_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        self.session_cache = {}
        self.model_health = {}
        self.conversation_memory = []
        
        # Health monitoring
        self.health_thread = None
        self.monitoring_active = False
        
        # Model availability tracking
        self.available_models = set()
        self.last_health_check = {}
        
    def start_health_monitoring(self):
        """Start background health monitoring"""
        self.monitoring_active = True
        self.health_thread = threading.Thread(target=self._health_monitor_loop, daemon=True)
        self.health_thread.start()
        logger.info("🩺 Health monitoring started")
    
    def stop_health_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        if self.health_thread:
            self.health_thread.join(timeout=5)
        logger.info("🛑 Health monitoring stopped")
    
    def _health_monitor_loop(self):
        """Background health monitoring loop"""
        while self.monitoring_active:
            try:
                self.scan_available_models()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def scan_available_models(self) -> List[str]:
        """Scan for available Ollama models (MrLore pattern)"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                models = [model['name'] for model in models_data.get('models', [])]
                
                # Update availability tracking
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
        # Check if primary model is available
        if config.model in self.available_models:
            return True
        
        # Check fallback models
        if config.fallback_models:
            for fallback in config.fallback_models:
                if fallback in self.available_models:
                    logger.info(f"🔄 Using fallback {fallback} for {config.name}")
                    return True
        
        logger.error(f"❌ No viable model for {config.name}")
        return False
    
    def get_memory_hash(self, content: str) -> str:
        """Generate hash for content (MrLore pattern)"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def cache_conversation(self, topic: str, responses: List[str]):
        """Cache conversation for analysis"""
        cache_key = self.get_memory_hash(topic + str(time.time()))
        self.session_cache[cache_key] = {
            'topic': topic,
            'responses': responses,
            'timestamp': datetime.now().isoformat()
        }
        
        # Persist to disk
        cache_file = self.cache_dir / f"session_{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(self.session_cache[cache_key], f, indent=2)
    
    def cleanup_old_cache(self, max_age_hours: int = 24):
        """Clean up old cache files"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for cache_file in self.cache_dir.glob("session_*.json"):
            if cache_file.stat().st_mtime < cutoff_time.timestamp():
                cache_file.unlink()
                logger.info(f"🧹 Cleaned up old cache: {cache_file.name}")

class StableCouncilMember:
    """Stable council member with fallback and retry logic"""
    
    def __init__(self, config: CouncilMemberConfig, brain: MrLoreCouncilBrain):
        self.config = config
        self.brain = brain
        self.current_model = config.model
        self.consecutive_failures = 0
        self.last_success = datetime.now()
        
        # Request session for connection reuse
        self.session = requests.Session()
        
    def get_active_model(self) -> str:
        """Get the currently active model for this member"""
        # Check if primary model is available
        if self.config.model in self.brain.available_models:
            if self.current_model != self.config.model:
                logger.info(f"🔄 {self.config.name} switching back to primary model: {self.config.model}")
                self.current_model = self.config.model
            return self.current_model
        
        # Try fallback models
        if self.config.fallback_models:
            for fallback in self.config.fallback_models:
                if fallback in self.brain.available_models:
                    if self.current_model != fallback:
                        logger.info(f"🔄 {self.config.name} switching to fallback: {fallback}")
                        self.current_model = fallback
                    return self.current_model
        
        # No viable model found
        raise Exception(f"No viable model available for {self.config.name}")
    
    def respond(self, context: str, prompt: str) -> str:
        """Generate response with stability and retry logic"""
        for attempt in range(self.config.max_retries):
            try:
                active_model = self.get_active_model()
                
                # Build full prompt
                if context:
                    full_prompt = f"{context}\n\n{self.config.personality}\n\n{prompt}\n\n{self.config.name}:"
                else:
                    full_prompt = f"{self.config.personality}\n\n{prompt}\n\n{self.config.name}:"
                
                # Prepare request
                payload = {
                    "model": active_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 600,
                        "num_ctx": int(4096 * self.config.context_weight)
                    }
                }
                
                logger.info(f"🤔 {self.config.name} thinking with {active_model} (attempt {attempt + 1})")
                
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
                        self.consecutive_failures = 0
                        self.last_success = datetime.now()
                        logger.info(f"✅ {self.config.name} responded successfully")
                        return text
                    else:
                        raise Exception("Empty response")
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.consecutive_failures += 1
                logger.warning(f"⚠️ {self.config.name} attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"🔄 Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        # All attempts failed
        error_msg = f"❌ {self.config.name} failed all {self.config.max_retries} attempts"
        logger.error(error_msg)
        return f"[{self.config.name} temporarily unavailable - too many failures]"
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get member health status"""
        return {
            'name': self.config.name,
            'current_model': self.current_model,
            'consecutive_failures': self.consecutive_failures,
            'last_success': self.last_success.isoformat(),
            'healthy': self.consecutive_failures < 3
        }

class StableCouncilSystem:
    """Stable Council of 5 with MrLore intelligence"""
    
    def __init__(self):
        self.brain = MrLoreCouncilBrain()
        self.members: List[StableCouncilMember] = []
        self.conversation_history: List[str] = []
        
        # Default council configuration
        self.member_configs = [
            CouncilMemberConfig(
                name="Bob",
                model="qwen2.5:7b-instruct",
                personality="Strategic Analyst: Deep thinker who analyzes problems fundamentally",
                fallback_models=["llama3:8b", "phi3:3.8b"]
            ),
            CouncilMemberConfig(
                name="Sarah", 
                model="llama3:8b",
                personality="Knowledge Archivist: Comprehensive expert with well-researched information",
                fallback_models=["qwen2.5:7b-instruct", "dolphin3:8b"]
            ),
            CouncilMemberConfig(
                name="Quick",
                model="phi3:3.8b", 
                personality="Lightning Scout: Rapid-response specialist with concise insights",
                fallback_models=["llama3:8b", "qwen2.5:7b-instruct"],
                timeout=30  # Faster timeout for quick responses
            ),
            CouncilMemberConfig(
                name="Deep",
                model="dolphin3:8b",
                personality="Depth Philosopher: Explores implications and deeper meanings",
                fallback_models=["mistral-nemo:12b", "llama3:8b"]
            ),
            CouncilMemberConfig(
                name="Synthesis",
                model="mistral-nemo:12b",
                personality="Master Synthesizer: Combines perspectives into coherent conclusions",
                fallback_models=["qwen2.5:7b-instruct", "llama3:8b"],
                context_weight=1.2  # More context for synthesis
            )
        ]
        
    def initialize(self) -> bool:
        """Initialize the stable council system"""
        logger.info("🏛️ Initializing Stable Council System...")
        
        # Start health monitoring
        self.brain.start_health_monitoring()
        
        # Wait for initial model scan
        time.sleep(2)
        
        if not self.brain.available_models:
            logger.error("❌ No Ollama models available - cannot initialize council")
            return False
        
        # Initialize members
        for config in self.member_configs:
            if self.brain.validate_member_config(config):
                member = StableCouncilMember(config, self.brain)
                self.members.append(member)
                logger.info(f"✅ Initialized {config.name}")
            else:
                logger.warning(f"⚠️ Skipping {config.name} - no viable model")
        
        if len(self.members) < 2:
            logger.error("❌ Not enough viable council members")
            return False
        
        logger.info(f"🏛️ Council initialized with {len(self.members)} members")
        return True
    
    def conduct_session(self, topic: str, max_rounds: int = 3) -> Dict[str, Any]:
        """Conduct a stable council session"""
        if not self.members:
            return {"error": "Council not initialized"}
        
        logger.info(f"🏛️ Starting council session: {topic}")
        session_start = time.time()
        
        responses = []
        context = f"Council Topic: {topic}\n\nPrevious Discussion:\n" + "\n".join(self.conversation_history[-10:])
        
        # Conduct rounds
        for round_num in range(1, max_rounds + 1):
            logger.info(f"🔄 Round {round_num}")
            round_responses = []
            
            for member in self.members:
                try:
                    prompt = f"Round {round_num}: Discuss '{topic}'. Consider others' perspectives and build upon them."
                    response = member.respond(context, prompt)
                    
                    if not response.startswith("[") or "unavailable" not in response:
                        round_responses.append(f"{member.config.name}: {response}")
                        logger.info(f"✅ {member.config.name} contributed")
                    else:
                        logger.warning(f"⚠️ {member.config.name} unavailable this round")
                
                except Exception as e:
                    logger.error(f"❌ {member.config.name} error: {e}")
            
            responses.extend(round_responses)
            
            # Update context for next round
            if round_responses:
                context += "\n\n" + "\n".join(round_responses)
        
        # Cache the session
        self.brain.cache_conversation(topic, responses)
        
        # Add to conversation history
        self.conversation_history.extend(responses)
        
        # Trim history to prevent bloat
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-30:]
        
        session_duration = time.time() - session_start
        
        return {
            "topic": topic,
            "responses": responses,
            "participants": len([m for m in self.members if m.consecutive_failures < 3]),
            "duration": session_duration,
            "success": len(responses) > 0
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        member_status = [member.get_health_status() for member in self.members]
        healthy_members = sum(1 for status in member_status if status['healthy'])
        
        return {
            "system_health": healthy_members / len(self.members) if self.members else 0,
            "available_models": list(self.brain.available_models),
            "members": member_status,
            "conversation_length": len(self.conversation_history),
            "cache_sessions": len(self.brain.session_cache),
            "monitoring_active": self.brain.monitoring_active
        }
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down Stable Council System...")
        
        # Stop health monitoring
        self.brain.stop_health_monitoring()
        
        # Clean up resources
        for member in self.members:
            member.session.close()
        
        # Clean old cache
        self.brain.cleanup_old_cache()
        
        logger.info("✅ Council shutdown complete")

def main():
    """CLI interface for stable council"""
    import sys
    
    council = StableCouncilSystem()
    
    if not council.initialize():
        print("❌ Failed to initialize council system")
        sys.exit(1)
    
    print("🏛️ STABLE COUNCIL OF 5 - READY")
    print("=" * 50)
    print("Commands:")
    print("  discuss <topic>    - Start council discussion")
    print("  status            - Show system status") 
    print("  health            - Show member health")
    print("  history           - Show conversation history")
    print("  exit              - Shutdown council")
    print()
    
    try:
        while True:
            command = input("Council> ").strip()
            
            if not command:
                continue
            elif command.lower() in ['exit', 'quit']:
                break
            elif command.startswith('discuss '):
                topic = command[8:].strip()
                if topic:
                    result = council.conduct_session(topic)
                    print(f"\n📊 Session Results:")
                    print(f"Topic: {result['topic']}")
                    print(f"Participants: {result['participants']}")
                    print(f"Duration: {result['duration']:.1f}s")
                    print(f"Success: {'✅' if result['success'] else '❌'}")
                    print("\n💬 Responses:")
                    for response in result['responses']:
                        print(f"  {response}")
                else:
                    print("❌ Please provide a topic")
            elif command == 'status':
                status = council.get_system_status()
                print(f"\n🎯 System Status:")
                print(f"Health: {status['system_health']:.2%}")
                print(f"Available Models: {len(status['available_models'])}")
                print(f"Active Members: {len([m for m in status['members'] if m['healthy']])}/{len(status['members'])}")
                print(f"Monitoring: {'✅' if status['monitoring_active'] else '❌'}")
            elif command == 'health':
                status = council.get_system_status()
                print("\n🩺 Member Health:")
                for member in status['members']:
                    health = "✅" if member['healthy'] else "❌"
                    print(f"  {health} {member['name']}: {member['current_model']} (failures: {member['consecutive_failures']})")
            elif command == 'history':
                print(f"\n📚 Conversation History ({len(council.conversation_history)} entries):")
                for entry in council.conversation_history[-10:]:
                    print(f"  {entry}")
            else:
                print("❌ Unknown command. Type 'exit' to quit.")
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
    finally:
        council.shutdown()

if __name__ == "__main__":
    main()
