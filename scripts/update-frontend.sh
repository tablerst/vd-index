#!/bin/bash

echo "========================================"
echo "Frontend Update Deployment"
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 参数解析
RESTART_NGINX=false
SKIP_BUILD=false
BACKUP_STATIC=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --restart-nginx)
            RESTART_NGINX=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --no-backup)
            BACKUP_STATIC=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --restart-nginx    Restart nginx after deployment"
            echo "  --skip-build       Skip frontend build (use existing dist)"
            echo "  --no-backup        Skip backup of current static files"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Basic frontend update"
            echo "  $0 --restart-nginx           # Update and restart nginx"
            echo "  $0 --skip-build              # Deploy existing build"
            echo "  $0 --restart-nginx --no-backup  # Fast update with nginx restart"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "Configuration:"
echo "  Restart Nginx: $RESTART_NGINX"
echo "  Skip Build: $SKIP_BUILD"
echo "  Backup Static: $BACKUP_STATIC"
echo ""

# 检查前端目录
if [ ! -d "$PROJECT_ROOT/src/frontend" ]; then
    echo "Error: Frontend directory not found"
    exit 1
fi

# 检查后端目录
if [ ! -d "$PROJECT_ROOT/src/backend" ]; then
    echo "Error: Backend directory not found"
    exit 1
fi

# 步骤1: 备份当前静态文件（如果启用）
if [ "$BACKUP_STATIC" = true ]; then
    echo "[1/4] Backing up current static files..."
    echo "----------------------------------------"
    cd "$PROJECT_ROOT/src/backend"
    
    if [ -d "static" ]; then
        BACKUP_DIR="static_backup_$(date +%Y%m%d_%H%M%S)"
        echo "Creating backup: $BACKUP_DIR"
        cp -r static "$BACKUP_DIR"
        
        # 保留最近5个备份
        ls -dt static_backup_* 2>/dev/null | tail -n +6 | xargs rm -rf 2>/dev/null || true
        echo "Backup completed: $BACKUP_DIR"
    else
        echo "No existing static directory to backup"
    fi
else
    echo "[1/4] Skipping backup..."
    echo "----------------------------------------"
fi

# 步骤2: 构建前端（如果不跳过）
if [ "$SKIP_BUILD" = false ]; then
    echo ""
    echo "[2/4] Building Frontend..."
    echo "----------------------------------------"
    cd "$PROJECT_ROOT/src/frontend"
    
    if [ ! -f "package.json" ]; then
        echo "Error: package.json not found in frontend directory"
        exit 1
    fi
    
    # 检查依赖是否已安装
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        pnpm install
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install frontend dependencies"
            exit 1
        fi
    fi
    
    echo "Building production frontend..."
    pnpm run build
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build frontend"
        exit 1
    fi
    
    # 检查构建输出
    if [ ! -d "dist" ]; then
        echo "Error: Build output directory 'dist' not found"
        exit 1
    fi
    
    echo "Frontend build completed successfully"
else
    echo ""
    echo "[2/4] Skipping frontend build..."
    echo "----------------------------------------"
    cd "$PROJECT_ROOT/src/frontend"
    
    if [ ! -d "dist" ]; then
        echo "Error: No existing build found. Please run without --skip-build first."
        exit 1
    fi
    
    echo "Using existing build from dist directory"
fi

# 步骤3: 部署静态文件
echo ""
echo "[3/4] Deploying Static Files..."
echo "----------------------------------------"
cd "$PROJECT_ROOT/src/backend"

# 创建静态目录
mkdir -p static

# 清空现有静态文件
echo "Clearing existing static files..."
rm -rf static/*

# 复制新的构建文件
echo "Copying built files to backend static directory..."
cp -r "../frontend/dist/"* "static/"
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy static files"
    
    # 尝试恢复备份
    if [ "$BACKUP_STATIC" = true ]; then
        LATEST_BACKUP=$(ls -dt static_backup_* 2>/dev/null | head -n 1)
        if [ -n "$LATEST_BACKUP" ]; then
            echo "Attempting to restore from backup: $LATEST_BACKUP"
            rm -rf static/*
            cp -r "$LATEST_BACKUP/"* "static/"
            echo "Backup restored"
        fi
    fi
    exit 1
fi

# 验证部署
if [ ! -f "static/index.html" ]; then
    echo "Warning: index.html not found in deployed static files"
fi

echo "Static files deployed successfully"

# 步骤4: 重启nginx（如果需要）
if [ "$RESTART_NGINX" = true ]; then
    echo ""
    echo "[4/4] Restarting Nginx..."
    echo "----------------------------------------"
    
    # 检查nginx控制脚本
    if [ -f "$SCRIPT_DIR/nginx-control.sh" ]; then
        echo "Using nginx control script..."
        chmod +x "$SCRIPT_DIR/nginx-control.sh"
        
        # 重新加载nginx配置
        if "$SCRIPT_DIR/nginx-control.sh" reload; then
            echo "✅ Nginx reloaded successfully!"
        else
            echo "⚠️  Nginx reload failed, trying restart..."
            if "$SCRIPT_DIR/nginx-control.sh" restart; then
                echo "✅ Nginx restarted successfully!"
            else
                echo "❌ Failed to restart nginx"
                echo "Please check nginx manually"
            fi
        fi
    else
        echo "Nginx control script not found, using direct commands..."
        
        # 测试nginx配置
        if nginx -t 2>/dev/null; then
            echo "Nginx configuration is valid"
            
            # 重新加载配置
            if nginx -s reload 2>/dev/null; then
                echo "✅ Nginx reloaded successfully!"
            else
                echo "❌ Failed to reload nginx"
            fi
        else
            echo "❌ Nginx configuration test failed"
        fi
    fi
else
    echo ""
    echo "[4/4] Skipping nginx restart..."
    echo "----------------------------------------"
    echo "Note: You may need to clear browser cache to see changes"
fi

echo ""
echo "========================================"
echo "Frontend Update Completed!"
echo "========================================"
echo "Frontend: Built and deployed to static files"
echo "Static files location: $PROJECT_ROOT/src/backend/static/"

if [ "$BACKUP_STATIC" = true ]; then
    LATEST_BACKUP=$(ls -dt "$PROJECT_ROOT/src/backend/static_backup_"* 2>/dev/null | head -n 1)
    if [ -n "$LATEST_BACKUP" ]; then
        echo "Backup available: $(basename "$LATEST_BACKUP")"
    fi
fi

if [ "$RESTART_NGINX" = true ]; then
    echo "Nginx: Restarted"
else
    echo "Nginx: Not restarted (use --restart-nginx to restart)"
fi

echo "========================================"
echo ""
echo "🎉 Frontend update deployment successful!"
echo ""
echo "Access your application at: https://tomo-loop.icu"
echo ""

if [ "$RESTART_NGINX" = false ]; then
    echo "💡 Tip: If changes don't appear immediately:"
    echo "   1. Clear browser cache (Ctrl+F5)"
    echo "   2. Or restart nginx: $0 --restart-nginx --skip-build"
fi

echo ""
echo "📁 Useful commands:"
echo "   View nginx logs: $SCRIPT_DIR/nginx-control.sh logs"
echo "   Check nginx status: $SCRIPT_DIR/nginx-control.sh status"
echo "   Rollback: cp -r static_backup_*/\* static/"
echo "========================================"
