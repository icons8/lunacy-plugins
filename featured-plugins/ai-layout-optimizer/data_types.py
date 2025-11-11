"""
Data types for AI Layout Optimizer
"""

from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict, Any

@dataclass
class LayerContext:
    """Structured layer metadata for analysis"""
    id: str
    name: str
    type: str
    position: Tuple[float, float]
    size: Tuple[float, float]
    text_content: Optional[str] = None
    has_image: bool = False
    children_count: int = 0

@dataclass
class LayoutPlan:
    """LLM-generated layout instructions"""
    groups: List[Dict[str, Any]]
    transformations: List[Dict[str, Any]]
    rename_map: Dict[str, str]
    container_structure: List[Dict[str, Any]]
    auto_layout: Optional[Dict[str, Any]] = None
    layer_properties: Optional[Dict[str, Dict[str, Any]]] = None
