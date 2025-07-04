#!/bin/bash

# 故障排除脚本
# 用于诊断和解决常见的部署问题

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "故障排除诊断工具"
echo "========================================"
echo ""

# 检查系统基本信息
echo "1. 系统信息检查"
echo "----------------------------------------"
echo "操作系统: $(uname -a)"
echo "当前用户: $(whoami)"
echo "当前目录: $(pwd)"
echo "项目根目录: $PROJECT_ROOT"
echo ""

# 检查必要的命令
echo "2. 必要命令检查"
echo "----------------------------------------"
commands=("nginx" "node" "npm" "python3" "curl" "netstat" "lsof")

for cmd in "${commands[@]}"; do
    if command -v "$cmd" &> /dev/null; then
        version=$($cmd --version 2>/dev/null | head -1 || echo "无版本信息")
        echo "✅ $cmd: $version"
    else
        echo "❌ $cmd: 未安装"
    fi
done
echo ""

# 检查端口占用
echo "3. 端口占用检查"
echo "----------------------------------------"
ports=(80 8000 3000 5173)

for port in "${ports[@]}"; do
    if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
        echo "⚠️  端口 $port 已被占用:"
        netstat -tuln 2>/dev/null | grep ":$port " || ss -tuln 2>/dev/null | grep ":$port "
        
        if command -v lsof &> /dev/null; then
            echo "   占用进程:"
            lsof -i :$port 2>/dev/null | head -5 || echo "   无法确定进程"
        fi
    else
        echo "✅ 端口 $port 可用"
    fi
done
echo ""

# 检查nginx进程
echo "4. Nginx 进程检查"
echo "----------------------------------------"
if pgrep nginx > /dev/null; then
    echo "✅ 发现 nginx 进程:"
    ps aux | grep nginx | grep -v grep
    echo ""
    echo "nginx 配置测试:"
    if [ -f "$PROJECT_ROOT/nginx.conf" ]; then
        sudo nginx -t -c "$PROJECT_ROOT/nginx.conf" 2>&1
    else
        echo "❌ nginx 配置文件不存在: $PROJECT_ROOT/nginx.conf"
    fi
else
    echo "❌ 未发现 nginx 进程"
fi
echo ""

# 检查后端进程
echo "5. 后端进程检查"
echo "----------------------------------------"
if pgrep -f "run.py\|uvicorn\|fastapi" > /dev/null; then
    echo "✅ 发现后端进程:"
    ps aux | grep -E "run.py|uvicorn|fastapi" | grep -v grep
    
    echo ""
    echo "后端健康检查:"
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "✅ 后端服务响应正常"
    else
        echo "❌ 后端服务无响应"
        echo "尝试访问 http://localhost:8000/health"
        curl -v http://localhost:8000/health 2>&1 | head -10
    fi
else
    echo "❌ 未发现后端进程"
fi
echo ""

# 检查文件和目录
echo "6. 文件和目录检查"
echo "----------------------------------------"
files_to_check=(
    "$PROJECT_ROOT/src/frontend/package.json"
    "$PROJECT_ROOT/src/frontend/dist/index.html"
    "$PROJECT_ROOT/src/backend/run.py"
    "$PROJECT_ROOT/src/backend/static/index.html"
    "$PROJECT_ROOT/.env"
    "$PROJECT_ROOT/nginx.conf"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "unknown")
        echo "✅ $file ($size bytes)"
    elif [ -d "$file" ]; then
        echo "✅ $file (目录)"
    else
        echo "❌ $file (不存在)"
    fi
done
echo ""

# 检查日志文件
echo "7. 日志文件检查"
echo "----------------------------------------"
log_files=(
    "$PROJECT_ROOT/logs/backend.log"
    "$PROJECT_ROOT/logs/access.log"
    "$PROJECT_ROOT/logs/error.log"
    "$PROJECT_ROOT/logs/app.log"
)

for log_file in "${log_files[@]}"; do
    if [ -f "$log_file" ]; then
        size=$(stat -c%s "$log_file" 2>/dev/null || stat -f%z "$log_file" 2>/dev/null || echo "unknown")
        echo "✅ $log_file ($size bytes)"
        
        if [ "$size" != "0" ] && [ "$size" != "unknown" ]; then
            echo "   最后 3 行:"
            tail -3 "$log_file" | sed 's/^/   /'
        fi
    else
        echo "❌ $log_file (不存在)"
    fi
done
echo ""

# 网络连接测试
echo "8. 网络连接测试"
echo "----------------------------------------"
echo "测试本地连接:"

# 测试localhost:8000
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ http://localhost:8000/health - 后端正常"
else
    echo "❌ http://localhost:8000/health - 后端无响应"
fi

# 测试localhost:80
if curl -f -s http://localhost/ > /dev/null; then
    echo "✅ http://localhost/ - nginx正常"
else
    echo "❌ http://localhost/ - nginx无响应"
fi

# 测试域名
if curl -f -s -H "Host: tomo-loop.icu" http://localhost/ > /dev/null; then
    echo "✅ http://tomo-loop.icu (本地) - 域名配置正常"
else
    echo "❌ http://tomo-loop.icu (本地) - 域名配置异常"
fi
echo ""

# 提供解决方案
echo "9. 常见问题解决方案"
echo "----------------------------------------"
echo "如果发现问题，可以尝试以下解决方案:"
echo ""
echo "端口占用问题:"
echo "  sudo ./scripts/nginx-control.sh force-stop"
echo "  sudo fuser -k 80/tcp  # 强制释放80端口"
echo ""
echo "nginx配置问题:"
echo "  ./scripts/nginx-control.sh test"
echo "  ./scripts/generate-nginx-conf.sh tomo-loop.icu $PROJECT_ROOT"
echo ""
echo "后端服务问题:"
echo "  cd src/backend && python3 run.py"
echo "  检查 logs/backend.log 日志"
echo ""
echo "前端构建问题:"
echo "  cd src/frontend && npm run build"
echo "  检查 dist/ 目录是否生成"
echo ""
echo "权限问题:"
echo "  sudo chown -R \$USER:\$USER $PROJECT_ROOT"
echo "  chmod +x scripts/*.sh"
echo ""
echo "完整重启:"
echo "  ./scripts/nginx-control.sh force-stop"
echo "  pkill -f 'run.py|uvicorn|fastapi'"
echo "  ./scripts/prod.sh"
echo ""

echo "========================================"
echo "诊断完成"
echo "========================================"
echo ""
echo "如需查看实时日志:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/error.log"
echo "  tail -f logs/access.log"
echo ""
echo "如需获取更多帮助，请提供以上诊断信息"
