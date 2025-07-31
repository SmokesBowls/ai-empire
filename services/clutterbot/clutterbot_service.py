#!/usr/bin/env python3
"""
ClutterBot - File organization and asset management service
"""
from flask import Flask, request, jsonify
import os
import shutil
from pathlib import Path

app = Flask(__name__)

class ClutterBot:
    def __init__(self):
        self.capabilities = ["file_organization", "asset_management"]
    
    def organize_files(self, source_dir, target_dir, organization_type="godot_project"):
        """Organize files by type and purpose"""
        organized = {"scripts": [], "scenes": [], "assets": [], "data": []}
        
        source_path = Path(source_dir)
        if not source_path.exists():
            return {"error": "Source directory not found"}
        
        for file_path in source_path.rglob("*"):
            if file_path.is_file():
                if file_path.suffix == ".gd":
                    organized["scripts"].append(str(file_path))
                elif file_path.suffix == ".tscn":
                    organized["scenes"].append(str(file_path))
                elif file_path.suffix in [".json", ".cfg"]:
                    organized["data"].append(str(file_path))
                else:
                    organized["assets"].append(str(file_path))
        
        return organized

clutterbot = ClutterBot()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "ClutterBot"})

@app.route('/organize', methods=['POST'])
def organize():
    data = request.get_json()
    result = clutterbot.organize_files(
        data.get('source_directory'),
        data.get('target_directory'),
        data.get('organization_type', 'godot_project')
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
