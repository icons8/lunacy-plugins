# Plugin Troubleshooting Guide

Comprehensive guide to diagnosing and fixing common plugin issues.

## Table of Contents

- [Quick Diagnostic Checklist](#quick-diagnostic-checklist)
- [Plugin Not Appearing](#plugin-not-appearing)
- [Connection Issues](#connection-issues)
- [Execution Failures](#execution-failures)
- [Data Issues](#data-issues)
- [Performance Problems](#performance-problems)
- [Service Plugin Issues](#service-plugin-issues)
- [Dynamic UI Issues](#dynamic-ui-issues)
- [Debugging Tools](#debugging-tools)
- [Logging and Diagnostics](#logging-and-diagnostics)
- [FAQ](#faq)

---

## Quick Diagnostic Checklist

When your plugin isn't working, check these first:

### Basic Checks

- [ ] Is Lunacy running?
- [ ] Is Automation API enabled? (Check: `AI → Model Context Protocol → MCP server enabled`)
- [ ] Test API: `curl http://localhost:31415/getselected` (should respond, not "Connection refused")
- [ ] Is `plugin.jsonc` syntax valid? (Use JSON validator)
- [ ] Are file paths in `plugin.jsonc` correct?
- [ ] Does the plugin directory exist in correct location?
- [ ] Did you restart Lunacy after changes?

### Platform-Specific Plugin Directories

**Windows:**

```
%LOCALAPPDATA%\Icons8\Lunacy\Plugins\your-plugin-name\
```

Example: `C:\Users\YourName\AppData\Local\Icons8\Lunacy\Plugins\your-plugin-name\`

**macOS:**

```bash
~/Library/Application Support/Icons8/Lunacy/Plugins/your-plugin-name/
```

**Linux:**

```bash
~/.local/share/Icons8/Lunacy/Plugins/your-plugin-name/
```

### Quick Tests

**Test API connectivity:**

Windows (PowerShell):

```powershell
Invoke-WebRequest -Uri http://localhost:31415/getselected
```

macOS/Linux:

```bash
curl http://localhost:31415/getselected
```

**Test plugin script directly:**

Windows (PowerShell):

```powershell
node your-plugin.js
python your-plugin.py
dotnet run --project YourPlugin.csproj
```

macOS/Linux:

```bash
node your-plugin.js
python3 your-plugin.py
dotnet run --project YourPlugin.csproj
```

---

## Plugin Not Appearing

### Problem: Plugin doesn't show in Plugins menu

**Cause 1: Invalid JSON syntax**

Windows (PowerShell):

```powershell
Get-Content plugin.jsonc | ConvertFrom-Json
```

macOS/Linux:

```bash
cat plugin.jsonc | jq .
```

Common JSON errors:

- Missing commas
- Trailing commas (last item in array/object)
- Unquoted keys
- Single quotes instead of double quotes
- Comments in `.json` files (use `.jsonc` for comments)

**Solution:**

```jsonc
// WRONG
{
  id: "my-plugin",           // ❌ Unquoted key
  'name': 'My Plugin',       // ❌ Single quotes
  "version": "1.0.0",        // ❌ Trailing comma
}

// CORRECT
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0"
}
```

**Cause 2: Wrong file location**

Windows (PowerShell):

```powershell
# Check if plugin directory exists
Get-ChildItem "$env:LOCALAPPDATA\Icons8\Lunacy\Plugins\"

# Check if plugin.jsonc exists
Test-Path "$env:LOCALAPPDATA\Icons8\Lunacy\Plugins\your-plugin-name\plugin.jsonc"
```

macOS:

```bash
ls ~/Library/Application\ Support/Icons8/Lunacy/Plugins/
ls ~/Library/Application\ Support/Icons8/Lunacy/Plugins/your-plugin-name/plugin.jsonc
```

Linux:

```bash
ls ~/.local/share/Icons8/Lunacy/Plugins/
ls ~/.local/share/Icons8/Lunacy/Plugins/your-plugin-name/plugin.jsonc
```

**Solution:**

- Create plugin directory in correct location
- Ensure `plugin.jsonc` is in plugin root directory
- Restart Lunacy

**Cause 3: Missing required fields**

Required fields in `plugin.jsonc`:

- `id` - Unique plugin identifier
- `name` - Display name
- `version` - Version string
- Either `commands` array (utility) or `serviceCommand` (service)

**Cause 4: Invalid executable path**

```jsonc
// WRONG - Absolute path
{
  "executable": "/usr/bin/node",
  "args": ["/home/user/plugin.js"]
}

// CORRECT - Relative to plugin directory or system PATH
{
  "executable": "node",
  "args": ["plugin.js"]
}
```

### Problem: Plugin appears but commands are disabled

**Cause:** Executable not found or not executable

**Solution:**

Windows (PowerShell):

```powershell
# Check if executable exists
Get-Command node
Get-Command python
Get-Command dotnet
```

macOS/Linux:

```bash
# Check if executable exists
which node
which python3
which dotnet

# Make script executable
chmod +x your-script.sh
```

---

## Connection Issues

### Problem: "Connection refused" or "ECONNREFUSED"

**Cause 1: Lunacy not running**

**Solution:**

- Start Lunacy
- Wait for it to fully load
- Retry plugin

**Cause 2: Automation API disabled**

**Solution:**

The Automation API is controlled by a setting in Lunacy's AI menu:

1. **Open Lunacy**
2. **Go to menu:** `AI → Model Context Protocol`
3. **Enable checkbox:** "MCP server enabled"
4. **Verify it's running:**

Windows (PowerShell):

```powershell
Invoke-WebRequest -Uri http://localhost:31415/getselected
```

macOS/Linux:

```bash
curl http://localhost:31415/getselected
```

**Expected behavior:**

- If server is running: You'll get a response (200 OK or JSON data)
- If server is disabled: "Connection refused" error

**Note:** The server will automatically enable when you add your first plugin to the plugins directory,
but you can enable it manually at any time.

**Location of the setting:**

- Menu: `AI → Model Context Protocol → MCP server enabled`
- Default port: `31415`
- Setting key: `IsMcpServerEnabled` (boolean)

**Cause 3: Port conflict**

Windows (PowerShell):

```powershell
Get-NetTCPConnection -LocalPort 31415
```

macOS/Linux:

```bash
lsof -i :31415
```

**Solution:**

- Close other applications using port 31415
- Restart Lunacy

**Cause 4: Firewall blocking**

**Solution:**

Windows:

- Open Windows Defender Firewall
- Check if Lunacy is allowed through firewall
- Localhost connections usually allowed by default

macOS:

- System Preferences > Security & Privacy > Firewall
- Allow Lunacy if prompted
- Localhost connections usually allowed by default

Linux:

```bash
# Allow localhost connections (if using ufw)
sudo ufw allow from 127.0.0.1 to any port 31415

# Check firewall status
sudo ufw status
```

### Problem: Timeout errors

**Cause:** Operation takes longer than configured timeout

**Solution:**
Increase timeout in `plugin.jsonc`:

```jsonc
{
  "commands": [
    {
      "id": "long-operation",
      "name": "Long Operation",
      "executable": "node",
      "args": ["script.js"],
      "timeoutMs": 60000  // Increase to 60 seconds
    }
  ]
}
```

Recommended timeouts:

- Simple operations: 5000ms (5 sec)
- Export operations: 30000ms (30 sec)
- AI/LLM operations: 120000ms (2 min)

---

## Execution Failures

### Problem: Plugin exits immediately without output

**Debugging steps:**

1. **Test script directly:**

Windows (PowerShell):

```powershell
node your-plugin.js
python your-plugin.py
```

macOS/Linux:

```bash
node your-plugin.js
python3 your-plugin.py
```

2. **Check script permissions (macOS/Linux only):**

```bash
ls -l your-plugin.js
# Should be readable: -rw-r--r--
```

3. **Check shebang (macOS/Linux executable scripts):**

```bash
#!/usr/bin/env node
# Must be first line, not needed on Windows
```

4. **Check dependencies:**

Node.js (all platforms):

```bash
npm install
npm list
```

Python (Windows PowerShell):

```powershell
pip install -r requirements.txt
pip list
```

Python (macOS/Linux):

```bash
pip3 install -r requirements.txt
pip3 list
```

C# (all platforms):

```bash
dotnet restore
dotnet build
```

### Problem: Script runs but does nothing

**Cause 1: No selection**

```javascript
// Add selection check
const response = await axios.get(`${API}/getselected`);
const data = response.data;
const layers = Array.isArray(data) ? data : [data];

if (layers.length === 0 || !layers[0]._t) {
  console.error('No layers selected');
  await showToast('Please select layers', 4);
  process.exit(1);
}
```

**Cause 2: Silent errors**

```javascript
// Always log errors
try {
  await processLayers(layers);
} catch (error) {
  console.error('Plugin error:', error);
  console.error('Stack:', error.stack);
  process.exit(1);
}
```

**Cause 3: Wrong API endpoint**

```javascript
// Check response status
const response = await axios.get(`${API}/getselected`);
console.log('Status:', response.status);
console.log('Data:', response.data);

if (response.status !== 200) {
  throw new Error(`API error: ${response.status}`);
}
```

### Problem: Permission denied errors

**Windows:**

```powershell
# Check file ownership
Get-Acl "$env:LOCALAPPDATA\Icons8\Lunacy\Plugins\your-plugin-name"

# Run PowerShell as administrator if needed
# Right-click PowerShell > Run as administrator
```

**macOS/Linux:**

```bash
# Check file permissions
ls -l ~/Library/Application\ Support/Icons8/Lunacy/Plugins/your-plugin-name/  # macOS
ls -l ~/.local/share/Icons8/Lunacy/Plugins/your-plugin-name/  # Linux

# Fix permissions
chmod 755 plugin-directory/
chmod 644 plugin.jsonc
chmod 755 script.js  # If executable script
```

---

## Data Issues

### Problem: Empty selection response

**Cause:** Nothing selected in Lunacy

**Solution:**

```javascript
// Always check for empty selection
const response = await axios.get(`${API}/getselected`);
const data = response.data;

// Empty response is {}
if (!data || Object.keys(data).length === 0) {
  console.error('Nothing selected');
  process.exit(1);
}

// Convert to array
const layers = Array.isArray(data) ? data : [data];

// Validate layer data
if (layers.length === 0 || !layers[0]._t) {
  console.error('Invalid selection');
  process.exit(1);
}
```

### Problem: "Layer not found" errors

**Cause:** Layer ID doesn't exist or changed

**Debug approach:**

```javascript
// Log layer IDs
console.log('Selected layer IDs:', layers.map(l => l.id));

// Verify layer exists before operations
const layerIds = layers.map(l => l.id);
const verification = await axios.post(`${API}/getlayersbyids`, layerIds);

if (verification.data.length !== layerIds.length) {
  console.error('Some layers not found');
}
```

**Solution:**

- Don't cache layer IDs between operations
- Always get fresh selection data
- Validate layer IDs before use

### Problem: Export data corrupted

**Cause:** Incorrect data handling

**Solution:**

```javascript
// WRONG - Treating byte array as string
const data = result.data.toString();

// CORRECT - Handle as Buffer
const buffer = Buffer.from(result.data);
fs.writeFileSync(filename, buffer);
```

```python
# CORRECT - Python
file_data = bytes(result["data"])
with open(filename, "wb") as f:
    f.write(file_data)
```

### Problem: FREE format validation errors

**Cause:** Invalid FREE format data

**Common issues:**

```javascript
// NULL values
layer.name = null;  // ❌ Use empty string: ""

// NaN values
layer.opacity = NaN;  // ❌ Use valid number: 1.0

// Infinity
layer.rotation = Infinity;  // ❌ Use valid number: 0

// Wrong GUID length
layer.id = "abc123";  // ❌ Must be 22 chars base64
```

**Solution:**

```javascript
function sanitizeFreeFormat(layer) {
  // Remove null values
  Object.keys(layer).forEach(key => {
    if (layer[key] === null) {
      if (typeof key === 'string') {
        layer[key] = '';
      } else if (typeof key === 'number') {
        layer[key] = 0;
      }
    }
  });
  
  // Replace NaN and Infinity
  if (isNaN(layer.opacity)) layer.opacity = 1.0;
  if (!isFinite(layer.rotation)) layer.rotation = 0;
  
  return layer;
}
```

---

## Performance Problems

### Problem: Plugin is slow

**Diagnosis:**

```javascript
// Add timing
console.time('operation');
await performOperation();
console.timeEnd('operation');
```

**Common causes:**

1. **Too many API calls**

```javascript
// SLOW - Multiple calls
for (const layer of layers) {
  await axios.post(`${API}/updatelayers`, [layer]);
}

// FAST - Single batch call
await axios.post(`${API}/updatelayers`, layers);
```

2. **Large data transfers**

```javascript
// Only request needed data
const layers = await axios.post(`${API}/getlayersbyids`, layerIds);
const minimal = layers.data.map(l => ({
  id: l.id,
  name: l.name,
  size: l.size
}));
```

3. **Synchronous operations**

```javascript
// SLOW - Sequential
for (const layer of layers) {
  await processLayer(layer);
}

// FAST - Parallel
await Promise.all(layers.map(processLayer));
```

### Problem: Memory usage growing

**Cause:** Memory leak in service plugin

**Diagnosis:**

```javascript
// Monitor memory
setInterval(() => {
  const usage = process.memoryUsage();
  console.log('Memory:', {
    rss: `${Math.round(usage.rss / 1024 / 1024)}MB`,
    heapUsed: `${Math.round(usage.heapUsed / 1024 / 1024)}MB`
  });
}, 60000);
```

**Solution:**

```javascript
// Limit cache size
const cache = new Map();
const MAX_CACHE_SIZE = 100;

function addToCache(key, value) {
  if (cache.size >= MAX_CACHE_SIZE) {
    const firstKey = cache.keys().next().value;
    cache.delete(firstKey);
  }
  cache.set(key, value);
}

// Clear old data
function clearOldData() {
  const cutoff = Date.now() - 3600000; // 1 hour
  for (const [key, value] of cache.entries()) {
    if (value.timestamp < cutoff) {
      cache.delete(key);
    }
  }
}

setInterval(clearOldData, 300000); // Every 5 minutes
```

---

## Service Plugin Issues

### Problem: Service plugin doesn't start

**Check logs:**

Windows:

```powershell
# View logs
Get-ChildItem "$env:LOCALAPPDATA\Icons8\Lunacy\Logs\"
Get-Content "$env:LOCALAPPDATA\Icons8\Lunacy\Logs\latest.log"
```

Example: `C:\Users\YourName\AppData\Local\Icons8\Lunacy\Logs\`

macOS:

```bash
# View logs
ls ~/Library/Logs/Icons8/Lunacy/
tail -f ~/Library/Logs/Icons8/Lunacy/latest.log
```

Linux:

```bash
# View logs
ls ~/.local/share/Icons8/Lunacy/Logs/
tail -f ~/.local/share/Icons8/Lunacy/Logs/latest.log
```

**Common causes:**

1. **Missing lifecycle field**

```jsonc
// WRONG
{
  "id": "my-service",
  "commands": [...]  // ❌ Service plugin needs serviceCommand
}

// CORRECT
{
  "id": "my-service",
  "lifecycle": "Service",
  "serviceCommand": {
    "id": "run-service",
    "name": "Run Service",
    "executable": "node",
    "args": ["service.js"]
  }
}
```

2. **Script doesn't stay running**

```javascript
// WRONG - Exits immediately
console.log('Service started');
// Script ends here

// CORRECT - Keep alive
const ws = new WebSocket('ws://localhost:31416');

ws.on('message', (data) => {
  // Handle events
});

// Keep process running
process.on('SIGTERM', () => {
  ws.close();
  process.exit(0);
});
```

### Problem: Service plugin crashes

**Add crash recovery:**

```javascript
// Restart WebSocket on disconnect
function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:31416');
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
  
  ws.on('close', () => {
    console.log('WebSocket closed, reconnecting in 5s...');
    setTimeout(connectWebSocket, 5000);
  });
  
  ws.on('message', (data) => {
    handleEvent(JSON.parse(data));
  });
  
  return ws;
}

let ws = connectWebSocket();
```

### Problem: Service plugin not stopping

**Implement graceful shutdown:**

```javascript
let isShuttingDown = false;

process.on('SIGTERM', async () => {
  if (isShuttingDown) return;
  isShuttingDown = true;
  
  console.log('Shutting down...');
  
  // Close connections
  if (ws) ws.close();
  
  // Save state
  await saveState();
  
  // Exit
  process.exit(0);
});

process.on('SIGINT', () => process.emit('SIGTERM'));
```

---

## Dynamic UI Issues

### Problem: UI dialog doesn't appear

**Cause 1: WebSocket not connected**

Service plugins must connect to WebSocket before registering UI:

```javascript
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:31416');

ws.on('open', async () => {
  console.log('Connected to Lunacy');
  await registerUi();
});
```

**Cause 2: Invalid field definition**

Check field types are correct:

```javascript
// CORRECT
{
  id: 'format',
  type: 'select',
  label: 'Format',
  options: ['PNG', 'JPEG']
}

// WRONG - type must be lowercase
{
  type: 'Select'
}

// WRONG - missing required properties
{
  id: 'format',
  type: 'select'
}
```

**Cause 3: pluginId mismatch**

```javascript
await axios.post(`${API}/registerui`, {
  pluginId: 'my-plugin',
  // ...
});

// Must match exactly
const values = await axios.post(`${API}/getpluginuivalues`, "my-plugin");
```

### Problem: Can't get UI values

**Cause 1: Getting values too early**

```javascript
// WRONG - Gets values immediately
await axios.post(`${API}/registerui`, { ... });
const values = await axios.post(`${API}/getpluginuivalues`, "xxx");
```

**Solution:** Wait for `close_ui` event:

```javascript
ws.on('message', async (data) => {
  const event = JSON.parse(data);
  
  if (event.event === 'close_ui' && event.pluginId === 'my-plugin') {
    const values = await axios.post(`${API}/getpluginuivalues`, "my-plugin");
    console.log('User values:', values.data);
  }
});
```

**Cause 2: Wrong pluginId**

```javascript
// WRONG
await axios.post(`${API}/registerui`, { pluginId: 'my-plugin', ... });
const values = await axios.post(`${API}/getpluginuivalues`, "myPlugin");

// CORRECT - Use constant
const PLUGIN_ID = 'my-plugin';
await axios.post(`${API}/registerui`, { pluginId: PLUGIN_ID, ... });
const values = await axios.post(`${API}/getpluginuivalues`, PLUGIN_ID);
```

### Problem: Values are all strings

**Expected behavior:** All field values returned as strings.

```javascript
const values = await axios.post(`${API}/getpluginuivalues`, "xxx");

// WRONG - Direct use
const quality = values.data.quality;  // "80" (string)

// CORRECT - Parse values
const quality = parseInt(values.data.quality);  // 80 (number)
const scale = parseFloat(values.data.scale);  // 2.5 (number)
const enabled = values.data.enabled === 'true';  // true (boolean)
```

### Problem: UI doesn't close

**Cause:** Forgot to unregister UI

```javascript
// WRONG
async function handleCloseUi() {
  const values = await axios.post(`${API}/getpluginuivalues`, "xxx");
  await processValues(values.data);
  // Dialog stays open
}

// CORRECT
async function handleCloseUi() {
  const values = await axios.post(`${API}/getpluginuivalues`, "xxx");
  await processValues(values.data);
  await axios.post(`${API}/unregisterui`, { pluginId: 'xxx' });
}
```

### Problem: UI events not received

**Cause:** Not listening to WebSocket events

```javascript
// WRONG - Polling or timeout
await axios.post(`${API}/registerui`, { ... });
setTimeout(async () => {
  const values = await axios.post(`${API}/getpluginuivalues`, "xxx");
}, 5000);

// CORRECT - Event-driven
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

await axios.post(`${API}/registerui`, { pluginId: 'my-plugin', ... });
```

### Problem: updateuifields doesn't work

**Cause 1: UI not registered yet**

```javascript
// WRONG - Update before register
await axios.post(`${API}/updateuifields`, { ... });
await axios.post(`${API}/registerui`, { ... });

// CORRECT - Register first
await axios.post(`${API}/registerui`, { ... });
await axios.post(`${API}/updateuifields`, { ... });
```

**Cause 2: Field ID mismatch**

```javascript
// Registered field
{
  id: 'exportFormat',
  type: 'select',
  // ...
}

// WRONG - Different ID
await axios.post(`${API}/updateuifields`, {
  pluginId: 'my-plugin',
  updates: {
    format: 'JPEG'  // Field 'format' doesn't exist
  }
});

// CORRECT - Match field ID
await axios.post(`${API}/updateuifields`, {
  pluginId: 'my-plugin',
  updates: {
    exportFormat: 'JPEG'
  }
});
```

### Problem: Toast notifications don't appear

**Cause:** Wrong iconType or missing message

```javascript
// WRONG - Invalid iconType
await axios.post(`${API}/showtoast`, {
  text: 'Done',
  iconType: 100
});

// CORRECT - Valid iconType (0-13)
await axios.post(`${API}/showtoast`, {
  text: 'Export complete',
  iconType: 1
});
```

**Icon types (0-13):**

- 0: None
- 1: Copy (Success)
- 2: CheckDone
- 3: Document
- 4: Warning/Error
- 5: Update (Loading)
- 6: Love
- 7: Human
- 8: Trash
- 9: Smile
- 10: CloudDisconnect
- 11: Message
- 12: Copyright
- 13: Stars

---

## Debugging Tools

### Console Logging

**Structured logging:**

```javascript
function log(level, message, data = {}) {
  const timestamp = new Date().toISOString();
  console.log(JSON.stringify({
    timestamp,
    level,
    message,
    ...data
  }));
}

log('info', 'Plugin started', { version: '1.0.0' });
log('error', 'Operation failed', { error: error.message, layerId });
```

### API Request Logging

**Log all API calls:**

```javascript
async function apiRequest(endpoint, method = 'GET', data = null) {
  const startTime = Date.now();
  
  try {
    const config = { method, url: `${API}${endpoint}` };
    if (data) config.data = data;
    
    const response = await axios(config);
    const duration = Date.now() - startTime;
    
    console.log('API:', {
      endpoint,
      method,
      status: response.status,
      duration: `${duration}ms`
    });
    
    return response;
  } catch (error) {
    const duration = Date.now() - startTime;
    
    console.error('API Error:', {
      endpoint,
      method,
      error: error.message,
      duration: `${duration}ms`
    });
    
    throw error;
  }
}
```

### File Logging

**Log to file for debugging:**

```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

// Cross-platform temp directory
const logFile = path.join(os.tmpdir(), 'plugin-debug.log');

function logToFile(message) {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] ${message}\n`;
  
  fs.appendFileSync(logFile, logLine);
  console.log(message);
}

logToFile('Plugin started');
console.log('Log file location:', logFile);
```

### Network Inspection

**Capture HTTP traffic:**

Windows:

- Use Wireshark with filter: `tcp.port == 31415`
- Or use browser DevTools for HTTP requests

macOS:

```bash
# Using tcpdump
sudo tcpdump -i lo0 -A 'tcp port 31415'
```

Linux:

```bash
# Using tcpdump
sudo tcpdump -i lo -A 'tcp port 31415'
```

All platforms:

- Wireshark: Filter `tcp.port == 31415`
- Postman: Test API endpoints manually

---

## Logging and Diagnostics

### Enable Verbose Logging

**Node.js:**

Windows (PowerShell):

```powershell
$env:DEBUG="*"; node plugin.js
```

macOS/Linux:

```bash
DEBUG=* node plugin.js
```

All platforms (via plugin.jsonc):

```jsonc
{
  "commands": [{
    "executable": "node",
    "args": ["plugin.js"],
    "env": {
      "DEBUG": "*",
      "NODE_ENV": "development"
    }
  }]
}
```

**Python:**

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('plugin-debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.debug('Plugin started')
```

### Diagnostic Information

**Collect system info:**

```javascript
function getSystemInfo() {
  return {
    platform: process.platform,
    nodeVersion: process.version,
    cwd: process.cwd(),
    env: {
      PATH: process.env.PATH,
      NODE_ENV: process.env.NODE_ENV
    },
    memory: process.memoryUsage(),
    uptime: process.uptime()
  };
}

console.log('System Info:', JSON.stringify(getSystemInfo(), null, 2));
```

### Health Check Endpoint

**For service plugins:**

```javascript
const http = require('http');

const healthServer = http.createServer((req, res) => {
  const health = {
    status: 'ok',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    websocket: ws && ws.readyState === 1 ? 'connected' : 'disconnected'
  };
  
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(health));
});

healthServer.listen(9999, 'localhost');
console.log('Health check: http://localhost:9999');
```

---

## FAQ

### Q: Why doesn't my plugin appear after I created it?

**A:** Most common causes:

1. Invalid JSON syntax in `plugin.jsonc`
2. Plugin not in correct directory
3. Lunacy not restarted after adding plugin
4. Missing required fields (id, name, version, commands)

**Solution:** Run through [Quick Diagnostic Checklist](#quick-diagnostic-checklist)

### Q: Plugin runs but selection is always empty

**A:** This happens when:

1. Nothing is actually selected in Lunacy
2. You're checking wrong field (use `_t` field, not `id`)

**Solution:**

```javascript
const layers = Array.isArray(data) ? data : [data];
if (layers.length === 0 || !layers[0]._t) {
  // Empty selection
}
```

### Q: Export files are corrupted or empty

**A:** Export data is byte array, not base64 string.

**Solution:**

```javascript
// Node.js
const buffer = Buffer.from(result.data);
fs.writeFileSync(filename, buffer);

// Python
file_data = bytes(result["data"])
```

### Q: Service plugin stops working after a while

**A:** Common causes:

1. WebSocket connection lost
2. Memory leak causing crash
3. Unhandled errors

**Solution:**

- Implement WebSocket reconnection
- Add error handlers for all async operations
- Monitor memory usage
- Implement graceful shutdown

### Q: Plugin works on Windows but not Linux

**A:** Common causes:

1. Path separators (use `path.join()`)
2. File permissions (Linux/macOS require executable bit, Windows doesn't)
3. Line endings (Windows: CRLF, Linux/macOS: LF)
4. Case-sensitive file systems (Linux only)
5. Python executable name (`python` on Windows, `python3` on Linux/macOS)

**Solution:**

```javascript
// Use path.join for cross-platform paths
const path = require('path');
const filePath = path.join(__dirname, 'data', 'file.json');

// Cross-platform Python execution
const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
```

Fix line endings:

```bash
# Convert to Unix line endings (LF)
dos2unix script.sh  # Linux/macOS

# Or use git
git config --global core.autocrlf input  # Linux/macOS
git config --global core.autocrlf true   # Windows
```

Fix permissions (Linux/macOS only):

```bash
chmod +x script.sh
```

### Q: How do I debug intermittent issues?

**A:** Add comprehensive logging:

```javascript
// Log everything
console.log('Starting operation');
console.log('Selection:', layers.length, 'layers');

try {
  const result = await operation();
  console.log('Success:', result);
} catch (error) {
  console.error('Error:', error.message);
  console.error('Stack:', error.stack);
  console.error('Context:', { layers, config });
}
```

### Q: Plugin times out but runs fine when tested directly

**A:** Increase timeout in `plugin.jsonc`:

```jsonc
{
  "timeoutMs": 60000  // 60 seconds instead of default 5000
}
```

### Q: Can I debug plugin while it runs from Lunacy?

**A:** Yes, use file logging:

```javascript
const fs = require('fs');
const path = require('path');
const os = require('os');

// Cross-platform log file location
const logPath = path.join(os.tmpdir(), 'plugin-debug.log');

function debug(message) {
  fs.appendFileSync(logPath, 
    `${new Date().toISOString()} ${message}\n`
  );
}

debug('Plugin started from Lunacy');
console.log('Debug log:', logPath);
```

Monitor the log:

Windows (PowerShell):

```powershell
Get-Content "$env:TEMP\plugin-debug.log" -Wait
```

macOS/Linux:

```bash
tail -f /tmp/plugin-debug.log
```

### Q: UI dialog appears but values are empty

**A:** You're calling `/getpluginuivalues` before user closes dialog.

Wait for `close_ui` WebSocket event:

```javascript
ws.on('message', async (data) => {
  const event = JSON.parse(data);
  
  if (event.event === 'close_ui' && event.pluginId === 'my-plugin') {
    const values = await axios.post(`${API}/getpluginuivalues`, "my-plugin");
    // Now values.data contains user input
  }
});
```

### Q: How do I update UI fields dynamically?

**A:** Use `/updateuifields` endpoint:

```javascript
ws.on('message', async (data) => {
  const event = JSON.parse(data);
  
  if (event.event === 'show_ui' && event.pluginId === 'my-plugin') {
    await axios.post(`${API}/updateuifields`, {
      pluginId: 'my-plugin',
      updates: {
        format: 'JPEG',
        quality: '95'
      }
    });
  }
});
```

### Q: Why doesn't my plugin receive show_ui or close_ui events?

**A:** You need to:

1. Connect to WebSocket: `ws://localhost:31416`
2. Listen to `message` event
3. Parse JSON and check `event.event` field
4. Check `event.pluginId` matches your plugin

```javascript
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:31416');

ws.on('message', (data) => {
  const event = JSON.parse(data);
  console.log('Received event:', event.event, 'pluginId:', event.pluginId);
});
```

### Q: All UI field values are strings, how do I get numbers/booleans?

**A:** Parse them:

```javascript
const values = response.data;

const quality = parseInt(values.quality);
const scale = parseFloat(values.scale);
const enabled = values.enabled === 'true';
```

---

## Getting Help

If you're still stuck after trying these solutions:

1. **Check logs:**
   - Plugin output (stdout/stderr)
   - Lunacy logs
   - System logs

2. **Create minimal reproduction:**
   - Simplify plugin to smallest failing case
   - Share plugin.jsonc and script

3. **Gather information:**
   - Lunacy version
   - Plugin configuration
   - Error messages
   - Steps to reproduce

4. **Ask for help:**
   - GitHub Issues: [icons8/lunacy-plugins](https://github.com/icons8/lunacy-plugins)
   - Discord: Plugin development channel
   - Include all diagnostic information

## Additional Resources

- [Plugin Development Guide](./PLUGIN_DEVELOPMENT_GUIDE.md)
- [API Reference](./API_REFERENCE.md)
- [Best Practices](./BEST_PRACTICES.md)
- [Examples](../examples/)
