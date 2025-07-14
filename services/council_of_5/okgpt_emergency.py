#!/usr/bin/env python3
"""
OKGpt - Resource-Optimized AI Council
Emergency patch for system stability - lightweight mode enabled! ⚡🛡️
"""

import requests
import json
import time
import os
import sys
import subprocess
from typing import List, Dict, Optional
from datetime import datetime

# Resource monitoring functions
def check_memory_usage() -> float:
    """Check current memory usage percentage"""
    try:
        result = subprocess.check_output("free -t | awk 'NR==2 {print $3/$2*100}'", shell=True)
        return float(result.decode().strip())
    except:
        return 0.0

def check_swap_usage() -> float:
    """Check current swap usage percentage"""
    try:
        result = subprocess.check_output("free -t | awk 'NR==3 {print $3/$2*100}'", shell=True)
        return float(result.decode().strip())
    except:
        return 0.0

def clear_swap():
    """Emergency swap clearing"""
    print("🔄 Clearing swap space...")
    os.system("sudo swapoff -a && sudo swapon -a")
    print("✅ Swap cleared!")

def kill_resource_hogs():
    """Terminate resource-intensive processes"""
    print("🔫 Killing resource hogs...")
    os.system("sudo pkill -f snapd")
    os.system("sudo systemctl stop snapd > /dev/null 2>&1")
    print("✅ Resource hogs terminated!")

class ResourceAwareMember:
    def __init__(self, name: str, model: str, personality: str, weight: float):
        self.name = name
        self.model = model
        self.personality = personality
        self.weight = weight  # Resource impact score (0.1-1.0)
        self.base_url = "http://localhost:11434/api/generate"
    
    def safe_respond(self, conversation_history: str, user_input: str) -> str:
        """Get response with resource monitoring"""
        mem_usage = check_memory_usage()
        swap_usage = check_swap_usage()
        
        # Emergency resource handling
        if mem_usage > 90 or swap_usage > 70:
            print(f"🚨 CRITICAL RESOURCE USAGE: MEM {mem_usage:.1f}% SWAP {swap_usage:.1f}%")
            if "light" not in self.model:
                return f"{self.name} is offline due to system overload. Please use lightweight mode."
        
        # Build context with resource awareness
        context = f"System Status: Memory {mem_usage:.1f}%, Swap {swap_usage:.1f}%\n{conversation_history}"
        
        full_prompt = (
            f"Current Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"You are {self.name}, {self.personality}. Respond concisely.\n\n"
            f"{context}\n\nUser: {user_input}\n\n{self.name}:"
        )
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 400,  # Reduced output length
                "num_ctx": 2048     # Reduced context window
            }
        }
        
        try:
            print(f"🤔 {self.name} is thinking...")
            response = requests.post(self.base_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response').strip()
            return f"Error: HTTP {response.status_code}"
        except requests.exceptions.RequestException:
            return f"{self.name} is unavailable. Try again later."
    
    def is_available(self) -> bool:
        """Check if model can be safely loaded"""
        mem_usage = check_memory_usage()
        swap_usage = check_swap_usage()
        
        # Only allow heavy models if resources permit
        if self.weight > 0.7 and (mem_usage > 80 or swap_usage > 60):
            return False
        return True

class OKGptCouncil:
    def __init__(self):
        self.conversation_history = []
        self.council_members = []
        self.lightweight_mode = True  # Default to safe mode
        self.setup_council()
        self.resource_check_interval = 3  # Resource checks every 3 commands
        self.command_count = 0
        
        # Emergency resource cleanup
        kill_resource_hogs()
        clear_swap()
        
        print("🛡️ Resource protection measures activated!")
    
    def setup_council(self):
        """Initialize optimized council members"""
        if self.lightweight_mode:
            print("⚡ LIGHTWEIGHT MODE ACTIVATED - Using minimal models")
            self.council_members = [
                ResourceAwareMember(
                    name="Quick", 
                    model="phi3:3.8b",
                    personality="Lightning Scout: Rapid-response specialist",
                    weight=0.3
                ),
                ResourceAwareMember(
                    name="Rod", 
                    model="dolphin3:8b",
                    personality="Balanced Moderator: Practical analyst",
                    weight=0.6
                ),
                ResourceAwareMember(
                    name="Tiny", 
                    model="tinydolphin:latest",
                    personality="Mini Analyst: Compact perspective provider",
                    weight=0.2
                )
            ]
        else:
            print("💪 FULL COUNCIL MODE - Use with caution")
            self.council_members = [
                ResourceAwareMember(
                    name="Bob", 
                    model="qwen2.5:7b-instruct",
                    personality="Strategic Analyst",
                    weight=0.8
                ),
                ResourceAwareMember(
                    name="Sarah", 
                    model="llama3:8b",
                    personality="Knowledge Archivist",
                    weight=0.7
                ),
                ResourceAwareMember(
                    name="Quick", 
                    model="phi3:3.8b",
                    personality="Lightning Scout",
                    weight=0.3
                ),
                ResourceAwareMember(
                    name="Rod", 
                    model="dolphin3:8b",
                    personality="Balanced Moderator",
                    weight=0.6
                )
            ]
    
    def toggle_mode(self):
        """Switch between lightweight and full modes"""
        self.lightweight_mode = not self.lightweight_mode
        mode = "LIGHTWEIGHT" if self.lightweight_mode else "FULL"
        print(f"🔄 Switched to {mode} MODE")
        self.setup_council()
    
    def check_resources(self):
        """Periodic resource monitoring"""
        self.command_count += 1
        if self.command_count % self.resource_check_interval == 0:
            mem = check_memory_usage()
            swap = check_swap_usage()
            print(f"📊 Resource Check: MEM {mem:.1f}% | SWAP {swap:.1f}%")
            
            if mem > 85 or swap > 75:
                print("⚠️ Switching to lightweight mode for safety")
                self.lightweight_mode = True
                self.setup_council()
    
    def get_conversation_context(self, max_lines: int = 10) -> str:
        """Build conversation history with limited lines"""
        return "\n".join(self.conversation_history[-max_lines:])
    
    def add_to_history(self, speaker: str, message: str):
        """Add exchange with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_history.append(f"[{timestamp}] {speaker}: {message}")
    
    def consult_individual(self, member_name: str, user_input: str):
        """Consult a specific council member"""
        self.check_resources()
        
        member = next((m for m in self.council_members 
                      if m.name.lower() == member_name.lower() and m.is_available()), None)
        
        if not member:
            print(f"❌ {member_name} unavailable in current resource conditions")
            print(f"Available members: {', '.join([m.name for m in self.council_members if m.is_available()])}")
            return
        
        print(f"\n🎯 Consulting {member.name}...")
        
        context = self.get_conversation_context()
        response = member.safe_respond(context, user_input)
        
        print(f"\n🗣️  **{member.name}:** {response}\n")
        self.add_to_history("User", user_input)
        self.add_to_history(member.name, response)
    
    def consult_council(self, user_input: str, selected_members: List[str] = None):
        """Resource-optimized council consultation"""
        self.check_resources()
        
        # Get available members
        available_members = [m for m in self.council_members if m.is_available()]
        
        if not available_members:
            print("🚨 All council members offline due to resource constraints")
            return
        
        if selected_members:
            members = [m for m in available_members if m.name in selected_members]
        else:
            members = available_members
        
        if not members:
            print("❌ No selected members available")
            return
        
        print(f"\n🏛️  Consulting: {', '.join([m.name for m in members])}")
        print("=" * 60)
        
        # Add user input to history
        self.add_to_history("User", user_input)
        context = self.get_conversation_context()
        
        # Get responses in order with safety delays
        for member in members:
            response = member.safe_respond(context, user_input)
            print(f"\n🗣️  **{member.name}:** {response}")
            print("-" * 60)
            self.add_to_history(member.name, response)
            
            # Update context for next member
            context = self.get_conversation_context()
            
            # Add safety delay between members
            time.sleep(member.weight * 2)
        
        print("\n✅ Council consultation complete!")
    
    def show_help(self):
        """Show available commands"""
        print("""
🛡️  **Resource-Optimized OKGpt Commands:**

**Individual Consultation:**
- ok [member] [question] - Consult specific member

**Council Consultation:**
- council [question]    - Available council members
- select [members] [q]  - Selected members only

**System Management:**
- mode                 - Toggle lightweight/full mode
- resources            - Show current resource usage
- clearswap            - Emergency swap clearing
- killhogs             - Terminate resource hogs
- history              - Conversation history
- clear                - Clear history
- members              - List available members
- help                 - Show this help
- exit                 - Quit OKGpt

**Lightweight Members:**
- Quick (phi3:3.8b)    - Lightning Scout
- Rod (dolphin3:8b)    - Balanced Moderator
- Tiny (tinydolphin)   - Mini Analyst

**Full Mode Members:**
- Bob, Sarah, Quick, Rod

**Examples:**
- ok quick What's the weather?
- council How can we optimize resources?
- select quick,tiny Simple question
""")

    def show_members(self):
        """Display available council members"""
        print("\n👥 **ACTIVE COUNCIL MEMBERS:**")
        for member in self.council_members:
            status = "✅ Available" if member.is_available() else "❌ Resource-limited"
            print(f"  {status} - {member.name} ({member.model})")
    
    def show_resources(self):
        """Display current resource usage"""
        mem = check_memory_usage()
        swap = check_swap_usage()
        print(f"\n📊 SYSTEM RESOURCES:")
        print(f"  Memory Usage: {mem:.1f}%")
        print(f"  Swap Usage:   {swap:.1f}%")
        print(f"  Council Mode: {'LIGHTWEIGHT' if self.lightweight_mode else 'FULL'}")
        
        if mem > 80 or swap > 70:
            print("\n🚨 WARNING: High resource usage - recommend:")
            print("  - Run 'clearswap'")
            print("  - Run 'killhogs'")
            print("  - Switch to lightweight mode")

    # ... (show_history and clear_history remain similar)

    def run(self):
        """Main OKGpt loop with resource protection"""
        print("⚡🛡️ **RESOURCE-AWARE OKGPT COUNCIL** 🛡️⚡")
        print("Emergency stability measures activated!")
        print("Type 'help' for commands or 'exit' to quit.\n")
        
        while True:
            try:
                user_input = input("🎯 OKGpt> ").strip()
                
                if not user_input:
                    continue
                
                # Parse commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Council dismissed! OKGpt shutting down...")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                
                elif user_input.lower() == 'history':
                    self.show_history()
                
                elif user_input.lower() == 'clear':
                    self.clear_history()
                
                elif user_input.lower() == 'members':
                    self.show_members()
                
                elif user_input.lower() == 'resources':
                    self.show_resources()
                
                elif user_input.lower() == 'clearswap':
                    clear_swap()
                
                elif user_input.lower() == 'killhogs':
                    kill_resource_hogs()
                
                elif user_input.lower() == 'mode':
                    self.toggle_mode()
                
                elif user_input.lower().startswith('ok '):
                    parts = user_input[3:].split(' ', 1)
                    if len(parts) >= 2:
                        member_name, question = parts[0], parts[1]
                        self.consult_individual(member_name, question)
                    else:
                        print("❌ Usage: ok [member] [question]")
                
                elif user_input.lower().startswith('council '):
                    question = user_input[8:]
                    self.consult_council(question)
                
                elif user_input.lower().startswith('select '):
                    parts = user_input[7:].split(' ', 1)
                    if len(parts) >= 2:
                        members_str, question = parts[0], parts[1]
                        selected = [m.strip().title() for m in members_str.split(',')]
                        self.consult_council(question, selected)
                    else:
                        print("❌ Usage: select member1,member2 [question]")
                
                else:
                    print("🤔 Consulting available council members...")
                    self.consult_council(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Council dismissed! OKGpt shutting down...")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Launch Resource-Optimized OKGpt Council"""
    council = OKGptCouncil()
    council.run()

if __name__ == "__main__":
    # Emergency resource preparation
    os.system("sudo swapoff -a && sudo swapon -a")
    os.system("sudo pkill -f snapd")
    os.system("sudo systemctl stop snapd > /dev/null 2>&1")
    main()