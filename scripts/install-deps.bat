@echo off
echo ========================================
echo Installing Frontend and Backend Dependencies
echo ========================================

echo.
echo [1/2] Installing Frontend Dependencies...
echo ----------------------------------------
cd /d "%~dp0..\src\frontend"
if not exist "package.json" (
    echo Error: package.json not found in frontend directory
    pause
    exit /b 1
)

echo Installing npm packages...
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo [2/2] Installing Backend Dependencies...
echo ----------------------------------------
cd /d "%~dp0..\src\backend"
if not exist "pyproject.toml" (
    echo Error: pyproject.toml not found in backend directory
    pause
    exit /b 1
)

echo Installing Python packages with uv...
call uv sync
if %errorlevel% neq 0 (
    echo Error: Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Dependencies Installation Completed!
echo ========================================
echo Frontend: npm packages installed
echo Backend: Python packages installed with uv
echo.
echo You can now run:
echo - dev.bat for development mode
echo - prod.bat for production mode
echo ========================================
pause
