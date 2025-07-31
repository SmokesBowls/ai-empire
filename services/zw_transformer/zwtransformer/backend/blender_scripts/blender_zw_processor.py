#!/usr/bin/env python3
"""
Complete Blender ZW Processor Script
Runs inside Blender to process ZW packets and create 3D objects.
Integrates proven working mesh creation from your existing tools.
"""

import bpy
import bmesh
import json
import sys
import os
from mathutils import Vector, Euler
import math
sys.path.append(os.path.dirname(__file__))  # So Blender can find local modules

def clear_scene():
    """Clear all mesh objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    
    # Clear orphaned data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

def create_mesh_from_zw(zw_mesh):
    """Create a Blender mesh object from a ZW-MESH block."""
    obj_type = zw_mesh.get("PROPERTIES", {}).get("TYPE", "CUBE").upper()    
    name = zw_mesh.get("NAME", "ZW_Object")
    location = tuple(zw_mesh.get("LOCATION", (0, 0, 0)))
    rotation = tuple(zw_mesh.get("ROTATION", (0, 0, 0)))
    
    props = zw_mesh.get("PROPERTIES", {})
    size = props.get("SIZE", 1.0)
    scale = tuple(props.get("SCALE", (size, size, size)))
    base_color = props.get("BASE_COLOR", "#ffffff")
    
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    if obj_type == "MESH":
        # Handle custom mesh from vertex/face data
        data = props.get("DATA", {})
        vertices = data.get("vertices", [])
        faces = data.get("faces", [])
        
        # Create mesh data
        mesh = bpy.data.meshes.new(name=name)
        bm = bmesh.new()
        
        # Add vertices
        for v in vertices:
            bm.verts.new(Vector(v))
        
        # Add faces
        for f in faces:
            if len(f) >= 3:  # Ensure face has at least 3 vertices
                try:
                    face_verts = [bm.verts[i] for i in f]
                    bm.faces.new(face_verts)
                except (IndexError, ValueError) as e:
                    print(f"Face error: {e} - Face: {f}")
        
        bm.to_mesh(mesh)
        bm.free()
        
        # Create object
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
    else:
        # Handle primitives using existing code
        if obj_type == "CUBE":
            bpy.ops.mesh.primitive_cube_add(location=location, rotation=Euler(rotation), scale=scale)
        elif obj_type == "SPHERE":
            bpy.ops.mesh.primitive_uv_sphere_add(location=location, rotation=Euler(rotation), scale=scale)
        elif obj_type == "CYLINDER":
            bpy.ops.mesh.primitive_cylinder_add(location=location, rotation=Euler(rotation), scale=scale)
        elif obj_type == "PLANE":
            bpy.ops.mesh.primitive_plane_add(location=location, rotation=Euler(rotation), scale=scale)
        elif obj_type == "CONE":
            bpy.ops.mesh.primitive_cone_add(location=location, rotation=Euler(rotation), scale=scale)
        elif obj_type == "TORUS":
            bpy.ops.mesh.primitive_torus_add(location=location, rotation=Euler(rotation), scale=scale)
        elif obj_type == "EMPTY":
            bpy.ops.object.empty_add(location=location, rotation=Euler(rotation))
        elif obj_type == "CAMERA":
            bpy.ops.object.camera_add(location=location, rotation=Euler(rotation))
        elif obj_type == "LIGHT":
            bpy.ops.object.light_add(type='POINT', location=location, rotation=Euler(rotation))
        else:
            raise ValueError(f"Unsupported object type: {obj_type}")
        
        obj = bpy.context.active_object
        obj.name = name
    
    # Common material assignment for both primitive and custom meshes
    if obj_type != "EMPTY" and obj_type != "CAMERA" and obj_type != "LIGHT":
        mat = bpy.data.materials.new(name=f"{name}_Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            # Convert hex color to RGB
            if isinstance(base_color, str) and base_color.startswith("#") and len(base_color) == 7:
                r = int(base_color[1:3], 16) / 255.0
                g = int(base_color[3:5], 16) / 255.0
                b = int(base_color[5:7], 16) / 255.0
                bsdf.inputs['Base Color'].default_value = (r, g, b, 1)
        
        obj.data.materials.append(mat)
    
    print(f"Created {obj_type} object '{name}' at {location} with color {base_color}")
    
    return {
        "name": obj.name,
        "type": obj_type,
        "location": list(obj.location),
        "scale": list(obj.scale),
        "color": base_color
    }

def create_light_from_zw(zw_light_data, light_name="ZW_Light"):
    """Create a Blender light from ZW-LIGHT data."""
    
    light_type = zw_light_data.get('TYPE', 'SUN').upper()
    location = zw_light_data.get('LOCATION', (0, 0, 5))
    properties = zw_light_data.get('PROPERTIES', {})
    
    # Convert location if string
    if isinstance(location, str):
        location = location.strip('()').split(',')
        location = [float(x.strip()) for x in location]
    
    # Create light data
    light_data = bpy.data.lights.new(name=light_name, type=light_type)
    
    # Set properties
    if 'ENERGY' in properties:
        light_data.energy = float(properties['ENERGY'])
    
    if 'COLOR' in properties:
        color_hex = properties['COLOR']
        if color_hex.startswith('#'):
            color_hex = color_hex[1:]
            rgb = tuple(int(color_hex[i:i+2], 16)/255.0 for i in (0, 2, 4))
            light_data.color = rgb
    
    # Create object
    light_obj = bpy.data.objects.new(light_name, light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = Vector(location)
    
    print(f"Created {light_type} light '{light_name}' at {location}")
    return light_obj

def create_camera_from_zw(zw_camera_data, camera_name="ZW_Camera"):
    """Create a Blender camera from ZW-CAMERA data."""
    
    location = zw_camera_data.get('LOCATION', (7, -7, 5))
    rotation = zw_camera_data.get('ROTATION', (60, 0, 45))
    properties = zw_camera_data.get('PROPERTIES', {})
    
    # Convert location and rotation if strings
    if isinstance(location, str):
        location = location.strip('()').split(',')
        location = [float(x.strip()) for x in location]
    
    if isinstance(rotation, str):
        rotation = rotation.strip('()').split(',')
        rotation = [float(x.strip()) for x in rotation]
    
    # Create camera
    camera_data = bpy.data.cameras.new(camera_name)
    camera_obj = bpy.data.objects.new(camera_name, camera_data)
    bpy.context.collection.objects.link(camera_obj)
    
    # Set location and rotation
    camera_obj.location = Vector(location)
    camera_obj.rotation_euler = Euler([math.radians(r) for r in rotation])
    
    # Set properties
    if 'FOCAL_LENGTH' in properties:
        camera_data.lens = float(properties['FOCAL_LENGTH'])
    
    print(f"Created camera '{camera_name}' at {location}")
    return camera_obj

def recursive_process_zw_blocks(data, results):
    """Recursively process nested ZW blocks from parsed ZW data."""
    if not isinstance(data, dict):
        return

    for key, value in data.items():
        if not isinstance(value, dict):
            continue

        # Handle mesh or object
        if key.upper().startswith("ZW-MESH") or key.upper().startswith("ZW-OBJECT"):
            print(f"Processing mesh block: {key}")
            obj_result = create_mesh_from_zw(value)
            results.append({
                "type": "mesh",
                "name": obj_result["name"],
                "location": obj_result["location"],
                "status": "created",
                "mesh_type": obj_result["type"],
                "color": obj_result["color"]
            })

        # Handle light
        elif key.upper().startswith("ZW-LIGHT"):
            print(f"Processing light block: {key}")
            obj = create_light_from_zw(value, key)
            results.append({
                "type": "light",
                "name": obj.name,
                "location": list(obj.location),
                "status": "created"
            })

        # Handle camera
        elif key.upper().startswith("ZW-CAMERA"):
            print(f"Processing camera block: {key}")
            obj = create_camera_from_zw(value, key)
            results.append({
                "type": "camera",
                "name": obj.name,
                "location": list(obj.location),
                "status": "created"
            })

        # Handle scene (and recurse)
        elif key.upper().startswith("ZW-SCENE"):
            print(f"Processing scene block: {key}")
            results.append({
                "type": "scene",
                "name": key,
                "status": "processed"
            })
            recursive_process_zw_blocks(value, results)

        # Handle unknown keys by recursing (to allow deeply nested structures)
        else:
            recursive_process_zw_blocks(value, results)



def process_zw_packet(zw_data):
    results = []

    try:
        if isinstance(zw_data, str):
            try:
                parsed_data = json.loads(zw_data)
                print("✅ Successfully parsed JSON data")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse failed: {e}. Attempting to parse as ZW...")
                from zw_fallback_parser import parse_zw_to_dict
                parsed_data = parse_zw_to_dict(zw_data)
                print("✅ Parsed as ZW:", parsed_data)
        else:
            parsed_data = zw_data

        if not isinstance(parsed_data, dict):
            return [{"error": "Invalid ZW data format"}]

        print(f"Processing ZW data with keys: {list(parsed_data.keys())}")
        print("ZW RAW INPUT >>>", str(zw_data)[:200])

        # 🔁 Recursively walk nested ZW blocks
        def process_node(node, path=""):
            if isinstance(node, dict):
                for key, value in node.items():
                    current_path = f"{path}.{key}" if path else key

                    if key.startswith("ZW-MESH") or key.startswith("ZW-OBJECT"):
                        print(f"Processing mesh block: {current_path}")
                        obj_result = create_mesh_from_zw(value)
                        results.append({
                            "type": "mesh",
                            "name": obj_result["name"],
                            "location": obj_result["location"],
                            "status": "created",
                            "mesh_type": obj_result["type"],
                            "color": obj_result["color"]
                        })

                    elif key.startswith("ZW-LIGHT"):
                        print(f"Processing light block: {current_path}")
                        obj = create_light_from_zw(value, key)
                        results.append({
                            "type": "light",
                            "name": obj.name,
                            "location": list(obj.location),
                            "status": "created"
                        })

                    elif key.startswith("ZW-ASSET"):
                         print(f"Processing asset block: {current_path}")
                         asset_result = create_asset_from_zw_with_real_import(value, key)
                         if asset_result and "status" in asset_result:
                             results.append({
                             "type": "asset",
                             "name": asset_result.get("name", "unknown"),
                             "source": asset_result.get("source", "unknown"),
                             "location": asset_result.get("location", [0, 0, 0]),
                             "status": asset_result["status"],
                             "asset_type": asset_result.get("type", "unknown"),
                             "object_count": asset_result.get("object_count", 1)
                        })

                    elif key.startswith("ZW-CAMERA"):
                        print(f"Processing camera block: {current_path}")
                        obj = create_camera_from_zw(value, key)
                        results.append({
                            "type": "camera",
                            "name": obj.name,
                            "location": list(obj.location),
                            "status": "created"
                        })

                    elif key.startswith("ZW-ASSET"):
                        print(f"Processing asset block: {current_path}")
                        asset_result = create_asset_from_zw(value, key)
                        results.append({
                            "type": "asset",
                            "name": asset_result["name"],
                            "source": asset_result["source"],
                            "location": asset_result["location"],
                            "status": asset_result["status"],
                            "asset_type": asset_result["type"]
                        })

                    elif key.startswith("ZW-SCENE"):
                        print(f"Processing scene block: {current_path}")
                        results.append({
                            "type": "scene",
                            "name": key,
                            "status": "processed"
                        })

                        process_node(value, current_path)

                    else:
                        process_node(value, current_path)
            elif isinstance(node, list):
                for i, item in enumerate(node):
                    process_node(item, f"{path}[{i}]")

        # 🚀 Begin processing
        process_node(parsed_data)

        bpy.context.view_layer.update()

        if not results:
            print("No ZW blocks processed, creating fallback test cube")
            fallback_result = create_mesh_from_zw({
                "PROPERTIES": {
                    "TYPE": "cube",
                    "SIZE": 1.0,
                    "BASE_COLOR": "#808080"
                },
                "NAME": "FallbackCube",
                "LOCATION": (0, 0, 0)
            })
            results.append({
                "type": "mesh",
                "name": fallback_result["name"],
                "location": fallback_result["location"],
                "status": "fallback_created"
            })

    except Exception as e:
        print(f"❌ Error processing ZW packet: {str(e)}")
        results.append({"error": f"Processing failed: {str(e)}"})

    return results

def create_asset_from_zw_asset(data, asset_name="ZW Asset"):
    """Create a Blender asset from ZW-ASSET data with Polyhaven integration."""
    source = data.get("SOURCE", "").lower()
    name = data.get("NAME", "default_asset")
    location = tuple(data.get("LOCATION", (0, 0, 0)))
    rotation = tuple(data.get("ROTATION", (0, 0, 0)))
    scale = tuple(data.get("SCALE", (1, 1, 1)))

    print(f"Processing asset: {name} from {source} at {location}")

    # Placeholder object
    bpy.ops.object.select_all(action='DESELECT')

    # Create primitive as stand-in
    created = bpy.ops.mesh.primitive_cube_add(location=location, rotation=Euler(rotation), scale=scale)
    if created:
        obj = bpy.context.active_object
        obj.name = f"{source.capitalize()}_{name}"

        # Assign basic material
        mat = bpy.data.materials.new(name=f"{name}_Polyhaven_Material")
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (1.0, 0.5, 0.0, 1.0)  # Orange

        obj.data.materials.append(mat)

        print(f"✅ Created Polyhaven placeholder for '{name}' at {location}")
        return {
            "type": "asset",
            "name": obj.name,
            "source": source.upper() + "_ASSET",
            "location": list(location),
            "rotation": list(rotation),
            "scale": list(scale),
            "status": "placeholder_created"
        }

    return {
        "type": "asset",
        "name": name,
        "source": source,
        "status": "creation_failed"
    }


def main():
    """Main function - called when script is run by Blender."""
    
    if len(sys.argv) < 3:
        print("Usage: blender --background --python blender_zw_processor.py -- <input_file> <output_file>")
        sys.exit(1)
    
    # Get file paths from command line
    input_file = sys.argv[-2]  # ZW file path
    output_file = sys.argv[-1]  # JSON results path
    
    try:
        # Read ZW data
        with open(input_file, 'r') as f:
            zw_data = f.read()
        
        print(f"Processing ZW file: {input_file}")
        print(f"Input data length: {len(zw_data)} characters")
        
        # Clear existing scene
        clear_scene()
        
        # Process ZW data
        results = process_zw_packet(zw_data)
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to: {output_file}")
        print(f"Created {len([r for r in results if r.get('status') in ['created', 'fallback_created']])} objects")
        
        # Save the Blender file
        blend_file = output_file.replace('.json', '.blend')
        bpy.ops.wm.save_as_mainfile(filepath=blend_file)
        print(f"Blender file saved: {blend_file}")
        
    except Exception as e:
        error_result = [{"error": f"Script execution failed: {str(e)}"}]
        with open(output_file, 'w') as f:
            json.dump(error_result, f, indent=2)
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
