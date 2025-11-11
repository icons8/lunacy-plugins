# Hello World Plugin (Node.js)

Your first Lunacy plugin in Node.js!

## Installation

1. Install dependencies:

```bash
npm install
```

2. Test directly:

```bash
node hello.js
```

3. Copy to Lunacy plugins directory:

**Linux:**

```bash
cp -r . ~/.local/share/Icons8/Lunacy/Plugins/hello-world-node
```

**Windows:**

```bash
xcopy /E /I . %APPDATA%\Icons8\Lunacy\Plugins\hello-world-node
```

**macOS:**

```bash
cp -r . ~/Library/Application\ Support/Icons8/Lunacy/Plugins/hello-world-node
```

4. Restart Lunacy

## Usage

1. Open Lunacy
2. Go to **Plugins** menu
3. Click **Hello World (Node.js)** → **Say Hello**
4. You should see a toast notification!

## What it does

This simple plugin shows a toast notification with a "Hello World" message.

## Next Steps

Check out the [Quick Start Guide](../../docs/QUICK_START.md) for more features like:

- Working with selected layers
- Modifying layer properties
- Exporting layers
