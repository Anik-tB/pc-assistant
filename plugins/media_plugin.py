"""
Media Control Plugin
Controls system volume and media playback
"""

from modules.plugin_manager import PluginBase
import ctypes
from typing import Dict, Any

class MediaPlugin(PluginBase):
    """Plugin for controlling system media and volume"""

    name = "Media Controller"
    version = "1.0.0"
    author = "PC Assistant Team"
    description = "Control system volume and media playback"

    def initialize(self) -> bool:
        """Initialize the plugin"""
        # Virtual key codes for Windows
        self.VK_VOLUME_MUTE = 0xAD
        self.VK_VOLUME_DOWN = 0xAE
        self.VK_VOLUME_UP = 0xAF
        self.VK_MEDIA_NEXT_TRACK = 0xB0
        self.VK_MEDIA_PREV_TRACK = 0xB1
        self.VK_MEDIA_PLAY_PAUSE = 0xB3
        return True

    def register_commands(self) -> Dict[str, callable]:
        return {
            "set_volume_up": self.volume_up,
            "set_volume_down": self.volume_down,
            "toggle_mute": self.toggle_mute,
            "media_play_pause": self.play_pause,
            "media_next": self.next_track,
            "media_prev": self.prev_track,
        }

    def _press_key(self, vk_code):
        try:
            ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def volume_up(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Increase system volume. Optionally provide 'amount' (int)"""
        amount = int(params.get("amount", 2))
        for _ in range(amount):
            self._press_key(self.VK_VOLUME_UP)
        return {"success": True, "message": "Increased volume"}

    def volume_down(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Decrease system volume. Optionally provide 'amount' (int)"""
        amount = int(params.get("amount", 2))
        for _ in range(amount):
            self._press_key(self.VK_VOLUME_DOWN)
        return {"success": True, "message": "Decreased volume"}

    def toggle_mute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Toggle system mute"""
        self._press_key(self.VK_VOLUME_MUTE)
        return {"success": True, "message": "Toggled mute"}

    def play_pause(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Play or pause current media"""
        self._press_key(self.VK_MEDIA_PLAY_PAUSE)
        return {"success": True, "message": "Toggled play/pause"}

    def next_track(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Skip to next track"""
        self._press_key(self.VK_MEDIA_NEXT_TRACK)
        return {"success": True, "message": "Next track"}

    def prev_track(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Go to previous track"""
        self._press_key(self.VK_MEDIA_PREV_TRACK)
        return {"success": True, "message": "Previous track"}
