#!/usr/bin/env python3
"""MrLore Service Wrapper for Argo Connector"""

class MrLoreService:
    def __init__(self):
        self.mrlore_instance = None
        self.status = "stopped"
    
    def start(self):
        try:
            from mrlore_compare_final import MrLore
            self.mrlore_instance = MrLore(chapters_dir="chapters", model="phi3:3.8b")
            self.status = "running"
            return True
        except Exception as e:
            print(f"Failed to start MrLore: {e}")
            self.status = "error"
            return False
    
    def stop(self):
        if self.mrlore_instance:
            self.mrlore_instance = None
        self.status = "stopped"
        return True
    
    def health_check(self):
        return self.mrlore_instance is not None and self.status == "running"
    
    def query(self, question):
        if self.mrlore_instance:
            return self.mrlore_instance.query(question)
        return {"error": "MrLore not running"}

# Create Service instance for Argo connector
Service = MrLoreService
