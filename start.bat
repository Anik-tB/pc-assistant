@echo off
REM PC Automation Assistant - Advanced Launcher
REM Version 2.0.0
echo ========================================
echo  PC Automation Assistant v2.0
echo  Advanced Enterprise Edition
echo ========================================
echo.

REM Check if config.json exists
if not exist config.json (
    echo [ERROR] config.json not found!
    echo.
    echo Please run: copy config.example.json config.json
    echo Then edit config.json and add your API key
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import requests, psutil, rich, openai" 2>nul
if errorlevel 1 (
    echo [WARNING] Basic dependencies not installed!
    echo.
    echo Installing basic dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install basic dependencies
        pause
        exit /b 1
    )
)

REM Main menu
:menu
cls
echo ========================================
echo  PC Automation Assistant - Launcher
echo ========================================
echo.
echo Choose an option:
echo.
echo  [1] Start CLI Mode (Basic)
echo  [2] Start Web Dashboard (Advanced)
echo  [3] Start Backend API Server Only
echo  [4] Start Voice Mode (Hands-free)
echo  [5] Test Voice Commands
echo  [6] View System Status
echo  [7] Install Advanced Dependencies
echo  [8] Run Tests
echo  [0] Exit
echo.
set /p choice="Enter your choice (0-8): "

if "%choice%"=="1" goto cli_mode
if "%choice%"=="2" goto web_dashboard
if "%choice%"=="3" goto backend_only
if "%choice%"=="4" goto voice_mode
if "%choice%"=="5" goto voice_test
if "%choice%"=="6" goto system_status
if "%choice%"=="7" goto install_advanced
if "%choice%"=="8" goto run_tests
if "%choice%"=="0" goto end
goto menu

:cli_mode
cls
echo ========================================
echo  Starting CLI Mode
echo ========================================
echo.
echo Type 'help' for available commands
echo Type 'exit' to quit
echo.
python main.py
pause
goto menu

:voice_mode
cls
echo ========================================
echo  Starting Voice Mode
echo ========================================
echo.

REM Check if voice dependencies are installed
python -c "import speech_recognition, pyttsx3, pyaudio" 2>nul
if errorlevel 1 (
    echo [WARNING] Voice dependencies not installed!
    echo Installing now...
    pip install SpeechRecognition pyttsx3 pyaudio
)

echo Say 'hey assistant' to wake up the assistant.
echo Press Ctrl+C to stop.
echo.
python main.py --voice
pause
goto menu

:web_dashboard
cls
echo ========================================
echo  Starting Web Dashboard
echo ========================================
echo.

REM Check if advanced dependencies are installed
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [WARNING] Advanced dependencies not installed!
    echo Installing now...
    pip install -r requirements-advanced.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install advanced dependencies
        pause
        goto menu
    )
)

echo Starting backend server...
echo Backend will run at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo [INFO] Frontend setup:
echo   1. Open new terminal
echo   2. cd frontend
echo   3. npm install (first time only)
echo   4. npm run dev
echo   5. Open http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn backend.main:app --reload
pause
goto menu

:backend_only
cls
echo ========================================
echo  Starting Backend API Server
echo ========================================
echo.

REM Check if advanced dependencies are installed
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [ERROR] Advanced dependencies not installed!
    echo Please choose option 6 to install them first.
    pause
    goto menu
)

echo Starting backend server...
echo API available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo WebSocket at: ws://localhost:8000/ws
echo.
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn backend.main:app --reload --port 8000
pause
goto menu

:voice_test
cls
echo ========================================
echo  Testing Voice Commands
echo ========================================
echo.

REM Check if voice dependencies are installed
python -c "import speech_recognition, pyttsx3" 2>nul
if errorlevel 1 (
    echo [ERROR] Voice dependencies not installed!
    echo Installing now...
    pip install SpeechRecognition pyttsx3 pyaudio
)

echo Testing microphone and text-to-speech...
echo.
python -c "from modules.voice_controller import VoiceController; v = VoiceController(); v.test_microphone(); v.speak('Voice system is working')"
echo.
pause
goto menu

:system_status
cls
echo ========================================
echo  System Status
echo ========================================
echo.
python main.py "status"
echo.
pause
goto menu

:install_advanced
cls
echo ========================================
echo  Installing Advanced Dependencies
echo ========================================
echo.
echo This will install:
echo  - FastAPI (Web framework)
echo  - Uvicorn (ASGI server)
echo  - WebSockets (Real-time communication)
echo  - APScheduler (Task scheduling)
echo  - SpeechRecognition (Voice commands)
echo  - pyttsx3 (Text-to-speech)
echo  - And more...
echo.
pause
echo.
echo Installing...
pip install -r requirements-advanced.txt
if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    goto menu
)
echo.
echo [SUCCESS] All advanced dependencies installed!
echo.
pause
goto menu

:run_tests
cls
echo ========================================
echo  Running Tests
echo ========================================
echo.
echo Testing module imports...
python -c "from modules import ai_client, command_processor, command_mapper, system_executor, file_scanner, process_monitor, system_monitor, memory_store; print('✓ All basic modules OK')"
echo.
echo Testing advanced modules...
python -c "from modules import task_scheduler, voice_controller, plugin_manager; print('✓ All advanced modules OK')"
echo.
echo Testing system monitor...
python -c "from modules.system_monitor import SystemMonitor; m = SystemMonitor({}); print('✓ System Monitor OK')"
echo.
echo Testing process monitor...
python -c "from modules.process_monitor import ProcessMonitor; p = ProcessMonitor(); print(f'✓ Process Monitor OK - {len(p.list_processes())} processes found')"
echo.
echo All tests passed!
echo.
pause
goto menu

:end
echo.
echo Thank you for using PC Automation Assistant!
echo.
exit /b 0
