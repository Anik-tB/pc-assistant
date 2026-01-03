"""
Example Plugin: Browser Controller
Controls web browsers (Chrome, Firefox, Edge)
"""

from modules.plugin_manager import PluginBase
import subprocess
import platform
from typing import Dict, Any


class BrowserPlugin(PluginBase):
    """Plugin for controlling web browsers"""

    name = "Browser Controller"
    version = "1.0.0"
    author = "PC Assistant Team"
    description = "Control web browsers - open URLs, manage tabs, etc."

    def initialize(self) -> bool:
        """Initialize the plugin"""
        self.os_type = platform.system().lower()
        print(f"🌐 Browser Controller initialized for {self.os_type}")
        return True

    def register_commands(self) -> Dict[str, callable]:
        """Register plugin commands"""
        return {
            "open_url": self.open_url,
            "open_browser": self.open_browser,
            "close_browser": self.close_browser
        }

    def open_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Open a URL in default browser

        Params:
            url: URL to open
            browser: Optional browser name (chrome, firefox, edge)
        """
        url = params.get("url", "")
        browser = params.get("browser", "default")

        if not url:
            return {"success": False, "error": "No URL provided"}

        try:
            if browser == "default":
                if self.os_type == "windows":
                    subprocess.run(["start", url], shell=True)
                elif self.os_type == "darwin":  # macOS
                    subprocess.run(["open", url])
                else:  # Linux
                    subprocess.run(["xdg-open", url])
            else:
                # Open in specific browser
                browser_commands = {
                    "chrome": "chrome" if self.os_type != "windows" else "start chrome",
                    "firefox": "firefox",
                    "edge": "msedge" if self.os_type == "windows" else "microsoft-edge"
                }

                cmd = browser_commands.get(browser.lower(), "")
                if cmd:
                    subprocess.run(f"{cmd} {url}", shell=True)
                else:
                    return {"success": False, "error": f"Unknown browser: {browser}"}

            return {
                "success": True,
                "message": f"Opened {url} in {browser}"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_browser(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Open a browser

        Params:
            browser: Browser name (chrome, firefox, edge)
        """
        browser = params.get("browser", "chrome").lower()

        try:
            if self.os_type == "windows":
                commands = {
                    "chrome": "start chrome",
                    "firefox": "start firefox",
                    "edge": "start msedge"
                }
            else:
                commands = {
                    "chrome": "google-chrome &",
                    "firefox": "firefox &",
                    "edge": "microsoft-edge &"
                }

            cmd = commands.get(browser)
            if cmd:
                subprocess.run(cmd, shell=True)
                return {"success": True, "message": f"Opened {browser}"}
            else:
                return {"success": False, "error": f"Unknown browser: {browser}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def close_browser(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Close a browser

        Params:
            browser: Browser name (chrome, firefox, edge)
        """
        browser = params.get("browser", "chrome").lower()

        try:
            if self.os_type == "windows":
                process_names = {
                    "chrome": "chrome.exe",
                    "firefox": "firefox.exe",
                    "edge": "msedge.exe"
                }
                process = process_names.get(browser)
                if process:
                    subprocess.run(f"taskkill /F /IM {process}", shell=True)
            else:
                subprocess.run(f"pkill -f {browser}", shell=True)

            return {"success": True, "message": f"Closed {browser}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def shutdown(self):
        """Cleanup when plugin is unloaded"""
        print("🌐 Browser Controller shutdown")
