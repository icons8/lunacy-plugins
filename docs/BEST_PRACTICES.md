# Plugin Development Best Practices

Practical guidelines and patterns for building robust, performant, and maintainable Lunacy plugins.

## Table of Contents

- [Understanding FREE Format](#understanding-free-format)
- [Development Patterns](#development-patterns)
- [Error Handling](#error-handling)
- [Timeouts](#timeouts)
- [Memory Management](#memory-management)
- [Security](#security)
- [UI Design](#ui-design)
- [Performance](#performance)
- [Testing](#testing)
- [Code Quality](#code-quality)

---

## Understanding FREE Format

Lunacy uses FREE (internal JSON format) for layer data. Understanding its constraints is critical.

### Key Constraints

**1. NULL-free, NaN-free, Infinity-free**

FREE format does NOT allow these values:
```javascript
// WRONG - Invalid FREE format
{
  "id": "abc123",
  "name": null,          // ❌ NULL not allowed
  "opacity": NaN,        // ❌ NaN not allowed
  "rotation": Infinity   // ❌ Infinity not allowed
}
```

```javascript
// CORRECT - Valid FREE format
{
  "id": "abc123",
  "name": "",            // ✓ Empty string instead of null
  "opacity": 1.0,        // ✓ Valid number
  "rotation": 0          // ✓ Valid number
}
```

**2. GUID Format**

GUIDs are always 22-character base64 strings:
```javascript
// CORRECT GUID format
"id": "nF7kM2xPqE-ABcD3fGhIjK"  // Exactly 22 chars

// WRONG formats
"id": "550e8400-e29b-41d4..."   // UUID format (36 chars) - WRONG
"id": "abc123"                   // Too short - WRONG
```

**3. Property Names**

Use correct FREE property names:
```javascript
// CORRECT - FREE property names
{
  "borders": [...],      // ✓ Border styles
  "hidden": false,       // ✓ Visibility state
  "size": [100, 50],     // ✓ Width and height as array
  "transform": [...]     // ✓ Transform matrix
}

// WRONG - Invalid property names
{
  "strokes": [...],      // ❌ Invalid property
  "visible": true,       // ❌ Invalid property
  "width": 100,          // ❌ Use "size" array instead
  "height": 50,
  "x": 10,               // ❌ Use "transform" matrix
  "y": 20
}
```

**4. Layer Type Names**

Use correct `_t` values:
```javascript
// CORRECT layer types
"_t": "OVAL"      // ✓ Oval shape
"_t": "FRAME"     // ✓ Frame/artboard
"_t": "PATH"      // ✓ Vector path

// WRONG layer types
"_t": "oval"      // ❌ Must be UPPERCASE
"_t": "ARTBOARD"  // ❌ Invalid type (use FRAME)
"_t": "IMAGE"     // ❌ Invalid type (doesn't exist in FREE format)
```

### Working with Transform Matrix

Layers use transform matrix instead of x/y/rotation:

```javascript
// Transform matrix structure: [scaleX, skewX, transX, skewY, scaleY, transY]
// Index mapping: [0]=scaleX, [1]=skewX, [2]=X position, [3]=skewY, [4]=scaleY, [5]=Y position

// Identity transform (no transformation)
"transform": [1, 0, 0, 0, 1, 0]

// Translation only (x=100, y=50)
"transform": [1, 0, 100, 0, 1, 50]

// Translation + scale 2x
"transform": [2, 0, 100, 0, 2, 50]

// Helper to create translation matrix
function createTransform(x, y, scaleX = 1, scaleY = 1) {
  return [scaleX, 0, x, 0, scaleY, y];
}

// Helper to extract position from matrix
function getPosition(transform) {
  return { 
    x: transform[2],  // X is at index 2
    y: transform[5]   // Y is at index 5
  };
}

// Helper to update position in matrix
function setPosition(transform, x, y) {
  const newTransform = [...transform];
  newTransform[2] = x;
  newTransform[5] = y;
  return newTransform;
}

// Helper to move layer by offset
function moveLayer(layer, offsetX, offsetY) {
  const newTransform = [...layer.transform];
  newTransform[2] += offsetX;
  newTransform[5] += offsetY;
  return {
    ...layer,
    transform: newTransform
  };
}
```

### Common FREE Format Patterns

```javascript
// Pattern 1: Visibility
layer.hidden = true;   // ✓ Layer is hidden
layer.hidden = false;  // ✓ Layer is visible

// Pattern 2: Borders
layer.borders = [...]; // ✓ Correct property name

// Pattern 3: Size
layer.size = [100, 50]; // ✓ Array format [width, height]

// Pattern 4: Corner radius
layer.cornerRadius = [10, 10, 10, 10]; // ✓ [topLeft, topRight, bottomRight, bottomLeft]

// Pattern 5: Colors
fill.color = "FFFF0000"; // ✓ 8-char hex ARGB format
fill.color = "FF0000";   // ❌ Missing alpha channel
```

### Validation Helper

```javascript
function validateFreeFormat(layer) {
  const str = JSON.stringify(layer);
  
  // Check for forbidden values
  if (str.includes('null')) {
    throw new Error('FREE format cannot contain null');
  }
  if (str.includes('NaN')) {
    throw new Error('FREE format cannot contain NaN');
  }
  if (str.includes('Infinity')) {
    throw new Error('FREE format cannot contain Infinity');
  }
  
  // Validate GUID length
  if (layer.id && layer.id.length !== 22) {
    throw new Error(`Invalid GUID length: ${layer.id.length} (expected 22)`);
  }
  
  // Validate required fields
  if (!layer._t) {
    throw new Error('Layer must have _t (type) field');
  }
  
  return true;
}
```

---

## Development Patterns

### Helper Functions

Define common helpers at the start of your plugin:

```javascript
const axios = require('axios');
const API = 'http://localhost:31415';

async function showToast(text, iconType = 1) {
  await axios.post(`${API}/showtoast`, {
    text,
    iconType,
    priority: 5,
    durationSeconds: 3
  });
}
```

### Selection Handling

Always handle both single object and array responses from `/getselected`:

```javascript
// CORRECT
const response = await axios.get(`${API}/getselected`);
const data = response.data;
const layers = Array.isArray(data) ? data : [data];

// Check for empty selection (empty response is {})
if (layers.length === 0 || !layers[0]._t) {
  // Show warning and exit
  return;
}
```

```python
# CORRECT
response = requests.get(f"{API}/getselected")
data = response.json()
layers = data if isinstance(data, list) else [data]

# Check for empty selection
if not layers or not layers[0].get('_t'):
    # Show warning and exit
    return
```

### Layer Type Checking

Always verify layer type before operations:

```javascript
// CORRECT - Check layer type
const rectangles = layers.filter(l => l._t === 'RECT');
const texts = layers.filter(l => l._t === 'TEXT');

if (rectangles.length === 0) {
  await showToast('Please select rectangle layers', 4);
  return;
}
```

**Common Layer Types:**
- `RECT` - Rectangle
- `OVAL` - Oval/Ellipse
- `TEXT` - Text layer
- `PATH` - Vector path
- `GROUP` - Group
- `FRAME` - Frame/Artboard
- `SECTION` - Section
- `POLYGON` - Polygon
- `STAR` - Star
- `TRIANGLE` - Triangle
- `SHAPE` - Shape (boolean operation container)
- `COMPONENT` - Component master
- `INSTANCE` - Component instance

### Batch Operations

Update multiple layers in single API call for better performance:

```javascript
// CORRECT - Batch update
const modified = layers.map(layer => {
  // Modify transform matrix for position (FREE format uses transform, not x/y)
  const newTransform = [...layer.transform];
  newTransform[2] += 10; // Offset X position
  
  return {
    ...layer,
    transform: newTransform,
    fills: [{color: 'FF0000'}]
  };
});

await axios.post(`${API}/updatelayers`, modified);
```

```javascript
// WRONG - Multiple API calls
for (const layer of layers) {
  await axios.post(`${API}/updatelayers`, [layer]);
}
```

### State Management for Service Plugins

Maintain plugin state properly:

```javascript
// CORRECT - Track state
let isProcessing = false;
let lastSelection = [];

ws.on('message', async (data) => {
  const event = JSON.parse(data);
  
  // Prevent concurrent operations
  if (isProcessing) return;
  
  if (event.type === 'selection') {
    isProcessing = true;
    try {
      await handleSelection(event);
      lastSelection = event.layer_ids;
    } finally {
      isProcessing = false;
    }
  }
});
```

### Resource Cleanup

Always clean up resources on exit:

```javascript
// CORRECT - Cleanup on exit
process.on('SIGTERM', async () => {
  console.log('Shutting down...');
  
  // Close WebSocket
  if (ws) ws.close();
  
  // Save state
  await saveState();
  
  // Exit gracefully
  process.exit(0);
});
```

---

## Error Handling

### API Call Error Handling

Handle connection errors, HTTP errors, and timeouts:

```javascript
// CORRECT - Comprehensive error handling
async function safeApiCall(endpoint, method = 'GET', data = null) {
  try {
    const config = {
      method,
      url: `${API}${endpoint}`,
      timeout: 5000
    };
    
    if (data) config.data = data;
    
    const response = await axios(config);
    return { success: true, data: response.data };
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      return { 
        success: false, 
        error: 'Connection refused - Is Lunacy running?' 
      };
    }
    
    if (error.response) {
      return { 
        success: false, 
        error: `API error: ${error.response.status}` 
      };
    }
    
    if (error.code === 'ECONNABORTED') {
      return { 
        success: false, 
        error: 'Request timeout' 
      };
    }
    
    return { 
      success: false, 
      error: error.message 
    };
  }
}
```

### User-Friendly Error Messages

Provide clear, actionable error messages:

```javascript
// CORRECT - Clear error messages
if (layers.length === 0) {
  await showToast('Please select at least one layer', 4);
  return;
}

if (!layers.every(l => l._t === 'RECT')) {
  await showToast('This plugin only works with rectangles', 4);
  return;
}

if (outputPath && !fs.existsSync(outputPath)) {
  await showToast(`Output directory not found: ${outputPath}`, 4);
  return;
}
```

```javascript
// WRONG - Cryptic errors
if (layers.length === 0) {
  console.error('Error: invalid input');
  return;
}
```

### Error Recovery

Implement retry logic for transient errors:

```javascript
// CORRECT - Retry with exponential backoff
async function retryApiCall(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      const delay = Math.pow(2, i) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

// Usage
const result = await retryApiCall(async () => {
  return await axios.get(`${API}/getselected`);
});
```

### Logging Errors

Log errors for debugging but don't expose internals to users:

```javascript
// CORRECT - Log details, show friendly message
try {
  await processLayers(layers);
} catch (error) {
  // Detailed logging for debugging
  console.error('Plugin error:', {
    message: error.message,
    stack: error.stack,
    context: { layerCount: layers.length }
  });
  
  // User-friendly message
  await showToast('Operation failed. Check console for details.', 4);
}
```

---

## Timeouts

### Configure Appropriate Timeouts

Set realistic timeouts based on operation complexity:

```jsonc
// plugin.jsonc
{
  "commands": [
    {
      "id": "quick-operation",
      "name": "Quick Operation",
      "executable": "node",
      "args": ["script.js"],
      "timeoutMs": 5000  // 5 seconds for simple operations
    },
    {
      "id": "export-operation",
      "name": "Export All",
      "executable": "node",
      "args": ["export.js"],
      "timeoutMs": 60000  // 60 seconds for export operations
    },
    {
      "id": "ai-operation",
      "name": "AI Processing",
      "executable": "python3",
      "args": ["ai_process.py"],
      "timeoutMs": 120000  // 2 minutes for AI/LLM operations
    }
  ]
}
```

### Internal Timeout Handling

Implement internal timeouts for external services:

```javascript
// CORRECT - Timeout for external API
async function callExternalApi(data) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  
  try {
    const response = await fetch('https://api.example.com/process', {
      method: 'POST',
      body: JSON.stringify(data),
      signal: controller.signal
    });
    
    return await response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('External API timeout');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
```

### Progress Feedback

Show progress for long-running operations:

```javascript
// CORRECT - Progress updates
async function processLargeBatch(items) {
  const total = items.length;
  
  for (let i = 0; i < total; i++) {
    await processItem(items[i]);
    
    // Update progress every 10 items
    if (i % 10 === 0) {
      await showToast(
        `Processing: ${i + 1}/${total}`,
        1,  // Info icon
        5,
        2   // Short duration
      );
    }
  }
  
  await showToast(`Completed: ${total} items processed`, 2);
}
```

---

## Memory Management

### Service Plugin Memory

Service plugins run continuously - manage memory carefully:

```javascript
// CORRECT - Bounded cache
class BoundedCache {
  constructor(maxSize = 100) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }
  
  set(key, value) {
    if (this.cache.size >= this.maxSize) {
      // Remove oldest entry
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
  
  get(key) {
    return this.cache.get(key);
  }
  
  clear() {
    this.cache.clear();
  }
}

// Usage
const layerCache = new BoundedCache(50);
```

### Avoid Memory Leaks

Common memory leak patterns to avoid:

```javascript
// WRONG - Global accumulation
let allProcessedLayers = [];

ws.on('message', (data) => {
  const event = JSON.parse(data);
  allProcessedLayers.push(event);  // Grows forever!
});
```

```javascript
// CORRECT - Bounded storage
const recentEvents = [];
const MAX_EVENTS = 100;

ws.on('message', (data) => {
  const event = JSON.parse(data);
  recentEvents.push(event);
  
  if (recentEvents.length > MAX_EVENTS) {
    recentEvents.shift();  // Remove oldest
  }
});
```

### Large Data Handling

Process large datasets in chunks:

```javascript
// CORRECT - Chunked processing
async function processLargeSelection(layers) {
  const CHUNK_SIZE = 50;
  
  for (let i = 0; i < layers.length; i += CHUNK_SIZE) {
    const chunk = layers.slice(i, i + CHUNK_SIZE);
    await processChunk(chunk);
    
    // Allow GC between chunks
    if (global.gc) global.gc();
  }
}
```

### Clean Up Resources

Release resources when done:

```javascript
// CORRECT - Resource cleanup
async function processWithTempFiles() {
  const tempFiles = [];
  
  try {
    // Create temp files
    for (const layer of layers) {
      const tempFile = await createTempFile(layer);
      tempFiles.push(tempFile);
      await processFile(tempFile);
    }
  } finally {
    // Always clean up
    for (const file of tempFiles) {
      try {
        await fs.unlink(file);
      } catch (error) {
        console.error(`Failed to delete ${file}:`, error);
      }
    }
  }
}
```

---

## Security

### Input Validation

Always validate and sanitize inputs:

```javascript
// CORRECT - Validate layer data
function validateLayer(layer) {
  if (!layer || typeof layer !== 'object') {
    throw new Error('Invalid layer object');
  }
  
  if (!layer.id || typeof layer.id !== 'string') {
    throw new Error('Invalid layer ID');
  }
  
  // GUID must be exactly 22 chars (base64)
  if (layer.id.length !== 22) {
    throw new Error('Invalid GUID format');
  }
  
  if (!layer._t || typeof layer._t !== 'string') {
    throw new Error('Invalid layer type');
  }
  
  // FREE format is NULL-free, NaN-free, Infinity-free
  const jsonStr = JSON.stringify(layer);
  if (jsonStr.includes('null') || jsonStr.includes('NaN') || jsonStr.includes('Infinity')) {
    throw new Error('Invalid FREE format: contains null/NaN/Infinity');
  }
  
  return true;
}

// Use validation
try {
  layers.forEach(validateLayer);
  await processLayers(layers);
} catch (error) {
  await showToast(`Validation error: ${error.message}`, 4);
  return;
}
```

### Path Security

Prevent path traversal attacks:

```javascript
// CORRECT - Safe path handling
const path = require('path');

function safeOutputPath(userPath, basePath) {
  const resolved = path.resolve(basePath, userPath);
  
  // Ensure path is within base directory
  if (!resolved.startsWith(path.resolve(basePath))) {
    throw new Error('Invalid output path');
  }
  
  return resolved;
}

// Usage
const outputPath = safeOutputPath(
  userProvidedPath,
  '/safe/output/directory'
);
```

### API Key Management

Never hardcode or log API keys:

```javascript
// CORRECT - Use environment variables
require('dotenv').config();

const API_KEY = process.env.OPENAI_API_KEY;

if (!API_KEY) {
  console.error('Error: OPENAI_API_KEY not set');
  await showToast('API key not configured', 4);
  process.exit(1);
}

// Use API key (never log it)
const response = await fetch('https://api.openai.com/v1/chat', {
  headers: {
    'Authorization': `Bearer ${API_KEY}`
  }
});
```

```javascript
// WRONG - Exposed keys
const API_KEY = 'sk-proj-abc123...';  // NEVER DO THIS
console.log('Using key:', API_KEY);    // NEVER LOG KEYS
```

### Command Injection Prevention

Avoid executing user-provided commands:

```javascript
// WRONG - Command injection risk
const { exec } = require('child_process');
exec(`convert ${userFilename} output.png`);  // DANGEROUS!
```

```javascript
// CORRECT - Use safe APIs
const sharp = require('sharp');
await sharp(sanitizedFilename)
  .png()
  .toFile('output.png');
```

### Limit Resource Usage

Protect against resource exhaustion:

```javascript
// CORRECT - Limit file size
const MAX_FILE_SIZE = 200 * 1024 * 1024;  // 200 MB

async function validateFileSize(filePath) {
  const stats = await fs.stat(filePath);
  
  if (stats.size > MAX_FILE_SIZE) {
    throw new Error(`File too large: ${stats.size} bytes`);
  }
  
  return true;
}
```

---

## UI Design

### Choose Appropriate UI Type

**Toast notifications** for:
- Quick status updates
- Progress indication
- Error messages
- Confirmation of actions

```javascript
await axios.post(`${API}/showtoast`, {
  text: 'Export complete: 5 files created',
  iconType: 1
});
```

**Dynamic UI registration** for:
- Configuration before operation
- Multiple user inputs needed
- Settings that persist across runs

```javascript
await axios.post(`${API}/registerui`, {
  pluginId: 'my-plugin',
  title: 'Settings',
  fields: [...]
});
```

**External UI** for:
- Complex workflows
- Real-time preview
- Rich interactive controls

### Always Handle UI Lifecycle

Service plugins MUST listen to `show_ui` and `close_ui` events:

```javascript
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:31416');

ws.on('message', async (data) => {
  const event = JSON.parse(data);
  
  if (event.event === 'show_ui' && event.pluginId === 'my-plugin') {
    console.log('UI opened');
  }
  
  if (event.event === 'close_ui' && event.pluginId === 'my-plugin') {
    const values = await axios.post(`${API}/getpluginuivalues`, "my-plugin");
    await processValues(values.data);
    await axios.post(`${API}/unregisterui`, { pluginId: 'my-plugin' });
  }
});
```

### Always Cleanup UI

Unregister UI when done:

```javascript
try {
  await performOperation();
} finally {
  await axios.post(`${API}/unregisterui`, { pluginId: 'my-plugin' });
}
```

### Don't Block UI Thread

For long operations, show progress:

```javascript
for (let i = 0; i < items.length; i++) {
  await processItem(items[i]);
  
  if (i % 10 === 0) {
    await axios.post(`${API}/showtoast`, {
      text: `Processing ${i + 1}/${items.length}...`,
      iconType: 5,
      isContinuable: true
    });
  }
}
```

See [UI_DESIGN_GUIDE.md](./UI_DESIGN_GUIDE.md) for complete UI reference.

---

## Performance

### Minimize API Calls

Batch operations and cache results:

```javascript
// CORRECT - Single batch call
const layerIds = selection.map(l => l.id);
const layers = await axios.post(`${API}/getlayersbyids`, layerIds);
```

```javascript
// WRONG - Multiple calls
const layers = [];
for (const item of selection) {
  const layer = await axios.post(`${API}/getlayersbyids`, [item.id]);
  layers.push(layer.data[0]);
}
```

### Use WebSocket for Real-Time Updates

For service plugins monitoring events:

```javascript
// CORRECT - WebSocket for events
const ws = new WebSocket('ws://localhost:31416');

ws.on('message', (data) => {
  const event = JSON.parse(data);
  if (event.type === 'selection') {
    handleSelectionChange(event);
  }
});
```

```javascript
// WRONG - Polling (slow and inefficient)
setInterval(async () => {
  const response = await axios.get(`${API}/getselected`);
  // Check if changed...
}, 1000);
```

### Optimize Data Serialization

Minimize data transferred:

```javascript
// CORRECT - Only request needed fields
const response = await axios.post(`${API}/getlayersbyids`, layerIds);
const minimalData = response.data.map(l => ({
  id: l.id,
  name: l.name,
  transform: l.transform,
  size: l.size
}));
```

### Async/Await Patterns

Use Promise.all for concurrent operations:

```javascript
// CORRECT - Concurrent execution
const results = await Promise.all(
  layers.map(layer => processLayer(layer))
);
```

```javascript
// WRONG - Sequential execution
const results = [];
for (const layer of layers) {
  results.push(await processLayer(layer));
}
```

### Debounce Frequent Operations

Avoid excessive processing:

```javascript
// CORRECT - Debounced handler
function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

const handleSelectionChange = debounce(async (event) => {
  await processSelection(event);
}, 500);

ws.on('message', (data) => {
  const event = JSON.parse(data);
  if (event.type === 'selection') {
    handleSelectionChange(event);
  }
});
```

---

## Testing

### Unit Testing

Test core logic separately from API calls:

```javascript
// layer-processor.js
function calculateNewPositions(layers, offsetX, offsetY) {
  return layers.map(layer => {
    // FREE format uses transform matrix [scaleX, skewX, transX, skewY, scaleY, transY]
    const newTransform = [...layer.transform];
    newTransform[2] += offsetX; // Update X translation
    newTransform[5] += offsetY; // Update Y translation
    
    return {
      ...layer,
      transform: newTransform
    };
  });
}

module.exports = { calculateNewPositions };
```

```javascript
// layer-processor.test.js
const { calculateNewPositions } = require('./layer-processor');

test('should offset layer positions', () => {
  const layers = [
    { id: '1', transform: [1, 0, 0, 0, 1, 0] },     // x=0, y=0
    { id: '2', transform: [1, 0, 10, 0, 1, 20] }    // x=10, y=20
  ];
  
  const result = calculateNewPositions(layers, 5, 10);
  
  expect(result[0].transform).toEqual([1, 0, 5, 0, 1, 10]);    // x=5, y=10
  expect(result[1].transform).toEqual([1, 0, 15, 0, 1, 30]);   // x=15, y=30
});
```

### Integration Testing

Test with mock API:

```javascript
// plugin.test.js
const nock = require('nock');

test('should handle empty selection', async () => {
  // Mock API response
  nock('http://localhost:31415')
    .get('/getselected')
    .reply(200, {});
  
  const result = await runPlugin();
  
  expect(result.error).toBe('No layers selected');
});

test('should process selection', async () => {
  nock('http://localhost:31415')
    .get('/getselected')
    .reply(200, [
      { id: '1', _t: 'RECT', x: 0, y: 0 }
    ]);
  
  nock('http://localhost:31415')
    .post('/updatelayers')
    .reply(200, { success: true });
  
  const result = await runPlugin();
  
  expect(result.success).toBe(true);
});
```

### Manual Testing Checklist

Before releasing plugin:

- [ ] Test with no selection
- [ ] Test with single layer selected
- [ ] Test with multiple layers selected
- [ ] Test with different layer types
- [ ] Test with large selections (100+ layers)
- [ ] Test timeout behavior
- [ ] Test error scenarios (Lunacy closed, network issues)
- [ ] Test on all supported platforms (Windows, macOS, Linux)
- [ ] Verify toast notifications appear correctly
- [ ] Check for memory leaks (service plugins)

---

## Code Quality

### Consistent Code Style

Use linters and formatters:

```json
// .eslintrc.json
{
  "extends": "eslint:recommended",
  "env": {
    "node": true,
    "es2021": true
  },
  "rules": {
    "no-unused-vars": "error",
    "no-console": "off",
    "semi": ["error", "always"],
    "quotes": ["error", "single"]
  }
}
```

### Documentation

Document complex logic:

```javascript
// CORRECT - Document non-obvious logic
/**
 * Calculates optimal grid layout for layers.
 * Uses bin-packing algorithm to minimize empty space.
 * 
 * @param {Array} layers - Layers to arrange
 * @param {number} maxWidth - Maximum grid width
 * @returns {Array} Layers with updated positions
 */
function calculateGridLayout(layers, maxWidth) {
  // Implementation...
}
```

### Type Safety (TypeScript)

Consider TypeScript for large plugins:

```typescript
// types.ts
interface Layer {
  id: string;
  name: string;
  _t: LayerType;
  transform: number[];
  size: number[];
}

type LayerType = 'RECT' | 'OVAL' | 'TEXT' | 'PATH' | 'GROUP' | 'FRAME';

// plugin.ts
function processLayers(layers: Layer[]): Layer[] {
  return layers.map(layer => {
    const newTransform = [...layer.transform];
    newTransform[2] += 10;
    return {
      ...layer,
      transform: newTransform
    };
  });
}
```

### Version Control

Use semantic versioning:

```jsonc
// plugin.jsonc
{
  "version": "1.2.3",
  // 1 = major (breaking changes)
  // 2 = minor (new features)
  // 3 = patch (bug fixes)
}
```

---

## Common Pitfalls

### Don't Assume Selection Type

```javascript
// WRONG - Assumes array
const firstLayer = selection[0];

// CORRECT - Handle both
const layers = Array.isArray(selection) ? selection : [selection];
const firstLayer = layers[0];
```

### Don't Ignore Empty Responses

```javascript
// WRONG - No empty check
const layers = response.data;
await processLayers(layers);

// CORRECT - Validate first
const layers = Array.isArray(response.data) 
  ? response.data 
  : [response.data];

if (layers.length === 0 || !layers[0]._t) {
  await showToast('Please select layers', 4);
  return;
}
```

### Don't Block Event Loop

```javascript
// WRONG - Synchronous heavy operation
const result = heavyComputationSync(data);

// CORRECT - Async or worker thread
const result = await heavyComputationAsync(data);
// OR
const { Worker } = require('worker_threads');
const worker = new Worker('./worker.js');
```

### Don't Forget Cleanup

```javascript
// WRONG - No cleanup
const ws = new WebSocket('ws://localhost:31416');

// CORRECT - Cleanup on exit
process.on('SIGTERM', () => {
  if (ws) ws.close();
  process.exit(0);
});
```

---

## Additional Resources

- [Plugin Development Guide](./PLUGIN_DEVELOPMENT_GUIDE.md) - Complete development guide
- [API Reference](./API_REFERENCE.md) - Full API documentation
- [Examples](./examples/) - Working plugin examples
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions

## Summary

Key takeaways:

1. **Always handle both single and array responses** from selection API
2. **Validate inputs** before processing
3. **Batch API calls** for better performance
4. **Handle errors gracefully** with user-friendly messages
5. **Set appropriate timeouts** based on operation complexity
6. **Manage memory** carefully in service plugins
7. **Validate and sanitize** all inputs for security
8. **Test thoroughly** before release
9. **Document your code** for maintainability
10. **Follow semantic versioning** for updates
