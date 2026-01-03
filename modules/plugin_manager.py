"""
Plugin System Base
Base class and manager for extensible plugins
"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod


class PluginBase(ABC):
    """Base class for all plugins"""

    # Plugin metadata (override in subclass)
    name: str = "Unknown Plugin"
    version: str = "1.0.0"
    author: str = "Unknown"
    description: str = ""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize plugin"""
        self.config = config or {}
        self.enabled = True

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def register_commands(self) -> Dict[str, callable]:
        """
        Register plugin commands

        Returns:
            Dictionary mapping command names to handler functions
        """
        pass

    def shutdown(self):
        """Cleanup when plugin is unloaded"""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "enabled": self.enabled
        }


class PluginManager:
    """Manages plugin loading, unloading, and execution"""

    def __init__(self, plugin_dir: str = "./plugins"):
        """Initialize plugin manager"""
        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(exist_ok=True)

        self.plugins: Dict[str, PluginBase] = {}
        self.commands: Dict[str, tuple] = {}  # command_name -> (plugin_name, handler)

        # Add plugin directory to Python path
        sys.path.insert(0, str(self.plugin_dir))

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directory

        Returns:
            List of plugin module names
        """
        plugin_files = []

        for file in self.plugin_dir.glob("*_plugin.py"):
            plugin_files.append(file.stem)

        return plugin_files

    def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """
        Load a plugin by name

        Args:
            plugin_name: Name of the plugin module
            config: Optional configuration for the plugin

        Returns:
            True if loaded successfully
        """
        try:
            # Import the plugin module
            module = importlib.import_module(plugin_name)

            # Find the plugin class (subclass of PluginBase)
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                    plugin_class = obj
                    break

            if not plugin_class:
                print(f"❌ No plugin class found in {plugin_name}")
                return False

            # Instantiate the plugin
            plugin = plugin_class(config)

            # Initialize the plugin
            if not plugin.initialize():
                print(f"❌ Failed to initialize plugin: {plugin.name}")
                return False

            # Register plugin commands
            commands = plugin.register_commands()
            for cmd_name, handler in commands.items():
                self.commands[cmd_name] = (plugin.name, handler)

            # Store plugin
            self.plugins[plugin.name] = plugin

            print(f"✅ Loaded plugin: {plugin.name} v{plugin.version}")
            return True

        except Exception as e:
            print(f"❌ Error loading plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if unloaded successfully
        """
        if plugin_name not in self.plugins:
            return False

        plugin = self.plugins[plugin_name]

        # Remove plugin commands
        self.commands = {
            cmd: (pname, handler)
            for cmd, (pname, handler) in self.commands.items()
            if pname != plugin_name
        }

        # Shutdown plugin
        plugin.shutdown()

        # Remove plugin
        del self.plugins[plugin_name]

        print(f"✅ Unloaded plugin: {plugin_name}")
        return True

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin (unload and load again)

        Args:
            plugin_name: Name of the plugin to reload

        Returns:
            True if reloaded successfully
        """
        # Get config before unloading
        config = None
        if plugin_name in self.plugins:
            config = self.plugins[plugin_name].config
            self.unload_plugin(plugin_name)

        # Find module name
        module_name = None
        for file in self.plugin_dir.glob("*_plugin.py"):
            module = importlib.import_module(file.stem)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                    if obj.name == plugin_name:
                        module_name = file.stem
                        break

        if module_name:
            # Reload module
            importlib.reload(sys.modules[module_name])
            return self.load_plugin(module_name, config)

        return False

    def execute_command(self, command_name: str, params: Dict[str, Any] = None) -> Any:
        """
        Execute a plugin command

        Args:
            command_name: Name of the command
            params: Parameters for the command

        Returns:
            Command result
        """
        if command_name not in self.commands:
            raise ValueError(f"Unknown command: {command_name}")

        plugin_name, handler = self.commands[command_name]

        try:
            return handler(params or {})
        except Exception as e:
            raise RuntimeError(f"Error executing {command_name} from {plugin_name}: {e}")

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins"""
        return [plugin.get_info() for plugin in self.plugins.values()]

    def list_commands(self) -> Dict[str, str]:
        """List all registered commands"""
        return {
            cmd: plugin_name
            for cmd, (plugin_name, _) in self.commands.items()
        }

    def load_all_plugins(self):
        """Discover and load all available plugins"""
        plugin_names = self.discover_plugins()

        for plugin_name in plugin_names:
            self.load_plugin(plugin_name)

        print(f"✅ Loaded {len(self.plugins)} plugins")


# Example usage
if __name__ == "__main__":
    manager = PluginManager()

    # Discover and load all plugins
    manager.load_all_plugins()

    # List loaded plugins
    print("\nLoaded plugins:")
    for plugin in manager.list_plugins():
        print(f"  - {plugin['name']} v{plugin['version']} by {plugin['author']}")

    # List available commands
    print("\nAvailable commands:")
    for cmd, plugin in manager.list_commands().items():
        print(f"  - {cmd} (from {plugin})")
