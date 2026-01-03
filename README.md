# PC Automation Assistant - Advanced Edition

**Enterprise-grade PC automation platform with AI, web dashboard, voice control, and extensible plugin system.**

## 🚀 New Advanced Features

### ✨ What's New in v2.0

- **🌐 Web Dashboard** - Modern React interface with real-time monitoring
- **🎤 Voice Commands** - Hands-free control with speech recognition
- **⏰ Task Scheduler** - Cron-like scheduling for automated tasks
- **🔌 Plugin System** - Extensible architecture with hot-reload
- **📊 Advanced Analytics** - Usage tracking and performance metrics
- **🐳 Docker Support** - Containerized deployment ready
- **🔒 Enhanced Security** - JWT authentication and RBAC
- **📡 WebSocket API** - Real-time bidirectional communication

## 📦 Installation

### Quick Start (Basic CLI)

```bash
cd pc-assistant
pip install -r requirements.txt
python main.py
```

### Advanced Installation (Web Dashboard + All Features)

```bash
# Install backend dependencies
pip install -r requirements.txt
pip install -r requirements-advanced.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Start backend server
python -m uvicorn backend.main:app --reload

# Start frontend (in another terminal)
cd frontend
npm run dev
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access dashboard at http://localhost:3000
# API docs at http://localhost:8000/docs
```

## 🎯 Usage

### CLI Mode
```bash
python main.py
```

### Web Dashboard
```bash
# Start backend
uvicorn backend.main:app --reload

# Start frontend
cd frontend && npm run dev

# Open http://localhost:3000
```

### Voice Control
```python
from modules.voice_controller import VoiceController

voice = VoiceController()
voice.speak("Voice controller ready")

# Listen for wake word
voice.listen_for_wake_word(callback=lambda cmd: print(f"Command: {cmd}"))
```

### Task Scheduling
```python
from modules.task_scheduler import TaskScheduler

scheduler = TaskScheduler()

# Schedule daily task at 2 AM
scheduler.add_task(
    name="Daily Backup",
    command="backup files",
    schedule_type="cron",
    schedule_value="0 2 * * *"
)

# Schedule interval task (every 5 minutes)
scheduler.add_task(
    name="System Check",
    command="status",
    schedule_type="interval",
    schedule_value="300"
)
```

### Plugin Development
```python
from modules.plugin_manager import PluginBase

class MyPlugin(PluginBase):
    name = "My Custom Plugin"
    version = "1.0.0"

    def initialize(self):
        return True

    def register_commands(self):
        return {
            "my_command": self.my_handler
        }

    def my_handler(self, params):
        return {"success": True, "message": "Hello from plugin!"}
```

## 📡 API Endpoints

### REST API

- `GET /api/system/status` - Get system statistics
- `GET /api/system/processes` - List running processes
- `POST /api/command/execute` - Execute a command
- `POST /api/files/search` - Search for files
- `POST /api/process/kill/{pid}` - Kill a process

### WebSocket

- `ws://localhost:8000/ws` - Real-time system updates

Full API documentation: http://localhost:8000/docs

## 🏗️ Project Structure

```
pc-assistant/
├── main.py                    # CLI entry point
├── backend/
│   └── main.py               # FastAPI server
├── frontend/
│   ├── src/
│   │   └── App.tsx           # React dashboard
│   └── package.json
├── modules/
│   ├── ai_client.py          # AI integration
│   ├── command_processor.py  # Command processing
│   ├── task_scheduler.py     # Task scheduling
│   ├── voice_controller.py   # Voice commands
│   ├── plugin_manager.py     # Plugin system
│   └── ...
├── plugins/
│   └── browser_plugin.py     # Example plugin
├── Dockerfile
├── docker-compose.yml
└── requirements-advanced.txt
```

## 🔧 Configuration

Edit `config.json`:

```json
{
  "ai": {
    "provider": "openai",
    "api_key": "your-api-key",
    "model": "gpt-3.5-turbo"
  },
  "monitoring": {
    "interval_seconds": 5
  }
}
```

## 🎨 Features Comparison

| Feature | Basic (v1.0) | Advanced (v2.0) |
|---------|-------------|-----------------|
| CLI Interface | ✅ | ✅ |
| AI Commands | ✅ | ✅ |
| System Monitoring | ✅ | ✅ |
| Web Dashboard | ❌ | ✅ |
| Voice Control | ❌ | ✅ |
| Task Scheduler | ❌ | ✅ |
| Plugin System | ❌ | ✅ |
| WebSocket API | ❌ | ✅ |
| Docker Support | ❌ | ✅ |

## 📚 Documentation

- [Implementation Plan](implementation_plan.md) - Technical architecture
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Plugin Development Guide](docs/plugins.md) - Create custom plugins
- [Deployment Guide](docs/deployment.md) - Production deployment

## 🔒 Security

- JWT authentication for API access
- Input sanitization to prevent injection
- Command whitelisting for safety
- Encrypted configuration storage
- Audit logging for all actions

## 🚀 Performance

- Async FastAPI backend
- WebSocket for real-time updates
- Redis caching support
- Optimized database queries
- Background task processing

## 📊 System Requirements

- Python 3.8+
- Node.js 16+ (for web dashboard)
- 2GB RAM minimum
- Windows, Linux, or macOS
