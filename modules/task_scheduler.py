"""
Task Scheduler Module
Advanced task scheduling with cron-like syntax
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path


class TaskScheduler:
    """Advanced task scheduler with cron support"""

    def __init__(self, db_path: str = "./data/scheduler.db"):
        """Initialize task scheduler"""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        self._init_database()
        self._load_tasks()

    def _init_database(self):
        """Initialize scheduler database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                command TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                schedule_value TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                last_run INTEGER,
                next_run INTEGER,
                run_count INTEGER DEFAULT 0,
                created_at INTEGER NOT NULL,
                description TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                executed_at INTEGER NOT NULL,
                success BOOLEAN NOT NULL,
                output TEXT,
                error TEXT,
                duration_ms INTEGER,
                FOREIGN KEY (task_id) REFERENCES scheduled_tasks(id)
            )
        """)

        conn.commit()
        conn.close()

    def _load_tasks(self):
        """Load tasks from database and schedule them"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scheduled_tasks WHERE enabled = 1")
        tasks = cursor.fetchall()

        for task in tasks:
            self._schedule_task(dict(task))

        conn.close()

    def _schedule_task(self, task: Dict[str, Any]):
        """Schedule a task with APScheduler"""
        task_id = task['id']
        schedule_type = task['schedule_type']
        schedule_value = task['schedule_value']

        if schedule_type == 'cron':
            # Parse cron expression
            trigger = CronTrigger.from_crontab(schedule_value)
        elif schedule_type == 'interval':
            # Interval in seconds
            trigger = IntervalTrigger(seconds=int(schedule_value))
        elif schedule_type == 'once':
            # One-time execution at specific datetime
            trigger = DateTrigger(run_date=datetime.fromtimestamp(int(schedule_value)))
        else:
            return

        self.scheduler.add_job(
            func=self._execute_task,
            trigger=trigger,
            args=[task_id, task['command']],
            id=f"task_{task_id}",
            replace_existing=True
        )

    def _execute_task(self, task_id: int, command: str):
        """Execute a scheduled task"""
        from modules.command_processor import CommandProcessor
        from utils.helpers import load_config

        start_time = datetime.now()

        try:
            # Execute command
            config = load_config()
            processor = CommandProcessor(config)
            result = processor.process(command)

            success = result.get('success', False)
            output = result.get('output', '')
            error = result.get('error', '')

        except Exception as e:
            success = False
            output = ''
            error = str(e)

        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Log execution
        self._log_execution(task_id, success, output, error, duration_ms)

        # Update task stats
        self._update_task_stats(task_id)

    def _log_execution(self, task_id: int, success: bool, output: str, error: str, duration_ms: int):
        """Log task execution to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO task_history (task_id, executed_at, success, output, error, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task_id, int(datetime.now().timestamp()), success, output, error, duration_ms))

        conn.commit()
        conn.close()

    def _update_task_stats(self, task_id: int):
        """Update task statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = int(datetime.now().timestamp())
        cursor.execute("""
            UPDATE scheduled_tasks
            SET last_run = ?, run_count = run_count + 1
            WHERE id = ?
        """, (now, task_id))

        conn.commit()
        conn.close()

    def add_task(
        self,
        name: str,
        command: str,
        schedule_type: str,
        schedule_value: str,
        description: str = ""
    ) -> int:
        """
        Add a new scheduled task

        Args:
            name: Unique task name
            command: Command to execute
            schedule_type: 'cron', 'interval', or 'once'
            schedule_value: Cron expression, interval in seconds, or timestamp
            description: Optional description

        Returns:
            Task ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO scheduled_tasks (name, command, schedule_type, schedule_value, created_at, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, command, schedule_type, schedule_value, int(datetime.now().timestamp()), description))

            task_id = cursor.lastrowid
            conn.commit()

            # Schedule the task
            task = {
                'id': task_id,
                'name': name,
                'command': command,
                'schedule_type': schedule_type,
                'schedule_value': schedule_value
            }
            self._schedule_task(task)

            return task_id

        except sqlite3.IntegrityError:
            raise ValueError(f"Task with name '{name}' already exists")
        finally:
            conn.close()

    def remove_task(self, task_id: int) -> bool:
        """Remove a scheduled task"""
        # Remove from scheduler
        try:
            self.scheduler.remove_job(f"task_{task_id}")
        except:
            pass

        # Remove from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scheduled_tasks WHERE id = ?", (task_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    def enable_task(self, task_id: int):
        """Enable a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE scheduled_tasks SET enabled = 1 WHERE id = ?", (task_id,))
        conn.commit()

        # Get task and schedule it
        cursor.execute("SELECT * FROM scheduled_tasks WHERE id = ?", (task_id,))
        task = dict(cursor.fetchone())
        conn.close()

        self._schedule_task(task)

    def disable_task(self, task_id: int):
        """Disable a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE scheduled_tasks SET enabled = 0 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        # Remove from scheduler
        try:
            self.scheduler.remove_job(f"task_{task_id}")
        except:
            pass

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all scheduled tasks"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scheduled_tasks ORDER BY created_at DESC")
        tasks = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return tasks

    def get_task_history(self, task_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history for a task"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM task_history
            WHERE task_id = ?
            ORDER BY executed_at DESC
            LIMIT ?
        """, (task_id, limit))

        history = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return history

    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()


# Example usage
if __name__ == "__main__":
    scheduler = TaskScheduler()

    # Add a daily task at 2 AM
    scheduler.add_task(
        name="Daily Cleanup",
        command="clean temp files",
        schedule_type="cron",
        schedule_value="0 2 * * *",
        description="Clean temporary files daily"
    )

    # Add an interval task (every 5 minutes)
    scheduler.add_task(
        name="System Check",
        command="status",
        schedule_type="interval",
        schedule_value="300",  # 300 seconds = 5 minutes
        description="Check system status every 5 minutes"
    )

    print("Scheduler started. Tasks:", scheduler.list_tasks())
