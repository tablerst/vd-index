#!/bin/bash

echo "========================================"
echo "Production Deployment"
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "[1/6] Installing Dependencies..."
echo "----------------------------------------"
"$SCRIPT_DIR/install-deps.sh"
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[2/6] Building Frontend..."
echo "----------------------------------------"
cd "$PROJECT_ROOT/src/frontend"
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found in frontend directory"
    exit 1
fi

echo "Building production frontend..."
npm run build
if [ $? -ne 0 ]; then
    echo "Error: Failed to build frontend"
    exit 1
fi

echo ""
echo "[3/6] Deploying Static Files..."
echo "----------------------------------------"
cd "$PROJECT_ROOT/src/backend"
mkdir -p static

echo "Copying built files to backend static directory..."
cp -r "../frontend/dist/"* "static/"
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy static files"
    exit 1
fi

echo ""
echo "[4/6] Configuring Nginx..."
echo "----------------------------------------"
cd "$PROJECT_ROOT"

# 创建 nginx 日志目录
mkdir -p logs

# 检查 nginx 是否安装
if ! command -v nginx &> /dev/null; then
    echo "Warning: nginx not found, installing..."
    sudo apt update && sudo apt install -y nginx
fi

# 生成 nginx 配置文件
echo "Generating nginx configuration..."
chmod +x "$SCRIPT_DIR/generate-nginx-conf.sh"
"$SCRIPT_DIR/generate-nginx-conf.sh" "tomo-loop.icu" "$PROJECT_ROOT"

echo "Nginx configuration ready."

echo ""
echo "[5/6] Starting Backend Server..."
echo "----------------------------------------"
cd "$PROJECT_ROOT/src/backend"
if [ ! -f "run.py" ]; then
    echo "Error: run.py not found in backend directory"
    exit 1
fi

echo "Starting backend server in background..."
nohup uv run python -m run > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!

if [ $? -ne 0 ]; then
    echo "Warning: Failed to start with uv, trying python3..."
    nohup python3 -m run > ../../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    if [ $? -ne 0 ]; then
        echo "Warning: Failed to start with python3, trying python..."
        nohup python -m run > ../../logs/backend.log 2>&1 &
        BACKEND_PID=$!
    fi
fi

echo "Backend server started with PID: $BACKEND_PID"
sleep 3

# 检查后端是否启动成功
if ! curl -f -s http://localhost:8000/health > /dev/null; then
    echo "Warning: Backend health check failed, but continuing..."
fi

echo ""
echo "[6/6] Starting Nginx..."
echo "----------------------------------------"
cd "$PROJECT_ROOT"

# 停止可能运行的 nginx
sudo nginx -s quit 2>/dev/null || true
sleep 2

# 启动 nginx
echo "Starting nginx with project configuration..."
sudo nginx -c "$PROJECT_ROOT/nginx.conf"

if [ $? -eq 0 ]; then
    echo "Nginx started successfully!"
else
    echo "Error: Failed to start nginx"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "========================================"
echo "Production Deployment Completed!"
echo "========================================"
echo "Frontend: Built and deployed to static files"
echo "Backend: Running on http://localhost:8000 (PID: $BACKEND_PID)"
echo "Nginx: Running on http://tomo-loop.icu"
echo "========================================"
echo ""
echo "Access your application at: https://tomo-loop.icu"
echo ""
echo "To stop services:"
echo "  Backend: kill $BACKEND_PID"
echo "  Nginx: sudo nginx -s quit"
echo ""
echo "Logs:"
echo "  Backend: $PROJECT_ROOT/logs/backend.log"
echo "  Nginx: $PROJECT_ROOT/logs/access.log, $PROJECT_ROOT/logs/error.log"
echo "========================================"
