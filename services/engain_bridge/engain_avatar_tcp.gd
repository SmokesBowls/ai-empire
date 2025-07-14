# Add this to your EngAin avatar in Godot
extends Node

var tcp_client: StreamPeerTCP
var bridge_url = "http://localhost:8005"

func _ready():
    print("🎮 EngAin avatar initializing empire connection...")
    setup_empire_bridge()

func setup_empire_bridge():
    # For now, use HTTP requests to bridge
    # Later: implement TCP for real-time communication
    print("📡 EngAin avatar ready for empire commands")

func send_command_to_empire(command: String, context: Dictionary = {}):
    """Send command from avatar to AI Empire"""
    var http_request = HTTPRequest.new()
    add_child(http_request)
    
    var json_data = JSON.stringify({
        "command": command,
        "context": context,
        "avatar_position": global_position,
        "scene_context": get_tree().current_scene.name
    })
    
    var headers = ["Content-Type: application/json"]
    http_request.request(bridge_url + "/avatar_command", headers, HTTPClient.METHOD_POST, json_data)
    http_request.request_completed.connect(_on_empire_response)
    
    print("🏰 EngAin avatar sent to empire: ", command)

func _on_empire_response(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray):
    var response = JSON.parse_string(body.get_string_from_utf8())
    print("⚡ Empire response: ", response)
    
    # Process empire response in avatar
    if response.has("empire_result"):
        var files_created = response.empire_result.get("files_created", [])
        if files_created.size() > 0:
            speak("Empire created " + str(files_created.size()) + " files!")

func speak(text: String):
    """Make EngAin avatar speak in game"""
    print("🗣️ EngAin: ", text)
    # Add your speech bubble/audio logic here

# Example usage in avatar:
# send_command_to_empire("Create a new weapon system for this game")
# send_command_to_empire("Analyze the current scene and suggest improvements")
