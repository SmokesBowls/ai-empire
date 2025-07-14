#!/usr/bin/env python3
"""
Enhanced OKGpt Council with DrLore Memory Integration
Persistent AI council that builds institutional wisdom over time
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class CouncilMemorySystem:
    def __init__(self, memory_dir="council_memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different memory types
        self.member_profiles_dir = self.memory_dir / "member_profiles"
        self.debate_history_dir = self.memory_dir / "debate_history" 
        self.synthesis_patterns_dir = self.memory_dir / "synthesis_patterns"
        self.topic_knowledge_dir = self.memory_dir / "topic_knowledge"
        
        for dir_path in [self.member_profiles_dir, self.debate_history_dir, 
                        self.synthesis_patterns_dir, self.topic_knowledge_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def save_member_memory(self, member_name: str, memory_data: Dict):
        """Save individual member's accumulated memory"""
        memory_file = self.member_profiles_dir / f"{member_name.lower()}_memory.json"
        
        # Load existing memory if it exists
        existing_memory = {}
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                existing_memory = json.load(f)
        
        # Merge new memory with existing
        merged_memory = self._merge_memories(existing_memory, memory_data)
        
        # Save updated memory
        with open(memory_file, 'w') as f:
            json.dump(merged_memory, f, indent=2)
    
    def load_member_memory(self, member_name: str) -> Dict:
        """Load individual member's memory"""
        memory_file = self.member_profiles_dir / f"{member_name.lower()}_memory.json"
        
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                return json.load(f)
        
        # Return default memory structure
        return {
            "expertise_areas": [],
            "successful_approaches": [],
            "debate_patterns": [],
            "topic_specializations": {},
            "collaboration_insights": [],
            "evolution_log": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def save_debate_session(self, session_data: Dict):
        """Save entire debate session for institutional memory"""
        session_id = session_data.get('session_id', datetime.now().strftime("%Y%m%d_%H%M%S"))
        session_file = self.debate_history_dir / f"session_{session_id}.json"
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def recall_relevant_debates(self, topic: str, member_name: str = None, limit: int = 5) -> List[Dict]:
        """Find past debates relevant to current topic"""
        relevant_sessions = []
        
        for session_file in self.debate_history_dir.glob("session_*.json"):
            with open(session_file, 'r') as f:
                try:
                    session = json.load(f)
                    
                    # Check topic relevance (simple keyword matching for now)
                    if self._is_topic_relevant(topic, session.get('topic', '')):
                        if member_name:
                            # Filter for specific member participation
                            if member_name in session.get('participants', []):
                                relevant_sessions.append(session)
                        else:
                            relevant_sessions.append(session)
                except:
                    continue
        
        # Sort by relevance and recency
        relevant_sessions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return relevant_sessions[:limit]
    
    def _merge_memories(self, existing: Dict, new: Dict) -> Dict:
        """Intelligently merge memory structures"""
        merged = existing.copy()
        
        for key, value in new.items():
            if key in merged:
                if isinstance(value, list) and isinstance(merged[key], list):
                    # Merge lists, avoiding duplicates
                    merged[key] = list(set(merged[key] + value))
                elif isinstance(value, dict) and isinstance(merged[key], dict):
                    # Recursively merge dictionaries
                    merged[key] = self._merge_memories(merged[key], value)
                else:
                    # Replace with new value
                    merged[key] = value
            else:
                merged[key] = value
        
        merged['last_updated'] = datetime.now().isoformat()
        return merged
    
    def _is_topic_relevant(self, current_topic: str, past_topic: str) -> bool:
        """Simple relevance checking (can be enhanced with embeddings)"""
        current_words = set(current_topic.lower().split())
        past_words = set(past_topic.lower().split())
        
        # Check for word overlap
        overlap = len(current_words.intersection(past_words))
        return overlap >= 2 or any(word in past_topic.lower() for word in current_words if len(word) > 4)

class MemoryEnhancedCouncilMember(AICouncilMember):
    def __init__(self, name: str, model: str, personality: str, memory_system: CouncilMemorySystem):
        super().__init__(name, model, personality)
        self.memory_system = memory_system
        self.personal_memory = memory_system.load_member_memory(name)
        self.session_contributions = []
    
    def respond_with_memory(self, conversation_history: str, user_input: str, topic: str = None) -> str:
        """Enhanced response that incorporates personal memory"""
        
        # Recall relevant past insights
        if topic:
            relevant_debates = self.memory_system.recall_relevant_debates(topic, self.name, limit=3)
            memory_context = self._build_memory_context(topic, relevant_debates)
        else:
            memory_context = self._build_general_memory_context()
        
        # Build enhanced prompt with memory
        enhanced_prompt = f"""You are {self.name}, {self.personality}

Your Personal Memory:
{memory_context}

Current Discussion:
{conversation_history}

User Input: {user_input}

Instructions:
1. Draw upon your accumulated expertise and past insights
2. Reference relevant patterns from previous debates when applicable  
3. Build upon your established knowledge while contributing fresh perspectives
4. Maintain your unique personality and role while evolving your thinking

{self.name}:"""
        
        # Get response using enhanced context
        response = self._get_ollama_response(enhanced_prompt)
        
        # Track this contribution for memory update
        self.session_contributions.append({
            "topic": topic or "General",
            "input": user_input,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _build_memory_context(self, topic: str, relevant_debates: List[Dict]) -> str:
        """Build memory context from personal history and relevant debates"""
        context_parts = []
        
        # Personal expertise areas
        if self.personal_memory.get('expertise_areas'):
            context_parts.append(f"Your expertise: {', '.join(self.personal_memory['expertise_areas'])}")
        
        # Topic-specific knowledge
        if topic in self.personal_memory.get('topic_specializations', {}):
            specialization = self.personal_memory['topic_specializations'][topic]
            context_parts.append(f"Your insights on {topic}: {specialization}")
        
        # Relevant past debates
        if relevant_debates:
            context_parts.append("Relevant past discussions:")
            for debate in relevant_debates[:2]:  # Limit to most relevant
                context_parts.append(f"- {debate.get('topic', 'Unknown')}: {debate.get('summary', 'No summary')}")
        
        return "\n".join(context_parts) if context_parts else "First time discussing this topic."
    
    def _build_general_memory_context(self) -> str:
        """Build general memory context for non-specific topics"""
        context_parts = []
        
        if self.personal_memory.get('successful_approaches'):
            context_parts.append(f"Your proven approaches: {', '.join(self.personal_memory['successful_approaches'][:3])}")
        
        if self.personal_memory.get('collaboration_insights'):
            context_parts.append(f"Your collaboration insights: {', '.join(self.personal_memory['collaboration_insights'][:2])}")
        
        return "\n".join(context_parts) if context_parts else "Drawing upon general experience."
    
    def update_memory_after_session(self, session_topic: str, session_outcome: str):
        """Update personal memory based on session results"""
        
        # Extract insights from this session's contributions
        new_insights = self._extract_session_insights(session_topic, session_outcome)
        
        # Update personal memory
        updated_memory = self.personal_memory.copy()
        
        # Add new expertise if demonstrated
        if session_topic not in updated_memory.get('topic_specializations', {}):
            updated_memory.setdefault('topic_specializations', {})[session_topic] = []
        
        # Add insights to topic specialization
        updated_memory['topic_specializations'][session_topic].extend(new_insights)
        
        # Update collaboration patterns
        if session_outcome in ['consensus', 'productive']:
            updated_memory.setdefault('successful_approaches', []).append(
                f"Effective contribution to {session_topic} discussion"
            )
        
        # Log evolution
        updated_memory.setdefault('evolution_log', []).append({
            "session_topic": session_topic,
            "outcome": session_outcome,
            "insights_gained": len(new_insights),
            "timestamp": datetime.now().isoformat()
        })
        
        # Save updated memory
        self.memory_system.save_member_memory(self.name, updated_memory)
        self.personal_memory = updated_memory
    
    def _extract_session_insights(self, topic: str, outcome: str) -> List[str]:
        """Extract key insights from session contributions"""
        insights = []
        
        for contribution in self.session_contributions:
            if len(contribution['response']) > 100:  # Substantial contributions
                # Extract key phrases (simplified - could use NLP)
                response = contribution['response']
                if any(word in response.lower() for word in ['framework', 'approach', 'method']):
                    insights.append(f"Framework insight for {topic}")
                if any(word in response.lower() for word in ['pattern', 'trend', 'observation']):
                    insights.append(f"Pattern recognition for {topic}")
        
        return insights[:3]  # Limit to top insights

class MemoryEnhancedOKGptCouncil(OKGptCouncil):
    def __init__(self):
        self.memory_system = CouncilMemorySystem()
        super().__init__()
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def setup_council(self):
        """Initialize memory-enhanced council members"""
        self.council_members = [
            MemoryEnhancedCouncilMember(
                name="Bob", 
                model="qwen2.5:7b-instruct",
                personality="Strategic Analyst with institutional memory of successful frameworks",
                memory_system=self.memory_system
            ),
            MemoryEnhancedCouncilMember(
                name="Sarah", 
                model="llama3:8b",
                personality="Knowledge Archivist who builds comprehensive understanding over time",
                memory_system=self.memory_system
            ),
            MemoryEnhancedCouncilMember(
                name="Quick", 
                model="phi3:3.8b",
                personality="Lightning Scout who remembers rapid insights and alternative approaches",
                memory_system=self.memory_system
            ),
            MemoryEnhancedCouncilMember(
                name="Rod", 
                model="dolphin3:8b",
                personality="Balanced Moderator with memory of perspective patterns and outcomes",
                memory_system=self.memory_system
            ),
            MemoryEnhancedCouncilMember(
                name="Mistral", 
                model="mistral-nemo:12b",
                personality="Diplomatic Steward who accumulates synthesis patterns and resolution strategies",
                memory_system=self.memory_system
            )
        ]
    
    def consult_council_with_memory(self, user_input: str, topic: str = None, selected_members: List[str] = None):
        """Enhanced council consultation with memory integration"""
        
        # Use topic extraction if not provided
        if not topic:
            topic = self._extract_topic(user_input)
        
        # Prepare session tracking
        session_data = {
            "session_id": self.current_session_id,
            "topic": topic,
            "user_input": user_input,
            "participants": selected_members or [m.name for m in self.council_members],
            "timestamp": datetime.now().isoformat(),
            "responses": [],
            "synthesis": "",
            "outcome": ""
        }
        
        if selected_members:
            members = [m for m in self.council_members if m.name in selected_members]
        else:
            members = self.council_members
        
        print(f"\n🧠 Memory-Enhanced Council Consultation: {topic}")
        print(f"🏛️ Consulting: {', '.join([m.name for m in members])}")
        print("=" * 60)
        
        # Add user input to history
        self.add_to_history("User", user_input)
        context = self.get_conversation_context()
        
        # Get memory-enhanced responses
        for member in members:
            print(f"\n🗣️ **{member.name}** (with memory):")
            response = member.respond_with_memory(context, user_input, topic)
            print(response)
            print("-" * 60)
            
            # Track response
            session_data["responses"].append({
                "member": member.name,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Add to history
            self.add_to_history(member.name, response)
            context = self.get_conversation_context()
        
        # Enhanced synthesis with memory
        if len(members) > 1:
            discussion_block = "\n\n".join([r["response"] for r in session_data["responses"]])
            synthesis = self.steward.synthesize(topic, discussion_block)
            print(f"\n✨ **Mistral Synthesis:** {synthesis}")
            session_data["synthesis"] = synthesis
            self.add_to_history("Mistral", f"MEMORY-ENHANCED SYNTHESIS: {synthesis}")
        
        # Determine session outcome
        session_data["outcome"] = self._assess_session_outcome(session_data["responses"])
        
        # Update member memories
        for member in members:
            member.update_memory_after_session(topic, session_data["outcome"])
        
        # Save session to institutional memory
        self.memory_system.save_debate_session(session_data)
        
        print(f"\n✅ Memory-enhanced consultation complete! Session saved as {self.current_session_id}")
        
        return session_data
    
    def _extract_topic(self, user_input: str) -> str:
        """Extract main topic from user input"""
        # Simplified topic extraction (could be enhanced with NLP)
        words = user_input.lower().split()
        
        # Look for key topic indicators
        topic_words = [word for word in words if len(word) > 4 and word not in 
                      ['should', 'would', 'could', 'might', 'about', 'through']]
        
        return " ".join(topic_words[:3]) if topic_words else "General Discussion"
    
    def _assess_session_outcome(self, responses: List[Dict]) -> str:
        """Assess the quality and outcome of the session"""
        total_length = sum(len(r["response"]) for r in responses)
        
        if total_length > 2000:  # Substantial discussion
            return "productive"
        elif total_length > 1000:
            return "consensus" 
        else:
            return "exploratory"
    
    def show_member_memories(self):
        """Display accumulated memories for each council member"""
        print("\n🧠 **COUNCIL MEMBER MEMORIES:**")
        print("=" * 60)
        
        for member in self.council_members:
            memory = member.personal_memory
            print(f"\n👤 **{member.name}:**")
            
            if memory.get('expertise_areas'):
                print(f"   🎯 Expertise: {', '.join(memory['expertise_areas'][:3])}")
            
            if memory.get('topic_specializations'):
                topics = list(memory['topic_specializations'].keys())[:3]
                print(f"   📚 Specialized in: {', '.join(topics)}")
            
            if memory.get('evolution_log'):
                sessions = len(memory['evolution_log'])
                print(f"   📈 Growth: {sessions} sessions of learning")
            
            last_updated = memory.get('last_updated', 'Never')
            print(f"   🕒 Last updated: {last_updated}")
        
        print("\n" + "=" * 60)

# Example usage
if __name__ == "__main__":
    # Create memory-enhanced council
    council = MemoryEnhancedOKGptCouncil()
    
    # Example session
    result = council.consult_council_with_memory(
        "How should we architect consciousness-aware AI systems?",
        topic="AI Consciousness Architecture"
    )
    
    # Show accumulated memories
    council.show_member_memories()
