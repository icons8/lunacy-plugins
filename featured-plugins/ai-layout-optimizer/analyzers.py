"""
Selection and visual context analyzers
"""

import os
import io
import base64
from typing import List, Optional, Dict, Any
from PIL import Image

from data_types import LayerContext
from lunacy_api import LunacyAPIClient
from helpers import TransformHelper

DEBUG = os.getenv("DEBUG", "0") == "1"

class SelectionAnalyzer:
    """Analyzes selected layers and extracts context"""
    
    def __init__(self, api_client: LunacyAPIClient):
        self.api = api_client
        self.transform = TransformHelper()
    
    def analyze(self, selection: List[Dict]) -> List[LayerContext]:
        """Extract structured metadata from layers"""
        contexts = []
        
        for layer in selection:
            layer_id = layer.get('id', '')
            layer_type = layer.get('_t', 'UNKNOWN')
            name = layer.get('name', 'Unnamed')
            
            transform = layer.get('transform', [1, 0, 0, 0, 1, 0])
            position = self.transform.get_position(transform)
            
            size_data = layer.get('size', [100, 100])
            size = (size_data[0], size_data[1]) if isinstance(size_data, list) else (100, 100)
            
            text_content = layer.get('text') if layer_type == 'TEXT' else None
            
            has_image = bool(layer.get('fills', []))
            
            children = layer.get('layers', [])
            children_count = len(children) if isinstance(children, list) else 0
            
            contexts.append(LayerContext(
                id=layer_id,
                name=name,
                type=layer_type,
                position=position,
                size=size,
                text_content=text_content,
                has_image=has_image,
                children_count=children_count
            ))
        
        return contexts

class VisualContextGatherer:
    """Captures and processes screenshots for LLM analysis"""
    
    def __init__(self, api_client: LunacyAPIClient):
        self.api = api_client
    
    def capture_screenshot(self, layer_ids: List[str]) -> Optional[str]:
        """Capture screenshot and encode as base64"""
        try:
            screenshot_data = self.api.get_screenshot(layer_ids)
            
            if not screenshot_data:
                return None
            
            img = Image.open(io.BytesIO(screenshot_data))
            
            max_size = 1024
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG', optimize=True)
            buffer.seek(0)
            
            base64_image = base64.b64encode(buffer.read()).decode('utf-8')
            return base64_image
            
        except Exception as e:
            print(f"Warning: Failed to capture screenshot: {e}")
            return None
