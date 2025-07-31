#!/usr/bin/env python3
"""
OKGpt - ULTIMATE AI Council Hub
The legendary multi-LLM council system - RESURRECTED & UPGRADED! 🔥⚡
"""

import requests
import json
import time
import re
from typing import List, Dict, Optional
import sys
from datetime import datetime

class DiplomaticMistral:
    """Specialized class for Mistral's diplomatic synthesis"""
    def __init__(self):
        self.name = "Mistral"
        self.model = "mistral-nemo:12b"
        self.base_url = "http://localhost:11434/api/generate"
        self.synthesis_template = """You are the Steward of Coherence. The council has spoken about: "{topic}"

Council Discussion:
{discussion}

Your task:
1. Synthesize key insights from ALL perspectives
2. Resolve contradictions where possible
3. Propose 1-3 actionable next steps
4. Keep response under 300 words

Format your response:
### Synthesis
[Concise summary of main points]

### Resolution
[How conflicting views complement each other]

### Recommended Path
1. [Actionable step 1]
2. [Actionable step 2]"""
    
    def synthesize(self, topic: str, discussion: str) -> str:
        """Generate diplomatic synthesis"""
        prompt = self.synthesis_template.format(topic=topic, discussion=discussion)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "top_p": 0.85,
                "max_tokens": 800,
                "num_ctx": 6144  # Extra context for synthesis
            }
        }
        
        try:
            print("\n🧙 Mistral synthesizing council wisdom...")
            response = requests.post(self.base_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Synthesis failed').strip()
            return "Error: Synthesis HTTP error"
        except requests.exceptions.RequestException:
            return "Error: Mistral unavailable for synthesis"

class AICouncilMember:
    def __init__(self, name: str, model: str, personality: str = ""):
        self.name = name
        self.model = model
        self.personality = personality
        self.base_url = "http://localhost:11434/api/generate"
        # Context weighting based on role importance
        self.context_weight = {
            "Mistral": 1.0,
            "Bob": 0.9,
            "Sarah": 0.8,
            "Rod": 0.8,
            "Quick": 0.6
        }.get(name, 0.7)
    
    def respond(self, conversation_history: str, user_input: str) -> str:
        """Get response from this council member"""
        # Weighted context based on member's role
        weighted_context = self._weight_context(conversation_history)
        
        full_context = f"{weighted_context}\n\nUser: {user_input}"
        
        if self.personality:
            system_prompt = f"Current Date: {datetime.now().strftime('%Y-%m-%d')}\nYou are {self.name}, {self.personality}."
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
                "max_tokens": 800,
                "num_ctx": int(4096 * self.context_weight)
            }
        }
        
        try:
            print(f"🤔 {self.name} is thinking...")
            response = requests.post(self.base_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Error: No response').strip()
            return f"Error: HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
    
    def _weight_context(self, history: str) -> str:
        """Apply context weighting based on member role"""
        lines = history.split('\n')
        if not lines:
            return ""
        
        # Keep all context for Mistral, reduce for others
        if self.context_weight >= 0.9:
            return history
        
        # Preserve recent exchanges more completely
        recent_lines = lines[-10:]
        older_lines = lines[:-10]
        
        # Downsample older context
        if older_lines:
            keep_every = max(1, int(1 / self.context_weight))
            downsampled = older_lines[::keep_every]
            return "\n".join(downsampled + recent_lines)
        return history

class OKGptCouncil:
    def __init__(self):
        self.conversation_history = []
        self.council_members = []
        self.steward = DiplomaticMistral()
        self.setup_council()
    
    def setup_council(self):
        """Initialize the ULTIMATE council members"""
        self.council_members = [
            AICouncilMember(
                name="Bob", 
                model="qwen2.5:7b-instruct",
                personality="Strategic Analyst: Deep thinker who analyzes problems fundamentally and provides framework-based solutions"
            ),
            AICouncilMember(
                name="Sarah", 
                model="llama3:8b",
                personality="Knowledge Archivist: Comprehensive expert who provides well-researched information with references"
            ),
            AICouncilMember(
                name="Quick", 
                model="phi3:3.8b",
                personality="Lightning Scout: Rapid-response specialist who gives concise, actionable insights and alternatives"
            ),
            AICouncilMember(
                name="Rod", 
                model="dolphin3:8b",
                personality="Balanced Moderator: Practical analyst who considers multiple perspectives and real-world implications"
            ),
            AICouncilMember(
                name="Mistral", 
                model="mistral-nemo:12b",
                personality="Diplomatic Steward: Synthesizes perspectives into coherent wisdom, identifies consensus, and proposes paths forward"
            )
        ]
    
    def get_conversation_context(self, max_lines: int = 30) -> str:
        """Build weighted conversation history"""
        return "\n".join(self.conversation_history[-max_lines:])
    
    def add_to_history(self, speaker: str, message: str):
        """Add exchange with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_history.append(f"[{timestamp}] {speaker}: {message}")
    
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
        
        # Special Mistral synthesis after individual consultation
        if member_name != "Mistral":
            self._offer_mistral_synthesis(user_input, response)
    
    def _offer_mistral_synthesis(self, topic: str, response: str):
        """Offer Mistral synthesis after individual consultation"""
        choice = input("\n🧙 Would you like Mistral to synthesize this? (y/n): ").strip().lower()
        if choice == 'y':
            synthesis = self.steward.synthesize(topic, f"{topic}\n\n{response}")
            print(f"\n✨ **Mistral Synthesis:** {synthesis}\n")
            self.add_to_history("Mistral", f"SYNTHESIS: {synthesis}")
    
    def consult_council(self, user_input: str, selected_members: List[str] = None):
        """Consult the council with Mistral synthesis"""
        if selected_members:
            members = [m for m in self.council_members if m.name in selected_members]
        else:
            members = self.council_members
        
        # Ensure Mistral is always last
        if "Mistral" in [m.name for m in members]:
            members.sort(key=lambda m: 1 if m.name == "Mistral" else 0)
        
        print(f"\n🏛️  Consulting: {', '.join([m.name for m in members])}")
        print("=" * 60)
        
        # Add user input to history
        self.add_to_history("User", user_input)
        context = self.get_conversation_context()
        
        # Collect responses for synthesis
        responses = []
        
        # Get responses in order
        for member in members:
            response = member.respond(context, user_input)
            print(f"\n🗣️  **{member.name}:** {response}")
            print("-" * 60)
            
            # Add to history
            self.add_to_history(member.name, response)
            responses.append(f"{member.name}: {response}")
            
            # Update context for next member
            context = self.get_conversation_context()
        
        # Mistral synthesis for council discussions
        if len(members) > 1:
            discussion_block = "\n\n".join(responses)
            synthesis = self.steward.synthesize(user_input, discussion_block)
            print(f"\n✨ **Mistral Synthesis:** {synthesis}")
            self.add_to_history("Mistral", f"COUNCIL SYNTHESIS: {synthesis}")
        
        print("\n✅ Council consultation complete!")
        
        # Continuous dialogue option
        if len(members) > 1:
            continuous = input("\n🔄 Enable continuous AI dialogue? (y/n): ").strip().lower()
            if continuous == 'y':
                self.continuous_dialogue(user_input, members)
    
    def continuous_dialogue(self, original_topic: str, members: List[AICouncilMember], max_rounds: int = 5):
        """Enhanced continuous dialogue with intermediate synthesis"""
        print(f"\n🔄 **CONTINUOUS DIALOGUE MODE ACTIVATED** (Max {max_rounds} rounds)")
        
        for round_num in range(1, max_rounds + 1):
            print(f"\n--- Round {round_num} ---")
            context = self.get_conversation_context()
            
            # Collect responses for this round
            round_responses = []
            
            for member in members:
                # Create a prompt for continued dialogue
                continued_prompt = (
                    f"Continue the discussion about: {original_topic}. "
                    f"Consider others' perspectives and build upon them."
                )
                
                print(f"\n🗣️ **{member.name}:**")
                response = member.respond(context, continued_prompt)
                print(f"{response}")
                print("-" * 40)
                
                # Add to history
                self.add_to_history(member.name, f"[Round {round_num}] {response}")
                round_responses.append(f"{member.name}: {response}")
                
                # Update context
                context = self.get_conversation_context()
            
            # Intermediate Mistral synthesis every 2 rounds
            if round_num % 2 == 0 and "Mistral" in [m.name for m in members]:
                discussion_block = "\n\n".join(round_responses)
                synthesis = self.steward.synthesize(
                    f"{original_topic} (Round {round_num})", 
                    discussion_block
                )
                print(f"\n✨ **Mistral Interim Synthesis:** {synthesis}")
                self.add_to_history("Mistral", f"INTERIM SYNTHESIS: {synthesis}")
            
            # Check for natural conclusion
            if self.should_end_dialogue(round_responses):
                print("\n🏁 Council has reached natural conclusion")
                break
            
            # Continue prompt
            if round_num < max_rounds:
                cont = input(f"\n↪️ Continue to round {round_num+1}? (y/n): ").strip().lower()
                if cont != 'y':
                    break
        
        # Final synthesis
        if "Mistral" in [m.name for m in members]:
            full_discussion = "\n\n".join(
                f"[Round {i}] {resp}" for i, resp in enumerate(self.conversation_history[-len(members)*round_num:], 1)
            )
            synthesis = self.steward.synthesize(original_topic, full_discussion)
            print(f"\n✨ **Mistral Final Synthesis:** {synthesis}")
            self.add_to_history("Mistral", f"FINAL SYNTHESIS: {synthesis}")
        
        print("\n🔄 Continuous dialogue ended\n")
    
    def should_end_dialogue(self, responses: List[str]) -> bool:
        """Improved conclusion detection"""
        consensus_phrases = [
            "consensus", "agreement", "conclusion", "settled", 
            "no further", "aligned", "unified"
        ]
        
        conflict_phrases = [
            "disagree", "contradict", "opposing", "conflict", 
            "differing", "contrary", "irreconcilable"
        ]
        
        consensus_count = sum(1 for r in responses 
                            if any(p in r.lower() for p in consensus_phrases))
        conflict_count = sum(1 for r in responses 
                           if any(p in r.lower() for p in conflict_phrases))
        
        # High consensus indicates conclusion
        if consensus_count >= len(responses) * 0.75:
            return True
        
        # High conflict without resolution also suggests conclusion
        if conflict_count >= len(responses) * 0.6 and consensus_count < 2:
            return True
            
        return False

    # ... (show_help, show_history, show_members, clear_history methods remain similar but updated for new members)

    def show_help(self):
        """Show available commands"""
        print("""
🏛️  **ULTIMATE OKGpt Council Commands:**

**Individual Consultation:**
- ok bob [question]     - Consult Bob (Strategic Analyst)
- ok sarah [question]   - Consult Sarah (Knowledge Archivist)  
- ok quick [question]   - Consult Quick (Lightning Scout)
- ok rod [question]     - Consult Rod (Balanced Moderator)
- ok mistral [question] - Consult Mistral (Diplomatic Steward)

**Council Consultation:**
- council [question]    - Full council with Mistral synthesis
- select bob,rod [q]    - Selected members with synthesis

**Continuous Dialogue:**
After council consultation, enable multi-round AI dialogue
with intermediate Mistral synthesis every 2 rounds!

**Utility:**
- history              - Show conversation history
- clear                - Clear conversation history
- members              - List council members
- help                 - Show this help
- exit                 - Quit OKGpt

**Examples:**
- ok bob What's the optimal AI collaboration framework?
- council How should we approach AGI safety?
- select sarah,mistral What are the ethical implications of LLMs?
""")

    def show_members(self):
        """Display council members"""
        print("\n👑 **ULTIMATE COUNCIL MEMBERS:**")
        for member in self.council_members:
            print(f"  🌟 {member.name} ({member.model}) - {member.personality}")
        print("\n⚡ **Diplomatic Steward:** Mistral provides synthesis after every consultation!")

    # ... (run method remains mostly the same)

    def run(self):
        """Main OKGpt loop"""
        print("🔥⚡ **OKGPT COUNCIL - LEGENDARY AI HUB** ⚡🔥")
        print("⚔️ ULTIMATE COUNCIL ACTIVATED WITH DIPLOMATIC STEWARD ⚔️")
        print("Type 'help' for commands or 'exit' to quit.\n")
        
        while True:
            try:
                user_input = input("🎯 OKGpt> ").strip()
                
                if not user_input:
                    continue
                
                # Parse commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👑 Council dismissed! OKGpt shutting down...")
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
                    print("🤔 Consulting full council with synthesis...")
                    self.consult_council(user_input)
                    
            except KeyboardInterrupt:
                print("\n👑 Council dismissed! OKGpt shutting down...")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Launch ULTIMATE OKGpt Council"""
    council = OKGptCouncil()
    council.run()

if __name__ == "__main__":
    main()