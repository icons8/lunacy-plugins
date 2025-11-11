# Quick Start: Interactive UI Plugins

This guide shows you how to create **interactive plugins with UI** using the Smart Duplicate plugin as a real-world example.

If you haven't created a basic plugin yet, start with [QUICK_START.md](./QUICK_START.md) first.

## What You'll Build

A **Smart Duplicate** plugin that:
- Opens an interactive dialog with input fields
- Lets users choose patterns: Grid, Circle, Wave, Spiral
- Duplicates selected layers with the chosen transformation
- Provides real-time feedback via WebSocket events

## Key Concepts

### Service Plugins vs Command Plugins

| Command Plugin | Service Plugin (UI) |
|----------------|---------------------|
| Runs once and exits | Stays running in background |
| No UI interaction | Interactive UI dialog |
| HTTP API only | HTTP API + WebSocket |
| Simple tasks | Complex workflows |

### UI Plugin Architecture

```
┌─────────────┐     WebSocket      ┌──────────────┐
│   Lunacy    │ ◄─────────────────►│ Your Plugin  │
└─────────────┘                    └──────────────┘
      │                                    │
      │         HTTP REST API              │
      └────────────────────────────────────┘
      
Events: plugin_initialized, show_ui, close_ui, ui_field_event
API:    /registerui, /getpluginuivalues, /showtoast, /duplicatelayers
```

## Prerequisites

Same as [QUICK_START.md](./QUICK_START.md), plus:
- Understanding of async/await patterns
- Basic WebSocket knowledge helpful (but not required)

## Implementation Guide

Choose **one** language below. All implementations are fully working and tested.

**Language Comparison:**
- **Node.js** - Fast development, good performance, minimal setup
- **Python** - Easy to read, great for prototyping, extensive libraries
- **C#** - Best performance when compiled, strongly typed, modern features

**Performance Note:** C# plugins can be compiled to native binaries for 20-30x faster startup compared to `dotnet run`. See step 6 in the C# section.

---

## Node.js Implementation

### 1. Create Plugin Directory

```bash
# Linux
mkdir -p ~/.local/share/Icons8/Lunacy/Plugins/smart-duplicate-node
cd ~/.local/share/Icons8/Lunacy/Plugins/smart-duplicate-node

# Windows
mkdir %APPDATA%\Icons8\Lunacy\Plugins\smart-duplicate-node
cd %APPDATA%\Icons8\Lunacy\Plugins\smart-duplicate-node

# macOS
mkdir -p ~/Library/Application\ Support/Icons8/Lunacy/Plugins/smart-duplicate-node
cd ~/Library/Application\ Support/Icons8/Lunacy/Plugins/smart-duplicate-node
```

### 2. Create `plugin.jsonc`

```jsonc
{
  "id": "smart-duplicate-node",
  "name": "Smart Duplicate (Node.js)",
  "description": "Advanced layer duplication with preset patterns",
  "version": "1.0.0",
  "services": [
    {
      "id": "smart-duplicate-service",
      "name": "Smart Duplicate Service",
      "executable": "node",
      "args": ["smart-duplicate.js"]
    }
  ]
}
```

**Note:** Services use `"services"` array, not `"commands"` - they run continuously.

### 3. Create `package.json`

```json
{
  "name": "smart-duplicate-node",
  "version": "1.0.0",
  "dependencies": {
    "ws": "^8.14.0"
  }
}
```

### 4. Install Dependencies

```bash
npm install
```

### 5. Create `smart-duplicate.js`

```javascript
#!/usr/bin/env node

const WebSocket = require('ws');

const LUNACY_API = 'http://localhost:31415';
const LUNACY_WS = 'ws://localhost:31416';
const PLUGIN_ID = 'smart-duplicate-node';

let ws = null;

async function registerUi() {
  const uiDefinition = {
    pluginId: PLUGIN_ID,
    title: 'Smart Duplicate',
    fields: [
      {
        id: 'preset',
        type: 'select',
        label: 'Preset Pattern',
        value: 'grid',
        options: ['grid', 'circle', 'wave', 'spiral'],
        description: 'Select transformation pattern'
      },
      {
        id: 'sep1',
        type: 'separator',
        label: 'Duplication Settings'
      },
      {
        id: 'count',
        type: 'number',
        label: 'Count',
        value: '5',
        min: 1,
        max: 50,
        step: 1,
        description: 'Number of copies to create'
      },
      {
        id: 'spacingX',
        type: 'number',
        label: 'Spacing X (px)',
        value: '100',
        min: -500,
        max: 500,
        step: 10,
        description: 'Horizontal spacing between copies'
      },
      {
        id: 'spacingY',
        type: 'number',
        label: 'Spacing Y (px)',
        value: '100',
        min: -500,
        max: 500,
        step: 10,
        description: 'Vertical spacing between copies'
      },
      {
        id: 'sep2',
        type: 'separator'
      },
      {
        id: 'apply',
        type: 'button',
        label: 'Apply Duplication'
      }
    ]
  };

  try {
    const response = await fetch(`${LUNACY_API}/registerui`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(uiDefinition)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    console.log('✓ UI registered successfully');
    return true;
  } catch (error) {
    console.error(`✗ Failed to register UI: ${error.message}`);
    return false;
  }
}

async function unregisterUi() {
  try {
    await fetch(`${LUNACY_API}/unregisterui`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(PLUGIN_ID)
    });
    console.log('✓ UI unregistered');
  } catch (error) {
    console.error(`✗ Failed to unregister UI: ${error.message}`);
  }
}

async function showToast(message, iconType = 2) {
  try {
    await fetch(`${LUNACY_API}/showtoast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: message, iconType })
    });
  } catch (error) {
    console.warn(`Warning: Failed to show toast: ${error.message}`);
  }
}

async function getFieldValues() {
  try {
    const response = await fetch(`${LUNACY_API}/getpluginuivalues`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(PLUGIN_ID)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`❌ Error getting field values: ${error.message}`);
    return {};
  }
}

function calculateGridPositions(count, spacingX, spacingY, layerWidth, layerHeight) {
  const positions = [];
  const gridSize = Math.ceil(Math.sqrt(count));

  for (let i = 0; i < count; i++) {
    const row = Math.floor(i / gridSize);
    const col = i % gridSize;
    const offsetX = col * (layerWidth + spacingX);
    const offsetY = row * (layerHeight + spacingY);
    
    if (i === 0) {
      continue;
    }
    
    positions.push({
      x: offsetX,
      y: offsetY,
      rotation: 0
    });
  }

  return positions;
}

function calculateCirclePositions(count, spacingX, spacingY) {
  const positions = [];
  const radius = Math.max(Math.abs(spacingX), Math.abs(spacingY));

  for (let i = 0; i < count; i++) {
    if (i === 0) {
      continue;
    }
    
    const angle = (2 * Math.PI * i) / count - Math.PI / 2;
    
    const offsetX = radius * (Math.cos(angle) - Math.cos(-Math.PI / 2));
    const offsetY = radius * (Math.sin(angle) - Math.sin(-Math.PI / 2));
    
    positions.push({
      x: offsetX,
      y: offsetY,
      rotation: (angle * 180 / Math.PI) + 90
    });
  }

  return positions;
}

function calculateWavePositions(count, spacingX, spacingY) {
  const positions = [];
  const amplitude = Math.abs(spacingY);
  const horizontalSpacing = Math.abs(spacingX);

  for (let i = 0; i < count; i++) {
    if (i === 0) {
      continue;
    }
    
    const offsetX = i * horizontalSpacing;
    const offsetY = amplitude * Math.sin(2 * Math.PI * i / count);
    
    const derivative = (2 * Math.PI / count) * amplitude * Math.cos(2 * Math.PI * i / count);
    const rotation = horizontalSpacing > 0 ? Math.atan(derivative / horizontalSpacing) * 180 / Math.PI : 0;
    
    positions.push({
      x: offsetX,
      y: offsetY,
      rotation: rotation
    });
  }

  return positions;
}

function calculateSpiralPositions(count, spacingX, spacingY) {
  const positions = [];
  const radiusIncrement = Math.max(Math.abs(spacingX), Math.abs(spacingY)) / count;

  for (let i = 0; i < count; i++) {
    if (i === 0) {
      continue;
    }
    
    const angle = (2 * Math.PI * i) / count - Math.PI / 2;
    const radius = radiusIncrement * i;
    const offsetX = radius * (Math.cos(angle) - Math.cos(-Math.PI / 2));
    const offsetY = radius * (Math.sin(angle) - Math.sin(-Math.PI / 2));
    
    positions.push({
      x: offsetX,
      y: offsetY,
      rotation: (angle * 180 / Math.PI) + 90
    });
  }

  return positions;
}


async function applySmartDuplicate(values) {
  try {
    const preset = values.preset || 'grid';
    const count = parseInt(values.count || 5);
    const spacingX = parseFloat(values.spacingX || 100);
    const spacingY = parseFloat(values.spacingY || 100);

    console.log(`Applying Applying ${preset} preset with ${count} copies...`);
    await showToast(`Creating ${count} copies using ${preset} pattern...`, 5);

    const selectionResponse = await fetch(`${LUNACY_API}/getselected`);
    if (!selectionResponse.ok) {
      throw new Error('Failed to get selection');
    }

    let selection = await selectionResponse.json();
    if (!Array.isArray(selection)) {
      selection = selection ? [selection] : [];
    }

    if (selection.length === 0) {
      console.log('❌ No layers selected');
      await showToast('Please select at least one layer', 4);
      return false;
    }

    const layerIds = selection.map(layer => layer.id);
    console.log(`✓ Selected ${layerIds.length} layer(s)`);

    const layerWidth = selection[0].size ? selection[0].size[0] : 100;
    const layerHeight = selection[0].size ? selection[0].size[1] : 100;

    let positions;
    switch (preset) {
      case 'grid':
        positions = calculateGridPositions(count, spacingX, spacingY, layerWidth, layerHeight);
        break;
      case 'circle':
        positions = calculateCirclePositions(count, spacingX, spacingY);
        break;
      case 'wave':
        positions = calculateWavePositions(count, spacingX, spacingY);
        break;
      case 'spiral':
        positions = calculateSpiralPositions(count, spacingX, spacingY);
        break;
      default:
        console.log(`❌ Unknown preset: ${preset}`);
        await showToast(`Unknown preset: ${preset}`, 4);
        return false;
    }

    let duplicatedCount = 0;

    for (let i = 0; i < positions.length; i++) {
      try {
        const pos = positions[i];

        const dupResponse = await fetch(`${LUNACY_API}/duplicatelayers`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            layerIds: layerIds,
            offsetX: pos.x,
            offsetY: pos.y,
            componentsToInstances: false
          })
        });

        if (!dupResponse.ok) {
          throw new Error(`Duplication failed: HTTP ${dupResponse.status}`);
        }

        const result = JSON.parse(await dupResponse.text());
        const newLayerIds = result.duplicatedLayerIds || [];

        if (newLayerIds.length > 0) {
          duplicatedCount += newLayerIds.length;
        }
      } catch (error) {
        console.warn(`Warning: Failed to process copy ${i + 1}: ${error.message}`);
      }
    }

    console.log(`✓ Created ${duplicatedCount} duplicates using ${preset} preset`);
    await showToast(`Created ${duplicatedCount} copies successfully!`, 2);
    return true;

  } catch (error) {
    console.error(`❌ Error applying duplication: ${error.message}`);
    await showToast(`Error: ${error.message}`, 4);
    return false;
  }
}

function onMessage(message) {
  try {
    const data = JSON.parse(message);
    const eventType = data.type;

    if (eventType === 'plugin_initialized') {
      console.log('\n📨 Received plugin_initialized event');
      registerUi();
    } else if (eventType === 'show_ui') {
      console.log('\n📨 UI dialog opened by user');
    } else if (eventType === 'close_ui') {
      console.log('\n📨 UI dialog closed by user');
    } else if (eventType === 'ui_field_event') {
      const fieldId = data.fieldId;
      const eventTypeDetail = data.eventType;

      if (fieldId === 'apply' && eventTypeDetail === 'click') {
        console.log('\n🔍 Apply button clicked - getting values...');
        getFieldValues().then(values => {
          applySmartDuplicate(values);
        });
      }
    }
  } catch (error) {
    console.error(`❌ Error processing message: ${error.message}`);
  }
}

function runService() {
  console.log('Starting Smart Duplicate Plugin starting...');
  console.log('Waiting for Lunacy to initialize plugin...');

  ws = new WebSocket(LUNACY_WS);

  ws.on('open', () => {
    console.log('✓ WebSocket connected');
    const registerMessage = JSON.stringify({
      type: 'plugin_register',
      pluginId: PLUGIN_ID
    });
    ws.send(registerMessage);
    console.log('✓ Sent plugin registration');
  });

  ws.on('message', (data) => {
    onMessage(data.toString());
  });

  ws.on('error', (error) => {
    console.error(`WebSocket error: ${error.message}`);
  });

  ws.on('close', () => {
    console.log('WebSocket connection closed');
  });
}

process.on('SIGINT', async () => {
  console.log('\n🛑 Service stopped by user');
  await unregisterUi();
  if (ws) ws.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Service terminated');
  await unregisterUi();
  if (ws) ws.close();
  process.exit(0);
});

runService();
```

### 6. Test the Plugin

```bash
# Test directly (Lunacy must be running)
node smart-duplicate.js

# In Lunacy:
# 1. Restart Lunacy
# 2. Select a layer
# 3. Go to Plugins menu → Smart Duplicate (Node.js)
# 4. Try different presets: Grid, Circle, Wave, Spiral
```

---

## Python Implementation

### 1. Create Plugin Directory

```bash
# Same paths as Node.js, just use "smart-duplicate-python"
mkdir -p ~/.local/share/Icons8/Lunacy/Plugins/smart-duplicate-python
cd ~/.local/share/Icons8/Lunacy/Plugins/smart-duplicate-python
```

### 2. Create `plugin.jsonc`

```jsonc
{
  "id": "smart-duplicate-python",
  "name": "Smart Duplicate (Python)",
  "description": "Advanced layer duplication with preset patterns",
  "version": "1.0.0",
  "services": [
    {
      "id": "smart-duplicate-service",
      "name": "Smart Duplicate Service",
      "executable": "python3",
      "args": ["smart_duplicate.py"]
    }
  ]
}
```

### 3. Create `requirements.txt`

```txt
requests>=2.31.0
websockets>=12.0
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Create `smart_duplicate.py`

```python
#!/usr/bin/env python3
import requests
import json
import sys
import asyncio
import websockets
import math
import copy

LUNACY_API = "http://localhost:31415"
LUNACY_WS = "ws://localhost:31416"
PLUGIN_ID = "smart-duplicate-python"

def register_ui():
    """Register UI with preset-based duplication controls"""
    ui_definition = {
        "pluginId": PLUGIN_ID,
        "title": "Smart Duplicate",
        "fields": [
            {
                "id": "preset",
                "type": "select",
                "label": "Preset Pattern",
                "value": "grid",
                "options": ["grid", "circle", "wave", "spiral"],
                "description": "Select transformation pattern"
            },
            {
                "id": "sep1",
                "type": "separator",
                "label": "Duplication Settings"
            },
            {
                "id": "count",
                "type": "number",
                "label": "Count",
                "value": "5",
                "min": 1,
                "max": 50,
                "step": 1,
                "description": "Number of copies to create"
            },
            {
                "id": "spacingX",
                "type": "number",
                "label": "Spacing X (px)",
                "value": "100",
                "min": -500,
                "max": 500,
                "step": 10,
                "description": "Horizontal spacing between copies"
            },
            {
                "id": "spacingY",
                "type": "number",
                "label": "Spacing Y (px)",
                "value": "100",
                "min": -500,
                "max": 500,
                "step": 10,
                "description": "Vertical spacing between copies"
            },
            {
                "id": "sep2",
                "type": "separator"
            },
            {
                "id": "apply",
                "type": "button",
                "label": "Apply Duplication"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{LUNACY_API}/registerui",
            json=ui_definition,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        response.raise_for_status()
        print(f"✓ UI registered successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to register UI: {e}")
        return False

def unregister_ui():
    """Unregister UI from Lunacy"""
    try:
        response = requests.post(
            f"{LUNACY_API}/unregisterui",
            json=PLUGIN_ID,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print(f"✓ UI unregistered")
    except Exception as e:
        print(f"✗ Failed to unregister UI: {e}")

def show_toast(message, icon_type=2):
    """Show toast notification"""
    try:
        requests.post(
            f"{LUNACY_API}/showtoast",
            json={"text": message, "iconType": icon_type},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
    except Exception as e:
        print(f"Warning: Failed to show toast: {e}")

def get_field_values():
    """Get current UI field values from Lunacy"""
    try:
        response = requests.post(
            f"{LUNACY_API}/getpluginuivalues",
            json=PLUGIN_ID,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error getting field values: {e}")
        return {}

def calculate_grid_positions(count, spacing_x, spacing_y, layer_width, layer_height):
    """Calculate positions for grid layout with spacing between objects
    count includes the original, so we create count-1 copies
    """
    positions = []
    grid_size = math.ceil(math.sqrt(count))
    
    for i in range(count):
        row = i // grid_size
        col = i % grid_size
        offset_x = col * (layer_width + spacing_x)
        offset_y = row * (layer_height + spacing_y)
        
        if i == 0:
            continue
        
        positions.append({
            'x': offset_x,
            'y': offset_y,
            'rotation': 0
        })
    
    return positions

def calculate_circle_positions(count, spacing_x, spacing_y):
    """Calculate positions for circular layout
    All objects (including original) are placed evenly on circle
    Original at 12 o'clock position (top), copies continue clockwise
    """
    positions = []
    radius = max(abs(spacing_x), abs(spacing_y))
    
    for i in range(count):
        if i == 0:
            continue
        
        angle = (2 * math.pi * i) / count - math.pi / 2
        
        offset_x = radius * (math.cos(angle) - math.cos(-math.pi / 2))
        offset_y = radius * (math.sin(angle) - math.sin(-math.pi / 2))
        
        positions.append({
            'x': offset_x,
            'y': offset_y,
            'rotation': math.degrees(angle) + 90
        })
    
    return positions

def calculate_wave_positions(count, spacing_x, spacing_y):
    """Calculate positions for wave pattern
    Objects are placed horizontally with sinusoidal vertical offset
    Spacing X = horizontal distance between objects
    Spacing Y = wave amplitude (vertical oscillation height)
    """
    positions = []
    amplitude = abs(spacing_y)
    horizontal_spacing = abs(spacing_x)
    
    for i in range(count):
        if i == 0:
            continue
        
        offset_x = i * horizontal_spacing
        offset_y = amplitude * math.sin(2 * math.pi * i / count)
        
        derivative = (2 * math.pi / count) * amplitude * math.cos(2 * math.pi * i / count)
        rotation = math.degrees(math.atan(derivative / horizontal_spacing)) if horizontal_spacing > 0 else 0
        
        positions.append({
            'x': offset_x,
            'y': offset_y,
            'rotation': rotation
        })
    
    return positions

def calculate_spiral_positions(count, spacing_x, spacing_y):
    """Calculate positions for spiral pattern
    Like a circle but with continuously increasing radius
    Spacing controls the distance between each turn of the spiral
    """
    positions = []
    radius_increment = max(abs(spacing_x), abs(spacing_y)) / count
    
    for i in range(count):
        if i == 0:
            continue
        
        angle = (2 * math.pi * i) / count - math.pi / 2
        radius = radius_increment * i
        offset_x = radius * (math.cos(angle) - math.cos(-math.pi / 2))
        offset_y = radius * (math.sin(angle) - math.sin(-math.pi / 2))
        
        positions.append({
            'x': offset_x,
            'y': offset_y,
            'rotation': math.degrees(angle) + 90
        })
    
    return positions


def apply_smart_duplicate(values):
    """Apply smart duplication with selected preset"""
    try:
        preset = values.get('preset', 'grid')
        count = int(values.get('count', 5))
        spacing_x = float(values.get('spacingX', 100))
        spacing_y = float(values.get('spacingY', 100))
        
        print(f"Applying Applying {preset} preset with {count} copies...")
        show_toast(f"Creating {count} copies using {preset} pattern...", 5)
        
        response = requests.get(f"{LUNACY_API}/getselected", timeout=10)
        response.raise_for_status()
        selection = response.json()
        
        if isinstance(selection, dict):
            selection = [selection] if selection else []
        
        if not selection:
            print("❌ No layers selected")
            show_toast("Please select at least one layer", 4)
            return False
        
        layer_ids = [layer['id'] for layer in selection]
        print(f"✓ Selected {len(layer_ids)} layer(s)")
        
        layer_size = selection[0].get('size', [100, 100])
        layer_width = layer_size[0]
        layer_height = layer_size[1]
        
        if preset == 'grid':
            positions = calculate_grid_positions(count, spacing_x, spacing_y, layer_width, layer_height)
        elif preset == 'circle':
            positions = calculate_circle_positions(count, spacing_x, spacing_y)
        elif preset == 'wave':
            positions = calculate_wave_positions(count, spacing_x, spacing_y)
        elif preset == 'spiral':
            positions = calculate_spiral_positions(count, spacing_x, spacing_y)
        else:
            print(f"❌ Unknown preset: {preset}")
            show_toast(f"Unknown preset: {preset}", 4)
            return False
        
        duplicated_count = 0
        
        for i, pos in enumerate(positions):
            try:
                offset_x = pos['x']
                offset_y = pos['y']
                
                dup_response = requests.post(
                    f"{LUNACY_API}/duplicatelayers",
                    json={
                        "layerIds": layer_ids,
                        "offsetX": offset_x,
                        "offsetY": offset_y,
                        "componentsToInstances": False
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                dup_response.raise_for_status()
                
                result = json.loads(dup_response.text)
                new_layer_ids = result.get('duplicatedLayerIds', [])
                
                if new_layer_ids:
                    duplicated_count += len(new_layer_ids)
                
            except Exception as e:
                print(f"Warning: Failed to process copy {i+1}: {e}")
        
        print(f"✓ Created {duplicated_count} duplicates using {preset} preset")
        show_toast(f"Created {duplicated_count} copies successfully!", 2)
        return True
        
    except Exception as e:
        print(f"❌ Error applying duplication: {e}")
        show_toast(f"Error: {str(e)}", 4)
        return False

async def handle_websocket():
    """Main WebSocket handler using asyncio"""
    async with websockets.connect(LUNACY_WS) as ws:
        print("✓ WebSocket connected")
        
        register_message = json.dumps({
            "type": "plugin_register",
            "pluginId": PLUGIN_ID
        })
        await ws.send(register_message)
        print("✓ Sent plugin registration")
        
        async for message in ws:
            try:
                data = json.loads(message)
                event_type = data.get('type')
                
                if event_type == 'plugin_initialized':
                    print("\n📨 Received plugin_initialized event")
                    register_ui()
                    
                elif event_type == 'show_ui' and data.get('pluginId') == PLUGIN_ID:
                    print("\n📨 UI dialog opened by user")
                    
                elif event_type == 'close_ui' and data.get('pluginId') == PLUGIN_ID:
                    print("\n📨 UI dialog closed by user")
                    
                elif event_type == 'ui_field_event' and data.get('pluginId') == PLUGIN_ID:
                    field_id = data.get('fieldId')
                    event_type_detail = data.get('eventType')
                    
                    if field_id == 'apply' and event_type_detail == 'click':
                        print("\n🔍 Apply button clicked - getting values...")
                        values = get_field_values()
                        apply_smart_duplicate(values)
                        
            except Exception as e:
                print(f"❌ Error processing message: {e}")

def main():
    """Main entry point"""
    print("Starting Smart Duplicate Plugin starting...")
    print("Waiting for Lunacy to initialize plugin...")
    print()
    
    try:
        asyncio.run(handle_websocket())
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
        unregister_ui()
    except Exception as e:
        print(f"❌ Service error: {e}")
        unregister_ui()
    finally:
        print("👋 Service terminated")

if __name__ == "__main__":
    main()
```

**Key Python Features:**
- **asyncio/websockets** - Modern async WebSocket handling with `async with` and `async for`
- **requests** - Simple synchronous HTTP calls for API
- **math module** - Trigonometric functions for position calculations
- **Type flexibility** - Easy dict/list handling with `.get()` defaults
- **Error handling** - Try/except with graceful degradation

---

## C# Implementation

### 1. Create Plugin Directory

```bash
mkdir -p ~/.local/share/Icons8/Lunacy/Plugins/smart-duplicate-csharp
cd ~/.local/share/Icons8/Lunacy/Plugins/smart-duplicate-csharp
```

### 2. Create `plugin.jsonc`

```jsonc
{
  "id": "smart-duplicate-csharp",
  "name": "Smart Duplicate (C#)",
  "description": "Advanced layer duplication with preset patterns",
  "version": "1.0.0",
  "services": [
    {
      "id": "smart-duplicate-service",
      "name": "Smart Duplicate Service",
      "executable": "dotnet",
      "args": ["run", "--project", "SmartDuplicateCSharp.csproj"]
    }
  ]
}
```

### 3. Create `SmartDuplicateCSharp.csproj`

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="System.Net.Http.Json" Version="9.0.0" />
    <PackageReference Include="System.Net.WebSockets.Client" Version="9.0.0" />
  </ItemGroup>
</Project>
```

### 4. Create `Program.cs`

```csharp
using System.Net.Http.Json;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace SmartDuplicatePlugin;

public static class Program
{
    private const string ApiUrl = "http://localhost:31415";
    private const string WsUrl = "ws://localhost:31416";
    private const string PluginId = "smart-duplicate-csharp";

    public static async Task Main()
    {
        Console.WriteLine("Starting Smart Duplicate Plugin starting...");
        Console.WriteLine("Waiting for Lunacy to initialize plugin...");

        using var httpClient = new HttpClient();
        using var ws = new ClientWebSocket();

        try
        {
            await ws.ConnectAsync(new Uri(WsUrl), CancellationToken.None);
            Console.WriteLine("✓ WebSocket connected");

            var registerMessage = JsonSerializer.Serialize(new PluginRegisterMessage
            {
                Type = "plugin_register",
                PluginId = PluginId
            }, SmartDuplicateJsonContext.Default.PluginRegisterMessage);
            await ws.SendAsync(
                Encoding.UTF8.GetBytes(registerMessage),
                WebSocketMessageType.Text,
                true,
                CancellationToken.None
            );
            Console.WriteLine("✓ Sent plugin registration");

            var buffer = new byte[8192];

            while (ws.State == WebSocketState.Open)
            {
                var result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);

                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
                    break;
                }

                var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                await MessageHandler.HandleMessage(message, httpClient);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Service error: {ex.Message}");
        }
        finally
        {
            await UiManager.UnregisterUi(httpClient);
            Console.WriteLine("👋 Service terminated");
        }
    }

    private static class MessageHandler
    {
        public static async Task HandleMessage(string message, HttpClient httpClient)
        {
            try
            {
                var pluginEvent = JsonSerializer.Deserialize(message, SmartDuplicateJsonContext.Default.PluginEvent);
                if (pluginEvent == null)
                {
                    return;
                }

                switch (pluginEvent.Type)
                {
                    case "plugin_initialized":
                        Console.WriteLine("\n📨 Received plugin_initialized event");
                        await UiManager.RegisterUi(httpClient);
                        break;

                    case "show_ui":
                        Console.WriteLine("\n📨 UI dialog opened by user");
                        break;

                    case "close_ui":
                        Console.WriteLine("\n📨 UI dialog closed by user");
                        break;

                    case "ui_field_event":
                        if (pluginEvent.FieldId == "apply" && pluginEvent.EventType == "click")
                        {
                            Console.WriteLine("\n🔍 Apply button clicked - getting values...");
                            var values = await UiManager.GetFieldValues(httpClient);
                            await DuplicationEngine.ApplySmartDuplicate(values, httpClient);
                        }
                        break;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error processing message: {ex.Message}");
            }
        }
    }

    private static class UiManager
    {
        public static async Task RegisterUi(HttpClient httpClient)
        {
            var uiDefinition = new PluginUiDefinition
            {
                PluginId = PluginId,
                Title = "Smart Duplicate",
                Fields =
                [
                    new() { Id = "preset", Type = "select", Label = "Preset Pattern", Value = "grid", Options = ["grid", "circle", "wave", "spiral"], Description = "Select transformation pattern" },
                    new() { Id = "sep1", Type = "separator", Label = "Duplication Settings" },
                    new() { Id = "count", Type = "number", Label = "Count", Value = "5", Min = 1, Max = 50, Step = 1, Description = "Number of copies to create" },
                    new() { Id = "spacingX", Type = "number", Label = "Spacing X (px)", Value = "100", Min = -500, Max = 500, Step = 10, Description = "Horizontal spacing between copies" },
                    new() { Id = "spacingY", Type = "number", Label = "Spacing Y (px)", Value = "100", Min = -500, Max = 500, Step = 10, Description = "Vertical spacing between copies" },
                    new() { Id = "sep2", Type = "separator" },
                    new() { Id = "apply", Type = "button", Label = "Apply Duplication" }
                ]
            };

            try
            {
                var json = JsonSerializer.Serialize(uiDefinition, SmartDuplicateJsonContext.Default.PluginUiDefinition);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                var response = await httpClient.PostAsync($"{ApiUrl}/registerui", content);
                response.EnsureSuccessStatusCode();
                Console.WriteLine("✓ UI registered successfully");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"✗ Failed to register UI: {ex.Message}");
            }
        }

        public static async Task UnregisterUi(HttpClient httpClient)
        {
            try
            {
                var content = new StringContent($"\"{PluginId}\"", Encoding.UTF8, "application/json");
                await httpClient.PostAsync($"{ApiUrl}/unregisterui", content);
                Console.WriteLine("✓ UI unregistered");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"✗ Failed to unregister UI: {ex.Message}");
            }
        }

        public static async Task ShowToast(string message, int iconType, HttpClient httpClient)
        {
            try
            {
                var toastMessage = new ShowToastMessage
                {
                    Text = message,
                    IconType = iconType
                };
                var json = JsonSerializer.Serialize(toastMessage, SmartDuplicateJsonContext.Default.ShowToastMessage);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                await httpClient.PostAsync($"{ApiUrl}/showtoast", content);
            }
            catch
            {
            }
        }

        public static async Task<Dictionary<string, string>> GetFieldValues(HttpClient httpClient)
        {
            try
            {
                var content = new StringContent($"\"{PluginId}\"", Encoding.UTF8, "application/json");
                var response = await httpClient.PostAsync($"{ApiUrl}/getpluginuivalues", content);
                response.EnsureSuccessStatusCode();
                var json = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize(json, SmartDuplicateJsonContext.Default.DictionaryStringString) ?? [];
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error getting field values: {ex.Message}");
                return [];
            }
        }
    }

    private static class PositionCalculator
    {
        public static List<Position> CalculateGridPositions(int count, double spacingX, double spacingY, double layerWidth, double layerHeight)
        {
            var positions = new List<Position>();
            var gridSize = (int)Math.Ceiling(Math.Sqrt(count));

            for (int i = 0; i < count; i++)
            {
                int row = i / gridSize;
                int col = i % gridSize;
                var offsetX = col * (layerWidth + spacingX);
                var offsetY = row * (layerHeight + spacingY);
                
                if (i == 0)
                {
                    continue;
                }
                
                positions.Add(new Position
                {
                    X = offsetX,
                    Y = offsetY,
                    Rotation = 0
                });
            }

            return positions;
        }

        public static List<Position> CalculateCirclePositions(int count, double spacingX, double spacingY)
        {
            var positions = new List<Position>();
            var radius = Math.Max(Math.Abs(spacingX), Math.Abs(spacingY));

            for (int i = 0; i < count; i++)
            {
                if (i == 0)
                {
                    continue;
                }
                
                var angle = (2 * Math.PI * i) / count - Math.PI / 2;
                
                var offsetX = radius * (Math.Cos(angle) - Math.Cos(-Math.PI / 2));
                var offsetY = radius * (Math.Sin(angle) - Math.Sin(-Math.PI / 2));
                
                positions.Add(new Position
                {
                    X = offsetX,
                    Y = offsetY,
                    Rotation = (angle * 180 / Math.PI) + 90
                });
            }

            return positions;
        }

        public static List<Position> CalculateWavePositions(int count, double spacingX, double spacingY)
        {
            var positions = new List<Position>();
            var amplitude = Math.Abs(spacingY);
            var horizontalSpacing = Math.Abs(spacingX);

            for (int i = 0; i < count; i++)
            {
                if (i == 0)
                {
                    continue;
                }
                
                var offsetX = i * horizontalSpacing;
                var offsetY = amplitude * Math.Sin(2 * Math.PI * i / count);
                
                var derivative = (2 * Math.PI / count) * amplitude * Math.Cos(2 * Math.PI * i / count);
                var rotation = horizontalSpacing > 0 ? Math.Atan(derivative / horizontalSpacing) * 180 / Math.PI : 0;
                
                positions.Add(new Position
                {
                    X = offsetX,
                    Y = offsetY,
                    Rotation = rotation
                });
            }

            return positions;
        }

        public static List<Position> CalculateSpiralPositions(int count, double spacingX, double spacingY)
        {
            var positions = new List<Position>();
            var radiusIncrement = Math.Max(Math.Abs(spacingX), Math.Abs(spacingY)) / count;

            for (int i = 0; i < count; i++)
            {
                if (i == 0)
                {
                    continue;
                }
                
                var angle = (2 * Math.PI * i) / count - Math.PI / 2;
                var radius = radiusIncrement * i;
                var offsetX = radius * (Math.Cos(angle) - Math.Cos(-Math.PI / 2));
                var offsetY = radius * (Math.Sin(angle) - Math.Sin(-Math.PI / 2));
                
                positions.Add(new Position
                {
                    X = offsetX,
                    Y = offsetY,
                    Rotation = (angle * 180 / Math.PI) + 90
                });
            }

            return positions;
        }
    }

    private static class DuplicationEngine
    {
        public static async Task ApplySmartDuplicate(Dictionary<string, string> values, HttpClient httpClient)
        {
            try
            {
                var preset = values.GetValueOrDefault("preset", "grid");
                var count = int.Parse(values.GetValueOrDefault("count", "5"));
                var spacingX = double.Parse(values.GetValueOrDefault("spacingX", "100"));
                var spacingY = double.Parse(values.GetValueOrDefault("spacingY", "100"));

                Console.WriteLine($"Applying Applying {preset} preset with {count} copies...");
                await UiManager.ShowToast($"Creating {count} copies using {preset} pattern...", 5, httpClient);

                var selectionResponse = await httpClient.GetAsync($"{ApiUrl}/getselected");
                selectionResponse.EnsureSuccessStatusCode();
                
                var selectionJson = await selectionResponse.Content.ReadAsStringAsync();
                
                LayerData[]? selection;
                try
                {
                    selection = JsonSerializer.Deserialize(selectionJson, SmartDuplicateJsonContext.Default.LayerDataArray);
                }
                catch
                {
                    var singleLayer = JsonSerializer.Deserialize(selectionJson, SmartDuplicateJsonContext.Default.LayerData);
                    selection = singleLayer != null ? [singleLayer] : null;
                }

                if (selection == null || selection.Length == 0)
                {
                    Console.WriteLine("❌ No layers selected");
                    await UiManager.ShowToast("Please select at least one layer", 4, httpClient);
                    return;
                }

                var layerIds = selection.Select(l => l.Id).ToArray();
                Console.WriteLine($"✓ Selected {layerIds.Length} layer(s)");

                var size = selection[0].Size;
                var layerWidth = size != null && size.Length >= 1 ? size[0] : 100.0;
                var layerHeight = size != null && size.Length >= 2 ? size[1] : 100.0;

                List<Position> positions = preset switch
                {
                    "grid" => PositionCalculator.CalculateGridPositions(count, spacingX, spacingY, layerWidth, layerHeight),
                    "circle" => PositionCalculator.CalculateCirclePositions(count, spacingX, spacingY),
                    "wave" => PositionCalculator.CalculateWavePositions(count, spacingX, spacingY),
                    "spiral" => PositionCalculator.CalculateSpiralPositions(count, spacingX, spacingY),
                    _ => throw new ArgumentException($"Unknown preset: {preset}")
                };

                int duplicatedCount = 0;

                for (int i = 0; i < positions.Count; i++)
                {
                    try
                    {
                        var pos = positions[i];

                        var dupRequest = new DuplicateLayersRequest
                        {
                            LayerIds = layerIds!,
                            OffsetX = pos.X,
                            OffsetY = pos.Y,
                            ComponentsToInstances = false
                        };

                        var dupJson = JsonSerializer.Serialize(dupRequest, SmartDuplicateJsonContext.Default.DuplicateLayersRequest);
                        var dupContent = new StringContent(dupJson, Encoding.UTF8, "application/json");
                        var dupResponse = await httpClient.PostAsync($"{ApiUrl}/duplicatelayers", dupContent);
                        dupResponse.EnsureSuccessStatusCode();

                        var result = await dupResponse.Content.ReadFromJsonAsync(SmartDuplicateJsonContext.Default.DuplicateLayersResponse);
                        
                        if (result?.DuplicatedLayerIds != null && result.DuplicatedLayerIds.Length > 0)
                        {
                            duplicatedCount += result.DuplicatedLayerIds.Length;
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Warning: Failed to process copy {i + 1}: {ex.Message}");
                    }
                }

                Console.WriteLine($"✓ Created {duplicatedCount} duplicates using {preset} preset");
                await UiManager.ShowToast($"Created {duplicatedCount} copies successfully!", 2, httpClient);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error applying duplication: {ex.Message}");
                await UiManager.ShowToast($"Error: {ex.Message}", 4, httpClient);
            }
        }
    }

    private sealed record Position
    {
        public double X { get; init; }
        public double Y { get; init; }
        public double Rotation { get; init; }
    }
}

internal sealed record PluginRegisterMessage
{
    [JsonPropertyName("type")]
    public string Type { get; init; } = "";
    
    [JsonPropertyName("pluginId")]
    public string PluginId { get; init; } = "";
}

internal sealed record PluginUiDefinition
{
    [JsonPropertyName("pluginId")]
    public string PluginId { get; init; } = "";
    
    [JsonPropertyName("title")]
    public string Title { get; init; } = "";
    
    [JsonPropertyName("fields")]
    public UiField[] Fields { get; init; } = [];
}

internal sealed record UiField
{
    [JsonPropertyName("id")]
    public string Id { get; init; } = "";
    
    [JsonPropertyName("type")]
    public string Type { get; init; } = "";
    
    [JsonPropertyName("label")]
    public string? Label { get; init; }
    
    [JsonPropertyName("value")]
    public string? Value { get; init; }
    
    [JsonPropertyName("min")]
    public int? Min { get; init; }
    
    [JsonPropertyName("max")]
    public int? Max { get; init; }
    
    [JsonPropertyName("step")]
    public int? Step { get; init; }
    
    [JsonPropertyName("options")]
    public string[]? Options { get; init; }
    
    [JsonPropertyName("description")]
    public string? Description { get; init; }
}

internal sealed record ShowToastMessage
{
    [JsonPropertyName("text")]
    public string Text { get; init; } = "";
    
    [JsonPropertyName("iconType")]
    public int IconType { get; init; }
}

internal sealed record DuplicateLayersRequest
{
    [JsonPropertyName("layerIds")]
    public string[] LayerIds { get; init; } = [];
    
    [JsonPropertyName("offsetX")]
    public double OffsetX { get; init; }
    
    [JsonPropertyName("offsetY")]
    public double OffsetY { get; init; }
    
    [JsonPropertyName("componentsToInstances")]
    public bool ComponentsToInstances { get; init; }
}

internal sealed record DuplicateLayersResponse
{
    [JsonPropertyName("duplicatedLayerIds")]
    public string[] DuplicatedLayerIds { get; init; } = [];
    
    [JsonPropertyName("message")]
    public string? Message { get; init; }
}

internal sealed record PluginEvent
{
    [JsonPropertyName("type")]
    public string Type { get; init; } = "";
    
    [JsonPropertyName("fieldId")]
    public string? FieldId { get; init; }
    
    [JsonPropertyName("eventType")]
    public string? EventType { get; init; }
}

internal sealed record LayerData
{
    [JsonPropertyName("id")]
    public string Id { get; init; } = "";
    
    [JsonPropertyName("size")]
    public double[]? Size { get; init; }
}

[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
[JsonSerializable(typeof(PluginRegisterMessage))]
[JsonSerializable(typeof(PluginUiDefinition))]
[JsonSerializable(typeof(UiField))]
[JsonSerializable(typeof(UiField[]))]
[JsonSerializable(typeof(ShowToastMessage))]
[JsonSerializable(typeof(DuplicateLayersRequest))]
[JsonSerializable(typeof(DuplicateLayersResponse))]
[JsonSerializable(typeof(PluginEvent))]
[JsonSerializable(typeof(LayerData))]
[JsonSerializable(typeof(LayerData[]))]
[JsonSerializable(typeof(Dictionary<string, string>))]
[JsonSerializable(typeof(string))]
internal sealed partial class SmartDuplicateJsonContext : JsonSerializerContext
{
}
```

**Key C# Features:**
- **JsonSourceGenerationOptions** - AOT-compatible JSON serialization (zero reflection)
- **Nullable reference types** - Proper `?` handling throughout
- **Collection expressions** - `[]` syntax for arrays
- **Static classes** - `UiManager`, `MessageHandler`, `PositionCalculator`, `DuplicationEngine`
- **Pattern matching** - `switch` expressions for presets
- **ClientWebSocket** - Native WebSocket client (no external dependencies)

### 5. Test the Plugin

**Development Mode (dotnet run):**
```bash
# Test directly (slower startup, no build needed)
dotnet run

# In Lunacy:
# 1. Restart Lunacy
# 2. Select a layer
# 3. Plugins menu → Smart Duplicate (C#)
# 4. Try different presets
```

### 6. Production Build (Recommended for Speed)

For faster startup and better performance, compile the plugin to a native binary:

```bash
# Build release version
dotnet build -c Release

# Test the compiled binary directly
./bin/Release/net9.0/SmartDuplicateCSharp
```

**Update `plugin.jsonc` to use compiled binary:**
```jsonc
{
  "id": "smart-duplicate-csharp",
  "name": "Smart Duplicate (C#)",
  "description": "Advanced layer duplication with preset patterns",
  "version": "1.0.0",
  "services": [
    {
      "id": "smart-duplicate-service",
      "name": "Smart Duplicate Service",
      "executable": "./bin/Release/net9.0/SmartDuplicateCSharp",
      "args": []
    }
  ]
}
```

**Performance Comparison:**
- `dotnet run` - ~2-3 seconds startup (includes build check)
- Compiled binary - ~100-200ms startup (instant)

**Note:** After changing `plugin.jsonc`, restart Lunacy to reload the plugin configuration.

---

## Understanding the Code

### 1. WebSocket Lifecycle

```
Start → Connect WS → Register Plugin → Wait for plugin_initialized → Register UI → Handle Events
```

### 2. Event Flow

```javascript
plugin_initialized  → Register your UI
show_ui            → User opened your dialog
ui_field_event     → User clicked button/changed field
close_ui           → User closed dialog
```

### 3. UI Field Types

```javascript
{
  type: 'number',     // Numeric input with min/max/step
  type: 'text',       // Text input
  type: 'select',     // Dropdown menu
  type: 'checkbox',   // Boolean checkbox
  type: 'button',     // Clickable button
  type: 'separator'   // Visual separator
}
```

### 4. Position Calculation Patterns

**Grid:** Regular rectangular grid
```javascript
offsetX = col * (layerWidth + spacingX)
offsetY = row * (layerHeight + spacingY)
```

**Circle:** Objects arranged on circle perimeter
```javascript
angle = (2π * i) / count
offsetX = radius * cos(angle)
offsetY = radius * sin(angle)
```

**Wave:** Sinusoidal vertical offset
```javascript
offsetX = i * horizontalSpacing
offsetY = amplitude * sin(2π * i / count)
```

**Spiral:** Expanding radius circle
```javascript
radius = radiusIncrement * i
offsetX = radius * cos(angle)
offsetY = radius * sin(angle)
```

## Common Patterns

### Handling Selection (Single vs Array)

```javascript
let selection = await selectionResponse.json();
if (!Array.isArray(selection)) {
  selection = selection ? [selection] : [];
}
```

### Error Handling with Toast Feedback

```javascript
try {
  await doSomething();
  await showToast('Success!', 2);  // CheckDone icon
} catch (error) {
  await showToast(`Error: ${error.message}`, 4);  // Warning icon
}
```

### Graceful Shutdown

```javascript
process.on('SIGTERM', async () => {
  await unregisterUi();
  if (ws) ws.close();
  process.exit(0);
});
```

## Troubleshooting

### WebSocket connection fails
- Ensure Lunacy is running
- Check port 31416 is not blocked
- Verify MCP server is enabled in settings

### UI doesn't appear
- Check `registerui` was successful (200 response)
- Verify `plugin_initialized` event was received
- Restart Lunacy completely

### Events not received
- Confirm `plugin_register` message was sent
- Check WebSocket is still connected
- Look for JSON parsing errors in console

### Values not updating
- Call `getpluginuivalues` after UI changes
- Parse returned values correctly (strings → numbers)
- Check field IDs match exactly

## Performance Tips

### For C# Plugins - Use Compiled Binaries

As shown in step 6 of the C# implementation, **always use compiled binaries for production**:

```bash
dotnet build -c Release
```

**Startup Time Comparison:**
- Node.js (interpreted) - ~200-300ms
- Python (interpreted) - ~300-500ms  
- C# with `dotnet run` - ~2-3 seconds (slow!)
- **C# compiled binary** - ~100-200ms (fastest!)

**Recommendation:** For the best user experience with C# plugins, ship compiled binaries instead of using `dotnet run`.

### For Service Plugins

Service plugins stay running, so startup time matters less after initial launch. However:
- **Node.js** - Excellent for rapid development, good runtime performance
- **Python** - Great for data processing, slightly slower than Node.js
- **C# compiled** - Best performance, especially for CPU-intensive operations

## Next Steps

Now that you understand UI plugins, you can:

- Modify the Smart Duplicate example for your needs
- Create your own UI plugins with different field types
- Explore other Lunacy API endpoints for more functionality

## Learn More

- [Plugin Development Guide](./PLUGIN_DEVELOPMENT_GUIDE.md) - Complete reference
- [API Reference](./API_REFERENCE.md) - All endpoints documented
- [UI Design Guide](./UI_DESIGN_GUIDE.md) - Best practices for plugin UI
- [Examples Directory](./examples/) - More working examples

---

**Congratulations!** You now know how to build advanced interactive plugins for Lunacy!
