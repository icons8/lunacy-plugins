"""
Helper utilities for AI Layout Optimizer
"""

import base64
import uuid
from typing import Tuple, List

GRID_SIZE = 8

class ShortGuid:
    """Generate Lunacy-compatible 22-char base64 GUIDs"""
    
    @staticmethod
    def new_guid() -> str:
        """Generate new ShortGuid compatible with Lunacy"""
        guid = uuid.uuid4()
        guid_bytes = guid.bytes
        
        base64_bytes = base64.b64encode(guid_bytes).decode('ascii')
        
        short_guid = base64_bytes[:22].replace('+', '-').replace('/', '_')
        
        return short_guid

class TransformHelper:
    """Helper for FREE format transform matrix operations"""
    
    @staticmethod
    def get_position(transform: List[float]) -> Tuple[float, float]:
        """Extract position from transform matrix
        
        Supports two formats:
        - Short: [x, y] - simple translation
        - Full: [scaleX, skewX, transX, skewY, scaleY, transY]
        """
        if len(transform) == 2:
            return (transform[0], transform[1])
        elif len(transform) >= 6:
            return (transform[2], transform[5])
        return (0.0, 0.0)
    
    @staticmethod
    def set_position(transform: List[float], x: float, y: float) -> List[float]:
        """Update position in transform matrix"""
        if len(transform) == 2:
            return [x, y]
        elif len(transform) >= 6:
            new_transform = transform.copy()
            new_transform[2] = x
            new_transform[5] = y
            return new_transform
        else:
            return [x, y]
    
    @staticmethod
    def snap_to_grid(value: float, grid_size: int = GRID_SIZE) -> float:
        """Snap value to nearest grid point"""
        return round(value / grid_size) * grid_size
