#!/usr/bin/env python3
"""
📚 MrLore with Service Discovery Beacon
Standalone literary analysis + automatic enhancement!
"""

from service_discovery import ServiceDiscoveryBeacon, ServiceCapability, create_flask_discovery_server
from flask import Flask, request, jsonify

class MrLoreService:
    def __init__(self, port=8001):
        capabilities = [
            ServiceCapability(
                name="literary_analysis",
                description="Analyze text for narrative patterns and literary devices",
                input_types=["text", "document"],
                output_types=["analysis", "summary", "insights"]
            ),
            ServiceCapability(
                name="memory_cache",
                description="Cache and retrieve analysis results",
                input_types=["query"],
                output_types=["cached_result"]
            )
        ]
        
        self.beacon = ServiceDiscoveryBeacon("MrLore", capabilities, port)
        self.enhanced_services = {}
        self.setup_standalone_mode()
        
        # Register for enhancements
        self.beacon.register_enhancement("ClutterBot", self._enhance_with_clutterbot)
        self.beacon.register_enhancement("ZW Transformer", self._enhance_with_zw)
        
    def setup_standalone_mode(self):
        print("✅ MrLore standalone mode ready")
        
    def _enhance_with_clutterbot(self, service_info):
        self.enhanced_services["clutterbot"] = service_info["endpoint"]
        print("🔗 MrLore enhanced with ClutterBot file indexing")
        
    def _enhance_with_zw(self, service_info):
        self.enhanced_services["zw_transformer"] = service_info["endpoint"]
        print("🔗 MrLore enhanced with ZW Transformer consciousness processing")
    
    def analyze_text(self, text):
        result = {"text": text, "analysis": "Literary analysis results", "source": "MrLore"}
        
        if "clutterbot" in self.enhanced_services:
            result["file_context_available"] = True
            
        if "zw_transformer" in self.enhanced_services:
            result["consciousness_patterns"] = True
            
        return result
    
    def start(self):
        self.beacon.start()
        app = create_flask_discovery_server(self.beacon)
        
        @app.route('/analyze', methods=['POST'])
        def analyze():
            data = request.json
            result = self.analyze_text(data.get('text', ''))
            return jsonify(result)
        
        print(f"🚀 MrLore service started on port {self.beacon.port}")
        app.run(host='0.0.0.0', port=self.beacon.port, debug=False)

if __name__ == "__main__":
    service = MrLoreService()
    service.start()
