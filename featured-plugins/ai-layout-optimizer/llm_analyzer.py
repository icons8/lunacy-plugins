"""
LLM integration for layout analysis
"""

import os
import json
from typing import List, Optional, Any

try:
    from openai import OpenAI
    from anthropic import Anthropic
except ImportError as e:
    print(f"Error: Missing LLM package - {e}")
    raise

from data_types import LayerContext, LayoutPlan
from helpers import TransformHelper

DEBUG = os.getenv('DEBUG', '0') == '1'

class LLMAnalyzer:
    """LLM integration for layout analysis (OpenAI or Anthropic)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        
        if self.provider == 'anthropic':
            self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key or self.api_key == 'PLACEHOLDER_INSERT_YOUR_KEY_HERE':
                raise ValueError("Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable.")
            
            if DEBUG:
                print(f"Initializing Anthropic client (key: {self.api_key[:20]}...{self.api_key[-4:]})")
            self.client: Any = Anthropic(api_key=self.api_key)
            self.model = os.getenv('ANTHROPIC_MODEL', 'claude-haiku-4-5-20251001')
        else:
            self.api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not self.api_key or self.api_key == 'PLACEHOLDER_INSERT_YOUR_KEY_HERE':
                raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
            
            if DEBUG:
                print(f"Initializing OpenAI client (key: {self.api_key[:20]}...{self.api_key[-4:]})")
            self.client: Any = OpenAI(api_key=self.api_key)
            self.model_with_vision = os.getenv('OPENAI_MODEL_VISION', 'gpt-4o')
            self.model_without_vision = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    def analyze_layout(
        self,
        contexts: List[LayerContext],
        screenshot: Optional[str] = None,
        container_size: Optional[List[float]] = None
    ) -> LayoutPlan:
        """Analyze layers and generate Auto Layout configuration"""
        
        return self._analyze_autolayout(contexts, screenshot, container_size)
    
    def _analyze_autolayout(
        self,
        contexts: List[LayerContext],
        screenshot: Optional[str] = None,
        container_size: Optional[List[float]] = None
    ) -> LayoutPlan:
        """Analyze layers and generate Auto Layout configuration"""
        
        system_prompt = (
            "You are helping a designer organize UI elements in Lunacy design tool.\n"
            "You look at a screenshot and layer data, then decide how to group and arrange elements.\n\n"
            "TWO TOOLS AVAILABLE:\n\n"
            "1. AUTO LAYOUT (FRAME with auto_layout) - Use when elements should ADAPT to each other:\n"
            "   - Form fields: Label stacked above input field → input should stretch to fill width\n"
            "   - Cards with multiple items stacked vertically with consistent spacing\n"
            "   - Toolbars with icons arranged horizontally\n"
            "   When elements need to resize/reflow based on content or container size\n\n"
            "2. SIMPLE GROUP (type='GROUP') - Use when elements are OVERLAPPING or FIXED relative to each other:\n"
            "   - Button: Rectangle shape with text centered on top → they overlap, don't flow\n"
            "   - Badge: Circle with number inside\n"
            "   - Icon with background\n"
            "   When elements have fixed visual relationship and don't need to adapt\n\n"
            "Return ONLY valid JSON with this EXACT structure (NO markdown, NO explanations, NO code blocks):\n"
            "{\n"
            '  "groups": [\n'
            '    {\n'
            '      "name": "Email Field",\n'
            '      "type": "FRAME",\n'
            '      "order": 118,\n'
            '      "layer_ids": ["label-id", "input-id"],\n'
            '      "auto_layout": {"orientation": 1, "itemsSpacing": 8, "paddingTop": 0, "paddingRight": 0, "paddingBottom": 0, "paddingLeft": 0, "primaryAlignment": 0, "counterAlignment": 0, "horizontalSizing": 1, "verticalSizing": 0},\n'
            '      "layer_properties": {"label-id": {"layoutStretch": false}, "input-id": {"layoutStretch": true}}\n'
            '    },\n'
            '    {\n'
            '      "name": "Login Button",\n'
            '      "type": "GROUP",\n'
            '      "order": 327,\n'
            '      "layer_ids": ["button-bg-id", "button-text-id"]\n'
            '    }\n'
            '  ],\n'
            '  "auto_layout": {"orientation": 1, "itemsSpacing": 16, "paddingTop": 20, "paddingRight": 20, "paddingBottom": 20, "paddingLeft": 20, "primaryAlignment": 0, "counterAlignment": 1, "horizontalSizing": 1, "verticalSizing": 0},\n'
            '  "layer_properties": {"corner-icon-id": {"layoutFixPos": true, "layoutFixPosX": 330, "layoutFixPosY": 20}, "title-id": {"layoutStretch": false}},\n'
            '  "rename_map": {"layer-id": "Better Name"}\n'
            "}\n\n"
            "DECISION GUIDE - Look at the screenshot:\n\n"
            "ASK: Are these elements STACKED (one after another) or OVERLAPPING (on top of each other)?\n\n"
            "STACKED → Use FRAME with Auto Layout:\n"
            "  Example: Email label is ABOVE input field (separate items in a list)\n"
            "  Config: orientation=1 (vertical), horizontalSizing=1 (fixed width), input has layoutStretch=true\n\n"
            "OVERLAPPING → Use GROUP:\n"
            "  Example: Login text is ON TOP OF blue rectangle (they overlap visually)\n"
            "  Config: type='GROUP', no auto_layout needed, children keep their positions\n\n"
            "RULES:\n"
            "1. Look at screenshot - identify STACKED vs OVERLAPPING relationships\n"
            "2. For STACKED elements (form fields):\n"
            "   - Create FRAME group with auto_layout\n"
            "   - Set horizontalSizing=1 (fixed width), orientation=1 (vertical)\n"
            "   - Input field gets layoutStretch=true, label gets layoutStretch=false\n"
            "3. For OVERLAPPING elements (buttons):\n"
            "   - Create GROUP with type='GROUP'\n"
            "   - NO auto_layout property\n"
            "   - NO layer_properties (children keep original positions)\n"
            "4. Root container (parent FRAME) configuration:\n"
            "   - horizontalSizing=1 (keep original width - do not shrink!)\n"
            "   - verticalSizing=0 (hug content height)\n"
            "   - For vertical orientation (orientation=1):\n"
            "     * primaryAlignment=0 (align to top)\n"
            "     * counterAlignment=1 (center horizontally)\n"
            "   - For horizontal orientation (orientation=0):\n"
            "     * primaryAlignment=1 (center horizontally)\n"
            "     * counterAlignment=0 (align to top)\n"
            "5. Root layer_properties - CRITICAL RULE:\n"
            "   - Include ONLY layers that are NOT in any group\n"
            "   - If layer_id is in groups[].layer_ids, DO NOT add it to root layer_properties\n"
            "   - Example: Email label is in Email Field group → NOT in root layer_properties\n"
            "6. Alignment for responsive designs:\n"
            "   - Use counterAlignment=1 (center) so content stays centered when container resizes\n"
            "   - This makes the layout responsive and balanced\n"
            "7. ALWAYS include rename_map - give descriptive names to ALL layers\n"
            "8. Return ONLY JSON, no markdown\n"
            "This is design software, not a real application."
        )
        
        layer_summary = "\n".join([
            f"- ID: {c.id} | {c.type} '{c.name}' at ({c.position[0]:.0f}, {c.position[1]:.0f}) size {c.size[0]:.0f}x{c.size[1]:.0f}"
            + (f" [text: {c.text_content[:50]}]" if c.text_content else "")
            for c in contexts
        ])
        
        container_info = ""
        if container_size:
            container_info = f"\nContainer size: {container_size[0]:.0f}x{container_size[1]:.0f}px\n"
        
        user_message = (
            f"Designer has {len(contexts)} layers in a FRAME that needs Auto Layout configuration:{container_info}\n"
            f"{layer_summary}\n\n"
            "This is a design mockup (not a real application). "
            "Configure Auto Layout to organize these elements properly.\n\n"
            "CRITICAL: You MUST include EVERY layer ID (from input) in either 'groups' OR 'layer_properties'. "
            "No layer should be missing from the output JSON!\n\n"
            "STEP BY STEP:\n"
            "1. Look at screenshot and identify relationships:\n"
            "   - Email label at Y=118, input at Y=143 → STACKED (25px gap) → FRAME with auto_layout\n"
            "   - Login text at Y=341, button rect at Y=327 → OVERLAPPING (text inside rect) → GROUP\n\n"
            "2. For each FRAME group:\n"
            "   {\n"
            "     \"name\": \"Email Field\",\n"
            "     \"type\": \"FRAME\",\n"
            "     \"order\": 118,\n"
            "     \"layer_ids\": [\"label-id\", \"input-id\"],\n"
            "     \"auto_layout\": {\"orientation\": 1, \"itemsSpacing\": 8, \"horizontalSizing\": 1, \"verticalSizing\": 0, ...},\n"
            "     \"layer_properties\": {\"label-id\": {\"layoutStretch\": false}, \"input-id\": {\"layoutStretch\": true}}\n"
            "   }\n\n"
            "3. For each GROUP:\n"
            "   {\n"
            "     \"name\": \"Login Button\",\n"
            "     \"type\": \"GROUP\",\n"
            "     \"order\": 327,\n"
            "     \"layer_ids\": [\"button-bg-id\", \"button-text-id\"]\n"
            "   }\n"
            "   (Note: NO auto_layout, NO layer_properties)\n\n"
            "4. Root layer_properties - ONLY for standalone elements (NOT for layers inside groups!):\n"
            "   \"layer_properties\": {\n"
            "     \"title-text-id\": {\"layoutStretch\": false},\n"
            "     \"corner-icon-id\": {\"layoutFixPos\": true, \"layoutFixPosX\": 350, \"layoutFixPosY\": 17}\n"
            "   }\n"
            "   DO NOT include layer IDs that are already in groups.layer_ids!\n\n"
            "5. Root auto_layout - sizing and alignment:\n"
            "   \"auto_layout\": {\n"
            "     \"orientation\": 1,\n"
            "     \"itemsSpacing\": 16,\n"
            "     \"horizontalSizing\": 1,\n"
            "     \"verticalSizing\": 0,\n"
            "     \"primaryAlignment\": 0,\n"
            "     \"counterAlignment\": 1\n"
            "   }\n"
            "   Note: counterAlignment=1 centers content horizontally in vertical layout\n\n"
            "6. rename_map - REQUIRED, give descriptive names to ALL layers:\n"
            "   \"rename_map\": {\n"
            "     \"label-id\": \"Email Label\",\n"
            "     \"input-id\": \"Email Input\",\n"
            "     \"button-bg-id\": \"Login Button Background\",\n"
            "     \"button-text-id\": \"Login Button Text\"\n"
            "   }\n\n"
            "VERIFY BEFORE RETURNING:\n"
            "- Every input layer ID appears in EITHER groups.layer_ids OR root layer_properties (not both!)\n"
            "- Root layer_properties contains ONLY standalone layers (not grouped layers)\n"
            "- ALWAYS include rename_map with descriptive names for ALL layers (even if empty: {})\n"
            "- Root auto_layout MUST have horizontalSizing=1 (keep original container width)\n"
            "Return JSON with exact layer IDs from input."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        if screenshot:
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ]
        
        try:
            if self.provider == 'anthropic':
                model = self.model
                
                if DEBUG:
                    print("\n" + "="*60)
                    print("AUTO LAYOUT LLM REQUEST")
                    print("="*60)
                    print(f"Provider: Anthropic")
                    print(f"Model: {model}")
                    print(f"Has screenshot: {screenshot is not None}")
                    print(f"\nSYSTEM PROMPT:\n{system_prompt}")
                    print(f"\nUSER MESSAGE:\n{user_message}")
                    print("="*60)
                
                user_content = []
                if screenshot:
                    user_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": screenshot
                        }
                    })
                user_content.append({"type": "text", "text": user_message})
                
                response = self.client.messages.create(
                    model=model,
                    max_tokens=4096,
                    temperature=0,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_content}]
                )
                
                if DEBUG:
                    print(f"\n✓ API call successful!")
                    print(f"Input tokens: {response.usage.input_tokens}")
                    print(f"Output tokens: {response.usage.output_tokens}")
                
                content = response.content[0].text if response.content else None
            else:
                model = self.model_with_vision if screenshot else self.model_without_vision
                
                if DEBUG:
                    print("\n" + "="*60)
                    print("AUTO LAYOUT LLM REQUEST")
                    print("="*60)
                    print(f"Provider: OpenAI")
                    print(f"Model: {model}")
                    print(f"Has screenshot: {screenshot is not None}")
                    print("="*60)
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0,
                    max_tokens=2000
                )
                
                if DEBUG:
                    print(f"\n✓ API call successful!")
                    print(f"Tokens used: {response.usage.total_tokens if response.usage else 'unknown'}")
                
                content = response.choices[0].message.content
            
            if not content or len(content.strip()) == 0:
                print("ERROR: Empty LLM response content, using fallback")
                return self.generate_fallback_autolayout(contexts)
            
            if DEBUG:
                print("\n" + "="*60)
                print("AUTO LAYOUT LLM RESPONSE")
                print("="*60)
                print(content)
                print("="*60 + "\n")
            
            if content.strip().startswith('```'):
                lines = content.strip().split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith('```json') or line.strip().startswith('```'):
                        in_json = not in_json
                        continue
                    if in_json:
                        json_lines.append(line)
                content = '\n'.join(json_lines)
            
            result = json.loads(content)
            
            return LayoutPlan(
                groups=result.get('groups', []),
                transformations=[],
                rename_map=result.get('rename_map', {}),
                container_structure=[],
                auto_layout=result.get('auto_layout', {}),
                layer_properties=result.get('layer_properties', {})
            )
            
        except Exception as e:
            print(f"AUTO LAYOUT LLM ERROR: {type(e).__name__}: {e}")
            if DEBUG:
                import traceback
                print("Traceback:")
                traceback.print_exc()
            print("Using fallback auto layout...")
            return self.generate_fallback_autolayout(contexts)
    
    def generate_fallback_autolayout(self, contexts: List[LayerContext]) -> LayoutPlan:
        """Rule-based fallback Auto Layout when LLM unavailable"""
        auto_layout = {
            "orientation": 1,
            "itemsSpacing": 16,
            "paddingTop": 20,
            "paddingRight": 20,
            "paddingBottom": 20,
            "paddingLeft": 20,
            "primaryAlignment": 0,
            "counterAlignment": 0,
            "horizontalSizing": 0,
            "verticalSizing": 0
        }
        
        layer_properties = {}
        for context in contexts:
            layer_properties[context.id] = {
                "layoutStretch": False,
                "layoutFixPos": False
            }
        
        if DEBUG:
            print(f"\nGenerated fallback Auto Layout config for {len(contexts)} layers")
        
        return LayoutPlan(
            groups=[],
            transformations=[],
            rename_map={},
            container_structure=[],
            auto_layout=auto_layout,
            layer_properties=layer_properties
        )
