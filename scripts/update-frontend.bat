@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Frontend Update Deployment
echo ========================================

:: 获取脚本目录和项目根目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

:: 参数解析
set "SKIP_BUILD=false"
set "BACKUP_STATIC=true"

:parse_args
if "%~1"=="" goto :args_done
if "%~1"=="--skip-build" (
    set "SKIP_BUILD=true"
    shift /1
    goto :parse_args
)
if "%~1"=="--no-backup" (
    set "BACKUP_STATIC=false"
    shift /1
    goto :parse_args
)
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help
echo Unknown option: %~1
echo Use --help for usage information
exit /b 1

:show_help
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --skip-build       Skip frontend build (use existing dist)
echo   --no-backup        Skip backup of current static files
echo   -h, --help         Show this help message
echo.
echo Examples:
echo   %~nx0                    # Basic frontend update
echo   %~nx0 --skip-build       # Deploy existing build
echo   %~nx0 --no-backup        # Fast update without backup
echo.
echo Note: Windows version does not support nginx restart.
echo For nginx management, please use WSL or manual configuration.
exit /b 0

:args_done
echo Configuration:
echo   Skip Build: !SKIP_BUILD!
echo   Backup Static: !BACKUP_STATIC!
echo.

:: 检查前端目录
if not exist "%PROJECT_ROOT%\src\frontend" (
    echo Error: Frontend directory not found
    pause
    exit /b 1
)

:: 检查后端目录
if not exist "%PROJECT_ROOT%\src\backend" (
    echo Error: Backend directory not found
    pause
    exit /b 1
)

:: 步骤1: 备份当前静态文件
if "!BACKUP_STATIC!"=="true" (
    echo [1/3] Backing up current static files...
    echo ----------------------------------------
    cd /d "%PROJECT_ROOT%\src\backend"
    
    if exist "static" (
        :: 生成备份目录名
        for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "DATE_PART=%%c%%a%%b"
        for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TIME_PART=%%a%%b"
        set "BACKUP_DIR=static_backup_!DATE_PART!_!TIME_PART!"
        
        echo Creating backup: !BACKUP_DIR!
        xcopy /E /I /Q "static" "!BACKUP_DIR!" >nul
        if !errorlevel! neq 0 (
            echo Warning: Failed to create backup
        ) else (
            echo Backup completed: !BACKUP_DIR!
        )
        
        :: 清理旧备份（保留最近5个）
        set "count=0"
        for /f "skip=5" %%d in ('dir /b /ad /o-d static_backup_* 2^>nul') do (
            rmdir /s /q "%%d" 2>nul
        )
    ) else (
        echo No existing static directory to backup
    )
) else (
    echo [1/3] Skipping backup...
    echo ----------------------------------------
)

:: 步骤2: 构建前端
if "!SKIP_BUILD!"=="false" (
    echo.
    echo [2/3] Building Frontend...
    echo ----------------------------------------
    cd /d "%PROJECT_ROOT%\src\frontend"
    
    if not exist "package.json" (
        echo Error: package.json not found in frontend directory
        pause
        exit /b 1
    )
    
    :: 检查依赖是否已安装
    if not exist "node_modules" (
        echo Installing frontend dependencies...
        call pnpm install
        if !errorlevel! neq 0 (
            echo Error: Failed to install frontend dependencies
            pause
            exit /b 1
        )
    )
    
    echo Building production frontend...
    call pnpm run build
    if !errorlevel! neq 0 (
        echo Error: Failed to build frontend
        pause
        exit /b 1
    )
    
    :: 检查构建输出
    if not exist "dist" (
        echo Error: Build output directory 'dist' not found
        pause
        exit /b 1
    )
    
    echo Frontend build completed successfully
) else (
    echo.
    echo [2/3] Skipping frontend build...
    echo ----------------------------------------
    cd /d "%PROJECT_ROOT%\src\frontend"
    
    if not exist "dist" (
        echo Error: No existing build found. Please run without --skip-build first.
        pause
        exit /b 1
    )
    
    echo Using existing build from dist directory
)

:: 步骤3: 部署静态文件
echo.
echo [3/3] Deploying Static Files...
echo ----------------------------------------
cd /d "%PROJECT_ROOT%\src\backend"

:: 创建静态目录
if not exist "static" mkdir "static"

:: 清空现有静态文件
echo Clearing existing static files...
del /q "static\*.*" 2>nul
for /d %%d in ("static\*") do rmdir /s /q "%%d" 2>nul

:: 复制新的构建文件
echo Copying built files to backend static directory...
xcopy /E /I /Y "..\frontend\dist\*" "static\" >nul
if !errorlevel! neq 0 (
    echo Error: Failed to copy static files
    
    :: 尝试恢复备份
    if "!BACKUP_STATIC!"=="true" (
        for /f %%d in ('dir /b /ad /o-d static_backup_* 2^>nul') do (
            echo Attempting to restore from backup: %%d
            del /q "static\*.*" 2>nul
            for /d %%x in ("static\*") do rmdir /s /q "%%x" 2>nul
            xcopy /E /I /Y "%%d\*" "static\" >nul
            echo Backup restored
            goto :backup_restored
        )
        :backup_restored
    )
    pause
    exit /b 1
)

:: 验证部署
if not exist "static\index.html" (
    echo Warning: index.html not found in deployed static files
)

echo Static files deployed successfully

echo.
echo ========================================
echo Frontend Update Completed!
echo ========================================
echo Frontend: Built and deployed to static files
echo Static files location: %PROJECT_ROOT%\src\backend\static\

if "!BACKUP_STATIC!"=="true" (
    for /f %%d in ('dir /b /ad /o-d static_backup_* 2^>nul') do (
        echo Backup available: %%d
        goto :backup_shown
    )
    :backup_shown
)

echo ========================================
echo.
echo 🎉 Frontend update deployment successful!
echo.
echo Backend will serve the updated frontend at: http://localhost:8000
echo.
echo 💡 Tips:
echo   1. Clear browser cache (Ctrl+F5) to see changes
echo   2. Restart backend if needed: uv run python -m run
echo   3. For nginx setup, use WSL or manual configuration
echo.
echo 📁 Useful commands:
echo   Rollback: xcopy /E /I /Y static_backup_*\* static\
echo   Check backend: curl http://localhost:8000/health
echo ========================================

pause
