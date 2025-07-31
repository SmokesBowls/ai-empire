#!/usr/bin/env python3
"""
🚀 Service Discovery Protocol - The Brain of Autonomous AI Collaboration
Makes every service discoverable and enables automatic enhancement!
"""

import json
import time
import threading
import requests
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Callable
from contextlib import contextmanager
from flask import Flask, request, jsonify

@dataclass
class ServiceCapability:
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]

@dataclass 
class ServiceAnnouncement:
    service_name: str
    capabilities: List[ServiceCapability]
    endpoint: str
    port: int
    metadata: Dict = None

class ServiceDiscoveryBeacon:
    """Each service runs this to announce itself and discover others"""
    
    DISCOVERY_PORTS = [8000, 8001, 8002, 8003, 8004, 8005]  # Standard port range
    BEACON_INTERVAL = 30  # Announce every 30 seconds
    DISCOVERY_INTERVAL = 15  # Discover others every 15 seconds
    
    def __init__(self, service_name: str, capabilities: List[ServiceCapability], 
                 port: int, metadata: Dict = None):
        self.service_name = service_name
        self.capabilities = capabilities
        self.port = port
        self.metadata = metadata or {}
        self.endpoint = f"http://localhost:{port}"
        
        self.running = False
        self.beacon_thread = None
        self.discovery_thread = None
        self.enhancement_callbacks = {}
        self.discovered_services = {}
        
    def start(self):
        """Start the discovery beacon"""
        if self.running:
            return
            
        self.running = True
        
        # Start beacon thread (announce presence)
        self.beacon_thread = threading.Thread(target=self._beacon_loop, daemon=True)
        self.beacon_thread.start()
        
        # Start discovery thread (find others)
        self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.discovery_thread.start()
        
        print(f"🔍 {self.service_name} discovery beacon started on port {self.port}")
    
    def stop(self):
        """Stop the discovery beacon"""
        self.running = False
        print(f"📡 {self.service_name} discovery beacon stopped")
    
    def register_enhancement(self, service_name: str, callback: Callable):
        """Register callback for when specific service becomes available"""
        self.enhancement_callbacks[service_name] = callback
    
    def _beacon_loop(self):
        """Continuously announce this service's presence"""
        while self.running:
            try:
                self._broadcast_presence()
                time.sleep(self.BEACON_INTERVAL)
            except Exception as e:
                logging.warning(f"Beacon error: {e}")
                time.sleep(5)
    
    def _discovery_loop(self):
        """Continuously discover other services"""
        while self.running:
            try:
                self._discover_peers()
                time.sleep(self.DISCOVERY_INTERVAL)
            except Exception as e:
                logging.warning(f"Discovery error: {e}")
                time.sleep(5)
    
    def _broadcast_presence(self):
        """Announce this service to all possible ports"""
        announcement = ServiceAnnouncement(
            service_name=self.service_name,
            capabilities=self.capabilities,
            endpoint=self.endpoint,
            port=self.port,
            metadata=self.metadata
        )
        
        # Broadcast to all discovery ports
        for port in self.DISCOVERY_PORTS:
            if port == self.port:
                continue
                
            try:
                response = requests.post(
                    f"http://localhost:{port}/discovery/announce",
                    json=asdict(announcement),
                    timeout=2
                )
            except requests.exceptions.RequestException:
                pass  # Service not running, that's fine
    
    def _discover_peers(self):
        """Find other services and check for enhancements"""
        for port in self.DISCOVERY_PORTS:
            if port == self.port:
                continue
                
            try:
                response = requests.get(f"http://localhost:{port}/capabilities", timeout=2)
                if response.status_code == 200:
                    service_info = response.json()
                    service_name = service_info["name"]
                    
                    # New service discovered?
                    if service_name not in self.discovered_services:
                        self.discovered_services[service_name] = service_info
                        
                        # Check for enhancement callbacks
                        if service_name in self.enhancement_callbacks:
                            try:
                                self.enhancement_callbacks[service_name](service_info)
                            except Exception as e:
                                print(f"Enhancement callback error: {e}")
                        
            except requests.exceptions.RequestException:
                pass  # Service not running

def create_flask_discovery_server(beacon: ServiceDiscoveryBeacon):
    """Create Flask app with discovery endpoints"""
    app = Flask(__name__)
    
    @app.route('/discovery/announce', methods=['POST'])
    def announce_service():
        """Receive service announcements"""
        try:
            data = request.json
            return jsonify({"status": "received", "service": data.get("service_name")})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    @app.route('/capabilities', methods=['GET'])
    def get_capabilities():
        """Return this service's capabilities"""
        return jsonify({
            "name": beacon.service_name,
            "capabilities": [asdict(cap) for cap in beacon.capabilities],
            "endpoint": beacon.endpoint,
            "port": beacon.port,
            "status": "available"
        })
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "healthy", "service": beacon.service_name})
    
    return app

