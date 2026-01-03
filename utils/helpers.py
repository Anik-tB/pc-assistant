"""
Helper Functions
Utility functions for the PC Assistant
"""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def load_config(config_path: str = "config.json") -> dict:
    """
    Load configuration from JSON file

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Config file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON in config file: {e}")
        raise


def save_config(config: dict, config_path: str = "config.json"):
    """
    Save configuration to JSON file

    Args:
        config: Configuration dictionary
        config_path: Path to config file
    """
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def display_banner():
    """Display welcome banner"""
    banner_text = Text()
    banner_text.append("🤖 Personal PC Automation Assistant\n", style="bold cyan")
    banner_text.append("Powered by AI • Type 'help' for commands • 'exit' to quit", style="dim")

    console.print(Panel(banner_text, border_style="cyan", padding=(1, 2)))
    console.print()


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def is_dangerous_command(command: str) -> bool:
    """
    Check if command is potentially dangerous

    Args:
        command: Command string

    Returns:
        True if dangerous, False otherwise
    """
    dangerous_keywords = [
        'shutdown', 'reboot', 'restart', 'delete', 'rm ', 'del ',
        'format', 'kill', 'taskkill', 'pkill', 'rmdir', 'rd '
    ]

    command_lower = command.lower()
    return any(keyword in command_lower for keyword in dangerous_keywords)
