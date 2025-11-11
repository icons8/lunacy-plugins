"""
Layout engine for applying transformations
"""

import json
from typing import List, Dict, Optional, Any

from data_types import LayoutPlan
from lunacy_api import LunacyAPIClient
from helpers import TransformHelper, ShortGuid
import os

DEBUG = os.getenv("DEBUG", "0") == "1"

class LayoutEngine:
    """Applies layout transformations to Lunacy layers"""
    
    def __init__(self, api_client: LunacyAPIClient):
        self.api = api_client
        self.transform = TransformHelper()
    
    def apply(self, plan: LayoutPlan, original_layers: List[Dict], parent_container_id: Optional[str] = None) -> bool:
        """Execute layout plan"""
        try:
            return self.apply_autolayout(plan, original_layers, parent_container_id)
        except Exception as e:
            print(f"Error applying layout: {e}")
            return False
    
    def apply_autolayout(self, plan: LayoutPlan, original_layers: List[Dict], parent_container_id: Optional[str] = None) -> bool:
        """Apply Auto Layout configuration with semantic grouping"""
        try:
            if not parent_container_id:
                print("ERROR: Auto Layout requires a parent FRAME container ID")
                return False
            
            if DEBUG:
                print(f"\nApplying Auto Layout to FRAME {parent_container_id}...")
                print(f"Groups: {len(plan.groups)}")
                print(f"Rename map: {len(plan.rename_map) if plan.rename_map else 0} items")
            
            layers_by_id = {layer['id']: layer for layer in original_layers}
            layers_in_groups = set()
            
            for group_spec in plan.groups:
                layers_in_groups.update(group_spec.get('layer_ids', []))
            
            all_items_to_create = []
            
            for group_spec in plan.groups:
                layer_pos_list = [self.transform.get_position(layers_by_id[lid].get('transform', [0, 0]))[1] 
                                 for lid in group_spec.get('layer_ids', []) if lid in layers_by_id]
                min_y = min(layer_pos_list) if layer_pos_list else group_spec.get('order', 0)
                all_items_to_create.append(('group', min_y, group_spec))
            
            for layer in original_layers:
                layer_id = layer['id']
                if layer_id not in layers_in_groups:
                    layer_pos = self.transform.get_position(layer.get('transform', [0, 0]))
                    all_items_to_create.append(('standalone', layer_pos[1], layer, layer_id))
            
            all_items_to_create.sort(key=lambda x: x[1], reverse=False)
            
            if DEBUG:
                print(f"\nBuilding final structure with {len(all_items_to_create)} elements...")
            
            final_children = []
            
            for item in all_items_to_create:
                if item[0] == 'group':
                    group_spec = item[2]
                    group_name = group_spec.get('name', 'Group')
                    group_type = group_spec.get('type', 'FRAME')
                    layer_ids = group_spec.get('layer_ids', [])
                    
                    if not layer_ids:
                        continue
                    
                    original_positions = {lid: self.transform.get_position(layers_by_id[lid].get('transform', [0, 0])) 
                                        for lid in layer_ids if lid in layers_by_id}
                    
                    if not original_positions:
                        continue
                    
                    min_x = min(pos[0] for pos in original_positions.values())
                    min_y = min(pos[1] for pos in original_positions.values())
                    
                    group_children = []
                    for lid in layer_ids:
                        if lid not in layers_by_id:
                            continue
                        
                        child = layers_by_id[lid].copy()
                        
                        if group_type == 'GROUP':
                            orig_pos = original_positions[lid]
                            relative_x = orig_pos[0] - min_x
                            relative_y = orig_pos[1] - min_y
                            child['transform'] = [relative_x, relative_y]
                        else:
                            group_layer_props = group_spec.get('layer_properties', {})
                            if lid in group_layer_props:
                                props = group_layer_props[lid]
                                if 'layoutStretch' in props:
                                    child['layoutStretch'] = props['layoutStretch']
                                if 'layoutFixPos' in props and props['layoutFixPos']:
                                    child['layoutFixPos'] = True
                                    if 'layoutFixPosX' in props and 'layoutFixPosY' in props:
                                        llm_x = props['layoutFixPosX']
                                        llm_y = props['layoutFixPosY']
                                        relative_x = llm_x - min_x
                                        relative_y = llm_y - min_y
                                        child['transform'] = [relative_x, relative_y]
                                    else:
                                        orig_pos = original_positions[lid]
                                        relative_x = orig_pos[0] - min_x
                                        relative_y = orig_pos[1] - min_y
                                        child['transform'] = [relative_x, relative_y]
                                else:
                                    child['transform'] = [0, 0]
                            else:
                                child['transform'] = [0, 0]
                        
                        if plan.rename_map is not None and lid in plan.rename_map:
                            child['name'] = plan.rename_map[lid]
                            if DEBUG:
                                print(f"    Renamed {lid} to '{plan.rename_map[lid]}'")
                        
                        group_children.append(child)
                    
                    if not group_children:
                        continue
                    
                    group_id = ShortGuid.new_guid()
                    
                    if group_type == 'GROUP':
                        group_frame = {
                            "_t": "GROUP",
                            "id": group_id,
                            "name": group_name,
                            "transform": [0, 0],
                            "layers": group_children
                        }
                    else:
                        group_auto_layout = group_spec.get('auto_layout', {})
                        padding_top = group_auto_layout.get('paddingTop', 0)
                        padding_right = group_auto_layout.get('paddingRight', 0)
                        padding_bottom = group_auto_layout.get('paddingBottom', 0)
                        padding_left = group_auto_layout.get('paddingLeft', 0)
                        
                        group_frame = {
                            "_t": group_type,
                            "id": group_id,
                            "name": group_name,
                            "transform": [0, 0],
                            "container": {
                                "_t": "AUTO",
                                "orientation": group_auto_layout.get('orientation', 1),
                                "spacing": group_auto_layout.get('itemsSpacing', 8),
                                "padding": [padding_left, padding_top, padding_right, padding_bottom],
                                "align": group_auto_layout.get('primaryAlignment', 0),
                                "valign": group_auto_layout.get('counterAlignment', 0),
                                "sizing": group_auto_layout.get('horizontalSizing', 0),
                                "vsizing": group_auto_layout.get('verticalSizing', 0)
                            },
                            "layers": group_children
                        }
                    
                    if group_type == 'FRAME':
                        group_frame['layoutStretch'] = True
                    
                    final_children.append(group_frame)
                    
                    if DEBUG:
                        print(f"  Built {group_type} '{group_name}' with {len(group_children)} children")
                
                elif item[0] == 'standalone':
                    layer = item[2]
                    original_id = item[3]
                    
                    standalone_layer = layer.copy()
                    
                    if plan.rename_map is not None and original_id in plan.rename_map:
                        standalone_layer['name'] = plan.rename_map[original_id]
                    
                    if plan.layer_properties and original_id in plan.layer_properties:
                        props = plan.layer_properties[original_id]
                        if 'layoutStretch' in props:
                            standalone_layer['layoutStretch'] = props['layoutStretch']
                        if 'layoutFixPos' in props and props['layoutFixPos']:
                            standalone_layer['layoutFixPos'] = True
                            if 'layoutFixPosX' in props and 'layoutFixPosY' in props:
                                new_x = props['layoutFixPosX']
                                new_y = props['layoutFixPosY']
                                standalone_layer['transform'] = self.transform.set_position(
                                    layer.get('transform', [0, 0]),
                                    new_x,
                                    new_y
                                )
                                if DEBUG:
                                    print(f"    {standalone_layer['name']}: layoutFixPos at [{new_x}, {new_y}]")
                            else:
                                standalone_layer['transform'] = layer.get('transform', [0, 0])
                        else:
                            standalone_layer['transform'] = [0, 0]
                    else:
                        standalone_layer['transform'] = [0, 0]
                    
                    final_children.append(standalone_layer)
                    
                    if DEBUG:
                        print(f"  Built standalone '{standalone_layer['name']}'")
            
            parent_frame = self.api.get_layers_by_ids([parent_container_id])
            if not parent_frame or len(parent_frame) == 0:
                print(f"ERROR: Parent FRAME {parent_container_id} not found")
                return False
            
            parent_data = parent_frame[0]
            
            if parent_data.get('_t') != 'FRAME':
                print(f"ERROR: Parent container is {parent_data.get('_t')}, not FRAME")
                return False
            
            auto_layout_config = plan.auto_layout or {}
            padding_top = auto_layout_config.get('paddingTop', 20)
            padding_right = auto_layout_config.get('paddingRight', 20)
            padding_bottom = auto_layout_config.get('paddingBottom', 20)
            padding_left = auto_layout_config.get('paddingLeft', 20)
            
            orientation = auto_layout_config.get('orientation', 1)
            primary = auto_layout_config.get('primaryAlignment', 0)
            counter = auto_layout_config.get('counterAlignment', 0)
            
            if orientation == 1:
                align_value = counter
                valign_value = primary
            else:
                align_value = primary
                valign_value = counter
            
            updated_parent = parent_data.copy()
            updated_parent["container"] = {
                "_t": "AUTO",
                "orientation": orientation,
                "spacing": auto_layout_config.get('itemsSpacing', 16),
                "padding": [padding_left, padding_top, padding_right, padding_bottom],
                "align": align_value,
                "valign": valign_value,
                "sizing": auto_layout_config.get('horizontalSizing', 0),
                "vsizing": auto_layout_config.get('verticalSizing', 0)
            }
            updated_parent["layers"] = final_children
            
            if DEBUG:
                print(f"\nReplacing entire FRAME with Auto Layout and {len(final_children)} children:")
                print(f"  Orientation: {'vertical' if orientation == 1 else 'horizontal'}")
                print(f"  Spacing: {auto_layout_config.get('itemsSpacing', 16)}px")
                print(f"  Padding: T{padding_top} R{padding_right} B{padding_bottom} L{padding_left}")
            
            try:
                success = self.api.update_layers([updated_parent])
                if not success:
                    print("ERROR: Failed to update parent FRAME with Auto Layout")
                    return False
                
                if DEBUG:
                    print("\n✓ Successfully applied Auto Layout!")
                
                return True
            except Exception as api_error:
                print(f"ERROR: API call failed: {type(api_error).__name__}: {api_error}")
                if DEBUG:
                    import traceback
                    traceback.print_exc()
                return False
            
        except Exception as e:
                print(f"Error applying Auto Layout: {e}")
                if DEBUG:
                    import traceback
                    traceback.print_exc()
                return False
    
    def apply_groups_layout(self, plan: LayoutPlan, original_layers: List[Dict], parent_container_id: Optional[str] = None) -> bool:
        """Apply groups-based layout (original behavior)"""
        try:
            if DEBUG:
                print(f"\nApplying layout plan with {len(plan.transformations)} transformations...")
                print(f"\nAvailable layer IDs in selection:")
                for layer_id, layer in {layer['id']: layer for layer in original_layers}.items():
                    print(f"  {layer_id}: {layer.get('name')}")
                print()
            
            layers_by_id = {layer['id']: layer for layer in original_layers}
            
            layers_in_groups = set()
            for group_spec in plan.groups:
                layers_in_groups.update(group_spec.get('layer_ids', []))
            
            if plan.groups:
                if DEBUG:
                    print(f"\nCreating {len(plan.groups)} semantic groups...")
                
                for group_spec in plan.groups:
                    group_name = group_spec.get('name', 'Group')
                    group_type = group_spec.get('type', 'GROUP')
                    layer_ids = group_spec.get('layer_ids', [])
                    
                    if not layer_ids:
                        continue
                    
                    group_layers = [layers_by_id[lid] for lid in layer_ids if lid in layers_by_id]
                    if not group_layers:
                        continue
                    
                    group_x_raw = group_spec.get('x', 0)
                    group_y_raw = group_spec.get('y', 0)
                    has_group_position = group_spec.get('x') is not None and group_spec.get('y') is not None
                    
                    group_x = self.transform.snap_to_grid(float(group_x_raw)) if has_group_position else 0.0
                    group_y = self.transform.snap_to_grid(float(group_y_raw)) if has_group_position else 0.0
                    
                    group_children = []
                    for lid in layer_ids:
                        if lid not in layers_by_id:
                            continue
                        
                        child = layers_by_id[lid].copy()
                        
                        if has_group_position:
                            transform_spec = next(
                                (t for t in plan.transformations if t.get('layer_id') == lid),
                                None
                            )
                            
                            if transform_spec:
                                new_x = self.transform.snap_to_grid(transform_spec.get('x', 0))
                                new_y = self.transform.snap_to_grid(transform_spec.get('y', 0))
                            else:
                                new_x, new_y = 0.0, 0.0
                            
                            child['transform'] = self.transform.set_position(
                                child.get('transform', [0, 0]),
                                new_x,
                                new_y
                            )
                            if DEBUG:
                                print(f"    {child.get('name')}: pos ({new_x}, {new_y})")
                        
                        new_name = plan.rename_map.get(lid)
                        if new_name:
                            child['name'] = new_name
                        
                        group_children.append(child)
                    
                    if not group_children:
                        continue
                    
                    if not has_group_position:
                        positions = [self.transform.get_position(c.get('transform', [0, 0])) 
                                   for c in group_children]
                        
                        min_x = min(p[0] for p in positions)
                        min_y = min(p[1] for p in positions)
                        group_x, group_y = min_x, min_y
                        
                        for child in group_children:
                            current_pos = self.transform.get_position(child.get('transform', [0, 0]))
                            relative_x = current_pos[0] - min_x
                            relative_y = current_pos[1] - min_y
                            
                            child['transform'] = self.transform.set_position(
                                child.get('transform', [0, 0]),
                                relative_x,
                                relative_y
                            )
                            if DEBUG:
                                print(f"    {child.get('name')}: pos ({relative_x}, {relative_y}) [from original]")
                    
                    group_id = ShortGuid.new_guid()
                    
                    group_json = json.dumps([{
                        "_t": group_type,
                        "id": group_id,
                        "name": group_name,
                        "transform": [group_x, group_y],
                        "layers": group_children
                    }])
                    
                    try:
                        response_text = self.api.create_group(parent_container_id, group_json)
                        
                        if DEBUG:
                            print(f"  Created group '{group_name}' at ({group_x}, {group_y}) with {len(group_children)} children (ID: {group_id})")
                            print(f"  API response: {response_text}")
                        
                        for lid in layer_ids:
                            self.api.delete_layers([lid])
                        
                        if DEBUG:
                            print(f"  Deleted {len(layer_ids)} original layers")
                        
                    except Exception as e:
                        print(f"Warning: Failed to create group '{group_name}': {e}")
            
            updated_layers = []
            for transform_spec in plan.transformations:
                layer_id = transform_spec.get('layer_id')
                if not layer_id or layer_id in layers_in_groups:
                    continue
                
                layer = layers_by_id.get(layer_id)
                if not layer:
                    continue
                
                new_x = self.transform.snap_to_grid(transform_spec.get('x', 0))
                new_y = self.transform.snap_to_grid(transform_spec.get('y', 0))
                
                current_transform = layer.get('transform', [0, 0])
                old_x, old_y = self.transform.get_position(current_transform)
                new_transform = self.transform.set_position(current_transform, new_x, new_y)
                
                if DEBUG:
                    print(f"  {layer.get('name')}: ({old_x}, {old_y}) → ({new_x}, {new_y})")
                
                updated_layer = layer.copy()
                updated_layer['transform'] = new_transform
                
                new_name = plan.rename_map.get(layer_id)
                if new_name:
                    updated_layer['name'] = new_name
                
                updated_layers.append(updated_layer)
            
            if updated_layers:
                if DEBUG:
                    print(f"\nUpdating {len(updated_layers)} standalone layers via API...")
                
                success = self.api.update_layers(updated_layers)
                if not success:
                    print("Warning: Failed to update standalone layers")
            
            return True
            
        except Exception as e:
            print(f"Error applying layout: {e}")
            return False
