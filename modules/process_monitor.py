"""
Process Monitor
Monitors and manages system processes
"""

import psutil
from typing import List, Dict, Any, Optional


class ProcessMonitor:
    """Monitors system processes"""

    def __init__(self):
        """Initialize process monitor"""
        pass

    def list_processes(self) -> List[Dict[str, Any]]:
        """
        List all running processes

        Returns:
            List of process dictionaries
        """
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'memory_mb': info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0,
                    'cpu_percent': info['cpu_percent'] or 0.0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    def find_process(self, name: str) -> List[Dict[str, Any]]:
        """
        Find processes by name

        Args:
            name: Process name to search for

        Returns:
            List of matching processes
        """
        matching = []

        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                if name.lower() in proc.info['name'].lower():
                    info = proc.info
                    matching.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'memory_mb': info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0,
                        'cpu_percent': info['cpu_percent'] or 0.0
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return matching

    def kill_process(self, pid: int) -> bool:
        """
        Kill a process by PID

        Args:
            pid: Process ID

        Returns:
            True if successful, False otherwise
        """
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=3)
            return True
        except psutil.NoSuchProcess:
            return False
        except psutil.AccessDenied:
            try:
                proc.kill()
                return True
            except:
                return False
        except Exception:
            return False

    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a process

        Args:
            pid: Process ID

        Returns:
            Process information dictionary or None
        """
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_mb': proc.memory_info().rss / (1024 * 1024),
                'num_threads': proc.num_threads(),
                'create_time': proc.create_time()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
