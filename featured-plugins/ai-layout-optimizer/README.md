# AI Layout Optimizer

AI-powered Auto Layout configuration plugin for Lunacy. Analyzes your design visually and configures Auto Layout with intelligent grouping, spacing, and alignment.

## What It Does

This plugin uses AI vision to:

1. **Analyze your design** - Takes a screenshot and examines layer relationships
2. **Identify patterns** - Recognizes form fields, buttons, cards, and UI components
3. **Create semantic groups** - Groups overlapping elements (e.g., button background + text)
4. **Configure Auto Layout** - Sets up responsive layout with proper spacing and alignment
5. **Rename layers** - Gives descriptive names to all elements

## Features

- **Vision-based analysis** - AI sees your design like a human designer
- **Smart grouping** - Distinguishes between stacked and overlapping elements
- **Auto Layout configuration** - Sets orientation, spacing, padding, alignment automatically
- **Layer properties** - Configures `layoutStretch` and `layoutFixPos` for responsive behavior
- **Semantic naming** - Renames layers for better organization
- **Multi-provider** - Works with Anthropic or OpenAI models

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### API Keys

Choose either Anthropic or OpenAI as your AI provider:

#### Anthropic

```jsonc
{
  "env": {
    "LLM_PROVIDER": "anthropic",
    "ANTHROPIC_API_KEY": "sk-ant-your-key-here",
    "ANTHROPIC_MODEL": "claude-haiku-4-5-20251001"
  }
}
```

- `ANTHROPIC_MODEL` - Any Claude model with vision support

#### OpenAI

```jsonc
{
  "env": {
    "LLM_PROVIDER": "openai",
    "OPENAI_API_KEY": "sk-your-key-here",
    "OPENAI_MODEL": "gpt-4o-mini",
    "OPENAI_MODEL_VISION": "gpt-4o"
  }
}
```

- `OPENAI_MODEL` - Model for text analysis (optional, used for fallback)
- `OPENAI_MODEL_VISION` - Model with vision capabilities (required for screenshot analysis)

### Debug Mode

Enable detailed logging:

```jsonc
{
  "env": {
    "DEBUG": "1"
  }
}
```

Shows LLM prompts, responses, and operation details in console.

## Usage

1. **Select a FRAME** containing layers you want to organize
2. Run **Plugins → AI Layout Optimizer → Configure Auto Layout**
3. Wait for analysis (~5-10 seconds)
4. Auto Layout configured automatically

**Requirements:**

- Must select a FRAME (not GROUP or SECTION)
- FRAME should contain child layers to organize

## How It Works

### Step 1: Extract Layers

Plugin reads all child layers from the selected FRAME, including their positions, sizes, types, and text content.

### Step 2: Capture Screenshot

Takes a visual snapshot of the layers for AI analysis.

### Step 3: AI Analysis

LLM examines the screenshot and layer data to determine:

- **Stacked vs Overlapping** - Identifies which elements flow vs overlap
  - Stacked: Form fields (label above input) → Create FRAME with Auto Layout
  - Overlapping: Buttons (text on background) → Create GROUP
- **Orientation** - Vertical or horizontal layout
- **Spacing** - Gaps between elements
- **Padding** - Container margins
- **Alignment** - How elements align on main/cross axis
- **Sizing** - Which elements stretch vs stay fixed
- **Grouping** - Which layers belong together semantically

### Step 4: Apply Configuration

Plugin rebuilds the FRAME structure:

1. Creates semantic groups (FRAMEs with Auto Layout or simple GROUPs)
2. Sets Auto Layout on parent FRAME
3. Configures child properties (`layoutStretch`, `layoutFixPos`)
4. Renames layers with descriptive names
5. Orders elements properly

### Step 5: Result

You get a fully configured Auto Layout that:

- Adapts when content changes
- Maintains proper spacing
- Aligns elements consistently
- Groups related components logically

## Example

**Before:**

- FRAME with 8 unorganized layers
- Email label at Y=118
- Email input at Y=143
- Password label at Y=198
- Password input at Y=223
- Button background at Y=327
- Button text at Y=341
- Etc.

**After:**

```text
FRAME (Auto Layout: vertical, spacing: 16px, padding: 20px)
├─ Email Field (FRAME with Auto Layout: vertical, spacing: 8px)
│  ├─ Email Label (layoutStretch: false)
│  └─ Email Input (layoutStretch: true)
├─ Password Field (FRAME with Auto Layout: vertical, spacing: 8px)
│  ├─ Password Label (layoutStretch: false)
│  └─ Password Input (layoutStretch: true)
├─ Login Button (GROUP)
│  ├─ Button Background
│  └─ Button Text
└─ Footer Links (layoutStretch: false)
```

Auto Layout configuration:

- **Orientation:** Vertical (stacks elements top to bottom)
- **Spacing:** 16px between groups
- **Padding:** 20px all sides
- **Primary Alignment:** Top (elements start from top)
- **Counter Alignment:** Center (elements centered horizontally)
- **Horizontal Sizing:** Fixed (keeps original FRAME width)
- **Vertical Sizing:** Hug (adjusts height to fit content)

## Auto Layout Reference

### Container Properties (Parent FRAME)

These configure the main Auto Layout behavior:

| Property | Values | Description |
|----------|--------|-------------|
| `orientation` | 0=horizontal, 1=vertical | Main axis direction |
| `itemsSpacing` | pixels | Gap between child elements |
| `paddingTop/Right/Bottom/Left` | pixels | Container padding |
| `primaryAlignment` | 0=start, 1=center, 2=end, 3=distribute | Alignment along main axis |
| `counterAlignment` | 0=start, 1=center, 2=end | Alignment along cross axis |
| `horizontalSizing` | 0=hug, 1=fixed | Width behavior |
| `verticalSizing` | 0=hug, 1=fixed | Height behavior |

**Alignment mapping:**

- Vertical layout: `primaryAlignment` → vertical position, `counterAlignment` → horizontal position
- Horizontal layout: `primaryAlignment` → horizontal position, `counterAlignment` → vertical position

### Child Layer Properties

These control individual layer behavior:

| Property | Type | Description |
|----------|------|-------------|
| `layoutStretch` | boolean | `true` = fill available space, `false` = fixed size |
| `layoutFixPos` | boolean | `true` = absolute positioning (ignores flow), `false` = flow with layout |
| `layoutFixPosX/Y` | pixels | Absolute position (only if `layoutFixPos=true`) |

**Common patterns:**

- Text inputs: `layoutStretch: true` (fill width)
- Labels: `layoutStretch: false` (fixed size)
- Buttons: `layoutStretch: true` or `false` depending on design
- Icons/decorations: `layoutFixPos: true` (absolute positioning)

## Troubleshooting

**"Please select layers to optimize"**

- You must select a FRAME that contains child layers
- Empty FRAMEs cannot be optimized

**"Auto Layout requires a parent FRAME container ID"**

- This plugin only works on FRAME objects
- Convert GROUP or SECTION to FRAME first

**"Parent container is GROUP, not FRAME"**

- Auto Layout is only supported on FRAME objects in Lunacy
- Right-click container → Convert to Frame

**"API key not configured"**

- Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `plugin.jsonc`
- Ensure `LLM_PROVIDER` matches your chosen provider
- Remove placeholder text like "your-anthropic-key-here"

**"LLM ERROR" or fallback layout used**

- Check API key validity and account credits
- Verify internet connection
- Try different model or switch AI provider
- Enable `DEBUG=1` to see detailed error messages

**Plugin timeout**

- Default timeout is 60 seconds
- Increase `timeoutMs` in `plugin.jsonc` if needed
- Complex layouts with many layers may take longer

**Unexpected layout results**

- Enable `DEBUG=1` to see AI reasoning
- Check screenshot quality (visible in debug output)
- Verify layer names and structure are clear
- AI performs better with well-organized initial state

## Requirements

- Python 3.8+
- Anthropic API key OR OpenAI API key
- Lunacy with Plugins support
- Internet connection for AI analysis

## Tips for Best Results

1. **Use clear layer names** - AI can better understand "Email Input" than "Rectangle 1"
2. **Organize before optimizing** - Rough positioning helps AI understand intent
3. **Group complex components first** - Pre-group buttons/cards if they have many parts
4. **Start with FRAMEs** - Always work with FRAME containers, not GROUPs
5. **Review AI decisions** - Enable DEBUG to see why AI made certain choices

## Privacy & Data

- Screenshots and layer data are sent to LLM provider (Anthropic or OpenAI)
- No data is stored by the plugin
- No telemetry or analytics
- All processing happens via API calls
- Review your LLM provider's privacy policy for details
