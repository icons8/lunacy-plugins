# Lunacy Automation API Reference

Complete reference for Lunacy plugin developers covering HTTP endpoints, WebSocket events, and data structures.

## Table of Contents

- [HTTP API](#http-api)
  - [Base URL](#base-url)
  - [Selection](#selection)
  - [Layer Operations](#layer-operations)
  - [Screenshots](#screenshots)
  - [Export](#export)
  - [Undo/Redo](#undoredo)
  - [UI](#ui)
  - [Document](#document)
- [WebSocket API](#websocket-api)
  - [Connection](#connection)
  - [Events](#events)
- [Data Structures](#data-structures)
  - [Request DTOs](#request-dtos)
  - [Response DTOs](#response-dtos)
  - [Layer Format](#layer-format)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)

---

## HTTP API

### Base URL

```
http://localhost:31415
```

All HTTP endpoints are relative to this base URL.

### Selection

#### GET /getselected

Get currently selected layers.

**Request:**

```bash
curl http://localhost:31415/getselected
```

**Response:**

- Single layer object when 1 layer selected
- Array of layer objects when multiple layers selected
- Empty object `{}` when nothing selected

```json
{
  "id": "abc123...",
  "name": "Rectangle 1",
  "_t": "RECT",
  "transform": [1, 0, 100, 0, 1, 200],
  "size": [300, 150],
  "fills": [{"color": "FFFF0000"}]
}
```

**Notes:**

- Layer objects are in FREE format (Lunacy's internal format)
- Always handle both single object and array responses
- Check `_t` field to determine layer type

#### POST /setselected

Change current selection.

**Request:**

```bash
curl -X POST http://localhost:31415/setselected \
  -H "Content-Type: application/json" \
  -d '[{"id": "layer-id-1"}, {"id": "layer-id-2"}]'
```

**Body:**

- Single layer object to select one layer
- Array of layer objects to select multiple layers
- Empty array `[]` to clear selection

**Response:**

```json
{
  "success": true
}
```

#### POST /getlayersbyids

Get layer data by layer IDs.

**Request:**

```bash
curl -X POST http://localhost:31415/getlayersbyids \
  -H "Content-Type: application/json" \
  -d '["layer-id-1", "layer-id-2"]'
```

**Body:**
Array of layer IDs (strings).

**Response:**
Array of layer objects in FREE format.

```json
[
  {"id": "layer-id-1", "name": "Layer 1", "_t": "RECT", ...},
  {"id": "layer-id-2", "name": "Layer 2", "_t": "OVAL", ...}
]
```

#### POST /getlayersinarea

Get all layers within specified rectangular area.

**Request:**

```bash
curl -X POST http://localhost:31415/getlayersinarea \
  -H "Content-Type: application/json" \
  -d '{"x": 0, "y": 0, "width": 500, "height": 500, "maxDepth": 2}'
```

**Body:** [GetLayersInAreaRequest](#getlayersinarearequest)

**Response:**
Array of layer objects within the specified area.

---

### Layer Operations

**IMPORTANT - Request Format Differences:**

The layer modification endpoints use **different request formats**:

| Endpoint | Request Format | Example |
|----------|---------------|---------|
| `/createlayers` | **CreateLayersRequest wrapper** | `{"parentId": "...", "layersJson": "[...]"}` |
| `/updatelayers` | **Direct layer array** | `[{...}, {...}]` |
| `/setselected` | **Direct layer array or single layer** | `[{...}]` or `{...}` |

**Key difference:** Only `/createlayers` uses a wrapper object with `layersJson` as a **JSON string**.
The other endpoints accept layer objects directly.

#### POST /createlayers

Create new layers in the document.

**Request:**

```bash
curl -X POST http://localhost:31415/createlayers \
  -H "Content-Type: application/json" \
  -d '{"parentId": "artboard-id", "layersJson": "FREE_FORMAT_STRING"}'
```

**Body:** [CreateLayersRequest](#createlayersrequest)

**Response:**

```json
{
  "CreatedLayerIds": ["new-id-1", "new-id-2"],
  "Message": "Created 2 layers successfully"
}
```

**Notes:**

- **CRITICAL:** `layersJson` must be a **JSON STRING** (not a JSON object!)
- Example in JavaScript: `JSON.stringify([{_t: "RECT", name: "Shape"}])`
- Layers are added to specified parent or root if `parentId` is null
- Returns IDs of created layers for further operations

#### POST /updatelayers

Update existing layers.

**Request:**

```bash
curl -X POST http://localhost:31415/updatelayers \
  -H "Content-Type: application/json" \
  -d '[{"id": "layer-id", "name": "New Name", "transform": [1, 0, 150, 0, 1, 200]}]'
```

**Body:**
Array of layer objects with modified properties. Must include `id` field.

**Response:**

```json
{
  "success": true,
  "updatedCount": 1
}
```

**Notes:**

- Only modified fields need to be provided
- `id` field is required to identify layer
- Creates single undo operation for all updates

#### POST /deletelayers

Delete layers by IDs.

**Request:**

```bash
curl -X POST http://localhost:31415/deletelayers \
  -H "Content-Type: application/json" \
  -d '["layer-id-1", "layer-id-2"]'
```

**Body:**
Array of layer IDs (strings) to delete.

**Response:**

```json
{
  "success": true,
  "deletedCount": 2
}
```

**Notes:**

- Deletion is permanent (unless undone)
- Deleting parent layer also deletes all children
- Creates single undo operation

#### POST /duplicatelayers

Duplicate layers with offset.

**Request:**

```bash
curl -X POST http://localhost:31415/duplicatelayers \
  -H "Content-Type: application/json" \
  -d '{
    "layerIds": ["layer-id-1"],
    "offsetX": 20,
    "offsetY": 20,
    "componentsToInstances": true
  }'
```

**Body:** [DuplicateLayersRequest](#duplicatelayersrequest)

**Response:** [DuplicateLayersResponse](#duplicatelayersresponse)

```json
{
  "DuplicatedLayerIds": ["new-id-1"],
  "Message": "Duplicated 1 layer successfully"
}
```

---

### Screenshots

#### POST /getscreenshotbyid

Get screenshot of specific layers by IDs.

**Request:**

```bash
curl -X POST http://localhost:31415/getscreenshotbyid \
  -H "Content-Type: application/json" \
  -d '["layer-id-1", "layer-id-2"]'
```

**Body:** JSON array of layer ID strings

**Response:**
Binary image data with appropriate `Content-Type` header and metadata in custom headers:

- `X-Image-Format`: Image format (PNG, JPG, WEBP)
- `X-Image-Width`: Image width in pixels
- `X-Image-Height`: Image height in pixels

#### POST /getscreenshotviewport

Get screenshot of current viewport.

**Request:**

```bash
curl -X POST http://localhost:31415/getscreenshotviewport
```

**Body:** Empty (no parameters required)

**Response:**
Binary image data with metadata in custom headers:

- `X-Image-Format`: Image format (PNG)
- `X-Image-Width`: Image width in pixels
- `X-Image-Height`: Image height in pixels

#### POST /getscreenshotarea

Get screenshot of specific rectangular area.

**Request:**

```bash
curl -X POST http://localhost:31415/getscreenshotarea \
  -H "Content-Type: application/json" \
  -d '{"x": 0, "y": 0, "width": 800, "height": 600, "format": "PNG", "scale": 1}'
```

**Body:** [ScreenshotAreaRequest](#screenshotarearequest)

**Response:**
Binary image data.

---

### Export

#### POST /export

Export layers to files.

**Request:**

```bash
curl -X POST http://localhost:31415/export \
  -H "Content-Type: application/json" \
  -d '{
    "layerIds": ["layer-id-1", "layer-id-2"],
    "format": "PNG",
    "scale": 2.0,
    "mergeObjects": false
  }'
```

**Body:** [ExportRequest](#exportrequest)

**Response:** [ExportResult](#exportresult)[]

```json
[
  {
    "layerId": "layer-id-1",
    "fileName": "Layer 1.png",
    "contentType": "image/png",
    "data": [137, 80, 78, 71, ...]
  }
]
```

**Supported Formats:**

- `PNG` - Portable Network Graphics
- `SVG` - Scalable Vector Graphics
- `PDF` - Portable Document Format
- `JPG` - JPEG image
- `WEBP` - WebP image
- `TIFF` - Tagged Image File Format
- `ICO` - Windows Icon

**Notes:**

- `data` field contains byte array (not base64)
- In JavaScript/Node.js, data is automatically converted to Buffer
- `fileName` is auto-generated from layer name
- `mergeObjects: true` exports all layers as single image

---

### Undo/Redo

#### POST /undo

Undo last operation.

**Request:**

```bash
curl -X POST http://localhost:31415/undo
```

**Response:**

```json
{
  "success": true
}
```

#### POST /redo

Redo last undone operation.

**Request:**

```bash
curl -X POST http://localhost:31415/redo
```

**Response:**

```json
{
  "success": true
}
```

#### POST /getundostack

Get undo history.

**Request:**

```bash
curl -X POST http://localhost:31415/getundostack \
  -H "Content-Type: text/plain" \
  -d "10"
```

**Body:**
Plain text number representing how many recent operations to fetch.

**Response:**
Array of undo operation objects.

```json
[
  {
    "op": "CreateLayers",
    "start": "...",
    "final": "...",
    "view": {...},
    "componentEditor": null
  }
]
```

**Notes:**

- Operations are in reverse chronological order (newest first)
- Each operation contains serialized layer states
- Use for undo history visualization or layer diff tools

---

### UI

#### POST /showtoast

Show toast notification in Lunacy.

**Request:**

```bash
curl -X POST http://localhost:31415/showtoast \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Operation completed!",
    "iconType": 2,
    "priority": 5,
    "durationSeconds": 5
  }'
```

**Body:** [ShowToastRequest](#showtoastrequest)

**Response:**

```json
{
  "success": true
}
```

**Icon Types:**

- `0` - None
- `1` - Copy
- `2` - CheckDone
- `3` - Document
- `4` - Warning
- `5` - Update
- `6` - Love
- `7` - Human
- `8` - Trash
- `9` - Smile
- `10` - CloudDisconnect
- `11` - Message
- `12` - Copyright
- `13` - Stars

**Priority:** 1-255 (higher = more important, default: 5)

**Additional Parameters:**

- `IsContinuable` (bool): Toast can be paused on hover (default: true)
- `IsSkippable` (bool): Can be skipped by newer toasts (default: false)
- `IsAttention` (bool): Attention-grabbing toast (default: false)

---

### Document

#### POST /getcomponents

Get components (master components) by IDs.

**Request:**

```bash
curl -X POST http://localhost:31415/getcomponents \
  -H "Content-Type: application/json" \
  -d '["component-id-1", "component-id-2"]'
```

**Body:**
Array of component IDs (strings).

**Response:**
Array of component layer objects in FREE format.

#### POST /getimage

Get image resource by ID.

**Request:**

```bash
curl -X POST http://localhost:31415/getimage \
  -H "Content-Type: application/json" \
  -d '{"id": "image-id"}'
```

**Body:** [GetImageRequest](#getimagerequest)

**Response:**
Binary image data with appropriate `Content-Type` header.

#### POST /insertimage

Insert image into document at specified position.

**Request:**

```bash
curl -X POST http://localhost:31415/insertimage \
  -H "Content-Type: image/png" \
  -H "X-Image-Position-X: 100" \
  -H "X-Image-Position-Y: 200" \
  -H "X-Image-File-Name: my-image.png" \
  -H "X-Image-Parent-Id: parent-layer-id" \
  --data-binary @image.png
```

**Headers:**

- `X-Image-Position-X` (optional): X position (default: 0)
- `X-Image-Position-Y` (optional): Y position (default: 0)
- `X-Image-File-Name` (optional): Image file name
- `X-Image-Parent-Id` (optional): Parent layer ID

**Body:**
Binary image data (PNG, JPG, WEBP, etc.)

**Response:**

```json
{
  "success": true,
  "layerId": "new-image-layer-id"
}
```

**Notes:**

- Image is inserted as new image layer
- Supported formats: PNG, JPG, JPEG, WEBP, GIF, BMP, TIFF
- Max size: 200 MB

#### GET /getviewportinfo

Get current viewport information.

**Request:**

```bash
curl http://localhost:31415/getviewportinfo
```

**Response:**
Plain text string with viewport coordinates.

Example:

```
Viewport: x=0, y=0, width=1920, height=1080
```

---

## WebSocket API

### Connection

Connect to WebSocket server for real-time events.

**URL:**

```
ws://localhost:31416
```

**Note:** WebSocket server runs on port **31416** (HTTP API is on 31415). If port 31416 is busy,
server auto-increments (31417, 31418, etc.).

**Port Discovery:**

If the default port is unavailable, use this pattern to discover the correct port:

```javascript
async function connectToWebSocket(startPort = 31416, maxAttempts = 10) {
  for (let i = 0; i < maxAttempts; i++) {
    const port = startPort + i;
    try {
      const ws = new WebSocket(`ws://localhost:${port}`);
      
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('timeout')), 1000);
        
        ws.onopen = () => {
          clearTimeout(timeout);
          console.log(`Connected to WebSocket on port ${port}`);
          resolve();
        };
        
        ws.onerror = () => {
          clearTimeout(timeout);
          reject(new Error('connection failed'));
        };
      });
      
      return ws;
    } catch (error) {
      if (i === maxAttempts - 1) {
        throw new Error('Could not connect to WebSocket server');
      }
    }
  }
}

const ws = await connectToWebSocket();
```

**Connection Example (JavaScript):**

```javascript
const ws = new WebSocket('ws://localhost:31416');

ws.onopen = () => {
  console.log('Connected to Lunacy events');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from Lunacy events');
};
```

### Events

#### Selection Event

Fired when layer selection changes.

**Event Type:** `"selection"`

**JSON Structure:**

```json
{
  "type": "selection",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "layer_ids": ["layer-id-1", "layer-id-2"],
  "layer_count": 2
}
```

**Fields:**

- `type` (string): Always `"selection"`
- `timestamp` (string): ISO 8601 UTC timestamp
- `layer_ids` (string[]): Array of selected layer IDs
- `layer_count` (number): Number of selected layers

#### Undo Event

Fired when undo/redo operation occurs or undo stack changes.

**Event Type:** `"undo"`

**JSON Structure:**

```json
{
  "type": "undo",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "operation": "created",
  "operation_type": "CreateLayers",
  "affected_layers": [
    {
      "id": "layer-id",
      "name": "Rectangle",
      "layer_type": "RECT"
    }
  ]
}
```

**Fields:**

- `type` (string): Always `"undo"`
- `timestamp` (string): ISO 8601 UTC timestamp
- `operation` (string): Operation category
  - `"created"` - Layers created
  - `"deleted"` - Layers deleted
  - `"modified"` - Properties changed
  - `"transformed"` - Position/size changed
  - `"styled"` - Styles changed
  - `"unknown"` - Other operations
- `operation_type` (string): Detailed operation name (e.g., `CreateLayers`, `DeleteLayers`)
- `affected_layers` (array): Layers involved in operation

#### Document Event

Fired when document state changes (opened, closed, activated, deactivated).

**Event Type:** `"document"`

**JSON Structure:**

```json
{
  "type": "document",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "document_type": "activated",
  "document_id": "doc-id",
  "document_name": "My Design.free",
  "document_path": "/path/to/file.free"
}
```

**Fields:**

- `type` (string): Always `"document"`
- `timestamp` (string): ISO 8601 UTC timestamp
- `document_type` (string): Event type
  - `"activated"` - Document tab became active
  - `"deactivated"` - Document tab became inactive
  - `"opened"` - Document opened (future)
  - `"closed"` - Document closed (future)
- `document_id` (string, optional): Unique document identifier
- `document_name` (string, optional): Document display name
- `document_path` (string, optional): Full file path or URL

#### Window Event

Fired when Lunacy window state changes.

**Event Type:** `"window"`

**JSON Structure:**

```json
{
  "type": "window",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "event_type": "focused",
  "window_state": "normal"
}
```

**Fields:**

- `type` (string): Always `"window"`
- `timestamp` (string): ISO 8601 UTC timestamp
- `event_type` (string): Event type
  - `"focused"` - Window gained focus
  - `"unfocused"` - Window lost focus
  - `"state_changed"` - Window state changed
  - `"closing"` - Window about to close
- `window_state` (string, optional): For `state_changed` events
  - `"normal"` - Regular window
  - `"minimized"` - Minimized
  - `"fullscreen"` - Fullscreen mode

---

## Data Structures

### Request DTOs

#### ExportRequest

```typescript
{
  layerIds: string[],        // Required: Layer IDs to export
  format: string,             // Required: PNG, SVG, PDF, JPG, WEBP, TIFF, ICO
  scale: number,              // Optional: Scale factor (default: 1.0)
  mergeObjects: boolean       // Optional: Merge all layers (default: false)
}
```

#### CreateLayersRequest

```typescript
{
  parentId: string | null,    // Optional: Parent layer ID (null = root)
  layersJson: string          // Required: FREE format JSON string
}
```

#### DuplicateLayersRequest

```typescript
{
  layerIds: string[],              // Required: Layer IDs to duplicate
  offsetX: number,                 // Optional: X offset (default: 0)
  offsetY: number,                 // Optional: Y offset (default: 0)
  componentsToInstances: boolean   // Optional: Convert to instances (default: false)
}
```

#### GetLayersInAreaRequest

```typescript
{
  x: number,           // Required: Area X coordinate
  y: number,           // Required: Area Y coordinate
  width: number,       // Required: Area width
  height: number,      // Required: Area height
  maxDepth: number     // Optional: Max hierarchy depth (default: unlimited)
}
```

#### ScreenshotAreaRequest

```typescript
{
  x: number,           // Required: Area X coordinate
  y: number,           // Required: Area Y coordinate
  width: number,       // Required: Area width
  height: number       // Required: Area height
}
```

**Note:** Format and scale are specified via query parameters for screenshot endpoints, not in request body.

#### ShowToastRequest

```typescript
{
  text: string,              // Required: Toast message
  iconType: number,          // Optional: 0-13 (default: 0)
  priority: number,          // Optional: 1-255 (default: 5)
  durationSeconds: number,   // Optional: Display duration (default: 7)
  isContinuable: boolean,    // Optional: Can pause on hover (default: true)
  isSkippable: boolean,      // Optional: Can be skipped (default: false)
  isAttention: boolean       // Optional: Attention-grabbing (default: false)
}
```

#### GetImageRequest

```typescript
{
  id: string                 // Required: Image resource ID
}
```

### Response DTOs

#### ExportResult

```typescript
{
  layerId: string,       // Layer ID that was exported
  fileName: string,      // Generated file name
  contentType: string,   // MIME type (e.g., "image/png")
  data: number[]        // Byte array (binary data)
}
```

#### DuplicateLayersResponse

```typescript
{
  DuplicatedLayerIds: string[],   // IDs of created duplicates
  Message: string                  // Success message
}
```

### Layer Format

Layers use FREE format - Lunacy's internal JSON representation.

**Important Notes:**

- FREE format is **NULL-free, NaN-free, Infinity-free**
- Any NULL, NaN, or Infinity values mean broken JSON
- GUIDs are 22-character base64 strings
- **NO x/y/width/height properties** - use `transform` and `size` instead

### Understanding Transform Matrix

Layers use a **transform matrix** for positioning and transformations, NOT x/y coordinates.

**Matrix Format:** `[scaleX, skewX, transX, skewY, scaleY, transY]`

**Index Mapping:**

- `[0]` = scaleX (horizontal scale)
- `[1]` = skewX (horizontal skew)
- `[2]` = **transX (X position)**
- `[3]` = skewY (vertical skew)
- `[4]` = scaleY (vertical scale)
- `[5]` = **transY (Y position)**

**Examples:**

```javascript
// Identity transform (no transformation)
transform: [1, 0, 0, 0, 1, 0]

// Position at x=100, y=200
transform: [1, 0, 100, 0, 1, 200]

// Position at x=100, y=200, scaled 2x
transform: [2, 0, 100, 0, 2, 200]

// Get position from transform
const x = layer.transform[2];
const y = layer.transform[5];

// Set position in transform
layer.transform[2] = 150;  // X position
layer.transform[5] = 250;  // Y position

// Move layer by offset
layer.transform[2] += 20;  // Move right by 20px
layer.transform[5] += 10;  // Move down by 10px
```

**Helper Functions:**

```javascript
// Extract position from transform matrix
function getPosition(transform) {
  return { x: transform[2], y: transform[5] };
}

// Create transform matrix for position
function createTransform(x, y, scaleX = 1, scaleY = 1) {
  return [scaleX, 0, x, 0, scaleY, y];
}

// Update position in transform
function setPosition(transform, x, y) {
  const newTransform = [...transform];
  newTransform[2] = x;
  newTransform[5] = y;
  return newTransform;
}
```

**Common Layer Properties:**

```typescript
{
  id: string,              // Unique GUID (22 chars base64)
  name: string,            // Layer name
  _t: string,              // Layer type (see below)
  transform: number[],     // Transform matrix [scaleX, skewX, transX, skewY, scaleY, transY]
  size: [number, number],  // [width, height]
  locked: boolean,         // Lock state
  hidden: boolean,         // Visibility
  opacity: number,         // 0-1 opacity
  fills: object[],         // Fill styles
  borders: object[],       // Border styles
  shadows: object[],       // Drop shadows
  innerShadows: object[],  // Inner shadows
  blur: object,            // Blur effect
  cornerRadius: number[]   // Corner radii [topLeft, topRight, bottomRight, bottomLeft]
}
```

**Layer Types (`_t` field):**

- `RECT` - Rectangle
- `OVAL` - Oval
- `TEXT` - Text layer
- `PATH` - Vector path
- `GROUP` - Group
- `FRAME` - Frame
- `SECTION` - Section
- `POLYGON` - Polygon
- `STAR` - Star
- `TRIANGLE` - Triangle
- `SHAPE` - Shape with boolean operations
- `SLICE` - Slice
- `COMPONENT` - Component master
- `INSTANCE` - Component instance
- `STATES` - Component states

### Color Format

**CRITICAL:** Colors in FREE format are 32-bit ARGB (Alpha-Red-Green-Blue) strings.

**Format:** 8-character hexadecimal string `"AARRGGBB"`

- **AA** = Alpha (00-FF): 00=transparent, FF=opaque
- **RR** = Red (00-FF)
- **GG** = Green (00-FF)
- **BB** = Blue (00-FF)

**Examples:**

```javascript
// Correct - 8 characters (ARGB)
"color": "FFFF0000"  // ✅ Opaque red
"color": "FF00FF00"  // ✅ Opaque green
"color": "FF0000FF"  // ✅ Opaque blue
"color": "FF8B00FF"  // ✅ Opaque purple
"color": "80FF0000"  // ✅ Semi-transparent red (50% opacity)
"color": "00000000"  // ✅ Fully transparent (default)

// Wrong - 6 characters (RGB)
"color": "FF0000"    // ❌ Invalid! Missing alpha channel
"color": "00FF00"    // ❌ Invalid!
"color": "8B00FF"    // ❌ Invalid!
```

**Common Color Values:**

```javascript
const COLORS = {
  RED: "FFFF0000",
  GREEN: "FF00FF00",
  BLUE: "FF0000FF",
  WHITE: "FFFFFFFF",
  BLACK: "FF000000",
  TRANSPARENT: "00000000",
  PURPLE: "FF8B00FF",
  YELLOW: "FFFFFF00",
  CYAN: "FF00FFFF",
  MAGENTA: "FFFF00FF"
};
```

**Text Layer Additional Properties:**

```typescript
{
  _t: "TEXT",
  text: string,                // Text content
  textStyle: {                 // Text style properties
    font: string,              // Font family (default: "Inter")
    size: number,              // Font size in points (default: 12)
    fills: object[],           // Text color fills
    kerning: number,           // Letter spacing (default: 0)
    lineHeight: number,        // Line height (optional)
    align: number,             // Horizontal alignment (0=left, 1=right, 2=center, 3=justify)
    valign: number,            // Vertical alignment (0=top, 1=middle, 2=bottom)
    underline: boolean,        // Underline (default: false)
    strikethrough: boolean,    // Strikethrough (default: false)
    casing: number             // Character casing (0=normal, 1=upper, 2=lower, 3=title)
  },
  behavior: number,            // Text behavior (0=flexible, 1=autoHeight, 2=fixed)
  clipContent: boolean,        // Clip overflowing text (default: true)
  truncate: boolean            // Truncate text with ellipsis (default: false)
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Request succeeded
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "error": true,
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

### Common Errors

**Connection Refused**

```
Error: connect ECONNREFUSED 127.0.0.1:31415
```

Solution: Ensure Lunacy is running and Automation API is enabled.

**Invalid Layer ID**

```json
{
  "error": true,
  "message": "Layer not found",
  "code": "LAYER_NOT_FOUND"
}
```

**Invalid Format**

```json
{
  "error": true,
  "message": "Unsupported export format",
  "code": "INVALID_FORMAT"
}
```

### Error Handling Best Practices

**JavaScript/Node.js:**

```javascript
try {
  const response = await axios.get(`${API}/getselected`);
  // Process response
} catch (error) {
  if (error.response) {
    // Server returned error response (400, 500, etc.)
    console.error('API Error:', error.response.status);
  } else if (error.request) {
    // No response received (connection refused)
    console.error('Connection Error: Is Lunacy running?');
  } else {
    // Other errors
    console.error('Error:', error.message);
  }
}
```

**Python:**

```python
try:
    response = requests.get(f"{API}/getselected")
    response.raise_for_status()
    data = response.json()
except requests.exceptions.ConnectionError:
    print("Connection Error: Is Lunacy running?")
except requests.exceptions.HTTPError as e:
    print(f"API Error: {e.response.json()['message']}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Rate Limits

**Current Limits:**

- No rate limiting implemented
- Plugins can make unlimited API calls

**Best Practices:**

- Batch operations when possible (e.g., update multiple layers in one request)
- Use WebSocket events instead of polling
- Cache layer data to minimize API calls
- Avoid tight loops with API calls

**Future Considerations:**
Rate limiting may be added in future versions to prevent abuse.

---

## Examples

### Complete Plugin Example (Node.js)

```javascript
const axios = require('axios');

const API = 'http://localhost:31415';

async function modifySelectedLayers() {
  try {
    // Get selection
    const response = await axios.get(`${API}/getselected`);
    const selectionData = response.data;
    
    // Handle both single layer and array
    let layers = Array.isArray(selectionData) 
      ? selectionData 
      : [selectionData];
    
    // Check if anything selected (empty response is {})
    if (layers.length === 0 || !layers[0]._t) {
      await axios.post(`${API}/showtoast`, {
        text: 'Please select layers first',
        iconType: 4,  // Warning icon
        priority: 5,
        durationSeconds: 3
      });
      return;
    }
    
    // Modify layers
    const modified = layers.map(layer => ({
      ...layer,
      fills: [{color: 'FF0000'}],  // Red color
      name: `Modified ${layer.name}`
    }));
    
    // Update layers
    await axios.post(`${API}/updatelayers`, modified);
    
    // Show success
    await axios.post(`${API}/showtoast`, {
      text: `Modified ${modified.length} layer(s)`,
      iconType: 2,  // CheckDone icon
      priority: 5,
      durationSeconds: 3
    });
    
  } catch (error) {
    console.error('Error:', error.message);
    
    // Show error toast
    try {
      await axios.post(`${API}/showtoast`, {
        text: 'Operation failed',
        iconType: 4,  // Warning icon
        priority: 5,
        durationSeconds: 5
      });
    } catch (toastError) {
      // Suppress toast errors
    }
  }
}

modifySelectedLayers();
```

### WebSocket Monitor Example (Node.js)

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:31416');

ws.on('open', () => {
  console.log('Connected to Lunacy events');
});

ws.on('message', (data) => {
  const event = JSON.parse(data);
  
  switch (event.type) {
    case 'selection':
      console.log(`Selection changed: ${event.layer_count} layer(s)`);
      break;
      
    case 'undo':
      console.log(`Undo: ${event.operation} - ${event.operation_type}`);
      break;
      
    case 'document':
      console.log(`Document: ${event.document_type} - ${event.document_name}`);
      break;
      
    case 'window':
      console.log(`Window: ${event.event_type}`);
      break;
  }
});

ws.on('error', (error) => {
  console.error('WebSocket error:', error);
});

ws.on('close', () => {
  console.log('Disconnected');
});
```

---

## API Limits

### Maximum Request Size

- **Image upload**: 200 MB max (`AutomationApiConstants.Limits.MaxImageSizeBytes`)
- **JSON requests**: No specific limit, but reasonable sizes recommended

### Timeouts

- No server-side timeouts implemented
- Plugin timeout configured in `plugin.jsonc` per command (default: varies)

### Concurrent Requests

- Multiple requests from same plugin allowed
- No rate limiting currently implemented

## Additional Resources

- [Plugin Development Guide](./PLUGIN_DEVELOPMENT_GUIDE.md) - Complete guide for building plugins
- [Quick Start](./QUICK_START.md) - Build your first plugin in 5 minutes
- [Examples](../examples/) - Working plugin examples

## Support

For questions and issues:

- GitHub Issues: [icons8/lunacy-plugins](https://github.com/icons8/lunacy-plugins)
- Discord: Plugin development channel
- Documentation: [Lunacy Documentation](https://lunacy.docs.icons8.com)
