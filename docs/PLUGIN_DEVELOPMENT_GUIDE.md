# Lunacy Plugin Development Guide

A comprehensive guide for developing Lunacy plugins using the HTTP Automation API.

## Quick Start

### Plugin Configuration

Create your plugin in its own directory within Lunacy's plugins folder:

**Plugin Directory Structure:**

- **Linux**: `~/.local/share/Icons8/Lunacy/Plugins/your-plugin-name/plugin.jsonc`
- **Windows**: `%APPDATA%\Icons8\Lunacy\Plugins\your-plugin-name\plugin.jsonc`
- **macOS**: `~/Library/Application Support/Icons8/Lunacy/Plugins/your-plugin-name/plugin.jsonc`

## Plugin Lifecycle Modes

Lunacy supports two distinct plugin lifecycle modes:

### **🔧 Utility Mode (Default)**

**Duration:** Runs only when user triggers commands  
**Use cases:** Quick tools, exports, format operations

```jsonc
{
  "id": "my-export-plugin",
  "name": "My Export Plugin", 
  "description": "Export selected artboards",
  "version": "1.0.0",
  "lifecycle": "utility",  // Optional - this is the default
  "commands": [
    {
      "id": "export-png",
      "name": "Export as PNG",
      "description": "Export selection as PNG files",
      "executable": "node",
      "args": ["my-plugin.js", "/home/user/exports", "PNG"],
      "timeoutMs": 60000,
      "env": {
        "NODE_ENV": "production",
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  ]
}
```

### **🖥️ Service Mode**

**Duration:** Runs continuously from Lunacy startup until shutdown  
**Use cases:** Background monitoring, real-time sync, WebSocket processing

```jsonc
{
  "id": "my-service-plugin",
  "name": "Background Sync Service", 
  "description": "Continuous monitoring and sync service",
  "version": "1.0.0",
  "lifecycle": "Service",
  "serviceCommand": {
    "id": "run-service",
    "name": "Run Background Service",
    "executable": "python3",
    "args": ["service.py"]
  },
  "commands": [
    {
      "id": "status",
      "name": "Show Sync Status",
      "executable": "python3",
      "args": ["status.py"],
      "timeoutMs": 5000
    },
    {
      "id": "pause",
      "name": "Pause Sync",
      "executable": "python3",
      "args": ["pause.py"],
      "timeoutMs": 3000
    }
  ]
}
  ]
}
```

### **Key Differences**

| Feature | **Utility Mode** | **Service Mode** |
|---------|------------------|------------------|
| **Startup** | On user command | With Lunacy startup |
| **Duration** | Seconds/minutes | Hours (until app closes) |
| **WebSocket Events** | ❌ Not available | ✅ Full access |
| **Memory Usage** | Minimal | Persistent |
| **Best for** | Quick tasks | Background monitoring |

## 🌐 API Ports and Endpoints

Lunacy provides two separate APIs for different purposes:

### **HTTP Automation API**

- **Port:** `31415` (default, auto-increments if busy)
- **URL:** `http://localhost:31415`
- **Purpose:** REST API for data operations (CRUD, export, screenshots)
- **Available to:** Both utility and service plugins

### **WebSocket Events API**

- **Port:** `31416` (default, auto-increments if busy)
- **URL:** `ws://localhost:31416`
- **Purpose:** Real-time event streaming (selection, undo, document events)
- **Available to:** Service plugins only

#### **Event Subscription**

Service plugins declare required events in `plugin.jsonc`:

```jsonc
{
  "lifecycle": "Service",
  "events": ["selection", "undo", "document", "window"],  // Subscribe to specific events
  "serviceCommand": { ... }
}
```

#### **Available Event Types**

##### 1️⃣ **SelectionEvent** (`"selection"`)

Fired when user changes layer selection in the document.

**When fired:**

- User selects/deselects layers
- Selection changes via API
- Switching between layers

**JSON Structure:**

```json
{
  "type": "selection",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "selected_layers": [
    {
      "id": "string",      // Layer ID in short GUID format
      "name": "string"     // Layer name
    }
  ]
}
```

**Fields:**

- `type` (string, required): Always `"selection"`
- `timestamp` (string, required): ISO 8601 UTC timestamp
- `selected_layers` (array, required): Array of selected layers (empty array if nothing selected)
  - `id` (string, required): Layer unique identifier (22-char base64)
  - `name` (string, required): Layer display name

##### 2️⃣ **UndoEvent** (`"undo"`)

Fired when undo/redo operation occurs, includes information about affected layers.

**When fired:**

- User creates/modifies/deletes layers
- Undo operation (Ctrl+Z)
- Redo operation (Ctrl+Shift+Z)
- Any operation that modifies document state

**JSON Structure:**

```json
{
  "type": "undo",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "operation_type": "created|undo|redo",
  "operation_description": "CreateLayers",
  "affected_layers": [
    {
      "id": "string",      // Layer ID
      "name": "string",    // Layer name
      "type": "string"     // Layer type (RECT, OVAL, TEXT, etc.)
    }
  ]
}
```

**Fields:**

- `type` (string, required): Always `"undo"`
- `timestamp` (string, required): ISO 8601 UTC timestamp
- `operation_type` (string, required): Type of operation
  - `"created"` - New operation performed
  - `"undo"` - Undo operation executed
  - `"redo"` - Redo operation executed
- `operation_description` (string, optional): Human-readable operation name
  - Examples: `"CreateLayers"`, `"DeleteLayers"`, `"ChangeFills"`, `"TransformLayers"`, `"Group"`, etc.
- `affected_layers` (array, optional): Layers affected by this operation
  - `id` (string, required): Layer unique identifier
  - `name` (string, required): Layer display name
  - `type` (string, required): Layer type code
    - Common types: `"RECT"`, `"OVAL"`, `"TEXT"`, `"PATH"`, `"GROUP"`, `"FRAME"`,
      `"COMPONENT"`, `"INSTANCE"`, `"SHAPE"`, `"SECTION"`

##### 3️⃣ **DocumentEvent** (`"document"`)

Fired when document lifecycle changes (open, close, activate, deactivate).

**When fired:**

- Document tab becomes active
- Document tab becomes inactive (switching tabs)
- Document opens (future)
- Document closes (future)

**JSON Structure:**

```json
{
  "type": "document",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "document_type": "activated|deactivated",
  "document_id": "string",
  "document_name": "string",
  "document_path": "string"
}
```

**Fields:**

- `type` (string, required): Always `"document"`
- `timestamp` (string, required): ISO 8601 UTC timestamp
- `document_type` (string, required): Type of document event
  - `"activated"` - Document tab became active
  - `"deactivated"` - Document tab became inactive
- `document_id` (string, optional): Document unique identifier in short GUID format
- `document_name` (string, optional): Document display name (e.g., "My Design.free")
- `document_path` (string, optional): Full file path for local documents or URL for cloud documents

##### 4️⃣ **WindowEvent** (`"window"`)

Fired when Lunacy window state changes (focus, minimize, fullscreen, closing).

**When fired:**

- Window gains or loses focus
- Window minimized/restored/fullscreen
- Window is about to close

**JSON Structure:**

```json
{
  "type": "window",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "event_type": "focused|unfocused|state_changed|closing",
  "window_state": "normal|minimized|fullscreen"
}
```

**Fields:**

- `type` (string, required): Always `"window"`
- `timestamp` (string, required): ISO 8601 UTC timestamp
- `event_type` (string, required): Type of window event
  - `"focused"` - Window gained focus
  - `"unfocused"` - Window lost focus
  - `"state_changed"` - Window state changed (minimized/fullscreen/normal)
  - `"closing"` - Window is about to close
- `window_state` (string, optional): Window state for `state_changed` events only
  - `"normal"` - Normal window state
  - `"minimized"` - Window minimized
  - `"fullscreen"` - Window in fullscreen mode

---

#### **Event Examples**

**SelectionEvent Example:**

```json
{
  "type": "selection",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "selected_layers": [
    {"id": "abc12345...", "name": "Rectangle 1"}
  ]
}
```

**UndoEvent Example:**

```json
{
  "type": "undo",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "operation_type": "created",
  "operation_description": "CreateLayers",
  "affected_layers": [
    {"id": "abc12345...", "name": "Rectangle 1", "type": "RECT"}
  ]
}
```

**DocumentEvent Example:**

```json
{
  "type": "document",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "document_type": "activated",
  "document_id": "xyz98765...",
  "document_name": "My Design.free",
  "document_path": "/home/user/Documents/My Design.free"
}
```

**WindowEvent Examples:**

```json
{
  "type": "window",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "event_type": "focused"
}
```

```json
{
  "type": "window",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "event_type": "state_changed",
  "window_state": "minimized"
}
```

```json
{
  "type": "window",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "event_type": "closing"
}
```

### **Port Assignment Logic**

Both servers automatically search for available ports starting from their defaults:

- HTTP API: tries 31415, 31416, 31417... (up to 31515)
- WebSocket API: tries 31416, 31417, 31418... (up to 31516)

**Important:** WebSocket port is separate from HTTP API port!

- ❌ Wrong: `ws://localhost:31415` (this is HTTP API port, not WebSocket)
- ✅ Correct: `ws://localhost:31416` (WebSocket events port)

**Port Discovery:**

If default ports are busy, you may need to discover the actual port:

```javascript
// Try connecting to WebSocket with fallback ports
async function connectToWebSocket() {
  const startPort = 31416;
  const maxAttempts = 10;
  
  for (let i = 0; i < maxAttempts; i++) {
    const port = startPort + i;
    try {
      const ws = new WebSocket(`ws://localhost:${port}`);
      
      await new Promise((resolve, reject) => {
        ws.on('open', () => {
          console.log(`Connected to WebSocket on port ${port}`);
          resolve();
        });
        ws.on('error', reject);
        setTimeout(reject, 1000); // Timeout after 1 second
      });
      
      return ws; // Successfully connected
    } catch (error) {
      // Try next port
      continue;
    }
  }
  
  throw new Error('Could not connect to WebSocket server');
}
```

**Example Plugins:**

- See the [examples directory](../examples/) for working plugin implementations

## 🌐 Lunacy HTTP Automation API

**Base URL**: `http://localhost:31415`

### Read Operations

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/getselected` | GET | Get selected layers | JSON (single layer or array) |
| `/getcomponents` | GET | Get components | JSON array |
| `/getimage` | GET | Get image by ID | Binary image data |
| `/getviewportinfo` | GET | Get viewport info | String with coordinates |
| `/getundostack` | GET | Get undo history | JSON array |

### Screenshots  

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/getscreenshotbyid` | POST | Screenshot of layers | JSON array of layer IDs | Binary image data + headers |
| `/getscreenshotviewport` | POST | Screenshot of viewport | None | Binary image data + headers |
| `/getscreenshotarea` | POST | Screenshot of area | ScreenshotAreaRequest | Binary image data + headers |

### Layer Queries

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/getlayersinarea` | POST | Layers in area | GetLayersInAreaRequest | JSON array (FREE format) |
| `/getlayersbyids` | POST | Layer data by IDs | string[] (array of IDs) | JSON array (FREE format) |

### Modification Operations

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/setselected` | POST | Change selection | FREE layers array (JSON) | Success/error message |
| `/updatelayers` | POST | Update existing layers | FREE layers array (JSON) | Success/error message |
| `/createlayers` | POST | Create new layers | LayersJsonRequest | Success/error message |
| `/deletelayers` | POST | Delete layers | String array (layer IDs) | Success/error message |
| `/duplicatelayers` | POST | Duplicate layers with offset | DuplicateLayersRequest | DuplicateLayersResponse |
| `/export` | POST | Export to files | ExportRequest | ExportResult[] |
| `/undo` | POST | Undo last operation | None | Success/error message |
| `/redo` | POST | Redo last undone operation | None | Success/error message |
| `/showtoast` | POST | Show toast notification | ShowToastRequest | Success/error message |

### Key API Details

#### Layer Modification Requests

**For `/setselected` and `/updatelayers`** - Direct JSON format:

- **Content-Type**: `application/json`
- **Body**: Array of FREE format layers directly
- **Format**: `[{layer1}, {layer2}, ...]` or `{single_layer}`
- **Example**: `[{"_t": "RECT", "id": "abc123", "fills": [{"color": "FFFF0000"}]}]`

**For `/createlayers`** - CreateLayersRequest format:

- **Content-Type**: `application/json`  
- **Body**: JSON object with `layersJson` field (as STRING) and optional `parentId`
- **Format**: `{"parentId": "parent-id", "layersJson": "serialized FREE format layers"}`
- **Example**: `{"parentId": "frame-id", "layersJson": "[{\"_t\": \"RECT\", \"name\": \"New Shape\"}]"}`
- **IMPORTANT:** `layersJson` is a JSON STRING, not an object!

#### Selection Response Format

- **Single layer selected**: Returns layer directly `{_t: "FRAME", id: "...", ...}`
- **Multiple layers**: Returns array `[{_t: "FRAME", ...}, {...}]`
- **Nothing selected**: Returns `{}` (empty object)

#### Export Response Format

Export returns JSON with byte array file data:

```jsonc
[
  {
    "layerId": "abc123",
    "fileName": "artboard.png", 
    "contentType": "image/png",
    "data": [137, 80, 78, 71, 13, 10, 26, 10, ...]  // byte array
  }
]
```

#### Screenshot Response Headers

Screenshot endpoints return binary image data with metadata in headers:

- `X-Screenshot-AbsoluteX` - X coordinate of screenshot
- `X-Screenshot-AbsoluteY` - Y coordinate of screenshot  
- `X-Screenshot-Width` - Width of screenshot
- `X-Screenshot-Height` - Height of screenshot
- `X-Screenshot-Timestamp` - When screenshot was taken
- `X-Screenshot-Error` - Error message if screenshot failed

## 📋 API Request/Response Objects

The Lunacy HTTP Automation API uses structured JSON objects for requests and responses.
All field names use **camelCase** format.

### Request Objects

#### ExportRequest (POST `/export`)

```json
{
  "layerIds": ["layer-id-1", "layer-id-2"],
  "format": "PNG",
  "scale": 1.0,
  "mergeObjects": false
}
```

**Fields:**

- `layerIds` - Array of layer IDs to export (required)
- `format` - Export format: "PNG", "SVG", "PDF", "JPG", "WEBP", "TIFF", "ICO" (default: "PNG")
- `scale` - Scale factor for export (default: 1.0)
- `mergeObjects` - Combine all layers into single file (default: false)

#### Command Configuration Fields

**Timeout Behavior:**

- `timeoutMs` - Command timeout in milliseconds (optional)
- **If specified**: Plugin will be terminated after this time
- **If not specified**: Plugin runs indefinitely until completion
- **Example values**: 30000 (30s), 120000 (2min), 600000 (10min)

**Environment Variables:**

- `env` - Custom environment variables for plugin process (optional)
- **Format**: Object with string key-value pairs
- **Usage**: Set PATH, runtime-specific variables, or custom configuration
- **Example**:

  ```json
  {
    "env": {
      "PATH": "/home/user/.dotnet:/usr/local/bin:/usr/bin:/bin",
      "DOTNET_ROOT": "/home/user/.dotnet"
    }
  }
  ```

- **Available for**: Both `commands` and `serviceCommand`
- **Behavior**: Variables are merged with system environment (custom values override system defaults)

#### Direct JSON Arrays (POST `/setselected`, `/updatelayers`)

```json
[
  {
    "_t": "RECT",
    "id": "layer-id-1", 
    "name": "My Shape",
    "fills": [{"color": "FFFF0000"}]
  }
]
```

**Format**: Array of FREE format layers (or single layer for one item)
**Usage:**

- **`/setselected`**: Replaces current selection with provided layers
- **`/updatelayers`**: Updates existing layers by their IDs with new properties

#### CreateLayersRequest (POST `/createlayers` only)

```json
{
  "parentId": "parent-layer-id",
  "layersJson": "[{\"_t\":\"RECT\",\"name\":\"My Shape\"}]"
}
```

**Fields:**

- `parentId` - ID of parent layer/frame (optional, null = root)
- `layersJson` - JSON string with layers in FREE format (required)

**Usage**: Creates new layers under the specified parent

#### DuplicateLayersRequest (POST `/duplicatelayers`)

```json
{
  "layerIds": ["layer-id-1", "layer-id-2"],
  "offsetX": 20,
  "offsetY": 20,
  "componentsToInstances": true
}
```

**Fields:**

- `layerIds` - Array of layer IDs to duplicate (required)
- `offsetX` - Horizontal offset in pixels (optional, default: 10)
- `offsetY` - Vertical offset in pixels (optional, default: 10)
- `componentsToInstances` - Convert components to instances (optional, default: true)

**Usage**: Duplicates existing layers with offset positioning

#### ShowToastRequest (POST `/showtoast`)

```json
{
  "text": "Plugin completed successfully!",
  "iconType": 2,
  "priority": 5,
  "durationSeconds": 7,
  "isContinuable": true,
  "isSkippable": false,
  "isAttention": false
}
```

**Fields:**

- `text` - The text message to display in the toast (required)
- `iconType` - Icon type: 0=None, 1=Copy, 2=CheckDone, 3=Document, 4=Warning, 5=Update, 6=Love,
  7=Human, 8=Trash, 9=Smile, 10=CloudDisconnect, 11=Message, 12=Copyright, 13=Stars (default: 0)
- `priority` - Priority level (higher numbers show first, default: 5)
- `durationSeconds` - Duration in seconds to show the toast (default: 7)
- `isContinuable` - Whether the toast can be paused when user hovers over it (default: true)
- `isSkippable` - Whether this toast can be skipped by newer toasts (default: false)
- `isAttention` - Whether this is an attention-grabbing toast (default: false)

#### GetLayersInAreaRequest (POST `/getlayersinarea`)

```json
{
  "x": 100,
  "y": 200,
  "width": 300,
  "height": 400,
  "maxDepth": 2
}
```

**Fields:**

- `x` - X coordinate of area top-left corner
- `y` - Y coordinate of area top-left corner
- `width` - Width of search area
- `height` - Height of search area
- `maxDepth` - Maximum hierarchy depth to traverse (default: 1)

#### ScreenshotAreaRequest (POST `/getscreenshotarea`)

```json
{
  "x": 100,
  "y": 200,
  "width": 300,
  "height": 400
}
```

**Fields:**

- `x` - X coordinate of screenshot area top-left corner
- `y` - Y coordinate of screenshot area top-left corner
- `width` - Width of screenshot area
- `height` - Height of screenshot area

### Response Objects

#### ExportResult[] (from `/export`)

```json
[
  {
    "layerId": "layer-id-1",
    "fileName": "artboard.png",
    "contentType": "image/png",
    "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
  }
]
```

**Fields:**

- `layerId` - ID of exported layer
- `fileName` - Generated filename for export
- `contentType` - MIME type of exported file
- `data` - Byte array with file content (automatically converted to Buffer in Node.js)

#### DuplicateLayersResponse (from `/duplicatelayers`)

```json
{
  "DuplicatedLayerIds": ["new-id-1", "new-id-2"],
  "Message": "Duplicated 2 layers successfully"
}
```

**Fields:**

- `DuplicatedLayerIds` - Array of IDs for newly created duplicate layers
- `Message` - Status message describing the operation result

**Usage**: Returns IDs of duplicated layers for subsequent operations

#### String Array (for various endpoints)

```json
["id1", "id2", "id3"]
```

Used for:

- `/getlayersbyids` - Request body with array of IDs
- `/deletelayers` - Request body with array of layer IDs to delete
- Various responses containing ID lists

## 💻 Plugin Development Examples

### C# Plugin Template (Utility Mode)

```csharp
using System.Net.Http.Json;
using System.Text.Json.Serialization;

const string API = "http://localhost:31415";

try
{
    using var client = new HttpClient();
    
    // Get current selection
    var selection = await client.GetFromJsonAsync<List<Layer>>($"{API}/getselected");
    
    if (selection == null || selection.Count == 0)
    {
        await ShowToast("Please select some layers first!", 4);
        return;
    }
    
    // Modify layers (example: change color to purple)
    foreach (var layer in selection)
    {
        if (layer.Fills != null)
        {
            foreach (var fill in layer.Fills)
            {
                fill.Color = "FF8B00FF";
            }
        }
    }
    
    // Update layers
    await client.PostAsJsonAsync($"{API}/setselected", selection);
    
    await ShowToast($"Changed {selection.Count} layer(s) to purple!", 2);
}
catch (Exception error)
{
    Console.WriteLine($"Error: {error.Message}");
    await ShowToast($"Error: {error.Message}", 4);
}

async Task ShowToast(string text, int iconType)
{
    using var client = new HttpClient();
    await client.PostAsJsonAsync($"{API}/showtoast", new
    {
        text,
        iconType,
        priority = 5,
        durationSeconds = 5
    });
}

class Layer
{
    [JsonPropertyName("_t")]
    public string? Type { get; set; }
    
    [JsonPropertyName("id")]
    public string? Id { get; set; }
    
    [JsonPropertyName("name")]
    public string? Name { get; set; }
    
    [JsonPropertyName("fills")]
    public List<Fill>? Fills { get; set; }
}

class Fill
{
    [JsonPropertyName("color")]
    public string? Color { get; set; }
}
```

**For Development (plugin.jsonc):**

```jsonc
{
  "id": "my-csharp-plugin",
  "name": "My C# Plugin",
  "version": "1.0.0",
  "commands": [
    {
      "id": "modify-colors",
      "name": "Modify Colors",
      "executable": "dotnet",
      "args": ["run", "--project", "MyPlugin.csproj"],
      "timeoutMs": 10000
    }
  ]
}
```

**For Production (plugin.jsonc):**

```jsonc
{
  "id": "my-csharp-plugin",
  "name": "My C# Plugin",
  "version": "1.0.0",
  "commands": [
    {
      "id": "modify-colors",
      "name": "Modify Colors",
      "executable": "./bin/Release/net9.0/MyPlugin",
      "timeoutMs": 5000
    }
  ]
}
```

### Service Plugin Template (Python)

```python
#!/usr/bin/env python3
import requests
import sys
import os
import json
import sys
import os

LUNACY_API = "http://localhost:31415"

def modify_selection_example(selection):
    """Example of how to modify layers and send back to Lunacy"""
    try:
        # Modify layers (change color to purple)
        modified_layers = []
        for layer in selection:
            modified_layer = layer.copy()
            if 'fills' in modified_layer:
                # Change existing fills to purple
                modified_layer['fills'] = [
                    {**fill, 'color': '8B00FF'} for fill in modified_layer['fills']
                ]
            else:
                # Add purple fill if no fills exist
                modified_layer['fills'] = [{'color': '8B00FF'}]
            modified_layers.append(modified_layer)
        
        # Send back to Lunacy as direct JSON array
        selection_data = modified_layers  # Always send as array
        
        response = requests.post(
            f"{LUNACY_API}/setselected",
            json=selection_data,  # Direct JSON array
            timeout=10
        )
        response.raise_for_status()
        print(f"Modified {len(modified_layers)} layers successfully!")
        
    except Exception as e:
        print(f"Failed to modify selection: {e}")

def update_layers_example(layer_ids):
    """Example of how to update existing layers by their IDs"""
    try:
        # Create updated layers with new properties
        updated_layers = []
        for layer_id in layer_ids:
            updated_layer = {
                "_t": "RECT",
                "id": layer_id,
                "name": "Updated Rectangle",
                "fills": [{"color": "FF00FF00"}]  # Green color
            }
            updated_layers.append(updated_layer)
        
        # Send to Lunacy using updatelayers endpoint
        response = requests.post(
            f"{LUNACY_API}/updatelayers",
            json=updated_layers,  # Direct JSON array
            timeout=10
        )
        response.raise_for_status()
        print(f"Updated {len(updated_layers)} layers successfully!")
        
    except Exception as e:
        print(f"Failed to update layers: {e}")

def delete_layers_example(layer_ids):
    """Example of how to delete layers by their IDs"""
    try:
        # Send layer IDs to delete endpoint
        response = requests.post(
            f"{LUNACY_API}/deletelayers",
            json=layer_ids,  # Direct array of strings
            timeout=10
        )
        response.raise_for_status()
        print(f"Deleted {len(layer_ids)} layers successfully!")
        
    except Exception as e:
        print(f"Failed to delete layers: {e}")

def main():
    try:
        # Get command line arguments  
        output_dir = sys.argv[1] if len(sys.argv) > 1 else "./exports"
        format = sys.argv[2].upper() if len(sys.argv) > 2 else "PNG"
        
        # Get selection
        print("Getting selection from Lunacy...")
        response = requests.get(f"{LUNACY_API}/getselected")
        selection = response.json()
        
        # Handle single object vs array
        if isinstance(selection, dict) and selection:
            selection = [selection]
        elif not selection:
            print("No layers selected. Please select layers in Lunacy.")
            sys.exit(1)
            
        print(f"Found {len(selection)} selected layer(s)")
        
        # Export layers
        export_data = {
            "layerIds": [layer["id"] for layer in selection],
            "format": format,
            "scale": 1.0,
            "mergeObjects": False
        }
        
        export_result = requests.post(f"{LUNACY_API}/export", json=export_data)
        export_result.raise_for_status()
        
        # Example: Modify selection (change colors to purple)
        modify_selection_example(selection)
        
        # Example: Use undo/redo operations
        print("Testing undo operation...")
        undo_response = requests.post(f"{LUNACY_API}/undo")
        print(f"Undo result: {undo_response.text}")
        
        print("Testing redo operation...")  
        redo_response = requests.post(f"{LUNACY_API}/redo")
        print(f"Redo result: {redo_response.text}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save files
        for result in export_result.json():
            if result.get("data"):
                file_path = os.path.join(output_dir, result["fileName"])
                file_data = bytes(result["data"])
                with open(file_path, "wb") as f:
                    f.write(file_data)
                print(f"Exported: {result['fileName']}")
                
        print("Export completed!")
        
    except Exception as e:
        print(f"Plugin failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### C# Export Plugin Template

```csharp
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;

const string API = "http://localhost:31415";

try
{
    var outputDir = args.Length > 0 ? args[0] : "./exports";
    var format = args.Length > 1 ? args[1].ToUpper() : "PNG";
    
    using var client = new HttpClient();
    
    // Get selection
    Console.WriteLine("Getting selection from Lunacy...");
    var response = await client.GetAsync($"{API}/getselected");
    var selectionJson = await response.Content.ReadAsStringAsync();
    
    // Parse as array or single object
    var selections = new List<Dictionary<string, JsonElement>>();
    using var doc = JsonDocument.Parse(selectionJson);
    
    if (doc.RootElement.ValueKind == JsonValueKind.Array)
    {
        selections = JsonSerializer.Deserialize<List<Dictionary<string, JsonElement>>>(selectionJson) ?? [];
    }
    else if (doc.RootElement.TryGetProperty("_t", out _))
    {
        var single = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(selectionJson);
        if (single != null) selections.Add(single);
    }
    
    if (selections.Count == 0)
    {
        Console.WriteLine("No layers selected");
        return;
    }
    
    Console.WriteLine($"Found {selections.Count} selected layer(s)");
    
    // Export layers
    var exportRequest = new ExportRequest
    {
        LayerIds = selections
            .Where(s => s.ContainsKey("id"))
            .Select(s => s["id"].GetString() ?? "")
            .Where(id => !string.IsNullOrEmpty(id))
            .ToList(),
        Format = format,
        Scale = 1.0,
        MergeObjects = false
    };
    
    var exportResult = await client.PostAsJsonAsync($"{API}/export", exportRequest);
    var results = await exportResult.Content.ReadFromJsonAsync<List<ExportResult>>();
    
    if (results == null || results.Count == 0)
    {
        Console.WriteLine("Export failed");
        return;
    }
    
    // Create output directory
    Directory.CreateDirectory(outputDir);
    
    // Save files
    foreach (var result in results)
    {
        if (result.Data != null && result.Data.Length > 0)
        {
            var filePath = Path.Combine(outputDir, result.FileName);
            await File.WriteAllBytesAsync(filePath, result.Data);
            Console.WriteLine($"Exported: {result.FileName}");
        }
    }
    
    Console.WriteLine("Export completed!");
    
    // Show success toast
    await client.PostAsJsonAsync($"{API}/showtoast", new
    {
        text = $"Exported {results.Count} file(s) to {format}!",
        iconType = 2,
        priority = 5,
        durationSeconds = 5
    });
}
catch (Exception error)
{
    Console.WriteLine($"Plugin failed: {error.Message}");
    Environment.Exit(1);
}

record ExportRequest
{
    [JsonPropertyName("layerIds")]
    public List<string> LayerIds { get; init; } = [];
    
    [JsonPropertyName("format")]
    public string Format { get; init; } = "PNG";
    
    [JsonPropertyName("scale")]
    public double Scale { get; init; } = 1.0;
    
    [JsonPropertyName("mergeObjects")]
    public bool MergeObjects { get; init; }
}

record ExportResult
{
    [JsonPropertyName("layerId")]
    public string LayerId { get; init; } = "";
    
    [JsonPropertyName("fileName")]
    public string FileName { get; init; } = "";
    
    [JsonPropertyName("contentType")]
    public string ContentType { get; init; } = "";
    
    [JsonPropertyName("data")]
    public string Data { get; init; } = "";
}
```

### Screenshot API Example

```javascript
// Modify selection using direct JSON array format
async function changeLayerColor() {
    // 1. Get current selection
    const getResponse = await axios.get(`${LUNACY_API}/getselected`);
    let selection = getResponse.data;
    
    // 2. Handle single layer vs array
    if (!Array.isArray(selection) && selection._t) {
        selection = [selection];
    }
    
    // 3. Modify layers (change color to red)
    const modifiedLayers = selection.map(layer => ({
        ...layer,
        fills: layer.fills ? layer.fills.map(fill => ({
            ...fill,
            color: "FF0000"  // Red color in HEX format
        })) : [{ color: "FF0000" }]
    }));
    
    // 4. Send back to Lunacy as direct JSON array
    const response = await axios.post(`${LUNACY_API}/setselected`, modifiedLayers);
    console.log('Selection updated:', response.data);
}

// Update existing layers by their IDs
async function updateLayersByIds(layerIds) {
    // Create updated layers
    const updatedLayers = layerIds.map(id => ({
        _t: "RECT",
        id: id,
        name: "Updated Rectangle", 
        fills: [{ color: "00FF00" }]  // Green color
    }));
    
    // Send to updatelayers endpoint
    const response = await axios.post(`${LUNACY_API}/updatelayers`, updatedLayers);
    console.log('Layers updated:', response.data);
}

// Get layers in area
async function getLayersInArea() {
    const areaRequest = {
        x: 100,
        y: 200, 
        width: 300,
        height: 400,
        maxDepth: 2
    };
    
    const response = await axios.post(`${LUNACY_API}/getlayersinarea`, areaRequest);
    console.log(`Found ${response.data.length} layers in area`);
    
    return response.data; // Array of layers in FREE format
}

// Create new layers  
async function createRectangle() {
    const newLayersJson = JSON.stringify({
        _t: "RECT",
        name: "My Rectangle",
        size: [200, 150],
        transform: [1, 0, 100, 0, 1, 100]  // Translation matrix: x=100, y=100
    });
    
    const createRequest = {
        parentId: null, // Create at root level
        layersJson: newLayersJson
    };
    
    const response = await axios.post(`${LUNACY_API}/createlayers`, createRequest);
    console.log('Layer created:', response.data);
}

// Modify selection using direct JSON array format
async function changeLayerColor() {
    // 1. Get current selection
    const getResponse = await axios.get(`${LUNACY_API}/getselected`);
    let selection = getResponse.data;
    
    // 2. Handle single layer vs array
    if (!Array.isArray(selection) && selection._t) {
        selection = [selection];
    }
    
    // 3. Modify layers (change color to red)
    const modifiedLayers = selection.map(layer => ({
        ...layer,
        fills: layer.fills ? layer.fills.map(fill => ({
            ...fill,
            color: "FF0000"  // Red color in HEX format
        })) : [{ color: "FF0000" }]
    }));
    
    // 4. Send back to Lunacy as direct JSON array
    const response = await axios.post(`${LUNACY_API}/setselected`, modifiedLayers);
    console.log('Selection updated:', response.data);
}

// Update existing layers by their IDs
async function updateLayersByIds(layerIds) {
    // Create updated layers
    const updatedLayers = layerIds.map(id => ({
        _t: "RECT",
        id: id,
        name: "Updated Rectangle", 
        fills: [{ color: "00FF00" }]  // Green color
    }));
    
    // Send to updatelayers endpoint
    const response = await axios.post(`${LUNACY_API}/updatelayers`, updatedLayers);
    console.log('Layers updated:', response.data);
}

// Delete layers by their IDs
async function deleteLayersByIds(layerIds) {
    try {
        const response = await axios.post(`${LUNACY_API}/deletelayers`, layerIds);
        console.log(`Deleted ${layerIds.length} layers:`, response.data);
    } catch (error) {
        console.error('Delete failed:', error.message);
    }
}

// Undo/Redo operations
async function undoLastOperation() {
    try {
        const response = await axios.post(`${LUNACY_API}/undo`);
        console.log('Undo result:', response.data);
    } catch (error) {
        console.error('Undo failed:', error.message);
    }
}

async function redoLastOperation() {
    try {
        const response = await axios.post(`${LUNACY_API}/redo`);
        console.log('Redo result:', response.data);
    } catch (error) {
        console.error('Redo failed:', error.message);
    }
}
```

```

## 🔧 Development Workflow

### 1. **Setup Development Environment**

#### For Utility Plugins (Quick Tools)
```bash
# Create plugin directory in Lunacy's plugins folder
mkdir -p ~/.local/share/Icons8/Lunacy/Plugins/my-utility-plugin
cd ~/.local/share/Icons8/Lunacy/Plugins/my-utility-plugin

# Create utility plugin configuration
cat > plugin.jsonc << 'EOF'
{
  "id": "my-utility-plugin",
  "name": "My Utility Plugin",
  "description": "Quick tool for Lunacy",
  "version": "1.0.0",
  "lifecycle": "utility",
  "commands": [
    {
      "id": "my-command",
      "name": "My Command",
      "executable": "node",
      "args": ["plugin.js"],
      "timeoutMs": 30000,
      "env": {
        "NODE_ENV": "production"
      }
    }
  ]
}
EOF

# For Node.js plugins
npm init -y
npm install axios

# For Python plugins  
pip install requests
```

#### For Service Plugins (Background Services)

```bash
# Create service plugin directory
mkdir -p ~/.local/share/Icons8/Lunacy/Plugins/my-service-plugin
cd ~/.local/share/Icons8/Lunacy/Plugins/my-service-plugin

# Create service plugin configuration
cat > plugin.jsonc << 'EOF'
{
  "id": "my-service-plugin",
  "name": "My Background Service",
  "description": "Continuous monitoring service",
  "version": "1.0.0",
  "lifecycle": "Service",
  "serviceCommand": {
    "id": "run-service",
    "name": "Run Background Service",
    "executable": "python3",
    "args": ["service.py"]
  }
}
EOF

# Create simple service script
cat > service.py << 'EOF'
#!/usr/bin/env python3
import time
import sys

print("Service starting...")
sys.stdout.flush()

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Service stopping...")
    sys.exit(0)
EOF

chmod +x service.py
```

**Service plugins start automatically** when Lunacy launches and run continuously in the background.

```

#### Example: Using Custom Environment Variables

For plugins that require custom runtime paths or environment configuration:

```jsonc
{
  "id": "dotnet-plugin",
  "name": "DotNet Plugin Example",
  "description": "Plugin using custom .NET SDK path",
  "version": "1.0.0",
  "lifecycle": "utility",
  "commands": [
    {
      "id": "run-dotnet-tool",
      "name": "Run .NET Tool",
      "executable": "dotnet",
      "args": ["run", "--project", "MyTool.csproj"],
      "timeoutMs": 60000,
      "env": {
        "PATH": "/home/user/.dotnet:/usr/local/bin:/usr/bin:/bin",
        "DOTNET_ROOT": "/home/user/.dotnet",
        "DOTNET_CLI_TELEMETRY_OPTOUT": "1"
      }
    }
  ]
}
```

**Common use cases for custom environment variables:**

- **Custom runtime paths**: Set `PATH` for specific Node.js, Python, or .NET versions
- **SDK locations**: `DOTNET_ROOT`, `JAVA_HOME`, `GOROOT`
- **Runtime behavior**: `NODE_ENV`, `PYTHONUNBUFFERED`, `DOTNET_CLI_TELEMETRY_OPTOUT`
- **Plugin-specific config**: Custom variables for your plugin's configuration

### 2. **Test API Connectivity**

```bash
# Test if Lunacy HTTP API is running
curl http://localhost:31415/getselected

# Test selection modification using direct JSON array
curl -X POST http://localhost:31415/setselected \
  -H "Content-Type: application/json" \
  -d '[{"_t":"RECT","id":"test123","fills":[{"color": "FFFF0000"}]}]'

# Test updating layers by IDs
curl -X POST http://localhost:31415/updatelayers \
  -H "Content-Type: application/json" \
  -d '[{"_t":"RECT","id":"existing-id","name":"Updated Shape"}]'

# Test deleting layers by IDs
curl -X POST http://localhost:31415/deletelayers \
  -H "Content-Type: application/json" \
  -d '["layer-id-1", "layer-id-2"]'

# Test duplicating layers with offset
curl -X POST http://localhost:31415/duplicatelayers \
  -H "Content-Type: application/json" \
  -d '{"layerIds":["layer-id-1"],"offsetX":20,"offsetY":20,"componentsToInstances":true}'

# Test export endpoint
curl -X POST http://localhost:31415/export \
  -H "Content-Type: application/json" \
  -d '{"layerIds":["test"],"format":"PNG","scale":1.0}'
```

### 3. **Develop Plugin Logic**

- Start with the template above
- Add your custom logic for processing objects
- Test directly: `node my-plugin.js` or `python my-plugin.py`

### 4. **Create Plugin Configuration**

- Create plugin directory with `plugin.jsonc` file
- Set correct `workingDirectory` path
- Define command arguments

### 5. **Test in Lunacy**

#### For Utility Plugins

- Select some objects/artboards in Lunacy
- Use plugin from menu: Plugins → [Your Plugin Name] → [Command Name]
- Check console output and exported files

#### For Service Plugins

- **Auto-start**: Service automatically starts when Lunacy opens
- **Manual commands**: Use menu commands while service runs in background
- **Logs**: Check service.log file for monitoring activity
- **Shutdown**: Service automatically stops when Lunacy closes

## 🔍 Debugging Tips

### Common Issues

**"Connection refused"**

- Ensure Lunacy is running
- Verify HTTP Automation API server is enabled (check Lunacy preferences)
- Test with: `curl http://localhost:31415/getselected`

**"No layers selected"**  

- Select layers in Lunacy before running plugin
- For exports, select artboards/frames (`_t: "FRAME"`)

**"Export files corrupted"**

- Export data is byte array, not string
- In Node.js: `Buffer.from(result.data)`
- In Python: `bytes(result["data"])`
- In C#: `result.Data` is already `byte[]`

**"Plugin not in menu"**

- Check JSON syntax in `plugin.jsonc`
- Verify `workingDirectory` path exists
- Restart Lunacy after configuration changes

**"Service plugin not starting"**

- Check plugin configuration for service lifecycle mode (`"lifecycle": "Service"`)
- Verify `serviceCommand` is defined with valid executable
- Check plugin logs for startup errors
- Service plugins start automatically with Lunacy

**"Service plugin stopping unexpectedly"**

- Check service.log for error messages
- Ensure service handles signals gracefully (SIGTERM, SIGINT)
- Verify long-running loop doesn't exit on API errors
- Check that service executable has proper permissions

**"Endpoint not found" (404) for layer operations**

- ❌ Wrong: `/setselection` endpoint name (should be `/setselected`)
- ❌ Wrong: Using LayersJsonRequest wrapper for `/setselected`/`/updatelayers`
- ✅ Correct: Direct JSON array for `/setselected` and `/updatelayers`
- ✅ Correct: LayersJsonRequest only for `/createlayers`

### Debug Commands

```bash
# Test selection API
curl http://localhost:31415/getselected | jq

# Test viewport info
curl http://localhost:31415/getviewportinfo

# Get screenshot of viewport  
curl -X POST http://localhost:31415/getscreenshotviewport --output viewport.png

# Get components
curl http://localhost:31415/getcomponents | jq

# Get undo stack
curl http://localhost:31415/getundostack | jq

# Test export endpoint (ExportRequest)
curl -X POST http://localhost:31415/export \
  -H "Content-Type: application/json" \
  -d '{"layerIds":["layer-id"],"format":"PNG","scale":1.0,"mergeObjects":false}' | jq

# Test undo/redo operations
curl -X POST http://localhost:31415/undo
curl -X POST http://localhost:31415/redo

# Test layers in area (GetLayersInAreaRequest)
curl -X POST http://localhost:31415/getlayersinarea \
  -H "Content-Type: application/json" \
  -d '{"x":0,"y":0,"width":500,"height":500,"maxDepth":2}' | jq

# Test get layers by IDs (string array)
curl -X POST http://localhost:31415/getlayersbyids \
  -H "Content-Type: application/json" \
  -d '["layer-id-1","layer-id-2"]' | jq

# Test delete layers by IDs (string array)
curl -X POST http://localhost:31415/deletelayers \
  -H "Content-Type: application/json" \
  -d '["layer-id-1","layer-id-2"]'

# Test duplicate layers with offset
curl -X POST http://localhost:31415/duplicatelayers \
  -H "Content-Type: application/json" \
  -d '{"layerIds":["layer-id-1","layer-id-2"],"offsetX":30,"offsetY":0,"componentsToInstances":false}' | jq

# Test screenshot area (ScreenshotAreaRequest)
curl -X POST http://localhost:31415/getscreenshotarea \
  -H "Content-Type: application/json" \
  -d '{"x":0,"y":0,"width":400,"height":300}' \
  --output area.png

# Run plugin directly
node my-plugin.js /tmp PNG

# Check plugin logs
# (Plugin output appears in Lunacy's console when run from menu)
```

## 📋 Best Practices

1. **Handle both single layers and arrays** from selection API
2. **Handle export data as byte arrays** (not base64 strings)
3. **Check for empty selections** before processing
4. **Create output directories** if they don't exist
5. **Provide clear error messages** and exit codes
6. **Use appropriate timeouts** in plugin configuration
7. **Test plugins both directly and through Lunacy menu**

---

**Ready to build?** Check out the [working examples](../examples/) for complete implementation details!
