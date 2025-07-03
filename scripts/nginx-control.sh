#!/bin/bash

# Nginx 控制脚本
# 用于管理项目的 nginx 服务

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NGINX_CONF="$PROJECT_ROOT/nginx.conf"
LOGS_DIR="$PROJECT_ROOT/logs"

# 创建日志目录
mkdir -p "$LOGS_DIR"

show_usage() {
    echo "用法: $0 {start|stop|restart|status|test|logs}"
    echo ""
    echo "命令说明:"
    echo "  start   - 启动 nginx"
    echo "  stop    - 停止 nginx"
    echo "  restart - 重启 nginx"
    echo "  status  - 查看 nginx 状态"
    echo "  test    - 测试 nginx 配置"
    echo "  logs    - 查看 nginx 日志"
    echo ""
}

check_nginx() {
    if ! command -v nginx &> /dev/null; then
        echo "错误: nginx 未安装"
        echo "请运行: sudo apt update && sudo apt install -y nginx"
        exit 1
    fi
}

check_config() {
    if [ ! -f "$NGINX_CONF" ]; then
        echo "错误: nginx 配置文件不存在: $NGINX_CONF"
        exit 1
    fi
}

start_nginx() {
    echo "启动 nginx..."
    check_nginx
    check_config
    
    # 测试配置
    sudo nginx -t -c "$NGINX_CONF"
    if [ $? -ne 0 ]; then
        echo "错误: nginx 配置测试失败"
        exit 1
    fi
    
    # 启动 nginx
    sudo nginx -c "$NGINX_CONF"
    if [ $? -eq 0 ]; then
        echo "✅ nginx 启动成功"
        echo "访问地址: http://tomo-loop.icu"
    else
        echo "❌ nginx 启动失败"
        exit 1
    fi
}

stop_nginx() {
    echo "停止 nginx..."
    sudo nginx -s quit 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ nginx 已停止"
    else
        echo "⚠️  nginx 可能未运行或停止失败"
    fi
}

restart_nginx() {
    echo "重启 nginx..."
    stop_nginx
    sleep 2
    start_nginx
}

status_nginx() {
    echo "检查 nginx 状态..."
    
    # 检查进程
    if pgrep nginx > /dev/null; then
        echo "✅ nginx 进程运行中"
        echo "进程信息:"
        ps aux | grep nginx | grep -v grep
    else
        echo "❌ nginx 进程未运行"
    fi
    
    echo ""
    
    # 检查端口
    if netstat -tlnp 2>/dev/null | grep :80 > /dev/null; then
        echo "✅ 端口 80 已监听"
        netstat -tlnp 2>/dev/null | grep :80
    else
        echo "❌ 端口 80 未监听"
    fi
    
    echo ""
    
    # 检查后端连接
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "✅ 后端服务连接正常"
    else
        echo "❌ 后端服务连接失败"
        echo "请确保后端服务在 http://localhost:8000 运行"
    fi
    
    echo ""
    
    # 检查域名访问
    if curl -f -s -H "Host: tomo-loop.icu" http://localhost/ > /dev/null; then
        echo "✅ 域名访问正常"
    else
        echo "❌ 域名访问失败"
    fi
}

test_config() {
    echo "测试 nginx 配置..."
    check_nginx
    check_config
    
    sudo nginx -t -c "$NGINX_CONF"
    if [ $? -eq 0 ]; then
        echo "✅ nginx 配置测试通过"
    else
        echo "❌ nginx 配置测试失败"
        exit 1
    fi
}

show_logs() {
    echo "nginx 日志文件:"
    echo "================"
    
    if [ -f "$LOGS_DIR/access.log" ]; then
        echo ""
        echo "📄 访问日志 (最后 20 行):"
        echo "------------------------"
        tail -20 "$LOGS_DIR/access.log"
    else
        echo "访问日志文件不存在: $LOGS_DIR/access.log"
    fi
    
    if [ -f "$LOGS_DIR/error.log" ]; then
        echo ""
        echo "📄 错误日志 (最后 20 行):"
        echo "------------------------"
        tail -20 "$LOGS_DIR/error.log"
    else
        echo "错误日志文件不存在: $LOGS_DIR/error.log"
    fi
    
    echo ""
    echo "实时查看日志:"
    echo "  访问日志: tail -f $LOGS_DIR/access.log"
    echo "  错误日志: tail -f $LOGS_DIR/error.log"
}

# 主逻辑
case "$1" in
    start)
        start_nginx
        ;;
    stop)
        stop_nginx
        ;;
    restart)
        restart_nginx
        ;;
    status)
        status_nginx
        ;;
    test)
        test_config
        ;;
    logs)
        show_logs
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
