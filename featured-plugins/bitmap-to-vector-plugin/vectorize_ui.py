#!/usr/bin/env python3
import requests
import sys
import os
import json
import tempfile
import subprocess
from pathlib import Path
import asyncio
import websockets
import platform
import urllib.request
import tarfile
import zipfile

LUNACY_API = "http://localhost:31415"
LUNACY_WS = "ws://localhost:31416"
PLUGIN_ID = "bitmap-to-vector-plugin"
PLUGIN_VERSION = "2.0.0"

VTRACER_BIN = Path(__file__).parent / ("vtracer.exe" if os.name == "nt" else "vtracer")
VTRACER_VERSION = "0.6.4"
DEBUG_MODE = os.environ.get("LUNACY_PLUGIN_DEBUG", "0") == "1"

PRESETS = {
    "Photo": {
        "colormode": "color",
        "mode": "spline",
        "hierarchical": "stacked",
        "color_precision": "8",
        "filter_speckle": "10",
        "corner_threshold": "180",
        "gradient_step": "48",
        "path_precision": "2",
        "segment_length": "4",
        "splice_threshold": "45"
    },
    "Poster": {
        "colormode": "color",
        "mode": "spline",
        "hierarchical": "stacked",
        "color_precision": "8",
        "filter_speckle": "4",
        "corner_threshold": "60",
        "gradient_step": "16",
        "path_precision": "2",
        "segment_length": "4",
        "splice_threshold": "45"
    },
    "BW": {
        "colormode": "bw",
        "mode": "spline",
        "hierarchical": "stacked",
        "color_precision": "6",
        "filter_speckle": "4",
        "corner_threshold": "60",
        "gradient_step": "16",
        "path_precision": "2",
        "segment_length": "4",
        "splice_threshold": "45"
    }
}

PRESET_PARAMS = [
    "colormode", "mode", "hierarchical", "color_precision",
    "filter_speckle", "corner_threshold", "gradient_step",
    "path_precision", "segment_length", "splice_threshold"
]

def update_ui_fields(updates: dict) -> bool:
    try:
        response = requests.post(
            f"{LUNACY_API}/updateuifields",
            json={
                "pluginId": PLUGIN_ID,
                "updates": updates
            },
            timeout=5
        )
        
        if response.ok:
            print(f"✓ Updated {len(updates)} UI field(s)")
            return True
        else:
            print(f"✗ Failed to update UI fields: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating UI fields: {e}")
        return False

def handle_preset_change(preset_name: str) -> bool:
    if preset_name == "Custom":
        return True
    
    preset_values = PRESETS.get(preset_name)
    if not preset_values:
        print(f"Unknown preset: {preset_name}")
        return False
    
    print(f"Applying preset: {preset_name}")
    return update_ui_fields(preset_values)

def detect_matching_preset(current_values: dict) -> str:
    for preset_name, preset_values in PRESETS.items():
        matches = True
        
        for param in PRESET_PARAMS:
            current = current_values.get(param, "")
            expected = preset_values.get(param, "")
            
            if current != expected:
                matches = False
                break
        
        if matches:
            return preset_name
    
    return "Custom"

def handle_parameter_change(current_values: dict) -> bool:
    matching_preset = detect_matching_preset(current_values)
    current_preset = current_values.get("preset", "Custom")
    
    if matching_preset != current_preset:
        print(f"Preset changed: {current_preset} → {matching_preset}")
        return update_ui_fields({"preset": matching_preset})
    
    return True

def ensure_vtracer():
    if VTRACER_BIN.exists():
        return True
    
    print("\n" + "=" * 50)
    print("vtracer binary not found - downloading...")
    print("=" * 50)
    print("\nvtracer is required for bitmap to vector conversion.")
    print("Downloading automatically (~2.5MB)...")
    print()
    
    try:
        system = platform.system()
        machine = platform.machine().lower()
        arch = "x86_64" if machine in ["x86_64", "amd64"] else "aarch64"
        
        if system == "Linux":
            url = f"https://github.com/visioncortex/vtracer/releases/download/{VTRACER_VERSION}/vtracer-{arch}-unknown-linux-musl.tar.gz"
        elif system == "Darwin":
            url = f"https://github.com/visioncortex/vtracer/releases/download/{VTRACER_VERSION}/vtracer-{arch}-apple-darwin.tar.gz"
        elif system == "Windows":
            url = f"https://github.com/visioncortex/vtracer/releases/download/{VTRACER_VERSION}/vtracer-x86_64-pc-windows-msvc.zip"
        else:
            print(f"Unsupported OS: {system}")
            return False
        
        print(f"Downloading from: {url}")
        archive_path = VTRACER_BIN.parent / ("vtracer.zip" if url.endswith(".zip") else "vtracer.tar.gz")
        
        urllib.request.urlretrieve(url, archive_path)
        print("Extracting...")
        
        if url.endswith(".zip"):
            with zipfile.ZipFile(archive_path, 'r') as z:
                z.extractall(VTRACER_BIN.parent)
        else:
            with tarfile.open(archive_path, 'r:gz') as t:
                t.extractall(VTRACER_BIN.parent, filter='data')
        
        archive_path.unlink()
        
        if system != "Windows":
            VTRACER_BIN.chmod(0o755)
        
        print("✓ vtracer installed successfully\n")
        
        try:
            requests.post(f"{LUNACY_API}/showtoast", json={
                "text": "vtracer installed successfully",
                "iconType": 2,
                "durationSeconds": 3
            }, timeout=2)
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"✗ Download failed: {e}")
        print("Please run install.py manually or download from:")
        print(f"https://github.com/visioncortex/vtracer/releases/tag/{VTRACER_VERSION}")
        return False

def register_ui():
    ui_config = {
        "pluginId": PLUGIN_ID,
        "title": "Bitmap to Vector",
        "fields": [
            {
                "type": "label",
                "value": f"Plugin v{PLUGIN_VERSION} | vtracer v{VTRACER_VERSION}",
                "description": "Plugin and vectorization engine versions"
            },
            {"type": "separator"},
            {
                "id": "preset",
                "type": "select",
                "label": "Preset",
                "description": "Quick configurations:\n• Photo - detailed, 8-bit color\n• Poster - simplified, 8-bit fewer gradients\n• BW - black/white line art\n• Custom - manual tuning",
                "options": ["Custom", "Photo", "Poster", "BW"],
                "value": "Custom"
            },
            {"type": "separator"},
            {
                "id": "colormode",
                "type": "select",
                "label": "Color Mode",
                "description": "Color: preserves all colors\nBW: pure black and white, ideal for line drawings and logos",
                "options": ["color", "bw"],
                "value": "color"
            },
            {
                "id": "mode",
                "type": "select",
                "label": "Curve Mode",
                "description": "Spline: smooth Bezier curves (organic shapes)\nPolygon: straight line segments (geometric)\nPixel: pixelated/retro art style",
                "options": ["spline", "polygon", "pixel"],
                "value": "spline"
            },
            {
                "id": "hierarchical",
                "type": "select",
                "label": "Hierarchical",
                "description": "Stacked: shapes layered on top (like Photoshop layers)\nCutout: inner shapes cut holes (for logos with knockouts)",
                "options": ["stacked", "cutout"],
                "value": "stacked"
            },
            {"type": "separator"},
            {
                "id": "color_precision",
                "type": "slider",
                "label": "Color Precision (bits)",
                "description": "Controls color quantization: 1 bit = 2 colors, 6 bit = 64 colors, 8 bit = 256 colors\nLower = fewer paths, Higher = more detail",
                "min": 1,
                "max": 8,
                "step": 1,
                "value": "6"
            },
            {
                "id": "filter_speckle",
                "type": "slider",
                "label": "Filter Speckle (px)",
                "description": "Removes noise by discarding isolated regions smaller than N px\nHigher = cleaner result but may lose small details",
                "min": 0,
                "max": 16,
                "step": 1,
                "value": "4"
            },
            {
                "id": "corner_threshold",
                "type": "slider",
                "label": "Corner Threshold (°)",
                "description": "Angle for sharp corners vs smooth curves\nLower = more corners (sharper), Higher = smoother (rounder)",
                "min": 0,
                "max": 180,
                "step": 5,
                "value": "60"
            },
            {
                "id": "gradient_step",
                "type": "slider",
                "label": "Gradient Step",
                "description": "Color similarity threshold for grouping pixels\nLower = more shapes (detailed gradients), Higher = fewer shapes (flatter colors)",
                "min": 0,
                "max": 255,
                "step": 1,
                "value": "16"
            },
            {"type": "separator"},
            {
                "id": "path_precision",
                "type": "number",
                "label": "Path Precision (decimals)",
                "description": "Decimal places in coordinates: 0 = integer pixels (smaller file), 2 = 0.01px precision (smoother)\nHigher = more accurate but larger file size",
                "min": 0,
                "max": 10,
                "step": 1,
                "value": "2"
            },
            {
                "id": "segment_length",
                "type": "number",
                "label": "Segment Length",
                "description": "Target length for path segments\nLower = more control points (accurate but complex), Higher = fewer points (simplified but less precise)",
                "min": 3.5,
                "max": 10,
                "step": 0.5,
                "value": "4"
            },
            {
                "id": "splice_threshold",
                "type": "slider",
                "label": "Splice Threshold (°)",
                "description": "Angle threshold for joining adjacent path segments\nLower = segments separate (detailed), Higher = merges segments (simplified)",
                "min": 0,
                "max": 180,
                "step": 5,
                "value": "45"
            },
            {"type": "separator"},
            {
                "type": "label",
                "value": "⚠️ Select a layer with bitmap fill before converting",
                "description": "Conversion only works on bitmap-filled layers"
            },
            {
                "id": "convert",
                "type": "button",
                "label": "Convert to Vector",
                "description": "Converts selected bitmap layers to editable vector paths using vtracer algorithm"
            },
            {
                "id": "vtracer_repo",
                "type": "linkButton",
                "label": "vtracer on GitHub",
                "value": "https://github.com/visioncortex/vtracer",
                "description": "View vtracer source code and documentation"
            }
        ]
    }
    
    response = requests.post(f"{LUNACY_API}/registerui", json=ui_config)
    if response.ok:
        print("✓ UI registered successfully")
    else:
        print(f"✗ Failed to register UI: {response.status_code}")
        sys.exit(1)

def get_ui_values():
    response = requests.post(
        f"{LUNACY_API}/getpluginuivalues",
        json=PLUGIN_ID,
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    if response.ok:
        return response.json()
    return {}

def apply_preset(preset_name):
    presets = {
        "Photo": {
            "colormode": "color",
            "mode": "spline",
            "hierarchical": "stacked",
            "color_precision": "8",
            "filter_speckle": "10",
            "corner_threshold": "180",
            "gradient_step": "48",
            "path_precision": "2",
            "segment_length": "4",
            "splice_threshold": "45"
        },
        "Poster": {
            "colormode": "color",
            "mode": "spline",
            "hierarchical": "stacked",
            "color_precision": "8",
            "filter_speckle": "4",
            "corner_threshold": "60",
            "gradient_step": "16",
            "path_precision": "2",
            "segment_length": "4",
            "splice_threshold": "45"
        },
        "BW": {
            "colormode": "bw",
            "mode": "spline",
            "hierarchical": "stacked",
            "color_precision": "6",
            "filter_speckle": "4",
            "corner_threshold": "60",
            "gradient_step": "16",
            "path_precision": "2",
            "segment_length": "4",
            "splice_threshold": "45"
        }
    }
    return presets.get(preset_name, {})

def get_image_by_id(image_id, format='png'):
    try:
        response = requests.post(
            f"{LUNACY_API}/getimage",
            json={'imageId': image_id, 'format': format},
            timeout=30
        )
        
        if not response.ok:
            print(f"  Error: HTTP {response.status_code}")
            return None
            
        print(f"  Received {format.upper()}: {len(response.content)} bytes")
        return response.content
    except Exception as e:
        print(f"  Error fetching image: {e}")
        return None

def extract_bitmap_from_layer(layer):
    if not layer:
        return None
    
    fills = layer.get('fills', [])
    for fill in fills:
        if fill.get('type') == 4 and fill.get('pattern'):
            pattern = fill['pattern']
            image_id = pattern.get('image')
            if image_id:
                print(f"  Found pattern fill with image ID: {image_id}")
                return get_image_by_id(image_id, format='png')
    
    return None

def run_vtracer_cli(input_path, output_path, params):
    if not VTRACER_BIN.exists():
        raise FileNotFoundError(f"vtracer binary not found at {VTRACER_BIN}")
    
    cmd = [
        str(VTRACER_BIN),
        "--input", str(input_path),
        "--output", str(output_path),
        "--colormode", params.get("colormode", "color"),
        "--mode", params.get("mode", "spline"),
        "--hierarchical", params.get("hierarchical", "stacked"),
        "--color_precision", params.get("color_precision", "6"),
        "--filter_speckle", params.get("filter_speckle", "4"),
        "--corner_threshold", params.get("corner_threshold", "60"),
        "--gradient_step", params.get("gradient_step", "16"),
        "--path_precision", params.get("path_precision", "2"),
        "--segment_length", params.get("segment_length", "4"),
        "--splice_threshold", params.get("splice_threshold", "45")
    ]
    
    print(f"  Running vtracer...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if result.returncode != 0:
        raise RuntimeError(f"vtracer failed: {result.stderr}")
    
    return result.stdout

def vectorize_selection(params):
    print("Getting selection from Lunacy...")
    response = requests.get(f"{LUNACY_API}/getselected", timeout=10)
    response.raise_for_status()
    
    selection = response.json()
    if isinstance(selection, dict):
        selection = [selection] if selection else []
    
    if not selection:
        print("No objects selected")
        return 0
    
    print(f"Selected: {len(selection)} object(s)\n")
    
    success_count = 0
    
    for i, layer in enumerate(selection):
        print(f"[{i+1}/{len(selection)}] Processing layer: {layer.get('name', 'Unnamed')}")
        
        bitmap_data = extract_bitmap_from_layer(layer)
        if not bitmap_data:
            print(f"  Skipped (no bitmap data)")
            continue
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            input_path = tmpdir_path / "input.png"
            input_path.write_bytes(bitmap_data)
            
            output_path = tmpdir_path / "output.svg"
            
            try:
                run_vtracer_cli(input_path, output_path, params)
                svg_data = output_path.read_bytes()
                
                transform = layer.get('transform', [0, 0])
                x = transform[0] if isinstance(transform, list) and len(transform) >= 1 else 0
                y = transform[1] if isinstance(transform, list) and len(transform) >= 2 else 0
                
                print(f"  Inserting SVG at ({x}, {y})...")
                response = requests.post(
                    f"{LUNACY_API}/insertimage",
                    data=svg_data,
                    headers={
                        'X-Image-Position-X': str(x),
                        'X-Image-Position-Y': str(y),
                        'X-Image-File-Name': f"{layer.get('name', 'vectorized')}.svg"
                    },
                    timeout=30
                )
                
                if response.ok:
                    print(f"  ✓ {response.text}")
                    success_count += 1
                else:
                    print(f"  ✗ Error: {response.status_code}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        print()
    
    return success_count

async def handle_websocket():
    async with websockets.connect(LUNACY_WS) as ws:
        print("✓ Connected to Lunacy WebSocket")
        
        register_message = json.dumps({
            "type": "plugin_register",
            "pluginId": PLUGIN_ID
        })
        await ws.send(register_message)
        print("✓ Sent plugin registration")
        
        async for message in ws:
            data = json.loads(message)
            event_type = data.get('type')
            
            if event_type == 'plugin_initialized':
                print("\n→ Plugin initialized event received")
                register_ui()
                print("→ UI registered successfully")
            
            elif event_type == 'show_ui' and data.get('pluginId') == PLUGIN_ID:
                print("\n→ UI opened by user")
            
            elif event_type == 'close_ui' and data.get('pluginId') == PLUGIN_ID:
                print("\n→ UI closed by user")
            
            elif event_type == 'ui_field_event' and data.get('pluginId') == PLUGIN_ID:
                field_id = data.get('fieldId')
                event_type_detail = data.get('eventType')
                value = data.get('value')
                
                if field_id == 'preset' and event_type_detail == 'value_change':
                    print(f"\n→ Preset changed to: {value}")
                    handle_preset_change(value)
                
                elif field_id in PRESET_PARAMS and event_type_detail == 'value_change':
                    print(f"\n→ Parameter '{field_id}' changed to: {value}")
                    current_values = get_ui_values()
                    current_values[field_id] = value
                    handle_parameter_change(current_values)
                
                elif field_id == 'convert' and event_type_detail == 'click':
                    print("\n→ Convert button clicked")
                    params = get_ui_values()
                    print(f"[DEBUG] Raw params from UI: {json.dumps(params, indent=2)}")
                    
                    preset = params.get('preset', 'Custom')
                    print(f"[DEBUG] Selected preset: {preset}")
                    
                    if preset != 'Custom':
                        preset_params = apply_preset(preset)
                        print(f"[DEBUG] Applying preset params: {json.dumps(preset_params, indent=2)}")
                        params.update(preset_params)
                    
                    print(f"[DEBUG] Final parameters for vtracer: {json.dumps(params, indent=2)}\n")
                    
                    success = vectorize_selection(params)
                    
                    if success > 0:
                        toast = {
                            "text": f"Vectorized {success} layer(s)",
                            "iconType": 2,
                            "durationSeconds": 3
                        }
                    else:
                        toast = {
                            "text": "No bitmap layers found",
                            "iconType": 4,
                            "durationSeconds": 3
                        }
                    
                    requests.post(f"{LUNACY_API}/showtoast", json=toast)

def main():
    print("=" * 50)
    print("Bitmap to Vector Plugin with UI")
    print("=" * 50)
    print()
    
    if not ensure_vtracer():
        print("Cannot start plugin without vtracer binary")
        sys.exit(1)
    
    print("Connecting to Lunacy...")
    print("UI will be registered after initialization")
    print()
    
    try:
        asyncio.run(handle_websocket())
    except KeyboardInterrupt:
        print("\n\n✓ Plugin stopped")

if __name__ == "__main__":
    main()
