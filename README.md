# Lunacy Plugins

> Official plugin repository for Lunacy - the fast and powerful graphic design software

Build powerful extensions for Lunacy using any programming language. Automate workflows, add AI features,
integrate external tools, and customize your design experience.

## What are Lunacy Plugins?

Lunacy plugins are external programs that interact with Lunacy via HTTP Automation API. They can:

- Modify layers and properties
- Add AI-powered design automation
- Export to custom formats
- Sync with external services
- Build custom tools and utilities
- Monitor design events in real-time

Matching preview builds also expose document/page lifecycle, components and instances,
shared styles, variables and themes, and authorized library discovery/import through
Automation API v2. Check `/v2/get_session` for availability; these additions are not
a claim that every currently installed release supports them.

## Quick Start

### 1. Find the plugin folder

Open Lunacy and choose **Help → Open App Data Folder**, then open/create its `Plugins`
folder. This is the reliable location for your installed package.

### 2. Install a Plugin

Download a plugin from this repository and place its directory, including
`plugin.jsonc` (or `plugin.json`), inside `Plugins`. Common locations include:

- **Linux:** `~/.local/share/Icons8/Lunacy/Plugins/`
- **Windows:** `%LOCALAPPDATA%\Icons8\Lunacy\Plugins\`
- **macOS:** `~/Library/Application Support/Icons8/Lunacy/Plugins/`

Locations can vary with packaging. A valid installed plugin starts the local API
automatically. For standalone development, enable **AI → Model Context Protocol →
MCP server enabled** without installing a plugin.

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
- **[Development Guide](./docs/PLUGIN_DEVELOPMENT_GUIDE.md)** - Manifests, processes and plugin lifecycle
- **[Automation API v2 Reference](./docs/API_V2_REFERENCE.md)** - All 26 new HTTP methods, actions, types and limits
- **[Automation Workflows](./docs/AUTOMATION_WORKFLOWS.md)** - Discovery, guarded batches, readback and recovery
- **[v2 Request Schemas](./docs/schemas/README.md)** - Complete machine-readable HTTP request contracts
- **[Legacy API Reference](./docs/API_REFERENCE.md)** - Layers, images, export, events and UI
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

→ [View Plugin](./featured-plugins/bitmap-to-vector-plugin/)

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
- Reading selection and editing selected layers
- Multi-format export (PNG, SVG, PDF, JPG, WEBP, TIFF, ICO)
- Screenshots and viewport access
- Undo/redo support
- Toast notifications
- Interactive UI system
- Real-time WebSocket events
- Document/tab/page lifecycle and explicit document targeting (v2 preview)
- Component definitions, properties, states and instances (v2 preview)
- Shared color/text/effect/guide styles and variable bindings (v2 preview)
- Collections, themes, aliases and layer theme evaluation (v2 preview)
- Authorized library discovery, import and refresh (v2 preview)

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
        iconType: 2  // CheckDone
    })
});
```

## Installation Paths

### Linux

```bash
~/.local/share/Icons8/Lunacy/Plugins/your-plugin-name/
```

### Windows

```cmd
%LOCALAPPDATA%\Icons8\Lunacy\Plugins\your-plugin-name\
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

## Powered by Icons8

Lunacy is made by **[Icons8](https://icons8.com?utm_source=github)** and ships with its full asset library. Build plugins that search, place, and automate Icons8 assets on the canvas:

- **[1.5M+ icons](https://icons8.com/icons?utm_source=github)** - try [Glyph Neue](https://icons8.com/icons/glyph-neue?utm_source=github), [iOS 27](https://icons8.com/icons/ios?utm_source=github), [Liquid Glass](https://icons8.com/icons/liquid-glass?utm_source=github)
- **[110,000+ illustrations](https://icons8.com/illustrations?utm_source=github)** - try [3D Stickle](https://icons8.com/illustrations/styles/3d-stickle?utm_source=github), [Cherry](https://icons8.com/illustrations/styles/cherry?utm_source=github), [3D Casual Life](https://icons8.com/illustrations/styles/3d-casual-life?utm_source=github)

[Get Lunacy](https://icons8.com/lunacy?utm_source=github), free.

## License

This repository is licensed under MIT License. See [LICENSE](./LICENSE) for details.

Individual plugins may have different licenses - check each plugin's LICENSE file.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

Made by the Lunacy Team

