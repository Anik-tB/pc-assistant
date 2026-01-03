"""
Memory Store
Stores command mappings and history in SQLite database
"""

import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
import time


class MemoryStore:
    """Stores command mappings and history"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize memory store"""
        self.config = config
        db_path = config.get("database", {}).get("path", "./data/commands.db")

        # Create data directory if needed
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.conn = None
        self._connect()
        self._init_tables()

    def _connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def _init_tables(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()

        # Command mappings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_phrase TEXT NOT NULL UNIQUE,
                command_template TEXT NOT NULL,
                description TEXT,
                created_date INTEGER NOT NULL
            )
        """)

        # Command history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                intent TEXT,
                executed_command TEXT,
                success BOOLEAN NOT NULL,
                output TEXT,
                error TEXT,
                timestamp INTEGER NOT NULL
            )
        """)

        self.conn.commit()

    def add_mapping(self, trigger: str, command: str, description: str = "") -> bool:
        """
        Add a custom command mapping

        Args:
            trigger: Trigger phrase
            command: Command template
            description: Optional description

        Returns:
            True if successful, False if duplicate
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO command_mappings (trigger_phrase, command_template, description, created_date) VALUES (?, ?, ?, ?)",
                (trigger, command, description, int(time.time()))
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_mapping(self, trigger: str) -> Optional[Dict[str, Any]]:
        """
        Get a command mapping by trigger

        Args:
            trigger: Trigger phrase

        Returns:
            Mapping dictionary or None
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM command_mappings WHERE trigger_phrase = ?",
            (trigger,)
        )
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def list_mappings(self) -> List[Dict[str, Any]]:
        """
        List all command mappings

        Returns:
            List of mapping dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM command_mappings ORDER BY created_date DESC")
        return [dict(row) for row in cursor.fetchall()]

    def delete_mapping(self, trigger: str) -> bool:
        """
        Delete a command mapping

        Args:
            trigger: Trigger phrase

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM command_mappings WHERE trigger_phrase = ?", (trigger,))
        self.conn.commit()
        return cursor.rowcount > 0

    def add_history(
        self,
        user_input: str,
        intent: str,
        executed_command: str,
        success: bool,
        output: str = "",
        error: str = ""
    ):
        """
        Add command to history

        Args:
            user_input: Original user input
            intent: Detected intent
            executed_command: Command that was executed
            success: Whether command succeeded
            output: Command output
            error: Error message if any
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO command_history
               (user_input, intent, executed_command, success, output, error, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_input, intent, executed_command, success, output, error, int(time.time()))
        )
        self.conn.commit()

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get command history

        Args:
            limit: Maximum number of records

        Returns:
            List of history dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM command_history ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
