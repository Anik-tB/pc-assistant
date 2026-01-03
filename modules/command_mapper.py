"""
Command Mapper
Maps intents to OS-specific system commands
"""

import platform
from typing import Dict, Any, List, Optional


class CommandMapper:
    """Maps intents to executable system commands"""

    def __init__(self):
        """Initialize command mapper"""
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == "windows"
        self.is_linux = self.os_type == "linux"
        self.is_mac = self.os_type == "darwin"

    def map_intent_to_command(self, intent: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Map intent and parameters to system command

        Args:
            intent: The intent type
            parameters: Parameters for the command

        Returns:
            Dictionary with command, shell flag, and metadata
        """
        mapper_method = getattr(self, f"_map_{intent}", None)

        if mapper_method:
            return mapper_method(parameters)
        else:
            return {
                "error": f"Unknown intent: {intent}",
                "command": None
            }

    def _map_open_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map open application intent"""
        app_name = params.get("app_name", "").lower()

        if self.is_windows:
            # Common Windows applications
            app_map = {
                "chrome": "start chrome",
                "firefox": "start firefox",
                "edge": "start msedge",
                "notepad": "start notepad",
                "calculator": "start calc",
                "explorer": "start explorer",
                "cmd": "start cmd",
                "powershell": "start powershell",
                "vscode": "start code",
                "word": "start winword",
                "excel": "start excel",
            }
            command = app_map.get(app_name, f"start {app_name}")

        elif self.is_linux:
            # Common Linux applications
            app_map = {
                "chrome": "google-chrome &",
                "firefox": "firefox &",
                "terminal": "gnome-terminal &",
                "files": "nautilus &",
                "vscode": "code &",
            }
            command = app_map.get(app_name, f"{app_name} &")

        else:  # macOS
            command = f"open -a {app_name}"

        return {
            "command": command,
            "shell": True,
            "description": f"Opening {app_name}"
        }

    def _map_close_app(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map close application intent"""
        app_name = params.get("app_name", "").lower()

        if self.is_windows:
            # Try to kill by process name
            command = f"taskkill /F /IM {app_name}.exe"
        elif self.is_linux:
            command = f"pkill -f {app_name}"
        else:  # macOS
            command = f"pkill -f {app_name}"

        return {
            "command": command,
            "shell": True,
            "description": f"Closing {app_name}",
            "requires_confirmation": True
        }

    def _map_find_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map find files intent"""
        extension = params.get("extension", "")
        name = params.get("name", "")
        path = params.get("path", "C:\\" if self.is_windows else "/home")

        if self.is_windows:
            if extension:
                command = f'powershell "Get-ChildItem -Path {path} -Filter *.{extension} -Recurse -ErrorAction SilentlyContinue | Select-Object FullName"'
            elif name:
                command = f'powershell "Get-ChildItem -Path {path} -Filter *{name}* -Recurse -ErrorAction SilentlyContinue | Select-Object FullName"'
            else:
                return {"error": "No search criteria specified", "command": None}
        else:
            if extension:
                command = f'find {path} -name "*.{extension}" 2>/dev/null'
            elif name:
                command = f'find {path} -name "*{name}*" 2>/dev/null'
            else:
                return {"error": "No search criteria specified", "command": None}

        return {
            "command": command,
            "shell": True,
            "description": f"Searching for files with {extension or name}"
        }

    def _map_shutdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map shutdown intent"""
        delay_minutes = params.get("delay_minutes", 0)
        delay_seconds = delay_minutes * 60

        if self.is_windows:
            command = f"shutdown /s /t {delay_seconds}"
        else:
            if delay_minutes > 0:
                command = f"shutdown -h +{delay_minutes}"
            else:
                command = "shutdown -h now"

        return {
            "command": command,
            "shell": True,
            "description": f"Shutting down in {delay_minutes} minutes" if delay_minutes > 0 else "Shutting down now",
            "requires_confirmation": True
        }

    def _map_restart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map restart intent"""
        delay_minutes = params.get("delay_minutes", 0)
        delay_seconds = delay_minutes * 60

        if self.is_windows:
            command = f"shutdown /r /t {delay_seconds}"
        else:
            if delay_minutes > 0:
                command = f"shutdown -r +{delay_minutes}"
            else:
                command = "shutdown -r now"

        return {
            "command": command,
            "shell": True,
            "description": f"Restarting in {delay_minutes} minutes" if delay_minutes > 0 else "Restarting now",
            "requires_confirmation": True
        }

    def _map_sleep(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map sleep intent"""
        if self.is_windows:
            command = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        elif self.is_linux:
            command = "systemctl suspend"
        else:  # macOS
            command = "pmset sleepnow"

        return {
            "command": command,
            "shell": True,
            "description": "Putting computer to sleep"
        }

    def _map_lock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map lock screen intent"""
        if self.is_windows:
            command = "rundll32.exe user32.dll,LockWorkStation"
        elif self.is_linux:
            command = "gnome-screensaver-command -l"
        else:  # macOS
            command = "pmset displaysleepnow"

        return {
            "command": command,
            "shell": True,
            "description": "Locking screen"
        }

    def _map_list_processes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map list processes intent"""
        if self.is_windows:
            command = "tasklist"
        else:
            command = "ps aux"

        return {
            "command": command,
            "shell": True,
            "description": "Listing running processes"
        }

    def _map_kill_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map kill process intent"""
        process_name = params.get("process_name", "")
        pid = params.get("pid")

        if self.is_windows:
            if pid:
                command = f"taskkill /F /PID {pid}"
            else:
                command = f"taskkill /F /IM {process_name}.exe"
        else:
            if pid:
                command = f"kill -9 {pid}"
            else:
                command = f"pkill -f {process_name}"

        return {
            "command": command,
            "shell": True,
            "description": f"Killing process {process_name or pid}",
            "requires_confirmation": True
        }

    def _map_disk_usage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map disk usage intent"""
        if self.is_windows:
            command = 'wmic logicaldisk get size,freespace,caption'
        else:
            command = 'df -h'

        return {
            "command": command,
            "shell": True,
            "description": "Getting disk usage"
        }

    def _map_create_folder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map create folder intent"""
        folder_name = params.get("folder_name", "")
        path = params.get("path", ".")

        full_path = f"{path}/{folder_name}" if path != "." else folder_name

        if self.is_windows:
            command = f'mkdir "{full_path}"'
        else:
            command = f'mkdir -p "{full_path}"'

        return {
            "command": command,
            "shell": True,
            "description": f"Creating folder {folder_name}"
        }

    def _map_delete_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map delete file intent"""
        file_path = params.get("file_path", "")

        if self.is_windows:
            command = f'del /F "{file_path}"'
        else:
            command = f'rm -f "{file_path}"'

        return {
            "command": command,
            "shell": True,
            "description": f"Deleting {file_path}",
            "requires_confirmation": True
        }
