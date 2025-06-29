#!/bin/bash

echo "========================================"
echo "Installing Frontend and Backend Dependencies"
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "[1/2] Installing Frontend Dependencies..."
echo "----------------------------------------"
cd "$PROJECT_ROOT/src/frontend"
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found in frontend directory"
    exit 1
fi

echo "Installing npm packages..."
npm install
if [ $? -ne 0 ]; then
    echo "Error: Failed to install frontend dependencies"
    exit 1
fi

echo ""
echo "[2/2] Installing Backend Dependencies..."
echo "----------------------------------------"
cd "$PROJECT_ROOT/src/backend"
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found in backend directory"
    exit 1
fi

echo "Installing Python packages with uv..."
uv sync
if [ $? -ne 0 ]; then
    echo "Error: Failed to install backend dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Dependencies Installation Completed!"
echo "========================================"
echo "Frontend: npm packages installed"
echo "Backend: Python packages installed with uv"
echo ""
echo "You can now run:"
echo "- ./dev.sh for development mode"
echo "- ./prod.sh for production mode"
echo "========================================"
