"""
Command Processor
Handles the agentic recursive thought loop to process commands
"""

from typing import Dict, Any
from rich.prompt import Confirm
import json

from .ai_client import AIClient
from .command_mapper import CommandMapper
from .system_executor import SystemExecutor
from .file_scanner import FileScanner
from .process_monitor import ProcessMonitor
from .system_monitor import SystemMonitor
from .plugin_manager import PluginManager

class CommandProcessor:
    """Main command processor using Agentic Loop"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ai_client = AIClient(config)
        self.mapper = CommandMapper()
        self.executor = SystemExecutor(config)
        self.file_scanner = FileScanner(config)
        self.process_monitor = ProcessMonitor()
        self.system_monitor = SystemMonitor(config)
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_all_plugins()

    def _get_available_tools(self) -> Dict[str, str]:
        """Get all available tools for the AI"""
        tools = {
            "system_info": "Get CPU, RAM, Disk usage. Params: type ('all', 'disk', 'ram', 'cpu')",
            "list_processes": "List top running processes and their PIDs",
            "find_files": "Search for files. Params: extension, name, path",
            "open_app": "Open an application. Params: app_name",
            "close_app": "Close an application. Params: app_name",
            "shutdown": "Shutdown PC. Params: delay_minutes",
            "restart": "Restart PC. Params: delay_minutes",
            "sleep": "Put PC to sleep",
            "lock": "Lock PC screen",
            "kill_process": "Kill a process. Params: process_name, pid"
        }
        
        # Add plugin commands
        for cmd_name, plugin_name in self.plugin_manager.list_commands().items():
            tools[cmd_name] = f"Command from {plugin_name} plugin"
            
        return tools

    def process(self, user_input: str) -> Dict[str, Any]:
        """Process a user command using an agentic loop"""
        available_tools = self._get_available_tools()
        messages = [{"role": "user", "content": user_input}]
        
        max_steps = 10
        
        for step in range(max_steps):
            # Get next action from AI
            response = self.ai_client.get_agent_response(messages, available_tools)
            
            action = response.get("action")
            
            if action == "final_answer":
                return {
                    "success": True,
                    "message": response.get("text", "Done."),
                    "output": response.get("text", "")
                }
                
            elif action == "tool_call":
                cmd = response.get("command_name")
                params = response.get("parameters", {})
                
                # Execute tool
                result = self._execute_tool(cmd, params)
                
                # Update history
                messages.append({"role": "assistant", "content": json.dumps(response)})
                messages.append({"role": "user", "content": f"Tool '{cmd}' returned: {json.dumps(result)}"})
                
            else:
                return {
                    "success": False,
                    "message": f"AI returned unknown action: {action}"
                }
                
        return {
            "success": False,
            "message": "AI reached maximum steps without finding an answer."
        }

    def _execute_tool(self, cmd: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool and return result"""
        
        # 1. Native System Modules
        if cmd == "system_info":
            stats = self.system_monitor.get_current_stats()
            return {"success": True, "data": stats}
            
        elif cmd == "list_processes":
            procs = self.process_monitor.list_processes()
            top = sorted(procs, key=lambda p: p.get('memory_mb', 0), reverse=True)[:10]
            return {"success": True, "data": top}
            
        elif cmd == "find_files":
            results = self.file_scanner.search(
                extension=params.get("extension"),
                name_pattern=params.get("name"),
                search_path=params.get("path")
            )
            return {"success": True, "files": results[:20]}
            
        # 2. Plugin Commands
        elif cmd in self.plugin_manager.commands:
            try:
                res = self.plugin_manager.execute_command(cmd, params)
                if isinstance(res, dict): return res
                return {"success": True, "output": str(res)}
            except Exception as e:
                return {"success": False, "error": str(e)}
                
        # 3. OS Mapped Commands
        else:
            mapped = self.mapper.map_intent_to_command(cmd, params)
            if not mapped or "error" in mapped:
                return {"success": False, "error": f"Tool '{cmd}' not found or mapping failed."}
                
            command_str = mapped.get("command")
            if mapped.get("requires_confirmation"):
                if not Confirm.ask(f"[yellow]⚠️  {mapped.get('description')}. Continue?[/yellow]"):
                    return {"success": False, "error": "User denied permission."}
                    
            return self.executor.execute(command_str, shell=mapped.get("shell", True))
