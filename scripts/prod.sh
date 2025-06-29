#!/bin/bash

echo "========================================"
echo "Production Deployment"
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "[1/4] Installing Dependencies..."
echo "----------------------------------------"
"$SCRIPT_DIR/install-deps.sh"
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[2/4] Building Frontend..."
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
echo "[3/4] Deploying Static Files..."
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
echo "[4/4] Starting Production Server..."
echo "----------------------------------------"
if [ ! -f "run.py" ]; then
    echo "Error: run.py not found in backend directory"
    exit 1
fi

echo ""
echo "========================================"
echo "Production Deployment Completed!"
echo "========================================"
echo "Frontend: Built and deployed to static files"
echo "Backend: Starting production server..."
echo "========================================"
echo ""

uv run python -m run
if [ $? -ne 0 ]; then
    echo "Warning: Failed to start with uv, trying python3..."
    python3 -m run
    if [ $? -ne 0 ]; then
        echo "Warning: Failed to start with python3, trying python..."
        python -m run
    fi
fi
