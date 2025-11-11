"""
Lunacy API Client
"""

import requests
from typing import List, Dict, Optional

class LunacyAPIClient:
    """HTTP API client for Lunacy"""
    
    def __init__(self, base_url: str = "http://localhost:31415"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def get_selected(self) -> List[Dict]:
        """Get currently selected layers"""
        try:
            response = self.session.get(f"{self.base_url}/getselected", timeout=10)
            response.raise_for_status()
            selection = response.json()
            
            if isinstance(selection, dict) and selection.get('_t'):
                return [selection]
            elif isinstance(selection, list):
                return selection
            else:
                return []
        except Exception as e:
            raise RuntimeError(f"Failed to get selection: {e}")
    
    def get_layers_by_ids(self, layer_ids: List[str]) -> List[Dict]:
        """Get layers by their IDs"""
        try:
            response = self.session.post(
                f"{self.base_url}/getlayersbyids",
                json=layer_ids,
                timeout=10
            )
            response.raise_for_status()
            layers = response.json()
            
            if isinstance(layers, dict) and layers.get('_t'):
                return [layers]
            elif isinstance(layers, list):
                return layers
            else:
                return []
        except Exception as e:
            raise RuntimeError(f"Failed to get layers by IDs: {e}")
    
    def get_screenshot(self, layer_ids: List[str]) -> bytes:
        """Get screenshot of specified layers"""
        try:
            response = self.session.post(
                f"{self.base_url}/getscreenshotbyid",
                json=layer_ids,
                timeout=30
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise RuntimeError(f"Failed to get screenshot: {e}")
    
    def update_layers(self, layers: List[Dict]) -> bool:
        """Update existing layers"""
        try:
            response = self.session.post(
                f"{self.base_url}/updatelayers",
                json=layers,
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error updating layers: {e}")
            print(f"Response: {e.response.text if e.response else 'No response'}")
            return False
        except Exception as e:
            print(f"Error updating layers: {type(e).__name__}: {e}")
            return False
    
    def create_group(self, parent_id: Optional[str], layers_json: str) -> str:
        """Create new group/frame container - returns plain text response"""
        try:
            payload = {
                "parentId": parent_id,
                "layersJson": layers_json
            }
            
            response = self.session.post(
                f"{self.base_url}/createlayers",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.text
            
        except Exception as e:
            raise RuntimeError(f"Failed to create group: {e}")
    
    def delete_layers(self, layer_ids: List[str]) -> str:
        """Delete layers by IDs"""
        try:
            response = self.session.post(
                f"{self.base_url}/deletelayers",
                json=layer_ids,
                timeout=10
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Failed to delete layers: {e}"
    
    def show_toast(self, text: str, icon_type: int = 2):
        """Show notification toast"""
        try:
            self.session.post(
                f"{self.base_url}/showtoast",
                json={
                    "text": text,
                    "iconType": icon_type,
                    "priority": 5,
                    "durationSeconds": 5
                },
                timeout=5
            )
        except Exception:
            pass
