#!/usr/bin/env python3
"""
TRAE Beacon Service - Joins the AI Empire beacon network
"""
import json
import time
import threading
import requests
from flask import Flask, request, jsonify
from real_working_agent import RealAgent

app = Flask(__name__)

class TRAEBeacon:
    def __init__(self, port=8009):
        self.port = port
        self.agent = RealAgent()
        self.capabilities = {
            "service_name": "TRAE",
            "version": "1.0.0",
            "capabilities": [
                "code_generation",
                "file_operations", 
                "bash_execution",
                "testing",
                "project_creation",
                "debugging"
            ],
            "endpoints": {
                "health": f"http://localhost:{port}/health",
                "engineer": f"http://localhost:{port}/engineer",
                "collaborate": f"http://localhost:{port}/collaborate"
            },
            "status": "active",
            "description": "TRAE - The Real Agent that Actually Executes"
        }
        
    def announce_to_beacons(self):
        """Announce TRAE to the beacon network"""
        beacon_ports = [8000, 8001, 8002, 8003]  # Your existing beacons
        
        for port in beacon_ports:
            try:
                response = requests.post(
                    f"http://localhost:{port}/register_service",
                    json=self.capabilities,
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"✅ Registered TRAE with beacon on port {port}")
                else:
                    print(f"⚠️ Failed to register with port {port}: {response.status_code}")
            except Exception as e:
                print(f"❌ Could not reach beacon on port {port}: {e}")
    
    def discover_services(self):
        """Discover other services in the beacon network"""
        services = []
        beacon_ports = [8000, 8001, 8002, 8003]
        
        for port in beacon_ports:
            try:
                response = requests.get(f"http://localhost:{port}/services", timeout=5)
                if response.status_code == 200:
                    port_services = response.json()
                    services.extend(port_services.get('services', []))
                    print(f"🔍 Discovered services from port {port}: {len(port_services.get('services', []))}")
            except Exception as e:
                print(f"❌ Could not discover services from port {port}: {e}")
        
        return services

# Initialize TRAE beacon
trae_beacon = TRAEBeacon()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "TRAE",
        "capabilities": trae_beacon.capabilities["capabilities"],
        "timestamp": time.time()
    })

@app.route('/engineer', methods=['POST'])
def engineer():
    """Main engineering endpoint - execute tasks"""
    data = request.get_json()
    task = data.get('task', '')
    
    if not task:
        return jsonify({"error": "No task provided"}), 400
    
    print(f"🎯 TRAE received engineering task: {task}")
    
    try:
        # Execute the task with our real agent
        result = trae_beacon.agent.run_task(task)
        
        # Get created files
        files = trae_beacon.agent.list_created_files()
        
        return jsonify({
            "status": "success",
            "result": result,
            "files_created": files,
            "working_directory": trae_beacon.agent.working_dir,
            "service": "TRAE",
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e),
            "service": "TRAE"
        }), 500

@app.route('/collaborate', methods=['POST'])
def collaborate():
    """Collaborate with other beacon services"""
    data = request.get_json()
    task = data.get('task', '')
    required_services = data.get('required_services', [])
    
    print(f"🤝 TRAE collaboration request: {task}")
    print(f"🔍 Required services: {required_services}")
    
    # Discover available services
    services = trae_beacon.discover_services()
    
    # Find matching services
    available_services = []
    for service in services:
        if any(req in service.get('capabilities', []) for req in required_services):
            available_services.append(service)
    
    return jsonify({
        "status": "ready_to_collaborate",
        "available_services": available_services,
        "trae_capabilities": trae_beacon.capabilities["capabilities"],
        "service": "TRAE"
    })

@app.route('/services', methods=['GET'])
def services():
    """Return TRAE service info"""
    return jsonify({
        "services": [trae_beacon.capabilities],
        "count": 1
    })

def beacon_announcer():
    """Background thread to announce TRAE to beacon network"""
    while True:
        try:
            trae_beacon.announce_to_beacons()
            time.sleep(30)  # Announce every 30 seconds
        except Exception as e:
            print(f"❌ Beacon announcement error: {e}")
            time.sleep(30)

if __name__ == '__main__':
    # Start beacon announcement in background
    announcement_thread = threading.Thread(target=beacon_announcer, daemon=True)
    announcement_thread.start()
    
    print("🚀 TRAE Beacon starting...")
    print("🏰 Joining the AI Empire beacon network...")
    print(f"📡 TRAE available at http://localhost:8009")
    
    # Initial announcement
    trae_beacon.announce_to_beacons()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=8009, debug=False)

@app.route('/register_service', methods=['POST'])
def register_service():
    """Accept service registrations (stub for clean logs)"""
    data = request.get_json()
    service_name = data.get('service_name', 'Unknown')
    print(f"📋 Registered service: {service_name}")
    return jsonify({"status": "registered", "message": f"Welcome {service_name}!"})
