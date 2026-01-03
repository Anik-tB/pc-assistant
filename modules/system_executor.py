"""
System Executor
Safely executes system commands with timeout and error handling
"""

import subprocess
import platform
from typing import Dict, Any, Optional, List
import shlex


class SystemExecutor:
    """Executes system commands safely"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize system executor"""
        self.config = config
        self.timeout = config.get("command", {}).get("timeout_seconds", 30)
        self.is_windows = platform.system().lower() == "windows"

    def execute(self, command: str, shell: bool = True) -> Dict[str, Any]:
        """
        Execute a system command

        Args:
            command: Command to execute
            shell: Whether to use shell execution

        Returns:
            Dictionary with success, output, error, and exit_code
        """
        try:
            # Execute command
            if shell:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    encoding='utf-8' if self.is_windows else None,
                    errors='replace'
                )
            else:
                # Split command for non-shell execution
                if self.is_windows:
                    cmd_parts = command.split()
                else:
                    cmd_parts = shlex.split(command)

                result = subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    encoding='utf-8' if self.is_windows else None,
                    errors='replace'
                )

            # Combine stdout and stderr
            output = result.stdout
            if result.stderr:
                output += f"\n{result.stderr}"

            return {
                "success": result.returncode == 0,
                "output": output.strip() if output else "",
                "error": result.stderr.strip() if result.stderr else "",
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after {self.timeout} seconds",
                "exit_code": -1
            }

        except FileNotFoundError as e:
            return {
                "success": False,
                "output": "",
                "error": f"Command not found: {e}",
                "exit_code": -1
            }

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "exit_code": -1
            }

    def execute_async(self, command: str) -> subprocess.Popen:
        """
        Execute command asynchronously (non-blocking)

        Args:
            command: Command to execute

        Returns:
            Popen process object
        """
        return subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input to prevent command injection

        Args:
            user_input: Raw user input

        Returns:
            Sanitized input
        """
        # Remove dangerous characters
        dangerous_chars = [';', '&&', '||', '|', '>', '<', '`', '$', '(', ')']
        sanitized = user_input

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        return sanitized.strip()
