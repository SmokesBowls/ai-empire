#!/usr/bin/env python3
"""
EngAin Avatar Bridge - Connect the Godot avatar to the AI Empire
"""
import json
import socket
import threading
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

class EngAinAvatarBridge:
    def __init__(self):
        self.port = 8005
        self.trae_url = "http://localhost:8009"
        self.empire_services = {
            "trae": "http://localhost:8009",
            "mrlore": "http://localhost:8001", 
            "zw": "http://localhost:8002",
            "council": "http://localhost:8003",
            "clutter": "http://localhost:8000"
        }
        # TCP connection to Godot (EngAin avatar)
        self.godot_socket = None
        self.setup_godot_connection()
        
    def setup_godot_connection(self):
        """Setup TCP connection to Godot EngAin avatar"""
        try:
            # This will connect to Godot's TCP server
            # You'll need to add a TCP server to EngAin avatar in Godot
            print("🔌 Setting up connection to EngAin avatar in Godot...")
            # self.godot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.godot_socket.connect(('localhost', 9999))  # Godot TCP port
            print("📡 Ready to connect to EngAin avatar")
        except Exception as e:
            print(f"⚠️ Godot connection pending: {e}")
    
    def send_to_avatar(self, message_type, data):
        """Send message to EngAin avatar in Godot"""
        message = {
            "type": message_type,
            "data": data,
            "timestamp": time.time()
        }
        
        # For now, just log - you'll implement the actual Godot TCP later
        print(f"🎮 → EngAin Avatar: {message_type} | {data}")
        
        # Later: send via TCP socket
        # if self.godot_socket:
        #     self.godot_socket.send(json.dumps(message).encode())
        
        return message
    
    def request_empire_service(self, service, task_data):
        """Request work from empire services"""
        url = self.empire_services.get(service)
        if not url:
            return {"error": f"Unknown service: {service}"}
            
        try:
            if service == "trae":
                response = requests.post(f"{url}/engineer", json={"task": task_data}, timeout=60)
            elif service == "mrlore":
                response = requests.post(f"{url}/analyze", json={"text": task_data}, timeout=30)
            elif service == "zw":
                response = requests.post(f"{url}/generate", json={"prompt": task_data}, timeout=30)
            else:
                response = requests.post(url, json={"input": task_data}, timeout=30)
                
            return response.json() if response.status_code == 200 else {"error": "Service error"}
        except Exception as e:
            return {"error": f"Service request failed: {e}"}

bridge = EngAinAvatarBridge()

@app.route('/avatar_command', methods=['POST'])
def avatar_command():
    """Receive commands from EngAin avatar in Godot"""
    data = request.get_json()
    command = data.get('command', '')
    avatar_context = data.get('context', {})
    
    print(f"🎮 EngAin Avatar says: {command}")
    
    # Process avatar command through the empire
    if "create" in command or "build" in command:
        # Send to TRAE for execution
        result = bridge.request_empire_service("trae", command)
        
        # Send result back to avatar
        bridge.send_to_avatar("task_result", {
            "command": command,
            "result": result,
            "files_created": result.get('files_created', [])
        })
        
        return jsonify({
            "status": "executed",
            "empire_result": result
        })
    
    elif "analyze" in command or "story" in command:
        # Send to MrLore for analysis
        result = bridge.request_empire_service("mrlore", command)
        bridge.send_to_avatar("analysis_result", result)
        return jsonify({"status": "analyzed", "result": result})
    
    else:
        bridge.send_to_avatar("acknowledgment", {"message": "Command received"})
        return jsonify({"status": "acknowledged"})

@app.route('/empire_to_avatar', methods=['POST'])
def empire_to_avatar():
    """Send messages from empire back to avatar"""
    data = request.get_json()
    message_type = data.get('type', 'notification')
    content = data.get('content', '')
    
    bridge.send_to_avatar(message_type, content)
    return jsonify({"status": "sent_to_avatar"})

@app.route('/avatar_status', methods=['GET'])
def avatar_status():
    """Get EngAin avatar status"""
    return jsonify({
        "avatar_connected": bridge.godot_socket is not None,
        "empire_services": list(bridge.empire_services.keys()),
        "bridge_active": True
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check for beacon registration"""
    return jsonify({
        "status": "healthy",
        "service": "EngAin_Avatar_Bridge",
        "capabilities": ["avatar_interface", "godot_integration", "empire_coordination"],
        "avatar_mode": True
    })

if __name__ == '__main__':
    print("🎮 EngAin Avatar Bridge starting...")
    print("🏰 Connecting Godot avatar to AI Empire...")
    print("📡 Bridge ready for avatar commands")
    
    app.run(host='0.0.0.0', port=8005, debug=False)
