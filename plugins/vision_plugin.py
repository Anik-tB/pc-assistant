"""
Screen Vision Plugin
Captures screen and provides it for AI analysis
"""

from modules.plugin_manager import PluginBase
from typing import Dict, Any
import base64
import os
import io

class VisionPlugin(PluginBase):
    """Plugin for capturing screen for AI vision analysis"""

    name = "Screen Vision"
    version = "1.0.0"
    author = "PC Assistant Team"
    description = "Capture screenshots for AI multimodal analysis"

    def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            import mss
            from PIL import Image
            self.mss = mss
            self.Image = Image
            return True
        except ImportError:
            print("Vision plugin requires mss and Pillow. Run: pip install mss Pillow")
            return False

    def register_commands(self) -> Dict[str, callable]:
        return {
            "take_screenshot_base64": self.take_screenshot_base64
        }

    def take_screenshot_base64(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a screenshot of the main monitor and returns it as a base64 encoded jpeg.
        """
        try:
            with self.mss.mss() as sct:
                monitor = sct.monitors[1]  # primary monitor
                sct_img = sct.grab(monitor)
                
                img = self.Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Compress to save tokens
                img.thumbnail((1024, 1024))
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=75)
                img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                return {
                    "success": True, 
                    "message": "Screenshot captured",
                    "output": img_str, # base64 string
                    "mime_type": "image/jpeg"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
