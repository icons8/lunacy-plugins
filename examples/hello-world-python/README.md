# Hello World Plugin (Python)

Your first Lunacy plugin in Python!

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Test directly:

```bash
python3 hello.py
```

3. Copy to Lunacy plugins directory:

**Linux:**

```bash
cp -r . ~/.local/share/Icons8/Lunacy/Plugins/hello-world-python
```

**Windows:**

```bash
xcopy /E /I . %LOCALAPPDATA%\Icons8\Lunacy\Plugins\hello-world-python
```

**macOS:**

```bash
cp -r . ~/Library/Application\ Support/Icons8/Lunacy/Plugins/hello-world-python
```

4. Restart Lunacy

## Usage

1. Open Lunacy
2. Go to **Plugins** menu
3. Click **Hello World (Python)** → **Say Hello**
4. You should see a toast notification!

## What it does

This simple plugin shows a toast notification with a "Hello World" message.

## Next Steps

Check out the [Quick Start Guide](../../docs/QUICK_START.md) for more features like:

- Working with selected layers
- Modifying layer properties
- Exporting layers
