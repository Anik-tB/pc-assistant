"""
Command Processor
Main command processing logic that coordinates AI, mapping, and execution
"""

from typing import Dict, Any
from rich.prompt import Confirm
from .ai_client import AIClient
from .command_mapper import CommandMapper
from .system_executor import SystemExecutor
from .file_scanner import FileScanner
from .process_monitor import ProcessMonitor
from .system_monitor import SystemMonitor
from .plugin_manager import PluginManager

class CommandProcessor:
    """Main command processor"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize command processor"""
        self.config = config
        self.ai_client = AIClient(config)
        self.mapper = CommandMapper()
        self.executor = SystemExecutor(config)
        self.file_scanner = FileScanner(config)
        self.process_monitor = ProcessMonitor()
        self.system_monitor = SystemMonitor(config)
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_all_plugins()

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user command

        Args:
            user_input: Natural language command from user

        Returns:
            Dictionary with success, message, and output
        """
        # Get intent from AI
        intent_data = self.ai_client.get_intent(user_input)

        if "error" in intent_data:
            return {
                "success": False,
                "message": "Failed to understand command",
                "error": intent_data["error"]
            }

        intent = intent_data.get("intent")
        parameters = intent_data.get("parameters", {})
        confidence = intent_data.get("confidence", 0.0)

        # Check confidence
        if confidence < 0.5:
            return {
                "success": False,
                "message": "I'm not confident I understood that command correctly. Please rephrase.",
                "confidence": confidence
            }

        # Handle special intents that don't need system commands
        if intent == "system_info":
            return self._handle_system_info(parameters)

        if intent == "list_processes":
            return self._handle_list_processes()

        if intent == "find_files":
            return self._handle_find_files(parameters)

        if intent == "plugin_command":
            return self._handle_plugin_command(parameters)

        # Map intent to system command
        command_data = self.mapper.map_intent_to_command(intent, parameters)

        if not command_data or "error" in command_data:
            return {
                "success": False,
                "message": command_data.get("error", "Failed to map command"),
                "intent": intent
            }

        command = command_data.get("command")
        description = command_data.get("description", "Executing command")
        requires_confirmation = command_data.get("requires_confirmation", False)

        # Check if confirmation needed
        if requires_confirmation:
            if not Confirm.ask(f"[yellow]⚠️  {description}. Continue?[/yellow]"):
                return {
                    "success": False,
                    "message": "Command cancelled by user"
                }

        # Execute command
        result = self.executor.execute(command, shell=command_data.get("shell", True))

        if result["success"]:
            return {
                "success": True,
                "message": description,
                "output": result["output"]
            }
        else:
            return {
                "success": False,
                "message": f"Command failed: {description}",
                "error": result["error"],
                "output": result["output"]
            }

    def _handle_system_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system info requests"""
        info_type = parameters.get("type", "all")
        stats = self.system_monitor.get_current_stats()

        if info_type == "disk" or "disk" in info_type:
            output = f"Disk Usage: {stats['disk_percent']}%\n"
            output += f"Free Space: {stats['disk_free_gb']:.1f} GB\n"
            output += f"Total Space: {stats['disk_total_gb']:.1f} GB"

        elif info_type == "ram" or "memory" in info_type:
            output = f"RAM Usage: {stats['ram_percent']}%\n"
            output += f"Used: {stats['ram_used_gb']:.1f} GB\n"
            output += f"Total: {stats['ram_total_gb']:.1f} GB"

        elif info_type == "cpu":
            output = f"CPU Usage: {stats['cpu_percent']}%"

        else:
            output = f"CPU: {stats['cpu_percent']}%\n"
            output += f"RAM: {stats['ram_percent']}% ({stats['ram_used_gb']:.1f}/{stats['ram_total_gb']:.1f} GB)\n"
            output += f"Disk: {stats['disk_percent']}% ({stats['disk_free_gb']:.1f} GB free)"

        return {
            "success": True,
            "message": "System information",
            "output": output
        }

    def _handle_list_processes(self) -> Dict[str, Any]:
        """Handle list processes request"""
        processes = self.process_monitor.list_processes()

        # Format top processes by memory
        top_processes = sorted(processes, key=lambda p: p.get('memory_mb', 0), reverse=True)[:10]

        output = "Top 10 Processes by Memory:\n\n"
        output += f"{'PID':<8} {'Name':<30} {'Memory (MB)':<12} {'CPU %':<8}\n"
        output += "-" * 70 + "\n"

        for proc in top_processes:
            output += f"{proc['pid']:<8} {proc['name'][:29]:<30} {proc['memory_mb']:<12.1f} {proc['cpu_percent']:<8.1f}\n"

        return {
            "success": True,
            "message": f"Found {len(processes)} running processes",
            "output": output
        }

    def _handle_find_files(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file search request"""
        extension = parameters.get("extension")
        name = parameters.get("name")
        path = parameters.get("path")

        results = self.file_scanner.search(
            extension=extension,
            name_pattern=name,
            search_path=path
        )

        if not results:
            return {
                "success": True,
                "message": "No files found matching criteria",
                "output": ""
            }

        # Limit results
        max_results = 50
        limited_results = results[:max_results]

        output = f"Found {len(results)} files"
        if len(results) > max_results:
            output += f" (showing first {max_results})"
        output += ":\n\n"

        for file_path in limited_results:
            output += f"{file_path}\n"

        return {
            "success": True,
            "message": f"Found {len(results)} files",
            "output": output
        }

    def _handle_plugin_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle plugin command requests"""
        command_name = parameters.get("command_name")
        if not command_name:
            return {
                "success": False,
                "message": "No command name specified for plugin"
            }
        
        try:
            result = self.plugin_manager.execute_command(command_name, parameters)
            
            # If the plugin returned a dict, extract its fields
            if isinstance(result, dict):
                return {
                    "success": result.get("success", True),
                    "message": result.get("message", "Plugin command executed"),
                    "output": result.get("output", result.get("error", ""))
                }
            
            # If it returned something else, just stringify it
            return {
                "success": True,
                "message": "Plugin command executed",
                "output": str(result)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Plugin error: {str(e)}",
                "error": str(e)
            }

