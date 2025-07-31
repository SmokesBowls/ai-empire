#!/usr/bin/env python3
"""
MrLore - Enhanced Literary Analysis CLI
Now with character modeling and adaptive AI selection

New Features:
🧠 Scene-by-scene memory caching
🎭 Character personality embeddings
🌐 Model availability scanning with fallback
"""

import os
import sys
import argparse
import json
import glob
import time
import hashlib
from datetime import datetime
from pathlib import Path
import requests

class MrLore:
    def __init__(self, chapters_dir="chapters", model="phi3:3.8b"):
        self.chapters_dir = Path(chapters_dir)
        self.scratchpad_dir = Path("scratchpad")
        self.memory_cache_dir = Path("memory_cache")
        self.characters_dir = Path("characters")
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_list_url = "http://localhost:11434/api/tags"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.scratchpad_file = self.scratchpad_dir / f"session_{self.session_id}.txt"
        
        # Ensure directories exist
        self.chapters_dir.mkdir(exist_ok=True)
        self.scratchpad_dir.mkdir(exist_ok=True)
        self.memory_cache_dir.mkdir(exist_ok=True)
        self.characters_dir.mkdir(exist_ok=True)
        
        # Initialize with validated model
        self.model = self._validate_model(model)
        
        # Load character cache
        self.character_profiles = self._load_character_profiles()

        # Initialize scratchpad
        self._init_scratchpad()
    
    def _validate_model(self, requested_model):
        """Check model availability with fallback logic"""
        try:
            # Get available models
            response = requests.get(self.model_list_url, timeout=5)
            available_models = [m["name"] for m in response.json().get("models", [])]
            
            # Check exact match
            if requested_model in available_models:
                return requested_model
            
            # Check without tag
            base_model = requested_model.split(':')[0]
            for model in available_models:
                if model.startswith(base_model):
                    print(f"⚠️  Using available variant: {model}")
                    return model
            
            # Fallback to suitable alternatives
            fallback_priority = [
                "phi3:3.8b", "dolphin3:8b", "llama3:8b", 
                "mistral:latest", "qwen2.5:7b"
            ]
            
            for model in fallback_priority:
                if model in available_models:
                    print(f"⚠️  Falling back to: {model}")
                    return model
            
            # Last resort
            if available_models:
                print(f"⚠️  Using first available: {available_models[0]}")
                return available_models[0]
                
            raise Exception("No Ollama models available")
            
        except requests.exceptions.ConnectionError:
            print("❌ Ollama not running. Start with: ollama serve")
            sys.exit(1)
    
    def _init_scratchpad(self):
        """Initialize session scratchpad"""
        with open(self.scratchpad_file, 'w') as f:
            f.write(f"=== MrLore Session {self.session_id} ===\n")
            f.write(f"Model: {self.model}\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("=== CHARACTER PROFILES ===\n")
            for name, profile in self.character_profiles.items():
                f.write(f"- {name}: {profile['summary'][:100]}...\n")
            f.write("\n=== SESSION MEMORY ===\n")
    
    def _load_character_profiles(self):
        """Load character profiles from disk"""
        profiles = {}
        for char_file in self.characters_dir.glob("*.json"):
            with open(char_file, 'r') as f:
                try:
                    data = json.load(f)
                    profiles[data['name']] = data
                except:
                    continue
        return profiles
    
    def _get_chapter_hash(self):
        """Generate hash of chapter contents for cache validation"""
        hasher = hashlib.sha256()
        for file in self.chapters_dir.glob("*"):
            if file.suffix in ['.md', '.txt', '.markdown']:
                hasher.update(file.read_bytes())
        return hasher.hexdigest()
    
    def _build_memory_cache(self):
        """Create scene-by-scene memory cache"""
        cache_file = self.memory_cache_dir / "scene_cache.json"
        current_hash = self._get_chapter_hash()
        
        # Load existing cache if valid
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                if cache_data.get('content_hash') == current_hash:
                    return cache_data['scenes']
        
        # Process chapters into scenes
        print("🧠 Building scene memory cache...")
        scenes = []
        chapter_files = sorted(self.chapters_dir.glob("*"))
        
        for chapter_file in chapter_files:
            if chapter_file.suffix not in ['.md', '.txt', '.markdown']:
                continue
                
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
                filename = chapter_file.name
                
                # Split into scenes (customize this per your formatting)
                raw_scenes = content.split('\n\n## ')
                for i, scene_text in enumerate(raw_scenes):
                    if not scene_text.strip():
                        continue
                        
                    scene_data = {
                        'chapter': filename,
                        'scene_index': i,
                        'content': scene_text.strip(),
                        'summary': "",
                        'characters': [],
                        'themes': []
                    }
                    scenes.append(scene_data)
        
        # Save new cache
        cache_data = {
            'created': datetime.now().isoformat(),
            'content_hash': current_hash,
            'scenes': scenes
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
            
        return scenes
    
    def _extract_character_profiles(self):
        """Create/update character profiles from text analysis"""
        print("🎭 Analyzing character profiles...")
        character_updates = {}
        
        # Simplified character extraction - customize as needed
        for char_file in self.characters_dir.glob("*.json"):
            with open(char_file, 'r') as f:
                try:
                    data = json.load(f)
                    character_updates[data['name']] = data
                except:
                    continue
        
        # Build prompt for character analysis
        prompt = f"""Identify main characters in the following text and create personality profiles:

{self._load_chapters()[:20000]}

Instructions:
1. List all significant characters
2. For each character, provide:
   - Core personality traits (3-5 adjectives)
   - Motivations and goals
   - Key relationships
   - 2-sentence summary
3. Output in JSON format: {{"characters": [{{"name": "...", "traits": [...], ...}}]}}"""
        
        try:
            response = self._query_ollama(prompt, temperature=0.3)
            if response.startswith('{'):
                char_data = json.loads(response)
                for character in char_data.get('characters', []):
                    name = character['name']
                    character_updates[name] = character
                    
                    # Save character file
                    with open(self.characters_dir / f"{name}.json", 'w') as f:
                        json.dump(character, f, indent=2)
        except:
            print("⚠️  Character extraction failed - using existing profiles")
        
        return character_updates
    
    def _load_chapters(self):
        """Load all chapter files"""
        full_text = ""
        patterns = ["*.md", "*.txt", "*.markdown"]
        
        for pattern in patterns:
            for file_path in glob.glob(str(self.chapters_dir / pattern)):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        full_text += f"\n\n=== {os.path.basename(file_path)} ===\n{f.read()}"
                except Exception as e:
                    print(f"⚠️  Error reading {file_path}: {e}")
        
        return full_text
    
    def _load_scratchpad(self):
        """Load current session memory"""
        if self.scratchpad_file.exists():
            with open(self.scratchpad_file, 'r') as f:
                return f.read()
        return ""
    
    def _update_scratchpad(self, content):
        """Add to session memory"""
        with open(self.scratchpad_file, 'a') as f:
            f.write(f"\n[{datetime.now().strftime('%H:%M:%S')}] {content}\n")
    
    def _query_ollama(self, prompt, temperature=0.7, timeout=120):
        """Send query to Ollama with error handling"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            }
            
            response = requests.post(
                self.ollama_url, 
                json=payload, 
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.Timeout:
            return "❌ Error: Analysis timed out - try simpler query or different model"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def query(self, question):
        """Enhanced query with memory caching"""
        # Build context layers
        scene_cache = self._build_memory_cache()
        memory = self._load_scratchpad()
        
        # Character context
        character_context = "\n".join(
            f"{name}: {profile['summary']}" 
            for name, profile in self.character_profiles.items()
        )
        
        # Build comprehensive prompt
        prompt = f"""You are MrLore, a literary analyst with perfect recall of texts. 
Use cached scene memories and character profiles to answer.

=== CHARACTER PROFILES ===
{character_context}

=== SCENE MEMORIES ===
{json.dumps(scene_cache[:5], indent=2)} 
[Only first 5 scenes shown - {len(scene_cache)} total]

=== SESSION MEMORY ===
{memory}

=== USER QUESTION ===
{question}

=== RESPONSE GUIDELINES ===
1. Reference relevant scenes by chapter/scene index
2. Cite character traits from profiles
3. Note new insights for memory
4. If unsure, say so and suggest analysis approach

Analysis:"""
        
        response = self._query_ollama(prompt)
        
        # Update scratchpad
        self._update_scratchpad(
            f"Q: {question[:120]}... | Insights: {response[:100]}..."
        )
        
        return response
    
    def build_character_profiles(self):
        """Force rebuild character profiles"""
        self.character_profiles = self._extract_character_profiles()
        return f"🆙 Updated {len(self.character_profiles)} character profiles"
    
    def debug(self):
        """Show system status"""
        status = [
            f"System Status:",
            f"- Chapters: {len(list(self.chapters_dir.glob('*')))} files",
            f"- Scenes: {len(self._build_memory_cache())} cached",
            f"- Characters: {len(self.character_profiles)} profiles",
            f"- Active model: {self.model}",
            f"- Session: {self.scratchpad_file.name}"
        ]
        return "\n".join(status)
    
    def reset(self):
        """Clear all session data"""
        cleared = 0
        for file in self.scratchpad_dir.glob("session_*.txt"):
            file.unlink()
            cleared += 1
        return f"🧹 Cleared {cleared} session files"

def main():
    parser = argparse.ArgumentParser(
        description="MrLore - Enhanced Literary Analysis",
        epilog="""
Examples:
  python3 mrlore.py --query "Analyze the protagonist's development"
  python3 mrlore.py --model dolphin3:8b --query "Compare character motivations"
  python3 mrlore.py --build-chars
  python3 mrlore.py --debug
  python3 mrlore.py --reset
        """
    )
    
    parser.add_argument("--query", "-q", help="Ask about your novel")
    parser.add_argument("--debug", "-d", action="store_true", help="Show system status")
    parser.add_argument("--reset", "-r", action="store_true", help="Clear session data")
    parser.add_argument("--model", "-m", default="phi3:3.8b", help="Ollama model to use")
    parser.add_argument("--chapters", "-c", default="chapters", help="Chapters directory")
    parser.add_argument("--build-chars", "-b", action="store_true", help="Rebuild character profiles")
    
    args = parser.parse_args()
    
    if not any([args.query, args.debug, args.reset, args.build_chars]):
        parser.print_help()
        return
    
    mrlore = MrLore(chapters_dir=args.chapters, model=args.model)
    
    try:
        if args.reset:
            print(mrlore.reset())
        
        elif args.build_chars:
            print(mrlore.build_character_profiles())
        
        elif args.debug:
            print(mrlore.debug())
        
        elif args.query:
            print(f"🔥 MrLore v1.0 - Enhanced Literary Analysis")
            print(f"📂 Chapters: {args.chapters}/")
            print(f"🤖 Model: {mrlore.model}")
            print(f"🎭 Characters: {len(mrlore.character_profiles)} loaded")
            print(f"❓ Query: {args.query}")
            print("=" * 60)
            
            start_time = time.time()
            result = mrlore.query(args.query)
            elapsed = time.time() - start_time
            
            print(f"\n💬 Analysis ({elapsed:.1f}s):\n{result}")
            print(f"\n📋 Session: {mrlore.scratchpad_file}")
    
    except KeyboardInterrupt:
        print("\n🛑 Session interrupted")
    except Exception as e:
        print(f"💥 Critical error: {e}")
        return 1
    
    return 0





DEFAULT_MODELS = [
    "phi3:3.8b",
    "llama3:8b",
    "dolphin3:8b",
    "mistral-nemo:12b",
    "qwen2.5:7b-instruct"
]

def run_comparisons(query, models, chapters):
    print(f"🎯 Comparing models for query: {query}")
    print(f"📚 Chapters: {chapters}")
    print("=" * 60)

    for model in models:
        print(f"\n🤖 Model: {model}")
        print("-" * 60)
        try:
            lore = MrLore(chapters_dir=chapters, model=model)
            start = time.time()
            result = lore.query(query)
            elapsed = time.time() - start
            print(f"🕒 Time: {elapsed:.1f}s")
            print(f"💬 Output:\n{result[:2000]}\n...")
        except Exception as e:
            print(f"❌ Error with model {model}: {e}")
        print("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MrLore Multi-Model Compare Mode")
    parser.add_argument("--query", "-q", required=True, help="Query to run across all models")
    parser.add_argument("--models", "-m", nargs="+", default=DEFAULT_MODELS,
                        help="List of Ollama models to compare")
    parser.add_argument("--chapters", "-c", default="chapters", help="Chapter directory")
    args = parser.parse_args()

    run_comparisons(args.query, args.models, args.chapters)
