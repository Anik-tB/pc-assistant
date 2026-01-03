#!/usr/bin/env python3
"""
Personal PC Automation Assistant
Main entry point for the application
"""

import sys
import os
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.command_processor import CommandProcessor
from modules.system_monitor import SystemMonitor
from utils.logger import setup_logger
from utils.helpers import load_config, display_banner

console = Console()
logger = setup_logger()


class PCAssistant:
    """Main PC Automation Assistant class"""

    def __init__(self, config_path="config.json"):
        """Initialize the assistant"""
        self.config = load_config(config_path)
        self.processor = CommandProcessor(self.config)
        self.system_monitor = SystemMonitor(self.config)
        self.running = True

        logger.info("PC Assistant initialized")

    def display_welcome(self):
        """Display welcome banner"""
        display_banner()

        # Show system status
        if self.config.get("ui", {}).get("show_system_stats", True):
            self.show_system_status()

    def show_system_status(self):
        """Display current system status"""
        stats = self.system_monitor.get_current_stats()

        table = Table(title="System Status", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("CPU Usage", f"{stats['cpu_percent']}%")
        table.add_row("RAM Usage", f"{stats['ram_percent']}% ({stats['ram_used_gb']:.1f} GB / {stats['ram_total_gb']:.1f} GB)")
        table.add_row("Disk Usage", f"{stats['disk_percent']}% ({stats['disk_free_gb']:.1f} GB free)")

        console.print(table)
        console.print()

    def process_command(self, user_input: str):
        """Process a single command"""
        if not user_input.strip():
            return

        # Handle special commands
        if user_input.lower() in ['exit', 'quit', 'bye']:
            console.print("[yellow]Goodbye! 👋[/yellow]")
            self.running = False
            return

        if user_input.lower() in ['help', '?']:
            self.show_help()
            return

        if user_input.lower() == 'status':
            self.show_system_status()
            return

        if user_input.lower() == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            return

        # Process command through AI
        try:
            with console.status("[bold green]Processing command...", spinner="dots"):
                result = self.processor.process(user_input)

            if result['success']:
                console.print(f"[green]✓[/green] {result['message']}")
                if result.get('output'):
                    console.print(Panel(result['output'], title="Output", border_style="blue"))
            else:
                console.print(f"[red]✗[/red] {result['message']}")
                if result.get('error'):
                    console.print(f"[dim]{result['error']}[/dim]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Command cancelled[/yellow]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            logger.error(f"Command processing error: {e}", exc_info=True)

    def show_help(self):
        """Display help information"""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]

[yellow]Application Control:[/yellow]
  • open <app>          - Open an application
  • close <app>         - Close an application
  • restart <app>       - Restart an application

[yellow]File Operations:[/yellow]
  • find <pattern>      - Search for files
  • create folder <name> - Create a new folder
  • delete <file>       - Delete a file/folder

[yellow]System Control:[/yellow]
  • shutdown [time]     - Shutdown computer
  • restart [time]      - Restart computer
  • sleep               - Put computer to sleep
  • lock                - Lock screen

[yellow]System Info:[/yellow]
  • status              - Show system status
  • list processes      - Show running processes
  • disk usage          - Show disk usage
  • ram usage           - Show memory usage

[yellow]Special Commands:[/yellow]
  • help, ?             - Show this help
  • status              - Show system status
  • clear               - Clear screen
  • exit, quit, bye     - Exit assistant

[dim]You can also use natural language like:
  "what's my disk usage"
  "kill chrome"
  "find all pdf files"[/dim]
        """
        console.print(Panel(help_text, title="Help", border_style="cyan"))

    def run_interactive(self):
        """Run in interactive mode"""
        self.display_welcome()

        while self.running:
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                self.process_command(user_input)
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except EOFError:
                break

        logger.info("PC Assistant stopped")

    def run_single_command(self, command: str):
        """Run a single command and exit"""
        self.process_command(command)


def main():
    """Main entry point"""
    # Check if config exists
    config_path = Path("config.json")
    if not config_path.exists():
        console.print("[red]Error:[/red] config.json not found!")
        console.print("[yellow]Please copy config.example.json to config.json and add your API key[/yellow]")
        sys.exit(1)

    # Initialize assistant
    try:
        assistant = PCAssistant()
    except Exception as e:
        console.print(f"[red]Failed to initialize assistant:[/red] {e}")
        logger.error(f"Initialization error: {e}", exc_info=True)
        sys.exit(1)

    # Check if command provided as argument
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        assistant.run_single_command(command)
    else:
        assistant.run_interactive()


if __name__ == "__main__":
    main()
