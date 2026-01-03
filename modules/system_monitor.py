"""
System Monitor
Monitors system resources (CPU, RAM, Disk)
"""

import psutil
from typing import Dict, Any
import threading
import time


class SystemMonitor:
    """Monitors system resources"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize system monitor"""
        self.config = config
        self.current_stats = {}
        self.monitoring = False
        self.monitor_thread = None

        # Get initial stats
        self._update_stats()

        # Start background monitoring if enabled
        if config.get("monitoring", {}).get("enable_background", False):
            self.start_monitoring()

    def _update_stats(self):
        """Update current system statistics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # RAM
        ram = psutil.virtual_memory()

        # Disk
        disk = psutil.disk_usage('/')

        self.current_stats = {
            'cpu_percent': cpu_percent,
            'ram_total_gb': ram.total / (1024 ** 3),
            'ram_used_gb': ram.used / (1024 ** 3),
            'ram_available_gb': ram.available / (1024 ** 3),
            'ram_percent': ram.percent,
            'disk_total_gb': disk.total / (1024 ** 3),
            'disk_used_gb': disk.used / (1024 ** 3),
            'disk_free_gb': disk.free / (1024 ** 3),
            'disk_percent': disk.percent
        }

    def get_current_stats(self) -> Dict[str, Any]:
        """
        Get current system statistics

        Returns:
            Dictionary with CPU, RAM, and disk stats
        """
        self._update_stats()
        return self.current_stats.copy()

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)

    def get_ram_usage(self) -> Dict[str, Any]:
        """Get RAM usage information"""
        ram = psutil.virtual_memory()
        return {
            'total_gb': ram.total / (1024 ** 3),
            'used_gb': ram.used / (1024 ** 3),
            'available_gb': ram.available / (1024 ** 3),
            'percent': ram.percent
        }

    def get_disk_usage(self, path: str = '/') -> Dict[str, Any]:
        """Get disk usage information"""
        disk = psutil.disk_usage(path)
        return {
            'total_gb': disk.total / (1024 ** 3),
            'used_gb': disk.used / (1024 ** 3),
            'free_gb': disk.free / (1024 ** 3),
            'percent': disk.percent
        }

    def get_battery_info(self) -> Dict[str, Any]:
        """Get battery information (if available)"""
        battery = psutil.sensors_battery()
        if battery:
            return {
                'percent': battery.percent,
                'plugged_in': battery.power_plugged,
                'time_left_seconds': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
            }
        return {'available': False}

    def _monitor_loop(self):
        """Background monitoring loop"""
        interval = self.config.get("monitoring", {}).get("interval_seconds", 5)

        while self.monitoring:
            self._update_stats()
            time.sleep(interval)

    def start_monitoring(self):
        """Start background monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
