# Hello World Plugin (C#)

Your first Lunacy plugin in C#!

## Installation

1. Test directly:
```bash
dotnet run
```

2. Build release version (optional):
```bash
dotnet build -c Release
```

3. Copy to Lunacy plugins directory:

**Linux:**
```bash
cp -r . ~/.local/share/Icons8/Lunacy/Plugins/hello-world-csharp
```

**Windows:**
```bash
xcopy /E /I . %APPDATA%\Icons8\Lunacy\Plugins\hello-world-csharp
```

**macOS:**
```bash
cp -r . ~/Library/Application\ Support/Icons8/Lunacy/Plugins/hello-world-csharp
```

4. Restart Lunacy

## Usage

1. Open Lunacy
2. Go to **Plugins** menu
3. Click **Hello World (C#)** → **Say Hello**
4. You should see a toast notification!

## Development vs Production

### Development Mode (Fast Iteration)
The default `plugin.jsonc` uses `dotnet run` for quick development:
- No build step needed
- Changes take effect immediately
- Slower startup time

### Production Mode (Faster Startup)
After development, you can use compiled binary:

1. Build release:
```bash
dotnet build -c Release
```

2. Update `plugin.jsonc`:
```jsonc
{
  "commands": [
    {
      "id": "say-hello",
      "name": "Say Hello",
      "executable": "./bin/Release/net9.0/HelloWorld",
      "timeoutMs": 5000
    }
  ]
}
```

## What it does

This simple plugin shows a toast notification with a "Hello World" message.

## Next Steps

Check out the [Quick Start Guide](../../docs/QUICK_START.md) for more features like:
- Working with selected layers
- Modifying layer properties
- Exporting layers
