#!/usr/bin/env python3
"""
TRAE Memory Module - Simple file-based persistence
"""
import json
import time
from pathlib import Path

class TRAEMemory:
    def __init__(self, memory_file="/tmp/trae_memory.json"):
        self.memory_file = Path(memory_file)
        self.memory = self.load_memory()
    
    def load_memory(self):
        """Load memory from file"""
        if self.memory_file.exists():
            try:
                return json.loads(self.memory_file.read_text())
            except:
                pass
        return {"sessions": {}, "project_history": [], "task_timeline": []}
    
    def save_memory(self):
        """Save memory to file"""
        self.memory_file.write_text(json.dumps(self.memory, indent=2))
    
    def remember_task(self, task, result, files_created):
        """Remember a completed task"""
        entry = {
            "timestamp": time.time(),
            "task": task,
            "result": result,
            "files_created": files_created,
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.memory["task_timeline"].append(entry)
        self.save_memory()
        print(f"🧠 Remembered: {task[:50]}...")
    
    def get_recent_tasks(self, count=5):
        """Get recent task history"""
        return self.memory["task_timeline"][-count:]
    
    def get_project_context(self):
        """Get current project context"""
        recent = self.get_recent_tasks(3)
        all_files = []
        for task in recent:
            all_files.extend(task.get("files_created", []))
        
        return {
            "recent_tasks": [t["task"] for t in recent],
            "active_files": list(set(all_files)),
            "session_count": len(self.memory["task_timeline"])
        }

# Add to real_working_agent.py
memory = TRAEMemory()
