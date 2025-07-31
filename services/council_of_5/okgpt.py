#!/usr/bin/env python3
"""
OKGpt - AI Council Hub
The legendary multi-LLM council system - RESURRECTED! 🔥⚡
"""

import requests
import json
import time
from typing import List, Dict
import sys

class AICouncilMember:
    def __init__(self, name: str, model: str, personality: str = ""):
        self.name = name
        self.model = model
        self.personality = personality
        self.base_url = "http://localhost:11434/api/generate"
    
    def respond(self, conversation_history: str, user_input: str) -> str:
        """Get response from this council member"""
        
        # Build the full context
        full_context = f"{conversation_history}\n\nUser: {user_input}"
        
        if self.personality:
            system_prompt = f"You are {self.name}, {self.personality}. Respond as this character would."
            full_prompt = f"{system_prompt}\n\n{full_context}\n\n{self.name}:"
        else:
            full_prompt = f"{full_context}\n\n{self.name}:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1000,
                "num_ctx": 4096
            }
        }
        
        try:
            print(f"🤔 {self.name} is thinking...")
            response = requests.post(self.base_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Error: No response').strip()
            else:
                return f"Error: HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Error connecting to {self.name}: {str(e)}"

class OKGptCouncil:
    def __init__(self):
        self.conversation_history = []
        self.council_members = []
        self.setup_council()
    
    def setup_council(self):
        """Initialize the AI council members"""
        self.council_members = [
            AICouncilMember(
                name="Bob", 
                model="qwen3:8b",
                personality="a strategic thinker who analyzes problems deeply and provides reasoned solutions"
            ),
            AICouncilMember(
                name="Rod", 
                model="dolphin3:8b",
                personality="a balanced analyst who considers multiple perspectives and practical implications"
            ),
            AICouncilMember(
                name="Sarah", 
                model="llama3:latest",
                personality="a knowledgeable generalist who provides clear, comprehensive responses"
            ),
            AICouncilMember(
                name="Quick", 
                model="tinydolphin:latest",
                personality="a rapid-response specialist who gives concise, actionable insights"
            )
        ]
    
    def get_conversation_context(self) -> str:
        """Build the full conversation history string"""
        return "\n".join(self.conversation_history)
    
    def add_to_history(self, speaker: str, message: str):
        """Add an exchange to conversation history"""
        self.conversation_history.append(f"{speaker}: {message}")
    
    def consult_individual(self, member_name: str, user_input: str):
        """Consult a specific council member"""
        member = next((m for m in self.council_members if m.name.lower() == member_name.lower()), None)
        
        if not member:
            print(f"❌ Council member '{member_name}' not found!")
            print(f"Available members: {', '.join([m.name for m in self.council_members])}")
            return
        
        print(f"\n🎯 Consulting {member.name} individually...")
        
        context = self.get_conversation_context()
        response = member.respond(context, user_input)
        
        print(f"\n🗣️  **{member.name}:** {response}\n")
        
        # Add to history
        self.add_to_history("User", user_input)
        self.add_to_history(member.name, response)
    
    def consult_council(self, user_input: str, selected_members: List[str] = None):
        """Consult the full council or selected members"""
        
        if selected_members:
            members = [m for m in self.council_members if m.name in selected_members]
        else:
            members = self.council_members
        
        print(f"\n🏛️  Consulting the council: {', '.join([m.name for m in members])}")
        print("=" * 60)
        
        # Add user input to history first
        self.add_to_history("User", user_input)
        
        # Get responses in order
        for member in members:
            context = self.get_conversation_context()
            response = member.respond(context, user_input)
            
            print(f"\n🗣️  **{member.name}:** {response}")
            print("-" * 40)
            
            # Add this member's response to history for next member to see
            self.add_to_history(member.name, response)
        
        print("\n✅ Initial council consultation complete!")
        
        # Ask if they want continuous dialogue
        continuous = input("\n🔄 Enable continuous AI-to-AI dialogue? (y/n): ").strip().lower()
        if continuous == 'y':
            self.continuous_dialogue(user_input, selected_members or self.council_members)
        else:
            print()
    
    def continuous_dialogue(self, original_topic: str, members: List[AICouncilMember]):
        """Enable continuous AI-to-AI dialogue"""
        print(f"\n🔄 **CONTINUOUS DIALOGUE MODE ACTIVATED**")
        print("The council will now continue discussing amongst themselves...")
        print("You'll be prompted to continue after each round\n")
        
        round_count = 1
        max_rounds = 20  # Prevent infinite loops
        
        while round_count <= max_rounds:
            print(f"\n--- Round {round_count} of Continuous Dialogue ---")
            
            # Each member responds to the ongoing conversation
            for member in members:
                context = self.get_conversation_context()
                
                # Create a prompt for continued dialogue
                continued_prompt = f"Continue this discussion. Respond to what others have said so far about: {original_topic}"
                
                print(f"\n🗣️ **{member.name} continues:**")
                response = member.respond(context, continued_prompt)
                print(f"{response}")
                print("-" * 40)
                
                # Add to history
                self.add_to_history(member.name, response)
            
            # Check if conversation is winding down
            recent_responses = self.conversation_history[-len(members):]
            if self.should_end_dialogue(recent_responses):
                print("\n🏁 Council has reached natural conclusion")
                break
            
            # Ask user if they want to continue
            print(f"\n🔄 Round {round_count} complete. Continue? (y/n/auto): ", end='')
            choice = input().strip().lower()
            
            if choice == 'n':
                print("\n⏹️ Continuous dialogue stopped by user")
                break
            elif choice == 'auto':
                print("🤖 Switching to auto mode - will run until natural conclusion")
                # Continue without asking
            elif choice != 'y' and choice != 'auto':
                print("\n⏹️ Continuous dialogue stopped")
                break
                
            round_count += 1
        
        if round_count > max_rounds:
            print(f"\n⏰ Reached maximum rounds ({max_rounds})")
        
        print("\n🔄 Continuous dialogue ended\n")
    
    def should_end_dialogue(self, recent_responses: List[str]) -> bool:
        """Check if the dialogue should naturally end"""
        # Simple heuristic: if responses are getting shorter or repetitive
        end_phrases = ["i agree", "nothing more to add", "well said", "that concludes", "no further"]
        
        for response in recent_responses:
            for phrase in end_phrases:
                if phrase in response.lower():
                    return True
        return False
    
    def show_help(self):
        """Show available commands"""
        print("""
🏛️  **OKGpt Council Commands:**

**Individual Consultation:**
- ok bob [question]     - Consult Bob (Strategic Thinker)
- ok rod [question]     - Consult Rod (Balanced Analyst)  
- ok sarah [question]   - Consult Sarah (Generalist)
- ok quick [question]   - Consult Quick (Rapid Response)

**Council Consultation:**
- council [question]    - Full council responds in order
- select bob,rod [q]    - Selected members only

**Continuous Dialogue:**
After any council consultation, you can enable continuous AI-to-AI dialogue
where the council members keep talking to each other about the topic!

**Utility:**
- history              - Show conversation history
- clear                - Clear conversation history
- members              - List council members
- help                 - Show this help
- exit                 - Quit OKGpt

**Examples:**
- ok bob What's the best strategy for learning Python?
- council How should I approach building a mobile app?
- select bob,sarah What are the pros and cons of remote work?

**New Feature:** After any council consultation, you'll be asked if you want 
continuous dialogue where the AIs keep discussing the topic amongst themselves!
""")
    
    def show_history(self):
        """Display conversation history"""
        if not self.conversation_history:
            print("📝 No conversation history yet.")
            return
        
        print("\n📝 **Conversation History:**")
        print("=" * 50)
        for entry in self.conversation_history:
            print(entry)
        print("=" * 50)
    
    def show_members(self):
        """Display council members"""
        print("\n👥 **Council Members:**")
        for member in self.council_members:
            print(f"  🤖 {member.name} ({member.model}) - {member.personality}")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️  Conversation history cleared!")
    
    def run(self):
        """Main OKGpt loop"""
        print("🔥⚡ **OKGPT COUNCIL - LEGENDARY AI HUB** ⚡🔥")
        print("The multi-LLM council system has been RESURRECTED!")
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
                
                elif user_input.lower().startswith('ok '):
                    # Individual consultation: "ok bob what should I do?"
                    parts = user_input[3:].split(' ', 1)
                    if len(parts) >= 2:
                        member_name, question = parts[0], parts[1]
                        self.consult_individual(member_name, question)
                    else:
                        print("❌ Usage: ok [member] [question]")
                
                elif user_input.lower().startswith('council '):
                    # Full council consultation
                    question = user_input[8:]
                    self.consult_council(question)
                
                elif user_input.lower().startswith('select '):
                    # Selected members: "select bob,rod what do you think?"
                    parts = user_input[7:].split(' ', 1)
                    if len(parts) >= 2:
                        members_str, question = parts[0], parts[1]
                        selected = [m.strip().title() for m in members_str.split(',')]
                        self.consult_council(question, selected)
                    else:
                        print("❌ Usage: select member1,member2 [question]")
                
                else:
                    # Default to full council
                    print("🤔 Consulting full council...")
                    self.consult_council(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Council dismissed! OKGpt shutting down...")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Launch OKGpt Council"""
    council = OKGptCouncil()
    council.run()

if __name__ == "__main__":
    main()
