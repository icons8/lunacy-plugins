#!/usr/bin/env python3
"""
AI Layout Optimizer Plugin for Lunacy
"""

import sys
import os

DEBUG = os.getenv("DEBUG", "0") == "1"

from lunacy_api import LunacyAPIClient
from analyzers import SelectionAnalyzer, VisualContextGatherer
from llm_analyzer import LLMAnalyzer
from layout_engine import LayoutEngine

class SmartLayoutGenerator:
    """Main orchestrator for smart layout generation"""
    
    def __init__(self):
        self.api = LunacyAPIClient()
        self.analyzer = SelectionAnalyzer(self.api)
        self.visual = VisualContextGatherer(self.api)
        
        try:
            self.llm = LLMAnalyzer()
            self.has_llm = True
        except ValueError as e:
            print(f"Warning: {e}")
            print("Falling back to rule-based layout")
            self.llm = None
            self.has_llm = False
        
        self.engine = LayoutEngine(self.api)
    
    def generate(self) -> bool:
        """Main execution flow"""
        try:
            self.api.show_toast("Analyzing selection...", 5)
            
            selection = self.api.get_selected()
            if not selection:
                self.api.show_toast("Please select layers to optimize", 4)
                return False
            
            layers_to_optimize = []
            parent_container_id = None
            parent_container_size = None
            
            for layer in selection:
                layer_type = layer.get('_t', '')
                if layer_type in ('FRAME', 'GROUP', 'SECTION'):
                    parent_container_id = layer.get('id')
                    parent_container_size = layer.get('size')
                    children = layer.get('layers', [])
                    if children:
                        if DEBUG:
                            print(f"Extracting {len(children)} children from {layer_type} '{layer.get('name')}' (ID: {parent_container_id})")
                        layers_to_optimize.extend(children)
                    else:
                        layers_to_optimize.append(layer)
                else:
                    layers_to_optimize.append(layer)
            
            if not layers_to_optimize:
                self.api.show_toast("No layers to optimize", 4)
                return False
            
            contexts = self.analyzer.analyze(layers_to_optimize)
            
            if DEBUG:
                print(f"Analyzing {len(layers_to_optimize)} layers...")
                print("\nLayer contexts generated:")
                for ctx in contexts:
                    print(f"  ID: {ctx.id}, Name: {ctx.name}, Type: {ctx.type}")
                print()
            
            if self.has_llm and self.llm:
                self.api.show_toast("Analyzing with AI...", 5)
                layer_ids = [c.id for c in contexts]
                screenshot = self.visual.capture_screenshot(layer_ids)
                
                plan = self.llm.analyze_layout(contexts, screenshot, parent_container_size)
                
                if DEBUG:
                    print(f"LLM returned plan with {len(plan.transformations)} transformations, {len(plan.groups)} groups")
            else:
                self.api.show_toast("Generating layout...", 5)
                analyzer = LLMAnalyzer.__new__(LLMAnalyzer)
                analyzer.client = None  # type: ignore
                analyzer.api_key = None
                plan = analyzer.generate_fallback_autolayout(contexts)
            
            self.api.show_toast("Applying layout...", 5)
            success = self.engine.apply(plan, layers_to_optimize, parent_container_id)
            
            if success:
                self.api.show_toast("Auto Layout configured!", 2)
                return True
            else:
                self.api.show_toast("Failed to apply layout", 4)
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            self.api.show_toast(f"Error: {str(e)}", 4)
            return False

def main():
    """Plugin entry point"""
    print("AI Layout Optimizer v1.0")
    print("=" * 50)
    
    try:
        generator = SmartLayoutGenerator()
        success = generator.generate()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
