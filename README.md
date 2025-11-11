# Lunacy Plugins

> Official plugin repository for Lunacy - the fast and powerful graphic design software

Build powerful extensions for Lunacy using any programming language. Automate workflows, add AI features, integrate external tools, and customize your design experience.

## What are Lunacy Plugins?

Lunacy plugins are external programs that interact with Lunacy via HTTP Automation API. They can:

- Modify layers and properties
- Add AI-powered design automation
- Export to custom formats
- Sync with external services
- Build custom tools and utilities
- Monitor design events in real-time

## Quick Start

### 1. Enable the API

1. Open Lunacy
2. Go to **AI → Model Context Protocol → MCP server enabled**
3. Enable the checkbox

### 2. Install a Plugin

Download any plugin from this repository and place it in:

- **Linux:** `~/.local/share/Icons8/Lunacy/Plugins/`
- **Windows:** `%APPDATA%\Icons8\Lunacy\Plugins\`
- **macOS:** `~/Library/Application Support/Icons8/Lunacy/Plugins/`

### 3. Run Your First Plugin

Try the [Hello World](./examples/hello-world-python/) example:

```bash
cd ~/.local/share/Icons8/Lunacy/Plugins/hello-world-python
python3 hello.py
```

See the [Quick Start Guide](./docs/QUICK_START.md) for detailed instructions.

## Documentation

- **[Quick Start Guide](./docs/QUICK_START.md)** - Your first plugin in 5 minutes
- **[Quick Start UI Guide](./docs/QUICK_START_UI.md)** - Complete UI plugin tutorial
- **[Development Guide](./docs/PLUGIN_DEVELOPMENT_GUIDE.md)** - Complete API reference
- **[API Reference](./docs/API_REFERENCE.md)** - All endpoints and data types
- **[Plugin UI Guide](./docs/PLUGIN_UI_GUIDE.md)** - Building interactive interfaces
- **[Best Practices](./docs/BEST_PRACTICES.md)** - Patterns and recommendations
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Common issues and solutions

## Featured Plugins

### AI Layout Optimizer

AI-powered Auto Layout configuration. Analyzes your design visually and sets up responsive layouts automatically.

**Features:**
- Vision-based design analysis
- Smart grouping and spacing
- Semantic layer naming
- Works with Anthropic or OpenAI

→ [View Plugin](./featured-plugins/ai-layout-optimizer/)

### Bitmap to Vector Converter

Convert raster images to scalable vector graphics with interactive UI and smart presets.

**Features:**
- Interactive parameter tuning
- Photo, Poster, B&W presets
- Background service mode
- Auto-downloads VTracer tool

→ [View Plugin](./featured-plugins/bitmap-to-vector/)

## Examples

Start with basic examples to learn plugin development:

- [Hello World (Node.js)](./examples/hello-world-node/) - Simple JavaScript plugin
- [Hello World (Python)](./examples/hello-world-python/) - Simple Python plugin
- [Hello World (C#)](./examples/hello-world-csharp/) - Simple C# plugin with dev/prod workflows

For production-ready examples, see [Featured Plugins](#featured-plugins).

## Plugin Features

### Two Lifecycle Modes

- **Utility Mode** - Run on-demand when user triggers commands
- **Service Mode** - Continuous background operation from Lunacy startup

### Language Support

Write plugins in any language:

- **Node.js** - Fast prototyping, rich ecosystem
- **Python** - AI/ML libraries, data processing
- **C#/.NET** - High performance, native feel
- **Go** - Concurrency, system tools
- **PowerShell** - Windows automation

### API Capabilities

- Layer operations (create, update, delete, duplicate)
- Selection management
- Multi-format export (PNG, SVG, PDF, JPG, WEBP, TIFF, ICO)
- Screenshots and viewport access
- Undo/redo support
- Toast notifications
- Interactive UI system
- Real-time WebSocket events

## Community Plugins

Looking for more? Check out [community-created plugins](./community/README.md).

Want to submit your plugin? See [CONTRIBUTING.md](./CONTRIBUTING.md).

## Use Cases

- **AI & Automation** - Auto-layout, content generation, smart naming
- **Export & Conversion** - Custom formats, batch processing
- **Integration** - Design systems, version control, CMS sync
- **Utilities** - Color tools, measurement, cleanup
- **Analytics** - Usage tracking, design metrics
- **Background Services** - Auto-save, real-time collaboration

## Technology

Lunacy plugins communicate via HTTP REST API on `localhost:31415`:

```javascript
// Get current selection
const response = await fetch('http://localhost:31415/getselected');
const selection = await response.json();

// Show notification
await fetch('http://localhost:31415/showtoast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        text: 'Plugin completed!',
        iconType: 1  // Success
    })
});
```

## Installation Paths

### Linux
```bash
~/.local/share/Icons8/Lunacy/Plugins/your-plugin-name/
```

### Windows
```
%APPDATA%\Icons8\Lunacy\Plugins\your-plugin-name\
```

### macOS
```bash
~/Library/Application Support/Icons8/Lunacy/Plugins/your-plugin-name/
```

## Links

- [Lunacy Website](https://icons8.com/lunacy)
- [Lunacy Documentation](https://lunacy.docs.icons8.com)
- [Plugin Documentation](./docs/)
- [Report Issues](https://github.com/icons8/lunacy-plugins/issues)

## License

This repository is licensed under MIT License. See [LICENSE](./LICENSE) for details.

Individual plugins may have different licenses - check each plugin's LICENSE file.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

Made by the Lunacy Team
