@echo off
echo ========================================
echo Production Deployment
echo ========================================

echo.
echo [1/4] Installing Dependencies...
echo ----------------------------------------
call "%~dp0install-deps.bat"
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Building Frontend...
echo ----------------------------------------
cd /d "%~dp0..\src\frontend"
if not exist "package.json" (
    echo Error: package.json not found in frontend directory
    pause
    exit /b 1
)

echo Building production frontend...
call npm run build
if %errorlevel% neq 0 (
    echo Error: Failed to build frontend
    pause
    exit /b 1
)

echo.
echo [3/4] Deploying Static Files...
echo ----------------------------------------
cd /d "%~dp0..\src\backend"
if not exist "static" mkdir static

echo Copying built files to backend static directory...
xcopy /E /I /Y "..\frontend\dist\*" "static\"
if %errorlevel% neq 0 (
    echo Error: Failed to copy static files
    pause
    exit /b 1
)

echo.
echo [4/4] Starting Production Server...
echo ----------------------------------------
if not exist "run.py" (
    echo Error: run.py not found in backend directory
    pause
    exit /b 1
)

echo.
echo ========================================
echo Production Deployment Completed!
echo ========================================
echo Frontend: Built and deployed to static files
echo Backend: Starting production server...
echo ========================================
echo.

uv run python -m run
if %errorlevel% neq 0 (
    echo Warning: Failed to start with uv, trying python3...
    python3 -m run
    if %errorlevel% neq 0 (
        echo Warning: Failed to start with python3, trying python...
        python -m run
    )
)
