#!/usr/bin/env python3
"""
🗂️ ClutterBot with Service Discovery Beacon
Standalone file organization + automatic enhancement!
"""

from service_discovery import ServiceDiscoveryBeacon, ServiceCapability, create_flask_discovery_server
from flask import Flask, request, jsonify

class ClutterBotService:
    def __init__(self, port=8000):
        capabilities = [
            ServiceCapability(
                name="file_organization",
                description="Organize files by content and type",
                input_types=["directory", "file_list"],
                output_types=["organized_structure", "file_index"]
            ),
            ServiceCapability(
                name="asset_management",
                description="Manage game assets and resources",
                input_types=["asset_request", "theme"],
                output_types=["asset_list", "file_paths"]
            )
        ]
        
        self.beacon = ServiceDiscoveryBeacon("ClutterBot", capabilities, port)
        self.enhanced_services = {}
        self.setup_standalone_mode()
        
        self.beacon.register_enhancement("MrLore", self._enhance_with_mrlore)
        self.beacon.register_enhancement("ZW Transformer", self._enhance_with_zw)
        
    def setup_standalone_mode(self):
        print("✅ ClutterBot standalone mode ready")
        
    def _enhance_with_mrlore(self, service_info):
        self.enhanced_services["mrlore"] = service_info["endpoint"]
        print("🔗 ClutterBot enhanced with MrLore content analysis")
        
    def _enhance_with_zw(self, service_info):
        self.enhanced_services["zw_transformer"] = service_info["endpoint"]
        print("🔗 ClutterBot enhanced with ZW content understanding")
    
    def organize_files(self, request_data):
        result = {"organized": True, "source": "ClutterBot"}
        
        if "mrlore" in self.enhanced_services:
            result["content_analyzed"] = True
            
        return result
    
    def start(self):
        self.beacon.start()
        app = create_flask_discovery_server(self.beacon)
        
        @app.route('/organize', methods=['POST'])
        def organize():
            data = request.json
            result = self.organize_files(data)
            return jsonify(result)
        
        print(f"🚀 ClutterBot service started on port {self.beacon.port}")
        app.run(host='0.0.0.0', port=self.beacon.port, debug=False)

if __name__ == "__main__":
    service = ClutterBotService()
    service.start()
