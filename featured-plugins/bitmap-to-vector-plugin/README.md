# Bitmap to Vector Plugin

Service plugin that converts bitmap images to vector graphics using VTracer with interactive UI.

## Installation

Just run the plugin - vtracer will be downloaded automatically on first run (~2.5MB):

**Linux/macOS:**

```bash
python3 vectorize_ui.py
```

**Windows:**

```cmd
python vectorize_ui.py
```

That's it! Plugin will auto-download vtracer binary and start working.

## Usage

1. Open UI: `Plugins → Bitmap to Vector Converter → Show`
2. Select bitmap-filled layers in Lunacy
3. Configure settings (or use preset)
4. Click "Convert to Vector"

## Features

**Interactive UI with all VTracer parameters:**

- **Smart Presets**: Photo, Poster, BW, Custom
  - Selecting preset auto-updates all parameters
  - Changing parameters auto-detects matching preset or switches to Custom
- Color Mode: color/bw
- Curve Mode: spline/polygon/pixel
- Hierarchical: stacked/cutout
- Color Precision: 1-8 bits
- Filter Speckle: 0-50 px
- Corner Threshold: 0-180°
- Gradient Step: 1-255
- Path Precision: 0-10 decimals
- Segment Length: 1-100
- Splice Threshold: 0-180°

**Background Service:**

- Auto-starts with Lunacy
- Always available in menu
- Real-time WebSocket communication
