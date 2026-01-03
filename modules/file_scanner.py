"""
File Scanner
Searches for files across the file system
"""

import os
from pathlib import Path
from typing import List, Optional
import fnmatch


class FileScanner:
    """Scans and searches files"""

    def __init__(self, config: dict):
        """Initialize file scanner"""
        self.config = config
        self.max_results = config.get("file_scanner", {}).get("max_results", 1000)
        self.excluded_dirs = config.get("file_scanner", {}).get("excluded_dirs", [])

    def search(
        self,
        extension: Optional[str] = None,
        name_pattern: Optional[str] = None,
        search_path: Optional[str] = None,
        max_depth: Optional[int] = None
    ) -> List[str]:
        """
        Search for files

        Args:
            extension: File extension to search for (without dot)
            name_pattern: File name pattern (supports wildcards)
            search_path: Path to search in (default: user home)
            max_depth: Maximum directory depth

        Returns:
            List of file paths matching criteria
        """
        if not search_path:
            search_path = str(Path.home())

        results = []

        try:
            for root, dirs, files in os.walk(search_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

                # Check depth
                if max_depth:
                    depth = root[len(search_path):].count(os.sep)
                    if depth > max_depth:
                        continue

                for file in files:
                    # Check if we've hit max results
                    if len(results) >= self.max_results:
                        return results

                    # Check extension
                    if extension:
                        if not file.lower().endswith(f".{extension.lower()}"):
                            continue

                    # Check name pattern
                    if name_pattern:
                        if not fnmatch.fnmatch(file.lower(), f"*{name_pattern.lower()}*"):
                            continue

                    # Add to results
                    full_path = os.path.join(root, file)
                    results.append(full_path)

        except PermissionError:
            pass  # Skip directories we can't access
        except Exception as e:
            pass  # Skip other errors

        return results

    def get_file_info(self, file_path: str) -> dict:
        """
        Get information about a file

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file information
        """
        try:
            stat = os.stat(file_path)
            return {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size_bytes": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "is_file": os.path.isfile(file_path),
                "is_dir": os.path.isdir(file_path)
            }
        except Exception as e:
            return {"error": str(e)}
