# Quick Start: Your First Lunacy Plugin in 5 Minutes

This guide will help you create and run your first Lunacy plugin in just a few minutes.

## Prerequisites

- Lunacy installed and running
- **One of:** Node.js 14+, Python 3.6+, or .NET SDK 8.0+
- Text editor (VS Code, Sublime, etc.)

## Step 0: Enable Automation API (Critical!)

**Before you start**, you must enable the Automation API in Lunacy:

1. Open Lunacy
2. Go to menu: **AI → Model Context Protocol**
3. Enable the **"MCP server enabled"** checkbox
4. The server will start automatically on `http://localhost:31415`

**Note:** The server will auto-enable when you add your first plugin, but it's recommended to enable it manually first.

**Test the API is running:**

Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri http://localhost:31415/getselected
```

macOS/Linux:
```bash
curl http://localhost:31415/getselected
```

If you get a response (even if empty), the API is working!

## Step 1: Create Plugin Directory

Choose your platform and create the plugins directory:

**Linux:**
```bash
mkdir -p ~/.local/share/Icons8/Lunacy/Plugins/hello-world
cd ~/.local/share/Icons8/Lunacy/Plugins/hello-world
```

**Windows:**
```bash
mkdir %APPDATA%\Icons8\Lunacy\Plugins\hello-world
cd %APPDATA%\Icons8\Lunacy\Plugins\hello-world
```

**macOS:**
```bash
mkdir -p ~/Library/Application\ Support/Icons8/Lunacy/Plugins/hello-world
cd ~/Library/Application\ Support/Icons8/Lunacy/Plugins/hello-world
```

## Step 2: Create Plugin Configuration

Create a file named `plugin.jsonc` - this is **the same for all languages**:

```jsonc
{
  "id": "hello-world",
  "name": "Hello World",
  "description": "My first Lunacy plugin",
  "version": "1.0.0",
  "commands": [
    {
      "id": "say-hello",
      "name": "Say Hello",
      "executable": "node",          // Change to "python3" or "dotnet" depending on your choice
      "args": ["hello.js"],           // Change to ["hello.py"] or ["run", "--project", "HelloWorld.csproj"]
      "timeoutMs": 5000
    }
  ]
}
```

## Step 3: Write Plugin Code

Choose **one** of the following languages:

### Option A: Node.js Plugin

**Update plugin.jsonc executable section:**
```jsonc
"executable": "node",
"args": ["hello.js"]
```

**Create `hello.js`:**
```javascript
#!/usr/bin/env node

const axios = require('axios');

const API = 'http://localhost:31415';

async function main() {
  try {
    await axios.post(`${API}/showtoast`, {
      text: 'Hello from your first Node.js plugin!',
      iconType: 2,
      priority: 5,
      durationSeconds: 5
    });
    
    console.log('Plugin executed successfully!');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
```

**Create `package.json`:**
```json
{
  "name": "hello-world-plugin",
  "version": "1.0.0",
  "dependencies": {
    "axios": "^1.6.0"
  }
}
```

**Install dependencies:**
```bash
npm install
```

---

### Option B: Python Plugin

**Update plugin.jsonc executable section:**
```jsonc
"executable": "python3",
"args": ["hello.py"]
```

**Create `hello.py`:**
```python
#!/usr/bin/env python3

import requests

API = "http://localhost:31415"

def main():
    try:
        response = requests.post(f"{API}/showtoast", json={
            "text": "Hello from your first Python plugin!",
            "iconType": 2,
            "priority": 5,
            "durationSeconds": 5
        })
        
        print("Plugin executed successfully!")
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
```

**Create `requirements.txt`:**
```txt
requests>=2.31.0
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

---

### Option C: C# Plugin

**Update plugin.jsonc executable section (for development):**
```jsonc
"executable": "dotnet",
"args": ["run", "--project", "HelloWorld.csproj"],
"timeoutMs": 10000
```

**Create `HelloWorld.csproj`:**
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="System.Net.Http.Json" Version="9.0.0" />
  </ItemGroup>
</Project>
```

**Create `Program.cs`:**
```csharp
using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace HelloWorld;

public static class Program
{
    private const string API = "http://localhost:31415";

    public static async Task Main(string[] args)
    {
        try
        {
            using var client = new HttpClient();
            
            var toastRequest = new ShowToastRequest
            {
                Text = "Hello from your first C# plugin!",
                IconType = 2,
                Priority = 5,
                DurationSeconds = 5
            };
            
            await client.PostAsJsonAsync($"{API}/showtoast", toastRequest, HelloWorldJsonContext.Default.ShowToastRequest);
            
            Console.WriteLine("Plugin executed successfully!");
        }
        catch (Exception error)
        {
            Console.WriteLine($"Error: {error.Message}");
        }
    }
}

public record ShowToastRequest
{
    [JsonPropertyName("text")]
    public string Text { get; init; } = "";
    
    [JsonPropertyName("iconType")]
    public int IconType { get; init; }
    
    [JsonPropertyName("priority")]
    public int Priority { get; init; }
    
    [JsonPropertyName("durationSeconds")]
    public int DurationSeconds { get; init; }
}

[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
[JsonSerializable(typeof(ShowToastRequest))]
internal sealed partial class HelloWorldJsonContext : JsonSerializerContext
{
}
```

**Production Build (Recommended for Speed):**

For faster startup, compile to native binary:
```bash
# Build release version
dotnet build -c Release

# Test compiled binary
./bin/Release/net9.0/HelloWorld
```

Update `plugin.jsonc` to use compiled binary:
```jsonc
{
  "id": "hello-world",
  "name": "Hello World",
  "description": "My first Lunacy plugin",
  "version": "1.0.0",
  "commands": [
    {
      "id": "say-hello",
      "name": "Say Hello",
      "executable": "./bin/Release/net9.0/HelloWorld",
      "args": [],
      "timeoutMs": 5000
    }
  ]
}
```

**Performance:** Compiled binary starts 20-30x faster (~50ms vs ~2-3s with `dotnet run`)

---

## Step 4: Test Your Plugin

### Test Directly (Recommended)

Before testing in Lunacy, verify the script works:

```bash
# For Node.js
node hello.js

# For Python
python3 hello.py

# For C#
dotnet run
```

Make sure Lunacy is running - you should see a toast notification!

### Test in Lunacy

1. **Restart Lunacy** to load the new plugin
2. Open any document in Lunacy
3. Go to **Plugins** menu
4. You should see **"Hello World"** in the menu
5. Click **"Hello World" → "Say Hello"**
6. You should see a toast notification

## Success!

You've just created your first Lunacy plugin! 

## What's Next?

Ready to create more advanced plugins with interactive UI?

Check out the **[UI Plugin Quick Start Guide](./QUICK_START_UI.md)** to learn how to:
- Create interactive UI dialogs with buttons, inputs, and dropdowns
- Listen to WebSocket events from Lunacy
- Build complex features like Smart Duplicate with preset transformations
- Handle user input and apply changes to layers

## Learn More

- [UI Plugin Quick Start](./QUICK_START_UI.md) - Interactive plugins with UI
- [Plugin Development Guide](./PLUGIN_DEVELOPMENT_GUIDE.md) - Complete guide with all features
- [API Reference](./API_REFERENCE.md) - Full API documentation
- [Examples](../examples/) - Working examples for inspiration

## Troubleshooting

### Plugin doesn't appear in menu
- Check `plugin.jsonc` syntax (use JSON validator)
- Verify file is in correct plugins directory
- Restart Lunacy completely

### "Connection refused" error
- Make sure Lunacy is running
- Check that Automation API server is enabled in Lunacy settings
- Test API: `curl http://localhost:31415/getselected`

### Script doesn't run
- Test script directly: `node hello.js`, `python3 hello.py`, or `dotnet run`
- Check console output for errors
- Verify dependencies are installed

### No toast appears
- Check Lunacy is in foreground
- Verify API endpoint is correct
- Try with longer `durationSeconds`

## Tips

1. Always test scripts directly first before loading in Lunacy
2. Use meaningful error messages to help debug issues
3. Add logging for debugging
4. Start simple and add features incrementally
5. Check examples when stuck

---

Congratulations! You're now a Lunacy plugin developer!
