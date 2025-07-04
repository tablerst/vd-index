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
    echo "用法: $0 {start|stop|restart|status|test|logs|force-stop|check-port}"
    echo ""
    echo "命令说明:"
    echo "  start      - 启动 nginx"
    echo "  stop       - 停止 nginx"
    echo "  force-stop - 强制停止所有 nginx 进程"
    echo "  restart    - 重启 nginx"
    echo "  status     - 查看 nginx 状态"
    echo "  test       - 测试 nginx 配置"
    echo "  logs       - 查看 nginx 日志"
    echo "  check-port - 检查端口占用情况"
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

# 检查端口80是否被占用
check_port_80() {
    echo "检查端口 80 占用情况..."

    if netstat -tuln 2>/dev/null | grep -q ":80 " || ss -tuln 2>/dev/null | grep -q ":80 "; then
        echo "⚠️  端口 80 已被占用:"
        netstat -tuln 2>/dev/null | grep ":80 " || ss -tuln 2>/dev/null | grep ":80 "

        # 显示占用端口的进程
        if command -v lsof &> /dev/null; then
            echo ""
            echo "占用端口 80 的进程:"
            lsof -i :80 2>/dev/null || echo "无法确定进程信息"
        fi

        # 检查是否是nginx进程
        if pgrep nginx > /dev/null; then
            echo ""
            echo "发现 nginx 进程正在运行"
            echo "nginx 进程 PID: $(pgrep nginx | tr '\n' ' ')"
            return 2  # nginx占用
        else
            echo ""
            echo "端口被其他进程占用，请先停止相关服务"
            return 1  # 其他进程占用
        fi
    else
        echo "✅ 端口 80 可用"
        return 0  # 端口可用
    fi
}

# 强制停止所有nginx进程
force_stop_nginx() {
    echo "强制停止所有 nginx 进程..."

    # 尝试优雅停止
    sudo nginx -s quit 2>/dev/null || true
    sleep 2

    # 检查是否还有nginx进程
    if pgrep nginx > /dev/null; then
        echo "发现残留的 nginx 进程，正在强制终止..."
        sudo pkill nginx 2>/dev/null || true
        sleep 2

        # 强制杀死
        if pgrep nginx > /dev/null; then
            echo "使用 SIGKILL 强制终止 nginx 进程..."
            sudo pkill -9 nginx 2>/dev/null || true
            sleep 1
        fi
    fi

    # 验证是否全部停止
    if pgrep nginx > /dev/null; then
        echo "❌ 仍有 nginx 进程运行，请手动检查"
        ps aux | grep nginx | grep -v grep
        return 1
    else
        echo "✅ 所有 nginx 进程已停止"
        return 0
    fi
}

start_nginx() {
    echo "启动 nginx..."
    check_nginx

    # 检查端口占用情况
    check_port_80
    port_status=$?

    if [ $port_status -eq 1 ]; then
        echo "❌ 端口 80 被其他进程占用，无法启动 nginx"
        echo "请先停止占用端口 80 的服务，或使用 'force-stop' 命令"
        exit 1
    elif [ $port_status -eq 2 ]; then
        echo "发现已有 nginx 进程运行，尝试停止..."
        force_stop_nginx
        if [ $? -ne 0 ]; then
            echo "❌ 无法停止现有 nginx 进程"
            exit 1
        fi
        sleep 2
    fi

    # 生成 nginx 配置文件
    echo "生成 nginx 配置文件..."
    chmod +x "$SCRIPT_DIR/generate-nginx-conf.sh"
    "$SCRIPT_DIR/generate-nginx-conf.sh" "tomo-loop.icu" "$PROJECT_ROOT"

    check_config

    # 测试配置
    echo "测试 nginx 配置..."
    sudo nginx -t -c "$NGINX_CONF"
    if [ $? -ne 0 ]; then
        echo "❌ nginx 配置测试失败"
        exit 1
    fi

    # 启动 nginx
    echo "启动 nginx 服务..."
    sudo nginx -c "$NGINX_CONF"

    if [ $? -eq 0 ]; then
        # 等待一下让nginx完全启动
        sleep 2

        # 验证nginx是否真的在运行
        if pgrep nginx > /dev/null; then
            echo "✅ nginx 启动成功"
            echo "nginx 进程 PID: $(pgrep nginx | tr '\n' ' ')"
            echo "访问地址: http://tomo-loop.icu"

            # 检查端口监听
            if netstat -tuln 2>/dev/null | grep -q ":80 " || ss -tuln 2>/dev/null | grep -q ":80 "; then
                echo "✅ 端口 80 正在监听"
            else
                echo "⚠️  端口 80 未监听，可能启动失败"
            fi
        else
            echo "❌ nginx 启动失败 - 未找到进程"
            if [ -f "$LOGS_DIR/error.log" ]; then
                echo "最近的错误日志:"
                tail -5 "$LOGS_DIR/error.log"
            fi
            exit 1
        fi
    else
        echo "❌ nginx 启动失败"
        if [ -f "$LOGS_DIR/error.log" ]; then
            echo "最近的错误日志:"
            tail -5 "$LOGS_DIR/error.log"
        fi
        exit 1
    fi
}

stop_nginx() {
    echo "停止 nginx..."

    if ! pgrep nginx > /dev/null; then
        echo "nginx 未运行"
        return 0
    fi

    # 尝试优雅停止
    sudo nginx -s quit 2>/dev/null
    sleep 2

    # 检查是否成功停止
    if pgrep nginx > /dev/null; then
        echo "⚠️  优雅停止失败，尝试强制停止..."
        force_stop_nginx
    else
        echo "✅ nginx 已停止"
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
    force-stop)
        force_stop_nginx
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
    check-port)
        check_port_80
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
