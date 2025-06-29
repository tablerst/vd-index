@echo off
echo ========================================
echo Starting Development Environment
echo ========================================

echo.
echo [1/2] Starting Backend Service...
echo ----------------------------------------
cd /d "%~dp0..\src\backend"
if not exist "run.py" (
    echo Error: run.py not found in backend directory
    pause
    exit /b 1
)

echo Starting FastAPI backend server...
start "Backend Server" cmd /k "uv run python -m run"
if %errorlevel% neq 0 (
    echo Warning: Failed to start backend with uv, trying python3...
    start "Backend Server" cmd /k "python3 -m run"
    if %errorlevel% neq 0 (
        echo Warning: Failed to start backend with python3, trying python...
        start "Backend Server" cmd /k "python -m run"
    )
)

echo Backend server starting in background...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] Starting Frontend Service...
echo ----------------------------------------
cd /d "%~dp0..\src\frontend"
if not exist "package.json" (
    echo Error: package.json not found in frontend directory
    pause
    exit /b 1
)

echo Starting Vite development server...
echo.
echo ========================================
echo Development Environment Started!
echo ========================================
echo Backend: Running in separate window
echo Frontend: Starting now...
echo.
echo Press Ctrl+C to stop frontend server
echo Close backend window manually to stop backend
echo ========================================
echo.

call npm run dev
