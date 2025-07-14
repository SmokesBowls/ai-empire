#!/usr/bin/env python3
"""
🧠 ZW Transformer with Service Discovery Beacon
Standalone consciousness processing + automatic enhancement!
"""

from service_discovery import ServiceDiscoveryBeacon, ServiceCapability, create_flask_discovery_server
import threading
from flask import Flask, request, jsonify

class ZWTransformerService:
    def __init__(self, port=8002):
        # Define ZW Transformer capabilities
        capabilities = [
            ServiceCapability(
                name="consciousness_processing",
                description="Process and generate ZW consciousness patterns",
                input_types=["zw_request", "consciousness_data"],
                output_types=["zw_content", "consciousness_patterns"]
            ),
            ServiceCapability(
                name="narrative_generation",
                description="Generate narrative content and game elements",
                input_types=["prompt", "context"],
                output_types=["generated_content", "narrative_structure"]
            )
        ]
        
        # Start discovery beacon
        self.beacon = ServiceDiscoveryBeacon("ZW Transformer", capabilities, port)
        self.enhanced_services = {}
        
        # Setup standalone mode
        self.setup_standalone_mode()
        
        # Register for enhancements
        self.beacon.register_enhancement("MrLore", self._enhance_with_mrlore)
        self.beacon.register_enhancement("ClutterBot", self._enhance_with_clutterbot)
        
    def setup_standalone_mode(self):
        """Core ZW Transformer functionality that works alone"""
        print("✅ ZW Transformer standalone mode ready")
        # Initialize your existing ZW processing here
        
    def _enhance_with_mrlore(self, service_info):
        """Enhancement when MrLore becomes available"""
        self.enhanced_services["mrlore"] = service_info["endpoint"]
        print("🔗 ZW Transformer enhanced with MrLore narrative intelligence")
        
    def _enhance_with_clutterbot(self, service_info):
        """Enhancement when ClutterBot becomes available"""
        self.enhanced_services["clutterbot"] = service_info["endpoint"]
        print("🔗 ZW Transformer enhanced with ClutterBot asset management")
    
    def process_request(self, request_data):
        """Process ZW request with all available enhancements"""
        # Base processing (always works)
        result = {"request": request_data, "source": "ZW Transformer"}
        
        # Enhanced with MrLore if available
        if "mrlore" in self.enhanced_services:
            # Add narrative intelligence to processing
            result["narrative_enhanced"] = True
            
        # Enhanced with ClutterBot if available
        if "clutterbot" in self.enhanced_services:
            # Add asset management capabilities
            result["assets_managed"] = True
            
        return result
    
    def start(self):
        """Start the service with discovery"""
        # Start discovery beacon
        self.beacon.start()
        
        # Start Flask server for service endpoints
        app = create_flask_discovery_server(self.beacon)
        
        @app.route('/generate', methods=['POST'])
        def generate():
            data = request.json
            result = self.process_request(data)
            return jsonify(result)
        
        print(f"🚀 ZW Transformer service started on port {self.beacon.port}")
        app.run(host='0.0.0.0', port=self.beacon.port, debug=False)

if __name__ == "__main__":
    service = ZWTransformerService()
    service.start()
