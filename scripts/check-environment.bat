@echo off
echo ============================================================
echo VRC Division 环境检查 (Windows)
echo ============================================================

cd /d "%~dp0.."

echo 正在运行环境检查脚本...
echo.

python scripts\check-environment.py
if %errorlevel% neq 0 (
    echo.
    echo 尝试使用 python3...
    python3 scripts\check-environment.py
    if %errorlevel% neq 0 (
        echo.
        echo 错误: 无法运行检查脚本
        echo 请确保 Python 已正确安装
        pause
        exit /b 1
    )
)

echo.
echo 按任意键退出...
pause >nul
