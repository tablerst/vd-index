#!/bin/bash

echo "========================================"
echo "Starting Development Environment"
echo "========================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "[1/2] Starting Backend Service..."
echo "----------------------------------------"
cd "$PROJECT_ROOT/src/backend"
if [ ! -f "run.py" ]; then
    echo "Error: run.py not found in backend directory"
    exit 1
fi

echo "Starting FastAPI backend server..."
# Start backend in background
uv run python -m run &
BACKEND_PID=$!

if [ $? -ne 0 ]; then
    echo "Warning: Failed to start backend with uv, trying python3..."
    python3 -m run &
    BACKEND_PID=$!
    if [ $? -ne 0 ]; then
        echo "Warning: Failed to start backend with python3, trying python..."
        python -m run &
        BACKEND_PID=$!
    fi
fi

echo "Backend server starting in background (PID: $BACKEND_PID)..."
sleep 3

echo ""
echo "[2/2] Starting Frontend Service..."
echo "----------------------------------------"
cd "$PROJECT_ROOT/src/frontend"
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found in frontend directory"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "Starting Vite development server..."
echo ""
echo "========================================"
echo "Development Environment Started!"
echo "========================================"
echo "Backend: Running in background (PID: $BACKEND_PID)"
echo "Frontend: Starting now..."
echo ""
echo "Press Ctrl+C to stop both servers"
echo "========================================"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    echo "Development environment stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start frontend (this will block)
npm run dev

# If npm run dev exits, cleanup
cleanup
