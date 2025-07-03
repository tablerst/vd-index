#!/bin/bash

echo "============================================================"
echo "VRC Division 环境检查 (Linux/macOS)"
echo "============================================================"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "正在运行环境检查脚本..."
echo ""

# Try to run the Python script
if command -v python3 &> /dev/null; then
    python3 scripts/check-environment.py
elif command -v python &> /dev/null; then
    python scripts/check-environment.py
else
    echo "错误: 未找到 Python 解释器"
    echo "请安装 Python 3.11+ 后重试"
    exit 1
fi

echo ""
echo "检查完成！"
