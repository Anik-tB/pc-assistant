"""
FastAPI Backend Server
Main entry point for the web API
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime

# Import our existing modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.command_processor import CommandProcessor
from modules.system_monitor import SystemMonitor
from modules.process_monitor import ProcessMonitor
from modules.file_scanner import FileScanner
from utils.helpers import load_config

# Initialize FastAPI app
app = FastAPI(
    title="PC Automation Assistant API",
    description="Advanced PC automation and control API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
config_path = Path(__file__).parent.parent / "config.json"
config = load_config(str(config_path))

# Initialize modules
command_processor = CommandProcessor(config)
system_monitor = SystemMonitor(config)
process_monitor = ProcessMonitor()
file_scanner = FileScanner(config)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Routes

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "PC Automation Assistant API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/api/system/status")
async def get_system_status():
    """Get current system status"""
    stats = system_monitor.get_current_stats()
    return {
        "success": True,
        "data": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/system/processes")
async def get_processes():
    """Get list of running processes"""
    processes = process_monitor.list_processes()
    # Sort by memory usage
    processes.sort(key=lambda p: p.get('memory_mb', 0), reverse=True)
    return {
        "success": True,
        "data": processes[:50],  # Top 50 processes
        "total": len(processes)
    }

@app.post("/api/command/execute")
async def execute_command(command: dict):
    """Execute a command"""
    try:
        user_input = command.get("input", "")
        if not user_input:
            raise HTTPException(status_code=400, detail="No command provided")

        result = command_processor.process(user_input)

        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "command_executed",
            "command": user_input,
            "result": result
        })

        return {
            "success": result.get("success", False),
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/files/search")
async def search_files(search: dict):
    """Search for files"""
    try:
        extension = search.get("extension")
        name = search.get("name")
        path = search.get("path")

        results = file_scanner.search(
            extension=extension,
            name_pattern=name,
            search_path=path
        )

        return {
            "success": True,
            "data": results[:100],  # Limit to 100 results
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/kill/{pid}")
async def kill_process(pid: int):
    """Kill a process by PID"""
    try:
        success = process_monitor.kill_process(pid)
        return {
            "success": success,
            "message": f"Process {pid} terminated" if success else f"Failed to terminate process {pid}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send initial system status
        stats = system_monitor.get_current_stats()
        await websocket.send_json({
            "type": "system_status",
            "data": stats
        })

        # Keep connection alive and send periodic updates
        while True:
            try:
                # Receive messages from client
                data = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except asyncio.TimeoutError:
                # Send periodic system updates
                stats = system_monitor.get_current_stats()
                await websocket.send_json({
                    "type": "system_status",
                    "data": stats
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Background task for broadcasting system stats
async def broadcast_system_stats():
    """Periodically broadcast system stats to all connected clients"""
    while True:
        await asyncio.sleep(5)  # Every 5 seconds
        stats = system_monitor.get_current_stats()
        await manager.broadcast({
            "type": "system_status",
            "data": stats
        })

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    # Start background tasks
    asyncio.create_task(broadcast_system_stats())
    print("🚀 PC Automation Assistant API started")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws")
    print("📚 API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
